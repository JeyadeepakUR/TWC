import pytest
from httpx import AsyncClient
import asyncio
from app.main import app
from app.db.mongodb import db

@pytest.fixture(scope="function")
async def db_connection():
    db.connect()
    yield
    db.disconnect()

@pytest.fixture(scope="function")
async def client(db_connection):
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture(scope="module")
async def test_org_data():
    return {
        "organization_name": "PytestOrg",
        "email": "pytest@org.com",
        "password": "pytestpassword"
    }

@pytest.fixture(scope="function", autouse=True)
async def cleanup(test_org_data, db_connection):
    # Setup
    yield
    # Teardown
    if db.client:
        await db.master_db.organizations.delete_one({"organization_name": test_org_data["organization_name"]})
        await db.master_db.admins.delete_many({"organization_name": test_org_data["organization_name"]})
        try:
            await db.master_db.drop_collection(f"org_{test_org_data['organization_name']}")
             # Also cleanup renamed version if exists
            await db.master_db.organizations.delete_one({"organization_name": test_org_data["organization_name"] + "Renamed"})
            await db.master_db.admins.delete_many({"organization_name": test_org_data["organization_name"] + "Renamed"})
            await db.master_db.drop_collection(f"org_{test_org_data['organization_name']}Renamed")
        except:
            pass
