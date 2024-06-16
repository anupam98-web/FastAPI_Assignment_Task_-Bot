# schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

# Pydantic models for Person
class PersonBase(BaseModel):
    first_name: str
    last_name: str
    email: str

class PersonCreate(PersonBase):
    password: str

class Person(PersonBase):
    id: int

    class Config:
        orm_mode = True

class PersonResponse(PersonBase):
    id: int

    class Config:
        orm_mode = True

# Pydantic models for Category
class CategoryBase(BaseModel):
    title: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# Pydantic models for Transaction
class TransactionBase(BaseModel):
    amount: float
    note: str
    transaction_date: date

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    category_id: int

    class Config:
        orm_mode = True



"""
SQLAlchemy and many others are by default "lazy loading".

That means, for example, that they don't fetch the data for relationships from the database unless you try to access the attribute that would contain that data.

This way, instead of only trying to get the id value from a dict, as in:


id = data["id"]
it will also try to get it from an attribute, as in:


id = data.id
"""