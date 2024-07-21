from flask import Flask, redirect, render_template, request, session, url_for, flash, send_from_directory
from tables import User, Product, Base, Product, User, Category, Address, Cart, CartProducts, Order, OrderProducts
from sqlalchemy import create_engine, select, join, update, func
from sqlalchemy.orm import sessionmaker, Session, declarative_base, contains_eager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import datetime
import os.path

# Creazione app flask
app = Flask(__name__, template_folder='templates', static_folder='static')

# Per upload file immagini prodotti
UPLOAD_FOLDER = './.upload/product_image' # In questa cartella vengono salvate le immagini dei prodotti
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configurazioni per il login manager
app.secret_key = 'jfweerjwi239marameo54:_f,,asd190ud'
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Usato per l'hash sulle password
bcrypt = Bcrypt()
bcrypt.init_app(app)

# Connette al database
engine = create_engine('sqlite:///./data.db', echo=True)
#Base = declarative_base()
Base.metadata.create_all(engine)
#Session = sessionmaker(bind=engine)
db_session = Session(engine)

def db_init():
    '''
    if db_session.scalars(select(Category)).all() == None:
        db_session.add_all([ Category(id=1, name='Arts'),
                             Category(id=2, name='Personal Care'),
                             Category(id=3, name='Eletronics'),
                             Category(id=4, name='Music'),
                             Category(id=5, name='Sports'),
                             Category(id=6, name='Movies & TV'),
                             Category(id=7, name='Software'),
                             Category(id=8, name='Games'),
                             Category(id=9, name='House'),
                             Category(id=10, name='DIY') ])
        db_session.commit()
    '''

@app.route('/')
def start():
    return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/home')
def home():
    return render_template('home.html' , items=(db_session.scalars(select(Product)).all()))

@app.route('/product-details/<int:pid>', methods=['GET', 'POST'])
def product_details(pid):
    if request.method == 'GET':
        item = db_session.scalar(select(Product).where(Product.id == pid))
        seller = db_session.scalar(select(User).where(User.id == item.user_id))
        return render_template('zoom_in.html', item=item, seller=seller)
    else:
        if current_user.is_authenticated:
            order_quantity = request.form.get('quantity')
            item = db_session.scalar(select(Product).where(Product.id == pid))

            # Controllo se esiste già il carrello prima di crearlo
            cart = db_session.scalar(select(Cart).where(Cart.user_id == current_user.get_id()))
            if cart == None:
                cart = Cart(current_user.get_id()) # Creiamo un nuovo carrello per questo utente, quando viene fatto l'ordine questo carrello viene distrutto
                db_session.add(cart)
                db_session.commit()
            cart.products.append(CartProducts(item, order_quantity, cart)) # Aggiungiamo alla lista di elementi del carello il prodotto che sta vedendo

            return redirect(url_for('cart'))
        else:
            flash('Login is required to place orders', 'error')
            return redirect(url_for('login'))

# Controlla se il file è di tipo corretto (foto/gif)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# route per aggiunta di un nuovo prodotto
@app.route('/sell', methods=['GET', 'POST'])
@login_required # Indica che è richiesto un login per accedere a questa pagina, un login avvenuto con successo e quindi con un utente loggato
def sell():
    if request.method == 'POST': # Sono stati inseriti i dati di un prodotto, lo memorizziamo
            if 'image_file' not in request.files:
                flash('No file attached', 'error')
                return redirect(request.url)
            file = request.files['image_file']
            if file.filename == '':
                flash('No selected file', 'error')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                # filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(path)
                
                from exceptions import MissingData
                try:
                    product = Product(user_id=current_user.get_id(),  # prende l'utente attualmente loggato (current_user)
                                    brand=request.form.get('brand'),
                                    category_id=request.form.get('category'),
                                    product_name=request.form.get('name'),
                                    date=datetime.datetime.now(),
                                    price=request.form.get('price'),
                                    availability=request.form.get('availability'),
                                    descr=request.form.get('description'),
                                    image_filename=file.filename)
                except MissingData as err:
                    flash(err.message, 'error')
                    return redirect(request.url)
                db_session.add(product)
                db_session.commit()
                return redirect(url_for('home')) # Reindirizza alla pagina di tutti i prodotti in vendita
            else:
                flash('Invalid file type', 'error')
                return redirect(request.url)
    else: # Renderizziamo la pagina in cui dovrà inserire i dettagli del prodotto
        return render_template('sell.html')

