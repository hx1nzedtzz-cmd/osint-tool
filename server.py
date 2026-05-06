#!/usr/bin/env python3
"""
mailxtract.py — Email OSINT Module for MailXtract v4.2
Provides: scan_email(), save_txt(), save_html(), save_json()
"""

import re
import socket
import json
import whois
import dns.resolver
import requests
from datetime import datetime
from pathlib import Path


# ─── Disposable email domains (curated list) ───────────────────────────────
DISPOSABLE_DOMAINS = {
    'mailinator.com', 'guerrillamail.com', 'sharklasers.com', 'grr.la',
    'temp-mail.org', 'tempmail.com', '10minutemail.com', 'throwaway.email',
    'disposemail.com', 'yopmail.com', 'mailnator.com', 'getnada.com',
    'inboxbear.com', 'tempemails.com', 'spam4.me', 'maildrop.cc',
    'tempinbox.com', 'trashmail.com', 'trashmail.net', 'trash2009.com',
    'mailmetrash.com', 'thankyou2010.com', 'trashymail.com', 'tyldd.com',
    'emailtmp.com', 'blackmarket.to', 'jetable.org', 'spamgourmet.com',
    'mytrashmail.com', 'mintemail.com', 'sneakmail.de', 'temporarymail.net',
    'fakeinbox.com', 'mailexpire.com', 'throwaway.de', 'wegwerfmail.de',
    'burnermail.io', 'discard.email', 'maillinator.com', 'mail-temp.com',
    'mailtemp.org', 'guerrillamail.org', 'guerrillamail.net', 'guerrillamail.biz',
    'mailforspam.com', 'mailsac.com', 'harakirimail.com', 'inboxalias.com',
    'anonbox.net', 'spambox.us', 'spambox.info', 'spambox.me',
    'mailmetrash.com', 'maileater.com', 'mailexpire.com', 'mailetc.com',
    'mailnator.com', 'mailnull.com', 'moakt.com', 'mohmal.com',
    'mvrht.com', 'mvrht.net', 'nepwk.com', 'nguyenused.com',
    'nthrl.com', 'oneoffemail.com', 'oopi.org', 'outlookat.com',
    'pfui.ru', 'pojok.ml', 'policeoffice.ml', 'proxymail.eu',
    'prtnx.com', 'quickinbox.com', 'rcpt.at', 'receiveee.com',
    'recode.me', 'recursor.net', 'relay-boss.ml', 'resgedupaded.gq',
    'rmqkr.net', 'rtrtr.com', 's0ny.net', 's1x.de',
    'sandbox.google.com', 'scatmail.com', 'schafmail.de', 'schrott-email.de',
    'sd3.in', 'secmail.net', 'secmail.pw', 'secretemail.de',
    'secure-mail.biz', 'selfdestructingmail.com', 'sendfree.org', 'sendhere.biz',
    'senseless-entertainment.com', 'server.ms', 'services391.com', 'services391.net',
    'shapoo.ch', 'sharklasers.com', 'shieldedmail.com', 'shmeriously.com',
    'shortmail.net', 'sibmail.com', 'sinnlos-mail.de', 'siteposter.net',
    'skepticalforum.com', 'slaskpost.se', 'slopsbox.com', 'slushmail.com',
    'sneakemail.com', 'sneakmail.de', 'snkmail.com', 'sofimail.com',
    'sofort-mail.de', 'softpls.asia', 'softpls.com', 'sogetthis.com',
    'spam.la', 'spam.su', 'spam4.me', 'spamavert.com',
    'spambob.com', 'spambob.net', 'spambob.org', 'spambog.com',
    'spambog.de', 'spambog.ru', 'spambooger.com', 'spamcowboy.com',
    'spamcowboy.net', 'spamcowboy.org', 'spamday.com', 'spamdecoy.net',
    'spameater.com', 'spameater.org', 'spamex.com', 'spamfighter.de',
    'spamfree24.com', 'spamfree24.de', 'spamfree24.eu', 'spamfree24.info',
    'spamfree24.net', 'spamfree24.org', 'spamgourmet.com', 'spamgourmet.net',
    'spamgourmet.org', 'spamherelot.com', 'spamhole.com', 'spamify.com',
    'spaminator.de', 'spamkill.info', 'spaml.com', 'spamlot.net',
    'spammotel.com', 'spamobox.com', 'spamoff.de', 'spamsalad.com',
    'spamserver.de', 'spamslicer.com', 'spamspameverywhere.com', 'spamspot.com',
    'spamstack.net', 'spamthis.co.uk', 'spamthisplease.com', 'spamtrail.com',
    'spamtrap.co.il', 'spamtrap.ro', 'spamtrap24.com', 'spamwc.de',
    'speed.1s.fr', 'spoofmail.de', 'stopdropandroll.com', 'stuffmail.de',
    'sudolife.me', 'sudomail.biz', 'sudomail.com', 'sudomail.net',
    'sudoverse.com', 'suremail.info', 'talkinator.com', 'teditemail.com',
    'teleworm.com', 'teleworm.us', 'temp-eml.com', 'temp-mail.com',
    'temp-mail.de', 'temp-mail.org', 'temp-mail.ru', 'tempail.com',
    'tempemail.biz', 'tempemail.co.za', 'tempemail.com', 'tempemail.net',
    'tempemail.org', 'tempinbox.co.uk', 'tempinbox.com', 'tempmail.be',
    'tempmail.co', 'tempmail.com', 'tempmail.de', 'tempmail.eu',
    'tempmail.info', 'tempmail.io', 'tempmail.net', 'tempmail.org',
    'tempmail.us', 'tempomail.com', 'temporaryemail.net', 'temporaryemail.us',
    'temporaryforwarding.com', 'temporaryinbox.com', 'thankyou2010.com',
    'thc.st', 'thrownmail.com', 'tittbit.in', 'tizi.com',
    'tmail.ws', 'tmailinator.com', 'toiea.com', 'trash2009.com',
    'trash-amil.com', 'trash-me.com', 'trash2009.com', 'trashdevil.com',
    'trashemail.de', 'trashmail.at', 'trashmail.com', 'trashmail.de',
    'trashmail.me', 'trashmail.net', 'trashmail.org', 'trashmail.ws',
    'trashmails.com', 'trashymail.com', 'trimex.org', 'trustami.com',
    'tryninja.io', 'tutuapp.bid', 'twinmail.de', 'tyldd.com',
    'uglytechnologies.com', 'uk.to', 'umail.net', 'upliftnow.com',
    'uplipht.com', 'uref.me', 'urfey.com', 'valemail.net',
    'venompen.com', 'veryrealemail.com', 'viditrc.com', 'view2mail.com',
    'vipmail.name', 'vipmail.pw', 'vipxm.net', 'vistomail.com',
    'vmail.me', 'vomoto.com', 'vpn.st', 'vsimcard.com', 'vubby.com',
    'walala.org', 'walkmail.net', 'walkmail.ru', 'wasd.dropmail.me',
    'web-emailbox.eu', 'web-mail.pp.ua', 'web2mailco.com', 'webcontact-france.eu',
    'webemail.me', 'webm4il.info', 'webmail24.top', 'webtrip.ch',
    'wee.my', 'weg-werf-mail.de', 'wegwerf-emails.de', 'wegwerfmail.de',
    'wegwerfmail.net', 'wegwerfmail.org', 'wh4f.org', 'whatiaas.com',
    'whatpaas.com', 'whatsaas.com', 'whopy.com', 'whtjddn.33mail.com',
    'willselfdestruct.com', 'winemaven.info', 'wronghead.com', 'wuzup.net',
    'wuzupmail.net', 'www.bccto.me', 'www.e4ward.com', 'www.gishpuppy.com',
    'www.mailinator.com', 'wwwnew.eu', 'xagloo.com', 'xemaps.com',
    'xents.com', 'xmaily.com', 'xoxy.net', 'xwaretech.com',
    'xwaretech.info', 'xwaretech.net', 'xww.ro', 'yep.it',
    'yogamaven.com', 'yopmail.com', 'yopmail.fr', 'yopmail.net',
    'ypmail.webarnak.fr.eu.org', 'yuurok.com', 'zehnminutenmail.de',
    'zippymail.info', 'zoaxe.com', 'zoemail.com', 'zoemail.net',
    'zoemail.org', 'zomg.info', 'zxcv.com', 'zxcvbnm.com',
}


