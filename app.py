import os
import psycopg2
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS # Add this import
from dotenv import load_dotenv
import re
from datetime import datetime, timedelta
import json

# Load environment variables
load_dotenv('ai_env.env')

# Initialize Flask app
app = Flask(__name__)
CORS(app) # NEW LINE: This enables CORS for all routes

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'support_ai_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password'),
        port=os.getenv('DB_PORT', '5432')
    )

# Generate embeddings
def generate_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# Classify ticket using AI
def classify_ticket(subject, message):
    prompt = f"""
    Analyze this support ticket and classify it. Return a JSON response with:
    - category: one of [Technical Issue, Billing, Account Access, Feature Request, General Inquiry, Bug Report, Refund Request]
    - priority: one of [Low, Medium, High, Critical]
    - sentiment: one of [Positive, Neutral, Negative, Frustrated]
    - urgency_keywords: list of words that indicate urgency
    
    Subject: {subject}
    Message: {message}
    
    Consider:
    - Keywords that indicate category
    - Tone and language that suggests priority
    - Emotional indicators for sentiment
    - Urgency indicators like "urgent", "immediately", "broken", "not working"
    
    Return only valid JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"Error classifying ticket: {e}")
        return {
            "category": "General Inquiry",
            "priority": "Medium",
            "sentiment": "Neutral",
            "urgency_keywords": []
        }

# Generate AI response
def generate_response(ticket_data, similar_tickets=None):
    context = ""
    if similar_tickets:
        context = "\n\nSimilar resolved tickets:\n"
        for ticket in similar_tickets[:2]:
            context += f"- {ticket['subject']}: {ticket['resolution']}\n"
    
    prompt = f"""
    Generate a professional, helpful response to this support ticket:
    
    Subject: {ticket_data['subject']}
    Message: {ticket_data['message']}
    Category: {ticket_data['category']}
    Priority: {ticket_data['priority']}
    Sentiment: {ticket_data['sentiment']}
    {context}
    
    Guidelines:
    - Be professional and empathetic
    - Acknowledge the issue clearly
    - Provide specific steps or solutions when possible
    - If it's a technical issue, ask for relevant details
    - Match the tone to the customer's sentiment
    - Keep response concise but complete
    - Include next steps or timeline when appropriate
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Thank you for contacting our support team. We have received your request and will respond shortly."

