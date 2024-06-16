from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from . import models, schemas

# User CRUD operations

def register_new_user(db: Session, user: schemas.PersonCreate):
    try:
        print('--->',user.dict())
        db_user = models.Person(**user.dict())
        print(db_user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with given email already exists")

def get_all_user(db: Session):
    try:
        users = db.query(models.Person).all()
        return users
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user found")

# Category CRUD operations

def get_categories(db: Session, user_id: int):
    # return db.query(models.Category).all()
    return db.query(models.Category).filter(models.Category.user_id == user_id)

def get_category_by_id(db: Session, category_id: int, user_id: int):
    return db.query(models.Category).filter(models.Category.user_id == user_id).filter(models.Category.id == category_id).first()

def create_category(db: Session, category: schemas.CategoryCreate,  user_id: int):
    try:
        db_category = models.Category(**category.dict(), user_id= user_id)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with given id does not exist")

def update_category(db: Session, category_id: int, category: schemas.CategoryCreate):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db_category.title = category.title
        db_category.description = category.description
        db.commit()
        db.refresh(db_category)
        return db_category
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with id {category_id} not found")

def delete_category(db: Session, category_id: int):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
        return {"message": f"Category with id {category_id} deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with id {category_id} not found")

# Transaction CRUD operations

def get_transactions_by_category(db: Session, category_id: int):
    return db.query(models.Transaction).filter(models.Transaction.category_id == category_id).all()

def get_transaction_by_id_and_category(db: Session, category_id: int, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.category_id == category_id, models.Transaction.id == transaction_id).first()

def create_transaction(db: Session, transaction: schemas.TransactionCreate, category_id: int, user_id: int):
    try:
        db_transaction = models.Transaction(**transaction.dict(), category_id=category_id, user_id = user_id)
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User or Category with given id does not exist")

def update_transaction(db: Session, category_id: int, transaction_id: int, transaction: schemas.TransactionCreate):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.category_id == category_id, models.Transaction.id == transaction_id).first()
    if db_transaction:
        db_transaction.amount = transaction.amount
        db_transaction.note = transaction.note
        db_transaction.transaction_date = transaction.transaction_date
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with id {transaction_id} in category {category_id} not found")

def delete_transaction(db: Session, category_id: int, transaction_id: int):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.category_id == category_id, models.Transaction.id == transaction_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
        return {"message": f"Transaction with id {transaction_id} in category {category_id} deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with id {transaction_id} in category {category_id} not found")
