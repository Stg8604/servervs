from fastapi import FastAPI, Depends,  HTTPException, status,Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated
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
  database="delta",
   port='3306'
)
cursor=mydb.cursor()
selectstatement="select * from user_info"
cursor.execute(selectstatement)
result=cursor.fetchall()
cursor.close()
db=dict()

secretkey="83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11692"
algo="HS256"
access=30
class Token(BaseModel):
    access_token:str
    token_type:str
class TokenData(BaseModel):
    username:str or None=None
class UserS(BaseModel):
    username: str
    image: str = None
    lent: int = None
    debt: int = None
    hashpass: str
class User(BaseModel):
    username:str
    image:str or None=None
    lent:int or None=None
    debt:int or None=None
class UserINDB(User):
    hashpass:str
class newUser(BaseModel):
    debt:int
    sname:str
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
def getuser2(db,username:str):
    if username in db:
        query="select name,amount,image,settle from transactions where username=%s"
        cursor=mydb.cursor()
        cursor.execute(query,(username,))
        result=cursor.fetchall()
        cursor.close()
        pb=list()
        for i in result:
            pb.append({"name":i[0],"money":i[1],"image":i[2],"settle":i[3]})
        return pb
#getuser2(db,"michael")
def authentication(db,username:str,password:str):
    cursor=mydb.cursor()
    selectstatement="select * from user_info"
    cursor.execute(selectstatement)
    result=cursor.fetchall()
    cursor.close()
    for i in result:
      db[i[0]]={"username":i[0],"image":i[1],"lent":i[2],"debt":i[3],"hashpass":gethaspass(i[4])}
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
         cursor=mydb.cursor()
         selectstatement="select * from user_info"
         cursor.execute(selectstatement)
         result=cursor.fetchall()
         cursor.close()
         for i in result:
            db[i[0]]={"username":i[0],"image":i[1],"lent":i[2],"debt":i[3],"hashpass":gethaspass(i[4])}
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
@app.get("/users/me/transaction")
async def read_users_me(current_user:User=Depends(getcurrent)):
    cursor=mydb.cursor()
    selectstatement="select * from user_info"
    cursor.execute(selectstatement)
    result=cursor.fetchall()
    cursor.close()
    cursor=mydb.cursor()
    selectstatement="select * from user_info"
    cursor.execute(selectstatement)
    result=cursor.fetchall()
    cursor.close()
    for i in result:
      db[i[0]]={"username":i[0],"image":i[1],"lent":i[2],"debt":i[3],"hashpass":gethaspass(i[4])}
    if current_user.username in db:
        query="select name,amount,image,settle from transactions where username=%s"
        cursor=mydb.cursor()
        cursor.execute(query,(current_user.username,))
        result=cursor.fetchall()
        cursor.close()
        pb=list()
        for i in result:
            pb.append({"name":i[0],"money":i[1],"image":i[2],"settle":i[3]})
        return pb
@app.get("/users/me/splithistory")
async def read_users_me(current_user:User=Depends(getcurrent)):
    cursor=mydb.cursor()
    selectstatement="select * from user_info"
    cursor.execute(selectstatement)
    result=cursor.fetchall()
    cursor.close()
    for i in result:
      db[i[0]]={"username":i[0],"image":i[1],"lent":i[2],"debt":i[3],"hashpass":gethaspass(i[4])}
    if current_user.username in db:
        query="select * from split where username=%s"
        cursor=mydb.cursor()
        cursor.execute(query,(current_user.username,))
        result=cursor.fetchall()
        cursor.close()
        pb=list()
        for i in result:
            pb.append({"spname":i[0],"spperson":i[1],"username":i[2],"image":i[3],"name":i[4],"amount":i[5]})
        return pb
    #Annotated[str, Form()]
@app.get("/users/me/grouphistory")
async def read_users_me(current_user:User=Depends(getcurrent)):
    cursor=mydb.cursor()
    selectstatement="select * from user_info"
    cursor.execute(selectstatement)
    result=cursor.fetchall()
    cursor.close()
    for i in result:
      db[i[0]]={"username":i[0],"image":i[1],"lent":i[2],"debt":i[3],"hashpass":gethaspass(i[4])}
    if current_user.username in db:
        query="select * from gp where username=%s"
        cursor=mydb.cursor()
        cursor.execute(query,(current_user.username,))
        result=cursor.fetchall()
        cursor.close()
        pb=list()
        for i in result:
            pb.append({"username":i[0],"gname":i[1],"name":i[2],"image":i[3]})
        return pb
@app.get("/users/me/groupsplits")
async def read_users_me(current_user:User=Depends(getcurrent)):
    cursor=mydb.cursor()
    selectstatement="select * from user_info"
    cursor.execute(selectstatement)
    result=cursor.fetchall()
    cursor.close()
    for i in result:
      db[i[0]]={"username":i[0],"image":i[1],"lent":i[2],"debt":i[3],"hashpass":gethaspass(i[4])}
    if current_user.username in db:
        query="select * from hg where username=%s"
        cursor=mydb.cursor()
        cursor.execute(query,(current_user.username,))
        result=cursor.fetchall()
        cursor.close()
        pb=list()
        for i in result:
            pb.append({"username":i[0],"spname":i[1],"spperson":i[2],"gname":i[3],"name":i[4],"image":i[5],"amount":i[6]})
        return pb
