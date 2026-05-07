#!/usr/bin/env python3
"""
=======================================================
 ██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗███████╗██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
 ██╔══██╗██║  ██║██╔═══██╗████╗  ██║██╔════╝██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
 ██████╔╝███████║██║   ██║██╔██╗ ██║█████╗  ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
 ██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║██╔══╝  ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
 ██║     ██║  ██║╚██████╔╝██║ ╚████║███████╗██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
 ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
 =======================================================
  PHONEPHANTOM — Advanced Phone Number OSINT Toolkit
  Authorized Pentesting Tool | Python 3 | Termux Ready
=======================================================
"""

import os
import sys
import json
import time
import re
import requests
import phonenumbers
from phonenumbers import carrier, geocoder, timezone, PhoneNumberType
from datetime import datetime
from typing import Dict, Any, Optional, List

# ─── Cyberpunk UI Styling ───────────────────────────────
class Colors:
    CYAN    = '\033[96m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    MAGENTA = '\033[95m'
    BLUE    = '\033[94m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    RESET   = '\033[0m'

SYM = {
    'arrow': f"{Colors.CYAN}▶{Colors.RESET}",
    'info': f"{Colors.BLUE}ℹ{Colors.RESET}",
    'ok': f"{Colors.GREEN}✓{Colors.RESET}",
    'warn': f"{Colors.YELLOW}⚠{Colors.RESET}",
    'err': f"{Colors.RED}✘{Colors.RESET}",
    'sep': f"{Colors.DIM}{'─'*60}{Colors.RESET}",
}

def cprint(text: str, color: str = "", bold: bool = False):
    """Print with color."""
    prefix = color
    if bold:
        prefix += Colors.BOLD
    print(f"{prefix}{text}{Colors.RESET}")

def animate_banner():
    """Animated cyberpunk banner."""
    os.system('cls' if os.name == 'nt' else 'clear')
    banner_lines = [
        f"{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════╗{Colors.RESET}",
        f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}  {Colors.MAGENTA}██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗███████╗██████╗{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}",
        f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}  {Colors.MAGENTA}██╔══██╗██║  ██║██╔═══██╗████╗  ██║██╔════╝██╔══██╗{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}",
        f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}  {Colors.MAGENTA}██████╔╝███████║██║   ██║██╔██╗ ██║█████╗  ██████╔╝{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}",
        f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}  {Colors.MAGENTA}██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║██╔══╝  ██╔═══╝ {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}",
        f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}  {Colors.MAGENTA}██║     ██║  ██║╚██████╔╝██║ ╚████║███████╗██║     {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}",
        f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET}  {Colors.MAGENTA}╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝     {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}",
        f"{Colors.CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════╝{Colors.RESET}",
    ]
    for line in banner_lines:
        print(line)
        time.sleep(0.05)
    
    subtitle = f"  {Colors.GREEN}Phone OSINT Toolkit{Colors.RESET}  {Colors.DIM}|{Colors.RESET}  {Colors.CYAN}v2.0{Colors.RESET}  {Colors.DIM}|{Colors.RESET}  {Colors.YELLOW}Termux Ready{Colors.RESET}"
    print(f"\n{' ' * 8}{subtitle}")
    
    print(f"\n{' ' * 10}{Colors.DIM}[ Initializing modules... ]{Colors.RESET}", end='', flush=True)
    for _ in range(5):
        time.sleep(0.15)
        print(f"{Colors.GREEN}.{Colors.RESET}", end='', flush=True)
    
    print(f" {Colors.GREEN}READY{Colors.RESET}\n")
    time.sleep(0.3)

def loading_animation(text: str, duration: float = 1.2):
    """Show a loading spinner."""
    spinner = '|/-\\'
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r  {Colors.CYAN}{spinner[i % len(spinner)]}{Colors.RESET} {text}...  ", end='', flush=True)
        i += 1
        time.sleep(0.1)
    print(f"\r  {Colors.GREEN}✓{Colors.RESET} {text}... {Colors.GREEN}Done{Colors.RESET}{' ' * 10}")

def format_e164(number: str) -> Optional[str]:
    """Clean and attempt to format a phone number to E.164."""
    cleaned = re.sub(r'[\s\-\(\)\.]', '', number)
    if not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    return cleaned

