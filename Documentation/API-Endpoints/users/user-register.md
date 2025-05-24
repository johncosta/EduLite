# Register New User

Allows a new user to register for an account by providing a username, email, and password.

## Endpoint URL

`/api/register/`

## HTTP Method

`POST`

## Permissions

* **Requires Authentication**: No
  * This endpoint is open and does not require authentication, allowing anyone to register.

## Request Headers

| Header         | Value              | Required | Description                                       |
| :------------- | :----------------- | :------- | :------------------------------------------------ |
| `Content-Type` | `application/json` | Yes      | Specifies that the request body is in JSON format. |

## Request Body

The request body must be a JSON object containing the user's registration details.

**Fields:**

| Field        | Type   | Required | Description                                                                                                |
| :----------- | :----- | :------- | :--------------------------------------------------------------------------------------------------------- |
| `username`   | String | Yes      | The desired username for the new account. Must be unique.                                                  |
| `email`      | String | Yes      | The email address for the new account. Must be unique and a valid email format. Cannot be from blocked domains. |
| `password`   | String | Yes      | The desired password for the new account. Must meet password strength requirements.                          |
| `password2`  | String | Yes      | Confirmation of the password. Must match the `password` field.                                             |
| `first_name` | String | No       | The user's first name (optional).                                                                          |
| `last_name`  | String | No       | The user's last name (optional).                                                                           |

**Example Request Body:**

```json
{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "ComplexPassword123!",
    "password2": "ComplexPassword123!",
    "first_name": "Test", // optional
    "last_name": "User" // optional
}
```

## Successful Response

**Status Code:** `201 Created`

Upon successful registration, the API will return a message indicating success, along with the new user's ID and username.

**Example JSON Response:**

```json
{
    "message": "User created successfully.",
    "user_id": 101,
    "username": "newuser"
}
```

## Error Responses

* **Status Code:** `400 Bad Request`
  * **Reason:** The provided data is invalid. This can occur for several reasons, such as:
    * Passwords do not match.
    * Email is already in use or invalid.
    * Username is already taken.
    * Password does not meet complexity requirements.
    * Required fields are missing.
  * **Response Body (Example - Passwords do not match):**

```json
{
    "password2": [
        "Password fields didn't match."
    ]
}
```

* **Response Body (Example - Email already exists):**

```json
{
    "email": [
        "A user with this email address already exists."
    ]
}
```

* **Response Body (Example - Username already exists):**

```json
{
    "username": [
        "A user with that username already exists."
    ]
}
```

* **Response Body (Example - Invalid email domain):**

```json
{
    "email": [
        "Registration from this email domain is not allowed."
    ]
}
```
