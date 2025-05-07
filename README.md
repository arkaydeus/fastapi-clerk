# FastAPI-Clerk Authentication Service

A FastAPI service with Clerk authentication and PostgreSQL database integration. The service checks if a user with the current Clerk ID exists in the database, creates one if not found, and returns the user record.

## Features

- Integration with the official Clerk Python SDK for authentication
- JWT token validation with Clerk's backend API
- PostgreSQL database connectivity
- User record validation and creation
- Secure user data retrieval
- JSON logging with structured context data

## Requirements

- Python 3.11+
- PostgreSQL
- [Pipenv](https://pipenv.pypa.io/en/latest/)
- Clerk account and API keys

## Setup

1. Clone the repository
2. Install Pipenv if not already installed:
   ```
   pip install --user pipenv
   ```
3. Install dependencies:
   ```
   pipenv install
   ```
4. Create a `.env` file in the project root with the following variables:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_clerk
   CLERK_SECRET_KEY=sk_your_clerk_secret_key
   CLERK_ISSUER=https://your-clerk-instance.clerk.accounts.dev
   API_ENV=development
   ```

## Clerk SDK Integration

This project uses the official [Clerk Python SDK](https://github.com/clerk/clerk-sdk-python) to handle authentication. Key features:

- **Direct API Integration**: Uses `clerk_client = Clerk(bearer_auth=settings.clerk_secret_key)` to initialize the client
- **User Verification**: Verifies users directly with `clerk_client.users.get(user_id=user_id)`
- **JWT Processing**: Extracts user ID from JWT tokens with minimal processing
- **Middleware Integration**: Optional authentication middleware that doesn't block public endpoints

To obtain your Clerk secret key:

1. Go to your Clerk Dashboard
2. Navigate to API Keys
3. Copy the "Secret Key" (starts with `sk_`)

### Authentication Flow

1. A user authenticates with Clerk on the frontend and receives a JWT token
2. The token is included in the `Authorization` header with `Bearer` prefix
3. Our auth middleware extracts the token and validates it in two steps:
   - Basic JWT decoding to extract the user ID (sub claim)
   - Verification that the user exists in Clerk via the SDK
4. If verification succeeds, the user ID is added to the request state
5. Protected endpoints can access the user ID via dependency injection

## Database Setup

1. Ensure PostgreSQL is installed and running
2. Create a database user and database (if not using default):
   ```sql
   CREATE USER clerk_user WITH PASSWORD 'yourpassword';
   CREATE DATABASE fastapi_clerk OWNER clerk_user;
   ```
3. Update your `.env` file with the correct database URL
4. Initialize the database tables:
   ```
   pipenv run python scripts/create_db.py
   ```
5. Verify database connection:
   ```
   curl http://localhost:8000/db-test/ping
   ```

## Running the application

To run the development server:

```
pipenv run uvicorn app.main:app --reload
```

Access the API documentation at `http://localhost:8000/docs`

## Docker Deployment

The project includes Docker configuration for easy deployment.

### Using Docker Compose (recommended)

1. Ensure you have Docker and Docker Compose installed
2. Create a `.env` file with your environment variables (see `.env.example`)
3. Run:

   ```
   docker-compose up -d
   ```

4. The API will be available at `http://localhost:8000` and the API documentation at `http://localhost:8000/docs`

### Container Structure

- The application runs on port 8000 inside the container
- PostgreSQL database runs on the default port 5432
- Volumes are configured for persistent database storage
- Environment variables are passed from the host to the containers

## Testing

To run tests:

```
pipenv run pytest
```

## Project Structure

```
app/
  ├── api/         # API endpoints
  ├── core/        # Core configuration and middleware
  │   ├── auth.py  # Clerk authentication logic
  │   ├── config.py # Environment and app settings
  │   ├── logging.py # JSON logging configuration
  │   └── middleware.py # Request middleware
  ├── db/          # Database configuration
  ├── models/      # SQLAlchemy and Pydantic models
  └── services/    # Business logic
scripts/           # Utility scripts
tests/             # Test files
Dockerfile         # Docker configuration
docker-compose.yml # Docker Compose configuration
```

## Error Handling

The application includes comprehensive error handling:

- Authentication errors return appropriate HTTP 401 responses
- Database errors include detailed logs with structured context data
- All errors are logged with relevant context for debugging

## Environment Variables Reference

| Variable         | Description                               | Required |
| ---------------- | ----------------------------------------- | -------- |
| DATABASE_URL     | PostgreSQL connection string              | Yes      |
| CLERK_SECRET_KEY | Clerk API secret key (starts with sk\_)   | Yes      |
| CLERK_ISSUER     | Clerk issuer URL                          | Yes      |
| API_ENV          | Environment mode (development/production) | No       |
