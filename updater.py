import os
from telegram.ext.updater import Updater
from dotenv import load_dotenv

load_dotenv()

updater = Updater( os.getenv("TELEGRAM_TOKEN") )