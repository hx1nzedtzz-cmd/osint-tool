#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                    PHANTOM EYE - OSINT Toolkit                   ║
║                  Ultimate Intelligence Gathering Platform         ║
║                      [ Ethical OSINT Framework ]                 ║
╚══════════════════════════════════════════════════════════════════╝
Author  : Phantom Security Research
Version : 2.0.0
License : Ethical OSINT - Authorized Use Only
"""

import os
import sys
import re
import json
import time
import socket
import urllib.parse
import urllib.request
import urllib.error
import subprocess
import platform
import ssl
import hashlib
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import OrderedDict
from pathlib import Path
import textwrap
import base64

# ============================================================================
# SECTION 1: GLOBAL CONFIGURATION & CONSTANTS
# ============================================================================

TOOL_NAME = "PHANTOM EYE"
VERSION = "2.0.0"
AUTHOR = "Phantom Security Research"
BANNER_COLOR = "\033[1;36m"      # Cyan
RESET = "\033[0m"
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
WHITE = "\033[1;37m"
DIM = "\033[2m"
BOLD = "\033[1m"
BG_BLACK = "\033[40m"
BG_DARK = "\033[48;5;235m"
CLEAR_LINE = "\033[K"

ASCII_BANNER = f"""
{CYAN}╔{'═'*60}╗
║ {'▀▄ ┬ ┬ ▄▀'}                    ║
║ {'▀█ └┬┘ █▀'}  {BOLD}{WHITE}PHANTOM EYE{RESET}{CYAN}           ║
║ {'█▄ ┴─┴ ▄█'}  {DIM}v{VERSION} - OSINT Framework{RESET}{CYAN}    ║
║{'─'*60}║
║ {DIM}► Phone Intel  ► Person Search  ► Username Tracking{RESET}{CYAN}  ║
║ {DIM}► Email Recon  ► Network Scan   ► Geo Tracking{RESET}{CYAN}     ║
╚{'═'*60}╝{RESET}"""

SESSION_ID = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
START_TIME = datetime.now()
SESSION_DATA = {
    "target_name": "",
    "findings": [],
    "start_time": START_TIME,
    "session_id": SESSION_ID,
    "modules_used": []
}

RESULTS_DIR = Path.home() / "phantom_eye_results"
RESULTS_DIR.mkdir(exist_ok=True)

REPORT_DATA = {
    "session_id": SESSION_ID,
    "timestamp": START_TIME.strftime("%Y-%m-%d %H:%M:%S"),
    "target": "",
    "modules_executed": [],
    "findings": [],
    "summary": {"total_findings": 0, "critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
}

# ============================================================================
# SECTION 2: UTILITY FUNCTIONS
# ============================================================================

class Spinner:
    """Terminal spinner for async operations"""
    def __init__(self, message="Processing", delay=0.1):
        self.spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.message = message
        self.delay = delay
        self.running = False
        self.thread = None

    def spin(self):
        i = 0
        while self.running:
            sys.stdout.write(f"\r{BG_DARK}{CYAN} {self.spinner[i]} {self.message}...{RESET}{CLEAR_LINE}")
            sys.stdout.flush()
            i = (i + 1) % len(self.spinner)
            time.sleep(self.delay)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin, daemon=True)
        self.thread.start()
        return self

    def stop(self, success=True):
        self.running = False
        if self.thread:
            self.thread.join()
        icon = f"{GREEN}✓" if success else f"{RED}✗"
        sys.stdout.write(f"\r{icon} {self.message}...{CLEAR_LINE}\n")
        sys.stdout.flush()


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Display animated banner with matrix reveal"""
    clear_screen()
    for line in ASCII_BANNER.split('\n'):
        print(f"\033[48;5;235m{CLEAR_LINE}{line}{RESET}")
        time.sleep(0.05)


def print_header(text: str, color: str = CYAN):
    """Print a styled section header"""
    width = 62
    padding = (width - len(text) - 2) // 2
    print(f"\n{BG_DARK}{color}╔{'═'*width}╗{RESET}")
    print(f"{BG_DARK}{color}║{' ' * padding} {text} {' ' * (width - len(text) - 2 - padding)}║{RESET}")
    print(f"{BG_DARK}{color}╚{'═'*width}╝{RESET}")


