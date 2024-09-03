from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base
import pytz
from datetime import datetime

# Define the IST time zone
IST = pytz.timezone('Asia/Kolkata')

# Function to get the current time in IST
def get_current_time_ist():
    return datetime.now(IST)

class ContactForm(Base):
    __tablename__ = 'contact_forms'

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100))
    email = Column(String(100), unique=True)
    gender = Column(String(10))
    newsletter = Column(Boolean)
    comment = Column(String(500))

class DeletedContactForm(Base):
    __tablename__ = 'deleted_contact_forms'

    id = Column(Integer, primary_key=True)
    fullname = Column(String(100))
    email = Column(String(100))
    gender = Column(String(10))
    newsletter = Column(Boolean)
    comment = Column(String(500))
    deleted_at = Column(DateTime, default=get_current_time_ist())
