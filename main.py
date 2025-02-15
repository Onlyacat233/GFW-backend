from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from utils import schemas, crud
from utils.config import load_env
from utils.database import Base, engine, SessionLocal

load_env()

Base.metadata.create_all(bind=engine)

app = FastAPI()

class InternalError(Exception):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    except InternalError:
        db.close()


@app.get("/")
def root():
    return {
        "version": "v1",
        "data": "Hello World"
    }


@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db=db, user=user)


@app.get("/users", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
