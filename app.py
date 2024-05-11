import re
from flask import Flask, redirect, render_template, request, session
from tables import User, Product, engine, Base, user_counter, product_counter
from sqlalchemy import create_engine, select, join, update
from sqlalchemy.orm import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import login_manager, LoginManager, login_required, login_user, logout_user
from flarender_templatesk_bcrypt import Bcrypt
import random

import datetime
import os.path

# Creazione app flask
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configurazioni per il login manager
app.config['SECRET KEY'] = 'jfweerjwi239marameo54:_f,,asd190ud'
login_manager = LoginManager()
login_manager.init_app(app)

# Crea il database
Base.metadata.create_all(engine)
db_session = Session(engine)

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


@app.route('/')
def start():
    if current_user.is_authenticated:
        return redirect('/product-list');
    return redirect('/register')

@app.route('/home')
def home():
    return render_template('home.html')

# route che lista tutti i prodotti in vendita
@app.route('/products-list')
def products_list():
    
    products = db_session.query(Product).all()
    # user_vendor = db_session.query(User).all()
    # prod_vend = db_session.scalars(select(User).join(User.product_fk)).all()

    return render_template('products.html', products=products)#, vendor=user_vendor, prod_vend=prod_vend)

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
    else # Renderizziamo la pagina in cui dovrà inserire i dettagli del prodotto
        return render_template('sell.html')

@login_manager.user_loader
def load_user(user_id):
    usr_id = int(user_id)
    return db_session.execute(select(User).where(User.id == usr_id))

# route del login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # ha inserito i dati, li verifichiamo e reindirizziamo di conseguenza
        email = request.form.get('email')
        password = request.form.get('password')
        query = select(User).where(User.email == email, User.password == password)
        try:
            usr = db_session.scalars(query).one()
            login_user(usr)
        except sqalchemy.exc.NoResultFound:
            return redirect('login.html') # Ritenta il login, aggiungere messaggio di errore nel login
        return redirect('/home')
        # else:
        #     return redirect('/login')
    else: # Carichiamo la pagina per inserire i dati
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/home') # route HOME da creare

# route per la registrazione
@app.route('/register', methods=['GET','POST'])
def registration():
    if request.method == 'POST':
        user_counter = user_counter+1
        id = user_counter
        name = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        new_user = Users(id=usr_id, email=email, username=username, password=password, name=name, last_name=lastname, user_type=user_type)

        db_session.add(new_user)
        db_session.commit()

        return redirect('/sell')
    else:
        return render_template('register.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)


