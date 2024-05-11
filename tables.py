import sqlalchemy as sq
from datetime import datetime
from sqlalchemy import Column, Table, ForeignKey, except_all, null
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped, backref
from sqlalchemy import Integer
from flask_login import UserMixin

engine = sq.create_engine('sqlite:///./data.db', echo=True)

user_counter: int = 0 # usato per gli ID
product_counter: int = 0 # usato per gli ID

class Base(DeclarativeBase):
    pass

# Le relationship() vengono definite nelle tabelle in cui "arriva" una foreign key (nel senso: se tab 1
# ha la sua chiave, e poi c'è tab 2 che ha una FK che indica tab 1; in tab 1 dobbiamo mettere una relationship()

class User(Base, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column(nullable=True)
    user_type: Mapped[bool] = mapped_column()

    def __init__(self, id, email, username, password, name, last_name, user_type):
        self.id = id
        self.email = email
        self.username = username
        self.password = password
        self.name = name
        self.last_name = last_name
        self.user_type = user_type

    # def is_authenticated(self):
    #     return 0

    # def is_active(self):
    #     return super().is_active

    # def is_anonymous(self):
    #     return 0

    # def get_id(self):
    #     return str(self.id)

    def __repr__(self):
        return f"Id:{self.id}, Email:{self.email}, Username:{self.username}, Password:{self.password}, Nome:{self.name}, Cognome:{self.last_name}, Tipo utente:{self.user_type}"

class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"{self.id} {self.name}"

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    brand: Mapped[str] = mapped_column(nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey(Category.id))
    product_name: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)
    availability: Mapped[int] = mapped_column(nullable=False)
    descr: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self):
        return f"Id:{self.id}, Venditore:{self.user_id}, Prodotto:{self.product_name}, Brand:{self.brand}, Messo in vendita: {self.date}, Prezzo:{self.price}€, Quantità in magazzino:{self.availability}, Descrizione:{self.descr}"


class Address(Base):
    __tablename__ = 'addresses'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete='CASCADE'))
    active: Mapped[bool]
    state: Mapped[str]
    province: Mapped[str]


    def __repr__(self):
        return f"{self.id} {self.user_id} {self.active} {self.state} {self:province}"


class Cart(Base):
    __tablename__ = 'carts'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    def __repr__(self):
        return f"{self.id} {self.user_id}"


# Tabella intermedia m:m
cart_product = Table(
    'cart_products',
    Base.metadata,
    Column('cart_id', ForeignKey(Cart.id), primary_key=True),
    Column('product_id', ForeignKey(Product.id), primary_key=True),
    Column('quantity', Integer, nullable=False),
        )

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    date: Mapped[datetime]
    price: Mapped[float]
    address: Mapped[int]
    payment_method: Mapped[str]
    status: Mapped[str]

    def __repr__(self):
        return f"{self.id} {self.user_id} {self.date} {self.price} {self.address} {self.payment_method} {self.status}"


# Tabella intermedia m:m
order_product = Table(
    'order_products',
    Base.metadata,
    Column('order_id', ForeignKey(Order.id), primary_key=True),
    Column('product_id', ForeignKey(Product.id), primary_key=True),
    Column('quantity', Integer, nullable=False),
        )




class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(nullable=False)


    def __repr__(self):
        return f"{self.id} {self.name}"

# Tabella intermedia m:m
tag_product = Table(
    'tag_products',
    Base.metadata,
    Column('tag_id', ForeignKey(Tag.id), primary_key=True),
    Column('product_id', ForeignKey(Product.id), primary_key=True),
        )


class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    review: Mapped[str]

    def __repr__(self):
        return f"{self.id} {self.product_id} {self.user_id} {self.review}"

# ---------------------------------------------------------------------------------------------------------------------------
# Relationship per le foreign key

# Relazine tra venditore e prodotti in vendita
Product.user_fk = relationship(User, back_populates='product_fk') # , cascade='all, delete, save-update'
User.product_fk = relationship(Product, back_populates='user_fk', order_by=Product.id)

# Relazione tra indirizzi e utenti
Address.user_fk = relationship(User, back_populates='addresses_fk')  # Serve per collegare la ForeignKey
User.addresses_fk = relationship(Address, back_populates='user_fk', cascade='all, delete, save-update')

# Relazione tra utenti e i loro rispettivi carrelli
Cart.user_fk = relationship(User, back_populates='cart_fk', cascade='all, delete, save-update')
User.cart_fk = relationship(Cart, back_populates='user_fk', cascade='all, delete, save-update')

# Relazione tra carrello e prodotti
Cart.product_fk = relationship(Product, secondary=cart_product, back_populates='cart_fk', cascade='all, delete, save-update')
Product.cart_fk = relationship(Cart, secondary=cart_product, back_populates='product_fk', cascade='all, delete, save-update')

# Relazione tra utente e i suoi ordini
Order.user_fk = relationship(User, back_populates='order_fk', cascade='all, delete, save-update')
User.order_fk = relationship(Order, back_populates='user_fk', cascade='all, delete, save-update')

# Relazione tra ordini e prodotti nell'ordine
Order.product_fk = relationship(Product, secondary=order_product, back_populates='order_fk', cascade='all, delete, save-update')
Product.order_fk = relationship(Order, secondary=order_product, back_populates='product_fk', cascade='all, delete, save-update')

# Relazione tra prodotti e categorie a cui appartengono
Category.product_fk = relationship(Product, back_populates='category_fk', cascade='all, delete, save-update')
Product.category_fk = relationship(Category, back_populates='product_fk', cascade='all, delete, save-update')

# Relazione tra tag e prodotti con intermedia tag_product
Tag.product_fk = relationship(Product, secondary=tag_product, back_populates='tag_fk', cascade='all, delete, save-update')
Product.tag_fk = relationship(Tag, secondary=tag_product, back_populates='product_fk', cascade='all, delete, save-update')

# Relazione tra prodotti e recensioni
Product.review_fk = relationship(Review, back_populates='product_fk', cascade='all, delete, save-update')
Review.product_fk = relationship(Product, back_populates='review_fk', cascade='all, delete, save-update' )

# Relazione tra recensioni e utenti
Review.user_fk = relationship(User, back_populates='review_fk', cascade='all, delete, save-update' )
User.review_fk = relationship(Review, back_populates='user_fk', cascade='all, delete, save-update')
