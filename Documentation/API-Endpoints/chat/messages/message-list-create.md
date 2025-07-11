# List Chat Message or Create Chat Message

Allows an authenticated user to retrieve a paginated list of chat room messages where the user is the sender or has read only access.

## Endpoint URL

`/api/chat/rooms/<int:chat_room_id>/messages/`

## HTTP Methods

* `GET`: Retrieves a paginated list of all chat room messages where the user is the sender or has read only access.
* `POST`: Creates a new chat room messages.

## Permissions

* **Requires Authentication**: Yes (`permissions.IsAuthenticated`)
  * Only authenticated users can access this endpoint.

* **Requires MessageSenderOrReadOnly Permission**: Yes (`permissions.IsMessageSenderOrReadOnly`)
  * Full access (read/write/delete) to the message senders messages.
  * Read-only access to messages in their rooms.

---

## `GET` - List Chat Room Messages

Retrieves a paginated list of all chat room messages the user is the message sender or has read only access.

**Request Headers:**

| Header          | Value                   | Required | Description                     |
|:----------------|:------------------------|:---------|:--------------------------------|
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication. |

**Query Parameters:**

**Query Parameters:**

| Parameter   | Type    | Optional | Description                                    | Default |
|:------------|:--------|:---------|:-----------------------------------------------|:--------|
| `cursor`    | String  | Yes      | A cursor value for pagination (opaque string). | None    |
| `page_size` | Integer | Yes      | Number of results to return per page.          | 50      |

**Successful `GET` Response:**

**Status Code:** `200 OK`

The response will be a paginated JSON object containing a list of all chat room messages the user is the sender or has read only access.

**Example `GET` JSON Response:**

```json
{
  "next": "http://localhost:8000/api/chat/rooms/1/messages/?cursor=cD0yMDIzLTEwLTAxKzEyJTNBMTU%3D",
  "previous": null,
  "results": [
    {
      "id": 3,
      "chat_room": 1,
      "sender": "admin",
      "content": "How is everyone doing today?",
      "created_at": "2023-10-01T12:15:00Z",
      "is_read": false
    },
    {
      "id": 2,
      "chat_room": 1,
      "sender": "edulite",
      "content": "Good morning!",
      "created_at": "2023-10-01T12:10:00Z",
      "is_read": false
    },
    {
      "id": 1,
      "chat_room": 1,
      "sender": "edulite",
      "content": "Hello, EduLite!",
      "created_at": "2023-10-01T12:00:00Z",
      "is_read": false
    }
  ]
}
```

**Response Fields (Paginated Structure):**

| Field      | Type   | Description                                                                    |
|:-----------|:-------|:-------------------------------------------------------------------------------|
| `next`     | String | URL with cursor to the next page of results, or `null` if no more pages.       |
| `previous` | String | URL with cursor to the previous page of results, or `null` if first page.      |
| `results`  | Array  | An array of chat room message objects ordered by creation time (newest first). |

**Response Fields (Messages Object in `results`):**

| Field        | Type    | Description                                                  |
|:-------------|:--------|:-------------------------------------------------------------|
| `id`         | Integer | The unique identifier of the message.                        |
| `chat_room`  | Integer | The ID of the chat room this message belongs to.             |
| `sender`     | String  | The username or string representation of the message sender. |
| `sender_id`  | Integer | The ID of the user sending the message (write-only).         |
| `content`    | String  | The text content of the message.                             |
| `created_at` | String  | ISO 8601 timestamp of when the message was created.          |
| `is_read`    | Boolean | Indicates whether the message has been read.                 |

**Pagination Notes:**
- Messages are ordered by creation time (newest first)
- Cursor pagination is used for better performance with large message histories
- The `cursor` parameter is an opaque string - do not attempt to parse or modify it
- Use the `next` and `previous` URLs directly for pagination navigation

---

## `POST` - Create Chat Message

Creates a new chat room message.

**Request Headers:**

| Header          | Value                   | Required | Description                                        |
|:----------------|:------------------------|:---------|:---------------------------------------------------|
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication.                    |
| `Content-Type`  | `application/json`      | Yes      | Specifies that the request body is in JSON format. |

**Request Body:**

The request body must be a JSON object containing the details for the new chat room message.

**Fields (from `MessageSerializer`):**

| Field     | Type    | Required | Description                                   |
|:----------|:--------|:---------|:----------------------------------------------|
| `content` | String  | Yes      | The text content of the message.              |
| `is_read` | Boolean | No       | Indicates whether the message has been read.  |

**Example `POST` Request Body:**

```json
{
  "content": "Hello everyone! How are you doing today?",
  "is_read": false
}
```

**Notes:**
- `sender` is automatically set to the authenticated user
- `chat_room` is automatically set from the URL parameter `chat_room_id`
- `content` is the only required field
- `is_read` defaults to `false` if not provided

**Successful `POST` Response:**

**Status Code:** `201 Created`

The response will contain the JSON object of the newly created group.

**Example `POST` JSON Response:**

```json
{
  "id": 15,
  "chat_room": 1,
  "sender": "edulite",
  "content": "Hello everyone! How are you doing today?",
  "created_at": "2023-10-01T14:30:00Z",
  "is_read": false
}
```

---

## Common Error Responses

* **Status Code:** `400 Bad Request`
  * **Reason (for `POST`):** The provided data is invalid (e.g., `sender_id` for the chat room does not exist).
  * **Response Body (Example - `sender_id` invalid):**

```json
{
  "sender_id": [
    "Invalid pk \"6\" - object does not exist."
  ]
}
```

* **Status Code:** `400 Bad Request`
  * **Reason (for `POST`):** The provided data is invalid (e.g., `content` field data empty).
  * **Response Body (Example - `content` invalid):**

```json
{
  "content": [
      "This field may not be blank."
  ]
}
```

* **Status Code:** `400 Bad Request`
  * **Reason (for `POST`):** The provided data is invalid (e.g., `content` field missing).
  * **Response Body (Example - `content` missing):**

```json
{
  "content": [
    "This field is required."
  ]
}
```

* **Status Code:** `400 Bad Request`
  * **Reason (for `POST`):** The provided data is invalid (e.g., `is_read` field is an integer).
  * **Response Body (Example - `is_read` invalid):**

```json
{
  "is_read": [
    "Must be a valid boolean."
  ]
}
```

* **Status Code:** `401 Unauthorized`
  * **Reason:** Authentication credentials were not provided or were invalid.
  * **Response Body:**

```json
{
    "detail": "Authentication credentials were not provided."
}
```

* **Status Code:** `403 Forbidden`
  * **Reason:** `chat_room_id` provided is invalid.
  * **Response Body:**

```json
{
    "detail": "You do not have permission to perform this action."
}
```