def is_disposable(domain):
    """Check if a domain is a known disposable email provider."""
    return domain.lower() in DISPOSABLE_DOMAINS


def get_domain_age(creation_date):
    """Calculate domain age in years from WHOIS creation date."""
    if not creation_date:
        return None
    if isinstance(creation_date, list):
        creation_date = creation_date[0]
    if isinstance(creation_date, str):
        try:
            creation_date = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
        except Exception:
            return None
    age = (datetime.now() - creation_date).days / 365.25
    return round(age, 1)


def dns_lookup(domain, record_type):
    """Generic DNS lookup wrapper."""
    try:
        answers = dns.resolver.resolve(domain, record_type)
        return [str(r) for r in answers]
    except Exception:
        return []


def check_blacklist(ip):
    """Check if IP is listed on common DNSBLs (simplified)."""
    if not ip:
        return False
    # Basic DNSBL check
    try:
        reversed_ip = '.'.join(reversed(ip.split('.')))
        queries = [
            f"{reversed_ip}.zen.spamhaus.org",
        ]
        for q in queries:
            try:
                socket.gethostbyname(q)
                return True
            except socket.gaierror:
                continue
    except Exception:
        pass
    return False


def scan_email(email):
    """
    Main scanning function.
    Returns a dict with keys matching what the web UI expects.
    """
    email = email.strip().lower()
    
    # Basic validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return {'status': 'error', 'error': 'Invalid email format'}
    
    parts = email.split('@')
    username = parts[0]
    domain = parts[1]
    
    result = {
        'status': 'ok',
        'email': email,
        'username': username,
        'domain': domain,
        'disposable': '⚠️ Yes' if is_disposable(domain) else '✅ No',
    }
    
    # ── WHOIS Lookup ──────────────────────────────────────────────────────
    try:
        w = whois.whois(domain)
        result['registrar'] = w.registrar or 'N/A'
        
        created = w.creation_date
        if created:
            if isinstance(created, list):
                created = created[0]
            result['created'] = str(created)
            age = get_domain_age(created)
            if age is not None:
                result['age'] = f"{age} years"
        
        expiry = w.expiration_date
        if expiry:
            if isinstance(expiry, list):
                expiry = expiry[0]
            result['expiry'] = str(expiry)
    except Exception:
        result['registrar'] = 'Lookup failed'
        result['created'] = 'N/A'
        result['age'] = 'N/A'
        result['expiry'] = 'N/A'
    
    # ── DNS Records ───────────────────────────────────────────────────────
    # SPF
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        spf_records = [str(r) for r in txt_records if 'v=spf1' in str(r)]
        result['spf'] = spf_records[0][:200] if spf_records else 'Not configured'
    except Exception:
        result['spf'] = 'Lookup failed'
    
    # DMARC
    try:
        dmarc_records = dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
        dmarc = [str(r) for r in dmarc_records if 'v=DMARC1' in str(r)]
        result['dmarc'] = dmarc[0][:200] if dmarc else 'Not configured'
    except Exception:
        result['dmarc'] = 'Lookup failed'
    
    # MX Records
    mx_records = dns_lookup(domain, 'MX')
    result['mx'] = ', '.join(mx_records[:5]) if mx_records else 'No MX records found'
    
    # DNSSEC check (via DNSKEY)
    try:
        dns.resolver.resolve(domain, 'DNSKEY')
        result['dnssec'] = '✅ Enabled'
    except Exception:
        result['dnssec'] = '❌ Not enabled or unavailable'
    
    # ── IP & Geolocation ──────────────────────────────────────────────────
    try:
        ip = socket.gethostbyname(domain)
        result['ip'] = ip
        
        # Geolocation via ip-api.com (free, no key needed)
        try:
            geo_resp = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
            if geo_resp.status_code == 200:
                geo = geo_resp.json()
                if geo.get('status') == 'success':
                    parts = []
                    if geo.get('city'): parts.append(geo['city'])
                    if geo.get('regionName'): parts.append(geo['regionName'])
                    if geo.get('country'): parts.append(geo['country'])
                    result['location'] = ', '.join(parts) if parts else 'N/A'
                    result['isp'] = geo.get('isp', 'N/A')
                else:
                    result['location'] = 'N/A'
                    result['isp'] = 'N/A'
            else:
                result['location'] = 'N/A'
                result['isp'] = 'N/A'
        except Exception:
            result['location'] = 'Lookup failed'
            result['isp'] = 'Lookup failed'
        
        # Blacklist check
        result['blacklisted'] = '🚫 Listed' if check_blacklist(ip) else '✅ Clean'
        
    except socket.gaierror:
        result['ip'] = 'DNS resolution failed'
        result['location'] = 'N/A'
        result['isp'] = 'N/A'
        result['blacklisted'] = 'N/A'
    
    # ── Gravatar ──────────────────────────────────────────────────────────
    import hashlib
    gravatar_hash = hashlib.md5(email.encode('utf-8').lower().strip()).hexdigest()
    gravatar_url = f"https://www.gravatar.com/avatar/{gravatar_hash}?d=404&s=1"
    try:
        resp = requests.head(gravatar_url, timeout=5, allow_redirects=True)
        result['gravatar'] = '✅ Registered' if resp.status_code == 200 else '❌ Not found'
    except Exception:
        result['gravatar'] = 'Check failed'
    
    return result


