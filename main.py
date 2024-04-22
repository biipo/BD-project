from tables import *
from sqlalchemy import *
from sqlalchemy.orm import *
import os.path

def main():
    if not os.path.exists('data.db'): # Se non esiste il file del database lo crea
        Base.metadata.create_all(engine)
    Categories.__table__

if __name__ == '__main__':
    main()
