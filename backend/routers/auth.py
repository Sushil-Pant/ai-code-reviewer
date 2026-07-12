"""
Authentication Router - Register, Login, Profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from models.schemas import UserCreate, UserLogin, UserResponse, Token
from services.auth_service import (
    create_user, authenticate_user, create_access_token,
    get_user_by_username, get_user_by_email
)
from utils.dependencies import get_current_user
from database.db import User

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account"""

    # Check username availability
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Check email availability
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = create_user(db, user_data)
    token = create_access_token(data={"sub": str(user.id)})

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and receive JWT token"""

    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": str(user.id)})

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.from_orm(current_user)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (client-side token invalidation)"""
    return {"message": "Logged out successfully"}


from pydantic import EmailStr, BaseModel
from typing import Optional

class PasswordlessLoginRequest(BaseModel):
    email: EmailStr


@router.post("/login-passwordless", response_model=Token)
async def login_passwordless(credentials: PasswordlessLoginRequest, db: Session = Depends(get_db)):
    """Login passwordlessly using email"""
    user = get_user_by_email(db, credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not registered. Please sign up."
        )
    token = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.post("/register-passwordless", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_passwordless(credentials: PasswordlessLoginRequest, db: Session = Depends(get_db)):
    """Register passwordlessly using email"""
    email = credentials.email
    if get_user_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate username from email prefix
    base_username = email.split("@")[0]
    username = "".join(c for c in base_username if c.isalnum() or c == "_")
    if len(username) < 3:
        username = username + "123"
        
    # Ensure uniqueness
    temp_username = username
    counter = 1
    while get_user_by_username(db, temp_username):
        temp_username = f"{username}{counter}"
        counter += 1
    username = temp_username
    
    # Create the user with a fallback password hash
    from services.auth_service import hash_password
    hashed_fallback = hash_password("passwordless_default_key_123!")
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_fallback,
        full_name=username.capitalize()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

