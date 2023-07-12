from fastapi import FastAPI, Depends,  HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime,timedelta
#from jose import JWTError,jwt
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import mysql.connector
from mysql.connector import connect,Error
'''try:
    with connect(
        host="localhost",
        user="root",
        password="Stg08604",
        database="delta"
    ) as connection:
        print(connection)
        with connection.cursor() as cursor:
            selectstatement="select * from user_info"
            cursor.execute(selectstatement)
            result=cursor.fetchall()
except Error as e:
    print(e)'''
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Stg08604",
  database="delta"
)
cursor=mydb.cursor()
selectstatement="select * from user_info"
cursor.execute(selectstatement)
result=cursor.fetchall()

db=dict()

secretkey="83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11692"
algo="HS256"
access=30
class Token(BaseModel):
    access_token:str
    token_type:str
class TokenData(BaseModel):
    username:str or None=None
class User(BaseModel):
    username:str
    image:str or None=None
    lent:int or None=None
    debt:int or None=None
class UserINDB(User):
    hashpass:str
pwd_context=CryptContext(schemes=["bcrypt"],deprecated='auto')
oauth2=OAuth2PasswordBearer(tokenUrl="token")
app=FastAPI()
def verify_pass(normalpass,hashpass):
        return pwd_context.verify(normalpass,hashpass)
def gethaspass(password):
    return pwd_context.hash(password)
for i in result:
    db[i[0]]={"username":i[0],"image":i[1],"lent":i[2],"debt":i[3],"hashpass":gethaspass(i[4])}
def getuser(db,username:str):
    if username in db:
        userdata=db[username]
        return UserINDB(**userdata)
use=getuser(db,"michael")
print(type(use))
def authentication(db,username:str,password:str):
    user=getuser(db,username)
    if not user:
        return False
    if not verify_pass(password,user.hashpass):   #yes
        return False
    return user
def accessing(data:dict,timeexpire:timedelta or None=None):
    encode=data.copy()
    if timeexpire:
        expire=datetime.utcnow()+ timeexpire
    else:
        expire=datetime.utcnow()+timedelta(minutes=15)
    encode.update({"exp":expire})
    encode_jwt=jwt.encode(encode,secretkey,algorithm=algo)
    return encode_jwt
async def getcurrent(token:str=Depends(oauth2)):
         credexcept=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Unvalidated",headers="Authenticate:Bearer")
         try:
             payload=jwt.decode(token,secretkey,algorithms=[algo])
             username:str=payload.get("sub")
             if username is None:
                 raise credexcept
             tokendata=TokenData(username=username)
         except InvalidTokenError:
            raise credexcept
         user=getuser(db,username=tokendata.username)
         if user is None:
             raise credexcept
         return user
@app.post("/token/",response_model=Token)
async def loginaccess(form_data:OAuth2PasswordRequestForm=Depends()):
    user=authentication(db,form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="incorrect",headers={"Authenticate":"Bearer"})
    access_token_expires=timedelta(minutes=access)
    accesstoken=accessing(data={"sub":user.username},timeexpire=access_token_expires)  
    return  {"access_token":accesstoken,"token_type":"bearer"}
@app.get("/users/me/",response_model=User)
async def read_users_me(current_user:User=Depends(getcurrent)):
    return current_user
@app.get("/users/me/debt/")
async def read_users_me(current_user:User=Depends(getcurrent)):
        return current_user.debt
#form_data:OAuth2PasswordRequestForm=Depends()
        