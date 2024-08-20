from decimal import Decimal
from flask import Flask, redirect, render_template, request, session, url_for, flash, send_from_directory
from sqlalchemy.engine import url
from tables import User, Product, Base, Product, User, Category, Address, CartProducts, Order, OrderProducts, Tag, TagProduct, Review
from sqlalchemy import create_engine, select, join, union, update, func, delete, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base, contains_eager, aliased
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import datetime
import os.path
from exceptions import InvalidCredential, MissingData, InvalidOrder

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
    
    if db_session.scalar(select(Tag)) is None:
        db_session.add_all([ 
            Tag('Red'),
            Tag('Blue'),
            Tag('Green'),
            Tag('Yellow'),
            Tag('Orange'),
            Tag('Purple'),
            Tag('Pink'),
            Tag('Brown'),
            Tag('Black'),
            Tag('White'),
            Tag('Gray'),
            Tag('Beige'),
            Tag('Maroon'),
            Tag('Navy'),
            Tag('Teal'),
            Tag('Turquoise'),
            Tag('Lavender'),
            Tag('Magenta'),
            Tag('Cyan'),
            Tag('Lime'),
        ])
        db_session.commit()

    # dim = TagGroup(name='Dimensions')
    # if db_session.scalar(select(TagGroup)) is None:
    #     db_session.add_all([ TagGroup(name='Color'),
    #                          TagGroup(name='Brand'),
    #                          dim
    #                          ])
    #     db_session.commit()

    # if db_session.scalar(select(Tag)) is None:
    #     db_session.add_all([ Tag(value='small (less than 200x200 mm)', tag_group=dim),
    #                          Tag(value='medium (between 200x200 and 500x500 mm)', tag_group=dim),
    #                          Tag(value='big (more than 500x500 mm)', tag_group=dim)
    #                         ])
    #     db_session.commit()

# Trigger che aggiorna il rating di un prodotto nel momento in cui viene aggiunta una nuova recensione
@event.listens_for(db_session, 'before_commit')
def before_commit(session):
    for obj in session.new:
        if isinstance(obj, Review):
            item = db_session.scalar(select(Product).filter(Product.id == obj.product_id))
            item.rating = sum(r.stars for r in item.reviews) / len(item.reviews) if len(item.reviews if item.reviews is not None else []) > 0 else 0
            session.add(item)
            

@app.route('/')
def start():
    db_init()
    return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/home')
def home():
    if request.method == 'GET':
        items_q = db_session.query(Product)
        
        # Parametri GET possibili
        seller = request.args.get('seller')
        search = request.args.get('search')
        
        if search is not None:
            items_q = items_q.filter(Product.product_name.like('%' + search + '%'))

        if seller is not None:
            items_q = items_q.filter(Product.user_id == seller)
            # Rimuove prodotti non disponibili, a meno che utente non ne sia venditore
            if current_user.get_id() != seller:
                items_q = items_q.filter(Product.availability > 0)
            items = items_q.all()
        else:
            items = (items_q.filter(Product.availability > 0)).all()

        return render_template('home.html' , items=items)
    
@app.route('/product-details/<int:pid>', methods=['GET', 'POST'])
def product_details(pid):
    if request.method == 'GET':
        item = db_session.scalar(select(Product).filter(Product.id == pid))
        print('gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg')
        print(item.rating)
        print(item.product_name)
        print('gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg')
        if item is None:
            return redirect(url_for('home'))

        # Se ci sono recensioni ne calcolo la media
        # rating = sum(r.stars for r in item.reviews) / len(item.reviews) if len(item.reviews) > 0 else 0

        # Se articolo acquistato e non recensito
        bought = db_session.scalar(
            select(OrderProducts)
            .join(Order)
            .filter(Order.user_id == current_user.get_id())
            .filter(OrderProducts.product_id == pid)
            .filter(Order.confirmed == True)
        ) is not None and db_session.scalar(
            select(Review)
            .filter(Review.user_id == current_user.get_id())
            .filter(Review.product_id == item.id)
        ) is None

        return render_template('zoom_in.html', item=item, bought=bought)

    else:
        # Aggiungi al carrello
        if request.form.get('add-cart') is not None:
            if current_user.is_authenticated: 
                order_quantity = int(request.form.get('quantity'))
                item = db_session.scalar(select(Product).where(Product.id == pid))
                
                # Check server-side disponibilità
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
    
        # Posta recensione
        elif request.form.get('add-review') is not None:
            new_review = Review(
                product_id = pid,
                user_id = current_user.get_id(),
                review = request.form.get('review-content'),
                stars = int(request.form.get('review-stars')),
                date = datetime.datetime.now(),
            )
            db_session.add(new_review)
            db_session.commit()
            return redirect(url_for('product_details', pid=pid))
        
        # Elimina prodotto
        elif request.form.get('delete-prod') is not None and current_user.is_seller():
            # Check esistenza prodotto con id=pid e venduto dall'utente 
            item = db_session.scalar(
                select(Product)
                .filter(Product.id == pid)
                .filter(Product.user_id == current_user.get_id())
            )
            if item is not None:
                # Non si può rimuovere prodotto perché è presente in carrelli e ordini vecchi
                # invece settiamo disponibilità a 0 e la usiamo come "filtro"
                item.availability = 0
                db_session.commit()
            return redirect(url_for('home'))
        
        # Aggiorna prodotto
        elif request.form.get('update-prod') is not None and current_user.is_seller():
            return redirect(url_for('edit_listing', pid=pid))

