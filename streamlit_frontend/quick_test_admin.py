#!/usr/bin/env python3
"""
Quick Interactive Admin Test
Simple script to test specific admin functions
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from lib.api import make_api_request
from lib.api_helpers import safe_get_users, safe_get_organizers, is_api_healthy

def print_separator(title=""):
    print("\n" + "="*60)
    if title:
        print(f" {title}")
        print("="*60)

def test_menu():
    """Display test menu"""
    print_separator("ADMIN ABILITIES QUICK TEST")
    print("1. Test API Health")
    print("2. Test User Management")
    print("3. Test Organizer Management") 
    print("4. Test Job Fair Management")
    print("5. Test Job Requirements Management")
    print("6. Test Booth Management")
    print("7. Test Admin Statistics")
    print("8. Run All Tests")
    print("0. Exit")
    print("-"*60)

def test_api_health():
    """Test API health"""
    print("Testing API Health...")
    try:
        healthy = is_api_healthy()
        print(f"✅ API Health: {'HEALTHY' if healthy else 'UNHEALTHY'}")
        return healthy
    except Exception as e:
        print(f"❌ API Health Error: {e}")
        return False

def test_users():
    """Test user management"""
    print("Testing User Management...")
    try:
        users, success = safe_get_users()
        print(f"✅ Retrieved {len(users)} users" if success else "❌ Failed to get users")
        
        if success and users:
            user = users[0]
            print(f"Sample user: {user.get('name', 'N/A')} ({user.get('email', 'N/A')})")
        
        return success
    except Exception as e:
        print(f"❌ User Management Error: {e}")
        return False

def test_organizers():
    """Test organizer management"""
    print("Testing Organizer Management...")
    try:
        pending, success1 = safe_get_organizers("pending")
        approved, success2 = safe_get_organizers("approved")
        
        print(f"✅ Pending organizers: {len(pending)}" if success1 else "❌ Failed to get pending organizers")
        print(f"✅ Approved organizers: {len(approved)}" if success2 else "❌ Failed to get approved organizers")
        
        return success1 and success2
    except Exception as e:
        print(f"❌ Organizer Management Error: {e}")
        return False

def test_job_fairs():
    """Test job fair management"""
    print("Testing Job Fair Management...")
    try:
        result, success, _ = make_api_request("admin/job-fairs", "GET", params={'per_page': 'all'})
        job_fairs = result.get('data', []) if success else []
        print(f"✅ Retrieved {len(job_fairs)} job fairs" if success else f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        if success and job_fairs:
            jf = job_fairs[0]
            print(f"Sample job fair: {jf.get('title', 'N/A')} - Status: {jf.get('status', 'N/A')}")
        
        return success
    except Exception as e:
        print(f"❌ Job Fair Management Error: {e}")
        return False

def test_job_requirements():
    """Test job requirements management"""
    print("Testing Job Requirements Management...")
    try:
        result, success, _ = make_api_request("admin/job-requirements", "GET", params={'per_page': 'all'})
        job_reqs = result.get('data', []) if success else []
        print(f"✅ Retrieved {len(job_reqs)} job requirements" if success else f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        if success and job_reqs:
            req = job_reqs[0]
            print(f"Sample job requirement: {req.get('title', 'N/A')} - Type: {req.get('employment_type', 'N/A')}")
        
        return success
    except Exception as e:
        print(f"❌ Job Requirements Management Error: {e}")
        return False

def test_booths():
    """Test booth management"""
    print("Testing Booth Management...")
    try:
        # Get a job fair first
        result, success, _ = make_api_request("admin/job-fairs", "GET", params={'per_page': 'all'})
        job_fairs = result.get('data', []) if success else []
        
        if not job_fairs:
            print("❌ No job fairs available for booth testing")
            return False
        
        jf_id = job_fairs[0]['id']
        result, success, _ = make_api_request(f"admin/job-fairs/{jf_id}/booths", "GET")
        booths = result.get('data', []) if success else []
        
        print(f"✅ Retrieved {len(booths)} booths for job fair {jf_id}" if success else f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        if success and booths:
            booth = booths[0]
            print(f"Sample booth: {booth.get('company_name', 'N/A')} - Booth #{booth.get('booth_number_on_map', 'N/A')}")
        
        return success
    except Exception as e:
        print(f"❌ Booth Management Error: {e}")
        return False

def test_statistics():
    """Test admin statistics"""
    print("Testing Admin Statistics...")
    try:
        # User statistics
        result, success1, _ = make_api_request("admin/users/statistics", "GET")
        user_stats = result.get('data', {}) if success1 else {}
        print(f"✅ User statistics: {user_stats}" if success1 else f"❌ Failed user stats: {result.get('error', 'Unknown error')}")
        
        # Job fair statistics
        result, success2, _ = make_api_request("admin/job-fairs/statistics", "GET")
        jf_stats = result.get('data', {}) if success2 else {}
        print(f"✅ Job fair statistics: {jf_stats}" if success2 else f"❌ Failed job fair stats: {result.get('error', 'Unknown error')}")
        
        return success1 and success2
    except Exception as e:
        print(f"❌ Statistics Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print_separator("RUNNING ALL TESTS")
    tests = [
        ("API Health", test_api_health),
        ("User Management", test_users),
        ("Organizer Management", test_organizers),
        ("Job Fair Management", test_job_fairs),
        ("Job Requirements Management", test_job_requirements),
        ("Booth Management", test_booths),
        ("Admin Statistics", test_statistics)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        success = test_func()
        results.append((test_name, success))
    
    print_separator("TEST RESULTS SUMMARY")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

def main():
    """Main interactive loop"""
    while True:
        test_menu()
        try:
            choice = input("Select test (0-8): ").strip()
            
            if choice == "0":
                print("Goodbye! 👋")
                break
            elif choice == "1":
                test_api_health()
            elif choice == "2":
                test_users()
            elif choice == "3":
                test_organizers()
            elif choice == "4":
                test_job_fairs()
            elif choice == "5":
                test_job_requirements()
            elif choice == "6":
                test_booths()
            elif choice == "7":
                test_statistics()
            elif choice == "8":
                run_all_tests()
            else:
                print("❌ Invalid choice. Please select 0-8.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
