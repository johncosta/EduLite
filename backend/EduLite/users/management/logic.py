from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
import random

from users.models import UserProfile
# Import your specific model choices if they are defined in models_choices.py

# Updated import path based on your file structure
from users.management.utils.faker_utils import (
    get_random_username,
    get_random_email,
    get_random_bio,
    get_random_first_name,
    get_random_last_name,
    get_random_subject, # Keep if 'subjects_studying' uses it directly
    get_random_occupation,
    get_random_country,
    get_random_language,
    get_random_profile_picture_path # If you implement this
)

User = get_user_model()

def generate_dummy_users_data(num_users: int, password: str):
    created_count = 0
    failed_count = 0
    created_users_list = []

    # Robustly fetch choices from model fields
    def get_choices_from_field(model, field_name):
        field = model._meta.get_field(field_name)
        return [choice[0] for choice in getattr(field, 'choices', []) if choice[0]]

    country_options = get_choices_from_field(UserProfile, 'country')
    occupation_options = get_choices_from_field(UserProfile, 'occupation')
    language_options = get_choices_from_field(UserProfile, 'preferred_language') # Assuming secondary uses same choices

    subjects_options = ["Mathematics", "Physics", "Computer Science", "History", "Literature", "Art", "Biology"]
    dummy_picture_paths = [
        'profile_pics/dummy/avatar1.png',
        'profile_pics/dummy/avatar2.jpg',
        'profile_pics/dummy/avatar3.jpeg',
    ]


    for i in range(num_users):
        username = get_random_username()
        email = get_random_email(username)
        first_name = get_random_first_name()
        last_name = get_random_last_name()

        try:
            with transaction.atomic():
                if User.objects.filter(username=username).exists() or \
                   User.objects.filter(email=email).exists():
                    print(f"Skipping user '{username}' ({email}) as username or email already exists.")
                    failed_count += 1
                    continue

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True
                )
                created_users_list.append(user)
                profile = user.userprofile

                # Populate UserProfile fields using faker_utils
                profile.bio = get_random_bio()
                profile.occupation = get_random_occupation(occupation_options)
                profile.country = get_random_country(country_options)
                profile.preferred_language = get_random_language(language_options)

                # Randomly decide if a secondary language is set
                if random.choice([True, False]):
                    profile.secondary_language = get_random_language(language_options)
                else:
                    profile.secondary_language = None # Or an empty string if your model allows/prefers


                # Randomly decide whether a profile picture is set
                if random.choice([True, False]):
                    # Handle 'picture'
                    # profile.picture = get_random_profile_picture_path(dummy_picture_paths)
                    # If using this, ensure the files exist at these paths relative to MEDIA_ROOT
                    # or handle ImageFieldFile assignment appropriately.
                    # For simplicity, you might leave it blank if picture is not mandatory.
                    profile.picture = get_random_profile_picture_path(dummy_picture_paths)

                profile.save()
                created_count += 1
                print(f"Successfully created user '{username}' and populated their profile.")

        except IntegrityError as e:
            print(f"Database integrity error for user '{username}': {e}. Skipping.")
            failed_count += 1
        except Exception as e:
            print(f"An unexpected error occurred while creating user '{username}': {e}. Skipping.")
            failed_count += 1

    # Friend connections logic (remains the same)
    if len(created_users_list) > 1:
        print("Establishing random friend connections...")
        for user_instance in created_users_list:
            profile = user_instance.userprofile
            potential_friends = [u for u in created_users_list if u.id != user_instance.id]
            if not potential_friends:
                continue
            num_friends_to_make = random.randint(0, min(len(potential_friends), 3))
            if num_friends_to_make > 0:
                friends_to_add = random.sample(potential_friends, num_friends_to_make)
                profile.friends.add(*friends_to_add)
                print(f"Added {len(friends_to_add)} friends to '{user_instance.username}'.")

    return created_count, failed_count