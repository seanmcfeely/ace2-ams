from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.models.auth import AuthBase
from api.routes import helpers
from db import crud
from db.database import get_db


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


def auth(auth: AuthBase, db: Session = Depends(get_db)):
    crud.auth(username=auth.username, password=auth.password, db=db)


helpers.api_route_auth(router, auth)
