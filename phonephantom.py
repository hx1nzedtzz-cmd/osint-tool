#!/usr/bin/env python3
# ================================================================
#  PHANTOM EYE — Advanced OSINT Investigation Toolkit v2.0
#  Author: HackerAI | Platform: Termux (Android)
#  Purpose: Legal OSINT & Pentest Reconnaissance Only
#  Modules: 9 | Lines: ~800 | License: Educational/Authored Pentest
# ================================================================

import os, sys, json, re, hashlib, socket, platform, subprocess
import urllib.request, urllib.error, urllib.parse
import time, datetime, random, textwrap, base64

# --- Core Dependencies (attempt import, fallback graceful) ---
try:
    import phonenumbers
    from phonenumbers import carrier, geocoder, timezone as pn_tz
    PHONENUM_OK = True
except ImportError:
    PHONENUM_OK = False

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

# ---- GLOBALS ----
VERSION = "2.0.0"
BANNER = """
▄▄▄█████▓ ██░ ██ ▄▄▄       ███▄    █ ▄▄▄█████▓ ▒█████   ██▓
▓  ██▒ ▓▒▓██░ ██▒████▄     ██ ▀█   █ ▓  ██▒ ▓▒▒██▒  ██▒▓██▒
▒ ▓██░ ▒░▒██▀▀██▒██  ▀█▄  ▓██  ▀█ ██▒ ▒██▒ ▒ ▒██░  ██▒▒██▒
░ ▓██▓ ░ ░▓█ ░██░██▄▄▄▄██ ▓██▒  ▐▌██▒ ░ ▓██░   ▒██   ██░░██░
  ▒██▒ ░ ░▓█▒░██▓▓█   ▓██▒▒██░   ▓██░   ▒██     ░ ████▓▒░░██░
  ▒ ░░    ▒ ░░▒░▒ ▒▒   ▓▒█░░ ▒░   ▒ ▒    ░▓      ░ ▒░▒░▒░ ░▓
    ░     ▒ ░▒░ ░  ▒   ▒▒ ░░ ░░   ░ ▒░    ▒ ░    ░ ▒ ▒░ ░ ▒ ░
  ░       ░  ░░ ░  ░   ▒      ░   ░ ░     ▒ ░  ░ ░ ░ ▒    ▒ ░
          ░  ░  ░      ░  ░         ░     ░        ░ ░    ░
"""
COLORS = {
    'R': '\033[91m', 'G': '\033[92m', 'Y': '\033[93m',
    'B': '\033[94m', 'M': '\033[95m', 'C': '\033[96m',
    'W': '\033[97m', 'N': '\033[0m', 'BOLD': '\033[1m',
    'BLINK': '\033[5m', 'BG_R': '\033[41m', 'BG_G': '\033[42m',
    'BG_B': '\033[44m', 'BG_M': '\033[45m'
}
RESULTS_DIR = "PhantomEye_Reports"
os.makedirs(RESULTS_DIR, exist_ok=True)
SESSION_DATA = {"target_name": "", "start_time": "", "findings": []}
UA_LIST = [
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/120.0.0.0",
]

# ---- HELPERS ----
def c(text, *codes):
    """Colorize text with ANSI codes."""
    prefix = ''.join(COLORS.get(c, '') for c in codes)
    return f"{prefix}{text}{COLORS['N']}"

def banner():
    """Animated ASCII banner with matrix-style reveal."""
    os.system('clear')
    lines = BANNER.strip('\n').split('\n')
    for i, line in enumerate(lines):
        colored = c(line, 'G', 'BOLD') if i < 4 else c(line, 'C')
        if i == 0: colored = c(line, 'R', 'BOLD', 'BLINK')
        if i == len(lines)//2: colored = c(line, 'M', 'BOLD')
        print(colored)
        time.sleep(0.04)
    
    title = f"═══ PHANTOM EYE v{VERSION} — OSINT PLATFORM ═══"
    subtitle = "Legal Reconnaissance | Ethical Investigations | Pentest Ready"
    print(f"\n  {c('┌', 'B')}{c('─' * (len(title)+2), 'B')}{c('┐', 'B')}")
    print(f"  {c('│', 'B')} {c(title, 'R', 'BOLD', 'BLINK')} {c('│', 'B')}")
    print(f"  {c('└', 'B')}{c('─' * (len(title)+2), 'B')}{c('┘', 'B')}")
    print(f"\n  {c(subtitle, 'Y')}")
    print(f"  {c('━' * 55, 'B')}\n")

