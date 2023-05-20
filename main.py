from typing import List,  Union
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Header
from sqlalchemy.orm import Session
import database
from models import User, Todo
from fastapi.middleware.cors import CORSMiddleware
import schemas
import models
import crud
from auth import AuthHandler
from fastapi import FastAPI, File, UploadFile, Form
import base64

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()
auth_handler = AuthHandler()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.post("/add_todo/", tags=["todo"], response_model=schemas.Show_Todo)
# def create_todo(todo: schemas.Create_Todo = Depends(), file: UploadFile = File(...),db: Session = Depends(get_db), token: str = Header(None)):
#     check = crud.user_varification(db, token= token )
#     if check:
#         file_location = f"files/{file.filename}"
#         with open(file_location, "wb+") as file_object:
#             file_object.write(file.file.read())
#             return crud.create_todo(db=db, todo=todo, token= token)
#     else:
#         raise HTTPException(status_code=404, detail="Token not valid")  


@app.post("/add_todo/", tags=["todo"], response_model=schemas.Show_Todo)
def create_todo(todo: schemas.Create_Todo , db: Session = Depends(get_db),token: str = Header(None)):
    check = crud.user_varification(db, token= token )
    if check:
        file_name = ''
        if todo.img != None:
            head, data = todo.img.split(',', 1)
            file_ext = head.split(';')[0].split('/')[1]
            plain_data = base64.b64decode(data)
            file_name = crud.generate_id()
            file_location = f"files/{file_name}."
            with open(file_location + file_ext, 'wb') as f:
                print(file_location)
                f.write(plain_data)
            img_path = "files/"+file_name+"."+file_ext 
        else:
            file_name = crud.generate_id()
            img_path = None    
        return crud.create_todo(db=db,todo_id = file_name, todo=todo, token= token, img_path = img_path)  
    else:
        raise HTTPException(status_code=404, detail="Token not valid")  

@app.get("/show_todos/", tags=["todo"], response_model=List[schemas.Show_Todo])
def read_todos(db: Session = Depends(get_db), offset: int = 0, limit: int = 100, token: str = Header(None)):
    print(token)
    check = crud.user_varification(db, token= token )
    if check:
        todo_list = crud.get_all_todos(db, token= token, limit = limit, offset = offset )
        for todo in todo_list:
            if todo.img != None:
                with open(todo.img, "rb") as image2string:
                    converted_string =  'data:image/jpg;base64,'+base64.b64encode(image2string.read()).decode()
                todo.img = converted_string
            else:
                todo.img = None
        return todo_list    
    else:
        raise HTTPException(status_code=404, detail="Token not valid")          


@app.get("/get_todo/{todo_id}", tags=["todo"], response_model=schemas.Show_Todo)
def read_todo(todo_id: str, db: Session = Depends(get_db), token: str = Header(None)):
    check = crud.user_varification(db, token= token )
    if check:
        db_todo = crud.get_todo(db, todo_id=todo_id, token= token)
        if db_todo.img != None:
            with open(db_todo.img, "rb") as image2string:
                converted_string =  'data:image/jpg;base64,'+base64.b64encode(image2string.read()).decode()
            db_todo.img = converted_string
        else:
            db_todo.img = None
        if db_todo is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        return db_todo
    else:
        raise HTTPException(status_code=404, detail="Token not valid") 
        
    

@app.put("/update_todo/{todo_id}", tags=["todo"], response_model=schemas.Show_Todo)
def put_todo(todo_id: str, todo: schemas.Create_Todo, db: Session = Depends(get_db), token: str = Header(None)):
    check = crud.user_varification(db, token= token )
    if check:
        db_todo = crud.get_todo(db, todo_id=todo_id, token= token)

        if todo.img != "":
            head, data = todo.img.split(',', 1)
            file_ext = head.split(';')[0].split('/')[1]
            plain_data = base64.b64decode(data)
            if db_todo.img == None:
                file_location = "files/"+db_todo.id+"."+file_ext 
                print(file_location)
                img_url = file_location   
            else:
                file_location = db_todo.img
                
            with open(file_location, 'wb') as f:
                f.write(plain_data)  
        else:
            file_location = None  
            print(file_location) 
        update_tod = crud.update_todo(db, todo_id=todo_id, todo = todo, file_location = file_location)  
        if db_todo is None:
            raise HTTPException(status_code=404, detail="User not found")
        return update_tod      
    else:
        raise HTTPException(status_code=404, detail="Token not valid") 


