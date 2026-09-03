
import os
from datetime import datetime, timedelta
from typing import Dict, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from api import schema
from api.crud import CRUDUser
from api.db import get_session
from api.models import UserDBModel
from api.utils import PasswordHasher


spotapp_auth_router = APIRouter(tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@spotapp_auth_router.post(
    path="/login",
    responses={
        200: {"description": "User loged in!"},
        400: {"model": schema.Error, "description": "Requested user not found"},
        406: {"model": schema.Error, "description": "Input data format error"},
    },
)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_session),
                ) -> Dict[str, str]:
    """Login user with email"""
    try:
        user = await CRUDUser.login(db=db, username=form_data.username)
        if not user or not PasswordHasher().verify_password(
                form_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect email or password",
                                headers={"WWW-Authenticate": "Bearer"})

        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})
    except HTTPException:
        raise
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error")


def create_access_token(data: dict,
                        expires_delta: Union[timedelta, None] = None) -> str:
    """Creating encoded JWT token for 30 min by default"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_session),
                           ) -> UserDBModel:
    """Getting current authorized user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schema.TokenData(email=email)
        user = await CRUDUser.get_user_by_email(db=db, email=token_data.email)
        if not user:
            raise credentials_exception
        return user
    except (JWTError, ValidationError):
        raise credentials_exception
    except NoResultFound:
        raise credentials_exception


async def get_current_active_user(current_user: UserDBModel = Depends(get_current_user)):
    """Getting active user"""
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                    detail="Inactive user")
    return current_user