# ─── Module 1: Number Validator ────────────────────────
def module_validator(number_raw: str) -> Dict[str, Any]:
    """Validate and parse phone number using Google libphonenumber."""
    results = {
        'module': 'Number Validator',
        'input': number_raw,
        'valid': False,
        'e164': None,
        'national_format': None,
        'international_format': None,
        'number_type': None,
        'country_code': None,
        'national_number': None,
        'extension': None,
        'is_possible': False,
    }
    
    loading_animation("Validating number", 0.8)
    
    e164 = format_e164(number_raw)
    if not e164:
        return results
    
    try:
        num = phonenumbers.parse(e164, None)
        results['valid'] = phonenumbers.is_valid_number(num)
        results['is_possible'] = phonenumbers.is_possible_number(num)
        
        if results['valid'] or results['is_possible']:
            results['e164'] = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
            results['national_format'] = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL)
            results['international_format'] = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            results['country_code'] = num.country_code
            results['national_number'] = num.national_number
            
            if num.extension:
                results['extension'] = num.extension
            
            # Determine number type
            num_type = phonenumbers.number_type(num)
            type_map = {
                PhoneNumberType.MOBILE: 'Mobile',
                PhoneNumberType.FIXED_LINE: 'Fixed Line',
                PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Fixed Line or Mobile',
                PhoneNumberType.TOLL_FREE: 'Toll Free',
                PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
                PhoneNumberType.SHARED_COST: 'Shared Cost',
                PhoneNumberType.VOIP: 'VoIP',
                PhoneNumberType.PERSONAL_NUMBER: 'Personal Number',
                PhoneNumberType.PAGER: 'Pager',
                PhoneNumberType.UAN: 'UAN',
                PhoneNumberType.VOICEMAIL: 'Voicemail',
                PhoneNumberType.UNKNOWN: 'Unknown',
            }
            results['number_type'] = type_map.get(num_type, 'Unknown')
    
    except Exception as e:
        results['error'] = str(e)
    
    return results

# ─── Module 2: Carrier & Region Finder ─────────────────
def module_carrier_region(number_raw: str) -> Dict[str, Any]:
    """Identify carrier, geographic region, and timezone."""
    results = {
        'module': 'Carrier & Region Finder',
        'carrier': None,
        'region': None,
        'country': None,
        'timezones': [],
        'coordinates': None,
    }
    
    loading_animation("Resolving carrier & location data", 1.0)
    
    e164 = format_e164(number_raw)
    if not e164:
        return results
    
    try:
        num = phonenumbers.parse(e164, None)
        
        # Carrier info (works for mobile numbers)
        try:
            carrier_name = carrier.name_for_number(num, 'en')
            if carrier_name:
                results['carrier'] = carrier_name
        except:
            pass
        
        # Geographic region
        try:
            region = geocoder.description_for_number(num, 'en')
            if region:
                results['region'] = region
        except:
            pass
        
        # Country
        try:
            country = geocoder.country_name_for_number(num, 'en')
            if country:
                results['country'] = country
            else:
                # Fallback: region code
                from phonenumbers import PhoneNumber
                results['country'] = phonenumbers.region_code_for_number(num)
        except:
            pass
        
        # Timezones
        try:
            tz_list = timezone.time_zones_for_number(num)
            if tz_list:
                results['timezones'] = list(tz_list)
        except:
            pass
        
        # Coordinates (approximate from region code)
        try:
            from phonenumbers.geocoder import _is_mobile_number_type, country_name_for_number
            reg_code = phonenumbers.region_code_for_number(num)
            coords = {
                'US': (37.0902, -95.7129),
                'GB': (55.3781, -3.4360),
                'DE': (51.1657, 10.4515),
                'FR': (46.6034, 1.8883),
                'IN': (20.5937, 78.9629),
                'CA': (56.1304, -106.3468),
                'AU': (-25.2744, 133.7751),
                'BR': (-14.2350, -51.9253),
                'JP': (36.2048, 138.2529),
                'RU': (61.5240, 105.3188),
                'CN': (35.8617, 104.1954),
                'ZA': (-30.5595, 22.9375),
                'NG': (9.0820, 8.6753),
                'MX': (23.6345, -102.5528),
                'IT': (41.8719, 12.5674),
                'ES': (40.4637, -3.7492),
                'KR': (35.9078, 127.7669),
                'SE': (60.1282, 18.6435),
                'NL': (52.1326, 5.2913),
                'CH': (46.8182, 8.2275),
            }
            if reg_code in coords:
                results['coordinates'] = coords[reg_code]
        except:
            pass
    
    except Exception as e:
        results['error'] = str(e)
    
    return results

