from fastapi import APIRouter, Depends, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import JSONResponse
from app.auth.service import UserService
from app.auth.schemas import UserCreateModel, UserResponseModel, UserLoginModel
from app.db.main import get_session
from app.auth.utils import create_access_token, decode_access_token, verify_password
from datetime import datetime, timedelta
from app.config import Config
from app.auth.dependencies import AccessTokenBearer, RefreshTokenBearer
from app.common.error_repsonses import _error_response
from app.common.schemas import APIResponse


REFRESH_TOKEN_EXPIRE_DAYS = Config.REFRESH_TOKEN_EXPIRE_DAYS

auth_router = APIRouter()
user_service = UserService()


@auth_router.post("/signup", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
async def user_signup(
    request: Request,
    user_data: UserCreateModel,
    session: AsyncSession = Depends(get_session),
) -> APIResponse[dict] | JSONResponse:
    email = user_data.email
    if await user_service.user_exists(email, session):
        return _error_response(
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="USER_ALREADY_EXISTS",
            message="Signup failed",
            details="Email already registered",
        )

    try:
        new_user = await user_service.create_user(user_data, session)
    except ValueError as exc:
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            error_code="USER_CONFLICT",
            message="Signup failed",
            details=str(exc),
        )
    created_user = UserResponseModel.from_orm(new_user)
    return APIResponse(
        status="success",
        statusCode=status.HTTP_201_CREATED,
        data={
            "user": {
                "uid": str(created_user.uid),
                "username": created_user.username,
                "email": created_user.email,
                "first_name": created_user.first_name,
                "last_name": created_user.last_name,
                "is_verified": created_user.is_verified,
                "is_active": created_user.is_active,
                "created_at": created_user.created_at.isoformat(),
                "updated_at": created_user.updated_at.isoformat(),
            }
        },
        message="Signup successful",
        errors=None,
    )


@auth_router.post("/signin", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
async def user_signin(
    request: Request,
    login_data: UserLoginModel,
    session: AsyncSession = Depends(get_session),
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
    
    if not user or not verify_password(password, user.password_hash):
        return _error_response(
            request=request,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS",
            message="Signin failed",
            details="Invalid credentials",
        )

    access_token = create_access_token(
        data={"sub": str(user.uid), "email": user.email}
    )

    refresh_token = create_access_token(
        data={"sub": str(user.uid), "email": user.email},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        refresh=True
    )

    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data={
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "user" : {
                "uid": str(user.uid),
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        },
        message="Login successful",
        errors=None,
    )


@auth_router.post("/refresh", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
async def refresh_access_token(request: Request, token_data: dict = Depends(RefreshTokenBearer())):
    user_id = token_data.get("sub")
    email = token_data.get("email")
    expiry_timestamp = token_data.get("exp")

    if datetime.fromtimestamp(expiry_timestamp) < datetime.now():
        return _error_response(
            request=request,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="REFRESH_TOKEN_EXPIRED",
            message="Token refresh failed",
            details="Refresh token has expired",
        )
    
    access_token = create_access_token(
            data={"sub": user_id, "email": email}
    )
    
    return APIResponse(
        status="success",
        statusCode=status.HTTP_200_OK,
        data={"access_token": access_token},
        message="Access token refreshed successfully",
        errors=None,
    )
    
    
