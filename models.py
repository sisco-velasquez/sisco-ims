from typing import Optional
from datetime import datetime
from sqlmodel import Field,SQLModel

class User(SQLModel, table=True):
    id :Optional[int]= Field(default=None,primary_key=True)
    username:str=Field(unique=True,index=True )
    hashed_password: str

class Product(SQLModel, table=True):
    id:Optional[int] =Field(default=None, primary_key=True)
    name:str =Field(index=True)
    description:Optional[str]=None
    price:float
    quantity:int
    category:str
    user_id: int = Field(foreign_key="user.id", index=True)

class Sale(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    quantity_sold: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id", index=True)
    