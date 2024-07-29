from flask import Flask, redirect, render_template, request, session, url_for, flash, send_from_directory
from sqlalchemy.engine import url
from tables import User, Product, Base, Product, User, Category, Address, CartProducts, Order, OrderProducts, Tag, TagProduct, TagGroup
from sqlalchemy import create_engine, select, join, update, func, delete
from sqlalchemy.orm import sessionmaker, Session, declarative_base, contains_eager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import datetime
import os.path
from exceptions import InvalidCredential, MissingData

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
    sub_categories = [
        SubCategory(categories[0], 'Painting Supplies'),
        SubCategory(categories[0], 'Drawing Tools'),
        SubCategory(categories[0], 'Sculpture Materials'),
        SubCategory(categories[0], 'Craft Kits'),
        SubCategory(categories[0], 'Art Books'),
        
        SubCategory(categories[1], 'Skincare'),
        SubCategory(categories[1], 'Haircare'),
        SubCategory(categories[1], 'Oral Care'),
        SubCategory(categories[1], 'Fragrances'),
        SubCategory(categories[1], 'Personal Hygiene'),
        
        SubCategory(categories[2], 'Smartphones'),
        SubCategory(categories[2], 'Laptops'),
        SubCategory(categories[2], 'Home Appliances'),
        SubCategory(categories[2], 'Wearable Technology'),
        SubCategory(categories[2], 'Audio & Video'),
        
        SubCategory(categories[3], 'Instruments'),
        SubCategory(categories[3], 'Sheet Music'),
        SubCategory(categories[3], 'Music Accessories'),
        SubCategory(categories[3], 'Recording Equipment'),
        SubCategory(categories[3], 'CDs & Vinyl Records'),
        
        SubCategory(categories[4], 'Fitness Equipment'),
        SubCategory(categories[4], 'Team Sports Gear'),
        SubCategory(categories[4], 'Outdoor Recreation'),
        SubCategory(categories[4], 'Sportswear'),
        SubCategory(categories[4], 'Athletic Footwear'),
        
        SubCategory(categories[5], 'DVDs & Blu-rays'),
        SubCategory(categories[5], 'Streaming Devices'),
        SubCategory(categories[5], 'TV Accessories'),
        SubCategory(categories[5], 'Collectibles & Memorabilia'),
        SubCategory(categories[5], 'Movie Posters'),
        
        SubCategory(categories[6], 'Operating Systems'),
        SubCategory(categories[6], 'Productivity Software'),
        SubCategory(categories[6], 'Security Software'),
        SubCategory(categories[6], 'Creative Software'),
        SubCategory(categories[6], 'Educational Software'),
        
        SubCategory(categories[7], 'Video Games'),
        SubCategory(categories[7], 'Board Games'),
        SubCategory(categories[7], 'Card Games'),
        SubCategory(categories[7], 'Gaming Accessories'),
        SubCategory(categories[7], 'Puzzles'),
        
        SubCategory(categories[8], 'Furniture'),
        SubCategory(categories[8], 'Kitchenware'),
        SubCategory(categories[8], 'Bedding & Linens'),
        SubCategory(categories[8], 'Home Decor'),
        SubCategory(categories[8], 'Cleaning Supplies'),
        
        SubCategory(categories[9], 'Tools'),
        SubCategory(categories[9], 'Building Materials'),
        SubCategory(categories[9], 'Paint & Supplies'),
        SubCategory(categories[9], 'Crafting Tools'),
        SubCategory(categories[9], 'Garden & Outdoor')
    ]
    '''
    if db_session.scalar(select(Category)) is None:
        db_session.add_all([ Category(name='Arts'),
                            Category(name='Personal Care'),
                            Category(name='Electronics'),
                            Category(name='Music'),
                            Category(name='Sports'),
                            Category(name='Movies & TV'),
                            Category(name='Software'),
                            Category(name='Games'),
                            Category(name='House'),
                            Category(name='DIY')
                            ])
        db_session.commit()

    dim = TagGroup(name='Dimensions')
    if db_session.scalar(select(TagGroup)) is None:
        db_session.add_all([ TagGroup(name='Color'),
                             TagGroup(name='Brand'),
                             dim
                             ])
        db_session.commit()

    if db_session.scalar(select(Tag)) is None:
        db_session.add_all([ Tag(value='small', tag_group=dim),
                             Tag(value='medium', tag_group=dim),
                             Tag(value='big', tag_group=dim)
                            ])
        db_session.commit()
    

@app.route('/')
def start():
    db_init()
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
            order_quantity = int(request.form.get('quantity'))
            item = db_session.scalar(select(Product).where(Product.id == pid))
            

            if order_quantity <= item.availability:
                new_cart_item = CartProducts(item, order_quantity, current_user)
            else:
                flash('Invalid quantity selected', 'error')
                return redirect(url_for('product_details', pid=item.id))

            # Controllo se esiste già l'elemento nel carrello prima di crearlo
            existing = db_session.scalar(
                select(CartProducts)
                .filter(CartProducts.product_id == new_cart_item.product_id)
                .filter(CartProducts.user_id == new_cart_item.user_id)
            )

            # Se già esiste aggiungiamo la quantità
            if existing is not None:
                existing.quantity += order_quantity
            else:
                db_session.add(new_cart_item)

            db_session.commit()

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
                dimensions = request.form.get('dimensions')
                color = request.form.get('color')
                brand = request.form.get('brand')
                
                try:
                    product = Product(user_id=current_user.get_id(),  # prende l'utente attualmente loggato (current_user)
                                      category_id=int(request.form.get('category')),
                                      product_name=request.form.get('name'),
                                      date=datetime.datetime.now(),
                                      price=float(request.form.get('price')),
                                      availability=int(request.form.get('availability')),
                                      descr=request.form.get('description'),
                                      image_filename=file.filename)

                    # Seleziona l'oggetto tag corrispondente al valore della dimensione scelta dal venditore, trattandosi
                    # della dimensione abbiamo imposto 3 grandezze che esistono già nel database quindi sicuramente non va aggiunta
                    prod_dim = TagProduct(db_session.scalar(select(Tag).where(Tag.value == str(dimensions))), product)

                    color_db = db_session.scalar(select(Tag).where(Tag.value == str(color)))
                    if  color_db == None: # Se il colore del prodotto è nuovo lo aggiungiamo
                        color_db = Tag(str(color), db_session.scalar(select(TagGroup).where(TagGroup.name == 'Color')))
                    prod_color = TagProduct(color_db , product)

                    brand_db = db_session.scalar(select(Tag).where(Tag.value == str(brand)))
                    if  brand_db  == None: # Se il brand del prodotto è nuovo
                        brand_db = Tag(str(brand), db_session.scalar(select(TagGroup).where(TagGroup.name == 'Brand')))
                    prod_brand = TagProduct(brand_db , product)
                except MissingData as err:
                    flash(err.message, 'error')
                    return redirect(request.url)

                product.tags.extend([prod_dim , prod_color , prod_brand]) # Aggiunge i tag relativi al prodotto

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

@app.route('/profile', methods=['GET', 'POST'])
@login_required # Indica che è richiesto un login per accedere a questa pagina, un login avvenuto con successo e quindi con un utente loggato
def profile():

    if request.method == 'GET':
        user = db_session.scalar(select(User).filter(User.id == current_user.get_id()))
        addrs = db_session.scalar(select(Address).where(Address.user_id == int(current_user.get_id())))

        return render_template('profile.html', user=user, addrs=addrs)
    
    else:
        if request.form.get('info-update') is not None:
            user = db_session.scalar(select(User).filter(User.id == current_user.get_id()))
            user.name = request.form.get('info-fname')
            user.last_name = request.form.get('info-lname')
            user.email = request.form.get('info-email')
            db_session.commit()
        
        elif request.form.get('address-delete') is not None:
            db_session.delete(db_session.scalar(select(Address).filter(Address.id == request.form.get('address-id'))))
            db_session.commit()
            
        elif request.form.get('address-set-active') is not None:
            curr_active = db_session.scalar(select(Address).filter(Address.user_id == current_user.get_id()).filter(Address.active == True))
            if not curr_active.id == request.form.get('address-id'):
                curr_active.active = False
                db_session.scalar(select(Address).filter(Address.id == request.form.get('address-id'))).active = True
                db_session.commit()

        elif request.form.get('address-add') is not None:
            new_address = Address(
                user_id=current_user.get_id(),
                active=False,
                first_name=request.form.get('fname'),
                last_name=request.form.get('lname'),
                street=request.form.get('street'),
                postcode=request.form.get('post-code'),
                state=request.form.get('state'),
                #city=request.form.get('city'),
                province=request.form.get('province')
            )
            db_session.add(new_address)
            db_session.commit()
        
        return redirect(url_for('profile'))


@app.route('/user/<username>')
def user(username):
    user = db_session.scalar(select(User).where(User.username == str(username)))
    return render_template('user.html', user=user)

@app.route('/cart' , methods=['GET', 'POST'])
@login_required
def cart():
    if request.method == 'GET':
        # La query ritorna una lista di elementi CartProduct
        products = db_session.scalars(select(CartProducts).where(CartProducts.user_id == int(current_user.get_id()))).all()
        total = sum(p.quantity * p.product.price for p in products)
        return render_template('cart.html', cart_items=products, total=total)
    else:
        if request.form.get('clear-cart') is not None:
            db_session.execute(delete(CartProducts).where(CartProducts.user_id == current_user.get_id()))
            return redirect(url_for('cart'))
        
        elif request.form.get('delete-item') is not None:
            db_session.delete(
                    db_session.scalar(
                        select(CartProducts)
                        .filter(CartProducts.product_id == request.form.get('item-id'))
                        .filter(CartProducts.user_id == current_user.get_id())
                    )
            )
            db_session.commit()
            return redirect(url_for('cart'))

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
        try:
            new_user = User(email= request.form.get('email'),
                            username= username,
                            password= password,
                            name= request.form.get('fname'),
                            last_name= request.form.get('lname'),
                            user_type= (request.form.get('user_type') == "Seller"))
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


