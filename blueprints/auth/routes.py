from . import auth_bp
from flask_bcrypt import Bcrypt
from decimal import Decimal
from flask import Flask, redirect, render_template, request, session, url_for, flash, send_from_directory
from sqlalchemy.engine import url

from tables import User, Product, Base, Product, User, Category, Address, CartProducts, Order, OrderProducts, Tag, TagProduct, Review
from exceptions import InvalidCredential, MissingData, InvalidOrder
from config import Base, engine, db_session, app, login_manager, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, bcrypt

from sqlalchemy import create_engine, select, join, union, update, func, delete, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base, contains_eager, aliased
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import datetime
import os.path

# route del login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # ha inserito i dati, li verifichiamo e reindirizziamo di conseguenza
        email = request.form.get('email')
        password_form = request.form.get('password')

        # Query per individuare l'utente per poi testare la password, se non trova l'utente ritorna 'None'
        usr = db_session.scalar(select(User).where(User.email == email))
        if usr == None: # Utente non trovato
            flash('Wrong credentials', 'error')
            return redirect(request.url)
        
        # Controllo della password; nel database abbiamo memorizzato l'hash quindi facciamo l'hash di quella inserita
        # e controlliamo che sia uguale
        if bcrypt.check_password_hash(usr.password, password_form):
            login_user(usr)
            if request.args.get('next'):
                return redirect(request.args.get('next'))

            return redirect(url_for('home'))

        else:
            flash('Wrong credentials', 'error')
            return redirect(request.url)

    else: # Carichiamo la pagina per inserire i dati
        return render_template('login.html')

@auth_bp.route('/logout')
@login_required # Indica che è richiesto un login per accedere a questa pagina, un login avvenuto con successo e quindi con un utente loggato
def logout():
    current_user.last_logout = datetime.datetime.now()
    db_session.commit()
    logout_user()
    return redirect(url_for('home'))

# route per la registrazione
@auth_bp.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if db_session.scalar(select(User).filter(User.username == username)) is not None:
            flash('Username already exists', 'error')
            return redirect(request.url)

        if db_session.scalar(select(User).filter(User.email == email)) is not None:
            flash('E-mail address already exists', 'error')
            return redirect(request.url)

        conf_password = request.form.get('conf-password')

        if password != conf_password:
            flash('Password and confirmation password do not match', 'error')
            return redirect(request.url)

        # Nel costruttore della classe User chiamiamo metodi che controllano la correttenzza dei dati e in caso lanciano un'eccezione
        # con un messaggio specifico, che prendiamo nel catch e stampiamo a schermo
        try:
            new_user = User(
                email= email,
                username= username,
                password= password,
                name= request.form.get('fname'),
                last_name= request.form.get('lname'),
                user_type= (request.form.get('user_type') == "Seller"),
                last_logout=datetime.datetime.min
            )
        except InvalidCredential as err:
            flash(err.message, 'error') # il primo è il messaggio che mandiamo e il secondo la tipologia del messaggio
            return redirect(request.url)

        db_session.add(new_user)

        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            flash(str(e), 'error')
            return redirect(request.url)

        return redirect(url_for('auth.login'))
    else:
        return render_template('signup.html')
