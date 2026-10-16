"""Portable behavioral mechanisms. Synthetic scenarios do not qualify Articles."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

from doctor_lives.portable_life_policy import PortableLifePolicy, DecisionFrame, Opportunity


def frame(*, motives=None, goals=(), cue='unfinished_project', native=None):
    return DecisionFrame('I consider what I can actually do next.', 'event-observed-01',
                         motives or {'curiosity': .8, 'obligation': .4, 'wellbeing': .2},
                         frozenset(goals), native or {}, cue)


def options(domain='laboratory'):
    return [
        Opportunity(f'{domain}:prepare', domain, 'prepare',
                    {'curiosity': .5, 'obligation': .5}, effort=.2,
                    goal_ids=frozenset({'finish_project'})),
        Opportunity(f'{domain}:rush', domain, 'rush',
                    {'curiosity': .8}, effort=.12, risk=.5),
        Opportunity(f'{domain}:rest', domain, 'recover',
                    {'wellbeing': 1.0}, effort=.05),
    ]


class PortablePolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'policy.sqlite3'
        self.ai = PortableLifePolicy(self.path)

    def learn(self, suffix, action='prepare', cue='unfinished_project', success=True):
        return self.ai.record_outcome(source_receipt=f'world-{suffix}', action_key=f'lab:{action}',
                                      cue=cue, strategy=action, succeeded=success,
                                      verify_receipt=lambda receipt, key: receipt.startswith('world-') and key == f'lab:{action}')

    def test_any_domain_with_same_cognitive_goal(self):
        for domain in ('laboratory', 'correspondence', 'village', 'library'):
            with self.subTest(domain=domain):
                choice = self.ai.choose(frame(goals=['finish_project']), options(domain))
                self.assertEqual(choice.strategy, 'prepare')

    def test_competing_needs_reverse_choice_without_domain_rules(self):
        for domain in ('laboratory', 'correspondence', 'village'):
            sleepy = frame(motives={'wellbeing': 1.0, 'curiosity': .02, 'obligation': .0})
            self.assertEqual(self.ai.choose(sleepy, options(domain)).strategy, 'recover')

    def test_commitment_priority_survives_new_environment(self):
        first = self.ai.choose(frame(goals=['finish_project']), options('laboratory'), commit=True)
        self.assertEqual(first.strategy, 'prepare')
        restarted = PortableLifePolicy(self.path)
        second = restarted.choose(frame(goals=['finish_project']), options('correspondence'))
        self.assertEqual(second.strategy, 'prepare')
        self.assertEqual(len(second.alternatives), 3)

    def test_discovered_habits_transfer_as_strategy_not_room_object(self):
        f = frame(motives={'curiosity': .7, 'obligation': 0., 'wellbeing': 0.}, goals=())
        before = self.ai.choose(f, options('laboratory'))
        for n in range(8):
            self.learn(str(n), success=True)
        after = self.ai.choose(f, options('village'))
        self.assertEqual(after.strategy, 'prepare')
        self.assertGreater(after.score, before.score)
        self.assertEqual(PortableLifePolicy(self.path).habit('unfinished_project', 'prepare'), (8, 0))

    def test_failed_strategy_reduces_preference_without_hard_ban(self):
        f = frame(motives={'curiosity': .8, 'obligation': 0., 'wellbeing': 0.})
        initial = self.ai.choose(f, options('library'))
        for n in range(8):
            self.learn(f'fail-{n}', success=False)
        reduced = self.ai.choose(f, options('library'))
        score_before = dict(initial.alternatives)['library:prepare']
        score_after = dict(reduced.alternatives)['library:prepare']
        self.assertLess(score_after, score_before)

    def test_native_weight_is_bounded_and_ablated(self):
        f = frame(native={'rush': 1.0})
        full = self.ai.choose(f, options())
        lesioned = self.ai.choose(f, options(), native_enabled=False)
        self.assertLessEqual(abs(dict(full.alternatives)['laboratory:rush'] -
                                 dict(lesioned.alternatives)['laboratory:rush']), .12 + 1e-6)

    def test_observation_and_provenance_boundaries(self):
        with self.assertRaises(ValueError):
            self.ai.choose(DecisionFrame('fatigue=8', 'engineer-only', {'wellbeing': 1}), options())
        with self.assertRaises(ValueError):
            self.ai.choose(frame(), [Opportunity('secret', 'village', 'spy', {'curiosity': .9}, perceived=False)])
        with self.assertRaises(PermissionError):
            self.ai.record_outcome(source_receipt='fake', action_key='a', cue='c', strategy='s',
                                   succeeded=True, verify_receipt=lambda *_: False)
        self.assertEqual(self.ai.habit('c', 's'), (0, 0))

    def test_idempotent_and_conflicting_receipts(self):
        self.assertTrue(self.learn('one'))
        self.assertFalse(self.learn('one'))
        with self.assertRaises(RuntimeError):
            self.learn('one', success=False)
        self.assertEqual(self.ai.habit('unfinished_project', 'prepare'), (1, 0))

    def test_invalid_numeric_inputs_and_duplicate_actions(self):
        with self.assertRaises(ValueError):
            self.ai.choose(frame(motives={'curiosity': float('nan')}), options())
        with self.assertRaises(ValueError):
            self.ai.choose(frame(), options()+options())
        with self.assertRaises(ValueError):
            self.ai.choose(frame(), [Opportunity('x', 'd', 's', {'curiosity': 2})])

    def test_decisions_do_not_act_or_write_memories(self):
        self.ai.choose(frame(), options(), commit=True)
        with self.ai._db() as db:
            names = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertEqual(names, {'procedures', 'receipts', 'continuity'})
            self.assertEqual(db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0], 0)

    def test_counterfactual_lesions_expose_distinct_components(self):
        self.ai.choose(frame(goals=['finish_project']), options(), commit=True)
        for i in range(4): self.learn(str(i))
        f = frame(goals=['finish_project'], native={'rush': .5})
        complete = self.ai.choose(f, options('correspondence'))
        lesioned = self.ai.choose(f, options('correspondence'), learn_enabled=False,
                                 inertia_enabled=False, native_enabled=False)
        self.assertGreater(complete.score, lesioned.score)


class RandomizedPortabilityTests(unittest.TestCase):
    def test_240_seeded_counterfactuals_across_four_domains(self):
        """Varied labels and utility inputs, not authored scenario-specific code."""
        import random
        r = random.Random(20261016)
        with tempfile.TemporaryDirectory() as d:
            ai = PortableLifePolicy(Path(d)/'s.db')
            for n in range(240):
                domain = ['home', 'library', 'correspondence', 'village'][n % 4]
                m = r.random()
                opts = [Opportunity(f'{domain}:a:{n}', domain, 'prepare', {'curiosity': 1.0},
                                    effort=.3),
                        Opportunity(f'{domain}:b:{n}', domain, 'recover', {'wellbeing': 1.0},
                                    effort=.3)]
                f = frame(motives={'curiosity': m, 'wellbeing': 1-m}, cue='random')
                original = ai.choose(f, opts)
                relabeled = [Opportunity('other:'+x.key, 'unseen-world', x.strategy,
                                         x.effects, x.effort, x.risk) for x in opts]
                self.assertEqual(ai.choose(f, relabeled).strategy, original.strategy)
                reversed_needs = frame(motives={'curiosity': 1-m, 'wellbeing': m}, cue='random')
                changed = ai.choose(reversed_needs, opts)
                if abs(m-.5) > .001:
                    self.assertNotEqual(changed.strategy, original.strategy)

    def test_hidden_high_reward_opportunity_does_not_leak(self):
        with tempfile.TemporaryDirectory() as d:
            ai = PortableLifePolicy(Path(d)/'s.db')
            opts = options() + [Opportunity('invisible', 'nowhere', 'cheat',
                                            {'curiosity': 1.0}, perceived=False)]
            self.assertNotEqual(ai.choose(frame(), opts).key, 'invisible')
