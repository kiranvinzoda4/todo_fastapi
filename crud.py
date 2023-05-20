from sqlalchemy.orm import Session
from typing import Union
import models
import schemas
import uuid
from auth import AuthHandler
auth_handler = AuthHandler()



def generate_id():
    id = str(uuid.uuid4())
    return id


def user_varification(db: Session, token : str):
    result_id = auth_handler.decode_token(token)
    user_record = db.query(models.User).filter(models.User.id == result_id).first()
    if user_record is not None:
        return True
    else:
        return False

def get_user_by_token(db: Session, token : str):
    result_id = auth_handler.decode_token(token)
    user_record = db.query(models.User).filter(models.User.id == result_id).first()
    return user_record
         


def get_todo(db: Session, todo_id: str, token : str):
    user = get_user_by_token(db, token)
    return db.query(models.Todo).filter(models.Todo.id == todo_id , models.Todo.is_active == True, models.Todo.owner == user.id).first()


def get_todo_by_id(db: Session, id: str):
    return db.query(models.Todo).filter(models.Todo.id == id, models.Todo.is_active == True).first()


def get_all_todos(db: Session, token : str, offset : int, limit : int):
    user = get_user_by_token(db, token)
    return db.query(models.Todo).filter(models.Todo.is_active == True, models.Todo.owner == user.id).offset(offset).limit(limit).all()


def create_todo(db: Session, todo_id : str, todo: schemas.Create_Todo, token= str, img_path= str):
    
    user = get_user_by_token(db , token = token)
    db_todo = models.Todo(id = todo_id, title=todo.title, desc=todo.desc, owner=user.id, img = img_path)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: str, todo: schemas.Create_Todo, file_location : Union[str, None] = None):
    if file_location != None :
        db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.is_active == True).first()
        db_todo.title = todo.title
        db_todo.desc = todo.desc
        db_todo.img = file_location
        db.commit()
    else:
        db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.is_active == True).first()
        db_todo.title = todo.title
        db_todo.desc = todo.desc
        db_todo.img = None
        db.commit()
    return db_todo

def delete_todo(db: Session, todo_id: str):
    
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.is_active == True).first()
    db_todo.is_active = False
    db_todo = db.commit()
    return True

def get_todo_by_search_key(db: Session, search_key: str):
    search = "%{}%".format(search_key)
    return db.query(models.Todo).filter(models.Todo.desc.like(search)).all()


def create_user(db: Session, user: schemas.Create_Usr ,password: str):
    
    user_id = generate_id()
    db_user = models.User(id = user_id,name=user.name, email=user.email,password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session):
    return db.query(models.User).filter(models.User.is_active == True).all()

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id , models.User.is_active == True).first()

def get_user_by_email(db: Session, user_email : str):
    test= db.query(models.User).filter(models.User.email == user_email , models.User.is_active == True).first()

    return test















