import sqlalchemy as sq
from datetime import datetime
from sqlalchemy import CheckConstraint, Column, Table, ForeignKey, except_all, null
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped, backref
from sqlalchemy import Integer
from flask_login import UserMixin
from exceptions import InvalidCredential, MissingData, InvalidOrder
from typing import List
import re # regular expressions

engine = sq.create_engine('sqlite:///./data.db', echo=True)



class Base(DeclarativeBase):
    pass

"""
Le relationship() vengono definite nelle tabelle in cui "arriva" una foreign key (nel senso: se tab 1
ha la sua chiave, e poi c'è tab 2 che ha una FK che indica tab 1; in tab 1 dobbiamo mettere una relationship()
"""
class User(Base, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column(nullable=True)
    user_type: Mapped[bool] = mapped_column() # True se venditore
    
    addresses: Mapped[List['Address']] = relationship(back_populates='user')
    cart_products: Mapped[List['CartProducts']] = relationship(back_populates='user')
    reviews: Mapped[List['Review']] = relationship(back_populates='user')

    @staticmethod
    def __email_checker(email: str):
        pat_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.match(pat_email, email): # Controlla che l'email segua il pattern "xxx@xxx.xxx"
            raise InvalidCredential("Invalid email")
        return email

    @staticmethod
    def __username_checker(username: str):
        if len(username) < 1 or len(username) > 16:
            raise InvalidCredential("Invalid username")
        return username

    @staticmethod
    def __password_checker(password: str):
        lower, upper, digit, special = 0, 0, 0, 0
        if(len(password) >= 8):
            for c in str(password):
                if c.islower():
                    lower += 1
                if c.isupper():
                    upper += 1
                if c.isdigit():
                    digit += 1
                if c in ["~","`", "!", "@","#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "+", "=", "{", "}", "[", "]", "|", "\\", ";", ":", "<", ">", ",", ".", "/", "?"]:
                    special += 1
            if (lower < 1 or upper < 1 or digit < 1 or special < 1):
                raise InvalidCredential("Invalid password")
        else:
            raise InvalidCredential("Invalid password")
        # Salvataggio del hash della password
        from app import bcrypt
        return bcrypt.generate_password_hash(password) # Salviamo l'hash della password sul database

    @staticmethod
    def __name_lastname_checker(name: str, lastname: str): # Controlla che non ci siano numeri o simboli in nome e cognome
        pat_name = r'\b[0-9._%+-]\b'
        if re.match(pat_name, name):
            raise InvalidCredential("Invalid name")
        if re.match(pat_name, lastname):
            raise InvalidCredential("Invalid last name")
        return name, lastname

    def __init__(self, email, username, password, name, last_name, user_type):
        self.email = self.__email_checker(email)
        self.username = self.__username_checker(username)
        self.password = self.__password_checker(password)
        self.name, self.last_name = self.__name_lastname_checker(name, last_name)
        self.user_type = user_type
    
    def is_seller(self):
        return  self.user_type


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

    # sub_categories_list: Mapped[List['SubCategory']] = relationship(back_populates='category')

    def __init__(self, name):
        self.name = name

# class SubCategory(Base):
#     __tablename__ = 'sub_categories'

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     category_id: Mapped[int] = mapped_column(ForeignKey(Category.id), nullable=False)
#     name: Mapped[str] = mapped_column(nullable=False)

#     category: Mapped['Category'] = relationship(back_populates='sub_categories_list')

#     def __init__(self, category, name):
#         self.category = category
#         self.category_id = category.id
#         self.name = name


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    brand: Mapped[str] = mapped_column(nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey(Category.id))
    product_name: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)
    availability: Mapped[int] = mapped_column(nullable=False)
    descr: Mapped[str] = mapped_column(nullable=True)
    rating: Mapped[int]
    image_filename: Mapped[str] = mapped_column(nullable=False)

    cart_product: Mapped[List['CartProducts']] = relationship(back_populates='product')
    orders: Mapped[List['OrderProducts']] = relationship(back_populates='product')
    seller: Mapped['User'] = relationship('User')
    tags: Mapped[List['TagProduct']] = relationship(back_populates='product')
    reviews: Mapped[List['Review']] = relationship(back_populates='product')

    def __init__(self, user_id, brand, category_id, product_name, date, price, availability, descr, image_filename):
        if user_id is None:
            raise MissingData('Missing user id')
        self.user_id = user_id
        self.brand = brand
        if category_id is None:
            raise MissingData('Missing category id')
        self.category_id = category_id
        self.product_name = product_name
        self.date = date
        if price is None:
            raise MissingData('Missing price')
        self.price = price
        if availability is None:
            raise MissingData('Missing quantity')
        self.availability = availability
        self.descr = descr
        self.rating = 0
        if image_filename is None:
            raise MissingData('Missing image')
        self.image_filename = image_filename

    def __repr__(self):
        return f"name: {self.product_name}"


class Address(Base):
    __tablename__ = 'addresses'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete='CASCADE'))
    active: Mapped[bool]
    first_name: Mapped[str]
    last_name: Mapped[str]
    street: Mapped[str]
    postcode: Mapped[str]
    #city: Mapped[str]
    state: Mapped[str] 
    province: Mapped[str] 
    
    user = relationship('User')

    def __init__(self, user_id, active, first_name, last_name, street, postcode, state, province):
        if user_id is None:
            raise MissingData('Missing user_id')
        if None in (first_name, last_name, street, postcode, state, province):
            raise MissingData('Missing not null attribute')
        self.user_id = user_id
        self.active = active
        self.active = active
        self.first_name = first_name
        self.last_name = last_name
        self.street = street
        self.postcode = postcode
        self.state = state
        self.province = province

    def __repr__(self):
        return f"{self.id} {self.user_id} {self.active} {self.first_name} {self.last_name} {self.street} {self.postcode} {self.state} {self.province}"

