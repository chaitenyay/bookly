from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import JSONResponse
from app.auth.service import UserService
from app.auth.schemas import UserCreateModel, UserResponseModel, UserLoginModel
from app.db.main import get_session
from app.auth.utils import create_access_token, decode_access_token, verify_password
from datetime import datetime, timedelta
from app.config import Config
from app.auth.dependencies import AccessTokenBearer, RefreshTokenBearer


REFRESH_TOKEN_EXPIRE_DAYS = Config.REFRESH_TOKEN_EXPIRE_DAYS

auth_router = APIRouter()
user_service = UserService()


@auth_router.post("/signup", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
async def user_signup(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)) -> UserResponseModel:
    email = user_data.email
    if await user_service.user_exists(email, session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    new_user = await user_service.create_user(user_data, session)
    return UserResponseModel.from_orm(new_user)


@auth_router.post("/signin")
async def user_signin(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(user.uid), "email": user.email}
    )

    referesh_token = create_access_token(
        data={"sub": str(user.uid), "email": user.email},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        refresh=True
    )

    return JSONResponse(
        content={
            "message": "Login successful",
            "access_token": access_token, 
            "refresh_token": referesh_token,
            "user" : {
                "uid": str(user.uid),
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        })


@auth_router.post("/refresh")
async def refresh_access_token(token_data: dict = Depends(RefreshTokenBearer())):
    user_id = token_data.get("sub")
    email = token_data.get("email")
    expiry_timestamp = token_data.get("exp")

    if datetime.fromtimestamp(expiry_timestamp) < datetime.now():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired")
    
    access_token = create_access_token(
            data={"sub": user_id, "email": email}
    )
    
    return JSONResponse(content={"access_token": access_token})
    
    