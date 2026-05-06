#!/usr/bin/env python3
# 🔍 MailXtract v4.2 — Email Info Scanner

import os, re, socket, requests, dns.resolver, whois, json, sys
from hashlib import md5
from datetime import datetime, timezone
from pathlib import Path

RED="\033[31m"; GRN="\033[32m"; YEL="\033[33m"
BLU="\033[34m"; MAG="\033[35m"; CYN="\033[36m"; RST="\033[0m"
WHT="\033[37m"

DISPOSABLE_DOMAINS = {
    "mailinator.com","tempmail.com","10minutemail.com","yopmail.com",
    "trashmail.com","guerrillamail.com","sharklasers.com","getnada.com",
    "throwaway.com","maildrop.cc","temp-mail.org","fakeinbox.com"
}

BLACKLIST_ZONES = ["zen.spamhaus.org", "b.barracudacentral.org"]
HEADERS = {"User-Agent":"MailXtract/4.2"}
TIMEOUT = 10

HTML_HEAD = """<html><head><meta charset='utf-8'>
<title>MailXtract Report</title>
<style>
    body{font-family:Arial;background:#0d1117;color:#c9d1d9;padding:20px}
    h1{color:#58a6ff}table{width:100%;border-collapse:collapse;background:#161b22}
    th,td{border:1px solid #30363d;padding:10px;text-align:left}
    th{background:#21262d;color:#58a6ff;width:200px}
    td{color:#c9d1d9}
    .good{color:#3fb950} .bad{color:#f85149}
</style></head><body>
<h1>📧 MailXtract Report</h1>
<table>"""
HTML_TAIL="</table></body></html>"

BANNER=f"""
{RED}╔════════════════════════════════════════════╗
{GRN}║ {YEL}🔍 MailXtract v4.2 — Email Info Scanner{' '*5}{GRN}║
{RED}║ {GRN}🔓 FREE — NO LICENSE REQUIRED{' '*22}{RED}║
{RED}╚════════════════════════════════════════════╝{RST}
"""

def rfc_validate(email):
    return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email))

def split_email(email):
    return email.split("@")[0], email.split("@")[1].lower()

def qdns(domain, rtype):
    try:
        res = dns.resolver.Resolver()
        res.nameservers = ['8.8.8.8', '1.1.1.1']
        return [r.to_text().strip('"') for r in res.resolve(domain, rtype, lifetime=TIMEOUT)]
    except:
        return None

def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return None

def dnssec(domain):
    return bool(qdns(domain, "DNSKEY"))

def bl_check(domain):
    for zone in BLACKLIST_ZONES:
        try:
            query = ".".join(reversed(domain.split("."))) + "." + zone
            dns.resolver.resolve(query, "A", lifetime=4)
            return True, zone
        except:
            continue
    return False, None

def geo(ip):
    if not ip:
        return "N/A", "N/A"
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=TIMEOUT, headers=HEADERS)
        if r.status_code == 200:
            d = r.json()
            loc = ", ".join(filter(None, [d.get("city"), d.get("region"), d.get("country_name")])) or "N/A"
            return loc, d.get("org", "N/A")
    except:
        pass
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=TIMEOUT, headers=HEADERS)
        if r.status_code == 200:
            d = r.json()
            loc = ", ".join(filter(None, [d.get("city"), d.get("region"), d.get("country")])) or "N/A"
            return loc, d.get("org", "N/A")
    except:
        pass
    return "N/A", "N/A"

def spf_dmarc(domain):
    spf = dmarc = "Not found"
    for rec in (qdns(domain, "TXT") or []):
        if "v=spf" in rec.lower():
            spf = rec
            break
    dmarc_txt = qdns(f"_dmarc.{domain}", "TXT") or []
    if dmarc_txt:
        dmarc = dmarc_txt[0]
    return spf, dmarc

def get_mx(domain):
    return qdns(domain, "MX") or []

def gravatar_check(email):
    h = md5(email.lower().encode()).hexdigest()
    url = f"https://www.gravatar.com/avatar/{h}?d=404"
    try:
        found = requests.get(url, timeout=TIMEOUT).status_code == 200
        return found, f"https://www.gravatar.com/avatar/{h}"
    except:
        return False, url

def whois_lookup(domain):
    try:
        return whois.whois(domain)
    except:
        return None

def clean_date(dt):
    if isinstance(dt, list):
        dt = dt[0]
    return dt.date() if hasattr(dt, "date") else str(dt)[:10]

