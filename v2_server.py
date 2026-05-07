#!/data/data/com.termux/files/usr/bin/python3
"""
CyberTermux Remote Support Panel — Real Backend Server
Run: python server.py
"""

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import json
import time
import random
import threading
import os
import socket

app = Flask(__name__, static_folder='.')
CORS(app)

# ─── In-memory session ───
connected_devices = {}
session_logs = []
device_id_counter = 0

# ─── HTML TEMPLATE (Inlined) ───
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"/>
<title>CyberTermux — Remote Panel</title>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Fira+Code:wght@300;400;500;600;700&display=swap');
:root{--ng:#00ff41;--nc:#00f0ff;--np:#b300ff;--bg:#0a0a0f;--gb:rgba(10,10,20,0.75)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Rajdhani',sans-serif;background:var(--bg);color:#d4d4d4;overflow-x:hidden;min-height:100vh}
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:#0a0a0f}
::-webkit-scrollbar-thumb{background:var(--ng);border-radius:3px}
.scanlines{position:fixed;top:0;left:0;width:100%;height:100%;z-index:9999;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,65,0.015)2px,rgba(0,255,65,0.015)4px)}
.glass-card{background:var(--gb);backdrop-filter:blur(16px) saturate(180%);-webkit-backdrop-filter:blur(16px) saturate(180%);border:1px solid rgba(0,255,65,0.15);border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,0.6);transition:all 0.3s ease}
.glass-card:hover{border-color:rgba(0,255,65,0.35);box-shadow:0 0 15px rgba(0,255,65,0.2),0 8px 32px rgba(0,0,0,0.6)}
.neon-green{color:var(--ng);text-shadow:0 0 7px rgba(0,255,65,0.5)}
.neon-cyan{color:var(--nc);text-shadow:0 0 7px rgba(0,240,255,0.5)}
.neon-purple{color:var(--np);text-shadow:0 0 7px rgba(179,0,255,0.5)}
.font-cyber{font-family:'Orbitron',monospace;letter-spacing:1px}
.font-term{font-family:'Fira Code','Courier New',monospace}
.btn-neon{position:relative;display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:10px 24px;border:1px solid var(--ng);border-radius:8px;background:rgba(0,255,65,0.06);color:var(--ng);font-family:'Orbitron',monospace;font-size:0.75rem;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:all 0.25s ease;box-shadow:0 0 8px rgba(0,255,65,0.15)}
.btn-neon:hover{background:rgba(0,255,65,0.15);box-shadow:0 0 20px rgba(0,255,65,0.4),inset 0 0 20px rgba(0,255,65,0.05);transform:translateY(-1px)}
.btn-cyan{border-color:var(--nc);color:var(--nc);background:rgba(0,240,255,0.06);box-shadow:0 0 8px rgba(0,240,255,0.15)}
.btn-cyan:hover{background:rgba(0,240,255,0.15);box-shadow:0 0 20px rgba(0,240,255,0.4)}
.status-dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;animation:pulse-dot 1.8s ease-in-out infinite}
.status-dot.online{background:var(--ng);box-shadow:0 0 10px rgba(0,255,65,0.7)}
.status-dot.offline{background:#555;box-shadow:none;animation:none}
@keyframes pulse-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.5;transform:scale(0.85)}}
.notif-container{position:fixed;top:20px;right:20px;z-index:10000;display:flex;flex-direction:column;gap:10px;max-width:360px;width:calc(100% - 40px);pointer-events:none}
.notif-toast{pointer-events:auto;background:rgba(5,5,15,0.92);backdrop-filter:blur(20px);border:1px solid rgba(0,255,65,0.2);border-radius:12px;padding:14px 18px;display:flex;align-items:flex-start;gap:12px;box-shadow:0 8px 32px rgba(0,0,0,0.7);transform:translateX(120%);opacity:0;transition:all 0.4s cubic-bezier(0.16,1,0.3,1)}
.notif-toast.show{transform:translateX(0);opacity:1}
.notif-toast .notif-close{margin-left:auto;background:none;border:none;color:#888;cursor:pointer}
.terminal-window{background:rgba(0,0,0,0.85);border:1px solid rgba(0,255,65,0.2);border-radius:12px;font-family:'Fira Code','Courier New',monospace;font-size:0.82rem;line-height:1.6;overflow:hidden}
.terminal-body{padding:14px;min-height:200px;max-height:300px;overflow-y:auto}
.terminal-body .log-line{opacity:0;animation:fadeInLog 0.3s ease forwards}
@keyframes fadeInLog{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:640px){.terminal-body{min-height:140px;max-height:180px;font-size:0.75rem}.btn-neon{font-size:0.65rem;padding:8px 16px}}
</style>
</head>
<body>
<div class="scanlines"></div>
<div id="notif-container" class="notif-container"></div>

<div style="padding:16px;max-width:1280px;margin:0 auto;width:100%">

  <!-- Header -->
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:16px">
    <div>
      <h1 class="font-cyber neon-green" style="font-size:1.5rem;font-weight:700;letter-spacing:2px;">
        <i class="fas fa-skull-crossbones"></i> CYBERTERMUX
      </h1>
      <p class="font-term" style="font-size:0.7rem;color:#666;">REMOTE SUPPORT // <span id="status-badge" class="neon-green">● ONLINE</span></p>
    </div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;">
      <span class="font-term" style="font-size:0.7rem;color:#555;padding:8px 12px;background:rgba(0,0,0,0.3);border-radius:8px;border:1px solid rgba(0,255,65,0.1);">
        <i class="fas fa-users"></i> <span id="conn-count">0</span> connected
      </span>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">

    <!-- LEFT: Terminal + Controls -->
    <div style="display:flex;flex-direction:column;gap:16px;">

      <div class="glass-card" style="padding:16px;overflow:hidden;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span class="font-cyber neon-green" style="font-size:0.75rem;"><i class="fas fa-terminal"></i> LIVE TERMINAL</span>
          <button class="btn-neon" style="padding:4px 12px;font-size:0.6rem;" onclick="document.getElementById('terminal-body').innerHTML='<div class=\\'log-line\\'><span class=\\'info\\'>[SYSTEM]</span> <span class=\\'output\\'>Terminal cleared</span></div>'">Clear</button>
        </div>
        <div class="terminal-window" style="border:none;">
          <div class="terminal-body" id="terminal-body">
            <div class="log-line"><span class="info">[SYSTEM]</span> <span class="output">Server started at <span id="server-time">--</span></span></div>
            <div class="log-line"><span class="info">[AUTH]</span> <span class="output">Waiting for connections...</span></div>
          </div>
        </div>
        <div style="display:flex;gap:8px;margin-top:8px;">
          <input id="cmd-input" class="font-term" style="flex:1;background:rgba(0,0,0,0.5);border:1px solid rgba(0,255,65,0.15);border-radius:6px;padding:8px 12px;color:var(--ng);font-size:0.8rem;outline:none;" placeholder="type command here..." onkeypress="if(event.key==='undefined'||event.key==='Enter')sendCommand()"/>
          <button class="btn-neon" style="padding:8px 16px;font-size:0.7rem;" onclick="sendCommand()"><i class="fas fa-paper-plane"></i></button>
        </div>
        <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap;">
          <button class="btn-neon btn-cyan" style="padding:6px 14px;font-size:0.6rem;" onclick="sendAction('vibrate')"><i class="fas fa-mobile-alt"></i> Vibrate</button>
          <button class="btn-neon btn-cyan" style="padding:6px 14px;font-size:0.6rem;" onclick="sendAction('flash')"><i class="fas fa-bolt"></i> Flash</button>
          <button class="btn-neon" style="padding:6px 14px;font-size:0.6rem;border-color:#ffaa00;color:#ffaa00;" onclick="sendAction('notify')"><i class="fas fa-bell"></i> Notify</button>
          <button class="btn-neon" style="padding:6px 14px;font-size:0.6rem;border-color:#ff3355;color:#ff3355;" onclick="sendAction('alert')"><i class="fas fa-exclamation-triangle"></i> Alert</button>
        </div>
      </div>

      <!-- Server Info -->
      <div class="glass-card" style="padding:16px;">
        <div class="font-cyber neon-cyan" style="font-size:0.75rem;margin-bottom:10px;"><i class="fas fa-server"></i> SERVER INFO</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 12px;font-size:0.85rem;font-family:'Fira Code',monospace;">
          <span style="color:#888;">Host</span><span style="color:#ddd;" id="srv-host">--</span>
          <span style="color:#888;">Port</span><span style="color:var(--ng);" id="srv-port">5000</span>
          <span style="color:#888;">Clients</span><span style="color:var(--nc);" id="srv-clients">0</span>
          <span style="color:#888;">Status</span><span class="neon-green">● RUNNING</span>
        </div>
      </div>
    </div>

    <!-- RIGHT: Devices + Chat -->
    <div style="display:flex;flex-direction:column;gap:16px;">

      <!-- Connected Devices -->
      <div class="glass-card" style="padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <span class="font-cyber neon-green" style="font-size:0.75rem;"><i class="fas fa-plug"></i> CONNECTED DEVICES</span>
          <span class="font-term" style="font-size:0.6rem;color:#555;" id="dev-count">0 devices</span>
        </div>
        <div id="device-list" style="display:flex;flex-direction:column;gap:6px;">
          <div style="text-align:center;padding:20px;color:#444;font-family:'Fira Code',monospace;font-size:0.8rem;">
            <i class="fas fa-hourglass-half" style="font-size:1.5rem;display:block;margin-bottom:8px;opacity:0.4;"></i>
            Waiting for devices to connect...
          </div>
        </div>
      </div>

      <!-- Quick Chat -->
      <div class="glass-card" style="padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span class="font-cyber neon-purple" style="font-size:0.75rem;"><i class="fas fa-comment"></i> SEND MESSAGE</span>
        </div>
        <textarea id="msg-text" style="width:100%;background:rgba(0,0,0,0.4);border:1px solid rgba(179,0,255,0.15);border-radius:8px;padding:10px;color:#ddd;font-family:'Fira Code',monospace;font-size:0.8rem;resize:vertical;min-height:60px;outline:none;" placeholder="Type message for connected devices..."></textarea>
        <button class="btn-neon" style="margin-top:8px;width:100%;font-size:0.65rem;border-color:var(--np);color:var(--np);" onclick="sendMessage()">
          <i class="fas fa-bullhorn"></i> Broadcast Message
        </button>
      </div>

      <!-- Connection Link -->
      <div class="glass-card" style="padding:16px;">
        <div class="font-cyber neon-cyan" style="font-size:0.75rem;margin-bottom:8px;"><i class="fas fa-link"></i> CLIENT CONNECTION LINK</div>
        <div style="background:rgba(0,0,0,0.4);border:1px solid rgba(0,240,255,0.1);border-radius:8px;padding:10px 14px;font-family:'Fira Code',monospace;font-size:0.75rem;word-break:break-all;">
          <span style="color:var(--nc);" id="conn-link">http://<span id="link-ip">--</span>:5000/client</span>
        </div>
        <button class="btn-neon btn-cyan" style="margin-top:8px;width:100%;font-size:0.6rem;" onclick="copyLink()"><i class="fas fa-copy"></i> Copy Link to Share</button>
        <p class="font-term" style="font-size:0.6rem;color:#555;margin-top:6px;text-align:center;">Dost ko yeh link bhejo — woh browser mein kholega</p>
      </div>
    </div>
  </div>

  <footer style="text-align:center;padding:20px 0 8px;font-size:0.6rem;color:#333;font-family:'Fira Code',monospace;border-top:1px solid rgba(0,255,65,0.04);margin-top:16px;">
    CYBERTERMUX v3.1.2 // RUNNING ON LOCAL NETWORK
  </footer>
</div>

<script>
// ─── NOTIFICATIONS ───
function pushNotif(type, title, msg) {
  const c = document.getElementById('notif-container');
  const icons = {success:'fa-check-circle',info:'fa-info-circle',warn:'fa-exclamation-triangle',error:'fa-times-circle'};
  const colors = {success:'var(--ng)',info:'var(--nc)',warn:'#ffaa00',error:'#ff3355'};
  const t = document.createElement('div'); t.className = 'notif-toast';
  t.innerHTML = '<span style="color:'+colors[type]+';font-size:1.3rem;min-width:28px"><i class="fas '+icons[type]+'"></i></span><div style="flex:1"><div class="font-cyber" style="font-size:0.7rem;color:#ddd">'+title+'</div><div class="font-term" style="font-size:0.72rem;color:#aaa">'+msg+'</div></div><button class="notif-close" onclick="this.parentElement.remove()"><i class="fas fa-times"></i></button>';
  c.appendChild(t);
  requestAnimationFrame(()=>t.classList.add('show'));
  setTimeout(()=>{t.classList.remove('show');t.classList.add('hide');setTimeout(()=>t.remove(),400)},4500);
}

// ─── POLL SERVER ───
let pollInterval = null;
function startPolling() {
  pollInterval = setInterval(() => {
    fetch('/api/status').then(r=>r.json()).then(d=>{
      document.getElementById('conn-count').textContent = d.devices;
      document.getElementById('dev-count').textContent = d.devices + ' devices';
      document.getElementById('srv-clients').textContent = d.devices;
      // Update device list
      const list = document.getElementById('device-list');
      if(d.devices===0) {
        list.innerHTML = '<div style="text-align:center;padding:20px;color:#444;font-family:\'Fira Code\',monospace;font-size:0.8rem;"><i class="fas fa-hourglass-half" style="font-size:1.5rem;display:block;margin-bottom:8px;opacity:0.4;"></i>Waiting for devices to connect...</div>';
      } else {
        let html = '';
        d.device_list.forEach(dev => {
          html += '<div style="display:flex;align-items:center;gap:12px;padding:8px 12px;background:rgba(0,255,65,0.03);border-radius:8px;border:1px solid rgba(0,255,65,0.08);">';
          html += '<i class="fas fa-mobile-alt neon-green"></i>';
          html += '<div style="flex:1"><div class="font-term" style="font-size:0.8rem;color:#ddd;">'+dev.name+'</div><div class="font-term" style="font-size:0.6rem;color:#666;">'+dev.ip+' • '+dev.ua+'</div></div>';
          html += '<span class="status-dot online"></span></div>';
        });
        list.innerHTML = html;
      }
      // Terminal logs from server
      if(d.logs && d.logs.length > 0) {
        const tb = document.getElementById('terminal-body');
        d.logs.forEach(log => {
          if(!tb.querySelector('[data-logid="'+log.id+'"]')) {
            const div = document.createElement('div');
            div.className = 'log-line';
            div.setAttribute('data-logid', log.id);
            div.innerHTML = '<span class="'+log.type+'">['+log.label+']</span> <span class="output">'+log.msg+'</span>';
            tb.appendChild(div);
            tb.scrollTop = tb.scrollHeight;
          }
        });
      }
    }).catch(()=>{});
  }, 1500);
}

// ─── SEND COMMAND ───
function sendCommand() {
  const input = document.getElementById('cmd-input');
  const cmd = input.value.trim();
  if(!cmd) return;
  fetch('/api/command', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({command:cmd})})
  .then(r=>r.json()).then(d=>{
    if(d.status==='ok') pushNotif('success','Command', 'Executed: '+cmd);
    input.value = '';
  }).catch(()=>pushNotif('error','Error','Failed to send command'));
}

