"""Operator-only loopback scene and conversational audio surface.

No raw world envelope or engine state is delivered to the subject renderer.
Browser speech is operator presentation, not proof of a lived utterance.
"""
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import secrets
from .small_tower import SmallTowerSource,run_tower_pulse,_bind
from .lab_runtime import _exclusive_host
from .first_person_governance import first_person_line
from .organs import SixOrganRuntime

def scene(snapshot):
    lines=snapshot["narrative"]
    if type(lines) is not list or not all(first_person_line(line)==line for line in lines):
        raise PermissionError("Unqualified scene projection")
    return {"narrative":lines,"occupied":bool(snapshot["busy"]),"deceased":bool(snapshot["deceased"])}

_HTML="""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pretorius | Small Tower</title>
<style>
:root{color-scheme:dark;--ink:#e9dfcd;--gold:#c6ac76;--paper:#262421;--edge:#544c3d}
*{box-sizing:border-box}body{margin:0;background:#171816;color:var(--ink);font:16px Georgia,serif}
main{max-width:1050px;margin:auto;padding:30px 20px}header{border-bottom:1px solid var(--edge);padding-bottom:18px}
h1{font-weight:normal;letter-spacing:.08em;margin:0;font-size:30px}h2{font-weight:normal;font-size:20px}
small,.muted{color:#bdb5a5;font:13px system-ui}section{border:1px solid var(--edge);padding:20px;background:var(--paper);border-radius:8px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:20px}
#scene{min-height:220px;background:#1b1c19;border:1px solid var(--edge);padding:16px}
#objects{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px}
.object{border:1px solid var(--edge);padding:12px;text-align:center;color:var(--gold)}
#narrative,#log{white-space:pre-wrap;line-height:1.55}#log{min-height:160px;max-height:400px;overflow-y:auto}
textarea,select,button{font:14px system-ui;color:var(--ink);background:#37342d;border:1px solid var(--edge);border-radius:5px;padding:9px}
textarea{width:100%;min-height:80px;margin:12px 0}button{cursor:pointer;margin:4px 3px 4px 0}
button:disabled{opacity:.5}button:focus-visible,textarea:focus-visible,select:focus-visible{outline:2px solid var(--gold)}
.controls{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}article{border-bottom:1px solid var(--edge);padding:12px 0}
#status{min-height:24px}.error{color:#efa99c}@media(max-width:720px){.grid{grid-template-columns:1fr}}
</style></head><body><main><header><small>CANONICAL DOCTOR / PRE-VILLAGE REHEARSAL</small>
<h1>The Small Tower</h1><p class="muted">A view of the Doctor's currently witnessed surroundings, not an omniscient map.</p></header>
<div class="grid"><section><h2>My surroundings</h2><div id="scene"><h3 id="room">Current scene</h3><div id="objects"></div></div>
<p id="narrative" aria-live="polite"></p><div class="controls"><button id="refresh">Observe scene</button><button id="pulse">Offer one opportunity</button></div></section>
<section><h2>Conversation</h2><div id="log" role="log" aria-live="polite"></div><form id="form">
<label for="message">Speak to the Doctor</label><textarea id="message" maxlength="800" required></textarea>
<button type="submit">Send</button><button type="button" id="mic">Dictate</button></form>
<div class="controls"><label for="voices">Local playback voice</label><select id="voices"></select>
<button id="speak">Read last reply aloud</button><button id="stop">Stop audio</button></div>
<p class="muted">Voice playback uses locally installed browser voices. Dictation is optional and may use your browser's remote speech service; the transcript can be reviewed before sending. Audio is not recorded into the Doctor's memory as an emitted utterance.</p>
</section></div><p id="status" role="status"></p></main>
<script>
const token="__TOKEN__",worldAuthorized=__AUTHORIZED__;
const $=id=>document.getElementById(id);let lastReply="",busy=false;
function status(message,error=false){$('status').textContent=message;$('status').className=error?'error':''}
function add(who,text){const el=document.createElement('article');el.textContent=who+': '+text;$('log').append(el);$('log').scrollTop=$('log').scrollHeight}
function draw(data){const lines=data.narrative;const room=lines.find(x=>x.startsWith('I am in my '))||'Current surroundings';
$('room').textContent=room.replace(/^I am in my /,'').replace(/\.$/,'');$('objects').replaceChildren();
for(const line of lines.filter(x=>x.startsWith('I can see ')||x.startsWith('I see '))){
const el=document.createElement('div');el.className='object';el.textContent=line.replace(/^I (can see|see) /,'').replace(/\.$/,'');$('objects').append(el)}
$('narrative').textContent=lines.join('\n');$('pulse').disabled=!worldAuthorized||data.deceased||busy}
async function call(path,value){const options={headers:{'X-Tower-Token':token}};if(value!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(value)}
const r=await fetch(path,options),d=await r.json();if(!r.ok)throw Error(d.error||'Local operation unavailable');return d}
async function task(fn){if(busy)return;busy=true;$('pulse').disabled=true;try{await fn()}catch(e){status(e.message,true)}finally{busy=false;$('pulse').disabled=!worldAuthorized}}
async function refresh(){draw(await call('/scene'));status('Scene read from the original Tower.')}
$('refresh').onclick=()=>task(refresh);$('pulse').onclick=()=>task(async()=>{draw(await call('/pulse',{}));status('One bounded opportunity completed.');});
$('form').onsubmit=e=>{e.preventDefault();task(async()=>{const text=$('message').value.trim();if(!text)return;const d=await call('/message',{text});$('message').value='';add('Operator',text);lastReply=d.text;add('Pretorius',lastReply);status('Response prepared.');})};
function voices(){const vs=window.speechSynthesis?.getVoices().filter(v=>v.localService)||[];$('voices').replaceChildren();
for(const v of vs){const opt=document.createElement('option');opt.value=v.voiceURI;opt.textContent=v.name+' ('+v.lang+')';$('voices').append(opt)}$('speak').disabled=!vs.length}
if(window.speechSynthesis){speechSynthesis.onvoiceschanged=voices;voices()}else{$('speak').disabled=true}
$('speak').onclick=()=>{if(!lastReply)return;const v=speechSynthesis.getVoices().find(v=>v.localService&&v.voiceURI===$('voices').value);if(!v){status('No local voice selected.',true);return}speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(lastReply);u.voice=v;u.onerror=()=>status('Audio playback failed.',true);u.onend=()=>status('Browser playback finished.');speechSynthesis.speak(u)};
$('stop').onclick=()=>window.speechSynthesis?.cancel();
const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
$('mic').disabled=!Recognition;$('mic').onclick=()=>{if(!confirm('Use browser speech recognition? Audio may be processed by the browser provider.'))return;const rec=new Recognition();rec.lang='en-US';rec.onresult=e=>{$('message').value=e.results[0][0].transcript;status('Review the transcript before sending.')};rec.onerror=()=>status('Dictation unavailable.',true);rec.start()};
task(refresh);
</script></body></html>"""

