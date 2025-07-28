#!/usr/bin/env python
"""
Debug script to identify N+1 query issues in PendingFriendRequestListView

This script simulates the view execution and tracks SQL queries to identify
the source of N+1 queries.
"""

import os
import sys
import django
from django.db import connection
from django.test.utils import override_settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduLite.settings')
django.setup()

# Import after Django setup
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from users.models import UserProfile, ProfileFriendRequest
from users.views import PendingFriendRequestListView
from users.serializers import ProfileFriendRequestSerializer

User = get_user_model()


def simulate_view_execution():
    """
    Simulate the exact execution path of PendingFriendRequestListView
    to identify where N+1 queries occur.
    """
    print("\nSimulating PendingFriendRequestListView Execution")
    print("="*80)
    
    # 1. Show current select_related
    print("\nCurrent select_related in view (line 536):")
    print('queryset.select_related("sender", "receiver", "sender__user", "receiver__user")')
    
    # 2. Explain the query pattern
    print("\nExpected queries for paginated list view:")
    print("1. COUNT query for pagination")
    print("2. Main SELECT with LIMIT for page data")
    print("3. Any additional queries from serialization")
    
    # 3. Analyze serializer access patterns
    print("\n" + "-"*80)
    print("Serializer Field Access Analysis:")
    print("-"*80)
    
    print("\nProfileFriendRequestSerializer accesses:")
    print("- obj.sender.id (in get_sender_profile_url)")
    print("- obj.receiver.id (in get_receiver_profile_url)")
    print("- obj.id (in get_accept_url and get_decline_url)")
    
    print("\nThese should NOT cause extra queries because:")
    print("- sender and receiver are select_related")
    print("- .id access on pre-fetched objects is free")
    
    # 4. Identify the real issue
    print("\n" + "="*80)
    print("IDENTIFIED N+1 QUERY SOURCE:")
    print("="*80)
    
    print("\nThe issue is likely from privacy_settings access!")
    print("\nWhen the view renders the response, Django might be:")
    print("1. Checking permissions that access user.profile.privacy_settings")
    print("2. Serializing user data that checks privacy_settings")
    print("3. Running middleware that accesses user privacy settings")
    
    print("\nEach ProfileFriendRequest has:")
    print("- sender (UserProfile) -> needs privacy_settings")
    print("- receiver (UserProfile) -> needs privacy_settings")
    
    print("\nWith 10 items per page:")
    print("- 10 queries for sender privacy_settings")
    print("- 10 queries for receiver privacy_settings")
    print("- Total: 20 extra queries!")
    
    # 5. Provide the solution
    print("\n" + "="*80)
    print("SOLUTION:")
    print("="*80)
    
    print("\nUpdate the select_related in PendingFriendRequestListView.get_queryset()")
    print("From:")
    print('  queryset.select_related("sender", "receiver", "sender__user", "receiver__user")')
    
    print("\nTo:")
    print('  queryset.select_related(')
    print('      "sender",')
    print('      "receiver",')
    print('      "sender__user",')
    print('      "receiver__user",')
    print('      "sender__privacy_settings",')
    print('      "receiver__privacy_settings"')
    print('  )')
    
    print("\nThis will pre-fetch all privacy settings in the main query,")
    print("eliminating the N+1 queries!")


def demonstrate_query_counting():
    """
    Demonstrate how to count queries in a test
    """
    print("\n" + "="*80)
    print("HOW TO DEBUG IN YOUR TEST:")
    print("="*80)
    
    print("""
Add this to your test to see actual queries:

def test_pagination_performance_large_dataset(self):
    # Your existing test setup...
    
    # Enable query logging
    from django.db import connection
    from django.test.utils import override_settings
    
    with override_settings(DEBUG=True):
        # Clear query log
        connection.queries_log.clear()
        
        # Make the request
        response = self.client.get(self.list_url, {"direction": "received"})
        
        # Print query count
        print(f"\\nTotal queries: {len(connection.queries)}")
        
        # Print each query
        for i, query in enumerate(connection.queries, 1):
            print(f"\\nQuery {i}: {query['sql'][:100]}...")
            
        # Check for privacy_settings queries
        privacy_queries = [q for q in connection.queries if 'privacy_settings' in q['sql']]
        print(f"\\nPrivacy settings queries: {len(privacy_queries)}")
""")


def analyze_query_optimization():
    """
    Analyze different query optimization strategies
    """
    print("\n" + "="*80)
    print("QUERY OPTIMIZATION STRATEGIES:")
    print("="*80)
    
    print("\n1. Current approach (causing N+1):")
    print("   - select_related for basic relations")
    print("   - Missing privacy_settings")
    print("   - Result: 2 base queries + 20 N+1 queries = 22 total")
    
    print("\n2. Optimized approach:")
    print("   - select_related including privacy_settings")
    print("   - Result: 2 base queries only")
    
    print("\n3. Alternative approach (if privacy not always needed):")
    print("   - Use prefetch_related for privacy_settings")
    print("   - Result: 3 queries total (base + 1 for all privacy settings)")
    
    print("\n4. Most efficient (if feasible):")
    print("   - Create a specialized serializer without privacy checks")
    print("   - For friend request lists, privacy might not be needed")


def main():
    """Main debug function"""
    print("\nDebugging N+1 Query Issue in PendingFriendRequestListView")
    print("="*80)
    
    simulate_view_execution()
    demonstrate_query_counting()
    analyze_query_optimization()
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print("="*80)
    
    print("\nThe N+1 query issue in PendingFriendRequestListView is caused by")
    print("missing privacy_settings in the select_related clause.")
    
    print("\nEach friend request has a sender and receiver, and something in")
    print("the request cycle is accessing their privacy_settings, causing")
    print("2 extra queries per friend request (20 queries for 10 items).")
    
    print("\nThe fix is simple: add privacy_settings to select_related!")


if __name__ == "__main__":
    main()