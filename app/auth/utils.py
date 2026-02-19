from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import Config
import jwt
import uuid
import logging

JWT_ACCESS_TOKEN_EXPIRE_SECONDS = Config.JWT_ACCESS_TOKEN_EXPIRE_SECONDS

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_password_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, refresh: bool = False) -> str:
    payload = {}
    payload['user'] = data
    payload['exp'] = datetime.now() + (expires_delta if expires_delta else timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRE_SECONDS))
    payload['jti'] = str(uuid.uuid4())  # Add unique identifier for token
    payload['refresh'] = refresh

    encoded_jwt = jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logging.error("Token has expired")
        return None  # Token has expired
    except jwt.InvalidTokenError:
        logging.error("Invalid token")
        return None  # Invalid token