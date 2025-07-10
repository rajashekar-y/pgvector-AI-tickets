# Inside start_flask.py

from flask import Flask, jsonify # Make sure jsonify is imported if you're returning JSON

app = Flask(__name__)

# ... other routes you might have ...

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the API.
    """
    return jsonify({"status": "healthy", "message": "API is up and running!"}), 200

# ... your if __name__ == '__main__': block ...
if __name__ == '__main__':
    # Make sure your app.run() matches the port expected by your test_support.py
    app.run(debug=True, port=5001, host='0.0.0.0')