# ─── Save Functions ────────────────────────────────────────────────────────

def save_txt(data, filepath):
    """Save results as plain text."""
    labels = {
        'email': 'Email', 'username': 'Username', 'domain': 'Domain',
        'disposable': 'Disposable', 'registrar': 'Registrar',
        'created': 'Created', 'age': 'Age', 'expiry': 'Expiry',
        'ip': 'IP Address', 'location': 'Location', 'isp': 'ISP',
        'dnssec': 'DNSSEC', 'blacklisted': 'Blacklisted',
        'spf': 'SPF Record', 'dmarc': 'DMARC Record', 'mx': 'MX Records',
        'gravatar': 'Gravatar',
    }
    
    lines = []
    lines.append("╔══════════════════════════════════════╗")
    lines.append("║     MailXtract v4.2 — Scan Report    ║")
    lines.append("╚══════════════════════════════════════╝")
    lines.append("")
    
    for key, label in labels.items():
        if key in data and not key.startswith('_') and key != 'status':
            lines.append(f"{label:20s} : {data[key]}")
    
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def save_html(data, filepath):
    """Save results as an HTML report."""
    labels = {
        'email': 'Email', 'username': 'Username', 'domain': 'Domain',
        'disposable': 'Disposable', 'registrar': 'Registrar',
        'created': 'Created', 'age': 'Age', 'expiry': 'Expiry',
        'ip': 'IP Address', 'location': 'Location', 'isp': 'ISP',
        'dnssec': 'DNSSEC', 'blacklisted': 'Blacklisted',
        'spf': 'SPF Record', 'dmarc': 'DMARC Record', 'mx': 'MX Records',
        'gravatar': 'Gravatar',
    }
    
    rows = []
    for key, label in labels.items():
        if key in data and not key.startswith('_') and key != 'status':
            val = data[key]
            rows.append(f"""        <tr>
            <th>{label}</th>
            <td>{val}</td>
        </tr>""")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MailXtract v4.2 - Scan Report</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; padding: 40px; }}
        .container {{ max-width: 700px; margin: 0 auto; background: #161b22; border: 1px solid #30363d; border-radius: 16px; padding: 30px; }}
        h1 {{ color: #58a6ff; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #30363d; padding: 10px 14px; text-align: left; }}
        th {{ background: #21262d; color: #58a6ff; width: 160px; }}
        td {{ color: #c9d1d9; word-break: break-all; }}
        .footer {{ text-align: center; color: #484f58; font-size: 12px; margin-top: 25px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 MailXtract v4.2</h1>
        <table>
{chr(10).join(rows)}
        </table>
        <div class="footer">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>
</body>
</html>"""
    
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)


def save_json(data, filepath):
    """Save results as JSON."""
    clean = {k: v for k, v in data.items() if not k.startswith('_')}
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(clean, f, indent=2, default=str)
