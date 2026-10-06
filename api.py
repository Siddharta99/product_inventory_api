from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
import hashlib,secrets

# 1. THE BLUEPRINT (The ORM Model)
class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    price: int

# 2. THE DATABASE CONNECTION
engine = create_engine("sqlite:///products.db")


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

class User(SQLModel,table=True):
    __tablename__ = "users"
    id:int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str
    hashed_password: str

class UserRegister(SQLModel):
    username:str
    email:str
    password: str

class UserLogin(SQLModel):
    username:str
    password:str

@app.post("/login")
def login(payload: UserLogin):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == payload.username)).first()
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=401,detail="wrong username or password")
        return {"message":"welcome back!","id":user.id}
def hash_password(password:str):
    salt = secrets.token_hex(16)
    grind = hashlib.pbkdf2_hmac("sha256",password.encode(),salt.encode(),100_000)
    return salt + ":" + grind.hex()

@app.post("/users")
def register_user(payload: UserRegister):
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.username == payload.username)).first()

        if existing_user:
            raise HTTPException(status_code=409,detail="Username already taken")

        fingerprint = hash_password(payload.password)

        new_user = User(
            username=payload.username,
            email=payload.email,
            hashed_password=fingerprint
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user) # Gets the new ID from the database
        return {"message": "user registered!", "id": new_user.id}

def verify_password(claimed:str,stored:str):
    salt, old_grind = stored.split(":")
    new_grind = hashlib.pbkdf2_hmac(
        "sha256",claimed.encode(),salt.encode(),100_000
    ).hex()
    return new_grind == old_grind
SQLModel.metadata.create_all(engine) # Creates the table if it doesn't exist