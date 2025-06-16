# Accept Friend Request

Allows an authenticated user to accept a pending friend request that was sent to them.

## Endpoint URL

`/api/friend-requests/<int:request_pk>/accept/`

Replace `<int:request_pk>` with the unique ID of the friend request you want to accept.

## HTTP Method

`POST`

## Permissions

* **Requires Authentication**: Yes
  * Only authenticated users can accept friend requests.
  * If the request is made by an unauthenticated user, a `401 Unauthorized` response will be returned.
* **Requires Receiver Permission**: Yes
  * Only the receiver of the friend request can accept it.
  * Uses `IsFriendRequestReceiver` permission class.

## URL Parameters

| Parameter    | Type    | Required | Description                                     |
| :----------- | :------ | :------- | :---------------------------------------------- |
| `request_pk` | Integer | Yes      | The unique identifier of the friend request.   |

## Request Headers

| Header        | Value                 | Required | Description                                     |
| :------------ | :-------------------- | :------- | :---------------------------------------------- |
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication.                 |
| `Content-Type`  | `application/json`    | No       | Not required for this POST endpoint.           |

## Request Body

No request body is required for this endpoint.

## Successful Response

**Status Code:** `200 OK`

The response will contain a JSON object confirming the friend request was accepted.

**Example JSON Response:**

	```json
	{
	    "detail": "Friend request accepted."
	}
	```

## Error Responses

* **Status Code:** `401 Unauthorized`
  * **Reason:** Authentication credentials were not provided or were invalid.
  * **Response Body:**

	```json
	{
	    "detail": "Authentication credentials were not provided."
	}
	```

* **Status Code:** `403 Forbidden`
  * **Reason:** The authenticated user is not the receiver of this friend request.
  * **Response Body:**

	```json
	{
	    "detail": "You do not have permission to perform this action."
	}
	```

* **Status Code:** `404 Not Found`
  * **Reason:** A friend request with the specified `request_pk` does not exist.
  * **Response Body:**

	```json
	{
	    "detail": "Not found."
	}
	```

* **Status Code:** `400 Bad Request`
  * **Reason:** The friend request could not be accepted (possibly already processed).
  * **Response Body:**

	```json
	{
	    "detail": "Failed to accept friend request. It might have been already processed or an error occurred."
	}
	```

## Notes

* Once a friend request is accepted, both users become friends and the friend request is automatically deleted.
* The friendship is bidirectional - both users will see each other in their friends list.
* If the friend request has already been processed (accepted or declined), this endpoint will return an error.
