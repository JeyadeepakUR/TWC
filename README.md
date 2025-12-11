# Organization Management Service

Backend service for managing organizations in a multi-tenant environment using FastAPI and MongoDB.

## Features

- **Multi-tenancy**: Dedicated MongoDB collection for each organization (`org_<name>`).
- **Master Database**: Stores global metadata and admin credentials.
- **Organization CRUD**: Create, Read, Update, Delete organizations.
- **Authentication**: JWT-based Admin login.
- **Security**: Password hashing with Bcrypt.
- **Rate Limiting**: API throttling to prevent abuse (default 5 req/min on critical endpoints).

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

## API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| **POST** | `/admin/login` | Admin login to get JWT token | No |
| **POST** | `/org/create` | Create a new organization | No |
| **GET** | `/org/get?organization_name=...` | Get organization metadata | No |
| **PUT** | `/org/update` | Update/Rename organization | Yes (Admin) |
| **DELETE** | `/org/delete?organization_name=...` | Delete organization and data | Yes (Admin) |

## API Documentation

Once running, visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Testing

## Testing

This project uses **Pytest** for a professional and robust test suite.
The tests verify the complete lifecycle: Create -> Login -> Get -> Update -> Delete.

Ensure MongoDB is running, then drive:

```bash
# Run all tests
python -m pytest -v
```

## Project Structure

```
├── app/
│   ├── api/            # Route handlers (admin, org)
│   ├── core/           # Config, Security, Rate Limiter
│   ├── db/             # Database connection
│   ├── models/         # Pydantic models
│   └── main.py         # Entry point
├── tests/              # Pytest suite
│   ├── conftest.py     # Test fixtures
│   └── test_api.py     # E2E test cases
├── architecture.md     # High-level diagram and design notes
├── requirements.txt    # Dependencies
├── pytest.ini          # Pytest configuration
└── .env                # Environment variables
```

## License

This project is provided for evaluation purposes for The Wedding Company internship assignment.

