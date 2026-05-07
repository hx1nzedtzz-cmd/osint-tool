#!/data/data/com.termux/files/usr/bin/python3
"""
CyberTermux Remote Support Panel — v3.2
Run: python3 server.py
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json, time, random, threading, os, socket

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

connected_devices = {}
session_logs = []
device_id_counter = 0

# ─── Routes ───

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/client')
def client():
    return send_from_directory('.', 'client.html')

@app.route('/api/info')
def api_info():
    host = get_local_ip()
    return jsonify({
        'host': host,
        'port': 5000,
        'time': time.strftime('%H:%M:%S'),
        'devices': len(connected_devices)
    })

@app.route('/api/status')
def api_status():
    device_list = []
    for cid, dev in connected_devices.items():
        device_list.append({
            'id': cid,
            'name': dev.get('name', 'Unknown'),
            'ip': dev.get('ip', '--'),
            'ua': dev.get('ua', '--')
        })
    return jsonify({
        'devices': len(connected_devices),
        'device_list': device_list,
        'logs': session_logs[-20:]
    })

@app.route('/api/command', methods=['POST'])
def api_command():
    data = request.json
    cmd = data.get('command', '')
    log_entry = {
        'id': str(int(time.time()*1000)),
        'type': 'cmd',
        'label': 'CMD',
        'msg': cmd
    }
    session_logs.append(log_entry)
    for cid in connected_devices:
        connected_devices[cid]['pending_command'] = cmd
    return jsonify({'status': 'ok', 'command': cmd})

@app.route('/api/action', methods=['POST'])
def api_action():
    data = request.json
    action = data.get('action', '')
    log_entry = {
        'id': str(int(time.time()*1000)),
        'type': 'action',
        'label': 'ACTION',
        'msg': 'Triggered: ' + action
    }
    session_logs.append(log_entry)
    for cid in connected_devices:
        connected_devices[cid]['pending_action'] = action
    return jsonify({'status': 'ok', 'action': action})

@app.route('/api/message', methods=['POST'])
def api_message():
    data = request.json
    msg = data.get('message', '')
    log_entry = {
        'id': str(int(time.time()*1000)),
        'type': 'msg',
        'label': 'MSG',
        'msg': 'Broadcast: ' + msg[:50]
    }
    session_logs.append(log_entry)
    for cid in connected_devices:
        connected_devices[cid]['pending_message'] = msg
    return jsonify({'status': 'ok', 'message': msg})

@app.route('/api/client/register', methods=['POST'])
def api_client_register():
    global device_id_counter
    data = request.json
    device_id_counter += 1
    cid = str(device_id_counter)
    ip = request.remote_addr or '--'
    connected_devices[cid] = {
        'name': data.get('name', 'Unknown'),
        'ip': ip,
        'ua': data.get('ua', ''),
        'pending_command': None,
        'pending_action': None,
        'pending_message': None
    }
    log_entry = {
        'id': str(int(time.time()*1000)),
        'type': 'success',
        'label': 'CONNECT',
        'msg': 'Device connected: ' + data.get('name', 'Unknown') + ' (' + ip + ')'
    }
    session_logs.append(log_entry)
    return jsonify({'client_id': cid, 'ip': ip})

@app.route('/api/client/poll/<client_id>')
def api_client_poll(client_id):
    if client_id not in connected_devices:
        return jsonify({'error': 'Not found'})
    dev = connected_devices[client_id]
    result = {}
    if dev.get('pending_command'):
        result['command'] = dev['pending_command']
        dev['pending_command'] = None
    if dev.get('pending_action'):
        result['action'] = dev['pending_action']
        dev['pending_action'] = None
    if dev.get('pending_message'):
        result['message'] = dev['pending_message']
        dev['pending_message'] = None
    return jsonify(result)

@app.route('/api/client/disconnect/<client_id>')
def api_client_disconnect(client_id):
    if client_id in connected_devices:
        name = connected_devices[client_id].get('name', 'Unknown')
        ip = connected_devices[client_id].get('ip', '--')
        del connected_devices[client_id]
        log_entry = {
            'id': str(int(time.time()*1000)),
            'type': 'warn',
            'label': 'DISCONNECT',
            'msg': 'Device disconnected: ' + name + ' (' + ip + ')'
        }
        session_logs.append(log_entry)
    return jsonify({'status': 'disconnected'})

@app.route('/api/log', methods=['POST'])
def api_log():
    data = request.json
    log_entry = {
        'id': str(int(time.time()*1000)),
        'type': data.get('type', 'info'),
        'label': data.get('label', 'LOG'),
        'msg': data.get('msg', '')
    }
    session_logs.append(log_entry)
    return jsonify({'status': 'ok'})

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

if __name__ == '__main__':
    host_ip = get_local_ip()
    print()
    print('+==========================================+')
    print('|         CYBERTERMUX REMOTE PANEL         |')
    print('|         v3.2 - Local Network Mode        |')
    print('+==========================================+')
    print('|  IP:   ' + host_ip.ljust(32) + '|')
    print('|  Port:  5000' + ' ' * 28 + '|')
    print('+------------------------------------------+')
    print('|  CONTROL PANEL:                          |')
    print('|  http://' + host_ip + ':5000' + ' ' * (30 - len(host_ip)) + '|')
    print('|                                          |')
    print('|  CLIENT LINK (dost ko bhejo):            |')
    print('|  http://' + host_ip + ':5000/client' + ' ' * (26 - len(host_ip)) + '|')
    print('+------------------------------------------+')
    print('|  Dono devices same WiFi pe hona zaroori  |')
    print('+==========================================+')
    print()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
