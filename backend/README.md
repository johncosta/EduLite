# 🧠 EduLite Backend

This is the backend part of EduLite – built with Django & Django REST Framework to serve APIs

## 🛠️ Tech Stack

- Python + Django  
- Django REST Framework  
- PostgreSQL / SQLite (for local dev)  
- Django JWT (for auth)

## 🗂️ Project Structure
```
backend/
├── EduLite/ # Django settings and project config
├── EduLite/media/ # Contains media for profile pictures
├── EduLite/users # App for managing users, includes registration
├── EduLite/chat # App for managing the lightweight chat system
├── project_choices_data/ # contains occupations.json, countries.json, etc.
├── README.md # backend documentation
└── manage.py
```


## 🚀 Getting Started

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Creating Dummy Users for Development

To populate your development database with sample users and profiles, use the `create_dummy_users` management command. This is helpful for testing UI components, APIs, and general development.

**How to Run:**

* To create 10 dummy users with the default password (`password123`):
    `python manage.py create_dummy_users 10`

* To create 25 dummy users with a custom password (e.g., `mynewpass`):
    `python manage.py create_dummy_users 25 --password mynewpass`

* For more options and help:
    `python manage.py create_dummy_users --help`

**Important Notes & TODOs:**

* **Development Use Only:** This command is intended for development and testing environments. Do not run it in production.
* **Default Password:** The default password for created users is `password123` unless overridden with the `--password` option. Ensure this is known by the development team.
* **Future Enhancements (TODO):** This command will be enhanced over time. Future versions may include arguments for:
    * Setting user status (e.g., `is_active`, email verification status).
    * Assigning users to specific groups.
    * Populating different profile types or more diverse profile data as new features are added to user profiles.

## 📌 Todo

The Current Main Quest is to create a Lightweight Chat System - https://github.com/ibrahim-sisar/EduLite/issues/19

 [-] Define User, ChatRoom, Message models

 [-] Setup authentication system

 [] Allow Users to search for each-other

 [] Setup views/models/serializers for friend-request system

 [] Integrate the `create_dummy_users` command with new friend-request system

 [] Setup e-mail verification for `is_active` on User model

 [] Create APIs for messaging and assignments

