import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from config import db_connect
# from email_secrets import EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENTS
import os

conn = db_connect()
c = conn.cursor()

today = datetime.today().date()
threshold = today + timedelta(days=3)

c.execute("SELECT product_name, expiry_date FROM products")
rows = c.fetchall()

expiring_soon = [r for r in rows if datetime.strptime(r[1], "%Y-%m-%d").date() <= threshold]

EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
RECIPIENTS = os.environ['RECIPIENTS'].split(',')  # comma-separated list

if expiring_soon:
    msg = EmailMessage()
    msg['Subject'] = "Products Expiring Soon!"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ", ".join(RECIPIENTS)
    body = "\n".join([f"{r[0]} expires on {r[1]}" for r in expiring_soon])
    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        print("Notification email sent.")