# Send Friend Request

Allows an authenticated user to send a friend request to another user. When a friend request is successfully sent, the recipient will automatically receive a notification.

## Endpoint URL

`/api/friend-requests/send/`

## HTTP Method

`POST`

## Permissions

* **Requires Authentication**: Yes
  * Only authenticated users can send friend requests.
  * If the request is made by an unauthenticated user, a `401 Unauthorized` response will be returned.

## Request Headers

| Header        | Value                 | Required | Description                                     |
| :------------ | :-------------------- | :------- | :---------------------------------------------- |
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication.                 |
| `Content-Type`  | `application/json`    | Yes      | Specifies that the request body is in JSON format. |

## Request Body

The request body must be a JSON object containing the friend request details.

**Fields:**

| Field                  | Type    | Required | Description                                                    |
| :--------------------- | :------ | :------- | :------------------------------------------------------------- |
| `receiver_profile_id` | Integer | Yes      | The unique identifier of the user profile to send request to. |
| `message`             | String  | No       | Optional custom message (max 500 characters) to include with the request. |

**Example JSON Request Body:**

	```json
	{
	    "receiver_profile_id": 5,
		"message": "Hey! We were in the same Python class. Would love to connect!"

	}
	```

## Successful Response

**Status Code:** `201 Created`

The response will contain a simple confirmation message with the friend request ID for reference.

**Example JSON Response:**

	```json
	{
	    "detail": "Friend request sent successfully.",
	    "request_id": 12
	}
	```

**Response Fields:**

| Field        | Type    | Description                                           |
| :----------- | :------ | :---------------------------------------------------- |
| `detail`     | String  | Confirmation message that the request was sent.      |
| `request_id` | Integer | The unique identifier of the created friend request. |

## Automatic Notifications

When a friend request is successfully sent, the system automatically:
- Creates a notification for the recipient
- The notification will appear in the recipient's notification feed
- The recipient can view pending friend requests via the [List Pending Friend Requests](./friend-request-list-pending.md) endpoint

## Error Responses

* **Status Code:** `401 Unauthorized`
  * **Reason:** Authentication credentials were not provided or were invalid.
  * **Response Body:**

	```json
	{
	    "detail": "Authentication credentials were not provided."
	}
	```

* **Status Code:** `400 Bad Request`
  * **Reason:** The request body is missing required fields or contains invalid data.
  * **Response Body Examples:**

	```json
	{
	    "detail": "receiver_profile_id is required."
	}
	```

	```json
	{
	    "detail": "Invalid receiver_profile_id. Must be an integer."
	}
	```

	```json
	{
	    "detail": "You cannot send a friend request to yourself."
	}
	```

	```json
	{
	    "detail": "You are already friends with this user."
	}
	```

	```json
	{
	    "detail": "You have already sent a friend request to this user."
	}
	```

	```json
	{
	    "detail": "This user has already sent you a friend request. Check your pending requests."
	}
	```

	```json
	{
	    "detail": "Sender profile not found."
	}
	```

	```json
	{
    "detail": "Message must be 500 characters or fewer."
	}
	```

* **Status Code:** `404 Not Found`
  * **Reason:** A user profile with the specified `receiver_profile_id` does not exist.
  * **Response Body:**

	```json
	{
	    "detail": "Not found."
	}
	```

* **Status Code:** `500 Internal Server Error`
  * **Reason:** An unexpected server error occurred during friend request creation.
  * **Response Body:**

	```json
	{
	    "detail": "A friend request between these users already exists or another integrity issue occurred."
	}
	```

## Usage Flow

1. **Send Request**: User A sends a friend request to User B (optionally with a personalized message)
2. **Automatic Notification**: System creates a notification for User B
3. **User B Receives**: User B sees the notification and can check pending requests
4. **Response**: User B can accept or decline using the respective endpoints

## Field Notes

- `message` is optional but recommended for personalization.
- The message must be under 500 characters.
- Basic content moderation may be applied in the future to block inappropriate messages.

## Related Endpoints

- [List Pending Friend Requests](./friend-request-list-pending.md) - View pending requests
- [Accept Friend Request](./friend-request-accept.md) - Accept a received request
- [Decline Friend Request](./friend-request-decline.md) - Decline or cancel a request