def print_result(label: str, value: str, severity: str = "info"):
    """Print a styled key-value result"""
    colors = {
        "good": GREEN,
        "bad": RED,
        "warn": YELLOW,
        "info": BLUE,
        "critical": MAGENTA
    }
    color = colors.get(severity, WHITE)
    icon_map = {"good": "✓", "bad": "✗", "warn": "!", "info": "▸", "critical": "⚠"}
    icon = icon_map.get(severity, " ")
    print(f"  {color}{icon} {WHITE}{label:<30}{color}{value}{RESET}")


def print_divider():
    """Print a styled divider"""
    print(f"  {DIM}{'─'*56}{RESET}")


def print_dashboard():
    """Display hacker-style dashboard"""
    uptime = datetime.now() - START_TIME
    uptime_str = str(uptime).split('.')[0]
    findings_count = len(REPORT_DATA["findings"])

    print(f"\n{BG_DARK}{GREEN}╔{'═'*58}╗{RESET}")
    print(f"{BG_DARK}{GREEN}║ {WHITE}SESSION DASHBOARD{RESET}{BG_DARK}{' ' * 42}{GREEN}║{RESET}")
    print(f"{BG_DARK}{GREEN}╠{'═'*58}╣{RESET}")
    print(f"{BG_DARK}{GREEN}║ {DIM}Session ID :{RESET} {YELLOW}{SESSION_ID}{RESET}{BG_DARK}{' ' * (42 - len(SESSION_ID))}{GREEN}║{RESET}")
    print(f"{BG_DARK}{GREEN}║ {DIM}Target     :{RESET} {CYAN}{REPORT_DATA['target'] or 'Not Set'}{RESET}{BG_DARK}{' ' * (38 - len(REPORT_DATA['target']))}{GREEN}║{RESET}")
    print(f"{BG_DARK}{GREEN}║ {DIM}Findings   :{RESET} {WHITE}{findings_count}{RESET}{BG_DARK}{' ' * 43}{GREEN}║{RESET}")
    print(f"{BG_DARK}{GREEN}║ {DIM}Uptime     :{RESET} {WHITE}{uptime_str}{RESET}{BG_DARK}{' ' * (42 - len(uptime_str))}{GREEN}║{RESET}")
    print(f"{BG_DARK}{GREEN}║ {DIM}Modules    :{RESET} {WHITE}{len(REPORT_DATA['modules_executed'])}{RESET}{BG_DARK}{' ' * 42}{GREEN}║{RESET}")
    print(f"{BG_DARK}{GREEN}╚{'═'*58}╝{RESET}\n")


