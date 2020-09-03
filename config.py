import os
from dotenv import find_dotenv, load_dotenv

# load the first .env file we find, if any

load_dotenv(find_dotenv())


class Config:
    """Default configuration"""

    DEBUG = True
    BASE_FOLDER = os.getcwd()
    PROCESS_LOG = os.path.join(BASE_FOLDER, "logs", "process_log.txt")
    REPORTS_FOLDER = os.path.join(BASE_FOLDER, "REPORTS")

    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", REPORTS_FOLDER)
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALLOWED_EXTENSIONS = set(os.environ.get("ALLOWED_EXTENSIONS", "csv").split(","))

    GMAIL_USER = os.environ.get("GMAIL_USER")
    GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")
    SENT_FROM = os.environ.get("SENT_FROM")
    GOOGLE_FOLDER_ID = os.environ.get("GOOGLE_FOLDER_ID")
    GOOGLE_TEMPLATE_ID = os.environ.get("GOOGLE_TEMPLATE_ID")
    SPIDER = True


