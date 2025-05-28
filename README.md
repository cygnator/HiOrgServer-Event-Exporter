# HiOrgServer-Event-Exporter
A Set of Python Scripts to Export HiOrgs Server Events and import them into Typo3 news.

This script uses the Typo3 News importer from georgringer to import public HiOrg Server Events into the Typo3 News.

To use this script you need python3 python3-pip mysql-client and cron on your server. On Typo 3 you need news and news_importicsxml.

For python you need pytz pymysql python-dotenv.

____
# Configuration

For configuration you need a .env file with your variables.

This is an example:
```
DB_HOST = "{db host - typical localhost}"
DB_USER = "{db user name}"
DB_PASS = "{db password}"
DB_NAME = "{db name}"
CATEGORY_UID = {ID of category you want to import to}
TYPO3_PROJECT_DIR = {Typo 3 Website document root}
STORAGE_PID = {UID of Import storage in typo3}
CATEGORY_MAPPING = "{Mapping for Category: uid of category:"Veranstalltung"}"
TYPO3_URL = "{URL of Typo3 Site}"
DEFAULT_IMAGE = "${TYPO3_URL}/{fileadmin path for Default Image}"
BEREITSCHAFT_IMAGE = "${TYPO3_URL}/{fileadmin path for Dienstabend Image}"
BLUTSPENDE_IMAGE = "${TYPO3_URL}/{fileadmin path for Blutspende Image}"

```
