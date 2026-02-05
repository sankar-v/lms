# API Documentation

## Base URL
- Development: `http://localhost:8000/api/v1`

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Users
- `POST /users/` - Create new user
- `GET /users/{user_id}` - Get user by ID
- `GET /users/` - List all users
- `PUT /users/{user_id}` - Update user

### Modules
- `POST /modules/` - Create new module
- `GET /modules/{module_id}` - Get module by ID
- `GET /modules/` - List all modules (supports filtering by category)
- `PUT /modules/{module_id}` - Update module

### Progress
- `POST /progress/` - Record progress
- `GET /progress/user/{user_id}` - Get all progress for user
- `GET /progress/user/{user_id}/module/{module_id}` - Get specific progress
- `PUT /progress/{progress_id}` - Update progress

### Recommendations
- `GET /recommendations/user/{user_id}` - Get personalized recommendations
- `POST /recommendations/feedback` - Submit recommendation feedback

### Chat
- `POST /chat/` - Send question to Q&A assistant
- `GET /chat/history/{user_id}` - Get chat history

## Response Formats

### Success Response
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error
