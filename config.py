import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Config:
    IMAP_SERVER = os.getenv('IMAP_SERVER')
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASS = os.getenv('EMAIL_PASS')
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
    MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")
    