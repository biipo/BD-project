from decimal import Decimal
from flask import Flask, redirect, render_template, request, session, url_for, flash, send_from_directory
from sqlalchemy.engine import url
from sqlalchemy import create_engine, select, join, union, update, func, delete, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base, contains_eager, aliased
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import datetime
import os.path

from . import product_bp
from tables import User, Product, Base, Product, User, Category, Address, CartProducts, Order, OrderProducts, Tag, TagProduct, Review
from config import Base, engine, db_session, app, login_manager, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, bcrypt
from exceptions import InvalidCredential, InvalidOrder, MissingData

@product_bp.route('/product-details/<int:pid>', methods=['GET', 'POST'])
def product_details(pid):
    if request.method == 'GET':
        item = db_session.scalar(select(Product).filter(Product.id == pid))
        if item is None:
            return redirect(url_for('home'))

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
                    new_cart_item = CartProducts(product=item, quantity=order_quantity, user=current_user)
                else:
                    flash('Invalid quantity selected', 'error')
                    return redirect(url_for('product.product_details', pid=item.id))

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
                return redirect(url_for('auth.login'))
    
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
            return redirect(url_for('product.product_details', pid=pid))
        
        # Elimina prodotto
        elif request.form.get('delete-prod') is not None and current_user.is_seller():
            # Check esistenza prodotto con id=pid e venduto dall'utente 
            item = db_session.scalar(
                select(Product)
                .filter(Product.id == pid)
                .filter(Product.user_id == current_user.get_id())
            )
            if item is not None:
                # Impostiamo la disponibilità a 0 e la usiamo come "filtro"
                item.availability = 0
                db_session.commit()
            return redirect(url_for('home'))
        
        # Aggiorna prodotto
        elif request.form.get('update-prod') is not None and current_user.is_seller():
            return redirect(url_for('product.edit_listing', pid=pid))

@product_bp.route('/edit-listing/<int:pid>', methods=['GET', 'POST'])
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
        categories = db_session.scalars(select(Category)).all()
        return render_template('update.html', item=item, tags=tags, it_tags=it_tags, categories=categories)

    else:
        # Aggiorna prodotto 
        if request.form.get('update') is not None:
            image_filename = item.image_filename
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file.filename != '' and file and allowed_file(file.filename):
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
                    db_session.add_all([TagProduct(tag=db_session.scalar(select(Tag).filter(Tag.id == tag_id)), product=item)])

            try:
                db_session.commit()    
            except Exception as e:
                flash(str(e), 'error')
                return redirect(request.url)

            return redirect(url_for('product.product_details', pid=pid))

        return redirect(url_for('home'))

@product_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
# Controlla se il file è di tipo corretto (foto/gif)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# route per aggiunta di un nuovo prodotto
@product_bp.route('/sell', methods=['GET', 'POST'])
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
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)

            tags = request.form.getlist('tag')

            try:
                product = Product(
                    user_id = current_user.get_id(),  # prende l'utente attualmente loggato (current_user)
                    brand = request.form.get('brand'),
                    category = db_session.scalar(select(Category).filter(Category.id == int(request.form.get('category')))),
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
                db_session.add_all([TagProduct(tag=db_session.scalar(select(Tag).filter(Tag.id == tag_id)), product=product)])

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

    else:
        # Renderizziamo la pagina in cui dovrà inserire i dettagli del prodotto
        tags = db_session.scalars(select(Tag)).all()
        categories = db_session.scalars(select(Category)).all()
        return render_template('sell.html', tags=tags, categories=categories)