# ─── Module 3: Public Social Footprint Checker ─────────
def check_whatsapp(number_e164: str) -> bool:
    """Check if number has WhatsApp account via wa.me redirect."""
    try:
        resp = requests.get(
            f"https://wa.me/{number_e164.lstrip('+')}",
            timeout=8,
            allow_redirects=True,
            headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'}
        )
        # If the page shows "Send message" button, number is on WhatsApp
        # wa.me redirects to web.whatsapp.com for valid numbers
        if 'web.whatsapp.com' in resp.url:
            return True
        # Check for "not registered" indicator in response
        if 'invalid' in resp.text.lower() or 'not registered' in resp.text.lower():
            return False
        # Fallback: check if we got a valid page vs error
        if resp.status_code == 200 and len(resp.text) > 500:
            return True
        return False
    except:
        return False

def google_dork_phone(number: str) -> List[Dict[str, str]]:
    """Search for phone number exposure via Google (limited)."""
    results = []
    try:
        # We use a public search approach via textise dot iitty
        import urllib.parse
        query = urllib.parse.quote(f'"{number}"')
        resp = requests.get(
            f'https://html.duckduckgo.com/html/?q={query}',
            timeout=8,
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        )
        # Extract basic info from results
        import re
        snippets = re.findall(r'<a rel="nofollow" class="result__a" href="(.*?)".*?>(.*?)</a>', resp.text, re.DOTALL)
        for url, title in snippets[:8]:
            title_clean = re.sub(r'<[^>]+>', '', title).strip()
            if title_clean and number[:6] in resp.text:
                results.append({
                    'title': title_clean[:120],
                    'url': url
                })
    except:
        pass
    return results

def module_social_footprint(number_raw: str, e164: str = None) -> Dict[str, Any]:
    """Check public social footprint and web presence."""
    results = {
        'module': 'Public Social Footprint Checker',
        'whatsapp_registered': False,
        'google_exposure_count': 0,
        'web_mentions': [],
    }
    
    loading_animation("Scouting social footprint", 1.5)
    
    if not e164:
        e164 = format_e164(number_raw)
    if not e164:
        return results
    
    # WhatsApp check
    try:
        results['whatsapp_registered'] = check_whatsapp(e164)
    except:
        pass
    
    # Google dork / web mentions
    number_variants = [
        number_raw,
        e164.lstrip('+'),
        e164,
    ]
    
    for variant in number_variants[:2]:
        mentions = google_dork_phone(variant)
        if mentions:
            results['web_mentions'].extend(mentions)
    
    # Deduplicate
    seen_urls = set()
    unique_mentions = []
    for m in results['web_mentions']:
        if m['url'] not in seen_urls:
            seen_urls.add(m['url'])
            unique_mentions.append(m)
    results['web_mentions'] = unique_mentions[:10]
    results['google_exposure_count'] = len(results['web_mentions'])
    
    return results

