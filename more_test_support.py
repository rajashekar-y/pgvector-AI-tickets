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
            "subject": "App keeps crashing!",
            "message": "This app is completely unusable! It crashes every time I open it. Fix this now! I'm extremely frustrated."
        },
        {
            "customer_email": "happy@customer.com",
            "subject": "Great new feature!",
            "message": "Just wanted to say I love the new dark mode! It's fantastic and makes using the app so much better. Keep up the good work!"
        }
    ]
    
    ticket_ids = []
    for ticket_data in sample_tickets:
        print(f"Submitting ticket: '{ticket_data['subject']}'")
        response = requests.post(f"{BASE_URL}/tickets", json=ticket_data)
        if response.status_code == 200:
            result = response.json()
            ticket_id = result.get('ticket_id')
            ticket_ids.append(ticket_id)
            print(f"  Ticket submitted. ID: {ticket_id}")
            print(f"  AI Classification: {result['classification']}")
            print(f"  AI Suggested Response (first 100 chars): {result['suggested_response'][:100]}...")
        else:
            print(f"  Failed to submit ticket. Status: {response.status_code}, Error: {response.json().get('error')}")
    print()
    return ticket_ids

def test_get_ticket(ticket_id):
    print(f"=== Testing Get Single Ticket (ID: {ticket_id}) ===")
    response = requests.get(f"{BASE_URL}/tickets/{ticket_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        ticket = response.json().get('ticket')
        if ticket:
            print(f"  Subject: {ticket['subject']}")
            print(f"  Category: {ticket['category']}")
            print(f"  Status: {ticket['status']}")
            print(f"  Responses: {len(response.json().get('responses', []))}")
    print()

def test_analytics():
    print("=== Testing Analytics ===")
    response = requests.get(f"{BASE_URL}/analytics")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        analytics = response.json()
        print("  Analytics Data:")
        for cat in analytics['categories']:
            print(f"    Category {cat['name']}: {cat['count']}")
        for pri in analytics['priorities']:
            print(f"    Priority {pri['name']}: {pri['count']}")
        for sent in analytics['sentiments']:
            print(f"    Sentiment {sent['name']}: {sent['count']}")
        recent = analytics['recent_week']
        print(f"  Recent Week (Total/Open/Resolved): {recent['total']}/{recent['open']}/{recent['resolved']}")
    print()

def test_list_tickets():
    print("=== Testing List Tickets with Filters ===")
    response = requests.get(f"{BASE_URL}/tickets?status=open&limit=3")
    print(f"Status (Open, limit 3): {response.status_code}")
    if response.status_code == 200:
        tickets = response.json().get('tickets')
        print(f"  Found {len(tickets)} open tickets:")
        for t in tickets:
            print(f"    ID: {t['id']}, Subject: {t['subject']}, Status: {t['status']}")
    print()

def demonstrate_ai_capabilities():
    print("=== Demonstrating AI Classification and Response Generation ===")
    edge_cases = [
        {
            "customer_email": "tech.issue@example.com",
            "subject": "My internet is down, need help ASAP!",
            "message": "My internet connection completely stopped working an hour ago. I've tried restarting the modem multiple times. I work from home and this is critical."
        },
        {
            "customer_email": "billing.question@example.com",
            "subject": "Query about my last bill",
            "message": "I received my bill for June, and the amount seems higher than usual. Could you please clarify the charges for this month? My account reference is ABC-789."
        },
        {
            "customer_email": "happy.customer@example.com",
            "subject": "Loving the new update!",
            "message": "Just wanted to say how much I appreciate the recent update. The new user interface is so much cleaner and more intuitive. Great job!"
        },
        {
            "customer_email": "confused@example.com",
            "subject": "Question about new analytics feature",
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
            print(f"  Suggested Response Preview: {result['suggested_response'][:150]}...")
        else:
            print(f"  Failed to submit. Status: {response.status_code}, Error: {response.json().get('error')}")
        print()

if __name__ == "__main__":
    print("🤖 AI Support System Test Suite - Focusing on AI Demonstration")
    print("=" * 50)
    
    try:
        test_health() # Keep this to ensure connection

        # Comment out the lines below if you don't want to submit a fresh batch
        # of the original sample tickets every time.
        # ticket_ids = test_submit_tickets()
        # if ticket_ids:
        #     test_get_ticket(ticket_ids[0])
        # test_list_tickets() # Only needed if you have specific filters to test here

        # >>> THIS IS THE KEY PART TO FOCUS ON FOR DEMONSTRATING AI CAPABILITIES <<<
        demonstrate_ai_capabilities()

        # After submitting new tickets via demonstrate_ai_capabilities, check analytics
        print("\n=== Re-testing Analytics after AI Demonstration ===")
        test_analytics() # Call analytics again to see the impact of new tickets

        print("🎉 AI demonstration focused tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the Flask server is running on localhost:5001")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
