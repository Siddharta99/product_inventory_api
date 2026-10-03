from sqlmodel import SQLModel, Field, create_engine, Session, select

class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    price: int

engine = create_engine("sqlite:///products.db")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    mouse = Product(name="Mouse", price=500)
    session.add(mouse)
    session.commit()

with Session(engine) as session:
    products = session.exec(select(Product)).all()
    for p in products:
        print(p.id, p.name, p.price)