@app.post("/signup/",response_model=Token)
async def loginaccess(username:Annotated[str, Form()],image:Annotated[str, Form()],lent:Annotated[int, Form()],debt:Annotated[int, Form()],hashpass:Annotated[str, Form()]):

    access_token_expires=timedelta(minutes=access)
    accesstoken=accessing(data={"sub":username},timeexpire=access_token_expires)  
    str2="insert into user_info values(%s,%s,%s,%s,%s)"
    cursor=mydb.cursor()
    #cursor.execute(str2,("user_info",user.username,user.image,user.lent,user.debt,user.hashpass))
    cursor.execute(str2,(username,image,lent,debt,hashpass))
    mydb.commit()
    cursor.close()
    cursor=mydb.cursor()
    db=dict()
    for i in result:
        db[i[0]]={"username":i[0],"image":i[1],"lent":i[2],"debt":i[3],"hashpass":gethaspass(i[4])}
    return  {"access_token":accesstoken,"token_type":"bearer"}

    '''
    cursor=mydb.cursor()
    query = "SELECT * FROM user_info WHERE username = %s"
    cursor.execute(query, (user.username,))
    result = cursor.fetchall()
    if result:
        raise HTTPException(status_code=400, detail="User already exists")

    # Add the user to the database

    ''' 
'''
@app.post("/signup/")
async def signup(username:str,image:str,lent:int,debt:int,hashpass:str):
    str2="insert into user_info values(%s,%s,%s,%s,%s)"
    cursor=mydb.cursor()
    #cursor.execute(str2,("user_info",user.username,user.image,user.lent,user.debt,user.hashpass))
    cursor.execute(str2,(username,image,lent,debt,hashpass))
    mydb.commit()
    cursor.close()
    
    query = "SELECT * FROM user_info WHERE username = %s"
    cursor.execute(query, (user.username,))
    result = cursor.fetchall()
    if result:
        raise HTTPException(status_code=400, detail="User already exists")

    # Add the user to the database
    query = "INSERT INTO user_info (username, image, lent, debt, hashpass) VALUES (%s, %s, %s, %s, %s)"

    values = (user.username, user.image, user.lent, user.debt, user.hashpass)
    cursor.execute(query, values)
    mydb.commit()
    '''   
@app.post("/mod/")
async def read_users_me(debt:Annotated[int, Form()],sname:Annotated[str, Form()],sname2:Annotated[str, Form()]):
    que="update user_info set debt=%s where username=%s"
    values=(debt,sname)
    cursor=mydb.cursor()
    cursor.execute(que,values)
    cursor.close()
    que2="update transactions set settle=%s where name=%s"
    cursor=mydb.cursor()
    values2=("settled",sname2)
    cursor.execute(que2,values2)
    mydb.commit()
@app.post("/append/")
async def read_users_me(spname:Annotated[str,Form()],spperson:Annotated[str,Form()],username:Annotated[str,Form()],image:Annotated[str,Form()],name:Annotated[str,Form()],amount:Annotated[float,Form()]):   #[(username,image,name,amount)]
    cursor=mydb.cursor()
    que="insert into split values(%s,%s,%s,%s,%s,%s)"
    values=(spname,spperson,username,image,name,amount)
    cursor.execute(que,values)
    cursor.close()
    mydb.commit()
@app.post("/add/")
async def read_users_me(username:Annotated[str,Form()],gname:Annotated[str,Form()],name:Annotated[str,Form()],image:Annotated[str,Form()]):
    cursor=mydb.cursor()
    que="insert into gp values(%s,%s,%s,%s)"
    values=(username,gname,name,image)
    cursor.execute(que,values)
    cursor.close()
    mydb.commit()
query="select * from gp where username=%s"
cursor=mydb.cursor()
cursor.execute(query,("bhaskar",))
result=cursor.fetchall()
cursor.close()
pb=list()
for i in result:
        pb.append({"username":i[0],"gname":i[1],"name":i[2],"image":i[3]})
print(result)
@app.post("/hg/")
async def read_users_me(username:Annotated[str, Form()],spname:Annotated[str, Form()],spperson:Annotated[str, Form()],gname:Annotated[str, Form()],name:Annotated[str, Form()],image:Annotated[str, Form()],amount:Annotated[int, Form()]):
    que="insert into gp values(%s,%s,%s,%s,%s,%s,%s)"
    values=(username,spname,spperson,gname,name,image,amount)
    cursor=mydb.cursor()
    cursor.execute(que,values)
    cursor.close()
    mydb.commit()


    
