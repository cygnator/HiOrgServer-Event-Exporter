#!/usr/bin/env python3
from pathlib import Path
from dotenv import load_dotenv
import os



load_dotenv(dotenv_path="/var/www/hiorg-exporter/.env")
TYPO3_PROJECT_DIR = os.environ.get("TYPO3_PROJECT_DIR")
rss_file = TYPO3_PROJECT_DIR / "public/fileadmin/eventImport/new_events.xml"

if rss_file.exists():
    rss_file.unlink()
    print("✅ RSS file deleted.")
else:
    print("ℹ️ No RSS file to delete.")
