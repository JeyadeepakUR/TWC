from fastapi import APIRouter, HTTPException, status, Depends
from app.models.org import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.db.mongodb import db
from app.core.security import get_password_hash
from app.api.deps import get_current_user
from app.core.limiter import limiter
from fastapi import Request

router = APIRouter()

@router.post("/create", response_model=OrganizationResponse)
@limiter.limit("5/minute")
async def create_organization(request: Request, org: OrganizationCreate):
    # 1. Check if org exists
    existing_org = await db.master_db.organizations.find_one({"organization_name": org.organization_name})
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization name already exists")
    
    # 2. Prepare Collection Name
    collection_name = f"org_{org.organization_name}"
    
    # 3. Create Admin User
    hashed_pw = get_password_hash(org.password)
    admin_doc = {
        "email": org.email,
        "password": hashed_pw,
        "organization_name": org.organization_name,
        "role": "admin"
    }
    await db.master_db.admins.insert_one(admin_doc)
    
    # 4. Create Org Metadata
    org_doc = {
        "organization_name": org.organization_name,
        "collection_name": collection_name,
        "admin_email": org.email
    }
    await db.master_db.organizations.insert_one(org_doc)
    
    # 5. Create Dynamic Collection (implicitly created on insert, or explicit create)
    # We can create it explicitly to be sure
    try:
        await db.master_db.create_collection(collection_name)
    except Exception:
        pass # Might exist or other issue, but we proceed given unique org check

    return OrganizationResponse(**org_doc)

@router.get("/get", response_model=OrganizationResponse)
async def get_organization(organization_name: str):
    org = await db.master_db.organizations.find_one({"organization_name": organization_name})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationResponse(**org)

@router.put("/update")
async def update_organization(
    org_update: OrganizationUpdate, 
    current_user: dict = Depends(get_current_user)
):
    # Enforce current user is admin of the org they want to update (or at least of *an* org)
    # If the user is trying to change the org name, they must be admin of the OLD org name.
    # The requirement endpoint input is: organization_name, email, password.
    # It implies we identify the org by the INPUT organization_name?
    # BUT, if we are UPDATING, we need to know WHICH org to update.
    # Usually we update the org identified by the JWT or a path param.
    # ENDPOINT: PUT /org/update
    # User sends new data.
    # We should probably trust the JWT for which org they manage, or check if the input org name exists?
    # Requirement: "Validate that the organization name does not already exist." (This implies changing name)
    
    # Let's assume the admin can only update THEIR OWN organization.
    current_org_name = current_user.get("org")
    if not current_org_name:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Use current_org_name to find the record
    existing_org = await db.master_db.organizations.find_one({"organization_name": current_org_name})
    if not existing_org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # If updating name
    new_name = org_update.organization_name
    old_collection_name = existing_org["collection_name"]
    
    if new_name != current_org_name:
        # Check duplicate
        if await db.master_db.organizations.find_one({"organization_name": new_name}):
             raise HTTPException(status_code=400, detail="New organization name already exists")
        
        # Rename collection
        new_collection_name = f"org_{new_name}"
        try:
            # Motor collection rename
            await db.master_db[old_collection_name].rename(new_collection_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to rename collection: {str(e)}")
            
        # Update Org Metadata
        await db.master_db.organizations.update_one(
            {"organization_name": current_org_name},
            {"$set": {"organization_name": new_name, "collection_name": new_collection_name}}
        )
        
        # Update Admin Metadata (Organization Name ref)
        await db.master_db.admins.update_many(
            {"organization_name": current_org_name},
            {"$set": {"organization_name": new_name}}
        )
        
        # Update current_org_name var for subsequent updates
        current_org_name = new_name

    # If updating email/password (Admin updates)
    # We update the admin record associated with this org.
    # Wait, there might be multiple admins? Requirement says "email (admin email)". 
    # It implies updating THE admin credentials or the org's contact email.
    # Let's assume updating the primary admin that matches the INPUT email or just the current user.
    # If the input email is different, we update the admin email?
    
    update_fields = {}
    if org_update.email:
         # Check if email is being changed. 
         # We need to identify which admin to update. `current_user['sub']` is the email.
         # Let's update the admin that is logged in.
         update_fields["email"] = org_update.email
    
    if org_update.password:
        update_fields["password"] = get_password_hash(org_update.password)
        
    if update_fields:
        await db.master_db.admins.update_one(
            {"email": current_user["sub"]}, 
            {"$set": update_fields}
        )
        # Also update org metadata if it stores admin_email
        if org_update.email:
             await db.master_db.organizations.update_one(
                {"organization_name": current_org_name},
                {"$set": {"admin_email": org_update.email}}
            )

    return {"message": "Organization updated successfully", "new_name": current_org_name}

@router.delete("/delete")
async def delete_organization(organization_name: str, current_user: dict = Depends(get_current_user)):
    # Verify user is admin of this org
    if current_user["org"] != organization_name:
         raise HTTPException(status_code=403, detail="Not authorized to delete this organization")
         
    org = await db.master_db.organizations.find_one({"organization_name": organization_name})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    collection_name = org["collection_name"]
    
    # Delete Org Metadata
    await db.master_db.organizations.delete_one({"organization_name": organization_name})
    
    # Delete Admins
    await db.master_db.admins.delete_many({"organization_name": organization_name})
    
    # Drop Collection
    try:
        await db.master_db.drop_collection(collection_name)
    except Exception:
        pass
        
    return {"message": "Organization deleted successfully"}
