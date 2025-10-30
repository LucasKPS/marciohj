from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory database for users
users = []
user_id_counter = 1

class User:
    def __init__(self, name, email):
        global user_id_counter
        self.id = user_id_counter
        self.name = name
        self.email = email
        self.watched_series = []
        user_id_counter += 1

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify([user.__dict__ for user in users])

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not 'name' in data or not 'email' in data:
        return jsonify({'error': 'Missing name or email'}), 400
    
    new_user = User(name=data['name'], email=data['email'])
    users.append(new_user)
    return jsonify(new_user.__dict__), 201

if __name__ == '__main__':
    # Running on port 5001 to avoid conflicts with other services
    app.run(debug=True, port=5001)
