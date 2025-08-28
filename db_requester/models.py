from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserDBModel(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    email = Column(String)
    full_name = Column(String)
    password = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    verified = Column(Boolean)
    banned = Column(Boolean)
    roles = Column(String)

class MovieDBModel(Base):
    __tablename__ = 'movies'
    id = Column(String, primary_key=True)
    name: Column[str] = Column(String, nullable=False)
    description = Column(String)
    price = Column(Integer, nullable=False)
    genre_id = Column(String, ForeignKey('genres.id'), nullable=False)
    image_url = Column(String)
    location = Column(String)
    rating = Column(Integer)
    published = Column(Boolean)
    created_at = Column(DateTime)

class AccountTransactionTemplate(Base):
    __tablename__ = 'accounts_transaction_template'
    user = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False)
