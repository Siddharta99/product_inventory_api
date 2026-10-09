from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, Field, create_engine, Session, select
import hashlib, secrets
import jwt
from datetime import datetime, timedelta, timezone

# The secret holographic stamp
SECRET_KEY = "super-secret-wax-seal-12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# The scanner tool (Fixed spelling: oauth2_scheme, tokenUrl="login")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 1. THE BLUEPRINTS (Moved to the top so they exist early!)
class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    price: int

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str
    hashed_password: str

class UserRegister(SQLModel):
    username: str
    email: str
    password: str

class UserLogin(SQLModel):
    username: str
    password: str

# 2. THE DATABASE CONNECTION
engine = create_engine("sqlite:///products.db")

# 3. THE HELPER TOOLS
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def hash_password(password: str):
    salt = secrets.token_hex(16)
    grind = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return salt + ":" + grind.hex()

def verify_password(claimed: str, stored: str):
    salt, old_grind = stored.split(":")
    new_grind = hashlib.pbkdf2_hmac(
        "sha256", claimed.encode(), salt.encode(), 100_000
    ).hex()
    return new_grind == old_grind

# The Scanner (Fixed capital 'S' for Session)
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Fake wristband!")
    except Exception:
        raise HTTPException(status_code=401, detail="Fake or expired wristband!")

    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found!")
        return user

# 4. THE API ROUTES
app = FastAPI()

@app.get("/")
def home():
    return {"message": "The API is alive"}

@app.get("/products")
def list_products():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        return products

@app.post("/products")
def add_product(product: Product, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
        return {"message": "Product added!", "id": product.id}

@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product):
    with Session(engine) as session:
        db_product = session.get(Product, product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
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

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == form_data.username)).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="wrong username or password")
        access_token = create_access_token(data={"user_id": user.id})
        return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users")
def register_user(payload: UserRegister):
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.username == payload.username)).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Username already taken")
        fingerprint = hash_password(payload.password)
        new_user = User(
            username=payload.username,
            email=payload.email,
            hashed_password=fingerprint
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"message": "user registered!", "id": new_user.id}

SQLModel.metadata.create_all(engine)