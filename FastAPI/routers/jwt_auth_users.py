from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext 
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET = "7f4b934b30e7019e2dd4a9db09b487a209beab0267b5ce53bab7af73b56df565"

router = APIRouter(prefix="/jwt", 
                   tags= ["JWT"],
                   responses={404: {"message": "No encontrado"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="login")
crypt = CryptContext(schemes=["bcrypt"])

# pip install "python-jose[cryptography]"  
# pip install "passlib[bcrypt]" 
# openssl rand -hex 32

# Entidad User
class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool


class UserDB(User):
    password: str


users_db = {    
        "istok":{
            "username": "istok",
            "full_name": "istok carvallo",
            "email": "istok.carvallo@rioblanco.net",
            "disabled": False,
            "password": "$2a$12$XScUssGYolvCdzPA/y3nWuPum6Z8wKXIUos06XQWwX0fb5E1m9LaG"        
        },
        "rafa":{
            "username": "rafa",
            "full_name": "rafa carvallo",
            "email": "istok.carvallo@rioblanco.net",
            "disabled": True,
            "password": "$2a$12$OHjYMFtmOR7ci.JOcllulOurebsjUtMD1aF4zl0rxi1i1V.L252la"        
        }
}

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])


def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])


async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail="Credenciales de autenticacion invalidas", 
                             headers={"WWW-Authenticate": "Bearer"})
    
    try:
        username = jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception
    
    return search_user(username)

async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                             detail="Usuario Inactivo")

    return user


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")
    
    user = search_user_db(form.username)

    if not  crypt.verify(form.password, user.password):
        raise  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcto")
    
    access_token = {"sub": user.username,
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}


@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user