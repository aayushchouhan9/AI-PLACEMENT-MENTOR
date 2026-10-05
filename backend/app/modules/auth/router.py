from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import httpx

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.deps import get_current_user
from app.models import User, StudentProfile

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    branch: Optional[str] = None
    graduation_year: Optional[int] = None

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthSchema(BaseModel):
    credential: str

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str

@router.post("/register", response_model=TokenResponseSchema)
def register_user(payload: UserRegisterSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name
    )
    db.add(user)
    db.flush()

    # Create associated student profile
    profile = StudentProfile(
        user_id=user.id,
        branch=payload.branch,
        graduation_year=payload.graduation_year
    )
    db.add(profile)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name
    }

@router.post("/login", response_model=TokenResponseSchema)
def login_user(payload: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if user.is_deleted:
        raise HTTPException(status_code=403, detail="Account deletion requested. Please restore your account.")

    token = create_access_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name
    }

@router.post("/google", response_model=TokenResponseSchema)
def google_auth(payload: GoogleAuthSchema, db: Session = Depends(get_db)):
    # Verify Google credential token via Google tokeninfo endpoint
    token_info_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.credential}"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(token_info_url)
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid Google OAuth credential")
            data = resp.json()
            email = data.get("email")
            name = data.get("name", email.split("@")[0])
            sub = data.get("sub")
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to verify Google token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            full_name=name,
            google_id=sub
        )
        db.add(user)
        db.flush()

        profile = StudentProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(user)
    else:
        if not user.google_id:
            user.google_id = sub
            db.commit()

    token = create_access_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_deleted": current_user.is_deleted,
        "deletion_requested_at": current_user.deletion_requested_at,
        "profile": {
            "branch": profile.branch if profile else None,
            "graduation_year": profile.graduation_year if profile else None,
            "target_role_id": profile.target_role_id if profile else None
        }
    }
