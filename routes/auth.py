from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models import User
from schemas import UserCreate, UserRead, UserLogin 
from security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserRead, status_code=201)
async def register(user_data: UserCreate, session: Session = Depends(get_session)):
   
    statement = select(User).where(User.username == user_data.username)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    
    new_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user

from auth_handler import create_access_token # Import the maker

@router.post("/login")
async def login(login_data: UserLogin, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == login_data.username)
    user = session.exec(statement).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create the token (the "VIP Pass")
    token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": token, 
        "token_type": "bearer",
        "username": user.username
    }