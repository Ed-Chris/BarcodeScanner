import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import requests
import numpy as np

st.title("📷 Grocery Barcode Scanner Prototype")

# Camera input (takes snapshots instead of continuous loop)
img_file = st.camera_input("Take a picture of the barcode")

if img_file:
    # Convert the captured image to an array
    file_bytes = np.asarray(bytearray(img_file.getvalue()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, 1)

    # Detect barcodes
    barcodes = decode(frame)
    if not barcodes:
        st.warning("No barcode detected. Try adjusting focus/lighting.")
    else:
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            st.write(f"✅ Detected: {barcode_data} ({barcode_type})")

            # Call OpenFoodFacts
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_data}.json"
            res = requests.get(url).json()
            if res.get("status") == 1:
                product = res["product"]
                st.success(f"**Product:** {product.get('product_name', 'Unknown')}")
            else:
                st.warning("Product not found")
