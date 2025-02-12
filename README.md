# AI-Supported Invoice Processing Tool 

This project automates invoice processing by **fetching invoices from emails**, **extracting key details**, and **storing them in MongoDB**. It uses **Google Vision API** to extract invoice information from PDF attachments.

## Features

- Automatically fetches invoices from emails
- Extracts key invoice details (Invoice Number, Amount, Due Date, Sender)
- Processes PDF attachments using Google Vision API
- Stores extracted invoices in MongoDB
- Simple Web Dashboard for viewing and editing invoices

## Technologies Used

- **Python** (Flask, pymongo, pdfplumber, IMAPClient)
- **MongoDB Atlas** (Database for invoices)
- **Google Vision API** (OCR for extracting text from PDFs)
- **Flask** (For the web dashboard)
- **CSS** (For styling)

## Setup Guide

1. Prerequisites
    - Python 3.8+
    - MongoDB instance (local/Atlas)
    - Google Cloud Account (For Vision API)
    - Email account for IMAP Access

2. Installation
``` bash
# Clone repository
git clone https://github.com/yourusername/invoice-processor.git
cd invoice-processor

# Install dependencies
pip install flask pymongo imapclient pdfplumber google-cloud-vision pillow python-dotenv
```

3. Congiguration
Create ```.env``` file
```bash
# Email Configuration
IMAP_SERVER=imap.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-email-password

# MongoDB Configuration (For MongoDB Atlas)
MONGO_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=ai-invoice
MONGO_COLLECTION_NAME=invoices
```

4. Google Vision Setup
    - Create service account credentials in Google cloud console
    - Download the JSON Key File
    - Save as ```google_vision_key.json``` in project root

## Usage

### Process Emails
```bash
python app.py
```

### Access Dashboard
```bash
python dashboard.py
```
Visit ```http://localhost:5000``` to:
- View all the invoices
- Edit incorrect data
- Identify Overdue Payments
- Track recurring bills 


## Project Structure
``` plaintext
AI-Invoice-Processing/
│── app.py                   # Main script to process invoices
│── config.py                # Configuration settings
│── database.py              # MongoDB integration
│── email_client.py          # Fetches emails via IMAP
│── invoice_processor.py     # Extracts invoice data from PDFs and texts
│── dashboard.py             # Flask web dashboard
│── static/
│   └── styles.css           # Styles for UI
│── templates/
│   ├── dashboard.html       # Invoice list page
│   ├── edit.html            # Edit invoice details
│── .env                     # Environment variables
│── requirements.txt         # Python dependencies
│── README.md                # Documentation
```

## Example Usage
This section demonstrates how the AI Supported Invoice Processing Tool works with real examples.

---

### Sample Invoices for Testing
To test the tool, attach one of the sample invoices to an email and process it.
- Standard Invoice (USD): `static/invoices/Invoice_Details_1.pdf`
- UK Invoice with VAT (GBP): `static/invoices/Invoice_Details_1.pdf`

**How to use these sample invoices:**
1. **Send an email to yourself** with the **subject** `"Invoice INV-2025-00123"`.
2. **Attach one of the invoice PDFs** from the paths mentioned above.
3. **Run the invoice processor script**:
   ```bash
   python app.py
   ```
4. **Start the web dashboard and view the extracted invoice**:
    ```bash
   python dashboard.py
   ```

### Screenshots: How it looks in the Dashboard

#### **Invoice Management Dashboard**
Once an invoice is processed, it will be displayed in the web dashboard.
- **Columns:**
  - Sender, Invoice Number, Amount, Due Date, Processed At, Status
- **Invoice Status:**
  - **Recurring:** Automatically detected repeating invoices.
  - **Overdue:** Past-due invoices.
  - **No Due Date:** Invoices without a due date.
  - **No Status:** Default state for invoices without special condition
- **Actions:**
  - **Edit:** Modify invoice details.
 
**Dashboard Screenshot:**

![Invoice Management](static/images/invoice_management.png)

#### **Editing an Invoice**
This page allows users to edit an existing invoice.

- **Editable Fields:**
  - Invoice Number
  - Amount
  - Due Date
- **Action Buttons:**
  - `"Save Changes"` – Updates the invoice.

**Edit Invoice Screenshot:**

![Edit Invoice](static/images/edit_invoice.png)
