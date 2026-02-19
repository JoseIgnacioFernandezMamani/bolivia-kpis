from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.user import User
from auth.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    build_google_auth_url,
    exchange_google_code,
    get_or_create_google_user,
)
from auth.schemas import UserCreate, UserLogin, Token, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        name=payload.name,
    )
    db.add(user)
    await db.flush()
    return user


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/google")
async def google_login():
    return RedirectResponse(url=build_google_auth_url())


@router.get("/google/callback", response_model=Token)
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    try:
        user_info = await exchange_google_code(code)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Google OAuth error") from exc

    user = await get_or_create_google_user(user_info, db)
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}
