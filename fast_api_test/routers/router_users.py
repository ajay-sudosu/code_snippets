from fastapi import APIRouter, Depends, Response
from typing import List, Optional, Union
from schema import Showuser, User
from database import get_db
from sqlalchemy.orm import Session
from models import UserTable
from hashing_file import hash_obj

router_user = APIRouter()

@router_user.post("/create-user", tags=["Users"])
async def create_user(user: User, db: Session = Depends(get_db)):
    try:
        data = user.dict()
        hashed_password = hash_obj.bcrypt(data.get("password"))
        data.update({"password": hashed_password})
        user_data = UserTable(**data)
        db.add(user_data)
        db.flush()
        db.commit()
        return {"status": "success", "data": []}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

# @app.get("/users", response_model=List[Showuser])
@router_user.get("/users", tags=["Users"])
async def get_users(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        if not user_id:
            data = db.query(UserTable).all()
            return data
        else:
            data = db.query(UserTable).filter_by(id=user_id).first()
            return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@router_user.get("/users/{user_id}", tags=["Users"])
async def get_users(user_id: int, response: Response, db: Session = Depends(get_db)):
    try:
        '''For custom response/custom response model code refer here.'''
        data = db.query(UserTable).filter_by(id=user_id).first()
        if not data:
            raise Exception
        # return data
        response.status_code = status.HTTP_200_OK
        return {"status": status.HTTP_200_OK, "data": Showuser(name=data.name, is_active=data.is_active, items=data.items)}
    except Exception as e:
        return {"status": "failed", "error": str(e)}



