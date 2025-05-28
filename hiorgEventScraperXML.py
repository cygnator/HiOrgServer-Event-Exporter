#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from dotenv import load_dotenv
import os


load_dotenv(dotenv_path="/var/www/hiorg-exporter/.env")

# === Configuration ===
REMOTE_URL = os.getenv("REMOTE_URL")
BASE_DIR = Path(os.getenv("BASE_DIR"))
TYPO3_PROJECT_DIR = Path(os.getenv("TYPO3_PROJECT_DIR"))
TYPO3_URL = os.getenv("TYPO3_URL")
ALL_EVENTS_FILE = f"{TYPO3_PROJECT_DIR}/hiorgServerFullEvents.json"
NEW_RSS_FILE = f"{TYPO3_PROJECT_DIR}public/fileadmin/eventImport/new_events.xml"
DEFAULT_IMAGE = os.getenv("DEFAULT_IMAGE")
BEREITSCHAFT_IMAGE = os.getenv("BEREITSCHAFT_IMAGE")
BLUTSPENDE_IMAGE = os.getenv("BLUTSPENDE_IMAGE")

# === Ensure paths exist ===
BASE_DIR.mkdir(parents=True, exist_ok=True)
NEW_RSS_FILE.parent.mkdir(parents=True, exist_ok=True)

# === Load stored events ===
if ALL_EVENTS_FILE.exists():
    with open(ALL_EVENTS_FILE, "r", encoding="utf-8") as f:
        all_events = json.load(f)
else:
    all_events = []

existing_ids = {e["id"] for e in all_events}

# === Fetch events from HiOrg ===
try:
    response = requests.get(REMOTE_URL, timeout=10)
    response.raise_for_status()
    remote_data = response.json().get("data", [])
except Exception as e:
    print(f"❌ Error fetching HiOrg events: {e}")
    remote_data = []

# === Process new events ===
new_events = [e for e in remote_data if e["id"] not in existing_ids]

if not new_events:
    if NEW_RSS_FILE.exists():
        NEW_RSS_FILE.unlink()
    print("✅ No new events.")
    exit(0)

# === Save updated full list ===
all_events.extend(new_events)
with open(ALL_EVENTS_FILE, "w", encoding="utf-8") as f:
    json.dump(all_events, f, indent=2, ensure_ascii=False)

# === Generate RSS ===
rss = Element('rss', {
    'version': '2.0',
    'xmlns:content': 'http://purl.org/rss/1.0/modules/content/'
})
channel = SubElement(rss, 'channel')
SubElement(channel, 'title').text = "DRK Göhl Events"
SubElement(channel, 'link').text = f"{TYPO3_URL}"
SubElement(channel, 'description').text = "Veranstaltungen und Termine des DRK Göhl"

for event in new_events:
    dt = datetime.fromtimestamp(event["sortdate"])
    pub_date = dt.strftime("%a, %d %b %Y %H:%M:%S +0200")
    archiveDate = dt + + timedelta(days=1)
    title = event.get("verbez", "DRK Veranstaltung")
    location = event.get("verort", "Unbekannt")

    # Description formatting
    if "Bereitschaftsabend" in title:
        description = f"Wir treffen uns am {dt.strftime('%d.%m.%Y')} um {dt.strftime('%H:%M')} zum Bereitschaftsabend in {location}"
        image_url = BEREITSCHAFT_IMAGE
    elif "Blutspende" in title:
        description = f"{title} in {location} am {dt.strftime('%d.%m.%Y')} um {dt.strftime('%H:%M')}"
        image_url = BLUTSPENDE_IMAGE
    else:
        description = f"Sanitätsdienst: {title} in {location} am {dt.strftime('%d.%m.%Y')} um {dt.strftime('%H:%M')}"
        image_url = DEFAULT_IMAGE

    slug = title.lower().replace(" ", "-")

    item = SubElement(channel, 'item')
    SubElement(item, 'title').text = title
    SubElement(item, 'link').text = f"{TYPO3_URL}/events/{slug}"
    SubElement(item, 'description').text = description
    SubElement(item, '{http://purl.org/rss/1.0/modules/content/}encoded').text = f"{description}"
    SubElement(item, 'category').text = "Veranstaltungen"
    SubElement(item, 'pubDate').text = pub_date
    SubElement(item, 'archiveDate').text = archiveDate.strftime("%a, %d %b %Y %H:%M:%S +0200")
    SubElement(item, 'enclosure', {
        'url': image_url,
        'type': 'image/jpeg'
    })

# === Save to XML file ===
pretty_xml = parseString(tostring(rss, 'utf-8')).toprettyxml(indent="  ")
NEW_RSS_FILE.write_text(pretty_xml, encoding="utf-8")

print(f"✅ RSS feed with images written to: {NEW_RSS_FILE}")
