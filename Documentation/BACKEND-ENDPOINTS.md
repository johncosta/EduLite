# EduLite Backend API Endpoints

This document provides details for interacting with the EduLite backend API.

## General API Information

* **Base URL (Development):** `http://localhost:8000/api/`
  
* **Data Format:** All request and response bodies are in JSON format.
  
* **Authentication:** For protected endpoints, JWT (JSON Web Token) authentication is used. Tokens must be sent in the `Authorization` header as `Bearer <access_token>`.

---

## Authentication Endpoints

These endpoints are provided by `djangorestframework-simplejwt` and are used to obtain and refresh JSON Web Tokens.

### 1. Obtain Token Pair (Login)

* **Purpose:** Allows a registered user to obtain an access token and a refresh token by providing their username and password.
* **HTTP Method:** `POST`
* **URL Path:** `/token/` *(Assuming base URL is `/api/`, so full path is `/api/token/`)*
* **Headers:**
    * `Content-Type: application/json`
* **Request Body:**
    * **`username`** (string, required): The user's registered username.
    * **`password`** (string, required): The user's password.
    * **Example:**
        ```json
        {
            "username": "testuser",
            "password": "testpassword123"
        }
        ```
* **Success Response:**
    * **Status Code:** `200 OK`
    * **Body Example:**
        ```json
        {
            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2...",
            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2..."
        }
        ```
        * `access`: The JWT access token. Used to authenticate subsequent requests to protected API endpoints.
        * `refresh`: The JWT refresh token. Used to obtain a new access token once the current one expires.
* **Error Responses:**
    * **Status Code:** `401 Unauthorized`
        * **Reason:** Invalid credentials (username or password incorrect).
        * **Body Example:**
            ```json
            {
                "detail": "No active account found with the given credentials"
            }
            ```
    * **Status Code:** `400 Bad Request`
        * **Reason:** Missing `username` or `password` in the request body.
        * **Body Example (missing password):**
            ```json
            {
                "password": ["This field is required."]
            }
            ```

### 2. Refresh Access Token

* **Purpose:** Allows a client to obtain a new access token using a valid refresh token, typically after the original access token has expired.
* **HTTP Method:** `POST`
* **URL Path:** `/token/refresh/` *(Assuming base URL is `/api/`, so full path is `/api/token/refresh/`)*
* **Headers:**
    * `Content-Type: application/json`
* **Request Body:**
    * **`refresh`** (string, required): The refresh token obtained during login.
    * **Example:**
        ```json
        {
            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2..."
        }
        ```
* **Success Response:**
    * **Status Code:** `200 OK`
    * **Body Example:**
        ```json
        {
            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2Nlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE2MjM1MjYxLCJpYXQiOjE3MTYyMzQ5NjEsImp0aSI6ImZmY2U0ZjQzNTg4MDRkYmZiMjkxNjg0NWMxZTVhYjU4IiwidXNlcl9pZCI6MX0.new_access_token_value"
        }
        ```
        * `access`: The new JWT access token.
* **Error Responses:**
    * **Status Code:** `401 Unauthorized`
        * **Reason:** The refresh token is invalid, expired, or blacklisted.
        * **Body Example:**
            ```json
            {
                "detail": "Token is invalid or expired",
                "code": "token_not_valid"
            }
            ```
    * **Status Code:** `400 Bad Request`
        * **Reason:** Missing `refresh` token in the request body.
        * **Body Example:**
            ```json
            {
                "refresh": ["This field is required."]
            }
            ```

---

## User & Group Endpoints

These endpoints are provided by the `users` app and are used to manage users and groups.

### User Registration

* **Purpose:** Allows a new user to register an account.
* **HTTP Method:** `POST`
* **URL Path:** `/register/`
* **Permissions:** Public (No authentication required).
* **Headers:**
    * `Content-Type: application/json`
* **Request Body:**
    * **`username`** (string, required): Desired username.
    * **`password`** (string, required): Desired password.
    * **`email`** (string, required): User's email.
    * **`first_name`** (string, optional): User's first name.
    * **`last_name`** (string, optional): User's last name.
    * **Example:**
        ```json
        {
            "username": "newuser",
            "password": "strongpassword123",
            "email": "newuser@example.com"
        }
        ```
* **Success Response:**
    * **Status Code:** `201 Created`
    * **Body Example:** 
        ```json
        {
            "id": 2,
            "username": "newuser",
            "email": "newuser@example.com"
            // ... other user fields from your UserSerializer
        }
        ```
* **Error Responses:**
    * **Status Code:** `400 Bad Request`
        * **Reason:** Invalid data (e.g., username already exists, password too weak, email invalid).
        * **Body Example:**
            ```json
            {
                "username": ["A user with that username already exists."],
                "password": ["This password is too common."]
            }
            ```

### List Users

* **Purpose:** Retrieves a list of users.
* **HTTP Method:** `GET`
* **URL Path:** `/users/`
* **Permissions:** Authenticated users (Likely admin/staff only, or needs further definition).
* **Headers:**
    * `Authorization: Bearer <access_token>`
