import pandas as pd
from datetime import datetime, timedelta
from email.message import EmailMessage
import smtplib
from config import db_run_query  # your DB helper

# Detect Streamlit environment
try:
    import streamlit as st
    USING_STREAMLIT = True
except ImportError:
    USING_STREAMLIT = False
    from dotenv import load_dotenv
    load_dotenv()

def send_expiry_email():
    # --- Load credentials ---
    if USING_STREAMLIT:
        EMAIL_ADDRESS = st.secrets.get("EMAIL_ADDRESS")
        EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD")
        RECIPIENTS_STR = st.secrets.get("RECIPIENTS", "")
    else:
        import os
        EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
        EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
        RECIPIENTS_STR = os.environ.get("RECIPIENTS", "")

    RECIPIENTS_STR = st.secrets.get("RECIPIENTS") or ""
    RECIPIENTS = [r.strip() for r in RECIPIENTS_STR.split(",") if r.strip()]


    # Check credentials
    if not all([EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENTS]):
        msg = "❌ Email credentials or recipients are missing!"
        if USING_STREAMLIT:
            st.error(msg)
        else:
            print(msg)
        return

    # --- Fetch products from DB ---
    try:
        df = db_run_query("SELECT product_name, expiry_date FROM products;")
    except Exception as e:
        msg = f"❌ Failed to fetch products: {e}"
        if USING_STREAMLIT:
            st.error(msg)
        else:
            print(msg)
        return

    if df.empty or "expiry_date" not in df.columns:
        msg = "ℹ️ No products found in database."
        if USING_STREAMLIT:
            st.info(msg)
        else:
            print(msg)
        return

    # --- Convert expiry_date to datetime.date ---
    try:
        df["expiry_date"] = pd.to_datetime(df["expiry_date"]).dt.date
    except Exception as e:
        msg = f"❌ Failed to parse expiry_date: {e}"
        if USING_STREAMLIT:
            st.error(msg)
        else:
            print(msg)
        return

    # --- Filter products expiring within 3 days ---
    threshold = datetime.today().date() + timedelta(days=3)
    expiring_soon = [r for r in df.itertuples(index=False) if r.expiry_date <= threshold]

    if not expiring_soon:
        msg = "ℹ️ No products expiring within 3 days."
        if USING_STREAMLIT:
            st.info(msg)
        else:
            print(msg)
        return

    # --- Prepare and send email ---
    msg_email = EmailMessage()
    msg_email['Subject'] = "Products Expiring Soon!"
    msg_email['From'] = EMAIL_ADDRESS
    msg_email['To'] = ", ".join(RECIPIENTS)
    body = "\n".join([f"{r.product_name} expires on {r.expiry_date}" for r in expiring_soon])
    msg_email.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg_email)
        msg = "✅ Expiry email sent successfully!"
        if USING_STREAMLIT:
            st.success(msg)
        else:
            print(msg)
    except Exception as e:
        msg = f"❌ Error sending email: {e}"
        if USING_STREAMLIT:
            st.error(msg)
        else:
            print(msg)
