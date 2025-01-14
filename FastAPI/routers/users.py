from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/users",
                   tags=["Users"],
                   responses={404: {"message": "No encontrado"}})

# Entidad User
class User(BaseModel):
    id: int
    name: str
    surname: str
    url: str
    age: int

users_list = [User(id=1, name="istok", surname="carvallo", url="wwww.google.com", age=47),
        User(id=2, name="lenka", surname="carvallo", url="wwww.bci.com", age=37),
        User(id=3, name="rafael", surname="carvallo", url="wwww.bchile.com", age=18)]

@router.get("/")
async def users():
    return users_list

@router.get("/{id}") # Path
async def user(id: int):
    return search_user(id)

@router.get("/") # Query
async def user(id: int):
    return search_user(id)

@router.post("/", response_model= User, status_code=201) # codigo generico de termino
async def user(user: User):
    if type(search_user(user.id)) == User:
        # lanzar codigo por error
        raise  HTTPException(status_code=404, detail="El usuario ya existe")
    
    users_list.append(user)
    return user

@router.put("/")
async def user(user: User):
    found = False

    for index, users in enumerate(users_list):
        if users.id == user.id:
            users_list[index] = user
            found = True

    if not found:
        return {"error": "No se ha encontrado el usuario"}

    return user

@router.delete("/{id}")
async def user(id: int):
    found = False

    for index, users in enumerate(users_list):
        if users.id == id:
            del users_list[index] 
            found = True           

    if not found:
        return {"error": "No se ha encontrado el usuario"}

def search_user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except:
        return {"error": "No se ha encontrado el usuario"}
