import sqlalchemy as sq
from datetime import datetime
from sqlalchemy import CheckConstraint, Column, Table, ForeignKey, except_all, null
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped, backref, validates
from sqlalchemy import Integer, Numeric, Text, String
from decimal import Decimal
from flask_login import UserMixin
from exceptions import InvalidCredential, MissingData, InvalidOrder
from typing import List
import re # regular expressions

from config import Base, engine, db_session, app, login_manager, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, bcrypt

def not_none_checker(key, value): # 'key' identifica l'attributo 'value' che stiamo verificando non essere nullo 
    if value is None:
        raise MissingData('Missing ' + str(key))
    return value

class User(Base, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column(nullable=True)
    user_type: Mapped[bool] = mapped_column() # True se venditore
    last_logout: Mapped[datetime] = mapped_column()

    addresses: Mapped[List['Address']] = relationship(back_populates='user')
    cart_products: Mapped[List['CartProducts']] = relationship(back_populates='user')
    reviews: Mapped[List['Review']] = relationship(back_populates='user')

    @validates('email')
    def email_checker(self, key, email: str):
        pat_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.match(pat_email, email): # Controlla che l'email segua il pattern "xxx@xxx.xxx"
            raise InvalidCredential("Invalid email")
        return email

    @validates('username')
    def username_checker(self, key, username: str):
        if len(username) < 1 or len(username) > 16:
            raise InvalidCredential("Invalid username")
        return username

    @validates('password')
    def password_checker(self, key, password: str):
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
        return bcrypt.generate_password_hash(password) # Salviamo l'hash della password sul database

    @validates('name', 'last_name')
    def name_lastname_checker(self, key, value: str): # Controlla che non ci siano numeri o simboli in nome e cognome
        pat_name = r'[0-9._%+-]'
        if re.search(pat_name, value): # usando validates SQLAlchemy chiama questa funzione 2 volte per i 2 attributi e value assume un valore alla volta
            raise InvalidCredential('Invalid ' + str(key))
        return value

    def is_seller(self):
        return  self.user_type


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

    products: Mapped[List['Product']] = relationship(back_populates='category')

    @validates('name')
    def attribute_checker(self, key, value):
        return not_none_checker(key, value)

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    brand: Mapped[str] = mapped_column(nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey(Category.id))
    size: Mapped[str] = mapped_column(CheckConstraint('size = "small" OR size = "medium" OR size = "big"'), nullable=False)
    product_name: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(precision=8, scale=2), nullable=False) #8 cifre totali, 2 dopo virgola
    availability: Mapped[int] = mapped_column(nullable=False)
    descr: Mapped[str] = mapped_column(nullable=True)
    rating: Mapped[int] = mapped_column(default=0)
    image_filename: Mapped[str] = mapped_column(nullable=False)

    cart_product: Mapped[List['CartProducts']] = relationship(back_populates='product')
    orders: Mapped[List['OrderProducts']] = relationship(back_populates='product')
    seller: Mapped['User'] = relationship('User')
    tags: Mapped[List['TagProduct']] = relationship(back_populates='product')
    reviews: Mapped[List['Review']] = relationship(back_populates='product')
    category: Mapped['Category'] = relationship(back_populates='products')

    @validates('brand', 'product_name', 'descr', 'user_id', 'category', 'price', 'availability', 'image_filename')
    def attributes_checker(self, key, value):
        not_none_checker(key, value)
        if key  == 'brand' and len(value) > 20:
            raise ValueError('Brand name too long')
        elif key == 'product_name' and len(value) > 50:
            raise ValueError('Product name too long')
        elif key == 'descr' and len(value) > 50:
            raise ValueError('Description too long')
        return value


class Address(Base):
    __tablename__ = 'addresses'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete='CASCADE'))
    active: Mapped[bool]
    first_name: Mapped[str]
    last_name: Mapped[str]
    street: Mapped[str]
    postcode: Mapped[str]
    city: Mapped[str]
    state: Mapped[str] 
    province: Mapped[str] 
    
    user = relationship('User')

    @validates('user_id', 'first_name', 'last_name', 'street', 'postcode', 'state', 'province')
    def attribute_checker(self, key, value):
        not_none_checker(key, value)
        if key == 'postcode' and (not re.fullmatch(r'^\d+$', value) or len(value) != 5):
            raise ValueError('Postal code must contains only numbers (exactly 5 numbers)')
        return value

class CartProducts(Base):
    __tablename__ = 'cart_product'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), primary_key=True)
    quantity: Mapped[int]

    product: Mapped['Product'] = relationship(back_populates='cart_product')
    user: Mapped['User'] = relationship(back_populates='cart_products')

class OrderProducts(Base):
    __tablename__ = 'order_product'
    
    # Utilizziamo un id perché un utente nel tempo potrebbe fare più ordini dello stesso prodotto
    # e ponendo order_id e product_id come chiavi darebbe errore perché ripeteremmo la coppia delle 2 chiavi
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int]
    
    product: Mapped['Product'] = relationship(back_populates='orders')
    order: Mapped['Order'] = relationship(back_populates='products')

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    date: Mapped[datetime]
    price: Mapped[Decimal] = mapped_column(Numeric(precision=8, scale=2), nullable=False) #8 cifre totali, 2 dopo virgola
    address: Mapped[int] = mapped_column(ForeignKey(Address.id))
    payment_method: Mapped[str]
    status: Mapped[str]
    status_time: Mapped[datetime]
    confirmed: Mapped[bool]

    # Rename address_obj to address and address to address_id later
    address_obj = relationship('Address')
    products: Mapped[List['OrderProducts']] = relationship(back_populates='order')

    @validates('status')
    def status_checker(self, key, value):
        if value not in ['Paid', 'Received', 'Processing', 'Sent', 'Cancelled']:
            raise ValueError('Invalid status')
        return value

class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(nullable=False, unique=True)

    products: Mapped[List['TagProduct']] = relationship(back_populates='tag')

    @validates('value')
    def value_checker(self, key, value):
        return not_none_checker(key, value)

# Tabella intermedia m:m
class TagProduct(Base):
    __tablename__ = 'tag_products'

    tag_id: Mapped[int] = mapped_column(ForeignKey(Tag.id), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id), primary_key=True)

    tag: Mapped['Tag'] = relationship(back_populates='products')
    product: Mapped['Product'] = relationship(back_populates='tags')

class Review(Base):
    __tablename__ = 'reviews'
    
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), primary_key=True)
    review: Mapped[str] = mapped_column(nullable=False)
    stars: Mapped[int] = mapped_column(CheckConstraint('stars >= 1 AND stars <= 5'))
    date: Mapped[datetime] 

    user = relationship('User')
    product = relationship('Product')