def dashboard():
    """Display the hacker dashboard."""
    elapsed = "00:00:00"
    if SESSION_DATA["start_time"]:
        elapsed = str(datetime.datetime.now() - SESSION_DATA["start_time"]).split('.')[0]
    
    print(f"\n  {c('╔══════════════════════ HACKER DASHBOARD ═══════════════════════╗', 'B')}")
    print(f"  {c('║', 'B')} {c('TARGET:', 'R', 'BOLD'):<10} {c(SESSION_DATA['target_name'] or 'NOT SET', 'W', 'BOLD'):<48} {c('║', 'B')}")
    findings_count = len(SESSION_DATA["findings"])
    print(f"  {c('║', 'B')} {c('STATUS:', 'Y', 'BOLD'):<10} {c('ACTIVE', 'G', 'BOLD'):<48} {c('║', 'B')}")
    print(f"  {c('║', 'B')} {c('SCANS:', 'C', 'BOLD'):<10} {c(str(findings_count) + ' findings', 'Y'):<48} {c('║', 'B')}")
    print(f"  {c('║', 'B')} {c('UPTIME:', 'M', 'BOLD'):<10} {c(elapsed, 'G'):<48} {c('║', 'B')}")
    print(f"  {c('╚══════════════════════════════════════════════════════════════╝', 'B')}\n")

def log_finding(module, data_type, value, detail):
    """Record a finding into session data."""
    entry = {
        "module": module, "type": data_type, "value": value,
        "detail": detail, "timestamp": str(datetime.datetime.now())
    }
    SESSION_DATA["findings"].append(entry)
    return entry

def fetch_url(url, timeout=12, headers=None):
    """Fetch URL content with error handling."""
    if not REQUESTS_OK:
        return None, "REQUESTS module not installed. Run: pip install requests"
    try:
        hdrs = {"User-Agent": random.choice(UA_LIST)}
        if headers:
            hdrs.update(headers)
        r = requests.get(url, headers=hdrs, timeout=timeout)
        return r, None
    except requests.exceptions.Timeout:
        return None, "Request timed out"
    except requests.exceptions.ConnectionError:
        return None, "Connection error"
    except Exception as e:
        return None, str(e)

def print_section(title):
    """Print a formatted section header."""
    print(f"\n  {c('┌──', 'B')}{c('[' + title + ']', 'R', 'BOLD')}{c('──' * 20, 'B')}")
    print(f"  {c('│', 'B')}")

def print_result(key, value, status='info'):
    """Print a key: value pair with color coding."""
    color_map = {'info': 'C', 'good': 'G', 'warn': 'Y', 'bad': 'R', 'highlight': 'M'}
    vc = color_map.get(status, 'C')
    print(f"  {c('│', 'B')}  {c(key + ':', 'W', 'BOLD'):>20} {c(str(value), vc)}")

def save_report_json(data, filename):
    """Save results to JSON file."""
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    return path

def save_report_txt(text, filename):
    """Save results to TXT file."""
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    return path

# ===================================================================
#  MODULE 1: PERSON SEARCH — Name/Username to Public Footprints
# ===================================================================
def module_person_search():
    """Search for a person's digital footprint using public sources."""
    print_section("PERSON SEARCH ENGINE")
    name = input(f"  {c('>>>', 'G', 'BOLD')} Enter full name to search: {c('', 'W')}").strip()
    if not name:
        print(f"  {c('│', 'B')}  {c('✗ No input provided', 'R')}")
        return
    
    print(f"\n  {c('│', 'B')}  {c('⚡ CONDUCTING DIGITAL FOOTPRINT ANALYSIS...', 'Y')}")
    time.sleep(0.5)
    
    results = {"name": name, "sources": [], "social_media": []}
    
    # 1. Google dork-style public mentions via DuckDuckGo
    print(f"  {c('│', 'B')}  {c('→ Searching web mentions...', 'C')}")
    search_queries = [
        f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(name)}",
        f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(name)}+profile",
    ]
    web_mentions = []
    for qurl in search_queries[:1]:
        resp, err = fetch_url(qurl)
        if resp:
            html = resp.text.lower()
            mentions = len(re.findall(re.escape(name.lower()), html))
            if mentions > 0:
                web_mentions.append(f"Web mentions found: ~{mentions}")
    
    if web_mentions:
        for m in web_mentions:
            print_result("Web", m, 'good')
            results["sources"].append(m)
    else:
        print_result("Web", "No direct results (try a more specific name)", 'warn')
    
    # 2. Check common social platforms
    platforms = [
        ("GitHub", f"https://github.com/search?q={urllib.parse.quote(name)}&type=users"),
        ("LinkedIn", f"https://www.linkedin.com/pub/dir/?first={urllib.parse.quote(name.split()[0])}&last={'+'.join(name.split()[1:])}" if len(name.split())>1 else ""),
    ]
    
    for plat_name, plat_url in platforms:
        if not plat_url:
            continue
        resp, err = fetch_url(plat_url, timeout=8)
        if resp and resp.status_code == 200:
            print_result(plat_name, f"Profile likely exists (HTTP {resp.status_code})", 'good')
            results["social_media"].append({"platform": plat_name, "status": "found", "url": plat_url})
        else:
            print_result(plat_name, "Not found or blocked", 'info')
    
    # 3. Blackbird-style name-to-username permutations
    print(f"  {c('│', 'B')}  {c('→ Generating username permutations...', 'M')}")
    parts = name.lower().split()
    usernames = set()
    if len(parts) >= 1:
        usernames.add(parts[0])
        usernames.add(''.join(parts))
        usernames.add('.'.join(parts))
        usernames.add('_'.join(parts))
        usernames.add(parts[0] + (parts[-1][0] if len(parts) > 1 else ''))
        usernames.add((parts[0][0] if parts[0] else '') + parts[-1] if len(parts) > 1 else parts[0])
    print_result("Usernames", ', '.join(list(usernames)[:8]) + ('...' if len(usernames) > 8 else ''), 'info')
    results["generated_usernames"] = list(usernames)
    
    log_finding("PersonSearch", "Name", name, json.dumps(results, default=str))
    print(f"\n  {c('│', 'B')}  {c('✓ Person search complete', 'G', 'BOLD')}")

