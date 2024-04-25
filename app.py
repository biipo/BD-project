from flask import Flask, redirect, render_template, request
from tables import Users, Base, Categories
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os.path

app = Flask(__name__, template_folder='templates')
engine = create_engine('sqlite:///data.db', echo=True)

Session = sessionmaker(engine)
session = Session()

# def db_init():
#     session.add_all([ Categories(id=1, name='Arts'),
#                                  Categories(id=2, name='Personal Care'),
#                                  Categories(id=3, name='Eletronics'),
#                                  Categories(id=4, name='Music'),
#                                  Categories(id=5, name='Sports'),
#                                  Categories(id=6, name='Movies & TV'),
#                                  Categories(id=7, name='Software'),
#                                  Categories(id=8, name='Games'),
#                                  Categories(id=9, name='House'),
#                                  Categories(id=10, name='DIY'), ])

#     session.commit()

def main():
    app.run(host='127.0.0.1', debug=True)

@app.route('/')
def start():
    Base.metadata.create_all(engine)
    return redirect('/prova', code=302)


# ---------------------- METODO DA RIMUOVERE, SOLO PER PROVA DELLE QUERY
@app.route('/prova', methods=['GET', 'POST'])
def prova():
    if request.method == 'POST':
        id = request.form.get('id')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        last_name = request.form.get('last_name')

        user = Users(id=id, email=email, username=username, password=password, name=name, last_name=last_name, user_type=False)
        session.add(user)
        session.commit()
        users = session.query(Users).all()
        return render_template('index.html', users=users)
    else:
        users = session.query(Users).all()
        return render_template('index.html', users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        # if 'email' in request.args and 'password' in request.args:
        email = request.form.get('email')
        password = request.form.get('password')
        if email == 'admin' and password == 'admin':
            return f"The email: {email} and password: {password}"
        else:
            return redirect('/login', code=302)
    else:
        return "Nooooooo"



if __name__ == '__main__':
    main()
