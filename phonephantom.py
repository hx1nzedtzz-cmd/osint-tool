#!/usr/bin/env python3
"""
PhonePhantom v2.0 — Phone Number OSINT Toolkit
Authorized Pentesting Use Only | Termux Ready
"""

import os, sys, json, time, re, requests
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from phonenumbers import PhoneNumberType
from datetime import datetime

# Colors
C = type('C', (), {})()
C.END = '\033[0m'
C.RED = '\033[91m'
C.GREEN = '\033[92m'
C.YELLOW = '\033[93m'
C.BLUE = '\033[94m'
C.MAGENTA = '\033[95m'
C.CYAN = '\033[96m'
C.BOLD = '\033[1m'
C.DIM = '\033[2m'

def c(text, color='', bold=False):
    prefix = color + (C.BOLD if bold else '')
    print(f"{prefix}{text}{C.END}")

def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    b = f"""{C.CYAN}{C.BOLD}
╔══════════════════════════════════════════════╗
║  {C.MAGENTA}██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗{C.CYAN}  ║
║  {C.MAGENTA}██╔══██╗██║  ██║██╔═══██╗████╗  ██║{C.CYAN}  ║
║  {C.MAGENTA}██████╔╝███████║██║   ██║██╔██╗ ██║{C.CYAN}  ║
║  {C.MAGENTA}██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║{C.CYAN}  ║
║  {C.MAGENTA}██║     ██║  ██║╚██████╔╝██║ ╚████║{C.CYAN}  ║
║  {C.MAGENTA}╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝{C.CYAN}  ║
╚══════════════════════════════════════════════╝{C.END}
{C.GREEN}       Phone OSINT Toolkit  v2.0{C.END}
{C.DIM}          Termux Ready | Python 3{C.END}
"""
    print(b)
    time.sleep(0.5)
    print(f"  {C.DIM}[ Initializing... ]{C.END}", end='', flush=True)
    for i in range(3):
        time.sleep(0.2)
        print(f"{C.GREEN}.{C.END}", end='', flush=True)
    print(f" {C.GREEN}READY{C.END}\n")

def loading(text, duration=1.0):
    spinner = '|/-\\'
    end = time.time() + duration
    i = 0
    while time.time() < end:
        print(f"\r  {C.CYAN}{spinner[i%4]}{C.END} {text}...  ", end='', flush=True)
        i += 1
        time.sleep(0.1)
    print(f"\r  {C.GREEN}✓{C.END} {text}... {C.GREEN}Done{C.END}{' '*10}")

def clean_num(n):
    n = re.sub(r'[\s\-\(\)\.]', '', n)
    if not n.startswith('+'):
        n = '+' + n
    return n

# ─── MODULE 1 ──────────────────────────────────────
def validate(n_raw):
    r = {'valid': False, 'possible': False, 'e164': None, 'national': None,
         'international': None, 'type': None, 'country_code': None}
    loading("Validating number", 0.6)
    e164 = clean_num(n_raw)
    if not e164: return r
    try:
        n = phonenumbers.parse(e164, None)
        r['valid'] = phonenumbers.is_valid_number(n)
        r['possible'] = phonenumbers.is_possible_number(n)
        if r['valid'] or r['possible']:
            r['e164'] = phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164)
            r['national'] = phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.NATIONAL)
            r['international'] = phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            r['country_code'] = n.country_code
            nt = phonenumbers.number_type(n)
            types = {PhoneNumberType.MOBILE:'Mobile', PhoneNumberType.FIXED_LINE:'Fixed Line',
                     PhoneNumberType.TOLL_FREE:'Toll Free', PhoneNumberType.VOIP:'VoIP',
                     PhoneNumberType.PREMIUM_RATE:'Premium Rate', PhoneNumberType.SHARED_COST:'Shared Cost',
                     PhoneNumberType.PERSONAL_NUMBER:'Personal', PhoneNumberType.PAGER:'Pager',
                     PhoneNumberType.UAN:'UAN'}
            r['type'] = types.get(nt, 'Unknown')
    except: pass
    return r

# ─── MODULE 2 ──────────────────────────────────────
def carrier_region(n_raw):
    r = {'carrier': None, 'region': None, 'country': None, 'timezones': []}
    loading("Finding carrier & region", 0.7)
    e164 = clean_num(n_raw)
    if not e164: return r
    try:
        n = phonenumbers.parse(e164, None)
        try: r['carrier'] = carrier.name_for_number(n, 'en')
        except: pass
        try: r['region'] = geocoder.description_for_number(n, 'en')
        except: pass
        try: r['country'] = geocoder.country_name_for_number(n, 'en')
        except: pass
        try: r['timezones'] = list(timezone.time_zones_for_number(n))
        except: pass
    except: pass
    return r

