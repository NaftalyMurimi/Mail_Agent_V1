from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    email:     EmailStr
    password:  str
    full_name: str

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"

class TokenData(BaseModel):
    user_id: str | None = None