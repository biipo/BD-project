import sqlalchemy as sq
from datetime import datetime
from sqlalchemy import ForeignKey, except_all, null
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped, backref
from typing import List
from sqlalchemy import Integer

engine = sq.create_engine('sqlite:///./data.db', echo=True)
class Base(DeclarativeBase):
    pass

# Le relationship() vengono definite nelle tabelle in cui "arriva" una foreign key (nel senso: se tab 1
# ha la sua chiave, e poi c'è tab 2 che ha una FK che indica tab 1; in tab 1 dobbiamo mettere una relationship()

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column(nullable=True)
    user_type: Mapped[bool] = mapped_column()

    # def __init__(self, id, email, username, password, name, last_name, user_type):
    #     self.id = id
    #     self.email = email
    #     self.username = username
    #     self.password = password
    #     self.name = name
    #     self.last_name = last_name
    #     self.user_type = user_type

    # Da addresses
    # addresses_fk: Mapped['Addresses'] = relationship(back_populates='user_fk', cascade='all, delete, save-update')

    # # Da ordini
    # order_fk: Mapped['Orders'] = relationship(back_populates='user_fk', cascade='all, delete, save-update')

    # # Da recensioni
    # review_fk: Mapped['Reviews'] = relationship(back_populates='user_fk', cascade='all, delete, save-update')

    # # Da carrello
    # cart_fk: Mapped['Cart'] = relationship(back_populates='user_fk', cascade='all, delete, save-update')

    # A Products (come venditore)
    # product_fk = relationship(Product, back_populates='user_fk', order_by=Product.id)
    # products_in_sales = relationship('Products', backref='vendor', lazy=True)


    def __repr__(self):
        return f"Id:{self.id}, Email:{self.email}, Username:{self.username}, Password:{self.password}, Nome:{self.name}, Cognome:{self.last_name}, Tipo utente:{self.user_type}"




class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    brand: Mapped[str] = mapped_column(nullable=True)
    product_name: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(nullable=True)
    # category_id: Mapped[int] = mapped_column(ForeignKey('Categories.id'))
    price: Mapped[float] = mapped_column(nullable=False)
    availability: Mapped[int] = mapped_column(nullable=False)
    descr: Mapped[str] = mapped_column(nullable=True)

    # def __init__(self, id, user_id, brand, product_name, date, price, availability, descr):
    #     self.id = id
    #     self.user_id = user_id
    #     self.brand = brand
    #     self.product_name = product_name
    #     self.date = date
    #     self.price = price
    #     self.availability = availability
    #     self.descr = descr

    # Serve per collegare la foreign key alla tabella CartProducts (secondary) che a sua volta collega a Cart, back_populates è la variabile in Cart
    # Preso da seconda risposta: https://stackoverflow.com/questions/5756559/how-to-build-many-to-many-relations-using-sqlalchemy-a-good-example
    # cart_fk: Mapped['Cart'] = relationship(secondary='CartProducts', back_populates='product_fk', cascade='all, delete, save-update')

    # # Collega ad Orders con la tabella tramite OrderProducts, back_populates è la variabile in Orders
    # order_fk: Mapped['Orders'] = relationship(secondary='OrderProducts', back_populates='product_fk', cascade='all, delete, save-update')

    # # Collega a Tags con la tabella intermedia TagProducts, back_populates è la variabile in Tags
    # tag_fk: Mapped['Tags'] = relationship(secondary='TagProducts', back_populates='product_fk', cascade='all, delete, save-update')

    # # Collega Reviews con una relazione uno(Product)-molti(Review)
    # review_fk: Mapped['Reviews'] = relationship(back_populates='product_fk', cascade='all, delete, save-update')

    # Collega a Users (venditore)
    user_fk: Mapped[User] = relationship(User, back_populates='product_fk') # , cascade='all, delete, save-update'

    # Collega a Categories
    # category_fk: Mapped['Categories'] = relationship(back_populates='product_fk', cascade='all, delete, save-update')

    # Riaggiungere la category
    def __repr__(self):
        return f"Id:{self.id}, Venditore:{self.user_id}, Prodotto:{self.product_name}, Brand:{self.brand}, Messo in vendita: {self.date}, Prezzo:{self.price}€, Quantità in magazzino:{self.availability}, Descrizione:{self.descr}"