# Find similar tickets
def find_similar_tickets(embedding, category, limit=3):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, subject, message, category, 
                   embedding <=> %s as similarity
            FROM support_tickets
            WHERE category = %s AND status = 'resolved'
            ORDER BY embedding <=> %s
            LIMIT %s
        """, (embedding, category, embedding, limit))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return [
            {
                'id': row[0],
                'subject': row[1],
                'message': row[2],
                'category': row[3],
                'similarity': float(row[4]),
                'resolution': 'Sample resolution...'  # In real system, you'd store actual resolutions
            }
            for row in results
        ]
    except Exception as e:
        print(f"Error finding similar tickets: {e}")
        return []

# Create new support ticket
def create_ticket(customer_email, subject, message):
    try:
        # Generate embedding
        full_text = f"{subject} {message}"
        embedding = generate_embedding(full_text)
        
        # Classify ticket
        classification = classify_ticket(subject, message)
        
        # Insert ticket
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO support_tickets (customer_email, subject, message, category, 
                                       priority, sentiment, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (customer_email, subject, message, classification['category'],
              classification['priority'], classification['sentiment'], embedding))
        
        ticket_id = cur.fetchone()[0]
        
        # Find similar tickets
        similar_tickets = find_similar_tickets(embedding, classification['category'])
        
        # Generate AI response
        ticket_data = {
            'subject': subject,
            'message': message,
            'category': classification['category'],
            'priority': classification['priority'],
            'sentiment': classification['sentiment']
        }
        
        ai_response = generate_response(ticket_data, similar_tickets)
        
        # Store AI response
        cur.execute("""
            INSERT INTO ticket_responses (ticket_id, response_text, response_type, confidence_score)
            VALUES (%s, %s, %s, %s)
        """, (ticket_id, ai_response, 'ai_suggested', 0.85))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'ticket_id': ticket_id,
            'classification': classification,
            'ai_response': ai_response,
            'similar_tickets': similar_tickets
        }
        
    except Exception as e:
        print(f"Error creating ticket: {e}")
        return None

# Flask routes
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'AI Support System'})

@app.route('/tickets', methods=['POST'])
def submit_ticket():
    data = request.json
    customer_email = data.get('customer_email')
    subject = data.get('subject')
    message = data.get('message')
    
    if not all([customer_email, subject, message]):
        return jsonify({'error': 'Customer email, subject, and message are required'}), 400
    
    result = create_ticket(customer_email, subject, message)
    
    if result:
        return jsonify({
            'success': True,
            'ticket_id': result['ticket_id'],
            'classification': result['classification'],
            'suggested_response': result['ai_response'],
            'similar_tickets_found': len(result['similar_tickets'])
        })
    else:
        return jsonify({'error': 'Failed to create ticket'}), 500

@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get ticket details
        cur.execute("""
            SELECT id, customer_email, subject, message, category, priority, 
                   sentiment, status, created_at
            FROM support_tickets WHERE id = %s
        """, (ticket_id,))
        
        ticket = cur.fetchone()
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Get responses
        cur.execute("""
            SELECT response_text, response_type, confidence_score, created_at
            FROM ticket_responses WHERE ticket_id = %s
            ORDER BY created_at DESC
        """, (ticket_id,))
        
        responses = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'ticket': {
                'id': ticket[0],
                'customer_email': ticket[1],
                'subject': ticket[2],
                'message': ticket[3],
                'category': ticket[4],
                'priority': ticket[5],
                'sentiment': ticket[6],
                'status': ticket[7],
                'created_at': ticket[8].isoformat()
            },
            'responses': [
                {
                    'text': resp[0],
                    'type': resp[1],
                    'confidence': float(resp[2]) if resp[2] else None,
                    'created_at': resp[3].isoformat()
                }
                for resp in responses
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analytics', methods=['GET'])
def get_analytics():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Category distribution
        cur.execute("""
            SELECT category, COUNT(*) as count
            FROM support_tickets
            GROUP BY category
            ORDER BY count DESC
        """)
        category_stats = cur.fetchall()
        
        # Priority distribution
        cur.execute("""
            SELECT priority, COUNT(*) as count
            FROM support_tickets
            GROUP BY priority
            ORDER BY count DESC
        """)
        priority_stats = cur.fetchall()
        
        # Sentiment analysis
        cur.execute("""
            SELECT sentiment, COUNT(*) as count
            FROM support_tickets
            GROUP BY sentiment
            ORDER BY count DESC
        """)
        sentiment_stats = cur.fetchall()
        
        # Recent tickets
        cur.execute("""
            SELECT COUNT(*) as total_tickets,
                   COUNT(CASE WHEN status = 'open' THEN 1 END) as open_tickets,
                   COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_tickets
            FROM support_tickets
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)
        recent_stats = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'categories': [{'name': cat[0], 'count': cat[1]} for cat in category_stats],
            'priorities': [{'name': pri[0], 'count': pri[1]} for pri in priority_stats],
            'sentiments': [{'name': sent[0], 'count': sent[1]} for sent in sentiment_stats],
            'recent_week': {
                'total': recent_stats[0],
                'open': recent_stats[1],
                'resolved': recent_stats[2]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tickets', methods=['GET'])
def list_tickets():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get query parameters
        category = request.args.get('category')
        priority = request.args.get('priority')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 10))
        
        # Build query
        query = """
            SELECT id, customer_email, subject, category, priority, 
                   sentiment, status, created_at
            FROM support_tickets
            WHERE 1=1
        """
        params = []
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if priority:
            query += " AND priority = %s"
            params.append(priority)
            
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cur.execute(query, params)
        tickets = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'tickets': [
                {
                    'id': ticket[0],
                    'customer_email': ticket[1],
                    'subject': ticket[2],
                    'category': ticket[3],
                    'priority': ticket[4],
                    'sentiment': ticket[5],
                    'status': ticket[6],
                    'created_at': ticket[7].isoformat()
                }
                for ticket in tickets
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Test database connection
    try:
        conn = get_db_connection()
        conn.close()
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")
        exit(1)
    
    print("Starting AI Support Ticket System...")
    app.run(debug=True, host='0.0.0.0', port=5001)
