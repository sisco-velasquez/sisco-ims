from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username:str=Field( min_length=4, max_lenth=50,description="unique username")

class UserCreate(UserBase):
    password:str =Field(min_length=6, description="plain text")

class UserLogin(UserBase):
    password:str

class UserRead(UserBase):
    id:int

class config:
    from_attributes=True

class ProductCreate(BaseModel):
    name:str
    price:float
    quantity:int
    category:str
    description:Optional[str] =None

class ProductUpdate(BaseModel):
    quantity:Optional[int]=None
    price:Optional[float]=None
    