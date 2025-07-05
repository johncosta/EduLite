
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

---

### 2. Get Chat Room Details

#### **GET /api/chat/rooms/<room_id>/**

**Purpose**: Get info about a specific chat room.

**Permissions**: `IsAuthenticated`, `IsParticipant`

**Response:**
- `200 OK`
```json
{
  "id": 1,
  "name": "General",
  "participants": [1, 2]
}
```

**Error**:
- `404 Not Found`

---

### 3. List / Create Messages in a Chat Room

#### **GET /api/chat/rooms/<chat_room_id>/messages/**

**Purpose**: List all messages in a chat room.

**Permissions**: `IsAuthenticated`, `IsMessageSenderOrReadOnly`

**Query Params** (Cursor pagination):
- `cursor`: Optional cursor token

**Response:**
- `200 OK`
```json
{
  "next": "http://.../cursor=abc123",
  "previous": null,
  "results": [
    {
      "id": 10,
      "chat_room": 1,
      "sender": 1,
      "content": "Hello!",
      "timestamp": "2025-07-04T12:30:00Z"
    }
  ]
}
```

#### **POST /api/chat/rooms/<chat_room_id>/messages/**

**Purpose**: Send a new message in the chat room.

**Request Body:**
```json
{
  "content": "Hey there!"
}
```

**Success Response:**
- `201 Created`
```json
{
  "id": 11,
  "chat_room": 1,
  "sender": 1,
  "content": "Hey there!",
  "timestamp": "2025-07-04T12:31:00Z"
}
```

**Errors**:
- `400 Bad Request`
- `404 Not Found`

---

### 4. Retrieve / Update / Delete a Message

#### **GET /api/chat/rooms/<chat_room_id>/messages/<pk>/**

**Purpose**: Retrieve a specific message.

**Response:**
- `200 OK`
```json
{
  "id": 10,
  "chat_room": 1,
  "sender": 1,
  "content": "Hello!",
  "timestamp": "2025-07-04T12:30:00Z"
}
```

#### **PUT /api/chat/rooms/<chat_room_id>/messages/<pk>/**

**Purpose**: Full update of a message. Only the sender can update.

**Request Body:**
```json
{
  "content": "Updated message text"
}
```

**Response:**
- `200 OK`

#### **PATCH /api/chat/rooms/<chat_room_id>/messages/<pk>/**

**Purpose**: Partial update of a message.

**Request Body:**
```json
{
  "content": "Edited part"
}
```

**Response:**
- `200 OK`

#### **DELETE /api/chat/rooms/<chat_room_id>/messages/<pk>/**

**Purpose**: Delete a message.

**Response:**
- `204 No Content`
```json
{
  "message": "Message deleted successfully."
}
```

**Errors**:
- `400 Bad Request`
- `403 Forbidden`
- `404 Not Found`
