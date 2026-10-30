"""Loopback HTML UI for the ONE canonical operator conversation ingress path."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .lab_runtime import _exclusive_host
from .operator_conversation import OperatorConversation

_HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pretorius | Operator Conversation</title>
<style>body{font:17px system-ui;background:#17191e;color:#ebdfc4;max-width:760px;
margin:3rem auto;padding:1rem}h1{font-size:1.5rem}#log{min-height:300px;white-space:pre-wrap}
article{border-bottom:1px solid #48423a;padding:1rem 0}small{color:#aca28f}
textarea{width:100%;box-sizing:border-box;background:#23262c;color:#fff;
border:1px solid #666;padding:1rem;font:inherit}button{padding:.7rem 1.5rem;
background:#ae9455;border:0;font:inherit;cursor:pointer}</style></head>
<body><h1>Doctor Pretorius</h1><p>Local conversation, one original BrainStore.</p>
<div id="log" role="log" aria-live="polite"></div>
<form id="form"><label for="message">Speak to the Doctor</label>
<textarea id="message" required rows="3" maxlength="800"></textarea>
<button type="submit">Send</button></form>
<script>
const log=document.getElementById('log'), form=document.getElementById('form');
form.onsubmit=async(e)=>{e.preventDefault();
const input=document.getElementById('message');const text=input.value;input.value='';
const op=document.createElement('article');op.textContent='Operator: '+text;log.append(op);
try{
const r=await fetch('/message',{method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({text,request_id:'operator_'+crypto.randomUUID().replaceAll('-','')})});
const value=await r.json();
if(!r.ok)throw new Error(value.error||'Conversation failed');
const el=document.createElement('article');el.textContent='Pretorius: '+value.text;
const small=document.createElement('small');small.textContent='Evidence-backed claims: '+
(value.claims||[]).length+' | Model called: '+value.model_called;
el.append(small);log.append(el);
}catch(e){const err=document.createElement('article');err.textContent='Error: '+e.message;log.append(err);}
};</script></body></html>"""

def serve(state: Path, world: Path, *, port: int = 8766, model: str|None = None) -> int:
    if not 1024 <= port <= 65535:
        raise ValueError("Use an unprivileged loopback port")
    # The local page and terminal call exactly the same authoritative ingress.
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/":
                self.send_error(404);return
            raw=_HTML.encode()
            self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(raw)));self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            if self.path!="/message":
                self.send_error(404);return
            if self.headers.get("Content-Type","").split(";")[0]!="application/json":
                self.send_error(415);return
            try:
                length=int(self.headers.get("Content-Length","0"))
                if not 0 < length <= 4096:
                    raise ValueError("Message JSON size invalid")
                value=json.loads(self.rfile.read(length).decode("utf-8"))
                with _exclusive_host(state,world):
                    answer=OperatorConversation(state,world).submit(
                        value["text"],request_id=value.get("request_id"),
                        model=model,day=int(value.get("day",1)))
                body=json.dumps(answer,ensure_ascii=False,default=str).encode()
                status=200
            except (ValueError,KeyError,TypeError,RuntimeError,PermissionError,FileNotFoundError) as exc:
                body=json.dumps({"error":str(exc)}).encode();status=400
            self.send_response(status)
            self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header("Content-Length",str(len(body)));self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return
    server=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    print(f"Pretorius local conversation: http://127.0.0.1:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
