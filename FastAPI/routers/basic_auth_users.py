from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter(prefix="/basic", 
                   tags= ["basic"],
                   responses={404: {"message": "No encontrado"}})
oauth2 = OAuth2PasswordBearer(tokenUrl="login")


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
            "password": "1234"        
        },
        "rafa":{
            "username": "rafa",
            "full_name": "rafa carvallo",
            "email": "istok.carvallo@rioblanco.net",
            "disabled": True,
            "password": "4321"        
        }
}


def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])


def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])


async def current_user(token: str = Depends(oauth2)):
    user = search_user(token)
    if not user:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail="Credenciales de autenticacion invalidas", 
                             headers={"WWW-Authenticate": "Bearer"})

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

    if not user.password == form.password:
        raise  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcto")
    
    return {"access_token": user.username, "token_type": "bearer"}


@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user