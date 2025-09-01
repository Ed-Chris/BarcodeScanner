import streamlit as st
import cv2
import numpy as np
import requests
import sqlite3
from datetime import datetime, date
from config import db_connect

# ----------------- Database Setup -----------------
conn = db_connect()
c = conn.cursor()

st.title("📷 Grocery Barcode Scanner (Cloud-Friendly with DB)")

# Camera input
img_file = st.camera_input("Take a picture of the barcode")

if img_file:
    # Convert to OpenCV image
    file_bytes = np.asarray(bytearray(img_file.getvalue()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, 1)

    # Save temporarily to send to ZXing API
    is_success, buffer = cv2.imencode(".jpg", frame)
    if not is_success:
        st.error("Could not process image")
    else:
        files = {"f": ("barcode.jpg", buffer.tobytes(), "image/jpeg")}

        # ZXing online decode API
        api_url = "https://zxing.org/w/decode"
        response = requests.post(api_url, files=files)

        if response.status_code == 200 and "Parsed Result" in response.text:
            # Extract barcode value from HTML
            start = response.text.find("<pre>") + 5
            end = response.text.find("</pre>")
            barcode_data = response.text[start:end].strip()

            if barcode_data:
                st.success(f"✅ Detected barcode: {barcode_data}")

                # OpenFoodFacts API
                url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_data}.json"
                res = requests.get(url).json()
                product_name = "Unknown Product"

                if res.get("status") == 1:
                    product = res["product"]
                    product_name = product.get("product_name", "Unknown Product")

                    st.subheader(product_name)
                    st.write(f"**Brand:** {product.get('brands', 'Unknown')}")
                    st.write(f"**Quantity:** {product.get('quantity', 'Unknown')}")

                else:
                    st.warning("Product not found in OpenFoodFacts")

                # --- Expiry Date Input ---
                expiry_date = st.date_input("📅 Enter expiry date", min_value=date.today())

                # --- Save to DB ---
                if st.button("💾 Save to Database"):
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c.execute(
                        "INSERT INTO products (barcode, product_name, expiry_date, created_at) VALUES (?, ?, ?, ?)",
                        (barcode_data, product_name, str(expiry_date), created_at)
                    )
                    conn.commit()
                    st.success("✅ Product saved to database!")

            else:
                st.warning("No barcode found in image.")
        else:
            st.error("Error contacting ZXing API or barcode could not be detected.")

# ----------------- Show Database -----------------
if st.checkbox("📑 Show saved records"):
    c.execute("SELECT * FROM products ORDER BY created_at DESC")
    rows = c.fetchall()
    st.table(rows)
