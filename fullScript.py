#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/var/www/hiorg-exporter/.env")

# === Configuration ===
BASEDIR = Path("/var/www") / "hiorg-exporter"
TYPO3_PROJECT_DIR = os.getenv("TYPO3_PROJECT_DIR")
IMPORT_URL = "http://192.168.188.123/fileadmin/eventImport/new_events.xml"
STORAGE_PID = "649"
CATEGORY_MAPPING = "572:Veranstaltungen"

print(f"\n=== Log from {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
# === Step 1: Run XML Exporter ===
exporter = BASEDIR / "hiorgEventScraperXML.py"
print(f"▶ Running XML exporter: {exporter}")
subprocess.run([sys.executable, str(exporter)], check=True)

# === Step 2: Run TYPO3 Importer CLI Command ===
typo3_cmd = [
    str(TYPO3_PROJECT_DIR / "vendor/bin/typo3"),
    "news:importicsxml",
    IMPORT_URL,
    STORAGE_PID,
    "xml",
    "1", "", "", "", CATEGORY_MAPPING
]
if Path("/var/www/DRK-Goehl_Webseite/public/fileadmin/eventImport/new_events.xml").exists():
    print("▶ Importing XML into TYPO3 News...")
    subprocess.run(typo3_cmd, cwd=str(TYPO3_PROJECT_DIR), check=True)
else:
    print("⚠️ Skipping import: XML file not found.")


# === Step 3: Run Archive Date Correction ===
archive_fixer = BASEDIR / "databaseHandler.py"
print("▶ Updating archive dates for imported news...")
subprocess.run([sys.executable, str(archive_fixer)], check=True)

# === Step 4: Run Cleanup Script ===
cleanup_script = BASEDIR / "cleanup_rss.py"
print("▶ Cleaning up temporary files...")
subprocess.run([sys.executable, str(cleanup_script)], check=True)

print("✅ All steps completed.")
