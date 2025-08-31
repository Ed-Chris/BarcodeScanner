import streamlit as st
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests

st.title("📦 Barcode Scanner MVP")

# --- Step 1: Capture image from webcam ---
st.info("Use your phone camera or laptop webcam to scan the barcode")

barcode_val = None

uploaded_file = st.camera_input("Scan Barcode")
if uploaded_file is not None:
    # Convert uploaded image to OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # Decode barcode
    barcodes = decode(img)
    if barcodes:
        barcode_val = barcodes[0].data.decode("utf-8")
        st.success(f"✅ Detected barcode: {barcode_val}")
    else:
        st.error("❌ Could not detect barcode, try again.")

# --- Step 2: Send barcode to FastAPI ---
if barcode_val:
    backend_url = f"http://127.0.0.1:8000/scan/{barcode_val}"
    response = requests.get(backend_url)
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            st.warning(f"Product not found in OpenFoodFacts: {barcode_val}")
        else:
            st.subheader("Product Info")
            product = data.get("product")
            source = data.get("source")
            st.write(f"**Source:** {source}")
            st.write(f"**Barcode:** {product['barcode']}")
            st.write(f"**Name:** {product['name']}")
            st.write(f"**Brand:** {product['brand']}")
            st.write(f"**Quantity:** {product['quantity']}")
            st.write(f"**Categories:** {product['categories']}")
    else:
        st.error("❌ Failed to connect to FastAPI backend")
