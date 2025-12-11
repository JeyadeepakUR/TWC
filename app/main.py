from fastapi import FastAPI
from app.db.mongodb import db
from app.api.admin import router as admin_router
from app.api.org import router as org_router

app = FastAPI(title="Organization Management Service")

# Rate Limiting
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
async def startup_db_client():
    db.connect()

@app.on_event("shutdown")
async def shutdown_db_client():
    db.disconnect()

app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(org_router, prefix="/org", tags=["organization"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Organization Management Service"}
