import os
from dotenv import find_dotenv, load_dotenv
from pathlib import Path
from globals import Globals

# load the first .env file we find, if any

load_dotenv(find_dotenv())


class Config:
    """Default configuration"""

    DEBUG = True
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", Globals.gbl_report_folder)
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALLOWED_EXTENSIONS = set(os.environ.get("ALLOWED_EXTENSIONS", "csv").split(","))
