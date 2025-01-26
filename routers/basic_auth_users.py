from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/basic_auth_users",
    tags=["basic_auth_users"],
    responses={404: {"message": "No se ha encontrado"}},
)

oauth2 = OAuth2PasswordBearer(tokenUrl="login")


# Definición de modelos de usuario
class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool


class UserDB(User):
    password: str


# Base de datos simulada
users_db = {
    "Gabrielardo": {
        "username": "Gabrielardo",
        "full_name": "Gabriel Cari",
        "email": "Gabrielcari2008@gmail.com",
        "disabled": False,
        "password": "123456",
    },
    "Lucianardo": {
        "username": "Lucianardo",
        "full_name": "Luciano Cari",
        "email": "LLucianocari2024@gmail.com",
        "disabled": True,
        "password": "654321",
    },
}


# Funciones auxiliares
def search_user_db(username: str) -> UserDB | None:
    """Busca un usuario en la base de datos simulada y retorna UserDB."""
    if username in users_db:
        return UserDB(**users_db[username])
    return None


def search_user(username: str) -> User | None:
    """Busca un usuario en la base de datos simulada y retorna User."""
    if username in users_db:
        return User(**users_db[username])
    return None


async def current_user(token: str = Depends(oauth2)) -> User:
    """
    Valida el token (nombre de usuario) y retorna el usuario actual.
    """
    user = search_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    return user


# Endpoints
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica un usuario con su nombre de usuario y contraseña.
    """
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no existe",
        )

    user = search_user_db(form.username)
    if user.password != form.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña incorrecta",
        )

    # Retorna un token básico para pruebas (el nombre de usuario actúa como token)
    return {"access_token": user.username, "token_type": "bearer"}


@router.get("/users/me", response_model=User)
async def get_current_user(user: User = Depends(current_user)):
    """
    Retorna el perfil del usuario autenticado.
    """
    return user
