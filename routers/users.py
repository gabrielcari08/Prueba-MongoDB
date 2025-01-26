from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/users", 
                    tags=["users"],
                   responses={404: {"message": "No se ha encontrado"}})

# Entidad User
class Users(BaseModel):
    id: int
    name: str
    surname: str
    dni: int
    age: int

users_list = [
    Users(id=1, name="Gabriel", surname="Cari", dni=48405700, age=16),
    Users(id=2, name="Luciano", surname="Cari", dni=59000000, age=0),
    Users(id=3, name="Santino", surname="Cari", dni=53000000, age=10),
]

@router.get("/")
async def get_all_users(): 
    return users_list

@router.get("/{id}")
async def get_user_by_id(id: int):
    user = search_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.post("/", status_code=201)
async def create_user(user: Users):
    if search_user(user.id):
        raise HTTPException(status_code=400, detail="Este usuario ya existe")
    users_list.append(user)
    return user

@router.put("/")
async def update_user(user: Users):
    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.delete("/{id}")
async def delete_user(id: int):
    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]
            return {"message": "Usuario eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

def search_user(id: int):
    return next((user for user in users_list if user.id == id), None)
