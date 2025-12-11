from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class OrganizationBase(BaseModel):
    organization_name: str

class OrganizationCreate(OrganizationBase):
    email: EmailStr
    password: str

class OrganizationResponse(OrganizationBase):
    collection_name: str
    admin_email: EmailStr

class OrganizationUpdate(BaseModel):
    organization_name: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None
