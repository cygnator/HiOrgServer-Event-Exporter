#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from icalendar import Calendar, Event
import pytz
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/var/www/hiorg-exporter/.env")

# === CONFIGURATION ===
REMOTE_URL = os.getenv("REMOTE_URL")
BASE_DIR = os.getenv("BASE_DIR")
TYPO3_PROJECT_DIR = os.getenv("TYPO3_PROJECT_DIR")
TYPO3_URL = os.getenv("TYPO3_URL")
ALL_EVENTS_FILE = TYPO3_PROJECT_DIR / "hiorgServerFullEvents.json"
OUTPUT_ICS_FILE = TYPO3_PROJECT_DIR / "/public/fileadmin/eventImport/new_events.ics"

# Timezone
tz = pytz.timezone("Europe/Berlin")

# === Ensure Directories Exist ===
BASE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_ICS_FILE.parent.mkdir(parents=True, exist_ok=True)

# === Load Previously Stored Events ===
if ALL_EVENTS_FILE.exists():
    with open(ALL_EVENTS_FILE, "r", encoding="utf-8") as f:
        all_events = json.load(f)
else:
    all_events = []

existing_ids = {e["id"] for e in all_events}

# === Fetch Data from HiOrg ===
try:
    response = requests.get(REMOTE_URL, timeout=10)
    response.raise_for_status()
    remote_data = response.json().get("data", [])
except Exception as e:
    print(f"❌ Failed to fetch or parse data: {e}")
    exit(1)

# === Filter New Events ===
new_events = [e for e in remote_data if e["id"] not in existing_ids]

if not new_events:
    if OUTPUT_ICS_FILE.exists():
        OUTPUT_ICS_FILE.unlink()
    print("✅ No new events found.")
    exit(0)

# === Update Event Cache ===
all_events.extend(new_events)
with open(ALL_EVENTS_FILE, "w", encoding="utf-8") as f:
    json.dump(all_events, f, indent=2, ensure_ascii=False)

# === Generate ICS File ===
cal = Calendar()
cal.add("prodid", "-//DRK HiOrg Import//DE")
cal.add("version", "2.0")

for event in new_events:
    title = event.get("verbez", "DRK Veranstaltung")
    location = event.get("verort", "Unbekannt")
    dtstart = datetime.fromtimestamp(event["sortdate"], tz)
    dtend = dtstart + timedelta(days=1)

    # Description text
    if "Bereitschaftsabend" in title:
        description = f"Wir treffen uns am {dtstart.strftime('%d.%m.%Y')} um {dtstart.strftime('%H:%M')} zum Bereitschaftsabend in {location}"
    else:
        description = f"{title} in {location} am {dtstart.strftime('%d.%m.%Y')} um {dtstart.strftime('%H:%M')}"

    # Add event to calendar
    ics_event = Event()
    ics_event.add("summary", title)
    ics_event.add("dtstart", dtstart)
    ics_event.add("dtend", dtend)
    ics_event.add("location", location)
    ics_event.add("description", description)
    ics_event.add("categories", "Veranstaltungen")
    ics_event.add("uid", f"hiorg-{event['id']}@{TYPO3_URL}")
    cal.add_component(ics_event)

# === Write ICS File ===
with open(OUTPUT_ICS_FILE, "wb") as f:
    f.write(cal.to_ical())

print(f"✅ ICS file written to: {OUTPUT_ICS_FILE}")
