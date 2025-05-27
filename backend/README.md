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

## 📌 Todo

The Current Main Quest is to create a Lightweight Chat System - https://github.com/ibrahim-sisar/EduLite/issues/19

 [-] Define User, ChatRoom, Message models

 [-] Setup authentication system

 [] Create APIs for messaging and assignments