# ===================================================================
#  MODULE 2: PHONE NUMBER INTELLIGENCE
# ===================================================================
def module_phone_intel():
    """Phone number analysis using public databases and libraries."""
    print_section("PHONE NUMBER INTELLIGENCE")
    number = input(f"  {c('>>>', 'G', 'BOLD')} Enter phone (with country code, e.g. +1415555): {c('', 'W')}").strip()
    if not number:
        print(f"  {c('│', 'B')}  {c('✗ No input', 'R')}")
        return
    
    results = {"phone": number, "valid": False, "carrier": "", "location": "", "spam_score": "", "whatsapp": False}
    
    # ---------- MODULE 2A: phonenumbers library ----------
    if PHONENUM_OK:
        try:
            pn = phonenumbers.parse(number, None)
            valid = phonenumbers.is_valid_number(pn)
            results["valid"] = valid
            print_result("Valid", str(valid), 'good' if valid else 'bad')
            
            if valid:
                nat = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.NATIONAL)
                inter = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                e164 = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
                print_result("National", nat, 'info')
                print_result("International", inter, 'info')
                print_result("E164", e164, 'info')
                results["formats"] = {"national": nat, "international": inter, "e164": e164}
                
                # Carrier
                cr = carrier.name_for_number(pn, "en")
                if cr:
                    print_result("Carrier", cr, 'good')
                    results["carrier"] = cr
                
                # Location
                loc = geocoder.description_for_number(pn, "en")
                if loc:
                    print_result("Location", loc, 'good')
                    results["location"] = loc
                
                # Timezone
                tz = pn_tz.time_zones_for_number(pn)
                if tz:
                    print_result("Timezone", ', '.join(tz), 'info')
                    results["timezone"] = list(tz)
                    
                # Number type
                num_type = "Unknown"
                if phonenumbers.number_type(pn) == 0: num_type = "Fixed Line"
                elif phonenumbers.number_type(pn) == 1: num_type = "Mobile"
                elif phonenumbers.number_type(pn) == 2: num_type = "Fixed Line or Mobile"
                elif phonenumbers.number_type(pn) == 3: num_type = "Toll Free"
                elif phonenumbers.number_type(pn) == 4: num_type = "Premium Rate"
                elif phonenumbers.number_type(pn) == 5: num_type = "Shared Cost"
                elif phonenumbers.number_type(pn) == 6: num_type = "VoIP"
                elif phonenumbers.number_type(pn) == 7: num_type = "Personal Number"
                elif phonenumbers.number_type(pn) == 8: num_type = "Pager"
                print_result("Type", num_type, 'info')
                results["type"] = num_type
                
                # Country code info
                cc = pn.country_code
                print_result("Country Code", f"+{cc}", 'info')
                results["country_code"] = cc
        except Exception as e:
            print_result("Parse Error", str(e), 'bad')
    else:
        print(f"  {c('│', 'B')}  {c('⚠ phonenumbers module not installed', 'Y')}")
        print(f"  {c('│', 'B')}  {c('  Run: pip install phonenumbers', 'Y')}")
    
    # ---------- MODULE 2B: SkipCalls Spam Check (free, no key) ----------
    print(f"\n  {c('│', 'B')}  {c('→ Checking SkipCalls spam database...', 'C')}")
    clean_num = re.sub(r'[^\d]', '', number)
    if clean_num.startswith('1'): 
        clean_num = clean_num  # US numbers
    spam_url = f"https://spam.skipcalls.app/check/{clean_num}"
    resp, err = fetch_url(spam_url, timeout=10)
    if resp:
        try:
            spam_data = resp.json()
            is_spam = spam_data.get("isSpam", spam_data.get("spam", False))
            spam_score = spam_data.get("score", spam_data.get("confidence", "N/A"))
            spam_reports = spam_data.get("reports", spam_data.get("count", "N/A"))
            print_result("Spam Status", "SPAM DETECTED" if is_spam else "CLEAN", 'bad' if is_spam else 'good')
            print_result("Spam Score", str(spam_score), 'warn' if is_spam else 'good')
            print_result("Reports", str(spam_reports), 'info')
            results["spam"] = {"is_spam": is_spam, "score": spam_score, "reports": spam_reports}
        except:
            print_result("SkipCalls", "Response parse error", 'warn')
    else:
        print_result("SkipCalls", f"Offline: {err}", 'warn')
    
    # ---------- MODULE 2C: Tellows Reputation Check (free public JSON) ----------
    print(f"  {c('│', 'B')}  {c('→ Checking Tellows reputation...', 'C')}")
    tellows_num = re.sub(r'[\s\-\+\(\)]', '', number)
    tellows_url = f"https://www.tellows.de/basic/num/{tellows_num}?json=1"
    resp, err = fetch_url(tellows_url, timeout=10)
    if resp:
        try:
            td = resp.json()
            tellows_score = td.get("score", td.get("tellows_score", "N/A"))
            comments = td.get("commentCount", td.get("comments", 0))
            reputation = td.get("reputation", td.get("spamlevel", "unknown"))
            print_result("Tellows Score", f"{tellows_score}/9", 'bad' if int(tellows_score) > 5 if str(tellows_score).isdigit() else 'info')
            print_result("Comments", str(comments), 'info')
            results["tellows"] = {"score": tellows_score, "comments": comments, "reputation": reputation}
        except:
            print_result("Tellows", "Data parse error", 'warn')
    else:
        print_result("Tellows", "Offline", 'warn')
    
    # ---------- MODULE 2D: WhatsApp Presence Check ----------
    print(f"  {c('│', 'B')}  {c('→ Checking WhatsApp presence...', 'C')}")
    wa_num = re.sub(r'[^\d]', '', number)
    wa_url = f"https://wa.me/{wa_num}"
    resp, err = fetch_url(wa_url, timeout=10)
    if resp and resp.status_code == 200:
        wa_html = resp.text.lower()
        if "send?phone" in wa_html or "whatsapp.com" in wa_html:
            print_result("WhatsApp", "Number may have WhatsApp account", 'good')
            results["whatsapp"] = True
        else:
            print_result("WhatsApp", "No clear presence", 'info')
    else:
        print_result("WhatsApp", "Could not verify (rate limited)", 'warn')
    
    log_finding("PhoneIntel", "Phone", number, json.dumps(results, default=str))

