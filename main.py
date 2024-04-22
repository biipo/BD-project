from flask import Flask, render_template
from tables import Base, Categories
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os.path

app = Flask(__name__, template_folder='templates')
engine = create_engine('sqlite:///data.db', echo=True)

def data_insertion():
    Session = sessionmaker(engine)
    session = Session()
    # session.add_all([Products(),
    #                  Products(),
    #                  Products(),
    #                  Products() ])   

    session.add_all([ Categories(id=1, name='Arts'),
                                 Categories(id=2, name='Personal Care'),
                                 Categories(id=3, name='Eletronics'),
                                 Categories(id=4, name='Music'),
                                 Categories(id=5, name='Sports'),
                                 Categories(id=6, name='Movies & TV'),
                                 Categories(id=7, name='Software'),
                                 Categories(id=8, name='Games'),
                                 Categories(id=9, name='House'),
                                 Categories(id=10, name='DIY'), ])

    session.commit()

def main():
    if not os.path.exists('data.db'): # Se non esiste il file del database lo crea
        Base.metadata.create_all(engine)
    # Categories.__table__

@app.route('/')
def start():
    return render_template('index.html')



if __name__ == '__main__':
    main()
    app.run(host='127.0.0.1', debug=True)
