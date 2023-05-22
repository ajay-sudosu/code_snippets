from pydantic import BaseModel, Field, EmailStr



class UserSchema(BaseModel):
    username : str
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "abdulazeez@x.com",
                "password": "weakpassword"
            }
        }

class UserLoginSchema(BaseModel):
    username : str
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "abdulazeez@x.com",
                "password": "weakpassword"
            }
        }