class CartProducts(Base):
    __tablename__ = 'cart_product'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), primary_key=True)
    quantity: Mapped[int]

    product: Mapped['Product'] = relationship(back_populates='cart_product')
    user: Mapped['User'] = relationship(back_populates='cart_products')

    def __init__(self, product, quantity, user):
        self.product = product
        self.product_id = product.id
        self.user = user
        self.user_id = user.id
        self.quantity = quantity

class OrderProducts(Base):
    __tablename__ = 'order_product'
    
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), primary_key=True)
    quantity: Mapped[int]
    
    product: Mapped['Product'] = relationship(back_populates='orders')
    order: Mapped['Order'] = relationship(back_populates='products')

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    date: Mapped[datetime]
    price: Mapped[float]
    address: Mapped[int] = mapped_column(ForeignKey(Address.id))
    payment_method: Mapped[str]
    status: Mapped[str]
    status_time: Mapped[datetime]
    confirmed: Mapped[bool]

    # Rename address_obj to address and address to address_id later
    address_obj = relationship('Address')
    products: Mapped[List['OrderProducts']] = relationship(back_populates='order')

    # def set_status(status: str):
    #     if status in ['Paid', 'Confirmed', 'Sent', 'In transit', 'Arrived']: # Esempi di possibili stati
    #         self.status = status
    #     else:
    #         raise InvalidCredential('Invalid status')

    def __repr__(self):
        return f"{self.id} {self.user_id} {self.date} {self.price} {self.address} {self.payment_method} {self.status} {self.status_time} {self.confirmed}"

# class TagGroup(Base):
#     # Tabella con relazione (TagGroup)1:m(Tag), che serve per riconoscere di che categoria è il tag (dimensione, colore o brand)
#     __tablename__ = 'tag_group'

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(nullable=False, unique=True)

#     tag_list: Mapped[List['Tag']] = relationship(back_populates='tag_group')

#     def __init__(self, name):
#         self.name = name

class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(nullable=False, unique=True)

    # tag_group_id: Mapped[int] = mapped_column(ForeignKey(TagGroup.id))
    # tag_group: Mapped['TagGroup'] = relationship(back_populates='tag_list')

    products: Mapped[List['TagProduct']] = relationship(back_populates='tag')

    def __init__(self, value):
        if value is None:
            raise MissingData('Missing tag value')
        self.value = value

# Tabella intermedia m:m
class TagProduct(Base):
    __tablename__ = 'tag_products'

    tag_id: Mapped[int] = mapped_column(ForeignKey(Tag.id), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id), primary_key=True)

    tag: Mapped['Tag'] = relationship(back_populates='products')
    product: Mapped['Product'] = relationship(back_populates='tags')

    def __init__(self, tag, product):
        self.tag = tag
        self.product = product
        self.tag_id = tag.id
        self.product_id = product.id

class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    review: Mapped[str]
    stars: Mapped[int] = mapped_column(CheckConstraint('stars >= 1 AND stars <= 5'))
    date: Mapped[datetime] 

    user = relationship('User')
    product = relationship('Product')

    def __repr__(self):
        return f"££{self.id} {self.product.product_name} {self.user.username} {self.review}££"

