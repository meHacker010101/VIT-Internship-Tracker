from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import bcrypt
import random
import smtplib
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Initialize the Firebase app
if not firebase_admin._apps:
    cred = credentials.Certificate('intership-tracker-2a091-firebase-adminsdk-kpbyr-6fdcecabfd.json')
    firebase_admin.initialize_app(cred, {
        'projectId': 'intership-tracker-2a091',
    })

# Get a reference to the Firestore database
db = firestore.client()


def generate_otp():
    return random.randint(100000, 999999)

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = "mehacker010101@gmail.com"
SMTP_PASSWORD = "zoneyyslhspjxter"

def encrypt_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def send_otp(email, otp, purpose):
    # Create the email message
    message_body = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f0f2f5;
                color: #333;
                margin: 0;
                padding: 0;
                line-height: 1.6;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
                border-radius: 16px;
                padding: 30px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                width: 80px;
                height: 80px;
                background: #4CAF50;
                border-radius: 50%;
                margin: 0 auto 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }}
            h1 {{
                color: #2e7d32;
                font-size: 28px;
                margin: 20px 0;
                text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.1);
            }}
            .otp-container {{
                background: linear-gradient(135deg, #4CAF50 0%, #2e7d32 100%);
                border-radius: 12px;
                padding: 25px;
                margin: 30px 0;
                text-align: center;
            }}
            .otp {{
                font-size: 32px;
                font-weight: bold;
                color: #ffffff;
                letter-spacing: 8px;
                margin: 0;
            }}
            .timer {{
                color: #fff;
                font-size: 14px;
                margin-top: 10px;
                opacity: 0.9;
            }}
            .message {{
                background: #e8f5e9;
                border-left: 4px solid #4CAF50;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                font-size: 14px;
                color: #666;
                text-align: center;
            }}
            .footer-links a {{
                color: #4CAF50;
                text-decoration: none;
                margin: 0 15px;
                transition: color 0.3s;
            }}
            .footer-links a:hover {{
                color: #2e7d32;
                text-decoration: underline;
            }}
            .logo p{{
                margin: auto auto;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo"><p>V-I-T</p></div>
                <h2 style="margin: 10px 0 0; color: #4CAF50; font-size: 20px;">VIT Internship Tracker</h2>
                <h1>Verify Your Account</h1>
            </div>
            <div class="message">
                Hello! You've requested an OTP for <strong>{purpose}</strong>.
            </div>
            <div class="otp-container">
                <p class="otp">{otp}</p>
                <div class="timer">Valid for 10 minutes</div>
            </div>
            <footer>
                <div class="footer-links">
                    <a href="#">Privacy Policy</a>
                    <a href="#">Help Center</a>
                    <a href="https://forms.gle/FqewDcoaZx7cSeyX7">Contact Us</a>
                </div>
                <p>&copy; {datetime.now().year} VIT Internship Tracker • All rights reserved</p>
                <p style="color: #888; font-size: 12px; margin-top: 20px;">
                Disclaimer: This email and the VIT Internship Tracker are in no way affiliated with or endorsed by Vellore Institute of Technology (VIT).
                </p>
            </footer>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['Subject'] = f"OTP for {purpose}"
    msg['From'] = SMTP_USERNAME
    msg['To'] = email
    if email.endswith('@admin.in'):
        msg['To'] = "mehacker010101@gmail.com"
    msg.attach(MIMEText(message_body, 'html'))

    try:
        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()  # Identify yourself to the server
            server.starttls()  # Upgrade to a secure connection
            server.ehlo()  # Re-identify as an encrypted connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            print("OTP sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Failed to send OTP: {e}")


# Password Reset Function
def reset_password(email, new_password):
    # Update the password in Firestore
    doc_ref = db.collection('users').document(email)
    doc_ref.update({'password': encrypt_password(new_password)})
    return True, "Password has been reset successfully!"

def store_password(email, password):
    # Store the email and hashed password in Firestore
    doc_ref = db.collection('users').document(email)
    doc_ref.set({
        'email': email,
        'password': encrypt_password(password),
        'last_login': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f%z"),
        'previous_login': None
    })



def authenticate(email, password):
    try:
        # Fetch the user document from Firestore
        doc_ref = db.collection('users').document(email)
        doc = doc_ref.get()

        print(f"Document exists: {doc.exists}")  # Debug print

        if doc.exists:
            # Check if the stored password matches the provided password
            stored_password = doc.get('password')
            last_login = doc.get('last_login')
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                # Update the last login and previous login timestamps
                doc_ref.update({
                    'last_login': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f%z"),
                    'previous_login': doc.get('last_login')
                })
                return True, None, last_login
            else:
                return False, "Incorrect password", None
        else:
            return False, "Email not registered", None
    except Exception as e:
        print(f"Error during authentication: {str(e)}")  # Debug print
        raise ValueError(f"Authentication error: {str(e)}")


def rehash_passwords():
    # Fetch all user documents and rehash the passwords
    users_ref = db.collection('users')
    docs = users_ref.stream()
    for doc in docs:
        if isinstance(doc.get('password'), str):
            new_hashed_password = bcrypt.hashpw(doc.get('password').encode('utf-8'), bcrypt.gensalt())
            doc_ref = db.collection('users').document(doc.id)
            doc_ref.update({'password': new_hashed_password})

def register_user(email, password):
    # Check if the email already exists in Firestore
    doc_ref = db.collection('users').document(email)
    if doc_ref.get().exists:
        return False

    # Store the email and hashed password in Firestore
    doc_ref.set({
        'email': email,
        'password': encrypt_password(password),
        'last_login': None,
        'previous_login': None
    })
    return True

def verify_otp(sent_otp, entered_otp):
    return sent_otp == entered_otp

def check_email_exists(email):
    doc_ref = db.collection('users').document(email)
    return doc_ref.get().exists

def update_password(email, new_password):
    # Update the password in Firestore
    doc_ref = db.collection('users').document(email)
    doc_ref.update({'password': encrypt_password(new_password)})