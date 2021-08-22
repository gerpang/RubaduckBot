import datetime
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Required*
TOKEN = os.environ.get("TOKEN", "")
NAME = os.environ.get("NAME", "")
HOUR = int(os.environ.get("HOUR", 10))
MINUTE = int(os.environ.get("MINUTE", 00))
DAILY_TIME = datetime.time(hour=HOUR, minute=MINUTE)

# File locations
START_FILE = "app/msg/start.md"
DAILY_FILE = "app/msg/daily.md"
EXAMPLE_FILE = "app/msg/example.md"
ERROR_FILE = "app/msg/error.md"

chat_ids = os.environ.get("CHAT_ID", "").replace(" ", "").split(",")

# Port and link is given by Heroku/ngrok
PORT = os.environ.get("PORT", None)
LINK = os.environ.get("LINK", None)