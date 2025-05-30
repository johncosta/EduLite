---
name: "Newbie Backend Task"
about: "A beginner-friendly backend (Django/Python) task for EduLite contributors."
title: "[NEWBIE-BACKEND] Brief title describing the task"
labels: 'good first issue, backend, help wanted'
assignees: ''

---

## **🎯 Goal / Objective**

*Concisely describe what the contributor will achieve by completing this backend task. What is the main aim of this change or addition?*
*(Example: To add a new, non-essential field to the `UserProfile` model to store a user's favorite quote, and expose it in the ProfileSerializer.)*

## **📝 Task Description / Requirements**

*Provide a clear, step-by-step description of what needs to be done on the backend. Be specific about models to modify, expected API behavior (if any), or database changes.*
*(Example:*

1. Locate the `UserProfile` model in `backend/users/models.py`.
2. Add a new `CharField` named `favorite_quote` to the `UserProfile` model. It can be `blank=True`, `null=True`, with a `max_length` of 255.
3. Make and apply database migrations for this change (`python manage.py makemigrations users` and `python manage.py migrate`).
4. Add `favorite_quote` to the `fields` list in the `ProfileSerializer` in `backend/users/serializers.py` so it can be viewed and updated via the API.
5. Register the new field in the `UserProfileAdmin` in `backend/users/admin.py` if applicable, so it's visible in the Django admin panel.)*

## **✨ Benefits / Why this helps EduLite**

*Explain how completing this task will benefit the EduLite project, its backend functionality, data structure, or prepare it for future features.*
*(Example: This allows users to personalize their profiles further. It also gives a new contributor experience with Django model changes, migrations, and serializer updates.)*

## **🛠️ Skills Required**

*List the specific backend skills or technologies the contributor will need or will get a chance to practice. Be encouraging!*
*(Example:*
* *Basic Python syntax.*
* *Understanding of Django models and field types.*
* *Familiarity with Django migrations.*
* *Basic knowledge of Django REST Framework serializers (how to add a field).*
* *(Optional) Django admin customization.*
* *Git and GitHub for creating a branch and submitting a pull request (we're here to help!).)*

## **📚 Helpful Resources / Getting Started**

*Provide links to relevant Django/Python documentation, specific files in the `backend/` directory, or sections of the contribution guide relevant to backend development. Point them to where they can ask questions.*
*(Example:*
* *Django Model Field Reference: [https://docs.djangoproject.com/en/stable/ref/models/fields/](https://docs.djangoproject.com/en/stable/ref/models/fields/)*
* *Django Migrations: [https://docs.djangoproject.com/en/stable/topics/migrations/](https://docs.djangoproject.com/en/stable/topics/migrations/)*
* *Django REST Framework Serializers: [https://www.django-rest-framework.org/api-guide/serializers/](https://www.django-rest-framework.org/api-guide/serializers/)*
* *Relevant Files: `backend/users/models.py`, `backend/users/serializers.py`*
* *EduLite Backend README: `backend/README.md`*
* *EduLite Contributing Guide: `CONTRIBUTING.md`*
* *Feel free to ask questions in our Discord server's #backend channel!)*

## **💻 Files to be Altered or Created (if known)**

*List any specific files or directories within the `backend/` codebase that you believe will need to be modified or created.*
*(Example: `backend/users/models.py`, `backend/users/serializers.py`, new migration file in `backend/users/migrations/`)*

## **🧪 Testing Considerations (Optional)**

*Briefly mention any testing aspects the contributor should consider. This could be manual testing steps or ideas for simple automated tests.*
*(Example: "After making the changes, find the corresponding test in tests/test_classname.py and alter any failing tests, or add your own new ones.)*

## **💡 Additional Context / Tips (Optional)**

*Add any other helpful context, tips for approaching the backend problem, or relevant information about the existing backend setup. This is a good place for encouragement!*
*(Example: "Remember to activate your Python virtual environment before running `manage.py` commands. If you add a field to a model, Django's `makemigrations` command will create the migration file for you. We appreciate your contribution to improving EduLite's backend!")*

---
*This task is designed as a good entry point for new backend contributors. We're here to support you through the process!*
