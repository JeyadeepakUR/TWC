from fastapi import APIRouter, HTTPException, status
from app.models.admin import AdminLogin, Token
from app.db.mongodb import db
from app.core.security import verify_password, create_access_token
from app.core.limiter import limiter
from fastapi import Request

router = APIRouter()

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, login_data: AdminLogin):
    # Find admin in Master DB
    # We assume 'admins' collection in Master DB stores admin credentials
    # Structure: { "email": ..., "password": ..., "organization_name": ... }
    
    admin = await db.master_db.admins.find_one({"email": login_data.email})
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(login_data.password, admin["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT
    access_token = create_access_token(
        data={"sub": admin["email"], "org": admin["organization_name"]}
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "organization_name": admin["organization_name"],
        "organization_id": str(admin["_id"])
    }
