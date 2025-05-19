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
├── EduLite/users # App for managing users, includes registration
├── README.md/ # backend documentation
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
 [] Define User, ChatRoom, Message models

 [] Setup authentication system

 [] Create APIs for messaging and assignments