@login_manager.user_loader
def load_user(user_id):
    return db_session.scalar(select(User).where(User.id == int(user_id))) # Dovrebbe ritornare 'None' se l'ID non è valido

@app.route('/profile')
@login_required # Indica che è richiesto un login per accedere a questa pagina, un login avvenuto con successo e quindi con un utente loggato
def profile():
    user = db_session.scalar(select(User).where(User.id == int(current_user.get_id())))
    addrs = db_session.scalar(select(Address).where(Address.user_id == int(current_user.get_id())))
    return render_template('profile.html', user=user, addrs=addrs)

@app.route('/user/<username>')
def user(username):
    user = db_session.scalar(select(User).where(User.username == str(username)))
    return render_template('user.html', user=user)

@app.route('/cart')
@login_required
def cart():
    # La query ritorna una lista di elementi CartProduct
    prod = db_session.scalar(select(Cart).where(Cart.id == int(current_user.get_id()))) # Il carrello per un utente è sempre 1
    for item in prod.products:
        print(item.product.product_name)
    return render_template('cart.html', cart_items=prod.products)

@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    user = db_session.scalar(select(User).where(User.id == current_user.get_id()))
    curr_time = datetime.datetime.now()

    if request.method == 'GET':
        # Se utente non venditore
        if not user.is_seller():
            orders = db_session.scalars(select(Order).filter(Order.user_id == current_user.get_id()).order_by(Order.date.desc()))
            return render_template('orders.html', orders=orders, now=curr_time)

        else:
            orders = db_session.scalars(
                select(Order)
                .join(OrderProducts)
                .join(Product)
                .filter(Product.seller == user)
            )
            return render_template('orders_sold.html', orders=orders, now=curr_time)
    
    else:
        new_status = request.form.get('new-status')
        order_id = request.form.get('order-id')

        # If new status valid
        if not new_status or new_status not in ['Received', 'Sent', 'Processing', 'Cancelled']:
            return redirect(url_for('orders'))
        
        # Query for order with given id and sold by current user
        order = db_session.scalar(select(Order).join(OrderProducts).join(Product).filter(Order.id == order_id).filter(Product.seller == user))
        if order is None:
            return redirect(url_for('orders'))
       
        # If order status new and not received or cancelled
        if order.status not in [new_status, 'Received', 'Cancelled']:
            order.status = new_status
            db_session.commit()

        return redirect(url_for('orders'))

# route del login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # ha inserito i dati, li verifichiamo e reindirizziamo di conseguenza
        email = request.form.get('email')
        password_form = request.form.get('password')

        # Query per individuare l'utente per poi testare la password, se non trova l'utente ritorna 'None'
        usr = db_session.scalar(select(User).where(User.email == email))

        if usr == None: # Utente non trovato
            flash('Wrong credentials', 'error')
            return redirect(request.url) # Ritenta il login
        
        # Controllo della password; nel database abbiamo memorizzato l'hash quindi facciamo l'hash di quella inserita
        # e controlliamo che sia uguale
        if bcrypt.check_password_hash(usr.password, password_form):
            login_user(usr)
            # print(current_user.get_id())
            if request.args.get('next'):
                return redirect(request.args.get('next'))

            return redirect(url_for('home'))

        else:
            flash('Wrong credentials', 'error')
            return redirect(request.url) # Ritenta il login

    else: # Carichiamo la pagina per inserire i dati
        return render_template('login.html')

@app.route('/logout')
@login_required # Indica che è richiesto un login per accedere a questa pagina, un login avvenuto con successo e quindi con un utente loggato
def logout():
    logout_user()
    return redirect(url_for('home')) # route HOME da creare

# route per la registrazione
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conf_password = request.form.get('conf-password')

        if password != conf_password:
            flash('Password and confirmation password do not match', 'error')
            return redirect(request.url)

        # Nel costruttore della classe User chiamiamo metodi che controllano la correttenzza dei dati e in caso lanciano un'eccezione
        # con un messaggio specifico, che prendiamo nel catch e stampiamo a schermo
        from exceptions import InvalidCredential
        try:
            new_user = User(email= request.form.get('email'),
                            username= username,
                            password= password,
                            name= request.form.get('fname'),
                            last_name= request.form.get('lname'),
                            user_type= (request.form.get('user_type') == "Buyer"))
        except InvalidCredential as err:
            flash(err.message, 'error') # il primo è il messaggio che mandiamo e il secondo la tipologia del messaggio
            return redirect(request.url)

        db_session.add(new_user)
        db_session.commit()

        return redirect(url_for('login'))
    else:
        return render_template('signup.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)