# ===================================================================
#  MODULE 3: USERNAME INVESTIGATION — Cross-Platform Profile Detection
# ===================================================================
def module_username_investigation():
    """Check a username across multiple online platforms (Sherlock-style)."""
    print_section("USERNAME INVESTIGATION")
    username = input(f"  {c('>>>', 'G', 'BOLD')} Enter username to investigate: {c('', 'W')}").strip()
    if not username:
        print(f"  {c('│', 'B')}  {c('✗ No input', 'R')}")
        return
    
    results = {"username": username, "profiles_found": []}
    print(f"\n  {c('│', 'B')}  {c('⚡ Scanning 25+ platforms...', 'Y')}")
    
    # Target platforms with direct profile URL patterns
    platforms = {
        "GitHub": f"https://github.com/{username}",
        "Twitter/X": f"https://twitter.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "YouTube": f"https://www.youtube.com/@{username}",
        "Telegram": f"https://t.me/{username}",
        "Medium": f"https://medium.com/@{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Pinterest": f"https://www.pinterest.com/{username}/",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Facebook": f"https://www.facebook.com/{username}",
        "LinkedIn": f"https://www.linkedin.com/in/{username}",
        "DEV.to": f"https://dev.to/{username}",
        "Keybase": f"https://keybase.io/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "SoundCloud": f"https://soundcloud.com/{username}",
        "Spotify": f"https://open.spotify.com/user/{username}",
        "HackerNews": f"https://news.ycombinator.com/user?id={username}",
        "Imgur": f"https://imgur.com/user/{username}",
        "Patreon": f"https://www.patreon.com/{username}",
        "Behance": f"https://www.behance.net/{username}",
        "Dribbble": f"https://dribbble.com/{username}",
        "Flickr": f"https://www.flickr.com/people/{username}/",
        "VK": f"https://vk.com/{username}",
        "WhatsApp": f"https://wa.me/s/?phone={username}",
    }
    
    found_count = 0
    check_count = 0
    for plat_name, plat_url in platforms.items():
        check_count += 1
        # Quick scan with single HEAD-like request
        try:
            req = urllib.request.Request(plat_url, method='HEAD',
                headers={"User-Agent": random.choice(UA_LIST)})
            resp = urllib.request.urlopen(req, timeout=5)
            if resp.status == 200:
                found_count += 1
                print(f"  {c('│', 'B')}  {c('✓', 'G')} {c(plat_name + ':', 'W', 'BOLD'):<16} {c('PROFILE FOUND', 'G')}")
                results["profiles_found"].append({"platform": plat_name, "url": plat_url, "status": "found"})
            else:
                print(f"  {c('│', 'B')}  {c('·', 'B')} {c(plat_name + ':', 'W'):<16} {c('Not found', 'N')}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                pass  # Not found, skip
            elif e.code == 403 or e.code == 429:
                print(f"  {c('│', 'B')}  {c('·', 'B')} {c(plat_name + ':', 'W'):<16} {c(f'Rate limited ({e.code})', 'Y')}")
            else:
                print(f"  {c('│', 'B')}  {c('·', 'B')} {c(plat_name + ':', 'W'):<16} {c(f'HTTP {e.code}', 'Y')}")
        except Exception as e:
            pass  # Timeout or other errors
    
    print(f"\n  {c('│', 'B')}  {c('═══ SCAN SUMMARY', 'B')}")
    print_result("Platforms Checked", str(check_count), 'info')
    print_result("Profiles Found", str(found_count), 'good' if found_count > 0 else 'warn')
    results["profiles_found_count"] = found_count
    
    log_finding("UsernameInvestigation", "Username", username, json.dumps(results, default=str))

# ===================================================================
#  MODULE 4: EMAIL INVESTIGATION — Breach Check
def module_network_analyzer():
    """Network reconnaissance: DNS, IP, WHOIS-style lookups."""
    print_section("NETWORK ANALYZER")
    target = input(f"  {c('>>>', 'G', 'BOLD')} Enter domain or IP address: {c('', 'W')}").strip()
    if not target:
        print(f"  {c('│', 'B')}  {c('✗ No input', 'R')}")
        return
    
    results = {"target": target, "ip": "", "dns": {}, "geo": {}}
    print(f"\n  {c('│', 'B')}  {c('⚡ Analyzing network target...', 'Y')}")
    
    # ---- DNS Resolution ----
    print(f"  {c('│', 'B')}  {c('→ Resolving DNS...', 'C')}")
    try:
        ip = socket.gethostbyname(target)
        print_result("IP Address", ip, 'good')
        results["ip"] = ip
    except socket.gaierror:
        print_result("DNS", "Could not resolve", 'bad')
        ip = target
    
    # ---- Reverse DNS ----
    if ip and re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            print_result("Reverse DNS", hostname, 'info')
            results["reverse_dns"] = hostname
        except:
            pass
    
    # ---- IP Geolocation via ip-api.com (FREE, no key) ----
    if ip and re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
        print(f"  {c('│', 'B')}  {c('→ Fetching IP geolocation...', 'C')}")
        geo_url = f"http://ip-api.com/json/{ip}?fields=66846719"
        resp, err = fetch_url(geo_url, timeout=10)
        if resp:
            try:
                geo = resp.json()
                if geo.get("status") == "success":
                    print_result("Country", geo.get("country", "N/A"), 'info')
                    print_result("Region", geo.get("regionName", "N/A"), 'info')
                    print_result("City", geo.get("city", "N/A"), 'info')
                    print_result("ISP", geo.get("isp", "N/A"), 'info')
                    print_result("Org", geo.get("org", "N/A"), 'info')
                    print_result("AS", geo.get("as", "N/A"), 'info')
                    print_result("Lat/Lon", f"{geo.get('lat', '?')}, {geo.get('lon', '?')}", 'info')
                    print_result("Timezone", geo.get("timezone", "N/A"), 'info')
                    results["geo"] = geo
            except:
                print_result("GeoIP", "Parse failed", 'warn')
        else:
            print_result("GeoIP", "API unavailable", 'warn')
    
    # ---- Port Scan (common ports) ----
    print(f"  {c('│', 'B')}  {c('→ Quick port scan (common ports)...', 'M')}")
    common_ports = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 9000, 27017]
    open_ports = []
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.5)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                open_ports.append(port)
                print(f"  {c('│', 'B')}    ├ {c(f'Port {port}', 'G')} {c('OPEN', 'G', 'BOLD')}")
        except:
            pass
    
    if not open_ports:
        print_result("Ports", "No common ports open (or host filtered)", 'info')
    else:
        print_result("Open Ports", str(len(open_ports)), 'warn')
        results["open_ports"] = open_ports
    
    log_finding("NetworkAnalyzer", target, "Network scan", json.dumps(results, default=str))