# ─── Module 4: Spam/Scam Reputation Checker ──────────
def module_spam_reputation(number_raw: str) -> Dict[str, Any]:
    """Check spam/scam reputation from SkipCalls and tellows."""
    results = {
        'module': 'Spam/Scam Reputation Checker',
        'skipcalls': {'available': False, 'is_spam': None, 'spam_score': None, 'reports': None},
        'tellows': {'available': False, 'score': None, 'max_score': 9, 'location': None, 'country': None, 'comments': None},
        'overall_risk': 'Unknown',
    }
    
    loading_animation("Querying spam reputation databases", 1.5)
    
    e164 = format_e164(number_raw)
    national = re.sub(r'[\s\-\(\)\.\+]', '', number_raw)
    
    # 1. SkipCalls API (free, no key)
    try:
        resp = requests.get(
            f"https://spam.skipcalls.app/check/{national}",
            timeout=8,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        if resp.status_code == 200:
            data = resp.json()
            results['skipcalls']['available'] = True
            results['skipcalls']['is_spam'] = data.get('isSpam', data.get('spam', False))
            results['skipcalls']['spam_score'] = data.get('spamScore', data.get('score', None))
            results['skipcalls']['reports'] = data.get('reports', data.get('count', None))
    except:
        pass
    
    # 2. tellows.de (public JSON endpoint, no key needed for basic lookup)
    try:
        clean_num = re.sub(r'[^\d]', '', e164) if e164 else national
        resp = requests.get(
            f"https://www.tellows.de/basic/num/{clean_num}?json=1",
            timeout=8,
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        )
        if resp.status_code == 200:
            data = resp.json()
            if 'tellows' in data:
                tdata = data['tellows']
                results['tellows']['available'] = True
                results['tellows']['score'] = int(tdata.get('score', 0)) if tdata.get('score') else None
                results['tellows']['location'] = tdata.get('location', None)
                results['tellows']['country'] = tdata.get('country', None)
                results['tellows']['comments'] = int(tdata.get('comments', 0)) if tdata.get('comments') else None
                results['tellows']['searches'] = int(tdata.get('searches', 0)) if tdata.get('searches') else None
    except:
        pass
    
    # Determine overall risk
    risk_scores = []
    if results['skipcalls']['is_spam']:
        risk_scores.append(8)
    elif results['skipcalls']['is_spam'] == False:
        risk_scores.append(1)
    
    if results['tellows']['score'] is not None:
        ts = results['tellows']['score']
        if ts >= 7:
            risk_scores.append(9)
        elif ts >= 5:
            risk_scores.append(6)
        elif ts >= 3:
            risk_scores.append(4)
        else:
            risk_scores.append(1)
    
    if risk_scores:
        avg = sum(risk_scores) / len(risk_scores)
        if avg >= 7:
            results['overall_risk'] = 'HIGH — Likely Scam/Spam'
        elif avg >= 4:
            results['overall_risk'] = 'MEDIUM — Suspicious / Reported'
        else:
            results['overall_risk'] = 'LOW — Seems Safe'
    else:
        results['overall_risk'] = 'UNKNOWN — No reputation data found'
    
    return results

# ─── Module 5: Report Generator ────────────────────────
def module_report_generator(all_data: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """Generate consolidated TXT and JSON reports."""
    results = {'txt_path': None, 'json_path': None}
    
    loading_animation("Generating comprehensive report", 0.8)
    
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    number_tag = all_data.get('input', 'unknown').replace('+', '').replace(' ', '_')[:15]
    
    txt_path = os.path.join(output_dir, f'phonephantom_{number_tag}_{timestamp}.txt')
    json_path = os.path.join(output_dir, f'phonephantom_{number_tag}_{timestamp}.json')
    
    # JSON report
    report_json = {
        'tool': 'PhonePhantom',
        'version': '2.0',
        'scan_date': datetime.now().isoformat(),
        'target_number': all_data.get('input'),
        'results': {}
    }
    
    for key, data in all_data.items():
        if key != 'input':
            report_json['results'][key] = data
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report_json, f, indent=2, default=str)
    
    results['json_path'] = json_path
    
    # TXT report
    lines = []
    lines.append("=" * 62)
    lines.append("  PHONEPHANTOM — Phone OSINT Investigation Report")
    lines.append("=" * 62)
    lines.append(f"  Target    : {all_data.get('input', 'N/A')}")
    lines.append(f"  Date      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Tool      : PhonePhantom v2.0")
    lines.append("-" * 62)
    lines.append("")
    
    # Module 1: Validator
    if 'validator' in all_data:
        v = all_data['validator']
        lines.append("──[ MODULE 1: Number Validator ]" + "─" * 30)
        lines.append(f"  Valid          : {v.get('valid', False)}")
        lines.append(f"  Possible       : {v.get('is_possible', False)}")
        lines.append(f"  E.164          : {v.get('e164', 'N/A')}")
        lines.append(f"  National       : {v.get('national_format', 'N/A')}")
        lines.append(f"  International  : {v.get('international_format', 'N/A')}")
        lines.append(f"  Type           : {v.get('number_type', 'N/A')}")
        lines.append(f"  Country Code   : +{v.get('country_code', 'N/A')}")
        lines.append("")
    
    # Module 2: Carrier & Region
    if 'carrier_region' in all_data:
        cr = all_data['carrier_region']
        lines.append("──[ MODULE 2: Carrier & Region Finder ]" + "─" * 23)
        lines.append(f"  Carrier        : {cr.get('carrier', 'Not found')}")
        lines.append(f"  Region         : {cr.get('region', 'Not found')}")
        lines.append(f"  Country        : {cr.get('country', 'Not found')}")
        lines.append(f"  Timezones      : {', '.join(cr.get('timezones', [])) or 'N/A'}")
        if cr.get('coordinates'):
            lines.append(f"  Coordinates    : {cr['coordinates'][0]}, {cr['coordinates'][1]} (approx)")
        lines.append("")
    
    # Module 3: Social Footprint
    if 'social_footprint' in all_data:
        sf = all_data['social_footprint']
        lines.append("──[ MODULE 3: Public Social Footprint ]" + "─" * 24)
        lines.append(f"  WhatsApp       : {'REGISTERED' if sf.get('whatsapp_registered') else 'Not found'}")
        lines.append
