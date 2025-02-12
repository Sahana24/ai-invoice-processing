from pymongo import MongoClient
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        """Initialize MongoDB connection."""
        try:
            self.client = MongoClient(Config.MONGO_URI)
            self.db = self.client[Config.MONGO_DB_NAME]
            self.collection = self.db[Config.MONGO_COLLECTION_NAME]
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    def save_invoice(self, invoice_data):
        """Save extracted invoice data to MongoDB."""
        try:
            # Convert date strings to datetime objects
            document = {
                "sender": invoice_data['sender'],
                "invoice_number": invoice_data['invoice_number'],
                "amount": invoice_data['amount'],
                "due_date": datetime.fromisoformat(invoice_data['due_date']) if invoice_data['due_date'] else None,
                "processed_at": datetime.now(),
                "is_recurring": invoice_data.get('is_recurring', False)
            }
            
            result = self.collection.insert_one(document)
            logger.info(f"Inserted invoice with ID: {result.inserted_id}")
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"Error saving invoice: {e}")
            raise