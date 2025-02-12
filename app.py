import logging
import json
from datetime import datetime
from email_client import EmailClient
from invoice_processor import InvoiceProcessor
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to process invoices from unread emails."""
    db = DatabaseManager() # Initialize database manager
    mail_client = EmailClient() # Initialize email client
    processor = InvoiceProcessor() # Initialize invoice processor

    if not mail_client.connect():
        return

    try:
        # Fetch unread emails from the mailbox
        emails = mail_client.fetch_unread_emails()
        for msg_id, email in emails:
            # Check if the email contains an invoice
            if processor.identify_invoice(email):
                invoice_data = processor.extract_invoice_data(email)
                logger.info(f"Processing invoice: {invoice_data}")
                
                # Save to database
                db.save_invoice(invoice_data)
                
                # Export to JSON
                with open('invoices.json', 'a') as f:                    
                    invoice_data.pop('_id', None)
                    json.dump(invoice_data, f)
                    f.write('\n')
                
    except Exception as e:
        logger.error(f"Error processing emails: {e}")

if __name__ == '__main__':
    main()