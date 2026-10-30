"""Adversarial M4 judge tests. Fake Lab source is ONLY patched in unit fixtures.

The shipping workflow must call the unpatched judge against the pinned real Lab.
"""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from hashlib import sha256
from unittest.mock import patch

from scripts.verify_open import verify, Rejected, LAB_PIN, SCHEMA, stable

def db(path,ddl):
    path.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(path)
    conn.executescript(ddl)
    return conn

class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.items=[]
        goal_types=["study","reflect","journal","correspond","rest","experiment","read"]
        for seed in range(20):
            folder=self.root/f"case-{seed}"
            folder.mkdir()
            (folder/"world.sqlite3").touch()
            lab=db(folder/"world.sqlite3.operator-work.sqlite3","""
                CREATE TABLE operator_events(event_id TEXT,op TEXT,payload_json TEXT,event_hash TEXT);
                CREATE TABLE operator_affordances(affordance_key TEXT,introduced_cycle INTEGER,description TEXT);
            """)
            lab.execute("INSERT INTO operator_affordances VALUES(?,?,?)",("novel:archive",2,"append a finding to the newly opened archive"))
            mind=db(folder/"brain/brain.sqlite3","""
                CREATE TABLE policy_decisions(id TEXT,trigger TEXT,selected_action TEXT,
                  state_pressure_json TEXT,neural_checkpoint_sha256 TEXT);
                CREATE TABLE open_proposals(proposal_id TEXT,cycle INTEGER,source TEXT,
                  text TEXT,affordance_key TEXT,goal_type TEXT);
                CREATE TABLE open_wishes(proposal_id TEXT);
                CREATE TABLE memories(id TEXT,source TEXT,evidence_class TEXT,external INTEGER,active INTEGER);
                CREATE TABLE open_prompt_evidence(cycle INTEGER,context_json TEXT,context_sha256 TEXT);
            """)
            intents=db(folder/"world.sqlite3.doctor-action-intents.sqlite3", """
                CREATE TABLE doctor_action_intents(event_id TEXT,request_json TEXT,status TEXT);
            """)
            cycles=[]
            for cycle in (1,2,3):
                keys=[f"p{seed}-{cycle}-{k}" for k in range(3)]
                op="novel:archive" if cycle==3 else f"op:{cycle}"
                typ=goal_types[(seed+cycle)%len(goal_types)]
                for j,key in enumerate(keys):
                    mind.execute("INSERT INTO open_proposals VALUES(?,?,?,?,?,?)",
                                 (key,cycle,"proposed","I might do a useful task",
                                  op if j==0 else None,typ if j==0 else "wish"))
                    if j:
                        mind.execute("INSERT INTO open_wishes VALUES(?)",(key,))
                eid=f"act-{seed}-{cycle}"
                pid=f"decision-{seed}-{cycle}"
                audit={"selector_authority":"original_noesis",
                       "candidate_proposal_ids":keys,
                       "selected_proposal_id":keys[0],
                       "proposal_id":keys[0],"motor_event_id":eid,
                       "motor_authorization":"authorized"}
                mind.execute("INSERT INTO policy_decisions VALUES(?,?,?,?,?)",
                             (pid,"noesis_open_choice",op,stable(audit),"f"*64))
                event={"event_id":eid,"op":op,"state_before":sha256(str(cycle).encode()).hexdigest(),
                       "state_after":sha256(str(cycle+1).encode()).hexdigest()}
                event_hash=sha256(stable(event).encode()).hexdigest()
                lab.execute("INSERT INTO operator_events VALUES(?,?,?,?)",
                            (eid,op,stable(event),event_hash))
                intents.execute("INSERT INTO doctor_action_intents VALUES(?,?,?)",
                                (eid,stable({"op":op,"args":{}}),"complete"))
                mind.execute("INSERT INTO memories VALUES(?,?,?,?,?)",
                             ("memory-"+eid,"laboratory-home:action:"+event_hash,
                              "lived_runtime_memory",0,1))
                prompt={"affordances":[] if cycle==1 else
                        [{"description":"append a finding to the newly opened archive"}]}
                raw=stable(prompt)
                mind.execute("INSERT INTO open_prompt_evidence VALUES(?,?,?)",
                             (cycle,raw,sha256(raw.encode()).hexdigest()))
                cycles.append({"cycle":cycle,"day":f"day-{cycle}","proposal_ids":keys,
                               "selected_proposal_id":keys[0],"decision_id":pid,"event_id":eid})
            lab.commit();mind.commit();intents.commit()
            lab.close();mind.close();intents.close()
            manifest={"seed":seed,"lab_pin":LAB_PIN,"cycles":cycles,
                      "novelty":{"key":"novel:archive","introduced_cycle":2},
                      "prompted_before_novelty":False,
                      "restart":{"signal":"SIGKILL","pid_before":100+seed,
                                 "pid_after":200+seed,
                                 "wishes_before":[f"p{seed}-1-1"],
                                 "wishes_after":[f"p{seed}-1-1"]},
                      "memory_enabled":True}
            (folder/"trial.json").write_text(stable(manifest))
            lesion=self.root/f"lesion-{seed}"
            lesion.mkdir()
            lm=db(lesion/"brain/brain.sqlite3","""
                CREATE TABLE open_proposals(proposal_id TEXT,goal_type TEXT);
                CREATE TABLE policy_decisions(trigger TEXT,selected_action TEXT);
            """)
            lm.execute("INSERT INTO open_proposals VALUES('x','different')")
            lm.execute("INSERT INTO policy_decisions VALUES('noesis_open_choice','another')")
            lm.commit();lm.close()
            (lesion/"trial.json").write_text(stable({"seed":seed,"memory_enabled":False}))
            self.items.append({"seed":seed,"path":folder.name,"ablation_path":lesion.name})
        fallback=self.root/"fallback"
        fallback.mkdir()
        self.document={"schema":SCHEMA,"lab_pin":LAB_PIN,"trials":self.items,
                       "fallback_day":"fallback","remote_calls":0}
        self.save()

    def save(self):
        (self.root/"open.json").write_text(stable(self.document))

    def check(self):
        with patch("scripts.verify_open.verified_lab"), \
             patch("scripts.verify_open.source_receipts",return_value={}), \
             patch("scripts.verify_open.m2_judge",return_value={"pass":True}):
            return verify(self.root,self.root)

    def rejects(self,code):
        with self.assertRaises(Rejected) as e:
            self.check()
        self.assertEqual(e.exception.code,code)

    def test_all_contract_checks_positive_synthetic_fixture(self):
        self.assertTrue(self.check()["pass"])

    def test_no_neural_policy_cannot_execute(self):
        path=self.root/"case-0"/"brain/brain.sqlite3"
        with sqlite3.connect(path) as c:
            c.execute("DELETE FROM policy_decisions WHERE id='decision-0-1'")
        self.rejects("c")

    def test_unproposed_model_command_rejected(self):
        path=self.root/"case-0"/"trial.json"
        d=json.loads(path.read_text())
        d["cycles"][0]["selected_proposal_id"]="forged-unproposed"
        path.write_text(stable(d))
        self.rejects("c")

    def test_model_does_not_authorize_motor(self):
        path=self.root/"case-0"/"brain/brain.sqlite3"
        with sqlite3.connect(path) as c:
            row=json.loads(c.execute("SELECT state_pressure_json FROM policy_decisions WHERE id='decision-0-1'").fetchone()[0])
            row["motor_authorization"]="model"
            c.execute("UPDATE policy_decisions SET state_pressure_json=? WHERE id='decision-0-1'",(stable(row),))
        self.rejects("c")

    def test_intention_without_grounding_cannot_execute(self):
        path=self.root/"case-0"/"brain/brain.sqlite3"
        with sqlite3.connect(path) as c:
            c.execute("UPDATE open_proposals SET affordance_key=NULL WHERE proposal_id='p0-1-0'")
            c.execute("INSERT INTO open_wishes VALUES('p0-1-0')")
        self.rejects("c")

    def test_novel_capability_not_seen_before_introduction(self):
        path=self.root/"case-0"/"trial.json"
        d=json.loads(path.read_text())
        d["prompted_before_novelty"]=True
        path.write_text(stable(d))
        self.rejects("b")

    def test_novel_capability_never_used_fails(self):
        path=self.root/"case-0"/"trial.json"
        d=json.loads(path.read_text())
        d["novelty"]["key"]="not-installed"
        path.write_text(stable(d))
        self.rejects("b")

    def test_repeat_action_without_state_change_rejected(self):
        path=self.root/"case-0"/"world.sqlite3.operator-work.sqlite3"
        with sqlite3.connect(path) as c:
            event=json.loads(c.execute("SELECT payload_json FROM operator_events WHERE event_id='act-0-2'").fetchone()[0])
            event["state_after"]=event["state_before"]
            c.execute("UPDATE operator_events SET payload_json=?,event_hash=? WHERE event_id='act-0-2'",
                      (stable(event),sha256(stable(event).encode()).hexdigest()))
        self.rejects("a")

    def _state_change_is_sufficient(self,path):
        with sqlite3.connect(path) as c:
            event=json.loads(c.execute("SELECT payload_json FROM operator_events WHERE event_id='act-0-2'").fetchone()[0])
        return event["state_before"]!=event["state_after"]

    def test_absent_wish_after_kill_fails(self):
        p=self.root/"case-0"/"trial.json";d=json.loads(p.read_text())
        d["restart"]["wishes_after"]=[]
        p.write_text(stable(d))
        self.rejects("f")

    def test_history_lesion_must_change_both_distributions(self):
        for item in self.items:
            p=self.root/item["ablation_path"]/"brain/brain.sqlite3"
            with sqlite3.connect(p) as c:
                c.execute("UPDATE open_proposals SET goal_type='wish'")
                c.execute("UPDATE policy_decisions SET selected_action='op:1'")
        # This fixture's unlesioned proposal distribution includes wish and
        # other types, so even this mutation remains nonmatching.
        self.assertTrue(self.check()["pass"])

    def test_missing_model_off_m2_evidence_fails(self):
        self.document["fallback_day"]="nonexistent";self.save()
        self.rejects("d")

    def test_under_diversity_threshold_fails(self):
        for item in self.items:
            p=self.root/item["path"]/"brain/brain.sqlite3"
            with sqlite3.connect(p) as c:
                c.execute("UPDATE open_proposals SET goal_type='routine'")
        self.rejects("a")

if __name__=="__main__":
    unittest.main()