# ===================================================================
#  MODULE 6: DEVICE & SYSTEM INFO
# ===================================================================
def module_device_info():
    """Gather information about the current system/device."""
    print_section("DEVICE & SYSTEM INFO")
    print(f"\n  {c('│', 'B')}  {c('⚡ Profiling current system...', 'Y')}")
    
    results = {}
    
    # OS Info
    print(f"  {c('│', 'B')}  {c('→ OS & Platform...', 'C')}")
    os_name = platform.system()
    os_release = platform.release()
    os_version = platform.version()
    arch = platform.machine()
    node = platform.node()
    
    print_result("OS", f"{os_name} {os_release}", 'info')
    print_result("Architecture", arch, 'info')
    print_result("Hostname", node, 'info')
    results["os"] = {"name": os_name, "release": os_release, "version": os_version, "arch": arch, "hostname": node}
    
    # Python Info
    py_ver = sys.version.split()[0]
    py_exe = sys.executable
    print_result("Python", py_ver, 'info')
    results["python"] = {"version": py_ver, "executable": py_exe}
    
    # Termux specific
    is_termux = os.path.exists('/data/data/com.termux')
    print_result("Termux", "Yes" if is_termux else "No", 'good' if is_termux else 'info')
    results["is_termux"] = is_termux
    
    # CPU / Memory via /proc
    print(f"  {c('│', 'B')}  {c('→ Hardware resources...', 'C')}")
    cpu_info = "N/A"
    mem_info = "N/A"
    try:
        if os.path.exists('/proc/cpuinfo'):
            with open('/proc/cpuinfo') as f:
                for line in f:
                    if 'model name' in line:
                        cpu_info = line.split(':')[1].strip()
                        break
        if os.path.exists('/proc/meminfo'):
            with open('/proc/meminfo') as f:
                for line in f:
                    if 'MemTotal' in line:
                        kb = int(line.split()[1])
                        mem_info = f"{kb // 1024} MB"
                        break
    except:
        pass
    
    print_result("CPU", cpu_info[:60] if cpu_info != "N/A" else "Unavailable", 'info')
    print_result("RAM", mem_info, 'info')
    results["hardware"] = {"cpu": cpu_info, "ram": mem_info}
    
    # Network interfaces
    print(f"  {c('│', 'B')}  {c('→ Network interfaces...', 'M')}")
    if is_termux:
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=5)
            if result.stdout:
                interfaces = []
                for line in result.stdout.split('\n'):
                    if line and not line.startswith(' '):
                        iface = line.split(':')[0]
                        interfaces.append(iface)
                print_result("Interfaces", ', '.join(interfaces), 'info')
                results["interfaces"] = interfaces
        except:
            print_result("Interfaces", "Could not enumerate", 'warn')
    else:
        try:
            import netifaces
            ifaces = netifaces.interfaces()
            print_result("Interfaces", ', '.join(ifaces[:5]) + ('...' if len(ifaces) > 5 else ''), 'info')
            results["interfaces"] = ifaces
        except ImportError:
            print_result("Interfaces", "Run: pip install netifaces", 'info')
    
    # Termux-API location
    if is_termux:
        print(f"  {c('│', 'B')}  {c('→ GPS Location (via termux-api)...', 'C')}")
        try:
            result = subprocess.run(['termux-location'], capture_output=True, text=True, timeout=10)
            if result.stdout:
                loc_data = json.loads(result.stdout)
                lat = loc_data.get('latitude', 'N/A')
                lon = loc_data.get('longitude', 'N/A')
                alt = loc_data.get('altitude', 'N/A')
                acc = loc_data.get('accuracy', 'N/A')
                print_result("Latitude", lat, 'info')
                print_result("Longitude", lon, 'info')
                print_result("Altitude", alt, 'info')
                print_result("Accuracy", acc, 'info')
                results["gps_location"] = loc_data
            else:
                print_result("GPS", "No data (enable GPS + termux-api)", 'warn')
        except FileNotFoundError:
            print_result("GPS", "termux-api not installed (pkg install termux-api)", 'warn')
        except:
            print_result("GPS", "Error accessing GPS", 'warn')
    
    log_finding("DeviceInfo", node, "System profile", json.dumps(results, default=str))

