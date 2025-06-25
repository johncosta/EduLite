# backend/EduLite/users/tests/functions/test_validate_search_query.py
# Tests for the validate_search_query function from user_search_logic.py

from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response

from users.logic.user_search_logic import validate_search_query


class ValidateSearchQueryTests(TestCase):
    """
    Test suite for the validate_search_query function.
    Tests validation logic for search query parameters.
    """

    def test_valid_search_query_returns_true(self):
        """Test that a valid search query returns True with no error response."""
        query = "john"
        is_valid, error_response = validate_search_query(query)

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)

    def test_valid_search_query_with_minimum_length(self):
        """Test that a query with exactly minimum length is valid."""
        query = "ab"  # Default minimum length is 2
        is_valid, error_response = validate_search_query(query)

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)

    def test_valid_search_query_with_custom_minimum_length(self):
        """Test validation with custom minimum length."""
        query = "abc"
        is_valid, error_response = validate_search_query(query, min_length=3)

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)

    def test_empty_string_query_returns_false(self):
        """Test that an empty string query returns False with error response."""
        query = ""
        is_valid, error_response = validate_search_query(query)

        self.assertFalse(is_valid)
        self.assertIsInstance(error_response, Response)
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Search query is required", str(error_response.data))

    def test_none_query_returns_false(self):
        """Test that a None query returns False with error response."""
        query = None
        is_valid, error_response = validate_search_query(query)

        self.assertFalse(is_valid)
        self.assertIsInstance(error_response, Response)
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_whitespace_only_query_returns_false(self):
        """Test that a whitespace-only query returns False with error response."""
        query = "   "
        is_valid, error_response = validate_search_query(query)

        self.assertFalse(is_valid)
        self.assertIsInstance(error_response, Response)
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_too_short_returns_false(self):
        """Test that a query shorter than minimum length returns False."""
        query = "a"  # Only 1 character, default min is 2
        is_valid, error_response = validate_search_query(query)

        self.assertFalse(is_valid)
        self.assertIsInstance(error_response, Response)
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("must be at least 2 characters long", str(error_response.data))

    def test_query_too_short_with_custom_minimum(self):
        """Test validation with custom minimum length requirement."""
        query = "ab"  # 2 characters, but min_length is 3
        is_valid, error_response = validate_search_query(query, min_length=3)

        self.assertFalse(is_valid)
        self.assertIsInstance(error_response, Response)
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("must be at least 3 characters long", str(error_response.data))

    def test_query_with_leading_trailing_whitespace(self):
        """Test that queries with leading/trailing whitespace are handled correctly."""
        query = "  john  "
        is_valid, error_response = validate_search_query(query)

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)

    def test_unicode_query_is_valid(self):
        """Test that Unicode characters in query are handled correctly."""
        query = "José"
        is_valid, error_response = validate_search_query(query)

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)