@app.route('/edit-listing/<int:pid>', methods=['GET', 'POST'])
@login_required
def edit_listing(pid):
    item = db_session.scalar(
        select(Product)
        .filter(Product.id == pid)
        .filter(Product.user_id == current_user.get_id())
    )
    if item is None:
        return redirect(url_for('home'))

    if request.method == 'GET':
        tags = db_session.scalars(select(Tag)).all()
        # Prende tutti i valori dei tag correnti dell prodotto
        it_tags = [it.tag.value for it in item.tags]
        return render_template('update.html', item=item, tags=tags, it_tags=it_tags)

    else:
        # Aggiorna prodotto 
        if request.form.get('update') is not None:
            image_filename = item.image_filename
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file.filename != '' and file and allowed_file(file.filename):
                    # filename = secure_filename(file.filename)
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(path)
                    image_filename = file.filename

            item.product_name = request.form.get('name')
            item.brand = str(request.form.get('brand'))
            item.category_id = int(str(request.form.get('category')))
            item.size = request.form.get('size')
            item.price = Decimal(str(request.form.get('price')))
            item.availability = request.form.get('availability')
            item.descr = request.form.get('description')
            item.image_filename = image_filename
            
            # Tag inseriti nel form
            tags = request.form.getlist('tag')

            for i_t in item.tags:
                # Se tag corrente non presente nel form nuovo lo elimina
                if i_t.tag_id not in [int(tag) for tag in tags]:
                    db_session.delete(i_t)
            
            # Id dei tag correnti del prodotto
            it_tags = [i_t.tag.id for i_t in item.tags]
            for tag_id in tags:
                # Se tag nel form non presente in tag correnti lo aggiungo
                if int(tag_id) not in it_tags:
                    db_session.add_all([TagProduct(db_session.scalar(select(Tag).filter(Tag.id == tag_id)), item)])

            try:
                db_session.commit()    
            except Exception as e:
                flash(str(e), 'error')
                return redirect(request.url)

            return redirect(url_for('product_details', pid=pid))

        return redirect(url_for('home'))
    
@app.route('/search', methods=['GET', 'POST'])
def search():
    brands = db_session.scalars(select(Product.brand)).all()
    query = select(Product).distinct(Product.id).join(TagProduct).join(Tag)
    max_price = db_session.scalar(select(func.max(Product.price)))
    tags = db_session.scalars(select(Tag))

    if request.method == 'GET':
        items = db_session.scalars(query).all()
        return render_template('search.html', items=items, brands=brands, max_price=max_price, tags=tags)

    else:
        tag_list = request.form.getlist('tags')
        size = request.form.get('size')
        brand = request.form.get('brand')
        min_price_range = request.form.get('min_price_range')
        max_price_range = request.form.get('max_price_range')
        reviews_sort = request.form.get('reviews-sort')
        name_sort = request.form.get('name-sort')
        price_sort = request.form.get('price-sort')

        # I check servono perché potrebbe fare query cercando valori None tra gli attributi
        if tag_list:
            query = query.filter(Tag.id.in_(tag_list))
        if size and size != 'Any':
            query = query.filter(Product.size == size)
        if brand:
            query = query.filter(Product.brand == brand)
        if min_price_range:
            query = query.filter(Product.price >= min_price_range)
        if max_price_range:
            query = query.filter(Product.price <= max_price_range)
        # if reviews_sort:
        #     if reviews_sort == 'asc':
        #         query = query.order_by(Product.rating.asc())
        #     else:
        #         query = query.order_by(Product.rating.desc())
        if name_sort:
            if name_sort == 'asc':
                query = query.order_by(Product.product_name.asc())
            else:
                query = query.order_by(Product.product_name.desc())
        if price_sort:
            if price_sort == 'asc':
                query = query.order_by(Product.price.asc())
            else:
                query = query.order_by(Product.price.desc())
        items = db_session.scalars(query).all()

        return render_template('search.html', items=items, brands=brands, max_price=max_price, tags=tags)

