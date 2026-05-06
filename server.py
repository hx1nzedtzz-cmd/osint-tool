#!/usr/bin/env python3
# 🔍 MailXtract v4.2 Web Server - localhost:8080

from flask import Flask, render_template_string, request, jsonify, send_file
from mailxtract import scan_email, save_txt, save_html, save_json
from pathlib import Path
import os

app = Flask(__name__)

Path('outputs').mkdir(exist_ok=True)

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MailXtract v4.2 — Email OSINT Tool</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #c9d1d9;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 16px;
            padding: 40px;
            width: 90%;
            max-width: 700px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        }
        h1 {
            color: #58a6ff;
            font-size: 28px;
            margin-bottom: 5px;
            text-align: center;
        }
        .subtitle {
            color: #8b949e;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="email"] {
            flex: 1;
            padding: 14px 18px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #c9d1d9;
            font-size: 16px;
            outline: none;
            transition: border 0.3s;
        }
        input[type="email"]:focus { border-color: #58a6ff; }
        button {
            padding: 14px 28px;
            background: #238636;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover { background: #2ea043; }
        button:disabled { background: #21262d; cursor: not-allowed; }
        .loader { display: none; text-align: center; padding: 20px; }
        .spinner {
            border: 4px solid #30363d;
            border-top: 4px solid #58a6ff;
            border-radius: 50%;
            width: 40px; height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        #results { display: none; margin-top: 25px; }
        .result-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .result-table th, .result-table td {
            border: 1px solid #30363d;
            padding: 10px 14px;
            text-align: left;
        }
        .result-table th { background: #21262d; color: #58a6ff; width: 160px; }
        .result-table td { color: #c9d1d9; word-break: break-all; }
        .download-links {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            justify-content: center;
        }
        .download-btn {
            padding: 10px 20px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #58a6ff;
            text-decoration: none;
            font-size: 14px;
            transition: background 0.3s;
        }
        .download-btn:hover { background: #30363d; }
        .error-msg { color: #f85149; text-align: center; padding: 20px; font-size: 18px; }
        .good { color: #3fb950; }
        .bad { color: #f85149; }
        .footer { text-align: center; margin-top: 25px; color: #484f58; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 MailXtract v4.2</h1>
        <p class="subtitle">Email OSINT — Domain Recon · WHOIS · DNS · Geolocation</p>
        
        <div class="input-group">
            <input type="email" id="emailInput" placeholder="Enter email address (e.g., user@domain.com)" />
            <button id="scanBtn" onclick="scanEmail()">🔎 Scan</button>
        </div>
        
        <div class="loader" id="loader">
            <div class="spinner"></div>
            <p>🔍 Scanning email...</p>
            <p style="color: #8b949e; font-size: 13px;">Checking WHOIS, DNS, Geolocation & more</p>
        </div>
        
        <div id="error" class="error-msg" style="display:none;"></div>
        
        <div id="results">
            <h2 style="color: #3fb950; text-align: center;">✅ Scan Complete</h2>
            <table class="result-table" id="resultTable"></table>
            
            <div class="download-links">
                <a class="download-btn" id="downloadTxt" href="#">📄 Download TXT</a>
                <a class="download-btn" id="downloadHtml" href="#">📄 Download HTML</a>
                <a class="download-btn" id="downloadJson" href="#">📄 Download JSON</a>
            </div>
        </div>
        
        <div class="footer">
            🔓 FREE — No License Required
        </div>
    </div>

    <script>
        async function scanEmail() {
            const email = document.getElementById('emailInput').value.trim();
            if (!email || !email.includes('@')) {
                alert('Please enter a valid email address');
                return;
            }
            
            document.getElementById('loader').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            document.getElementById('scanBtn').disabled = true;
            
            try {
                const res = await fetch('/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email })
                });
                const data = await res.json();
                
                if (data.status === 'error') {
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('error').textContent = '❌ ' + data.error;
                    document.getElementById('loader').style.display = 'none';
                    document.getElementById('scanBtn').disabled = false;
                    return;
                }
                
                renderResults(data);
                
                document.getElementById('downloadTxt').href = '/download/txt/' + encodeURIComponent(email);
                document.getElementById('downloadHtml').href = '/download/html/' + encodeURIComponent(email);
                document.getElementById('downloadJson').href = '/download/json/' + encodeURIComponent(email);
                
                document.getElementById('results').style.display = 'block';
                document.getElementById('loader').style.display = 'none';
            } catch (err) {
                document.getElementById('error').style.display = 'block';
                document.getElementById('error').textContent = '❌ Connection error. Is the server running?';
                document.getElementById('loader').style.display = 'none';
            }
            
            document.getElementById('scanBtn').disabled = false;
        }
        
        function renderResults(data) {
            const table = document.getElementById('resultTable');
            table.innerHTML = '';
            
            const labels = {
                'email': '📧 Email', 'username': '👤 Username', 'domain': '🌐 Domain',
                'disposable': '♻️ Disposable', 'registrar': '🏢 Registrar',
                'created': '📅 Created', 'age': '⏰ Age (years)', 'expiry': '⏳ Expiry',
                'ip': '🌍 IP Address', 'location': '📍 Location', 'isp': '🏭 ISP',
                'dnssec': '🔐 DNSSEC', 'blacklisted': '🚫 Blacklisted',
                'spf': '📝 SPF', 'dmarc': '📝 DMARC', 'mx': '📬 MX Records',
                'gravatar': '👤 Gravatar'
            };
            
            for (const [key, label] of Object.entries(labels)) {
                if (data[key] !== undefined) {
                    const tr = document.createElement('tr');
                    const th = document.createElement('th');
                    th.textContent = label;
                    const td = document.createElement('td');
                    td.textContent = data[key];
                    tr.appendChild(th);
                    tr.appendChild(td);
                    table.appendChild(tr);
                }
            }
        }
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    email = data.get('email', '')
    result = scan_email(email)
    
    if result['status'] == 'error':
        return jsonify(result)
    
    safe_name = email.replace('@', '_at_').replace('.', '_')
    txt_file = f"outputs/{safe_name}.txt"
    html_file = f"outputs/{safe_name}.html"
    json_file = f"outputs/{safe_name}.json"
    
    save_txt(result, txt_file)
    save_html(result, html_file)
    save_json(result, json_file)
    
    clean_result = {k: v for k, v in result.items() if not k.startswith('_')}
    
    return jsonify(clean_result)

@app.route('/download/<fmt>/<path:email>')
def download(fmt, email):
    safe_name = email.replace('@', '_at_').replace('.', '_')
    file_map = {
        'txt': f"outputs/{safe_name}.txt",
        'html': f"outputs/{safe_name}.html",
        'json': f"outputs/{safe_name}.json"
    }
    filepath = file_map.get(fmt)
    if filepath and Path(filepath).exists():
        return send_file(filepath, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════╗
║  🔍 MailXtract v4.2 — Web Server          ║
║                                            ║
║  🌐 http://localhost:8080                  ║
╚════════════════════════════════════════════╝
""")
    app.run(host='0.0.0.0', port=8080, debug=True)