def domain_age(dt):
    try:
        if isinstance(dt, list):
            dt = dt[0]
        return datetime.now(timezone.utc).year - dt.year if dt else "Unknown"
    except:
        return "Unknown"

def scan_email(email):
    result = {"email": email, "status": "success"}
    
    if not rfc_validate(email):
        result["status"] = "error"
        result["error"] = "Invalid email format"
        return result
    
    user, domain = split_email(email)
    result["username"] = user
    result["domain"] = domain
    result["disposable"] = "Yes" if domain in DISPOSABLE_DOMAINS else "No"
    result["provider_logo"] = f"https://logo.clearbit.com/{domain}"
    
    w = whois_lookup(domain)
    if w:
        result["registrar"] = w.registrar or "N/A"
        result["created"] = str(clean_date(w.creation_date)) if w.creation_date else "N/A"
        result["age"] = str(domain_age(w.creation_date)) if w.creation_date else "Unknown"
        result["expiry"] = str(clean_date(w.expiration_date)) if w.expiration_date else "N/A"
    else:
        result["registrar"] = "N/A (WHOIS blocked)"
        result["created"] = "N/A"
        result["age"] = "Unknown"
        result["expiry"] = "N/A"
    
    ip = get_ip(domain)
    result["ip"] = ip or "Not Found"
    loc, isp = geo(ip)
    result["location"] = loc
    result["isp"] = isp
    
    result["dnssec"] = "Yes" if dnssec(domain) else "No"
    bl, zone = bl_check(domain)
    result["blacklisted"] = f"Yes ({zone})" if bl else "No"
    spf, dmarc = spf_dmarc(domain)
    result["spf"] = spf
    result["dmarc"] = dmarc
    mx_records = get_mx(domain)
    result["mx"] = ", ".join(mx_records[:3]) if mx_records else "None"
    
    gfound, gurl = gravatar_check(email)
    result["gravatar"] = gurl if gfound else "Not Found"
    result["gravatar_exists"] = gfound
    
    return result

def save_txt(data, file="output.txt"):
    lines = []
    for k, v in data.items():
        if k not in ["status", "gravatar_exists", "provider_logo"]:
            lines.append(f"{k.replace('_', ' ').title()}: {v}")
    Path(file).write_text("\n".join(lines), encoding="utf-8")
    return file

def save_html(data, file="output.html"):
    rows = []
    for k, v in data.items():
        if k not in ["status", "gravatar_exists", "provider_logo"]:
            key = k.replace("_", " ").title()
            rows.append(f"<tr><th>{key}</th><td>{v}</td></tr>")
    Path(file).write_text(HTML_HEAD + "\n".join(rows) + HTML_TAIL, encoding="utf-8")
    return file

def save_json(data, file="output.json"):
    Path(file).write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return file

def main():
    os.system("clear" if os.name == "posix" else "cls")
    print(BANNER)
    
    email = input(f"{YEL}📧 Enter Email: {RST}").strip()
    
    result = scan_email(email)
    
    if result["status"] == "error":
        print(f"{RED}[!] {result['error']}{RST}")
        return
    
    print(f"\n{BLU}📋 Results for {email}{RST}\n")
    
    labels = {
        "email": "📧 Email", "username": "👤 Username", "domain": "🌐 Domain",
        "disposable": "♻️ Disposable", "registrar": "🏢 Registrar",
        "created": "📅 Created", "age": "⏰ Age (years)", "expiry": "⏳ Expiry",
        "ip": "🌍 IP Address", "location": "📍 Location", "isp": "🏭 ISP",
        "dnssec": "🔐 DNSSEC", "blacklisted": "🚫 Blacklisted",
        "spf": "📝 SPF", "dmarc": "📝 DMARC", "mx": "📬 MX Records",
        "gravatar": "👤 Gravatar"
    }
    
    for key, label in labels.items():
        if key in result:
            print(f"  {label:<20}: {result[key]}")
    
    txt_file = save_txt(result)
    html_file = save_html(result)
    json_file = save_json(result)
    
    print(f"\n{GRN}✅ Reports saved:{RST}")
    print(f"  📄 {txt_file}")
    print(f"  📄 {html_file}")
    print(f"  📄 {json_file}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Exiting...{RST}")
    except Exception as e:
        print(f"\n{RED}[!] Error: {e}{RST}")
