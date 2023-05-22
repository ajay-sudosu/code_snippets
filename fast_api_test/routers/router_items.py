from fastapi import APIRouter, Depends
from typing import List, Optional, Union
from schema import ItemBase, ShowItem, User
from database import get_db
from sqlalchemy.orm import Session
from models import ItemTable
from oauth import get_current_user
import json
router_items = APIRouter()


@router_items.post("/create-items", tags=["Items"])
async def create_items(item: ItemBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user:
            print("yes")
        data = item.dict()
        item_add = ItemTable(**data)
        db.add(item_add)
        db.flush()
        db.commit()
        return {"status": "success", "data": "Done."}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@router_items.get("/fetch-items", response_model=List[ShowItem], tags=["Items"])
async def get_items(db: Session = Depends(get_db)):
    try:
        data = db.query(ItemTable).all()
        return data
        # return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@router_items.get("/fetch-items/{item_id}", response_model=ShowItem, tags=["Items"])
# @app.get("/fetch-items/{item_id}", tags=["Items"])
async def get_items(item_id: int, db: Session = Depends(get_db)):
    try:
        data = db.query(ItemTable).filter_by(id=item_id).first()
        return data
        # return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
