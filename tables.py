from sqlalchemy import *
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///data.db', echo=True)

Base = declarative_base()

class Users(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    username = Column(String)
    passsword = Column(String)
    name = Column(String)
    last_name = Column(String)
    user_type = Column(String)

    def __repr__(self):
        return "{self.id} {self.email} {self.username} {self.passsword} {self.name} {self.last_name} {self.user_type}"

class Addresses(Base):
    __tablename__ = 'Addresses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(Users.id))
    active = Column(Boolean)
    state = Column(String)
    province = Column(String)

    def __repr__(self):
        return "{self.id} {self.user_id} {self.active} {self.state} {self:province}"

class Cart(Base):
    __tablename__ = 'Cart'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(Users.id))

    def __repr__(self):
        return f"{self.id} {self.user_id}"

class CartProducts(Base):
    __tablename__ = 'CartProducts'

    cart_id = Column(Integer, primary_key=True, ForeignKey(Cart.id))
    product_id = Column(Integer, ForeignKey(Products.id))
    quantity = Column(Integer)

    def __repr__(self):
        return f"{self.cart_id} {self.product_id} {self.quantity}"

class Products(Base):
    __tablename__ = 'Products'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(Users.id)) # venditore
    brand = Column(String)
    product_name = Column(String)
    date = Column(Date) # Non sicuro del tipo
    category_id = Column(Integer, ForeignKey(Categories.id))
    price = Column(Float)
    availability = Column(Integer)
    descr = Column(String)

    def __repr__(self):
        return f"{self.id} {self.product_name} {self.brand} {self.date} {self.category_id} {self.price} {self.availability} {self.descr}"

class Orders(Base):
    __tablename__ = 'Orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(Users.id))
    date = Column(Date)
    price = Column(Float)
    address = Column(Integer) # è una Foreign Key alla tabella Addresses
    payment_method = Column(String)
    status = Column(String)

    def __repr__(self):
        return f"{self.id} {self.user_id} {self.date} {self.price} {self.address} {payment_method} {self.status}"

class OrderProducts(Base):
    __tablename__ = 'OrderProducts'

    order_id = Column(Integer, ForeignKey(Orders.id))
    product_id = Column(Integer, ForeignKey(Products.id))
    quantity = Column(Integer)

    def __repr__(self):
        return f"{self.order_id} {self.product_id} {self.quantity}"

class Categories(Base):
    __tablename__ = 'Categories'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return f"{self.id} {self.name}"

class Tags(Base):
    __tablename__ = 'Tags'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return f"{self.id} {self.name}"

class TagProducts(Base):
    __tablename__ = 'TagProducts'

    tag_id = Column(Integer, primary_key=True, ForeignKey(Tags.id))

class Reviews(Base):
    __tablename__ = 'Reviews'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey(Products.id))
    user_id = Column(Integer, ForeignKey(Users.id))
    review = Column(String)

    def __repr__(self):
        return f"{self.id} {self.product_id} {self.user_id} {self.review}"

def data_insertion():
    Session = sessionmaker(engine)
    with Session as session:
        session.add_all([Products(),
                         Products(),
                         Products(),
                         Products() ])   

        session.add_all([Categories(),
                         Categories(),
                         Categories(),
                         Categories() ])   

        session.commit()

