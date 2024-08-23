from decimal import Decimal
from flask import Flask, redirect, render_template, request, session, url_for, flash, send_from_directory
from sqlalchemy.engine import url
from sqlalchemy import create_engine, select, join, union, update, func, delete, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base, contains_eager, aliased, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import datetime
import os.path
from exceptions import InvalidCredential, MissingData, InvalidOrder

# Centralizza engine e session così da poterli importare anche nei blueprints e non avere import circolari

# Creazione app flask
app = Flask(__name__, template_folder='templates', static_folder='static')

# Per upload file immagini prodotti
UPLOAD_FOLDER = './.upload/product_image' # In questa cartella vengono salvate le immagini dei prodotti
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configurazioni per il login manager
app.secret_key = 'jfweerjwi239marameo54:_f,,asd190ud'
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

class Base(DeclarativeBase):
    pass

engine = create_engine('sqlite:///./data.db', echo=True)
Base.metadata.create_all(engine)
db_session = Session(engine)

bcrypt = Bcrypt()
bcrypt.init_app(app)