def serve(state,source,world,*,port=8767,model="qwen3:1.5b",authorize_world=False):
    from .local_subject_gloss import valid_local_model
    if type(authorize_world) is not bool or not 1024<=port<=65535 or not valid_local_model(model):
        raise ValueError("Invalid local Tower interface settings")
    state=Path(state);world=Path(world)
    if not (state/"brain.sqlite3").is_file() or not world.is_file():
        raise FileNotFoundError("Initialize a dedicated Tower rehearsal first")
    token=secrets.token_urlsafe(32)
    html=_HTML.replace("__TOKEN__",token).replace("__AUTHORIZED__",json.dumps(authorize_world))
    def current():
        with _exclusive_host(state,world):
            rt=SixOrganRuntime.open(state)
            provider=SmallTowerSource(source,world)
            snapshot=provider.snapshot()
            _bind(rt,provider,snapshot)
            return scene(snapshot)
    class Handler(BaseHTTPRequestHandler):
        def _write(self,status,value,kind="application/json"):
            data=(json.dumps(value,ensure_ascii=False) if kind=="application/json" else value).encode()
            self.send_response(status)
            self.send_header("Content-Type",kind+"; charset=utf-8")
            self.send_header("Content-Length",str(len(data)))
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.end_headers();self.wfile.write(data)
        def _local(self):
            return self.headers.get("Host")==f"127.0.0.1:{port}"
        def _auth(self):
            return self._local() and secrets.compare_digest(self.headers.get("X-Tower-Token",""),token)
        def do_GET(self):
            if not self._local():self.send_error(403);return
            if self.path=="/":self._write(200,html,"text/html");return
            if not self._auth():self.send_error(403);return
            if self.path!="/scene":self.send_error(404);return
            try:self._write(200,current())
            except Exception:self._write(409,{"error":"Scene unavailable; check the local host."})
        def do_POST(self):
            if not self._auth():self.send_error(403);return
            if self.headers.get("Content-Type","").split(";")[0]!="application/json":
                self.send_error(415);return
            try:
                n=int(self.headers.get("Content-Length","0"))
                if not 0<n<=4096:raise ValueError("Invalid request size")
                value=json.loads(self.rfile.read(n))
                if self.path=="/pulse":
                    if value!={} or not authorize_world:raise PermissionError("World authority disabled")
                    result=run_tower_pulse(state,source,world,authorize=True,steps=100)
                    self._write(200,scene({"narrative":result["subject_narrative"],
                        "busy":result["source_receipt"]["busy"],"deceased":result["source_receipt"]["deceased"]}))
                elif self.path=="/message":
                    if type(value) is not dict or set(value)!={"text"}:raise ValueError("Invalid message")
                    from .ipseity_local import local_turn
                    with _exclusive_host(state,world):
                        result=local_turn(state,user_text=value["text"],model=model,governed=True)
                    self._write(200,{"text":result})
                else:self.send_error(404)
            except Exception:self._write(409,{"error":"Operation unavailable; recover pending local work if necessary."})
        def log_message(self,*args):return
    server=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    print(f"Small Tower operator interface: http://127.0.0.1:{port}/",flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
    return 0
