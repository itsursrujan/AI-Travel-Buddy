#!/usr/bin/env python3
"""
Quick test script to verify attractions fetching works correctly
"""
import sys
sys.path.insert(0, r'c:\Users\Srujan Aravalli\Desktop\AI Travel Buddy\backend')

from services.ai_engine import AIEngine

# Test destinations
test_destinations = ["Paris", "London", "Hyderabad", "Tokyo"]

for destination in test_destinations:
    print(f"\n{'='*60}")
    print(f"Testing: {destination}")
    print(f"{'='*60}")
    
    attractions = AIEngine.fetch_attractions_from_internet(destination)
    
    print(f"\nFetched {len(attractions)} attractions:")
    for i, attr in enumerate(attractions, 1):
        print(f"  {i}. {attr['name']}")
        print(f"     Description: {attr['description']}")
