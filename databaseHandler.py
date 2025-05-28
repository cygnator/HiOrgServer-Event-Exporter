#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/var/www/hiorg-exporter/.env")

# === CONFIGURE ===
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
CATEGORY_UID = os.getenv("CATEGORY_UID")


# === Connect to MySQL ===
conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

with conn:
    with conn.cursor() as cursor:
        # Update records where archive is 0 (not set)
        sql = f"""
            UPDATE tx_news_domain_model_news n
            JOIN sys_category_record_mm mm ON mm.uid_foreign = n.uid
            SET n.archive = UNIX_TIMESTAMP(DATE_ADD(FROM_UNIXTIME(n.datetime), INTERVAL 1 DAY))
            WHERE n.archive = 0
              AND mm.uid_local = %s
              AND mm.tablenames = 'tx_news_domain_model_news'
        """
        cursor.execute(sql, (CATEGORY_UID,))
        affected = cursor.rowcount
        conn.commit()

print(f"✅ Updated archive date for {affected} news record(s) in category UID {CATEGORY_UID}.")