@app.delete("/delete_todo/{todo_id}", tags=["todo"])
def read_todo(todo_id: str, db: Session = Depends(get_db), token : str = Header(None)):
    check = crud.user_varification(db, token= token )
    if check:
        db_todo = crud.get_todo(db, todo_id=todo_id, token= token)
        if db_todo is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        db_todo = crud.delete_todo(db, todo_id=todo_id)
        if db_todo:
            raise HTTPException(status_code=404, detail="Todo deleted succesfully")
    else:
        raise HTTPException(status_code=404, detail="Token not valid")  



@app.get("/search_todo_by_key/{search_key}", tags=["todo"], response_model=List[schemas.Show_Todo])
def search_todo_by_key(search_key: str, db: Session = Depends(get_db), token: str = Header(None)):
    check = crud.user_varification(db, token= token )
    if check:
        todo_list = crud.get_todo_by_search_key(db, search_key=search_key)
        for todo in todo_list:
            with open(todo.img, "rb") as image2string:
                converted_string =  'data:image/jpg;base64,'+base64.b64encode(image2string.read()).decode()
            todo.img = converted_string
        print(todo_list)    
        return todo_list
        if todo_list is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        
    else:
        raise HTTPException(status_code=404, detail="Token not valid") 


@app.get("/show_users/", tags=["user"], response_model=List[schemas.Show_User])
def read_users(db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    return users


#jwt tokan



@app.post('/user_register', tags=["user"], status_code=201)
def register(user: schemas.Create_Usr , db: Session = Depends(get_db)):
    user_record = crud.get_user_by_email(db=db, user_email=user.email)
    if  user_record is not None :
        raise HTTPException(status_code=400, detail='email is taken')
    hashed_password = auth_handler.get_password_hash(user.password)
    return crud.create_user(db=db, user=user, password = hashed_password)



@app.post('/user_login', tags=["user"])
def login(auth_details: schemas.AuthDetails, db: Session = Depends(get_db)):
    user = None
    print(auth_details.email)
    user_record = crud.get_user_by_email(db=db, user_email=auth_details.email)
    print(user_record)
    if user_record is None:
        raise HTTPException(status_code=401, detail='invalid email')
         
    if (user_record is None) or (not auth_handler.verify_password(auth_details.password, user_record.password)):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user_record.id)
    return { "user": user_record, 'token': token }




import json
from fpdf import FPDF
import base64

