from fastapi import APIRouter, Depends, Response
from typing import List, Optional, Union
from schema import LoginSchema
from database import get_db
from models import UserTable
from sqlalchemy.orm import Session
from hashing_file import hash_obj
from jwt_token import create_access_token
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

router_auth = APIRouter()

@router_auth.post('/login', tags=['Authentication'])
def login(user_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        data = db.query(UserTable).filter_by(email=user_data.username).first()
        if not data:
            return {"msg": "No user found."}
        if not hash_obj.verify(user_data.password, data.password):
            return {"msg": "password incorrect."}

        # return jwt token
        access_token = create_access_token(data={"sub": data.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(str(e))
