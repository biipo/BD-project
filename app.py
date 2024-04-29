from flask import Flask, redirect, render_template, request, session
from tables import Users, Base, Categories, Products
from sqlalchemy import create_engine, select, join, update
from sqlalchemy.orm import sessionmaker
import random

import datetime
import os.path

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "?,u~Jnu@axx<kK_s`vcQfpqvQi4iV7XavP2£E:FI;!?apt^A%"
engine = create_engine('sqlite:///data.db', echo=True)

Session = sessionmaker(engine)
db_session = Session()

# def db_init():
#     db_session.add_all([ Categories(id=1, name='Arts'),
#                                  Categories(id=2, name='Personal Care'),
#                                  Categories(id=3, name='Eletronics'),
#                                  Categories(id=4, name='Music'),
#                                  Categories(id=5, name='Sports'),
#                                  Categories(id=6, name='Movies & TV'),
#                                  Categories(id=7, name='Software'),
#                                  Categories(id=8, name='Games'),
#                                  Categories(id=9, name='House'),
#                                  Categories(id=10, name='DIY'), ])

#     db_session.commit()

def main():
    app.run(host='127.0.0.1', debug=True)

# Pagina iniziale, per ora reindirizza ad altre pagine ma solo per test
@app.route('/')
def start():
    Base.metadata.create_all(engine)
    return redirect('/products-list', code=302)


# route dei prodotti in vendita
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST': # Sono stati inseriti i dati di un prodotto, lo memorizziamo
        product_id = random.randrange(100) # Cambiare metodo generazione id
        product_name = request.form.get('product-name')
        brand = request.form.get('brand')
        category = request.form.get('category')
        price = request.form.get('price')
        description = request.form.get('description')

        usr_id = session['id']
        product = Products(id=product_id, user_id=usr_id, brand=brand, product_name=product_name, date=datetime.datetime.now(),
                           category_id=category, price=price, availability=10, descr=description)
        db_session.add(product)
        db_session.commit()
        return redirect('/products-list') # Rimandato alla route con tutti i prodotti
    elif request.method == 'GET': # Renderizziamo la pagina in cui dovrà inserire i dettagli del prodotto
        return render_template('sell.html')
    else: # Richiesta inaspettata (NON dovrebbe neanche entrare nell'else visto che la route in se non accetta altri tipi di richieste)
        return "<h1>UNEXPECTED ERROR</h1>"


# route che lista tutti i prodotti in vendita
@app.route('/products-list')
def products_list():
    products = db_session.query(Products).all()
    user_vendor = db_session.query(Users).all()

    prova_user = Users(id=55, email="prova", username="prova", password="prova", name="prova", last_name="prova", user_type=False,
                       product_fk=[Products(id=38, user_id=55, brand="prova", product_name="prova", date=datetime.datetime.now(),
                           category_id="prova", price="prova", availability=10, descr="prova")])
    prova_product = Products(id=67, user_id=55, brand=4.0, product_name="prova", date=datetime.datetime.now(),
                           category_id="prova", price=4.0, availability=10, descr="prova")

    db_session.add(prova_user)
    db_session.add(prova_product)
    db_session.commit()
    # db_session.query(Users).filter(Users.id== 1).update({'product_fk': [56]})
    # db_session.query(Users).update({'product_fk': 56})
    # db_session.query(Users).filter(Users.id== 6).update({'product_fk': 88})
    # db_session.query(Users).filter(Users.id== 9).update({'product_fk': [52]})
    # db_session.commit()
    
    # prod_vend = db_session.scalars(select(Products).join(Products.user_id)).all()

    return render_template('products.html', products=products, vendor=user_vendor, prod_vend=user_vendor)


# route del login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET': # deve inserire i dati, renderizziamo la pagina per il login
        return render_template('login.html')
    elif request.method == 'POST': # ha inserito i dati, li verifichiamo e reindirizziamo di conseguenza
        email = request.form.get('email')
        password = request.form.get('password')
        if email == 'admin' and password == 'admin':
            return f"The email: {email} and password: {password}"
        else:
            return redirect('/login', code=302)
    else:
        return "<h1>UNEXPECTED ERROR</h1>"


# route per la registrazione
@app.route('/register', methods=['GET','POST'])
def registration():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        usr_id = random.randrange(20)
        name = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = True
        
        new_user = Users(id=usr_id, email=email, username=username, password=password, name=name, last_name=lastname, user_type=user_type)
        session['id'] = usr_id

        db_session.add(new_user)
        db_session.commit()

        return redirect('/sell')
    else:
        return "<h1>UNEXPECTED ERROR</h1>"


if __name__ == '__main__':
    main()
