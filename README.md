# Organization Management Service

Backend service for managing organizations in a multi-tenant environment using FastAPI and MongoDB.

## Features

- **Multi-tenancy**: Dedicated MongoDB collection for each organization (`org_<name>`).
- **Master Database**: Stores global metadata and admin credentials.
- **Organization CRUD**: Create, Read, Update, Delete organizations.
- **Authentication**: JWT-based Admin login.
- **Security**: Password hashing with Bcrypt.

## Tech Stack

- **Python 3.10+**
- **FastAPI**: Web Framework
- **MongoDB (Motor)**: Async Database Driver
- **Pydantic**: Data Validation
- **PyJWT**: Authentication

## Prerequisites

- **MongoDB**: You MUST have a MongoDB instance running.
    - Default: `mongodb://localhost:27017`
    - You can configure this in `.env`.

## Setup Instructions

1. **Clone the repository** (or use the provided files).

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   - Check `.env` file. Modify `MONGODB_URL` if needed.
   
   ```env
   MONGODB_URL=mongodb://localhost:27017
   MASTER_DB_NAME=master_org_db
   SECRET_KEY=change_this_to_a_secure_random_string
   ```

4. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Testing

A test script `test_flow.py` is included to verify the core workflow.
Ensure MongoDB is running, then drive:

```bash
python test_flow.py
```

## Project Structure

```
├── app/
│   ├── api/            # Route handlers
│   ├── core/           # Config and Security
│   ├── db/             # Database connection
│   ├── models/         # Pydantic models
│   └── main.py         # Entry point
├── architecture.md     # High-level diagram and design notes
├── requirements.txt    # Dependencies
├── test_flow.py        # Automated verification script
└── .env                # Environment variables
```