# Controlla se il file è di tipo corretto (foto/gif)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# route per aggiunta di un nuovo prodotto
@app.route('/sell', methods=['GET', 'POST'])
@login_required # Indica che è richiesto un login per accedere a questa pagina, un login avvenuto con successo e quindi con un utente loggato
def sell():
    if not current_user.is_seller():
        return redirect(url_for('home'))

    # Upload dati nuovo prodotto
    if request.method == 'POST':
        if 'image_file' not in request.files:
            flash('No file attached', 'error')
            return redirect(request.url)

        # Upload dell'immagine del prodotto
        file = request.files['image_file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)

            tags = request.form.getlist('tag')

            try:
                product = Product(
                    user_id = current_user.get_id(),  # prende l'utente attualmente loggato (current_user)
                    brand = request.form.get('brand'),
                    category_id = int(request.form.get('category')),
                    size = request.form.get('size'),
                    product_name = request.form.get('name'),
                    date = datetime.datetime.now(),
                    price = Decimal(request.form.get('price')),
                    availability = int(request.form.get('availability')),
                    descr = request.form.get('description'),
                    image_filename = file.filename
                )

            except MissingData as err:
                flash(err.message, 'error')
                return redirect(request.url)
            except ValueError as err:
                flash(str(err), 'error')
                return redirect(request.url)
            
            # Per ogni tag scelto si aggiunge una riga alla tabella intermedia tag_products
            for tag_id in tags:
                db_session.add_all([TagProduct(db_session.scalar(select(Tag).filter(Tag.id == tag_id)), product)])

            try:
                db_session.add(product)
                db_session.commit()
            except Exception as e:
                flash(str(e), 'error')
                return redirect(request.url)

            return redirect(url_for('home'))

        else:
            flash('Invalid file type', 'error')
            return redirect(request.url)

    # Se richiesta GET
    else:
        # Renderizziamo la pagina in cui dovrà inserire i dettagli del prodotto
        tags = db_session.scalars(select(Tag)).all()
        return render_template('sell.html', tags=tags)

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
        # Aggiorna dati personali
        if request.form.get('info-update') is not None:
            current_user.name = request.form.get('info-fname')
            current_user.last_name = request.form.get('info-lname')
            current_user.email = request.form.get('info-email')
            db_session.commit()
        
        # Elimina indirizzo
        elif request.form.get('address-delete') is not None:
            db_session.delete(db_session.scalar(
                select(Address)
                .filter(Address.id == request.form.get('address-id'))
            ))
            db_session.commit()
        
        # Setta come indirizzo attivo
        elif request.form.get('address-set-active') is not None:
            # Indirizzo attivo al momento
            curr_active = db_session.scalar(
                select(Address)
                .filter(Address.user_id == current_user.get_id())
                .filter(Address.active == True)
            )
            if not curr_active.id == request.form.get('address-id'):
                curr_active.active = False
                # Setta indirizzo indicato nel form come attivo
                db_session.scalar(
                    select(Address)
                    .filter(Address.id == request.form.get('address-id'))
                ).active = True
                db_session.commit()

        # Aggiungi indirizzo
        elif request.form.get('address-add') is not None:
            # Se non sono presenti altri indirizzi attivi, active = True
            active = (db_session.scalar
                (select(Address)
                 .filter(Address.user_id == current_user.get_id())
                 .filter(Address.active == True)) is None)

            new_address = Address(
                user_id = current_user.get_id(),
                active = active,
                first_name = request.form.get('fname'),
                last_name = request.form.get('lname'),
                street = request.form.get('street'),
                postcode = request.form.get('post-code'),
                state = request.form.get('state'),
                city = request.form.get('city'),
                province = request.form.get('province')
            )
            db_session.add(new_address)
            db_session.commit()
        
        return redirect(url_for('profile'))

@app.route('/reviews-page') # solo metodo GET
@login_required
def reviews_page():
    if current_user.is_seller():
        # Prodotti del venditore
        product_rev = db_session.scalars(
            select(Product)
            .filter(Product.user_id == current_user.get_id())
        ).all()
        return render_template('reviews.html', reviews=product_rev)
    else:
        # Recensioni dell'utente
        reviews = db_session.scalars(
            select(Review)
            .filter(Review.user_id == current_user.get_id())
        ).all()
        return render_template('reviews.html', reviews=reviews)

@app.route('/user/<username>')
def user(username):
    user = db_session.scalar(select(User).where(User.username == str(username)))
    return render_template('user.html', user=user)

def clear_cart(user_id):
    db_session.execute(delete(CartProducts).where(CartProducts.user_id == user_id))

@app.route('/cart' , methods=['GET', 'POST'])
@login_required
def cart():
    if current_user.is_seller():
        return redirect(url_for('home'))
    
    # Prodotti nel carrello dell'utente
    products = db_session.scalars(
        select(CartProducts)
        .filter(CartProducts.user_id == int(current_user.get_id()))
    ).all()
    # Totale dei prodotti nel carrello
    total = sum(p.quantity * p.product.price for p in products)

    if request.method == 'GET':
        return render_template('cart.html', cart_items=products, total=total)

    else:
        # Pulisci carrello
        if request.form.get('clear-cart') is not None:
            clear_cart(current_user.get_id())
            return redirect(url_for('cart'))
        
        # Elimina prodotto
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
        
        # Effettua ordine
        elif request.form.get('place-order') is not None:
            if len(products) == 0:
                flash('There are no products in the cart', 'error')
                return redirect(request.url)
            else:
                return redirect(url_for('payment')) # fare in modo di passare la query già fatta senza doverla rifare in '/payment'?
        
        # Aggiorna quantità prodotto
        elif request.form.get('update-item') is not None:
            new_qty = int(request.form.get('quantity'))
            for prod in products:
                # Se quantità non supera disponibilità
                if prod.product_id == int(request.form.get('item-id')) and prod.product.availability > new_qty:
                    prod.quantity = new_qty
                    db_session.commit()
            return redirect(url_for('cart'))
             

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    products = db_session.scalars(
        select(CartProducts)
        .filter(CartProducts.user_id == int(current_user.get_id()))
    ).all()
    total = sum(p.quantity * p.product.price for p in products)

    if request.method == 'GET':
        address = db_session.scalar(
            select(Address)
            .filter(Address.user_id == int(current_user.get_id()))
            .filter(Address.active == True)
        )
        if address is None:
            flash('Impossible to send the order, at least 1 shipping address is needed', 'error')
            return redirect('cart')
        if products is None: # caso in cui dalla lista si elimina qualcosa
            flash('There are no products in the cart', 'error')
            return redirect('cart')
        return render_template('payment.html', cart_items=products, total=total, address=address)
    else:
        # Cancella ordine
        if request.form.get('cancel') is not None:
            return redirect(url_for('cart'))

        # Elimina prodotto
        elif request.form.get('delete-item') is not None:
            db_session.execute(
                    delete(CartProducts)
                    .where(CartProducts.product_id == request.form.get('item-id'))
                    .where(CartProducts.user_id == current_user.get_id())
            )
            return redirect(url_for('payment'))

        # Effettua ordine
        elif request.form.get('order') is not None:
            sellers_orders = {}
            pay_method = request.form.get('payment_method')
            try:
                for p in products:
                    if p.quantity > p.product.availability:
                        flash('Product quantity exceeds availability', 'error')
                        return redirect(url_for('cart'))

                    seller_id = p.product.user_id
                    date = datetime.datetime.now()
                    # Viene creato un ordine per ciascun venditore
                    if seller_id not in sellers_orders.keys():
                        new_order = Order(
                            user_id = current_user.get_id(),
                            date = date,
                            price = p.quantity * p.product.price,
                            address = db_session.scalar(
                                select(Address.id)
                                .filter(Address.user_id == current_user.get_id())
                                .filter(Address.active == True)
                            ),
                            payment_method = pay_method,
                            status = 'Paid',
                            status_time = date,
                            confirmed = False,
                        )
                        db_session.add(new_order)
                        db_session.flush() # aggiungiamo nel database la transazione in corso
                        sellers_orders[seller_id] = new_order # aggiungiamo al dizionario il venditore con il relativo ordine
                    
                    else:
                        sellers_orders[seller_id].price += (p.quantity * p.product.price)

                    new_order_product = OrderProducts( # gruppo di prodotti che erano nello stesso carrello
                        order_id = sellers_orders[seller_id].id,
                        product_id = p.product_id,
                        quantity = p.quantity,
                    )
                    db_session.add(new_order_product)

            except InvalidOrder as err:
                flash(err, 'error')
                return redirect(request.url)

            db_session.commit()

            for p in products:
                p.product.availability -= p.quantity # finito l'ordine riduciamo la quantità di prodotti disponibile
                # if p.product.availability == 0:
                #     db_session.execute(delete(Product).where(Product.id == p.product.id)) # se la disponibilità del prodotto va a 0 lo togliamo dal database
            clear_cart(current_user.get_id())
            return redirect(url_for('home'))

@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    curr_time = datetime.datetime.now()

    if request.method == 'GET':
        # Se utente non venditore
        if not current_user.is_seller():
            orders = db_session.scalars(
                select(Order)
                .filter(Order.user_id == current_user.get_id())
                .order_by(Order.date.desc())
            )
            
            # La data dal cui calcolare le notifiche parte dall'ultimo logout
            # se non è ancora stata controllata la pagina
            date = session["last_check"] if "last_check" in session.keys() else current_user.last_logout
            # Prendo id ordini aggiornati dopo ultimo controllo degli ordini
            notifs = db_session.scalars(
                select(Order.id)
                .filter(Order.user_id == current_user.get_id())
                .filter(date < Order.status_time)
                .filter(Order.confirmed == False)
                .order_by(Order.status_time)
            )
            # Si aggiorna il timestamp dell'ultimo controllo al tempo corrente
            session["last_check"] = datetime.datetime.now()

            return render_template('orders.html', orders=orders, now=curr_time, notifs=notifs)

        else:
            orders = db_session.scalars(
                select(Order)
                .distinct(Order.id) # Altrimenti con la join ritorna più volte lo stesso prodotto
                .join(OrderProducts)
                .join(Product)
                .filter(Product.seller == current_user)
                .order_by(Order.date.desc())
            )
            return render_template('orders_sold.html', orders=orders, now=curr_time)
    
    # Richiesta POST per aggiornamento stato
    else:
        if request.form.get('update-status') is not None and current_user.is_seller():
            new_status = request.form.get('new-status')
            order_id = request.form.get('order-id')

            # Se nuovo stato valido
            if not new_status or new_status not in ['Received', 'Sent', 'Processing', 'Cancelled']:
                return redirect(url_for('orders'))
            
            # Query per ordine con certo id e venduto dall'utente corrente
            order = db_session.scalar(select(Order).join(OrderProducts).join(Product).filter(Order.id == order_id).filter(Product.seller == current_user))
            if order is None:
                return redirect(url_for('orders'))
           
            # Se nuovo stato diverso da prima e non ricevuto o cancellato, lo aggiorna 
            if order.status not in [new_status, 'Received', 'Cancelled']:
                order.status = new_status
                order.status_time = datetime.datetime.now()
                db_session.commit()

        elif not current_user.is_seller():
            # Conferma ricezione ordine
            if request.form.get('update-confirmed') is not None:
                order_id = request.form.get('order-id')
                order = db_session.scalar(
                    select(Order)
                    .filter(Order.id == order_id)
                    .filter(Order.user_id == current_user.get_id())
                    .filter(Order.status == 'Received')
                    .filter(Order.confirmed == False)
                )
                if order is not None:
                    order.confirmed = True
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

@app.route('/logout')
@login_required # Indica che è richiesto un login per accedere a questa pagina, un login avvenuto con successo e quindi con un utente loggato
def logout():
    current_user.last_logout = datetime.datetime.now()
    db_session.commit()
    logout_user()
    return redirect(url_for('home'))

# route per la registrazione
@app.route('/signup', methods=['GET','POST'])
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

        return redirect(url_for('login'))
    else:
        return render_template('signup.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)


