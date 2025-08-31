import streamlit as st
import cv2
import numpy as np
from pyzxing import BarCodeReader
import requests

st.title("📦 Barcode Scanner MVP (ZXing, no DLL issues)")

# --- Camera input ---
uploaded_file = st.camera_input("Scan Barcode")
barcode_val = None

if uploaded_file is not None:
    # Convert to OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # Save temp image
    temp_path = "temp_scan.jpg"
    cv2.imwrite(temp_path, img)

    # Decode barcode using ZXing
    reader = BarCodeReader()
    result = reader.decode(temp_path)
    if result:
        barcode_val = result[0].raw
        st.success(f"✅ Detected barcode: {barcode_val}")
    else:
        st.error("❌ Could not detect barcode. Try again.")

# --- Send barcode to FastAPI ---
if barcode_val:
    backend_url = f"http://127.0.0.1:8000/scan/{barcode_val}"
    r = requests.get(backend_url)
    if r.status_code == 200:
        data = r.json()
        if "error" in data:
            st.warning(f"Product not found in OpenFoodFacts: {barcode_val}")
        else:
            product = data.get("product")
            source = data.get("source")
            st.subheader("Product Info")
            st.write(f"**Source:** {source}")
            st.write(f"**Barcode:** {product['barcode']}")
            st.write(f"**Name:** {product['name']}")
            st.write(f"**Brand:** {product['brand']}")
            st.write(f"**Quantity:** {product['quantity']}")
            st.write(f"**Categories:** {product['categories']}")
    else:
        st.error("❌ Failed to connect to FastAPI backend")
