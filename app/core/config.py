import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MASTER_DB_NAME: str = os.getenv("MASTER_DB_NAME", "master_org_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkeyrequiredforjwt")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()
