from flask import Flask, jsonify
import requests

app = Flask(__name__)

USER_SERVICE_URL = 'http://localhost:5001'
CONTENT_SERVICE_URL = 'http://localhost:5002'

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    try:
        # Get user data from user_service
        user_response = requests.get(f'{USER_SERVICE_URL}/users')
        user_response.raise_for_status() # Raise an exception for bad status codes
        users = user_response.json()
        
        user = next((u for u in users if u['id'] == user_id), None)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get series data from content_service
        series_response = requests.get(f'{CONTENT_SERVICE_URL}/series')
        series_response.raise_for_status()
        all_series = series_response.json()

        # Simple recommendation logic: recommend top-rated series not yet watched by the user
        watched_series_ids = [s['id'] for s in user.get('watched_series', [])]
        
        recommendations = sorted(
            [s for s in all_series if s['id'] not in watched_series_ids],
            key=lambda s: s['rating'],
            reverse=True
        )

        return jsonify(recommendations)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error connecting to other services: {e}'}), 500

if __name__ == '__main__':
    # Running on port 5003 to avoid conflicts
    app.run(debug=True, port=5003)