* **Query Parameters:**
    * `page` (optional, integer): For pagination.
* **Success Response:**
    * **Status Code:** `200 OK`
    * **Body Example:** (Paginated list of user objects from `UserSerializer`)
        ```json
        {
            "count": 100,
            "next": "/api/users/?page=2",
            "previous": null,
            "results": [
                { "id": 1, "username": "user1", "email": "user1@example.com" /* ... */ },
                { "id": 2, "username": "user2", "email": "user2@example.com" /* ... */ }
            ]
        }
        ```
* **Error Responses:**
    * `401 Unauthorized`: If authentication is required and token is missing/invalid.
    * `403 Forbidden`: If the authenticated user does not have permission to list users.

### Retrieve User Details

* **Purpose:** Retrieves details for a specific user.
* **HTTP Method:** `GET`
* **URL Path:** `/users/<int:pk>/`
* **Permissions:** Authenticated users (User can retrieve their own details, or admin/staff for others).
* **Headers:**
    * `Authorization: Bearer <access_token>`
* **Success Response:**
    * **Status Code:** `200 OK`
    * **Body Example:** (A single user object from `UserSerializer`)
        ```json
        { "id": 1, "username": "user1", "email": "user1@example.com" /* ... */ }
        ```
* **Error Responses:**
    * `401 Unauthorized`
    * `403 Forbidden`
    * `404 Not Found`: If user with `pk` does not exist.

### Update User Details

* **Purpose:** Updates details for a specific user.
* **HTTP Method:** `PUT` or `PATCH`
* **URL Path:** `/users/<int:pk>/update/`
* **Permissions:** Authenticated users (User can update their own details, or admin/staff for others).
* **Headers:**
    * `Content-Type: application/json`
    * `Authorization: Bearer <access_token>`
* **Request Body:**
    * Fields from `UserSerializer` that are allowed to be updated (e.g., `email`, `first_name`, `last_name`).
    * **Example (`PATCH`):**
        ```json
        {
            "email": "updated_email@example.com"
        }
        ```
* **Success Response:**
    * **Status Code:** `200 OK`
    * **Body Example:** (The updated user object)
        ```json
        { "id": 1, "username": "user1", "email": "updated_email@example.com" /* ... */ }
        ```
* **Error Responses:**
    * `400 Bad Request`: Invalid data.
    * `401 Unauthorized`
    * `403 Forbidden`
    * `404 Not Found`

### List/Create Groups

* **Purpose:** Retrieves a list of user groups or creates a new group.
* **HTTP Method:** `GET` (List), `POST` (Create)
* **URL Path:** `/groups/`
* **Permissions:** Authenticated users (Likely admin/staff only).
* **Headers:**
    * `Authorization: Bearer <access_token>`
    * `Content-Type: application/json` (for `POST`)
* **Request Body (`POST`):**
    * **`name`** (string, required): Name of the new group.
    * **Example:**
        ```json
        { "name": "Editors" }
        ```
* **Success Response (`GET`):**
    * **Status Code:** `200 OK`
    * **Body Example:** (Paginated list of group objects from your `GroupSerializer`)
        ```json
        {
            "count": 5,
            "next": null,
            "previous": null,
            "results": [
                { "id": 1, "name": "Administrators" /* ... */ },
                { "id": 2, "name": "Teachers" /* ... */ }
            ]
        }
        ```
* **Success Response (`POST`):**
    * **Status Code:** `201 Created`
    * **Body Example:** (The created group object)
        ```json
        { "id": 3, "name": "Editors" }
        ```
* **Error Responses:**
    * `400 Bad Request` (for `POST` with invalid data).
    * `401 Unauthorized`
    * `403 Forbidden`

### Retrieve/Update/Delete Group Details

* **Purpose:** Retrieves, updates, or deletes a specific user group.
* **HTTP Method:** `GET` (Retrieve), `PUT`/`PATCH` (Update), `DELETE` (Delete)
* **URL Path:** `/groups/<int:pk>/`
* **Permissions:** Authenticated users (Likely admin/staff only).
* **Headers:**
    * `Authorization: Bearer <access_token>`
    * `Content-Type: application/json` (for `PUT`/`PATCH`)
* **Request Body (`PUT`/`PATCH`):**
    * **`name`** (string): New name for the group.
    * **Example (`PATCH`):**
        ```json
        { "name": "Super Editors" }
        ```
* **Success Response (`GET`, `PUT`/`PATCH`):**
    * **Status Code:** `200 OK`
    * **Body Example:** (The group object)
        ```json
        { "id": 3, "name": "Super Editors" }
        ```
* **Success Response (`DELETE`):**
    * **Status Code:** `204 No Content`
* **Error Responses:**
    * `400 Bad Request` (for `PUT`/`PATCH` with invalid data).
    * `401 Unauthorized`
    * `403 Forbidden`
    * `404 Not Found`

---

*As more API endpoints are added to the EduLite backend (e.g., for chat, courses), they will be documented here.*