// ─── SEND ACTION ───
function sendAction(action) {
  const labels = {vibrate:'📳 Vibration',flash:'⚡ Flash',notify:'🔔 Notification',alert:'🚨 Alert'};
  fetch('/api/action', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({action:action})})
  .then(r=>r.json()).then(d=>{
    pushNotif('info','Action', labels[action]+' sent to all devices');
  }).catch(()=>pushNotif('error','Error','Failed to send action'));
}

// ─── SEND MESSAGE ───
function sendMessage() {
  const msg = document.getElementById('msg-text').value.trim();
  if(!msg) { pushNotif('warn','Message','Type a message first'); return; }
  fetch('/api/message', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:msg})})
  .then(r=>r.json()).then(d=>{
    pushNotif('success','Message','Broadcast sent: "'+msg.substring(0,30)+'..."');
  }).catch(()=>pushNotif('error','Error','Failed to send message'));
}

// ─── COPY LINK ───
function copyLink() {
  const link = document.getElementById('conn-link').textContent;
  navigator.clipboard.writeText(link).then(()=>{
    pushNotif('success','Copied','Link copied to clipboard!');
  }).catch(()=>{
    const ta = document.createElement('textarea');
    ta.value = link; ta.style.position='fixed'; ta.style.left='-9999px';
    document.body.appendChild(ta); ta.select(); document.execCommand('copy');
    document.body.removeChild(ta);
    pushNotif('success','Copied','Link copied!');
  });
}

