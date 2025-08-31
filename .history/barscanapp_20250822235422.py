from fastapi import FastAPI
import requests
import from fastapi import FastAPI
import sqlite3
import requests

app = FastAPI()

# --- DB Setup ---
conn = sqlite3.connect("products.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    barcode TEXT PRIMARY KEY,
    name TEXT,
    brand TEXT,
    quantity TEXT,
    categories TEXT
)
""")
conn.commit()

# --- Fetch product from OpenFoodFacts ---
def fetch_product(barcode: str):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get("status") == 0:
        return None
    product = data["product"]
    return {
        "barcode": barcode,
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", "Unknown"),
        "quantity": product.get("quantity", "Unknown"),
        "categories": product.get("categories", "Unknown")
    }

# --- API Endpoint ---
@app.get("/scan/{barcode}")
def scan_barcode(barcode: str):
    # Check DB first
    cursor.execute("SELECT * FROM products WHERE barcode=?", (barcode,))
    row = cursor.fetchone()
    if row:
        return {"source": "local_db", "product": row}

    # Fetch from OpenFoodFacts
    product = fetch_product(barcode)
    if not product:
        return {"error": "Product not found"}

    cursor.execute("""
        INSERT OR REPLACE INTO products (barcode, name, brand, quantity, categories)
        VALUES (?, ?, ?, ?, ?)
    """, (product["barcode"], product["name"], product["brand"], product["quantity"], product["categories"]))
    conn.commit()
    return {"source": "openfoodfacts", "product": product}

@app.get("/all")
def get_all():
    cursor.execute("SELECT * FROM products")
    return {"products": cursor.fetchall()}


app = FastAPI()

# --- DB Setup ---
conn = sqlite3.connect("products.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    barcode TEXT PRIMARY KEY,
    name TEXT,
    brand TEXT,
    quantity TEXT,
    categories TEXT
)
""")
conn.commit()


# --- Function to fetch product details ---
def fetch_product_from_openfoodfacts(barcode: str):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)

    if response.status_code != 200:
        return None
    
    data = response.json()
    if data.get("status") == 0:  # Product not found
        return None

    product = data["product"]
    return {
        "barcode": barcode,
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", "Unknown"),
        "quantity": product.get("quantity", "Unknown"),
        "categories": product.get("categories", "Unknown")
    }


# --- API Endpoints ---
@app.get("/scan/{barcode}")
def scan_barcode(barcode: str):
    # 1. Check if product is already in DB
    cursor.execute("SELECT * FROM products WHERE barcode=?", (barcode,))
    row = cursor.fetchone()
    if row:
        return {"source": "local_db", "product": row}

    # 2. If not, fetch from OpenFoodFacts
    product = fetch_product_from_openfoodfacts(barcode)
    if not product:
        return {"error": "Product not found"}

    # 3. Save to DB
    cursor.execute("""
        INSERT OR REPLACE INTO products (barcode, name, brand, quantity, categories)
        VALUES (?, ?, ?, ?, ?)
    """, (product["barcode"], product["name"], product["brand"], product["quantity"], product["categories"]))
    conn.commit()

    return {"source": "openfoodfacts", "product": product}


@app.get("/all")
def get_all_products():
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    return {"products": rows}
