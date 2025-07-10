import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_health():
    print("=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_submit_tickets():
    print("=== Testing Ticket Submission ===")
    
    # Sample support tickets with different categories and priorities
    sample_tickets = [
        {
            "customer_email": "john@example.com",
            "subject": "Cannot login to my account",
            "message": "I've been trying to log in for the past hour but keep getting 'invalid credentials' error. I'm sure my password is correct. This is urgent as I need to access my account for work."
        },
        {
            "customer_email": "sarah@company.com",
            "subject": "Billing issue - charged twice",
            "message": "Hi, I noticed I was charged twice for my subscription this month. Can you please check and refund the duplicate charge? My account number is 12345."
        },
        {
            "customer_email": "mike@startup.io",
            "subject": "Feature request - API rate limiting",
            "message": "Would it be possible to add configurable rate limiting to the API? This would help us manage our usage better and prevent accidental overuse."
        },
        {
            "customer_email": "angry@customer.com",
            "subject": "URGENT: System completely broken!",
            "message": "Your system is completely broken! Nothing works! I've lost important data and this is completely unacceptable. I demand immediate action or I'm canceling my subscription!"
        },
        {
            "customer_email": "tech@company.com",
            "subject": "Bug report - Data export failing",
            "message": "When I try to export data from the dashboard, the download fails at around 50% completion. This happens consistently with large datasets. Error code: EXP_001"
        }
    ]
    
    ticket_ids = []
    
    for i, ticket in enumerate(sample_tickets, 1):
        print(f"Submitting ticket {i}: {ticket['subject']}")
        response = requests.post(f"{BASE_URL}/tickets", json=ticket)
        
        if response.status_code == 200:
            result = response.json()
            ticket_ids.append(result['ticket_id'])
            print(f"  ✓ Ticket ID: {result['ticket_id']}")
            print(f"  ✓ Category: {result['classification']['category']}")
            print(f"  ✓ Priority: {result['classification']['priority']}")
            print(f"  ✓ Sentiment: {result['classification']['sentiment']}")
            print(f"  ✓ AI Response: {result['suggested_response'][:100]}...")
        else:
            print(f"  ✗ Error: {response.status_code}")
        print()
    
    return ticket_ids

def test_get_ticket(ticket_id):
    print(f"=== Testing Get Ticket {ticket_id} ===")
    response = requests.get(f"{BASE_URL}/tickets/{ticket_id}")
    
    if response.status_code == 200:
        result = response.json()
        ticket = result['ticket']
        print(f"Subject: {ticket['subject']}")
        print(f"Category: {ticket['category']}")
        print(f"Priority: {ticket['priority']}")
        print(f"Sentiment: {ticket['sentiment']}")
        print(f"Status: {ticket['status']}")
        print(f"Responses: {len(result['responses'])}")
        
        if result['responses']:
            print(f"Latest Response: {result['responses'][0]['text'][:150]}...")
    else:
        print(f"Error: {response.status_code}")
    print()

def test_analytics():
    print("=== Testing Analytics ===")
    response = requests.get(f"{BASE_URL}/analytics")
    
    if response.status_code == 200:
        analytics = response.json()
        
        print("Category Distribution:")
        for cat in analytics['categories']:
            print(f"  {cat['name']}: {cat['count']} tickets")
        
        print("\nPriority Distribution:")
        for pri in analytics['priorities']:
            print(f"  {pri['name']}: {pri['count']} tickets")
        
        print("\nSentiment Analysis:")
        for sent in analytics['sentiments']:
            print(f"  {sent['name']}: {sent['count']} tickets")
        
        print(f"\nRecent Week Stats:")
        recent = analytics['recent_week']
        print(f"  Total: {recent['total']}")
        print(f"  Open: {recent['open']}")
        print(f"  Resolved: {recent['resolved']}")
    else:
        print(f"Error: {response.status_code}")
    print()

def test_list_tickets():
    print("=== Testing List Tickets ===")
    
    # Test different filters
    filters = [
        {},  # All tickets
        {"category": "Technical Issue"},
        {"priority": "High"},
        {"status": "open"},
        {"limit": "3"}
    ]
    
    for filter_params in filters:
        print(f"Filter: {filter_params}")
        response = requests.get(f"{BASE_URL}/tickets", params=filter_params)
        
        if response.status_code == 200:
            tickets = response.json()['tickets']
            print(f"  Found {len(tickets)} tickets")
            for ticket in tickets[:2]:  # Show first 2
                print(f"    - {ticket['subject']} ({ticket['category']}, {ticket['priority']})")
        else:
            print(f"  Error: {response.status_code}")
        print()

def demonstrate_ai_capabilities():
    print("=== AI Capabilities Demonstration ===")
    
    # Test edge cases and different scenarios
    edge_cases = [
        {
            "customer_email": "test@edge.com",
            "subject": "Password reset not working",
            "message": "I clicked the password reset link but it says the link is expired. I tried multiple times."
        },
        {
            "customer_email": "happy@customer.com",
            "subject": "Thank you for great service",
            "message": "Just wanted to say thank you for the excellent customer service. Your team resolved my issue quickly and professionally."
        },
        {
            "customer_email": "confused@user.com",
            "subject": "How do I use the new feature?",
            "message": "I saw the announcement about the new analytics feature but I can't figure out how to access it. Can you help?"
        }
    ]
    
    for case in edge_cases:
        print(f"Testing: {case['subject']}")
        response = requests.post(f"{BASE_URL}/tickets", json=case)
        
        if response.status_code == 200:
            result = response.json()
            print(f"  AI Classification:")
            print(f"    Category: {result['classification']['category']}")
            print(f"    Priority: {result['classification']['priority']}")
            print(f"    Sentiment: {result['classification']['sentiment']}")
            print(f"  AI Response Quality: {len(result['suggested_response'])} chars")
        print()

if __name__ == "__main__":
    print("🤖 AI Support System Test Suite")
    print("=" * 50)
    
    try:
        test_health()
        
        # Submit sample tickets
        ticket_ids = test_submit_tickets()
        
        # Test individual ticket retrieval
        if ticket_ids:
            test_get_ticket(ticket_ids[0])
        
        # Test analytics
        test_analytics()
        
        # Test listing with filters
        test_list_tickets()
        
        # Demonstrate AI capabilities
        demonstrate_ai_capabilities()
        
        print("🎉 All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the Flask server is running on localhost:5001")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
