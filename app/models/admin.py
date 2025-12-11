from pydantic import BaseModel, EmailStr
from typing import Optional

class AdminBase(BaseModel):
    email: EmailStr
    organization_name: str

class AdminCreate(AdminBase):
    password: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    organization_name: str
    organization_id: Optional[str] = None
