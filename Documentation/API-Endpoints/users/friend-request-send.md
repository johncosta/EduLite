# Send Friend Request

Allows an authenticated user to send a friend request to another user.

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

**Example JSON Request Body:**

	```json
	{
	    "receiver_profile_id": 5
	}
	```

## Successful Response

**Status Code:** `201 Created`

The response will contain a JSON object representing the created friend request with all relevant details and action URLs.

**Example JSON Response:**

	```json
	{
	    "id": 12,
	    "sender_id": 3,
	    "receiver_id": 5,
	    "sender_profile_url": "/api/users/3/profile/",
	    "receiver_profile_url": "/api/users/5/profile/",
	    "created_at": "2024-01-15 14:30:25",
	    "accept_url": "/api/friend-requests/12/accept/",
	    "decline_url": "/api/friend-requests/12/decline/"
	}
	```

**Response Fields:**

| Field                    | Type   | Description                                                               |
| :----------------------- | :----- | :------------------------------------------------------------------------ |
| `id`                     | Integer| The unique identifier of the friend request.                             |
| `sender_id`              | Integer| The unique identifier of the sender's user profile.                      |
| `receiver_id`            | Integer| The unique identifier of the receiver's user profile.                    |
| `sender_profile_url`     | String | The hyperlink to the sender's profile resource.                          |
| `receiver_profile_url`   | String | The hyperlink to the receiver's profile resource.                        |
| `created_at`             | String | The timestamp when the friend request was created (format: YYYY-MM-DD HH:MM:SS). |
| `accept_url`             | String | The hyperlink to accept this friend request.                             |
| `decline_url`            | String | The hyperlink to decline this friend request.                            |

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
