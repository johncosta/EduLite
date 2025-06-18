# User Privacy Settings

Allows an authenticated user to retrieve and update their privacy settings that control visibility and interaction permissions.

## Endpoint URL

`/api/privacy-settings/`

## HTTP Methods

`GET`, `PUT`, `PATCH`

## Permissions

* **Requires Authentication**: Yes
  * Only authenticated users can access their privacy settings.
  * If the request is made by an unauthenticated user, a `401 Unauthorized` response will be returned.
* **User Scope**: Own settings only
  * Users can only access and modify their own privacy settings.
  * The system automatically uses the authenticated user's settings.

## Request Headers

| Header        | Value                 | Required | Description                                     |
| :------------ | :-------------------- | :------- | :---------------------------------------------- |
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication.                 |
| `Content-Type`  | `application/json`    | Yes*     | Required for PUT and PATCH requests.           |

*Not required for GET requests.

## GET - Retrieve Privacy Settings

### Request Body

No request body is required for GET requests.

### Successful Response

**Status Code:** `200 OK`

**Example JSON Response:**

```json
{
    "search_visibility": "everyone",
    "profile_visibility": "friends_only",
    "show_full_name": true,
    "show_email": false,
    "allow_friend_requests": true,
    "allow_chat_invites": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:45:00Z"
}
```

## PUT - Full Update Privacy Settings

### Request Body

All fields are required for a full update.

**Example JSON Request:**

```json
{
    "search_visibility": "friends_only",
    "profile_visibility": "private",
    "show_full_name": false,
    "show_email": false,
    "allow_friend_requests": true,
    "allow_chat_invites": false
}
```

### Request Body Parameters

| Field                | Type    | Required | Description                                           |
| :------------------- | :------ | :------- | :---------------------------------------------------- |
| `search_visibility`  | String  | Yes      | Who can find you in search. See choices below.       |
| `profile_visibility` | String  | Yes      | Who can view your full profile. See choices below.   |
| `show_full_name`     | Boolean | Yes      | Whether to show your first and last name.            |
| `show_email`         | Boolean | Yes      | Whether to show your email address in profile.       |
| `allow_friend_requests` | Boolean | Yes   | Whether others can send you friend requests.         |
| `allow_chat_invites` | Boolean | Yes      | Whether others can send you chat invitations.        |

### Successful Response

**Status Code:** `200 OK`

Returns the updated privacy settings with the same format as the GET response.

## PATCH - Partial Update Privacy Settings

### Request Body

Only include the fields you want to update.

**Example JSON Request:**

```json
{
    "search_visibility": "friends_of_friends",
    "allow_chat_invites": false
}
```

### Successful Response

**Status Code:** `200 OK`

Returns the updated privacy settings with the same format as the GET response.

## Field Choices

### Search Visibility Options

| Value               | Label               | Description                                    |
| :------------------ | :------------------ | :--------------------------------------------- |
| `everyone`          | Everyone            | Anyone can find you in search results         |
| `friends_of_friends`| Friends of Friends  | Only friends and friends of friends can find you |
| `friends_only`      | Friends Only        | Only your friends can find you in search      |
| `nobody`            | Nobody              | You won't appear in search results            |

### Profile Visibility Options

| Value        | Label        | Description                                    |
| :----------- | :----------- | :--------------------------------------------- |
| `public`     | Public       | Anyone can view your full profile             |
| `friends_only` | Friends Only | Only your friends can view your full profile |
| `private`    | Private      | Only you can view your full profile           |

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
  * **Reason:** Invalid data was provided in the request body.
  * **Response Body:**

```json
{
    "search_visibility": [
        "\"invalid_choice\" is not a valid choice."
    ],
    "show_full_name": [
        "This field is required."
    ]
}
```

## Notes

* Privacy settings are automatically created when a user profile is created.
* If privacy settings don't exist for a user (edge case), they will be created automatically with default values.
* Changes to privacy settings take effect immediately and affect search visibility and profile access.
* The `updated_at` timestamp is automatically updated when any changes are made.
* Some combinations of settings may have validation rules (e.g., search visibility "nobody" with profile visibility "public" may be restricted).
