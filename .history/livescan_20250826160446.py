import cv2
import streamlit as st
from pyzbar.pyzbar import decode
import requests

st.title("📷 Grocery Barcode Scanner Prototype")

# Open webcam
cap = cv2.VideoCapture(0)

FRAME_WINDOW = st.image([])

while True:
    ret, frame = cap.read()
    if not ret:
        st.error("Failed to access camera")
        break

    # Detect barcodes
    barcodes = decode(frame)
    for barcode in barcodes:
        x, y, w, h = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type

        # Display on screen
        cv2.putText(frame, f"{barcode_data} ({barcode_type})", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        st.write(f"✅ Detected: {barcode_data} ({barcode_type})")

        # Call OpenFoodFacts
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_data}.json"
        res = requests.get(url).json()
        if res.get("status") == 1:
            product = res["product"]
            st.success(f"Product: {product.get('product_name', 'Unknown')}")
        else:
            st.warning("Product not found")

    FRAME_WINDOW.image(frame, channels="BGR")
