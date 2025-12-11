import pytest
from httpx import AsyncClient

# Mark all tests as async
pytestmark = pytest.mark.asyncio

async def test_end_to_end_lifecycle(client: AsyncClient, test_org_data):
    # 1. Create Organization
    response = await client.post("/org/create", json=test_org_data)
    assert response.status_code == 200, f"Create Org Failed: {response.text}"
    data = response.json()
    assert data["organization_name"] == test_org_data["organization_name"]
    
    # 2. Login Admin
    login_data = {
        "email": test_org_data["email"],
        "password": test_org_data["password"]
    }
    response = await client.post("/admin/login", json=login_data)
    assert response.status_code == 200, f"Login Failed: {response.text}"
    token_data = response.json()
    access_token = token_data["access_token"]
    assert access_token is not None
    
    # 3. Get Organization
    response = await client.get("/org/get", params={"organization_name": test_org_data["organization_name"]})
    assert response.status_code == 200, f"Get Org Failed: {response.text}"
    assert response.json()["organization_name"] == test_org_data["organization_name"]
    
    # 4. Update Organization (Rename)
    new_name = test_org_data["organization_name"] + "Renamed"
    update_data = {
        "organization_name": new_name
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = await client.put("/org/update", json=update_data, headers=headers)
    assert response.status_code == 200, f"Update Org Failed: {response.text}"
    assert response.json()["new_name"] == new_name
    
    # Verify Metadata updated
    response = await client.get("/org/get", params={"organization_name": new_name})
    assert response.status_code == 200
    
    # 5. Delete Organization
    # Login again to get token with NEW org name (if needed by backend, though we saw backend just checks user found)
    # Actually, our backend logic `current_user["org"] != organization_name` matches claim.
    # So we DO need a new token because the old token has the OLD org name claim.
    response = await client.post("/admin/login", json=login_data)
    assert response.status_code == 200
    new_token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {new_token}"}
    
    response = await client.delete("/org/delete", params={"organization_name": new_name}, headers=headers)
    assert response.status_code == 200, f"Delete Org Failed: {response.text}"

    # 6. Verify Deletion
    response = await client.get("/org/get", params={"organization_name": new_name})
    assert response.status_code == 404
