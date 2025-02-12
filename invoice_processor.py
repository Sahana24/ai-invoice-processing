import re
import logging
import pdfplumber
from google.cloud import vision
import io
from config import Config
from datetime import datetime

# Google Vision API Client
client = vision.ImageAnnotatorClient.from_service_account_file("google_vision_key.json")
logger = logging.getLogger(__name__)

class InvoiceProcessor:
    # Regular expressions for extracting invoice details
    PATTERNS = {
        'invoice_number': r'(?:Invoice|Bill)\s*(?:Number|#|No\.?)\s*:?\s*([A-Z0-9]+(?:[-/\.][A-Z0-9]+)+)',
        'amount': r'(?:Total\s+(?:Amount\s+Due|Due|Amount)\s*:?\s*)([$€£]?\s*\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2}))',
        'due_date': r'(?:(?:Payment\s+)?Due\s+(?:Date|By)|Pay\s+by)\s*:?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})'
    }

    def __init__(self, db_manager=None):
        self.db = db_manager

    def _extract_pdf_text(self, content):
        """Extract text from a PDF using Google Vision API."""
        try:
            pdf_reader = pdfplumber.open(io.BytesIO(content))
            extracted_text = ""
            for page in pdf_reader.pages:
                img_bytes = page.to_image(resolution=300).original.convert("RGB")
                img_byte_arr = io.BytesIO()
                img_bytes.save(img_byte_arr, format="PNG")
                image = vision.Image(content=img_byte_arr.getvalue())
                response = client.text_detection(image=image)
                text = response.text_annotations[0].description if response.text_annotations else ""
                extracted_text += text + "\n"
            return extracted_text.strip()
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            return ""
        
    def detect_recurring(self, current_invoice):
        """Check if the invoice is recurring based on sender and amount."""
        if not self.db:
            return False
            
        existing = self.db.collection.find({
            "sender": current_invoice['sender'],
            "amount": {"$gte": current_invoice['amount'] * 0.9, "$lte": current_invoice['amount'] * 1.1}
        }).sort("processed_at", -1).limit(1)

        if existing:
            last_invoice = existing[0]
            time_diff = datetime.now() - last_invoice['processed_at']
            if 25 <= time_diff.days <= 35:
                return True
        return False

    def extract_invoice_data(self, email):
        """Main method to extract invoice data from email attachments."""
        sender = self._extract_sender(email['From'])
        text_content = self._get_email_text(email)
        pdf_text = self._process_attachments(email)
        full_text = f"{text_content}\n{pdf_text}"

        invoice_number = self._extract_field('invoice_number', full_text)
        if invoice_number:
            invoice_number = invoice_number.replace(" ", "")

        amount = self._parse_amount(self._extract_field('amount', full_text))

        due_date_str = self._extract_field('due_date', full_text)
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                try:
                    due_date = datetime.strptime(due_date_str, "%d/%m/%Y").date()
                except ValueError:
                    try:
                        due_date = datetime.strptime(due_date_str, "%d-%m-%Y").date()
                    except ValueError:
                        try:
                            due_date = datetime.strptime(due_date_str, "%d %b %Y").date()
                        except ValueError:
                            print(f"Invalid Date Format: {due_date_str}")

        print("\n[DEBUG] Extracted Invoice Data:")
        print(f"Sender: {sender}")
        print(f"Invoice Number: {invoice_number}")
        print(f"Amount: {amount}")
        print(f"Due Date: {due_date}")

        invoice_data = {
            'sender': sender,
            'invoice_number': invoice_number,
            'amount': amount,
            'due_date': due_date.isoformat() if due_date else None
        }

        invoice_data['is_recurring'] = self.detect_recurring(invoice_data)
        return invoice_data

    def identify_invoice(self, email):
        """Determine if an email contains an invoice"""
        subject = email.get('Subject', '')

        if self._is_invoice_subject(subject):
            return True
        return self._has_pdf_attachment(email)

    def _is_invoice_subject(self, subject):
        """Check if subject contains invoice-related keywords"""
        invoice_keywords = ["invoice", "bill", "payment due", "receipt"]
        return any(keyword in subject.lower() for keyword in invoice_keywords)

    def _has_pdf_attachment(self, email):
        """Check if an email contains a PDF attachment"""
        for part in email.walk():
            if part.get_content_type() == 'application/pdf':
                return True
        return False
    
    def _extract_sender(self, from_header):
        """Extracts sender email address from the 'From' header"""
        try:
            match = re.search(r'<(.+?)>', from_header)
            if match:
                return match.group(1)  
            return from_header.strip()  
        except Exception as e:
            logging.error(f"Error parsing sender: {e}")
            return "Unknown Sender"
        
    def _get_email_text(self, email):
        """Extracts text content from the email body"""
        try:
            for part in email.walk():
                if part.get_content_type() == 'text/plain':  # Extract plain text content
                    return part.get_payload(decode=True).decode(errors='ignore')
            return ""  # If no text/plain part is found, return empty string
        except Exception as e:
            logging.error(f"Error reading email text: {e}")
            return ""
        
    def _process_attachments(self, email):
        """Process all PDF attachments and extract text"""
        pdf_text = ""
        for part in email.walk():
            if part.get_content_type() == 'application/pdf':
                try:
                    content = part.get_payload(decode=True)
                    pdf_text += self._extract_pdf_text(content) + "\n"
                except Exception as e:
                    logger.error(f"Error processing PDF attachment: {e}")
        return pdf_text.strip()
    
    def _extract_field(self, field_name, text):
        """Extracts a specific field (invoice number, amount, due date) using regex"""
        try:
            pattern = self.PATTERNS[field_name]
            match = re.search(pattern, text, re.IGNORECASE)
            return match.group(1) if match else None
        except KeyError:
            logging.error(f"Invalid field name: {field_name}")
            return None
        
    def _parse_amount(self, amount_str):
        """Convert extracted amount string into a float."""
        if not amount_str:
            return None
        try:
            # Handle currency symbols and thousand separators
            clean = amount_str.replace(",", "").replace("$", "").replace("€", "").replace("£", "")
            return float(clean)
        except ValueError:
            return None