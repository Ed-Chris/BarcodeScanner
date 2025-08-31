import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import requests
import numpy as np

st.title("📷 Grocery Barcode Scanner Prototype")

# Camera input
img_file = st.camera_input("Take a picture of the barcode")

if img_file:
    file_bytes = np.asarray(bytearray(img_file.getvalue()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, 1)

    barcodes = decode(frame)
    if not barcodes:
        st.warning("No barcode detected. Try adjusting focus/lighting.")
    else:
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            st.write(f"✅ Detected: {barcode_data} ({barcode_type})")

            # Call OpenFoodFacts API
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_data}.json"
            res = requests.get(url).json()

            if res.get("status") == 1:
                product = res.get("product", {})

                # Get product name (fallbacks)
                name = (
                    product.get("product_name") or
                    product.get("product_name_en") or
                    product.get("product_name_fr") or
                    "Unknown"
                )

                # Get brand (fallbacks)
                brand = (
                    product.get("brands") or
                    product.get("brands_tags", ["Unknown"])[0]
                )

                # Get product image
                image_url = product.get("image_small_url") or product.get("image_url")

                st.success(f"**Product Name:** {name}")
                st.info(f"**Brand:** {brand}")

                if image_url:
                    st.image(image_url, caption=name, use_column_width=True)
                else:
                    st.warning("No product image available")
            else:
                st.warning("Product not found")
