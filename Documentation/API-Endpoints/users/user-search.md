# User Search

Allows authenticated users to search for other users by username, first name, or last name. Search results respect user privacy settings and relationship status.

## Endpoint URL

`/api/users/search/`

## HTTP Method

`GET`

## Permissions

* **Requires Authentication**: Yes
  * Only authenticated users can search for other users.
  * If the request is made by an unauthenticated user, a `401 Unauthorized` response will be returned.

## Request Headers

| Header        | Value                 | Required | Description                                     |
| :------------ | :-------------------- | :------- | :---------------------------------------------- |
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication.                 |

## Query Parameters

| Parameter | Type   | Required | Description                                     |
| :-------- | :----- | :------- | :---------------------------------------------- |
| `q`       | String | Yes      | Search query (minimum 2 characters)            |
| `page`    | Integer| No       | Page number for pagination (default: 1)        |

## Request Body

No request body is required for this endpoint.

## Successful Response

**Status Code:** `200 OK`

The response contains paginated search results with users matching the search query.

**Example JSON Response:**

```json
{
    "count": 15,
    "next": "http://example.com/api/users/search/?q=john&page=2",
    "previous": null,
    "results": [
        {
            "id": 123,
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "is_active": true,
            "date_joined": "2024-01-15T10:30:00Z"
        },
        {
            "id": 124,
            "username": "johnny_smith",
            "first_name": "Johnny",
            "last_name": "Smith",
            "email": "johnny@example.com",
            "is_active": true,
            "date_joined": "2024-01-10T08:15:00Z"
        }
    ]
}
```

## Response Structure

### Pagination Fields

| Field      | Type    | Description                                    |
| :--------- | :------ | :--------------------------------------------- |
| `count`    | Integer | Total number of users matching the search     |
| `next`     | String  | URL for the next page (null if last page)     |
| `previous` | String  | URL for the previous page (null if first page)|
| `results`  | Array   | Array of user objects for current page        |

### User Object Fields

| Field        | Type    | Description                                    |
| :----------- | :------ | :--------------------------------------------- |
| `id`         | Integer | Unique identifier for the user                 |
| `username`   | String  | User's username                                |
| `first_name` | String  | User's first name                              |
| `last_name`  | String  | User's last name                               |
| `email`      | String  | User's email address                           |
| `is_active`  | Boolean | Whether the user account is active             |
| `date_joined`| String  | ISO timestamp when user joined                 |

## Privacy Features

### Search Visibility Controls

The search results are filtered based on each user's privacy settings:

#### Search Visibility Levels

| Setting             | Who Can Find This User                          |
| :------------------ | :---------------------------------------------- |
| `everyone`          | All authenticated users can find them          |
| `friends_only`      | Only their friends can find them               |
| `friends_of_friends`| Friends and friends of friends can find them   |
| `nobody`            | No one can find them in search (except self)   |

#### Privacy Logic

1. **Self-Discovery**: Users can always find themselves in search results regardless of their privacy settings.

2. **Everyone Visibility**: Users with `everyone` search visibility appear in all authenticated users' search results.

3. **Friends Only**: Users with `friends_only` visibility only appear in search results for users who are in their friends list.

4. **Friends of Friends**: Users with `friends_of_friends` visibility appear in search results for:
   - Direct friends
   - Users who share mutual friends with them

5. **Nobody Visibility**: Users with `nobody` visibility don't appear in anyone's search results except their own.

### Search Behavior

- **Case Insensitive**: Search queries are case-insensitive (`john` matches `John`, `JOHN`, etc.)
- **Partial Matching**: Search matches partial usernames, first names, and last names
- **Multiple Fields**: A single query searches across username, first name, and last name
- **Distinct Results**: Users matching in multiple fields appear only once
- **Active Users Only**: Only active user accounts appear in search results
- **Ordered Results**: Results are ordered alphabetically by username

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
  * **Reason:** Invalid search query (empty or too short).
  * **Response Body:**

```json
{
    "detail": "Search query is required."
}
```

```json
{
    "detail": "Search query must be at least 2 characters long."
}
```

## Pagination

- **Default Page Size**: 10 users per page
- **Navigation**: Use `next` and `previous` URLs for pagination
- **Page Parameter**: Use `?page=N` to access specific pages
- **Count**: Total matching users (across all pages) shown in `count`

## Usage Examples

### Basic Search

```bash
GET /api/users/search/?q=john
Authorization: Bearer your_access_token
```

### Search with Pagination

```bash
GET /api/users/search/?q=smith&page=2
Authorization: Bearer your_access_token
```

### Frontend Implementation

```javascript
// Search for users
async function searchUsers(query, page = 1) {
    const response = await fetch(`/api/users/search/?q=${encodeURIComponent(query)}&page=${page}`, {
        headers: {
            'Authorization': 'Bearer ' + accessToken,
            'Content-Type': 'application/json'
        }
    });

    if (response.ok) {
        return await response.json();
    } else {
        throw new Error('Search failed');
    }
}

// Usage
searchUsers('john')
    .then(data => {
        console.log(`Found ${data.count} users`);
        data.results.forEach(user => {
            console.log(`${user.first_name} ${user.last_name} (@${user.username})`);
        });
    })
    .catch(error => {
        console.error('Search error:', error);
    });
```

## Privacy Impact Examples

### Example Scenarios

1. **Public User Search**:
   - User A has `everyone` search visibility
   - Any authenticated user can find User A by searching their name

2. **Friends Only Search**:
   - User B has `friends_only` search visibility
   - User B is friends with User C
   - User C can find User B in search, but User D (not a friend) cannot

3. **Friends of Friends Search**:
   - User E has `friends_of_friends` search visibility
   - User E is friends with User F
   - User F is friends with User G
   - User G can find User E through their mutual connection with User F

4. **Private User Search**:
   - User H has `nobody` search visibility
   - Only User H can find themselves when searching
   - No other users can discover User H through search

## Notes

* Search functionality respects all user privacy settings in real-time
* Privacy settings changes take effect immediately on search results
* Friend relationships are bidirectional and affect search visibility
* Inactive user accounts are automatically excluded from search results
* Search queries are trimmed of whitespace automatically
* The search uses database-level filtering for optimal performance
* Results are cached efficiently to handle high search volumes
* Users always appear in their own search results regardless of privacy settings
