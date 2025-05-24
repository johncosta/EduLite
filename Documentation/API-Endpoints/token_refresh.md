# Refresh Access Token

Allows a client to obtain a new JWT access token by submitting a valid, unexpired refresh token. This is used to extend a user's session after their initial access token has expired.

## Endpoint URL

`/api/token/refresh`

## HTTP Method

`POST`

## Permissions

* **Requires Authentication**: No (in the traditional sense)
  * This endpoint is typically open. The validity and presence of the `refresh` token in the request body serve as the authorization for this specific action.

## Request Headers

| Header         | Value              | Required | Description                                       |
| :------------- | :----------------- | :------- | :------------------------------------------------ |
| `Content-Type` | `application/json` | Yes      | Specifies that the request body is in JSON format. |

## Request Body

The request body must be a JSON object containing the refresh token.

**Fields:**

| Field     | Type   | Required | Description                                     |
| :-------- | :----- | :------- | :---------------------------------------------- |
| `refresh` | String | Yes      | The valid refresh token obtained during login. |

**Example Request Body:**

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxNjYxMzk4MywiaWF0IjoxNzE2NTI3NTgzLCJqdGkiOiJhYmNkZWZnMTIzNDU2Nzg5IiwidXNlcl9pZCI6MX0.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

## Successful Response

**Status Code:** `200 OK`

Upon successful validation of the refresh token, the API will return a JSON object containing a new `access` token.

*Note: By default, `djangorestframework-simplejwt` does not issue a new refresh token when an access token is refreshed. However, it can be configured to "rotate" refresh tokens, in which case a new refresh token would also be included in this response.*

**Example JSON Response (Default Behavior - No Refresh Token Rotation):**

```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE2NTMxMTgzLCJpYXQiOjE3MTY1Mjc1ODMsImp0aSI6ImRlZmdoaWprazEyMzQ1Njc4OSIsInVzZXJfaWQiOjF9.zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
}
```

## Error Responses

* **Status Code:** `400 Bad Request`
  * **Reason:** The `refresh` field is missing from the request body.
  * **Response Body (Example):**

```json
{
    "refresh": [
        "This field is required."
    ]
}
```

* **Status Code:** `401 Unauthorized`
  * **Reason:** The provided refresh token is invalid, expired, or has been blacklisted.
  * **Response Body (Example from Simple JWT `TokenError`):**

```json
{
    "detail": "Token is invalid or expired",
    "code": "token_not_valid"
}
```