# ===================================================================
#  MODULE 7: GEO INFORMATION
# ===================================================================
def module_geo_info():
    """Geolocation intelligence from IP addresses and coordinates."""
    print_section("GEO INFORMATION")
    print(f"  {c('│', 'B')}  {c('1', 'Y')}. Lookup by IP Address")
    print(f"  {c('│', 'B')}  {c('2', 'Y')}. Lookup by Coordinates (lat,lon)")
    print(f"  {c('│', 'B')}  {c('3', 'Y')}. My Public IP Info")
    choice = input(f"\n  {c('>>>', 'G', 'BOLD')} Select option [1-3]: {c('', 'W')}").strip()
    
    results = {}
    
    if choice == '1':
        ip = input(f"  {c('>>>', 'G', 'BOLD')} Enter IP: {c('', 'W')}").strip()
        if not ip:
            return
        print(f"  {c('│', 'B')}  {c('→ Looking up IP...', 'C')}")
        geo_url = f"http://ip-api.com/json/{ip}?fields=66846719"
        resp, err = fetch_url(geo_url, timeout=10)
        if resp:
            try:
                geo = resp.json()
                if geo.get("status") == "success":
                    for key in ["country", "regionName", "city", "zip", "lat", "lon", "isp", "org", "as", "timezone"]:
                        if geo.get(key):
                            print_result(key.replace("Name","").replace("region","Region"), str(geo[key]), 'info')
                    results = geo
                else:
                    print_result("Error", geo.get("message", "Lookup failed"), 'bad')
            except:
                print_result("Error", "Parse failed", 'bad')
    
    elif choice == '2':
        coords = input(f"  {c('>>>', 'G', 'BOLD')} Enter lat,lon (e.g. 40.7128,-74.0060): {c('', 'W')}").strip()
        try:
            lat, lon = coords.replace(' ', '').split(',')
            print(f"  {c('│', 'B')}  {c('→ Reverse geocoding...', 'C')}")
            geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            resp, err = fetch_url(geo_url, timeout=12, headers={"User-Agent": "PhantomEye_OSINT/2.0"})
            if resp:
                data = resp.json()
                addr = data.get("address", {})
                display = data.get("display_name", "N/A")
                print_result("Address", display[:80] + ('...' if len(display) > 80 else ''), 'info')
                for k in ["country", "state", "city", "town", "village", "postcode"]:
                    if addr.get(k):
                        print_result(k.capitalize(), addr[k], 'info')
                results = data
            else:
                print_result("OSM", "API unavailable", 'warn')
        except:
            print_result("Error", "Invalid format. Use: lat,lon", 'bad')
    
    elif choice == '3':
        print(f"  {c('│', 'B')}  {c('→ Getting your public IP...', 'C')}")
        resp, err = fetch_url("http://ip-api.com/json/?fields=66846719", timeout=10)
        if resp:
            try:
                geo = resp.json()
                if geo.get("status") == "success":
                    print_result("Your IP", geo.get("query", "N/A"), 'good')
                    for key in ["country", "regionName", "city", "isp", "org", "timezone"]:
                        if geo.get(key):
                            print_result(key.replace("Name","").replace("region","Region"), str(geo[key]), 'info')
                    results = geo
                else:
                    print_result("Error", geo.get("message", "Lookup failed"), 'bad')
            except:
                print_result("Error", "Parse failed", 'bad')
    
    log_finding("GeoInfo", choice, "Geo lookup", json.dumps(results, default=str))

