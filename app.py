from flask import Flask, render_template, request, redirect, flash, url_for
from flask_mail import Mail, Message
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
import os
from threading import Thread

# Load environment variables (Local)
load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'selvi_textiles_secret_key')

# Flask-Mail Configuration for Vercel/Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'navaneethanv686@gmail.com'
# Use password from environment variable or hardcoded fallback for immediate functional testing on Vercel
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'rsad myyu sqhs oiww')
app.config['MAIL_DEFAULT_SENDER'] = ('Selvi Textiles', 'navaneethanv686@gmail.com')

mail = Mail(app)


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print("Email sent successfully via background thread!")
        except Exception as e:
            print(f"Background Email Error: {e}")

def send_mail(msg):
    # Asynchronous sending for better user experience
    Thread(target=send_async_email, args=(app, msg)).start()

# MongoDB Configuration (Local or Cloud)
MONGO_URI = os.environ.get('MONGO_URI', "mongodb://localhost:27017/")

try:
    # Set a 2-second timeout for server selection to prevent long hangs if DB is unreachable
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client["selvi_textiles"]
    contacts_collection = db["contacts"]
    inquiries_collection = db["inquiries"]
except Exception as e:
    print(f"Could not connect to MongoDB: {e}")

# Product catalog
PRODUCTS = [
    {
        "id": 1, 
        "name": "Medical Bandage", 
        "description": "High-quality, durable medical compression bandages for effective wound care and support.", 
        "image": "/static/images/product_1.jpg"
    },
    {
        "id": 2, 
        "name": "Cotton Rolls", 
        "description": "100% pure surgical grade absorbent cotton rolls for hospital, clinical, and personal use.", 
        "image": "/static/images/product_2.jpg"
    },
    {
        "id": 3, 
        "name": "Roller Bandage", 
        "description": "Sterile, non-fraying, and flexible roller bandages ensuring secure and comfortable dressing.", 
        "image": "/static/images/product_3.jpg"
    },
    {
        "id": 4, 
        "name": "Gamjee Roll", 
        "description": "Premium absorbent gauze roll, highly breathable and suitable for various medical applications.", 
        "image": "/static/images/product_4.jpg"
    },
    {
        "id": 5, 
        "name": "Gauze Swab", 
        "description": "Medical-grade sterile gauze swabs designed for precision clinical procedures and hygiene.", 
        "image": "/static/images/gauze_swab.png"
    },
    {
        "id": 6, 
        "name": "Surgical Masks", 
        "description": "3-ply protective medical masks designed for daily clinic use and preventing airborne contamination.", 
        "image": "/static/images/product_6.jpeg"
    },
    {
        "id": 7, 
        "name": "Dressing Pad | Mopping Pad", 
        "description": "Premium absorbent sterile dressing and mopping pads for effective wound care, surgical procedures, and optimal medical hygiene.", 
        "image": "/static/images/product_7.jpg"
    },
    {
        "id": 8, 
        "name": "Surgical Gown", 
        "description": "Standard sterile surgical gown for professional use in operating rooms, providing a high level of fluid resistance and comfort.", 
        "image": "/static/images/product_8.jpg"
    },
    {
        "id": 9, 
        "name": "Surgical Cap", 
        "description": "Lightweight and breathable medical surgical cap designed for full hair coverage and hygiene in clinical environments.", 
        "image": "/static/images/product_9.jpg"
    },
    {
        "id": 10, 
        "name": "Medical Nitrile Gloves", 
        "description": "Durable and puncture-resistant medical-grade nitrile gloves, providing superior protection and tactile sensitivity for clinical use.", 
        "image": "/static/images/product_10.jpg"
    }
]

@app.route('/')
def home():
    return render_template('index.html', title='Home')

@app.route('/about')
def about():
    return render_template('about.html', title='About Us')

@app.route('/products')
def products():
    return render_template('products.html', title='Our Products', products=PRODUCTS)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Prepare contact data
        contact_data = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "submitted_at": datetime.datetime.now()
        }

        # Try to save to Database
        db_saved = False
        try:
            contacts_collection.insert_one(contact_data)
            db_saved = True
        except Exception as e:
            print(f"Database Save Error: {e}")

        # Try to send Email notification
        email_sent = False
        try:
            msg = Message(
                subject=f"Contact Inquiry: {subject}",
                recipients=['navaneethanv686@gmail.com'],
                body=f"New Contact Form Submission:\n\nName: {name}\nEmail: {email}\nSubject: {subject}\nMessage: {message}"
            )
            send_mail(msg)
            email_sent = True
        except Exception as e:
            print(f"Email Send Error: {e}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if db_saved or email_sent:
                return {"status": "success", "message": f"Thank you, {name}. Your message has been received!"}
            else:
                return {"status": "error", "message": "Sorry, we encountered an error."}, 500

        if db_saved or email_sent:
            flash(f"Thank you, {name}. Your message has been received! Our team will get back to you soon.", "success")
        else:
            flash("Sorry, we encountered an error processing your request. Please contact us via WhatsApp or Phone.", "error")

        return redirect(url_for('contact'))
    return render_template('contact.html', title='Contact Us')


@app.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    product_name = request.args.get('product', '')
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        product_list = request.form.getlist('product')
        product = ", ".join(product_list) if product_list else "Not Specified"
        quantity = request.form.get('quantity')
        message = request.form.get('message')
        # Store in DB
        inquiry_data = {
            "name": name,
            "phone": phone,
            "products": product_list,  # Store as a list in DB
            "product_summary": product, # For legacy/easy view
            "quantity": quantity,
            "message": message,
            "submitted_at": datetime.datetime.now()
        }
        # Try to store in Database
        db_saved = False
        try:
            inquiries_collection.insert_one(inquiry_data)
            db_saved = True
        except Exception as e:
            print(f"Inquiry Database Error: {e}")

        # Try to send Email notification
        email_sent = False
        try:
            msg = Message(
                subject=f"New Quote Request: {product}",
                recipients=['navaneethanv686@gmail.com'],
                body=f"Hello,\n\nYou have a new Quote Request:\n\nName: {name}\nPhone: {phone}\nProduct: {product}\nQuantity: {quantity}\nMessage: {message}"
            )
            send_mail(msg)
            email_sent = True
        except Exception as e:
            print(f"Inquiry Email Error: {e}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if db_saved or email_sent:
                return {"status": "success", "message": f"Your quote request for {product} has been successfully sent!"}
            else:
                return {"status": "error", "message": "Inquiry could not be processed."}, 500

        if db_saved or email_sent:
            flash(f"Your quote request for {product} has been successfully sent! We will contact you soon.", "success")
        else:
            flash("Your request could not be processed at the moment. Please call us directly.", "error")

        return redirect(url_for('products'))
    return render_template('inquiry.html', title='Request Quote', product_name=product_name, products=PRODUCTS)

@app.route('/admin')
def admin():
    try:
        contacts = list(contacts_collection.find().sort("submitted_at", -1))
        inquiries = list(inquiries_collection.find().sort("submitted_at", -1))
    except Exception as e:
        contacts = []
        inquiries = []
        flash("Could not fetch data from database.", "error")
        print("Fetch Error:", e)
    return render_template('admin.html', title='Admin Dashboard', contacts=contacts, inquiries=inquiries)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
