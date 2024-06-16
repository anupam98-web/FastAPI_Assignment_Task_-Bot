from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import models, crud, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# class User(BaseModel):
#     username: str
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None


# class UserInDB(User):
#     hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login/")

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)




def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.Person).filter(models.Person.email == username).first()
    hash_password = get_password_hash(password)
    if not user:
        return False
    if not verify_password(user.password, hash_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    # user = get_user(fake_users_db, username=token_data.username)
    db = SessionLocal()
    user = db.query(models.Person).filter(models.Person.email == username).first()
    db.close()    
    print(user.id, user.email)
    if user is None:
        raise credentials_exception
    return user


# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user



@app.get('/getAllUsers', response_model=list[schemas.PersonResponse])
async def get_all_user(db: Session = Depends(get_db)):
     return crud.get_all_user(db)

# @app.post("/token")
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
# ) -> Token:
#     # db = SessionLocal()
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.email}, expires_delta=access_token_expires
#     )
#     return Token(access_token=access_token, token_type="bearer")

@app.post("/api/users/login/")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    # db = SessionLocal()
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# Endpoint to register a new user
@app.post("/api/users/register/", response_model=schemas.Person)
def register_new_user(user: schemas.PersonCreate, db: Session = Depends(get_db)):
    print(user, db)
    return crud.register_new_user(db, user)

# Category endpoints

@app.get("/api/categories/", response_model=list[schemas.Category])
def read_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    categories = crud.get_categories(db, current_user.id)
    return categories[skip: skip + limit]

@app.get("/api/categories/{category_id}", response_model=schemas.Category)
def read_category(category_id: int, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    db_category = crud.get_category_by_id(db, category_id, current_user.id)
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with id {category_id} not found")
    return db_category

@app.post("/api/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    return crud.create_category(db, category, current_user.id)

@app.put("/api/categories/{category_id}", response_model=schemas.Category)
def update_category(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    return crud.update_category(db, category_id, category)

@app.delete("/api/categories/{category_id}", response_model=dict)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    return crud.delete_category(db, category_id)

# Transaction endpoints

@app.get("/api/categories/{category_id}/transactions/", response_model=list[schemas.Transaction])
def read_transactions(category_id: int, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    transactions = crud.get_transactions_by_category(db, category_id)
    return transactions

@app.get("/api/categories/{category_id}/transactions/{transaction_id}", response_model=schemas.Transaction)
def read_transaction(category_id: int, transaction_id: int, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    transaction = crud.get_transaction_by_id_and_category(db, category_id, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with id {transaction_id} in category {category_id} not found")
    return transaction

@app.post("/api/categories/{category_id}/transactions/", response_model=schemas.Transaction)
def create_transaction(category_id: int, transaction: schemas.TransactionCreate, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    return crud.create_transaction(db, transaction, category_id, current_user.id)

@app.put("/api/categories/{category_id}/transactions/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(category_id: int, transaction_id: int, transaction: schemas.TransactionCreate, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    return crud.update_transaction(db, category_id, transaction_id, transaction)

@app.delete("/api/categories/{category_id}/transactions/{transaction_id}", response_model=dict)
def delete_transaction(category_id: int, transaction_id: int, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    return crud.delete_transaction(db, category_id, transaction_id)


# ----------- Doc ------------------
# @app.get("/users/me/", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user


# @app.get("/users/me/items/")
# async def read_own_items(current_user: User = Depends(get_current_active_user)):
#     return [{"item_id": "Foo", "owner": current_user.username}]