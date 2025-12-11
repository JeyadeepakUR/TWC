from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None

    def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        print("Connected to MongoDB")

    def disconnect(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

    @property
    def master_db(self):
        return self.client[settings.MASTER_DB_NAME]

    def get_org_db(self, collection_name: str):
        # In this design, the requirement says "Dynamic Collection".
        # This usually means creating a new collection in the SAME database or a new DATABASE.
        # The requirement says: "Create a new Mongo collection specifically for the organization... Example collection name pattern: org_<organization_name>"
        # It also says "Master Database for global metadata and create dynamic collections for each organization."
        # This implies all org collections live in the Master DB (or a specific DB) but are separate collections.
        # However, typical multi-tenancy with Mongo often uses separate DBs per tenant or one DB with collection per tenant.
        # The prompt explicitly says: "Dynamically create a new Mongo collection... Store ... Organization collection name in Master Database".
        # So I will assume they live in the `master_db` as separate collections, or I can use a separate `tenants_db`.
        # To keep it clean, I will use `master_db` for metadata and same DB for tenant collections effectively, or separate.
        # Let's use the same DB for simplicity unless specified otherwise.
        return self.client[settings.MASTER_DB_NAME][collection_name]

db = Database()
