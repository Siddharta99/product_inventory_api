import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

conn = sqlite3.connect("products.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price INTEGER NOT NULL
    )
""")
conn.commit()
conn.close()

@app.get("/")
def home():
    return {"message": "The API is alive"}

@app.get("/products")
def list_products():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    products = []
    for row in rows:
        products.append({"id": row[0], "name": row[1], "price": row[2]})
    return products

class Product(BaseModel):
    name: str
    price: int

@app.post("/products")
def add_product(product: Product):
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (product.name, product.price))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"message": "Product added!", "id": new_id}

@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product):
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name = ?, price = ? WHERE id = ?",
                   (product.name, product.price, product_id))
    conn.commit()
    changes = cursor.rowcount
    conn.close()
    if changes == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated!", "id": product_id}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    conn=sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?",(product_id,))
    conn.commit()
    changes = cursor.rowcount
    conn.close()
    if changes == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product Deleted!","id": product_id}