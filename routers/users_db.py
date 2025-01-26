from fastapi import APIRouter, HTTPException
from db.models.user import User
from db.schemas.user import user_schema, users_schema
from db.client import db_client
from bson import ObjectId

router = APIRouter(
    prefix="/userdb",
    tags=["userdb"],
    responses={404: {"message": "No se ha encontrado"}},
)

@router.get("/", response_model=list[User])
async def get_all_users():
    return users_schema(db_client.users.find())

@router.get("/{id}", response_model=User)
async def get_user_by_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no válido")
    
    found_user = search_user("_id", ObjectId(id))
    if not found_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return found_user

@router.post("/", response_model=User, status_code=201)
async def create_user(user: User):
    if search_user("email", user.email):
        raise HTTPException(status_code=400, detail="Este usuario ya existe")
    
    user_dict = user.dict()
    del user_dict["id"]
    
    inserted_id = db_client.users.insert_one(user_dict).inserted_id
    new_user = user_schema(db_client.users.find_one({"_id": inserted_id}))
    return User(**new_user)

@router.put("/{id}", response_model=User)
async def update_user(id: str, user: User):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no válido")

    existing_user = search_user("_id", ObjectId(id))
    if not existing_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    updated_data = {k: v for k, v in user.dict().items() if v is not None and k != "id"}

    if "email" in updated_data:
        email_in_use = search_user("email", updated_data["email"])
        if email_in_use and str(email_in_use.id) != id:
            raise HTTPException(status_code=400, detail="El email ya está registrado por otro usuario")
    
    db_client.users.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
    updated_user = user_schema(db_client.users.find_one({"_id": ObjectId(id)}))
    return User(**updated_user)

@router.delete("/{id}")
async def delete_user(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no válido")

    deleted_user = db_client.users.find_one_and_delete({"_id": ObjectId(id)})
    if not deleted_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado correctamente"}

def search_user(field: str, key):
    try:
        user = db_client.users.find_one({field: key})
        if user:
            return User(**user_schema(user))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar usuario: {str(e)}")
    return None
