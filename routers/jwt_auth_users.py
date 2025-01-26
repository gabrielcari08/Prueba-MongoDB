from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET = "8125acc8b2340831149e22ce361ec35b189183a23f0a64a5b9668797c9d0b231"

router = APIRouter(prefix="/jwt_auth_users", 
                    tags=["jwt_auth_users"],
                   responses={404: {"message":"No se ha encontrado"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])


class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool


class UserDB(User):
    password: str


users_db = {
    "Gabriel": {
        "username": "Gabriel",
        "full_name": "Gabriel Cari",
        "email": "Gabrielcari2008@gmail.com",
        "disabled": False,
        "password": "$2a$12$lrcB85SxOk4k.HbMqGD6PuI/butENaiGLDsjexNd7kuCCCuhicDBe",
    },
    "Luciano": {
        "username": "Luciano",
        "full_name": "Luciano Cari",
        "email": "Lucianocari2024@gmail.com",
        "disabled": True,
        "password": "$2a$12$DbKPMQtdw.txFZsEdLzRku4GiRtlhOjN3ey.bjlDwweK1niKtx8eu",
    },
}


def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])


def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])


async def auth_user(token: str = Depends(oauth2)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticacion invalidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise exception
    except JWTError:
        raise exception

    user = search_user(username)
    if not user:
        raise exception

    return user


async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo",
        )
    return user


@router.post("/")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Este usuario no existe"
        )

    user = search_user_db(form.username)
    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta contraseña es incorrecta",
        )

    access_token = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION),
    }

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}


@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user
