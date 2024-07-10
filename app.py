from flask import Flask, redirect, render_template, request, session, url_for
from tables import User, Product, engine, Base
from sqlalchemy import create_engine, select, join, update
from sqlalchemy.orm import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from tables import Product, User, Category

import datetime
import os.path

# Creazione app flask
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configurazioni per il login manager
app.secret_key = 'jfweerjwi239marameo54:_f,,asd190ud'
login_manager = LoginManager()
login_manager.init_app(app)

# Usato per l'hash sulle password
bcrypt = Bcrypt()
bcrypt.init_app(app)

# Crea il database
Base.metadata.create_all(engine)
db_session = Session(engine)

def db_init():
    if db_session.scalar(Category).all() == None:
        db_session.add_all([ Categories(id=1, name='Arts'),
                                    Categories(id=2, name='Personal Care'),
                                    Categories(id=3, name='Eletronics'),
                                    Categories(id=4, name='Music'),
                                    Categories(id=5, name='Sports'),
                                    Categories(id=6, name='Movies & TV'),
                                    Categories(id=7, name='Software'),
                                    Categories(id=8, name='Games'),
                                    Categories(id=9, name='House'),
                                    Categories(id=10, name='DIY'), ])
        db_session.commit()


@app.route('/')
def start():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    db_init()
    return render_template('prova.html' , items=(db_session.scalars(select(Product)).all()))

@app.route('/product-details/<int:pid>')
def product_details(pid):
    return render_template('zoom_in.html', item=db_session.scalar(select(Product).where(Product.id == pid)))

# route per aggiunta di un nuovo prodotto
@app.route('/sell', methods=['GET', 'POST'])
# @login_required
def sell():
    if request.method == 'POST': # Sono stati inseriti i dati di un prodotto, lo memorizziamo
        product = Product(user_id=1, # prende l'utente attualmente loggato (current_user)
                          brand=request.form.get('brand'),
                          category_id=request.form.get('category'),
                          product_name=request.form.get('name'),
                          date=datetime.datetime.now(),
                          price=request.form.get('price'),
                          availability=10,
                          descr=request.form.get('description'))
        db_session.add(product)
        db_session.commit()
        return redirect(url_for('sell')) # Reindirizza alla pagina di tutti i prodotti in vendita
    else: # Renderizziamo la pagina in cui dovrà inserire i dettagli del prodotto
        return render_template('sell.html')

@login_manager.user_loader
def load_user(user_id):
    return db_session.scalar(select(User).where(User.id == int(user_id))) # Dovrebbe ritornare 'None' se l'ID non è valido

# route del login
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # ha inserito i dati, li verifichiamo e reindirizziamo di conseguenza
        email = request.form.get('email')
        password_form = request.form.get('password')

        # Query per individuare l'utente per poi testare la password, se non trova l'utente ritorna 'None'
        usr = db_session.scalar(select(User).where(User.email == email))

        if usr == None: # Utente non trovato
            return render_template('login.html', error_login="wrong credentials") # Ritenta il login

        # Controllo della password; nel database abbiamo memorizzato l'hash quindi facciamo l'hash di quella inserita
        # e controlliamo che sia uguale
        if bcrypt.check_password_hash(usr.password, password_form):
            login_user(usr)
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error_login="wrong credentials") # Ritenta il login

    else: # Carichiamo la pagina per inserire i dati
        return render_template('login.html')

@app.route('/logout')
@login_required # Indica che è richiesto un login per accedere a questa pagina, un login avvenuto con successo e quindi con un utente loggato
def logout():
    logout_user()
    return redirect(url_for('home')) # route HOME da creare

# route per la registrazione
@app.route('/register', methods=['GET','POST'])
def registration():
    if request.method == 'POST':
        username = request.form.get('username')

        password = request.form.get('password')
        conf_password = request.form.get('conf-password')
        if password != conf_password:
            return render_template('register.html', error_registration="Password and Confirmation Password do not match")

        # Nel costruttore della classe User chiamiamo metodi che controllano la correttenzza dei dati e in caso lanciano un'eccezione
        # con un messaggio specifico, che prendiamo nel catch e stampiamo a schermo
        from exceptions import InvalidCredential
        try:
            new_user = User(email= request.form.get('email'),
                            username= request.form.get('username'),
                            password= password,
                            name= request.form.get('fname'),
                            last_name= request.form.get('lname'),
                            user_type= (True if request.form.get('user_type') == "Buyer" else False)) # Operatore ternario
        except InvalidCredential as e:
            return render_template('register.html', error_registration=e)

        db_session.add(new_user)
        db_session.commit()

        return redirect(url_for('login'))
    else:
        return render_template('register.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)


