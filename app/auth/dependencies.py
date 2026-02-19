
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from app.auth.utils import decode_access_token



class TokenBearer(HTTPBearer):
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials = await super().__call__(request)

        token = credentials.credentials
        token_data = decode_access_token(token)

        if not self.token_valid(token):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication credentials")

        self.verify_token_data(token_data)
        return token_data
        
    def token_valid(self, token: str) -> bool:
        decoded_token = decode_access_token(token)
        return True if decoded_token else False
    
    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Subclasses must implement this method to verify token data.")
    
    
    
class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:

        if token_data and token_data['refresh']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="please provide an access token.")
        
class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:

        if token_data and not token_data['refresh']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="please provide a refresh token.")