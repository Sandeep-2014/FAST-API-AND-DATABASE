from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = "mysql+pymysql://root:8287994601@localhost/BlogApplication"


engine = create_engine(URL_DATABASE)

SessinLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()