# ===================================================================
#  MODULE 8: REPORT GENERATOR
# ===================================================================
def module_report_generator():
    """Generate comprehensive reports from all findings."""
    print_section("REPORT GENERATOR")
    if not SESSION_DATA["findings"]:
        print(f"  {c('│', 'B')}  {c('⚠ No findings recorded yet. Run some modules first!', 'Y')}")
        return
    
    print(f"\n  {c('│', 'B')}  {c('1', 'Y')}. Generate TXT Report")
    print(f"  {c('│', 'B')}  {c('2', 'Y')}. Generate JSON Report")
    print(f"  {c('│', 'B')}  {c('3', 'Y')}. Generate Both")
    print(f"  {c('│', 'B')}  {c('4', 'Y')}. Generate HTML Dashboard Report")
    choice = input(f"\n  {c('>>>', 'G', 'BOLD')} Select format [1-4]: {c('', 'W')}").strip()
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r'[^\w]', '_', SESSION_DATA["target_name"] or "investigation")[:20]
    
    if choice in ['1', '3', '4']:
        # TXT Report
        txt = []
        txt.append("=" * 70)
        txt.append("  PHANTOM EYE — OSINT INVESTIGATION REPORT")
        txt.append(f"  Target: {SESSION_DATA['target_name'] or 'N/A'}")
        txt.append(f"  Generated: {datetime.datetime.now()}")
        txt.append(f"  Total Findings: {len(SESSION_DATA['findings'])}")
        txt.append("=" * 70)
        txt.append("")
        
        modules_used = set()
        for f in SESSION_DATA["findings"]:
            modules_used.add(f["module"])
        
        txt.append(f"Modules Used: {', '.join(sorted(modules_used))}")
        txt.append("")
        txt.append("-" * 70)
        txt.append("DETAILED FINDINGS:")
        txt.append("-" * 70)
        txt.append("")
        
        for i, f in enumerate(SESSION_DATA["findings"], 1):
            txt.append(f"  [{i}] Module: {f['module']}")
            txt.append(f"      Type:  {f['type']}")
            txt.append(f"      Value: {f['value']}")
            detail = f['detail']
            if len(detail) > 200:
                detail = detail[:200] + "..."
            txt.append(f"      Detail:{detail}")
            txt.append(f"      Time:  {f['timestamp']}")
            txt.append("")
        
        txt.append("=" * 70)
        txt.append("  Report generated by Phantom Eye OSINT v" + VERSION)
        txt.append("  Authorized pentesting & educational use only")
        txt.append("=" * 70)
        
        txt_path = save_report_txt('\n'.join(txt), f"{safe_name}_{timestamp}_report.txt")
        print(f"  {c('│', 'B')}  {c('✓ TXT Report saved:', 'G')} {c(txt_path, 'C')}")
    
    if choice in ['2', '3']:
        json_path = save_report_json(SESSION_DATA, f"{safe_name}_{timestamp}_report.json")
        print(f"  {c('│', 'B')}  {c('✓ JSON Report saved:', 'G')} {c(json_path, 'C')}")
    
    if choice == '4':
        # Simple HTML report
        html = []
        html.append("<!DOCTYPE html><html><head><meta charset='UTF-8'>")
        html.append(f"<title>Phantom Eye Report — {SESSION_DATA['target_name']}</title>")
        html.append("<style>")
        html.append("body{background:#0a0a0a;color:#00ff41;font-family:'Courier New',monospace;padding:20px}")
        html.append("h1{color:#ff0040;border-bottom:2px solid #00ff41;padding-bottom:10px}")
        html.append("h2{color:#00bfff}")
        html.append(".finding{border:1px solid #333;padding:10px;margin:10px 0;border-radius:5px}")
        html.append(".module{color:#ff00ff;font-weight:bold}")
        html.append(".value{color:#ffff00}")
        html.append(".time{color:#888;font-size:0.8em}")
        html.append("</style></head><body>")
        html.append(f"<h1>🔍 PHANTOM EYE OSINT REPORT</h1>")
        html.append(f"<p><strong>Target:</strong> {SESSION_DATA['target_name']}</p>")
        html.append(f"<p><strong>Generated:</strong> {datetime.datetime.now()}</p>")
        html.append(f"<p><strong>Findings:</strong> {len(SESSION_DATA['findings'])}</p>")
        html.append("<hr>")
        for i, f in enumerate(SESSION_DATA["findings"], 1):
            html.append(f"<div class='finding'>")
            html.append(f"<span class='module'>[{i}] {f['module']}</span> — <span class='value'>{f['type']}: {f['value']}</span><br>")
            html.append(f"<span class='time'>{f['timestamp']}</span>")
            html.append("</div>")
        html.append("</body></html>")
        
        html_path = os.path.join(RESULTS_DIR, f"{safe_name}_{timestamp}_report.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html))
        print(f"  {c('│', 'B')}  {c('✓ HTML Report saved:', 'G')} {c(html_path, 'C')}")

# ===================================================================
#  MODULE 9: EXTRA UTILITIES
# ===================================================================
def module_extra_utilities():
    """Extra utility tools for OSINT work."""
    print_section("EXTRA UTILITIES")
    print(f"  {c('│', 'B')}  {c('1', 'Y')}. Hash Generator (MD5, SHA1, SHA256)")
    print(f"  {c('│', 'B')}  {c('2', 'Y')}. Text/Data Encoder (base64, hex)")
    print(f"  {c('│', 'B')}  {c('3', 'Y')}. WHOIS-style Domain Info")
    print(f"  {c('│', 'B')}  {c('4', 'Y')}. IP Range Calculator (CIDR)")
    print(f"  {c('│', 'B')}  {c('5', 'Y')}. Quick URL Fetcher & Inspector")
    print(f"  {c('│', 'B')}  {c('0', 'Y')}. Back to Main Menu")
    
    choice = input(f"\n  {c('>>>', 'G', 'BOLD')} Select utility: {c('', 'W')}").strip()
    
    if choice == '1':
        data = input(f"  {c('>>>', 'G', 'BOLD')} Enter text to hash: {c('', 'W')}").strip()
        if data:
            print(f"  {c('│', 'B')}  {c('MD5:   ', 'C')} {hashlib.md5(data.encode()).hexdigest()}")
            print(f"  {c('│', 'B')}  {c('SHA1:  ', 'C')} {hashlib.sha1(data.encode()).hexdigest()}")
            print(f"  {c('│', 'B')}  {c('SHA256:', 'C')} {hashlib.sha256(data.encode()).hexdigest()}")
            log_finding("Utilities", "Hash", data[:30], "Generated hashes")
    
    elif choice == '2':
        data = input(f"  {c('>>>', 'G', 'BOLD')} Enter text to encode: {c('', 'W')}").strip()
        if data:
            b64 = base64.b64encode(data.encode()).decode()
            hexd = data.encode().hex()
            print(f"  {c('│', 'B')}  {c('Base64:', 'C')} {b64}")
            print(f"  {c('│', 'B')}  {c('Hex:   ', 'C')} {hexd}")
            log_finding("Utilities", "Encode", data[:30], "Encoded data")
    
    elif choice == '3':
        domain = input(f"  {c('>>>', 'G', 'BOLD')} Enter domain: {c('', 'W')}").strip()
        if domain:
            print(f"  {c('│', 'B')}  {c('→ Fetching domain info...', 'C')}")
            try:
                ip = socket.gethostbyname(domain)
                print_result("IP", ip, 'good')
                # Get some basic whois via ip-api (includes org/isp which approximates whois)
                resp, err = fetch_url(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=10)
                if resp:
                    geo = resp.json()
                    print_result("ISP", geo.get("isp", "N/A"), 'info')
                    print_result("Org", geo.get("org", "N/A"), 'info')
                    print_result("AS", geo.get("as", "N/A"), 'info')
                # Try direct whois if available
                try:
                    import subprocess
                    result = subprocess.run(['whois', domain], capture_output=True, text=True, timeout=10)
                    if result.stdout:
                        lines = result.stdout.split('\n')[:20]
                        print(f"\n  {c('│', 'B')}  {c('WHOIS (first 20 lines):', 'M')}")
                        for line in lines:
                            if line.strip():
                                print(f"  {c('│', 'B')}  {line[:70]}")
                except:
                    print_result("WHOIS", "whois command not available", 'info')
            except:
                print_result("Error", "Could not resolve domain", 'bad')
    
    elif choice == '4':
        cidr = input(f"  {c('>>>', 'G', 'BOLD')} Enter CIDR (e.g. 192.168.1.0/24): {c('', 'W')}").strip()
        try:
            ip_part, bits = cidr.split('/')
            bits = int(bits)
            if 0 <= bits <= 32:
                hosts = 2 ** (32 - bits)
                usable = max(0, hosts - 2)
                print_result("CIDR", cidr, 'info')
                print_result("Total IPs", str(hosts)
