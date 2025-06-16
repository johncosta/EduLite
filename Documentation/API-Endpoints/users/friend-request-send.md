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

The response will contain a simple confirmation message with the friend request ID.

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
