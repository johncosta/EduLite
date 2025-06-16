# Decline Friend Request

Allows an authenticated user to decline a friend request they received or cancel a friend request they sent.

## Endpoint URL

`/api/friend-requests/<int:request_pk>/decline/`

Replace `<int:request_pk>` with the unique ID of the friend request you want to decline or cancel.

## HTTP Method

`POST`

## Permissions

* **Requires Authentication**: Yes
  * Only authenticated users can decline or cancel friend requests.
  * If the request is made by an unauthenticated user, a `401 Unauthorized` response will be returned.
* **Requires Sender or Receiver Permission**: Yes
  * Either the sender (to cancel) or receiver (to decline) of the friend request can use this endpoint.
  * Uses `IsFriendRequestReceiverOrSender` permission class.

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

The response will contain a JSON object confirming the action taken. The message varies depending on whether the user was declining (as receiver) or canceling (as sender).

**Example JSON Response (Declining as Receiver):**

	```json
	{
	    "detail": "Friend request declined successfully."
	}
	```

**Example JSON Response (Canceling as Sender):**

	```json
	{
	    "detail": "Friend request canceled successfully."
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
  * **Reason:** The authenticated user is neither the sender nor receiver of this friend request.
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
  * **Reason:** The friend request could not be processed (possibly already actioned).
  * **Response Body:**

	```json
	{
	    "detail": "Failed to process the friend request. It might have been already actioned or an unexpected error occurred."
	}
	```

## Use Cases

* **Declining as Receiver**: When you receive a friend request and don't want to accept it.
* **Canceling as Sender**: When you sent a friend request but want to cancel it before it's accepted.

## Notes

* Once a friend request is declined or canceled, it is permanently deleted from the system.
* The action cannot be undone - if users want to connect later, a new friend request must be sent.
* Both declining and canceling result in the same outcome: the friend request is removed.