from base64 import b64encode
@app.post('/test', tags=["user"])
def login(db: Session = Depends(get_db)):
    travel_code = "128"
    travel_description="Annual Meetup at Bhuj"
    trip_type="Domestic"
    emp_code="TU002"
    design_code="test data"
    company_code = "test data1"
    cc_code="100505"
    start_date="2023-04-11"
    end_date="2023-04-13"
    purpose = "Annual Meet"
    comment = "test data"
    advance_amount="5000"
    currency_code="101"
    advance_purpose="test dat"
    advance_comment ="test data"
    hodapprovel="test data"
    hod_comment="test data"
    account_approvel="test data"
    account_comment="test data"
    status="test data"
    currency_name="INR"
    
    TABLE_DATA = (
        ("travel_code", travel_code),
        ("travel_description", travel_description),
        ("trip_type", trip_type),
        ("emp_code", emp_code),
        ("design_code", design_code),
        ("company_code", company_code),
        ("cc_code", cc_code),
        ("start_date", start_date),
        ("end_date", end_date),
        ("purpose", purpose),
        ("comment", comment),
        ("advance_amount", advance_amount),
        ("currency_code", currency_code),
        ("advance_purpose", advance_purpose),
        ("advance_comment", advance_comment),
        ("hodapprovel", hodapprovel),
        ("hod_comment", hod_comment),
        ("account_approvel", account_approvel),
        ("account_comment", account_comment),
        ("status", status),
        ("currency_name", currency_name)
    )
    
    
    strat_date = "Flight_Data"
    end_date="Flight_Data"
    from_city="Flight_Data"
    to_city="Flight_Data"
    remark="test Flight_Data"
    
    Flight_Data = (
        ("strat_date", strat_date),
        ("end_date", end_date),
        ("from_city", from_city),
        ("to_city", to_city),
        ("remark", remark)
    )
    
    
    strat_date = "Train_Data"
    id_card="Annual Train_Data"
    from_city="Train_Data"
    to_city="Train_Data"
    remark="test Train_Data"
    age="Train_Data"
    gender="test Train_Data"
    
    Train_Data = (
        ("strat_date", strat_date),
        ("id_card", id_card),
        ("from_city", from_city),
        ("to_city", to_city),
        ("remark", remark),
        ("age", age),
        ("gender", gender)
    )
    
    
    strat_date = "Bus_Data"
    id_card="Annual Bus_Data"
    from_city="Bus_Data"
    to_city="Bus_Data"
    remark="test Bus_Data"
    age="Bus_Data"
    gender="test Bus_Data"
    
    Bus_Data = (
        ("strat_date", strat_date),
        ("id_card", id_card),
        ("from_city", from_city),
        ("to_city", to_city),
        ("remark", remark),
        ("age", age),
        ("gender", gender)
    )
    
    
    strat_date = "Car_Data"
    end_date="Annual Car_Data"
    from_city="Car_Data"
    to_city="Car_Data"
    remark="test Car_Data"
    
    Car_Data = (
        ("strat_date", strat_date),
        ("id_card", id_card),
        ("from_city", from_city),
        ("to_city", to_city),
        ("remark", remark)
    )
    
    check_in = "Hotel_Data"
    check_out="Annual Hotel_Data"
    city="Hotel_Data"
    remark="test Hotel_Data"
    
    Hotel_Data = (
        ("check_in", check_in),
        ("check_out", check_out),
        ("city", city),
        ("remark", remark)
    )
    
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times","B", size=16)
    
    pdf.write(0, 'Trip Details')
    pdf.ln()
    with pdf.table() as table:
        for data_row in TABLE_DATA:
            row = table.row()
            for datum in data_row:
                row.cell(datum)
    
    pdf.cell(600, 40, '\n')   
    pdf.write(0, 'Flight Details')
    pdf.ln()
    
    with pdf.table() as table:
        for data_row in Flight_Data:
            row = table.row()
            for datum in data_row:
                row.cell(datum) 
                
                
    pdf.ln()
    pdf.write(0, 'Train Details')
    pdf.ln()
    
    with pdf.table() as table:
        for data_row in Train_Data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)
    
    pdf.ln()
    pdf.write(0, 'Bus Details')
    pdf.ln()
    with pdf.table() as table:
        for data_row in Bus_Data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)
    
    pdf.ln() 
    pdf.write(0, 'Car Details')
    pdf.ln()
    with pdf.table() as table:
        for data_row in Car_Data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)
    
    pdf.ln() 
    pdf.write(0, 'Hotel Details')
    pdf.ln()
    with pdf.table() as table:
        for data_row in Hotel_Data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)
    
    
    test = base64.b64encode(pdf.output()).decode()
    r = bytes(test,'utf-8')
    result = "data:application/pdf;base64,"+test
    print(type(r))

    return {
      'statusCode': 200,
     'headers': {
      'Content-Type': 'application/pdf', 
     },
    'body': result,
    'isBase64Encoded': True 
    }









# @app.post("/files/")
# async def create_file(
#     file: bytes = File(), fileb: UploadFile = File(), token: str = Form()
# ):
#     with open(file, 'rb') as binary_file:
#     binary_file_data = binary_file.read()
#     base64_encoded_data = base64.b64encode(binary_file_data)
#     base64_message = base64_encoded_data.decode('utf-8')

#     print(base64_message)



# @app.post("/files/")
# def create_file(user: schemas.Create_Todo , db: Session = Depends(get_db),token: str = Header(None)):

#     head, data = user.img.split(',', 1)

# # Get the file extension (gif, jpeg, png)
#     file_ext = head.split(';')[0].split('/')[1]

# # Decode the image data
#     plain_data = base64.b64decode(data)
#     file_name = crud.generate_id()
#     file_location = f"files/{file_name}."
# # Write the image to a file
#     with open(file_location + file_ext, 'wb') as f:
#         f.write(plain_data)



















