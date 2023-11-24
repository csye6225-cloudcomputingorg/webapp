from sqlalchemy import DateTime, Column, Integer, String, Sequence, VARBINARY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = Column(String(50), unique=False, nullable=False)
    last_name = Column(String(50), unique=False, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(VARBINARY(255), unique=True, nullable=False)
    account_created = Column(DateTime, unique=False, nullable=False)
    account_updated = Column(DateTime, unique=False, nullable=False)
    
class Assignment(Base):
    __tablename__ = 'assignments'
    
    id = Column(String(255), unique=True, primary_key=True)
    name = Column(String(50), unique=False, nullable=False)
    points = Column(Integer, unique=False, nullable=False)
    num_of_attempts = Column(Integer, unique=False, nullable=False)
    num_of_submission = Column(Integer, unique=False, nullable=False)
    deadline = Column(String(100), unique=False, nullable=False)
    assignment_created = Column(DateTime, unique=False, nullable=False)
    assignment_updated = Column(DateTime, unique=False, nullable=False)
    owner = Column(String(100), nullable=False)
