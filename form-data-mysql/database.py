from sqlalchemy import create_engine  # Import the function to create the database engine
from sqlalchemy.ext.declarative import declarative_base  # Import the base class for models
from sqlalchemy.orm import sessionmaker  # Import the function to create a session

DATABASE_URL = "mysql+pymysql://root:root123@localhost/User_Data"  # Define the database connection URL

engine = create_engine(DATABASE_URL)  # Create a database engine using the connection URL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Create a session factory, with the engine bound to it
Base = declarative_base()  # Create a declarative base class for models to inherit from
