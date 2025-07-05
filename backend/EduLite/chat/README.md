
# Chat API Documentation

## Authentication

All endpoints require JWT authentication.

**Header:**
```http
Authorization: Bearer <JWT_access_token>
```

---

## Endpoints

### 1. List / Create Chat Rooms

#### **GET /api/chat/rooms/**

**Purpose**: List chat rooms the user participates in.

**Permissions**: `IsAuthenticated`, `IsParticipant`  
**Query Params** (optional):
- `limit`: Items per page
- `offset`: Starting index

**Response:**
- `200 OK`
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "General",
      "participants": [1, 2]
    }
  ]
}
```

#### **POST /api/chat/rooms/**

**Purpose**: Create a new chat room. Authenticated user is added as participant.

**Permissions**: `IsAuthenticated`, `IsParticipant`

**Request Body:**
```json
{
  "name": "New Room",
  "participants": [2, 3]
}
```

**Success Response:**
- `201 Created`
```json
{
  "id": 5,
  "name": "New Room",
  "participants": [1, 2, 3]
}
```

**Error Response:**
- `400 Bad Request`
```json
{
  "name": ["This field is required."]
}
```