User.product_fk = relationship(Product, back_populates='user_fk', order_by=Product.id)

class Addresses(Base):
    __tablename__ = 'Addresses'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id', ondelete='CASCADE'))
    active: Mapped[bool]
    state: Mapped[str]
    province: Mapped[str]

#     user_fk: Mapped['Users'] = relationship(back_populates='addresses_fk')  # Serve per collegare la ForeignKey

    def __repr__(self):
        return f"{self.id} {self.user_id} {self.active} {self.state} {self:province}"


class Cart(Base):
    __tablename__ = 'Cart'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'))

#     # Collega la foreign key (alla tabella CartProducts), secondary (in teoria) è perché è una relazione molti-molti
#     # e quindi c'è una tabella intermedia, appunto CartProducts, prima di raggiungere Products
#     product_fk: Mapped['Products'] = relationship(secondary='CartProducts', back_populates='cart_fk', cascade='all, delete, save-update')

#     # A Users
#     user_fk: Mapped['Users'] = relationship(back_populates='cart_fk', cascade='all, delete, save-update')


    def __repr__(self):
        return f"{self.id} {self.user_id}"


# # https://stackoverflow.com/questions/5756559/how-to-build-many-to-many-relations-using-sqlalchemy-a-good-example

class CartProducts(Base):
    __tablename__ = 'CartProducts'

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey('Cart.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('Products.id'))
    quantity: Mapped[int]

    def __repr__(self):
        return f"{self.cart_id} {self.product_id} {self.quantity}"

class Orders(Base):
    __tablename__ = 'Orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'))
    date: Mapped[datetime]
    price: Mapped[float]
    address: Mapped[int]
    payment_method: Mapped[str]
    status: Mapped[str]

#     # La relazione collega la foreign key a Products passando per la tabella intermedia OrderProducts (in secondary), back_populates prende la variabile in Products
#     product_fk: Mapped['Products'] = relationship(secondary='OrderProducts', back_populates='order_fk', cascade='all, delete, save-update')

#     # Collega a user (uno(user)-molti(order))
#     user_fk: Mapped['Users'] = relationship(back_populates='order_fk', cascade='all, delete, save-update')

    def __repr__(self):
        return f"{self.id} {self.user_id} {self.date} {self.price} {self.address} {self.payment_method} {self.status}"


class OrderProducts(Base):
    __tablename__ = 'OrderProducts' # Tabella molti-molti tra Products e Orders

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('Orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('Products.id'))
    quantity: Mapped[int]

    def __repr__(self):
        return f"{self.order_id} {self.product_id} {self.quantity}"


class Categories(Base):
    __tablename__ = 'Categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

#     # Collegata a Products con relazione uno(Categories)-molti(Products)
#     product_fk: Mapped['Products'] = relationship(back_populates='category_fk', cascade='all, delete, save-update')

    def __repr__(self):
        return f"{self.id} {self.name}"


class Tags(Base):
    __tablename__ = 'Tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(nullable=False) # con vincolo di NOT NULL

#     product_fk: Mapped['Products'] = relationship(secondary='TagProducts', back_populates='tag_fk', cascade='all, delete, save-update')

    def __repr__(self):
        return f"{self.id} {self.name}"


class TagProducts(Base):
    __tablename__ = 'TagProducts'

    id: Mapped[int] = mapped_column(primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey('Tags.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('Products.id'))


class Reviews(Base):
    __tablename__ = 'Reviews'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(Products.id))
    user_id: Mapped[int] = mapped_column(ForeignKey(Users.id))
    review: Mapped[str]

#     # Da Users
#     user_fk: Mapped['Users'] = relationship(back_populates='review_fk', cascade='all, delete, save-update' )

#     # Da Products
#     product_fk: Mapped['Products'] = relationship(back_populates='review_fk', cascade='all, delete, save-update' )

    def __repr__(self):
        return f"{self.id} {self.product_id} {self.user_id} {self.review}"

