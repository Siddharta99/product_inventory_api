from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select

# 1. THE BLUEPRINT (The ORM Model)
class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    price: int

# 2. THE DATABASE CONNECTION
engine = create_engine("sqlite:///products.db")
SQLModel.metadata.create_all(engine) # Creates the table if it doesn't exist

# 3. THE API ROUTES
app = FastAPI()

@app.get("/")
def home():
    return {"message": "The API is alive"}

@app.get("/products")
def list_products():
    with Session(engine) as session:
        # Look how clean this is!
        products = session.exec(select(Product)).all()
        return products

@app.post("/products")
def add_product(product: Product):
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product) # Gets the new ID from the database
        return {"message": "Product added!", "id": product.id}

@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product):
    with Session(engine) as session:
        db_product = session.get(Product, product_id) # Finds by ID automatically!
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update the attributes directly
        db_product.name = product.name
        db_product.price = product.price
        
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
        return {"message": "Product updated!", "id": db_product.id}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    with Session(engine) as session:
        db_product = session.get(Product, product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
            
        session.delete(db_product)
        session.commit()
        return {"message": "Product Deleted!", "id": product_id}