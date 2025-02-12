import logging
from imapclient import IMAPClient
from email import message_from_bytes
from config import Config

logger = logging.getLogger(__name__)

class EmailClient:
    def __init__(self):
        """Initialize email client with server and credentials."""
        self.server = Config.IMAP_SERVER
        self.user = Config.EMAIL_USER
        self.password = Config.EMAIL_PASS
        self.client = None

    def connect(self):
        """Establish a connection to the email server."""
        try:
            self.client = IMAPClient(self.server)
            self.client.login(self.user, self.password)
            self.client.select_folder('INBOX')
            logger.info("Connected to email server")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def fetch_unread_emails(self):
        """Retrieve unread emails from the inbox."""
        try:
            messages = self.client.search(['UNSEEN'])
            emails = []
            for msg_id, data in self.client.fetch(messages, ['RFC822']).items():
                email_message = message_from_bytes(data[b'RFC822'])
                emails.append((msg_id, email_message))
            return emails
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []