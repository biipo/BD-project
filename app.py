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

from config import Base, engine, db_session, app, login_manager, UPLOAD_FOLDER, ALLOWED_EXTENSIONS

from blueprints.auth.routes import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
from blueprints.order.routes import order_bp
app.register_blueprint(order_bp, url_prefix='/order')
from blueprints.product.routes import product_bp
app.register_blueprint(product_bp, url_prefix='/product') 

Base.metadata.create_all(engine)

def db_init():
    # Serve per inserire nel database i tag e le categorie, ma solo nel caso in cui non è già presente il file .db con questi dati
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
            Tag(value='Red'),
            Tag(value='Blue'),
            Tag(value='Green'),
            Tag(value='Yellow'),
            Tag(value='Orange'),
            Tag(value='Purple'),
            Tag(value='Pink'),
            Tag(value='Brown'),
            Tag(value='Black'),
            Tag(value='White'),
            Tag(value='Gray'),
            Tag(value='Beige'),
            Tag(value='Maroon'),
            Tag(value='Navy'),
            Tag(value='Teal'),
            Tag(value='Turquoise'),
            Tag(value='Lavender'),
            Tag(value='Magenta'),
            Tag(value='Cyan'),
            Tag(value='Lime'),
        ])
        db_session.commit()

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

@app.route('/search', methods=['GET', 'POST'])
def search():
    brands = db_session.scalars(select(Product.brand)).all()
    query = select(Product).distinct(Product.id).join(TagProduct).join(Tag).join(Category)
    max_price = db_session.scalar(select(func.max(Product.price)))
    tags = db_session.scalars(select(Tag)).all()
    categories = db_session.scalars(select(Category)).all()

    if request.method == 'GET':
        items = db_session.scalars(query).all()
        return render_template('search.html', items=items, brands=brands, max_price=max_price, tags=tags, categories=categories)

    else:
        tag_list = request.form.getlist('tags')
        size = request.form.get('size')
        brand = request.form.get('brand')
        min_price_range = request.form.get('min_price_range')
        max_price_range = request.form.get('max_price_range')
        reviews_sort = request.form.get('reviews-sort')
        name_sort = request.form.get('name-sort')
        price_sort = request.form.get('price-sort')
        category = request.form.get('category')

        # I check servono perché potrebbe fare query cercando valori None tra gli attributi
        # a seconda di quale valore NON è none viene estesa la query con WHERE o ORDER BY
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
        if category and category != 'Any':
            query = query.filter(Category.id == category)
        if reviews_sort:
            if reviews_sort == 'asc':
                query = query.order_by(Product.rating.asc())
            else:
                query = query.order_by(Product.rating.desc())
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

        return render_template('search.html', items=items, brands=brands, max_price=max_price, tags=tags, categories=categories)
    
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

            try:
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
            except ValueError as err:
                flash(str(err), 'error')
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
                return redirect(url_for('order.payment')) # fare in modo di passare la query già fatta senza doverla rifare in '/payment'?
        
        # Aggiorna quantità prodotto
        elif request.form.get('update-item') is not None:
            new_qty = int(request.form.get('quantity'))
            for prod in products:
                # Se quantità non supera disponibilità
                if prod.product_id == int(request.form.get('item-id')) and prod.product.availability > new_qty:
                    prod.quantity = new_qty
                    db_session.commit()
            return redirect(url_for('cart'))

@login_manager.user_loader
def load_user(user_id):
    return db_session.scalar(select(User).where(User.id == int(user_id))) # Dovrebbe ritornare 'None' se l'ID non è valido

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)


