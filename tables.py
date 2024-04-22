from sqlalchemy import *
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('sqlite:///data.db', echo=True)

Base = declarative_base()

# Le relationship() vengono definite nelle tabelle in cui "arriva" una foreign key (nel senso: se tab 1
# ha la sua chiave, e poi c'è tab 2 che ha una FK che indica tab 1; in tab 1 dobbiamo mettere una relationship()

class Users(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    username = Column(String, nullable=False)
    passsword = Column(String, nullable=False)
    name = Column(String)
    last_name = Column(String)
    user_type = Column(Boolean)

    addresses = relationship('Addresses', back_populates='Users', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return "{self.id} {self.email} {self.username} {self.passsword} {self.name} {self.last_name} {self.user_type}"


class Addresses(Base):
    __tablename__ = 'Addresses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id', ondelete='CASCADE'))
    active = Column(Boolean)
    state = Column(String)
    province = Column(String)

    user = relationship(Users, back_populates='Addresses')  # Serve per collegare la ForeignKey

    def __repr__(self):
        return "{self.id} {self.user_id} {self.active} {self.state} {self:province}"


class Cart(Base):
    __tablename__ = 'Cart'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id'))

    # Collega la foreign key (alla tabella CartProducts), secondary (in teoria) è perché è una relazione molti-molti
    # e quindi c'è una tabella intermedia, appunto CartProducts, prima di raggiungere Products
    product = relationship('Products', secondary='CartProducts', back_populates='Cart', cascade='all, delete, '
                                                                                                'delete-orphan'
                                                                                                ', save-update')

    items = relationship('Products')

    def __repr__(self):
        return f"{self.id} {self.user_id}"


# https://stackoverflow.com/questions/5756559/how-to-build-many-to-many-relations-using-sqlalchemy-a-good-example

class CartProducts(Base):
    __tablename__ = 'CartProducts'

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('Cart.id'))
    product_id = Column(Integer, ForeignKey('Products.id'))
    quantity = Column(Integer)

    def __repr__(self):
        return f"{self.cart_id} {self.product_id} {self.quantity}"


class Products(Base):
    __tablename__ = 'Products'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id'))  # venditore
    brand = Column(String)
    product_name = Column(String)
    date = Column(Date)  # Non sicuro del tipo
    category_id = Column(Integer, ForeignKey('Categories.id'))
    price = Column(Float)
    availability = Column(Integer)
    descr = Column(String)

    # Serve per collegare la foreign key alla tabella CartProducts (secondary) che a sua volta collega a Cart
    # Preso da seconda risposta: https://stackoverflow.com/questions/5756559/how-to-build-many-to-many-relations-using-sqlalchemy-a-good-example
    cart = relationship('Cart', secondary='CartProducts', back_populates='Cart', cascade='all, delete, '
                                                                                         'delete-orphan'
                                                                                         ', save-update')

    def __repr__(self):
        return f"{self.id} {self.product_name} {self.brand} {self.date} {self.category_id} {self.price} {self.availability} {self.descr}"


class Orders(Base):
    __tablename__ = 'Orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id'))
    date = Column(Date)
    price = Column(Float)
    address = Column(Integer)  # è una Foreign Key alla tabella Addresses
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
        # session.add_all([Products(),
        #                  Products(),
        #                  Products(),
        #                  Products() ])   

        session.add_all([Categories(id=1, name='Arts'),
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
