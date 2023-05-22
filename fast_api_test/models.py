from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String(300), unique=True, index=True, nullable=True)
    password = Column(String(300))
    items = relationship("ItemTable", back_populates="user")


class ItemTable(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), index=True)
    description = Column(String(300))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("UserTable", back_populates="items")