// ─── INIT ───
document.addEventListener('DOMContentLoaded', function() {
  fetch('/api/info').then(r=>r.json()).then(d=>{
    document.getElementById('server-time').textContent = d.time;
    document.getElementById('srv-host').textContent = d.host;
    document.getElementById('link-ip').textContent = d.host+':'+d.port;
    document.getElementById('conn-link').innerHTML = 'http://'+d.host+':'+d.port+'/client';
  });
  startPolling();
});
</script>
</body>
</html>'''

# ─── CLIENT PAGE (jo dost kholega) ───
CLIENT_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"/>
<title>CyberTermux — Client</title>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600&family=Fira+Code:wght@400;500&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Rajdhani',sans-serif;background:#0a0a0f;color:#d4d4d4;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:16px}
.glass-card{background:rgba(10,10,20,0.8);backdrop-filter:blur(16px);border:1px solid rgba(0,255,65,0.15);border-radius:16px;padding:24px;max-width:420px;width:100%;text-align:center;box-shadow:0 8px 32px rgba(0,0,0,0.6)}
.neon-green{color:#00ff41;text-shadow:0 0 7px rgba(0,255,65,0.5)}
.neon-cyan{color:#00f0ff;text-shadow:0 0 7px rgba(0,240,255,0.5)}
.font-cyber{font-family:'Orbitron',monospace;letter-spacing:1px}
.font-term{font-family:'Fira Code','Courier New',monospace}
.status-dot{display:inline-block;width:12px;height:12px;border-radius:50%;background:#00ff41;box-shadow:0 0 10px rgba(0,255,65,0.7);animation:pulse-dot 1.8s ease-in-out infinite}
@keyframes pulse-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.5;transform:scale(0.85)}}
.btn-neon{display:inline-flex;align-items:center;gap:8px;padding:10px 24px;border:1px solid #00ff41;border-radius:8px;background:rgba(0,255,65,0.06);color:#00ff41;font-family:'Orbitron',monospace;font-size:0.7rem;font-weight:600;letter-spacing:1.5px;cursor:pointer;transition:all 0.25s ease}
.btn-neon:hover{background:rgba(0,255,65,0.15);box-shadow:0 0 20px rgba(0,255,65,0.4)}
</style>
</head>
<body>
<div class="glass-card">
  <div style="margin-bottom:16px;">
    <i class="fas fa-shield-haltered" style="font-size:3rem;color:var(--ng);opacity:0.5;"></i>
  </div>
  <div class="font-cyber neon-green" style="font-size:1.2rem;margin-bottom:4px;">● CYBERTERMUX</div>
  <div class="font-term" style="font-size:0.7rem;color:#666;margin-bottom:16px;">Remote Support Client</div>
  
  <div id="conn-status" style="margin-bottom:16px;">
    <span class="status-
