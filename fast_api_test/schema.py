from typing import Union, List, Optional

from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str
    password: str

class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None
    user_id: Optional[int] = None


class Item(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True

class Showuser(BaseModel):
    name: str
    items: List[Item] = []

    class Config:
        orm_mode = True


class ShowItem(BaseModel):
    title: str
    description: Union[str, None] = None
    user: Showuser

    class Config:
        orm_mode = True

class LoginSchema(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_tpe: str


class TokenData(BaseModel):
    username: Optional[str] = None