def save_finding(category: str, label: str, value: str, severity: str = "info"):
    """Save a finding to session data"""
    finding = {
        "category": category,
        "label": label,
        "value": value,
        "severity": severity,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    REPORT_DATA["findings"].append(finding)
    REPORT_DATA["summary"]["total_findings"] += 1
    if severity in REPORT_DATA["summary"]:
        REPORT_DATA["summary"][severity] += 1


def make_request(url: str, timeout: int = 15, headers: dict = None) -> Optional[str]:
    """Secure HTTP GET request with error handling"""
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux aarch64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "text/html,application/json,*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None


def animate_text(text: str, color: str = CYAN, delay: float = 0.02):
    """Typewriter animation effect"""
    for char in text:
        sys.stdout.write(f"{color}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def type_effect(text: str, color: str = CYAN, delay: float = 0.001):
    """Fast typewriter effect for longer text"""
    sys.stdout.write(f"{color}")
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print(f"{RESET}")


# ============================================================================
# SECTION 3: MODULE 1 - PERSON SEARCH
# ============================================================================

def module_person_search():
    """Search for person information across public sources"""
    print_header(" PERSON SEARCH MODULE ", GREEN)
    print(f"  {DIM}Searching public records and social footprints...{RESET}\n")

    name = input(f"  {CYAN}> {WHITE}Enter full name to search: {RESET}").strip()
    if not name:
        print(f"  {RED}✗ No name provided.{RESET}")
        return

    REPORT_DATA["target"] = name
    SESSION_DATA["target_name"] = name
    REPORT_DATA["modules_executed"].append("Person Search")

    spinner = Spinner("Searching public sources").start()

    findings = []
    name_encoded = urllib.parse.quote(name)

    # Simulate search across multiple platforms
    sources = [
        ("Google Search", f"https://www.google.com/search?q={name_encoded}"),
        ("LinkedIn", f"https://www.linkedin.com/search/results/all/?keywords={name_encoded}"),
        ("Twitter", f"https://twitter.com/search?q={name_encoded}"),
        ("GitHub", f"https://github.com/search?q={name_encoded}&type=users"),
        ("Facebook", f"https://www.facebook.com/search/top?q={name_encoded}"),
        ("Instagram", f"https://www.instagram.com/web/search/topsearch/?query={name_encoded}"),
        ("Reddit", f"https://www.reddit.com/search/?q={name_encoded}"),
        ("YouTube", f"https://www.youtube.com/results?search_query={name_encoded}"),
        ("Pinterest", f"https://www.pinterest.com/search/people/?q={name_encoded}"),
        ("Wikipedia", f"https://en.wikipedia.org/wiki/{name_encoded.replace(' ', '_')}"),
    ]

    time.sleep(1.5)
    spinner.stop()

    print(f"  {GREEN}✓ Search complete. Found {len(sources)} potential sources.{RESET}\n")

    print_header(" SEARCH RESULTS ", GREEN)
    for source_name, url in sources:
        severity = "info"
        result = f"{DIM}[URL Generated]{RESET} {url}"
        print_result(source_name, url[:55] + "..." if len(url) > 55 else url, severity)
        save_finding("Person Search", f"{source_name}", url, "info")
        print_divider()
        time.sleep(0.1)

    print(f"\n  {YELLOW}! Tip: Use the URLs above to manually verify findings.{RESET}")
    print(f"  {DIM}Legal OSINT - all sources are public information.{RESET}")
    input(f"\n  {DIM}[Press Enter to continue]{RESET}")


# ============================================================================
# SECTION 4: MODULE 2 - PHONE INTELLIGENCE
# ============================================================================

def module_phone_intel():
    """Phone number intelligence gathering"""
    print_header(" PHONE INTELLIGENCE MODULE ", MAGENTA)
    print(f"  {DIM}Gathering phone number intelligence from public sources...{RESET}\n")

    phone = input(f"  {CYAN}> {WHITE}Enter phone number (with country code, e.g. +1XXXXXXXXXX): {RESET}").strip()
    if not phone:
        print(f"  {RED}✗ No phone number provided.{RESET}")
        return

    REPORT_DATA["target"] = phone
    REPORT_DATA["modules_executed"].append("Phone Intelligence")

    # Validate phone format
    if not phone.startswith('+'):
        phone = '+' + phone

    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    phone_encoded = urllib.parse.quote(phone_clean)

    # ---- LOCAL ANALYSIS ----
    print_header(" LOCAL ANALYSIS ", MAGENTA)

    spinner = Spinner("Analyzing phone number pattern").start()
    time.sleep(0.8)
    spinner.stop()

    # Parse number characteristics
    country_codes = {
        "1": "USA/Canada", "44": "UK", "91": "India", "49": "Germany",
        "33": "France", "39": "Italy", "34": "Spain", "61": "Australia",
        "81": "Japan", "86": "China", "82": "South Korea", "55": "Brazil",
        "7": "Russia", "971": "UAE", "966": "Saudi Arabia", "27": "South Africa",
        "52": "Mexico", "31": "Netherlands", "46": "Sweden", "47": "Norway",
        "48": "Poland", "351": "Portugal", "90": "Turkey", "98": "Iran",
        "972": "Israel", "92": "Pakistan", "880": "Bangladesh", "62": "Indonesia",
        "63": "Philippines", "84": "Vietnam", "66": "Thailand", "60": "Malaysia",
        "65": "Singapore", "64": "New Zealand", "353": "Ireland", "32": "Belgium",
        "41": "Switzerland", "43": "Austria", "45": "Denmark", "358": "Finland",
        "30": "Greece", "36": "Hungary", "354": "Iceland", "370": "Lithuania",
        "352": "Luxembourg", "356": "Malta", "377": "Monaco", "31": "Netherlands"
    }

    detected_country = "Unknown"
    for code, country in sorted(country_codes.items(), key=lambda x: -len(x[0])):
        if phone_clean.startswith('+' + code):
            detected_country = country
            break

    length = len(phone_clean) - 1
    print_result("Phone Number", phone_clean, "info")
    print_result("Detected Country", detected_country, "good" if detected_country != "Unknown" else "warn")
    print_result("Digit Length (excl. code)", str(length), "info")
    print_result("Number Type", "Mobile" if length >= 10 else "Landline", "info")
    print_divider()

    save_finding("Phone Intel", "Number", phone_clean, "info")
    save_finding("Phone Intel", "Country", detected_country, "good" if detected_country != "Unknown" else "warn")
    save_finding("Phone Intel", "Length", str(length), "info")

    # ---- ONLINE SOURCES ----
    print_header(" ONLINE SOURCE LOOKUP ", MAGENTA)

    # Source 1: tellows.de - Public phone reputation
    spinner = Spinner("Querying tellows.de reputation").start()
    time.sleep(1.2)
    tellows_url = f"https://www.tellows.de/num/{phone_clean}"
    tellows_response = make_request(tellows_url)
    tellows_score = "N/A"
    if tellows_response:
        score_match = re.search(r'<strong[^>]*class="[^"]*tellows"[^>]*>(\d+)', tellows_response)
        if score_match:
            tellows_score = score_match.group(1)
    spinner.stop(success=(tellows_score != "N/A"))

    # FIXED LINE - was invalid chained ternary, now uses proper Python syntax
    print_result("Tellows Score", f"{tellows_score}/9", 'bad' if str(tellows_score).isdigit() and int(tellows_score) > 5 else 'info')
    print_result("Tellows URL", tellows_url, "info")
    print_divider()
    save_finding("Phone Intel", "Tellows Score", str(tellows_score), "bad" if str(tellows_score).isdigit() and int(tellows_score) > 5 else "info")

    # Source 2: FreeCarrierLookup
    spinner = Spinner("Querying carrier information").start()
    time.sleep(1.0)
    carrier_url = f"http://carrierlookup.com/lookup/{phone_clean}"
    carrier_response = make_request(carrier_url)
    carrier = "Unknown"
    if carrier_response:
        carrier_match = re.search(r'Carrier[:\s]+([^<]+)', carrier_response, re.I)
        if carrier_match:
            carrier = carrier_match.group(1).strip()
    spinner.stop(success=(carrier != "Unknown"))

    print_result("Carrier", carrier, "good" if carrier != "Unknown" else "warn")
    print_divider()
    save_finding("Phone Intel", "Carrier", carrier, "good" if carrier != "Unknown" else "info")

    # Source 3: WhatsApp presence
    spinner = Spinner("Checking WhatsApp presence").start()
    time.sleep(0.8)
    wa_url = f"https://wa.me/{phone_clean}"
    wa_response = make_request(wa_url)
    wa_active = "Unknown"
    if wa_response:
        if "send" in wa_response.lower() or "WhatsApp" in wa_response:
            wa_active = "Likely Active"
        else:
            wa_active = "Possibly Inactive"
    spinner.stop()

    print_result("WhatsApp", wa_active, "good" if "Active" in wa_active else "warn")
    print_result("WhatsApp URL", wa_url, "info")
    print_divider()
    save_finding("Phone Intel", "WhatsApp", wa_active, "good" if "Active" in wa_active else "info")

    # Source 4: TrueCaller public profile check
    spinner = Spinner("Checking TrueCaller public data").start()
    time.sleep(1.0)
    tc_url = f"https://www.truecaller.com/search/{phone_clean.lstrip('+')}"
    tc_response = make_request(tc_url)
    tc_name = "Not Found"
    if tc_response:
        name_match = re.search(r'<h1[^>]*>([^<]+)', tc_response)
        if name_match:
            tc_name = name_match.group(1).strip()
    spinner.stop(success=(tc_name != "Not Found"))

    print_result("TrueCaller Name", tc_name, "good" if tc_name != "Not Found" else "warn")
    print_divider()
    save_finding("Phone Intel", "TrueCaller", tc_name, "good" if tc_name != "Not Found" else "info")

    # Source 5: Numlookup public info
    spinner = Spinner("Querying Numlookup database").start()
    time.sleep(1.3)
    nl_url = f"https://www.numlookup.com/{phone_clean}"
    nl_response = make_request(nl_url)
    nl_info = "N/A"
    if nl_response:
        loc_match = re.search(r'Location[:\s]+([^<]+)', nl_response, re.I)
        if loc_match:
            nl_info = loc_match.group(1).strip()
    spinner.stop(success=(nl_info != "N/A"))

    print_result("Numlookup Location", nl_info, "info")
    print_result("Numlookup URL", nl_url, "info")
    print_divider()
    save_finding("Phone Intel", "Numlookup", nl_info, "info")

    # Summary
    print_header(" PHONE INTELLIGENCE SUMMARY ", MAGENTA)
    print_result("Number", phone_clean, "info")
    print_result("Country", detected_country, "good")
    print_result("Carrier", carrier, "info")
    print_result("WhatsApp", wa_active, "info")
    print_result("TrueCaller", tc_name, "info")
    print_result("Tellows Score", f"{tellows_score}/9", "bad" if str(tellows_score).isdigit() and int(tellows_score) > 5 else "info")

    print(f"\n  {DIM}ℹ All data from public sources. No unauthorized access.{RESET}")
    input(f"\n  {DIM}[Press Enter to continue]{RESET}")


# ============================================================================
# SECTION 5: MODULE 3 - USERNAME INVESTIGATION
# ============================================================================

def module_username_investigation():
    """Investigate username across public platforms"""
    print_header(" USERNAME INVESTIGATION MODULE ", YELLOW)
    print(f"  {DIM}Tracking username across public platforms...{RESET}\n")

    username = input(f"  {CYAN}> {WHITE}Enter username to investigate: {RESET}").strip()
    if not username:
        print(f"  {RED}✗ No username provided.{RESET}")
        return

    REPORT_DATA["target"] = username
    REPORT_DATA["modules_executed"].append("Username Investigation")

    username_encoded = urllib.parse.quote(username)

    platforms = {
        "GitHub": f"https://github.com/{username}",
        "Twitter/X": f"https://twitter.com/{username}",
        "Instagram": f"https://instagram.com/{username}",
        "Reddit": f"https://reddit.com/user/{username}",
        "YouTube": f"https://youtube.com/@{username}",
        "TikTok": f"https://tiktok.com/@{username}",
        "Facebook": f"https://facebook.com/{username}",
        "LinkedIn": f"https://linkedin.com/in/{username}",
        "Pinterest": f"https://pinterest.com/{username}",
        "Snapchat": f"https://snapchat.com/add/{username}",
        "Telegram": f"https://t.me/{username}",
        "Twitch": f"https://twitch.tv/{username}",
        "Medium": f"https://medium.com/@{username}",
        "Dev.to": f"https://dev.to/{username}",
        "Keybase": f"https://keybase.io/{username}",
        "Replit": f"https://replit.com/@{username}",
        "Chess.com": f"https://chess.com/member/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Spotify": f"https://open.spotify.com/user/{username}",
        "WordPress": f"https://{username}.wordpress.com",
        "Blogger": f"https://{username}.blogspot.com",
        "Gravatar": f"https://gravatar.com/{username}",
        "About.me": f"https://about.me/{username}",
        "AngelList": f"https://angel.co/u/{username}",
        "ProductHunt": f"https://producthunt.com/@{username}",
        "Behance": f"https://behance.net/{username}",
        "Dribbble": f"https://dribbble.com/{username}",
     
