from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from config import db_run_query
import os
import pandas as pd
from dotenv import load_dotenv

# Load env variables
load_dotenv()
EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
RECIPIENTS = os.environ['RECIPIENTS'].split(',')  # comma-separated list

# --- Step 1: Query the database ---
df = db_run_query("SELECT product_name, expiry_date FROM products")

# --- Step 2: Process data ---
today = datetime.today().date()
threshold = today + timedelta(days=3)

# Ensure expiry_date is a date
df["expiry_date"] = pd.to_datetime(df["expiry_date"]).dt.date

# Filter
expiring_soon = df[df["expiry_date"] <= threshold]

# --- Step 3: Send email if needed ---
if not expiring_soon.empty:
    msg = EmailMessage()
    msg['Subject'] = "Products Expiring Soon!"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ", ".join(RECIPIENTS)

    body = "\n".join([f"{row.product_name} expires on {row.expiry_date}"
                      for row in expiring_soon.itertuples()])
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Error sending email:", e)
else:
    print("No products expiring soon.")