# ─── MODULE 3 ──────────────────────────────────────
def social(n_raw, e164=None):
    r = {'whatsapp': False, 'web_mentions': []}
    loading("Social footprint scan", 1.2)
    if not e164: e164 = clean_num(n_raw)
    if not e164: return r
    # WhatsApp check
    try:
        resp = requests.get(f"https://wa.me/{e164.lstrip('+')}", timeout=6,
            allow_redirects=True,
            headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'})
        r['whatsapp'] = 'web.whatsapp.com' in resp.url
    except: pass
    # Web search
    try:
        import urllib.parse
        q = urllib.parse.quote(f'"{n_raw}"')
        resp = requests.get(f'https://html.duckduckgo.com/html/?q={q}', timeout=6,
            headers={'User-Agent': 'Mozilla/5.0'})
        import html
        snippets = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
        for url, title in snippets[:6]:
            t = re.sub(r'<[^>]+>', '', title).strip()
            t = html.unescape(t)
            if t and len(t) > 5:
                r['web_mentions'].append({'title': t[:100], 'url': url})
    except: pass
    return r

# ─── MODULE 4 ──────────────────────────────────────
def spam_check(n_raw):
    r = {'skipcalls': {}, 'tellows': {}, 'overall_risk': 'Unknown'}
    loading("Querying spam databases", 1.3)
    e164 = clean_num(n_raw)
    nat = re.sub(r'[^\d]', '', n_raw)
    
    # SkipCalls
    try:
        resp = requests.get(f"https://spam.skipcalls.app/check/{nat}", timeout=6,
            headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            d = resp.json()
            r['skipcalls'] = {'is_spam': d.get('isSpam', d.get('spam', False)),
                              'score': d.get('spamScore', d.get('score', None))}
    except: pass
    
    # tellows
    try:
        num_clean = re.sub(r'[^\d]', '', e164) if e164 else nat
        resp = requests.get(f"https://www.tellows.de/basic/num/{num_clean}?json=1", timeout=6,
            headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            d = resp.json()
            if 'tellows' in d:
                t = d['tellows']
                r['tellows'] = {'score': int(t.get('score', 0)) if t.get('score') else None,
                                'location': t.get('location'),
                                'country': t.get('country'),
                                'comments': int(t.get('comments', 0)) if t.get('comments') else None,
                                'searches': int(t.get('searches', 0)) if t.get('searches') else None}
    except: pass
    
    # Risk calc
    scores = []
    if r['skipcalls'].get('is_spam'): scores.append(8)
    elif r['skipcalls'].get('is_spam') == False: scores.append(1)
    if r['tellows'].get('score') is not None:
        s = r['tellows']['score']
        if s >= 7: scores.append(9)
        elif s >= 5: scores.append(6)
        elif s >= 3: scores.append(4)
        else: scores.append(1)
    if scores:
        avg = sum(scores)/len(scores)
        if avg >= 7: r['overall_risk'] = 'HIGH - Scam/Spam'
        elif avg >= 4: r['overall_risk'] = 'MEDIUM - Suspicious'
        else: r['overall_risk'] = 'LOW - Seems Safe'
    return r

# ─── MODULE 5 ──────────────────────────────────────
def report(all_data, out_dir='reports'):
    loading("Generating report", 0.6)
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    tag = str(all_data.get('input', 'unknown'))[:15].replace('+','')
    
    # JSON
    jpath = os.path.join(out_dir, f'phonephantom_{tag}_{ts}.json')
    report_data = {
        'tool': 'PhonePhantom v2.0',
        'date': datetime.now().isoformat(),
        'target': all_data.get('input'),
        'results': {k:v for k,v in all_data.items() if k != 'input'}
    }
    with open(jpath, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    # TXT
    tpath = os.path.join(out_dir, f'phonephantom_{tag}_{ts}.txt')
    lines = []
    lines.append("="*60)
    lines.append("  PHONEPHANTOM - Phone OSINT Report")
    lines.append("="*60)
    lines.append(f"  Target : {all_data.get('input', 'N/A')}")
    lines.append(f"  Date   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("-"*60)
    
    v = all_data.get('validator', {})
    lines.append("\n[MODULE 1: Validator]")
    lines.append(f"  Valid       : {v.get('valid', False)}")
    lines.append(f"  Possible    : {v.get('possible', False)}")
    lines.append(f"  E.164       : {v.get('e164', 'N/A')}")
    lines.append(f"  Type        : {v.get('type', 'N/A')}")
    lines.append(f"  Country Code: +{v.get('country_code', 'N/A')}")
    
    cr = all_data.get('carrier_region', {})
    lines.append("\n[MODULE 2: Carrier & Region]")
    lines.append(f"  Carrier  : {cr.get('carrier', 'N/A')}")
    lines.append(f"  Region   : {cr.get('region', 'N/A')}")
    lines.append(f"  Country  : {cr.get('country', 'N/A')}")
    lines.append(f"  Timezones: {', '.join(cr.get('timezones', [])) or 'N/A'}")
    
    sf = all_data.get('social_footprint', {})
    lines.append("\n[MODULE 3: Social Footprint]")
    lines.append(f"  WhatsApp    : {'YES' if sf.get('whatsapp') else 'Not found'}")
    lines.append(f"  Web Mentions: {len(sf.get('web_mentions', []))}")
    for m in sf.get('web_mentions', [])[:5]:
        lines.append(f"    -> {m.get('title','')}")
        lines.append(f"       {m.get('url','')}")
    
    sr = all_data.get('spam_reputation', {})
    lines.append("\n[MODULE 4: Spam/Scam Reputation]")
    lines.append(f"  Overall Risk: {sr.get('overall_risk', 'N/A')}")
    if sr.get('skipcalls'):
        lines.append(f"  SkipCalls: {json.dumps(sr['skipcalls'])}")
    if sr.get('tellows'):
        lines.append(f"  Tellows  : {json.dumps(sr['tellows'])}")
    
    lines.append("\n" + "="*60)
    lines.append("  Generated by PhonePhantom v2.0")
    lines.append("  Authorized pentesting only.")
    
    with open(tpath, 'w') as f:
        f.write('\n'.join(lines))
    
    return {'txt': tpath, 'json': jpath}

# ─── DISPLAY ────────────────────────────────────────
def show(module, data, title):
    print(f"\n  {'─'*56}")
    print(f"  {C.BOLD}{C.CYAN}[ {title} ]{C.END}")
    print(f"  {'─'*56}")
    def pr(d, indent=1):
        for k,v in d.items():
            p = "  "*indent
            if isinstance(v, dict):
                print(f"  {p}{C.YELLOW}{k}:{C.END}")
                pr(v, indent+1)
            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    print(f"  {p}{C.YELLOW}{k}:{C.END}")
                    for item in v[:3]:
                        for kk,vv in item.items():
                            print(f"  {p}  {C.DIM}{kk}:{C.END} {str(vv)[:80]}")
                else:
                    print(f"  {p}{C.YELLOW}{k}:{C.END} {', '.join(str(x) for x in v[:3])}")
            elif v is None:
                print(f"  {p}{C.YELLOW}{k}:{C.END} {C.DIM}N/A{C.END}")
            elif isinstance(v, bool):
                s = f"{C.GREEN}{v}{C.END}" if v else f"{C.RED}{v}{C.END}"
                print(f"  {p}{C.YELLOW}{k}:{C.END} {s}")
            else:
                print(f"  {p}{C.YELLOW}{k}:{C.END} {v}")
    pr(data)

# ─── FULL SCAN ──────────────────────────────────────
def full_scan(number, out_dir='reports'):
    print(f"\n  {C.BOLD}{C.CYAN}═══ Scanning: {number} ═══{C.END}\n")
    data = {'input': number}
    
    v = validate(number)
    data['validator'] = v
    show('validator', v, 'Number Validator')
    
    cr = carrier_region(number)
    data['carrier_region'] = cr
    show('carrier_region', cr, 'Carrier & Region Finder')
    
    sf = social(number, v.get('e164'))
    data['social_footprint'] = sf
    show('social_footprint', sf, 'Social Footprint')
    
    sr = spam_check(number)
    data['spam_reputation'] = sr
    show('spam_reputation', sr, 'Spam/Scam Reputation')
    
    r = report(data, out_dir)
    data['report'] = r
    
    print(f"\n  {C.BOLD}{C.GREEN}══════════ SCAN COMPLETE ══════════{C.END}")
    print(f"  {C.CYAN}TXT Report :{C.END} {r['txt']}")
    print(f"  {C.CYAN}JSON Report:{C.END} {r['json']}")
    print(f"  {C.BOLD}{C.GREEN}═══════════════════════════════════{C.END}\n")
    return data

# ─── BATCH ──────────────────────────────────────────
def batch_scan(fpath, out_dir='reports'):
    if not os.path.exists(fpath):
        print(f"  {C.RED}File not found: {fpath}{C.END}")
        return
    with open(fpath) as f:
        nums = [l.strip() for l in f if l.strip()]
    print(f"\n  {C.CYAN}Batch scanning {len(nums)} numbers...{C.END}\n")
    all_data = []
    for i, n in enumerate(nums, 1):
        print(f"  {C.DIM}[{i}/{len(nums)}]{C.END} {C.BOLD}{n}{C.END}")
        all_data.append(full_scan(n, out_dir))
        print()
    # Batch JSON
    batch = {
        'tool': 'PhonePhantom v2.0',
        'type': 'batch_scan',
        'date': datetime.now().isoformat(),
        'source': fpath,
        'count': len(all_data),
        'scans': all_data
    }
    bpath = os.path.join(out_dir, f'batch_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(bpath, 'w') as f:
        json.dump(batch, f, indent=2, default=str)
    print(f"  {C.GREEN}Batch report saved: {bpath}{C.END}\n")

# ─── MENU ───────────────────────────────────────────
def menu():
    print(f"\n  {C.BOLD}{C.CYAN}╔══════════════════════════════╗{C.END}")
    print(f"  {C.BOLD}{C.CYAN}║   PHONEPHANTOM v2.0         ║{C.END}")
    print(f"  {C.BOLD}{C.CYAN}╠══════════════════════════════╣{C.END}")
    print(f"  {C.BOLD}{C.CYAN}║{C.END} {C.YELLOW}[1]{C.END} Full Scan (All 5 modules)  {C.CYAN}║{C.END}")
    print(f"  {C.BOLD}{C.CYAN}║{C.END} {C.YELLOW}[2]{C.END} Validate Number Only       {C.CYAN}║{C.END}")
    print(f"  {C.BOLD}{C.CYAN}║{C.END} {C.YELLOW}[3]{C.END} Carrier & Region           {C.CYAN}║{C.END}")
    print(f"  {C.BOLD}{C.CYAN}║{C.END} {C.YELLOW}[4]{C.END} Social Footprint           {C.CYAN}║{C.END}")
    print(f"  {C.BOLD}{C.CYAN}║{C.END} {C.YELLOW}[5]{C.END} Spam/Scam Reputation       {C.CYAN}║{C.END}")
    print(f"  {C.BOLD}{C.CYAN}║{C.END} {C.YELLOW}[6]{C.END} Batch Scan (File)          {C.CYAN}║{C.END}")
    print(f"  {C.BOLD}{C.CYAN}║{C.END} {C.YELLOW}[0]{C.END} Exit                       {C.CYAN}║{C.END}")
    print(f"  {C.BOLD}{C.CYAN}╚══════════════════════════════╝{C.END}")

# ─── MAIN ───────────────────────────────────────────
def main():
    # Check deps
    try:
        import phonenumbers
        import requests
    except ImportError as e:
        print(f"\n  {C.RED}Missing: {e}{C.END}")
        print(f"  {C.YELLOW}Run: pip install phonenumbers requests{C.END}")
        sys.exit(1)
    
    banner()
    out_dir = 'reports'
    os.makedirs(out_dir, exist_ok=True)
    
    while True:
        menu()
        try:
            ch = input(f"\n  {C.CYAN}>{C.END} Option: ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {C.YELLOW}Bye.{C.END}")
            break
        
        if ch == '0':
            print(f"\n  {C.GREEN}Exiting. Stay sharp.{C.END}\n")
            break
        elif ch == '1':
            n = input(f"  {C.CYAN}>{C.END} Phone number: ").strip()
            if n: full_scan(n, out_dir)
        elif ch == '2':
            n = input(f"  {C.CYAN}>{C.END} Phone number: ").strip()
            if n: show('validator', validate(n), 'Number Validator')
        elif ch == '3':
            n = input(f"  {C.CYAN}>{C.END} Phone number: ").strip()
            if n: show('carrier_region', carrier_region(n), 'Carrier & Region')
        elif ch == '4':
            n = input(f"  {C.CYAN}>{C.END} Phone number: ").strip()
            if n: show('social', social(n), 'Social Footprint')
        elif ch == '5':
            n = input(f"  {C.CYAN}>{C.END} Phone number: ").strip()
            if n: show('spam', spam_check(n), 'Spam/Scam Reputation')
        elif ch == '6':
            f = input(f"  {C.CYAN}>{C.END} Path to number list file: ").strip()
            if f: batch_scan(f, out_dir)
        else:
            print(f"  {C.RED}Invalid option.{C.END}")
        
        if ch in '123456':
            input(f"\n  {C.DIM}Press Enter to continue...{C.END}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n  {C.YELLOW}Interrupted.{C.END}\n")
    except Exception as e:
        print(f"\n  {C.RED}Error: {e}{C.END}")
