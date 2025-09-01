import streamlit as st
import cv2
import numpy as np
import requests

st.title("📷 Grocery Barcode Scanner (Cloud-Friendly)")

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
                if res.get("status") == 1:
                    product = res["product"]

                    st.subheader(product.get("product_name", "Unknown Product"))
                    st.write(f"**Brand:** {product.get('brands', 'Unknown')}")
                    st.write(f"**Quantity:** {product.get('quantity', 'Unknown')}")

                    nutriments = product.get("nutriments", {})
                    if nutriments:
                        st.subheader("Nutrition Info (per 100g)")
                        st.write(f"Calories: {nutriments.get('energy-kcal_100g', 'N/A')} kcal")
                        st.write(f"Protein: {nutriments.get('proteins_100g', 'N/A')} g")
                        st.write(f"Fat: {nutriments.get('fat_100g', 'N/A')} g")
                        st.write(f"Carbs: {nutriments.get('carbohydrates_100g', 'N/A')} g")

                    st.subheader("Ingredients")
                    st.write(product.get("ingredients_text", "No ingredient info"))

                    if product.get("nutriscore_grade"):
                        st.info(f"Nutri-Score: {product['nutriscore_grade'].upper()}")

                else:
                    st.warning("Product not found in OpenFoodFacts")
            else:
                st.warning("No barcode found in image.")
        else:
            st.error("Error contacting ZXing API or barcode could not be detected.")
