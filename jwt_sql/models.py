from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Text, DECIMAL, BigInteger, Date
from sqlalchemy.orm import relationship

from .database import Base


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    email = Column(String(30), nullable=False)
    password = Column(Text, nullable=False)

    # Establish a relationship with the Category table
    categories = relationship("Category", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("person.id"), nullable=False)
    title = Column(String(30), nullable=False)
    description = Column(String(255))

    # Establish a relationship with the Person table
    user = relationship("Person", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("person.id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    note = Column(String(30), nullable=False)
    transaction_date = Column(Date, nullable=False)

    category = relationship("Category", back_populates="transactions")
    user = relationship("Person", back_populates="transactions")




"""
When accessing the attribute items in a User, as in my_user.items, it will have a list of Item SQLAlchemy models (from the items table) that have a foreign key pointing to this record in the users table.

When you access my_user.items, SQLAlchemy will actually go and fetch the items from the database in the items table and populate them here.

And when accessing the attribute owner in an Item, it will contain a User SQLAlchemy model from the users table. It will use the owner_id attribute/column with its foreign key to know which record to get from the users table.
"""