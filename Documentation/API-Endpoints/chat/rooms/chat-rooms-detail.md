# Retrieve Chat Room Details

Allows an authenticated user to retrieve details of a specific chat room identified by its primary key (pk). The user must be a participant in the chat room to access its details.

## Endpoint URL

`api/chat/rooms/<int:pk>/`

Replace `<int:pk>` with the unique ID of the chat room.

## HTTP Methods

* `GET`: Retrieves the details of a specific chat room.

## Permissions

* **Requires Authentication**: Yes (`permissions.IsAuthenticated`)
* **Requires Participation**: Yes (`IsParticipant`)
    * Only authenticated users who are participants in the chat room can access this endpoint.

## URL Parameters

| Parameter | Type    | Required | Description                             |
|:----------|:--------|:---------|:----------------------------------------|
| `pk`      | Integer | Yes      | The unique identifier of the Chat Room. |

## Request Headers

| Header          | Value                   | Required | Description                     |
|:----------------|:------------------------|:---------|:--------------------------------|
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication. |

---

## `GET` - Retrieve Chat Room

Retrieves the details of the specified chat room if the authenticated user is a participant.

**Successful `GET` Response:**

**Status Code:** `200 OK`

The response will contain a JSON object representing the chat room.

**Example `GET` JSON Response:**

```json
{
  "id": 1,
  "name": "Study Group Chat",
  "room_type": "GROUP",
  "participants": [1, 2, 3, 4],
  "messages": [
    {
      "id": 1,
      "chat_room": 1,
      "sender": 1,
      "sender_id": 1,
      "content": "Hello, EduLite!",
      "created_at": "2023-10-01T12:00:00Z",
      "is_read": true
    }
  ],
  "created_at": "2025-07-05T14:30:00.123456Z",
  "updated_at": "2025-07-05T16:44:51.889757Z"
}
```

---

## Common Error Responses

* **Status Code:** `401 Unauthorized`
  * **Reason:** Authentication credentials were not provided or were invalid.
  * **Response Body:**

```json
{
    "detail": "Authentication credentials were not provided."
}
```

* **Status Code:** `404 Not Found`
    * **Reason:** A `Chat Room` with the specified `pk` does not exist.
    * **Response Body:**

```json
{
    "detail":"No ChatRoom matches the given query."
}
```
