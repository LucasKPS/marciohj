from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

USER_SERVICE_URL = 'http://localhost:5001'
CONTENT_SERVICE_URL = 'http://localhost:5002'
RECOMMENDATION_SERVICE_URL = 'http://localhost:5003'

@app.route('/users', methods=['GET', 'POST'])
def users_route():
    if request.method == 'GET':
        try:
            resp = requests.get(f'{USER_SERVICE_URL}/users')
            return jsonify(resp.json()), resp.status_code
        except requests.exceptions.ConnectionError as e:
            return jsonify({'error': 'User service is unavailable'}), 503
    
    elif request.method == 'POST':
        try:
            resp = requests.post(f'{USER_SERVICE_URL}/users', json=request.get_json())
            return jsonify(resp.json()), resp.status_code
        except requests.exceptions.ConnectionError as e:
            return jsonify({'error': 'User service is unavailable'}), 503

@app.route('/series', methods=['GET', 'POST'])
def series_route():
    if request.method == 'GET':
        try:
            resp = requests.get(f'{CONTENT_SERVICE_URL}/series')
            return jsonify(resp.json()), resp.status_code
        except requests.exceptions.ConnectionError as e:
            return jsonify({'error': 'Content service is unavailable'}), 503
    
    elif request.method == 'POST':
        try:
            resp = requests.post(f'{CONTENT_SERVICE_URL}/series', json=request.get_json())
            return jsonify(resp.json()), resp.status_code
        except requests.exceptions.ConnectionError as e:
            return jsonify({'error': 'Content service is unavailable'}), 503

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def recommendations_route(user_id):
    try:
        resp = requests.get(f'{RECOMMENDATION_SERVICE_URL}/recommendations/{user_id}')
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': 'Recommendation service is unavailable'}), 503

if __name__ == '__main__':
    # Running on port 5000
    app.run(debug=True, port=5000)
