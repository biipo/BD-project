from flask import Flask, redirect, render_template, request, session
from tables import User, Product, engine, Base
from sqlalchemy import create_engine, select, join, update
from sqlalchemy.orm import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import random
import re
from tables import Product, User

import datetime
import os.path

# Creazione app flask
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configurazioni per il login manager
app.secret_key = 'jfweerjwi239marameo54:_f,,asd190ud'
login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt()
bcrypt.init_app(app)

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
    return redirect('/home')

@app.route('/home')
def home():
    # users_list = db_session.query(User).all()
    return render_template('home.html')

# route che lista tutti i prodotti in vendita
@app.route('/products-list')
def products_list():
    products = db_session.query(Product).all()
    return render_template('products.html', products=products)

# route dei prodotti in vendita
@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    if request.method == 'POST': # Sono stati inseriti i dati di un prodotto, lo memorizziamo
        product = Product(id=random.randrange(100), # cambiare metodo generazione id prodotto
                            user_id=session['id'],
                            brand=request.form.get('brand'),
                            product_name=request.form.get('product-name'),
                            date=datetime.datetime.now(),
                            category_id=request.form.get('category'),
                            price=request.form.get('price'),
                            availability=10,
                            descr=request.form.get('description')
                            )
        db_session.add(product)
        db_session.commit()
        return redirect('/products-list') # Reindirizza alla pagina di tutti i prodotti in vendita
    else: # Renderizziamo la pagina in cui dovrà inserire i dettagli del prodotto
        return render_template('sell.html')

@login_manager.user_loader
def load_user(user_id):
    return db_session.execute(select(User).where(User.id == int(user_id))) # Dovrebbe ritornare 'None' se l'ID non è valido

# route del login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # ha inserito i dati, li verifichiamo e reindirizziamo di conseguenza
        email = request.form.get('email')
        password_form = request.form.get('password')
        try:
            # La query per trovare l'utente con l'email inserita, "scalars"
            usr = db_session.scalars(select(User).where(User.email == email)).first()
        except sqalchemy.exc.NoResultFound:
            return render_template('login.html', error_login="wrong credentials") # Ritenta il login, aggiungere messaggio di errore nel login

        if bcrypt.check_password_hash(usr.password, password_form):
            login_user(usr)
        else:
            return render_template('login.html', error_login="wrong credentials") # Ritenta il login, aggiungere messaggio di errore nel login

        return redirect('/home')
    else: # Carichiamo la pagina per inserire i dati
        return render_template('login.html')

@app.route('/logout')
@login_required # Indica che è richiesto un login per accedere a questa pagina, un login avvenuto con successo e quindi con un utente loggato
def logout():
    logout_user()
    return redirect('/home') # route HOME da creare

# route per la registrazione
@app.route('/register', methods=['GET','POST'])
def registration():
    if request.method == 'POST':
        # Pattern da rispettare per l'email
        pat_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        email = request.form.get('email')
        if not re.match(pat_email, email): # Controlla che l'email segua il pattern "xxx@xxx.xxx"
            return render_template('register.html', error_registration="Invalid email")

        username = request.form.get('username')
        if len(username) < 1 or len(username) > 16:
            return render_template('register.html', error_registration="Invalid username")

        password = request.form.get('password')
        conf_password = request.form.get('conf-password')
        if password != conf_password:
            return render_template('register.html', error_registration="Password and Confirmation Password do not match")
        # Controllo della password in chiaro, che abbia le caratteristiche adatte
        lower, upper, digit, special = 0, 0, 0, 0
        if(len(password) >= 8):
            for c in password:
                if c.islower():
                    lower += 1
                if c.isupper():
                    upper += 1
                if c.isdigit():
                    digit += 1
                if c in ["~","`", "!", "@","#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "+", "=", "{", "}", "[", "]", "|", "\\", ";", ":", "<", ">", ",", ".", "/", "?"]:
                    special += 1
            if (lower < 1 or upper < 1 or digit < 1 or special < 1):
                return render_template('register.html', error_registration="Invalid password")
        # Salvataggio del hash della password
        password = bcrypt.generate_password_hash(password)

        name = request.form.get('fname')
        last_name = request.form.get('lname')
        pat_name = r'\b[0-9._%+-]\b'
        if re.match(pat_name, name):
            return render_template('register.html', error_registration="Invalid name")
        if re.match(pat_name, last_name):
            return render_template('register.html', error_registration="Invalid last name")

        new_user = User(id       = random.randrange(100), # cambiare metodo generazione ID
                        email=email,
                        username=username,
                        password=password,
                        name=name,
                        last_name=last_name,
                        user_type= True if request.form.get('user_type') == "1" else False # Operatore ternario
                        )

        db_session.add(new_user)
        db_session.commit()

        return redirect('/home') # Da reindirizzare al login
    else:
        return render_template('register.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)


