from flask import Flask, render_template, request, redirect
from database import DatabaseManager
from datetime import datetime
from bson.objectid import ObjectId
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)
db = DatabaseManager()

@app.route('/')
def invoice_dashboard():  
    """Fetch and display invoices on the dashboard."""  
    try:
        invoices = list(db.collection.find().sort("due_date", 1))
        today = datetime.now().date()
        
        # Validate invoice data
        valid_invoices = []
        for inv in invoices:
            try:
                # Convert MongoDB dates
                inv['due_date'] = inv['due_date'].strftime("%Y-%m-%d")
                inv['processed_at'] = inv['processed_at'].strftime("%Y-%m-%d %H:%M")
                
                # Validate required fields
                if not all([inv.get('sender'), inv.get('invoice_number'), inv.get('amount')]):
                    raise ValueError("Missing required fields")
                    
                valid_invoices.append(inv)
                
            except Exception as e:
                logger.error(f"Invalid invoice {inv.get('_id')}: {e}")
                continue

        return render_template('dashboard.html', 
                            invoices=valid_invoices,
                            now=today.isoformat())
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return "Error loading dashboard", 500

@app.route('/edit/<invoice_id>', methods=['GET', 'POST'])
def edit_invoice(invoice_id):
    """Edit an existing invoice."""
    try:
        if request.method == 'POST':
            update_data = {
                "invoice_number": request.form.get('invoice_number'),
                "amount": float(request.form.get('amount')),
                "due_date": datetime.strptime(request.form.get('due_date'), "%Y-%m-%d")
            }
            db.collection.update_one(
                {"_id": ObjectId(invoice_id)},
                {"$set": update_data}
            )
            return redirect('/')
        
        invoice = db.collection.find_one({"_id": ObjectId(invoice_id)})
        if not invoice:
            return "Invoice not found", 404
            
        invoice['due_date'] = invoice['due_date'].strftime("%Y-%m-%d")
        return render_template('edit.html', invoice=invoice)
    
    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    app.run(port=5000)