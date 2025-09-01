import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import requests
import numpy as np

st.title("📷 Grocery Barcode Scanner Prototype")

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

            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_data}.json"
            res = requests.get(url).json()

            if res.get("status") == 1:
                product = res["product"]

                # Basic product info
                st.success(f"**Product:** {product.get('product_name', 'Unknown')}")
                st.write(f"**Brand:** {product.get('brands', 'Unknown')}")
                st.write(f"**Quantity:** {product.get('quantity', 'Unknown')}")

                # Nutrition info
                nutriments = product.get("nutriments", {})
                if nutriments:
                    st.subheader("Nutrition Info (per 100g)")
                    st.write(f"Calories: {nutriments.get('energy-kcal_100g', 'N/A')} kcal")
                    st.write(f"Protein: {nutriments.get('proteins_100g', 'N/A')} g")
                    st.write(f"Fat: {nutriments.get('fat_100g', 'N/A')} g")
                    st.write(f"Carbs: {nutriments.get('carbohydrates_100g', 'N/A')} g")

                # Ingredients
                st.subheader("Ingredients")
                st.write(product.get("ingredients_text", "No ingredient info"))

                # Nutriscore
                if product.get("nutriscore_grade"):
                    st.info(f"Nutri-Score: {product['nutriscore_grade'].upper()}")

            else:
                st.warning("Product not found")
