# Privacy Settings Choices

Returns the available choices for privacy settings fields, useful for building form dropdowns and validation.

## Endpoint URL

`/api/privacy-settings/choices/`

## HTTP Method

`GET`

## Permissions

* **Requires Authentication**: Yes
  * Only authenticated users can access privacy setting choices.
  * If the request is made by an unauthenticated user, a `401 Unauthorized` response will be returned.

## Request Headers

| Header        | Value                 | Required | Description                                     |
| :------------ | :-------------------- | :------- | :---------------------------------------------- |
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication.                 |

## Request Body

No request body is required for this endpoint.

## Successful Response

**Status Code:** `200 OK`

The response contains all available choices for privacy settings fields in a structured format.

**Example JSON Response:**

```json
{
    "search_visibility_choices": [
        {
            "value": "everyone",
            "label": "Everyone"
        },
        {
            "value": "friends_of_friends",
            "label": "Friends of Friends"
        },
        {
            "value": "friends_only",
            "label": "Friends Only"
        },
        {
            "value": "nobody",
            "label": "Nobody"
        }
    ],
    "profile_visibility_choices": [
        {
            "value": "public",
            "label": "Public"
        },
        {
            "value": "friends_only",
            "label": "Friends Only"
        },
        {
            "value": "private",
            "label": "Private"
        }
    ]
}
```

## Response Structure

### Top-Level Fields

| Field                         | Type  | Description                                    |
| :---------------------------- | :---- | :--------------------------------------------- |
| `search_visibility_choices`   | Array | Available options for search visibility       |
| `profile_visibility_choices`  | Array | Available options for profile visibility      |

### Choice Object Structure

Each choice object contains:

| Field   | Type   | Description                                    |
| :------ | :----- | :--------------------------------------------- |
| `value` | String | The value to use when setting the privacy option |
| `label` | String | Human-readable label for display in UI        |

## Error Responses

* **Status Code:** `401 Unauthorized`
  * **Reason:** Authentication credentials were not provided or were invalid.
  * **Response Body:**

```json
{
    "detail": "Authentication credentials were not provided."
}
```

* **Status Code:** `405 Method Not Allowed`
  * **Reason:** A method other than GET was used.
  * **Response Body:**

```json
{
    "detail": "Method \"POST\" not allowed."
}
```

## Usage Examples

### Frontend Implementation

This endpoint is typically used to populate form dropdowns:

```javascript
// Fetch choices for form building
fetch('/api/privacy-settings/choices/', {
    headers: {
        'Authorization': 'Bearer ' + accessToken
    }
})
.then(response => response.json())
.then(data => {
    // Populate search visibility dropdown
    const searchSelect = document.getElementById('search-visibility');
    data.search_visibility_choices.forEach(choice => {
        const option = document.createElement('option');
        option.value = choice.value;
        option.textContent = choice.label;
        searchSelect.appendChild(option);
    });

    // Populate profile visibility dropdown
    const profileSelect = document.getElementById('profile-visibility');
    data.profile_visibility_choices.forEach(choice => {
        const option = document.createElement('option');
        option.value = choice.value;
        option.textContent = choice.label;
        profileSelect.appendChild(option);
    });
});
```

### Validation

Use the returned choices to validate user input before submitting to the privacy settings update endpoint.

## Notes

* This endpoint returns static data that defines the available privacy options.
* The choices returned are consistent with what's accepted by the privacy settings update endpoints.
* Frontend applications should call this endpoint once and cache the results, as choices rarely change.
* The response format is designed to be easily consumed by form libraries and validation systems.
* Boolean fields (`show_full_name`, `show_email`, `allow_friend_requests`, `allow_chat_invites`) don't need choices as they only accept `true` or `false`.
