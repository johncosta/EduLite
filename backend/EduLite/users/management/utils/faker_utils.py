from faker import Faker
import random

DEFAULT_FAKER = Faker()

# --- Basic Data ---
def get_random_username(faker_instance=None):
    fake = faker_instance or DEFAULT_FAKER
    return "test-" + fake.user_name().lower().replace(' ', '_') + str(random.randint(1000, 9999))

def get_random_email(username=None, faker_instance=None):
    fake = faker_instance or DEFAULT_FAKER
    if not username:
        username = get_random_username(fake)
    return f"{username}@example.edu"

def get_random_first_name(faker_instance=None):
    fake = faker_instance or DEFAULT_FAKER
    return fake.first_name()

def get_random_last_name(faker_instance=None):
    fake = faker_instance or DEFAULT_FAKER
    return fake.last_name()

def get_random_bio(num_sentences=None, faker_instance=None):
    fake = faker_instance or DEFAULT_FAKER
    if num_sentences is None:
        num_sentences = random.randint(2, 5)
    return fake.paragraph(nb_sentences=num_sentences)

# --- Utility for Choices ---
def get_random_choice_from_list(choices_list):
    if not choices_list:
        return None
    return random.choice(choices_list)

# --- EduLite Specific ---
def get_random_subject(faker_instance=None): # You already have this
    fake = faker_instance or DEFAULT_FAKER
    subjects = [
        "Applied Mathematics", "Astrophysics", "Bioinformatics", "Chemical Engineering",
        "Cognitive Science", "Creative Writing", "Data Science", "Digital Arts",
        "Environmental Policy", "Theoretical Physics", "Modern History", "Software Development"
    ]
    return random.choice(subjects)

def get_random_occupation(occupation_choices_list, faker_instance=None): # Renamed for clarity
    # occupation_choices_list should be a list of valid occupation values
    return get_random_choice_from_list(occupation_choices_list)

def get_random_country(country_choices_list, faker_instance=None): # Renamed for clarity
    return get_random_choice_from_list(country_choices_list)

def get_random_language(language_choices_list, faker_instance=None): # New generic language getter
    return get_random_choice_from_list(language_choices_list)

def get_random_profile_picture_path(picture_paths_list=None):
    if picture_paths_list:
        return get_random_choice_from_list(picture_paths_list)
    return None