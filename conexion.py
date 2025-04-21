from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from pydantic import BaseModel  

URL_DB = "mysql+mysqlconnector://root:1123038259@127.0.0.1:3306/consultorio"

crear = None
Sessionlocal = None

try:
    crear = create_engine(URL_DB)
    Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=crear)
except OperationalError as e:
    print(f"⚠️ No se pudo conectar a la base de datos: {e}")
    # Opcional: Loggear más o dejarlo en silencio
    Sessionlocal = None

base = declarative_base()

def get_db():
    if Sessionlocal is None:
        print("⚠️ No hay conexión a la base de datos. get_db no devolverá nada.")
        return  # O podrías hacer yield None si quieres
    cnn = Sessionlocal()
    try:
        yield cnn
    finally:
        cnn.close()