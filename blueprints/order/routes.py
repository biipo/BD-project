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

from . import order_bp
from tables import User, Product, Base, Product, User, Category, Address, CartProducts, Order, OrderProducts, Tag, TagProduct, Review
from config import Base, engine, db_session, app, login_manager, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, bcrypt
from exceptions import InvalidCredential, InvalidOrder, MissingData


@order_bp.route('/payment', methods=['GET', 'POST'])
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
            return redirect(url_for('cart'))
        if products is None: # caso in cui dalla lista si elimina qualcosa
            flash('There are no products in the cart', 'error')
            return redirect(url_for('cart'))
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
            return redirect(url_for('order.payment'))

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
                        try:
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
                        except InvalidOrder:
                            pass
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
            db_session.execute(delete(CartProducts).where(CartProducts.user_id == current_user.get_id()))
            return redirect(url_for('home'))

@order_bp.route('/orders', methods=['GET', 'POST'])
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
                return redirect(url_for('order.orders'))
            
            # Query per ordine con certo id e venduto dall'utente corrente
            order = db_session.scalar(
                select(Order)
                .join(OrderProducts)
                .join(Product)
                .filter(Order.id == order_id)
                .filter(Product.seller == current_user)
            )
            if order is None:
                return redirect(url_for('order.orders'))
           
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

        return redirect(url_for('order.orders'))