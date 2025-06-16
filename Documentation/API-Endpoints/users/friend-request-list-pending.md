# List Pending Friend Requests

Retrieves a paginated list of pending friend requests for the authenticated user. Can filter by direction (sent or received).

## Endpoint URL

`/api/friend-requests/pending/`

## HTTP Method

`GET`

## Permissions

* **Requires Authentication**: Yes
  * Only authenticated users can view their pending friend requests.
  * If the request is made by an unauthenticated user, a `401 Unauthorized` response will be returned.

## URL Parameters

None required, but query parameters are available for filtering.

## Query Parameters

| Parameter   | Type   | Required | Default    | Description                                               |
| :---------- | :----- | :------- | :--------- | :-------------------------------------------------------- |
| `direction` | String | No       | "received" | Filter requests by direction. Valid values: "sent", "received" |
| `page`      | Integer| No       | 1          | Page number for pagination.                               |

## Request Headers

| Header        | Value                 | Required | Description                                     |
| :------------ | :-------------------- | :------- | :---------------------------------------------- |
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication.                 |
| `Content-Type`  | `application/json`    | No       | Not strictly required for GET, but good practice. |

## Request Body

No request body is required for a `GET` request to this endpoint.

## Successful Response

**Status Code:** `200 OK`

The response will contain a paginated JSON object with a list of pending friend requests.

**Example JSON Response (Received Requests):**

	```json
	{
	    "count": 3,
	    "next": null,
	    "previous": null,
	    "results": [
	        {
	            "id": 15,
	            "sender_id": 7,
	            "receiver_id": 3,
	            "sender_profile_url": "/api/users/7/profile/",
	            "receiver_profile_url": "/api/users/3/profile/",
	            "created_at": "2024-01-15 16:45:10",
	            "accept_url": "/api/friend-requests/15/accept/",
	            "decline_url": "/api/friend-requests/15/decline/"
	        },
	        {
	            "id": 12,
	            "sender_id": 5,
	            "receiver_id": 3,
	            "sender_profile_url": "/api/users/5/profile/",
	            "receiver_profile_url": "/api/users/3/profile/",
	            "created_at": "2024-01-15 14:30:25",
	            "accept_url": "/api/friend-requests/12/accept/",
	            "decline_url": "/api/friend-requests/12/decline/"
	        }
	    ]
	}
	```

**Example JSON Response (Sent Requests):**

	```json
	{
	    "count": 2,
	    "next": null,
	    "previous": null,
	    "results": [
	        {
	            "id": 18,
	            "sender_id": 3,
	            "receiver_id": 9,
	            "sender_profile_url": "/api/users/3/profile/",
	            "receiver_profile_url": "/api/users/9/profile/",
	            "created_at": "2024-01-15 17:20:30",
	            "accept_url": "/api/friend-requests/18/accept/",
	            "decline_url": "/api/friend-requests/18/decline/"
	        }
	    ]
	}
	```

**Response Fields:**

| Field        | Type    | Description                                                     |
| :----------- | :------ | :-------------------------------------------------------------- |
| `count`      | Integer | Total number of pending friend requests.                       |
| `next`       | String  | URL for the next page of results (null if no next page).      |
| `previous`   | String  | URL for the previous page of results (null if no previous page).|
| `results`    | Array   | Array of friend request objects.                              |

**Friend Request Object Fields:**

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
  * **Reason:** User profile not found or invalid query parameters.
  * **Response Body:**

	```json
	{
	    "detail": "User profile not found."
	}
	```

## Usage Examples

**Get received friend requests:**
`GET /api/friend-requests/pending/`
or
`GET /api/friend-requests/pending/?direction=received`

**Get sent friend requests:**
`GET /api/friend-requests/pending/?direction=sent`

**Get second page of received requests:**
`GET /api/friend-requests/pending/?page=2`
