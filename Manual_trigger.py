# --- Function to send email ---
def send_expiry_email():
    import streamlit as st
    from datetime import datetime, timedelta
    import os
    import pandas as pd
    import smtplib
    from email.message import EmailMessage
    from config import db_run_query  # your DB helper
    from dotenv import load_dotenv
    load_dotenv()
    EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
    EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
    RECIPIENTS = os.environ['RECIPIENTS'].split(',')  # comma-separated list
    today = datetime.today().date()
    threshold = today + timedelta(days=3)
    
    df = db_run_query("SELECT product_name, expiry_date FROM products;")
    
    # --- Convert text expiry_date to datetime.date ---
    if not df.empty and "expiry_date" in df.columns:
        df["expiry_date"] = pd.to_datetime(df["expiry_date"]).dt.date

    threshold = datetime.today().date() + timedelta(days=3)

    expiring_soon = [r for r in df.itertuples(index=False) if r.expiry_date <= threshold]
    
    if not expiring_soon:
        st.info("No products expiring soon.")
        return

    msg = EmailMessage()
    msg['Subject'] = "Products Expiring Soon!"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ", ".join(RECIPIENTS)
    body = "\n".join([f"{r.product_name} expires on {r.expiry_date}" for r in expiring_soon])
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        st.success("✅ Expiry email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")
