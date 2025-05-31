# backend/users/
import logging

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.db.models import Q

logger = logging.getLogger(__name__)
User = get_user_model()

class UserSearchViewTests(APITestCase):
    """
    Test suite for the UserSearchView.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        cls.search_url = reverse('user-search') # Make sure 'user-search' is the name in your urls.py

        # User who will perform the searches
        cls.searching_user = User.objects.create_user(username='searcher', password='password123')

        # Users to be searched
        cls.user_alpha = User.objects.create_user(
            username='alpha_user', 
            first_name='Alpha', 
            last_name='One', 
            email='alpha@example.com',
            is_active=True
        )
        cls.user_beta_firstname = User.objects.create_user(
            username='beta_user', 
            first_name='BetaTest', 
            last_name='Two',
            email='beta@example.com',
            is_active=True
        )
        cls.user_gamma_lastname = User.objects.create_user(
            username='gamma_user', 
            first_name='Gamma', 
            last_name='TestThree',
            email='gamma@example.com',
            is_active=True
        )
        cls.user_delta_inactive = User.objects.create_user(
            username='delta_inactive_tester', 
            first_name='Delta', 
            last_name='Four',
            email='delta@example.com',
            is_active=False # Inactive user
        )
        cls.user_epsilon_nomatch = User.objects.create_user(
            username='epsilon_user', 
            first_name='Epsilon', 
            last_name='Five',
            email='epsilon@example.com',
            is_active=True
        )
        cls.user_zeta_case = User.objects.create_user(
            username='ZETA_USER_CASE',
            first_name='Zeta',
            last_name='SixTest',
            email='zeta@example.com',
            is_active=True
        )

    def setUp(self):
        """Authenticate the client for each test."""
        self.client.force_authenticate(user=self.searching_user)

    def test_search_requires_authentication(self):
        """
        Test that unauthenticated users cannot access the search endpoint.
        """
        self.client.logout() # Ensure no authentication
        response = self.client.get(self.search_url, {'q': 'test'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_with_empty_query(self):
        """
        Test that an empty query string returns a 400 Bad Request.
        (Based on your UserSearchView implementation detail for empty/short query)
        """
        response = self.client.get(self.search_url, {'q': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Search query must be at least", response.data.get('detail', ''))

    def test_search_with_short_query(self):
        """
        Test that a query string shorter than MIN_QUERY_LENGTH (e.g., 2) returns a 400.
        """
        logger.debug("test_search_with_short_query():")
        response = self.client.get(self.search_url, {'q': 'a'}) # Assuming MIN_QUERY_LENGTH is 2 or 3
        logger.debug(
            f"--\t response.status_code: {response.status_code}\n"
            f"--\t response.data['detail']: {response.data.get('detail', '')}\n"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Search query must be at least", response.data.get('detail', ''))

    def test_search_by_username_exact(self):
        """Test searching by a part of the username."""
        response = self.client.get(self.search_url, {'q': 'alpha_user'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'], self.user_alpha.username)

    def test_search_by_username_partial(self):
        """Test searching by a part of the username."""
        response = self.client.get(self.search_url, {'q': 'alpha'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'], self.user_alpha.username)

    def test_search_by_first_name(self):
        """Test searching by a part of the first name."""
        response = self.client.get(self.search_url, {'q': 'BetaTest'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'], self.user_beta_firstname.username)

    def test_search_by_last_name(self):
        """Test searching by a part of the last name."""
        response = self.client.get(self.search_url, {'q': 'TestThree'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'], self.user_gamma_lastname.username)

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        response = self.client.get(self.search_url, {'q': 'zeta_user_case'}) # Search with lowercase
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'], self.user_zeta_case.username)

        response_upper = self.client.get(self.search_url, {'q': 'ZETA'})
        self.assertEqual(response_upper.status_code, status.HTTP_200_OK)
        self.assertEqual(response_upper.data['count'], 1)
        self.assertEqual(response_upper.data['results'][0]['username'], self.user_zeta_case.username)
        
        response_mixed_fn = self.client.get(self.search_url, {'q': 'bEtAtEsT'}) # search for BetaTest
        self.assertEqual(response_mixed_fn.status_code, status.HTTP_200_OK)
        self.assertEqual(response_mixed_fn.data['count'], 1)
        self.assertEqual(response_mixed_fn.data['results'][0]['username'], self.user_beta_firstname.username)

    def test_search_no_results(self):
        """Test searching for a term that matches no active users."""
        response = self.client.get(self.search_url, {'q': 'nonexistentqueryxyz'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_search_multiple_matches_and_ordering(self):
        """Test search returning multiple users, ordered by username."""
        User.objects.create_user(username='test_user_c', first_name='Common', is_active=True)
        User.objects.create_user(username='test_user_a', first_name='Common', is_active=True)
        User.objects.create_user(username='test_user_b', last_name='Common', is_active=True)
        logger.debug("test_search_multiple_matches_and_ordering():")
        response = self.client.get(self.search_url, {'q': 'Common'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        
        results = response.data['results']
        logger.debug(
            f"--\t response.data['results'][0]['username']: {results[0]['username']}\n"
            f"--\t response.data['results'][1]['username']: {results[1]['username']}\n"
            f"--\t response.data['results'][2]['username']: {results[2]['username']}\n"
        )
        self.assertEqual(results[0]['username'], 'test_user_a') # Assuming order_by('username')
        self.assertEqual(results[1]['username'], 'test_user_b')
        self.assertEqual(results[2]['username'], 'test_user_c')

    def test_search_pagination(self):
        """Test that search results are paginated."""
        # Create enough users to ensure pagination (e.g., 12 users matching 'page_test')
        # Assuming page_size is 10 for UserSearchView's paginator
        for i in range(12):
            User.objects.create_user(username=f'page_test_user{i:02d}', first_name='PageTest', is_active=True)

        response_page1 = self.client.get(self.search_url, {'q': 'PageTest'})
        self.assertEqual(response_page1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_page1.data['count'], 12)
        self.assertEqual(len(response_page1.data['results']), 10) # Default page size from your view
        self.assertIsNotNone(response_page1.data['next'])
        self.assertIsNone(response_page1.data['previous'])

        # Fetch the next page
        next_page_url = response_page1.data['next']
        if next_page_url: # Ensure next_page_url is not None
            response_page2 = self.client.get(next_page_url) # DRF pagination links are full URLs
            self.assertEqual(response_page2.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response_page2.data['results']), 2) # Remaining users
            self.assertIsNone(response_page2.data['next'])
            self.assertIsNotNone(response_page2.data['previous'])

    def test_search_distinct_results(self):
        """
        Test that a user matching the query in multiple fields appears only once.
        The .distinct() in the view handles this, especially important if joins were involved.
        """
        User.objects.create_user(username='tester_distinct', first_name='Tester', last_name='Distinctive', is_active=True)
        logger.debug("test_search_distinct_results():")
        response = self.client.get(self.search_url, {'q': 'tester'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Count how many times 'tester_distinct' appears
        found_count = 0
        for user_data in response.data['results']:
            if user_data['username'] == 'tester_distinct':
                found_count += 1
        logger.debug(
            f"--\t found_count: {found_count}\n"
        )
        self.assertEqual(found_count, 1, "User matching in multiple fields should only appear once.")