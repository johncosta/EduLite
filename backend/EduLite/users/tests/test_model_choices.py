from django.test import TestCase
from django.conf import settings

import json

from ..models_choices import load_choices_from_json


class ModelChoicesIntegrationTests(TestCase):
    """
    Integration tests for model choices.
    """

    def test_load_occupations(self):
        """
        Test that the occupations choices are loaded correctly.
        """
        choices_list = load_choices_from_json("occupations.json")
        # Does it have student as a value?
        self.assertIn(("student", "Student"), choices_list)
        # Does it have teacher as a value?
        self.assertIn(("teacher", "Teacher"), choices_list)
        # Does it have 'other' as a value?
        self.assertIn(("other", "Other"), choices_list)
        # Does it have 'admin' as a value?
        self.assertIn(("admin", "Admin"), choices_list)

    def test_load_countries(self):
        """
        Test that the countries choices are loaded correctly.
        """
        choices_list = load_choices_from_json("countries.json")
        # Does it have 'CA' as a value?
        self.assertIn(("CA", "Canada"), choices_list)
        # Does it have 'US' as a value?
        self.assertIn(("US", "United States"), choices_list)
        # Does it have 'UK' as a value?
        self.assertIn(("UK", "United Kingdom"), choices_list)
        # Does it have 'IN' as a value?
        self.assertIn(("IN", "India"), choices_list)

    def test_load_languages(self):
        """
        Test that the languages choices are loaded correctly.
        """
        choices_list = load_choices_from_json("languages.json")
        # Does it have 'en' as a value?
        self.assertIn(("en", "English"), choices_list)
        # Does it have 'fr' as a value?
        self.assertIn(("fr", "French"), choices_list)
        # Does it have 'es' as a value?
        self.assertIn(("es", "Spanish"), choices_list)
        # Does it have 'ar' as a value?
        self.assertIn(("ar", "Arabic"), choices_list)
