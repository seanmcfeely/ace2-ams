from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.models.token import Token
from api.routes import helpers
from core.auth import create_access_token
from db import crud
from db.database import get_db


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


def auth(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.auth(username=form_data.username, password=form_data.password, db=db)

    if user is None or not user.enabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    return {
        "access_token": create_access_token(sub=user.username),
        "token_type": "bearer",
    }


helpers.api_route_auth(router, auth, Token)
