from re import U
import re
from sqlalchemy import ForeignKey, Boolean, create_engine, Date, Float, sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, mapped_column, Mapped

engine = create_engine('sqlite:///data.db', echo=True)

Base = declarative_base()

# Le relationship() vengono definite nelle tabelle in cui "arriva" una foreign key (nel senso: se tab 1
# ha la sua chiave, e poi c'è tab 2 che ha una FK che indica tab 1; in tab 1 dobbiamo mettere una relationship()

class Users(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str]
    passsword: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str]
    last_name: Mapped[str]
    user_type: Mapped[Boolean]

    # Da addresses
    addresses_fk: Mapped['Addresses'] = relationship(back_populates='user_fk', cascade='all, delete, delete-orphan, save-update')

    # Da ordini
    order_fk: Mapped['Orders'] = relationship(back_populates='user_fk', cascade='all, delete, delete-orphan, save-update')

    # Da recensioni
    review_fk: Mapped['Reviews'] = relationship(back_populates='user_fk', cascade='all, delete, delete-orphan, save-update')

    # Da carrello
    cart_fk: Mapped['Cart'] = relationship(back_populates='user_fk', cascade='all, delete, delete-orphan, save-update')

    # A Products (come venditore)
    product_fk: Mapped['Products'] = relationship(back_populates='user_fk', cascade='all, delete, delete-orphan, save-update')


    def __repr__(self):
        return "{self.id} {self.email} {self.username} {self.passsword} {self.name} {self.last_name} {self.user_type}"


class Addresses(Base):
    __tablename__ = 'Addresses'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id', ondelete='CASCADE'))
    active: Mapped[Boolean]
    state: Mapped[str]
    province: Mapped[str]

    user_fk: Mapped['Users'] = relationship(back_populates='addresses_fk')  # Serve per collegare la ForeignKey

    def __repr__(self):
        return "{self.id} {self.user_id} {self.active} {self.state} {self:province}"


class Cart(Base):
    __tablename__ = 'Cart'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'))

    # Collega la foreign key (alla tabella CartProducts), secondary (in teoria) è perché è una relazione molti-molti
    # e quindi c'è una tabella intermedia, appunto CartProducts, prima di raggiungere Products
    product_fk: Mapped['Products'] = relationship(secondary='CartProducts', back_populates='cart_fk', cascade='all, delete, delete-orphan, save-update')

    # A Users
    user_fk: Mapped['Users'] = relationship(back_populates='cart_fk', cascade='all, delete, delete-orphan, save-update')


    def __repr__(self):
        return f"{self.id} {self.user_id}"


# https://stackoverflow.com/questions/5756559/how-to-build-many-to-many-relations-using-sqlalchemy-a-good-example

class CartProducts(Base):
    __tablename__ = 'CartProducts'

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey('Cart.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('Products.id'))
    quantity: Mapped[int]

    def __repr__(self):
        return f"{self.cart_id} {self.product_id} {self.quantity}"


class Products(Base):
    __tablename__ = 'Products'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'))  # venditore
    brand: Mapped[str]
    product_name: Mapped[str]
    date: Mapped[Date]
    category_id: Mapped[int] = mapped_column(ForeignKey('Categories.id'))
    price: Mapped[Float]
    availability: Mapped[int]
    descr: Mapped[str]

    # Serve per collegare la foreign key alla tabella CartProducts (secondary) che a sua volta collega a Cart, back_populates è la variabile in Cart
    # Preso da seconda risposta: https://stackoverflow.com/questions/5756559/how-to-build-many-to-many-relations-using-sqlalchemy-a-good-example
    cart_fk: Mapped['Cart'] = relationship(secondary='CartProducts', back_populates='product_fk', cascade='all, delete, delete-orphan, save-update')

    # Collega ad Orders con la tabella tramite OrderProducts, back_populates è la variabile in Orders
    order_fk: Mapped['Orders'] = relationship(secondary='OrderProducts', back_populates='product_fk', cascade='all, delete, delete-orphan, save-update')

    # Collega a Tags con la tabella intermedia TagProducts, back_populates è la variabile in Tags
    tag_fk: Mapped['Tags'] = relationship(secondary='TagProducts', back_populates='product_fk', cascade='all, delete, delete-orphan, save-update')

    # Collega Reviews con una relazione uno(Product)-molti(Review)
    review_fk: Mapped['Reviews'] = relationship(back_populates='product_fk', cascade='all, delete, delete-orphan, save-update')

    # Collega a Users (venditore)
    user_fk: Mapped['Users'] = relationship(back_populates='product_fk', cascade='all, delete, delete-orphan, save-update')

    # Collega a Categories
    category_fk: Mapped['Categories'] = relationship(back_populates='product_fk', cascade='all, delete, delete-orphan, save-update')

    def __repr__(self):
        return f"{self.id} {self.product_name} {self.brand} {self.date} {self.category_id} {self.price} {self.availability} {self.descr}"


class Orders(Base):
    __tablename__ = 'Orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'))
    date: Mapped[Date]
    price: Mapped[Float]
    address: Mapped[int]
    payment_method: Mapped[str]
    status: Mapped[str]

    # La relazione collega la foreign key a Products passando per la tabella intermedia OrderProducts (in secondary), back_populates prende la variabile in Products
    product_fk: Mapped['Products'] = relationship(secondary='OrderProducts', back_populates='order_fk', cascade='all, delete, delete-orphan, save-update')

    # Collega a user (uno(user)-molti(order))
    user_fk: Mapped['Users'] = relationship(back_populates='order_fk', cascade='all, delete, delete-orphan, save-update')

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

    # Collegata a Products con relazione uno(Categories)-molti(Products)
    product_fk: Mapped['Products'] = relationship(back_populates='category_fk', cascade='all, delete, delete-orphan, save-update')

    def __repr__(self):
        return f"{self.id} {self.name}"


class Tags(Base):
    __tablename__ = 'Tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(nullable=False) # con vincolo di NOT NULL

    product_fk: Mapped['Products'] = relationship(secondary='TagProducts', back_populates='tag_fk', cascade='all, delete, delete-orphan, save-update')

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

    # Da Users
    user_fk: Mapped['Users'] = relationship(back_populates='review_fk', cascade='all, delete, delete-orphan, save-update' )

    # Da Products
    product_fk: Mapped['Products'] = relationship(back_populates='review_fk', cascade='all, delete, delete-orphan, save-update' )

    def __repr__(self):
        return f"{self.id} {self.product_id} {self.user_id} {self.review}"


def data_insertion():
    Session = sessionmaker(engine)
    session = Session()
        # session.add_all([Products(),
        #                  Products(),
        #                  Products(),
        #                  Products() ])   

    session.add_all([ Categories(id=1, name='Arts'),
                                 Categories(id=2, name='Personal Care'),
                                 Categories(id=3, name='Eletronics'),
                                 Categories(id=4, name='Music'),
                                 Categories(id=5, name='Sports'),
                                 Categories(id=6, name='Movies & TV'),
                                 Categories(id=7, name='Software'),
                                 Categories(id=8, name='Games'),
                                 Categories(id=9, name='House'),
                                 Categories(id=10, name='DIY'), ])

    session.commit()
