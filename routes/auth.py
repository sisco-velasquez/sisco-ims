from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from database import get_session
from models import User
from schemas import UserCreate, UserRead, UserLogin 
from security import hash_password, verify_password
from auth_handler import create_access_token ,SECRET_KEY, ALGORITHM

# Import jwt to decode the token. 
# (Note: if you use PyJWT instead of python-jose, this is just 'import jwt')
from jose import JWTError, jwt 

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Tells FastAPI to look for the token in the headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



# --- 1. EXISTING REGISTRATION & LOGIN ---

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


# --- 2. THE GATEKEEPER (Fixes your ImportError) ---

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    """Decodes the JWT token and returns the active User object."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Open the token to get the username
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Find the exact user in the PostgreSQL database 
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
        
    return user


# --- 3. FETCH CURRENT USER ROUTE ---

@router.get("/me", response_model=UserRead)
async def get_logged_in_user(current_user: User = Depends(get_current_user)):
    """Allows the frontend to fetch the profile of the person currently logged in."""
    return current_user