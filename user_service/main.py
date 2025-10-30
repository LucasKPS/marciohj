
from flask import Flask, jsonify, request

app = Flask(__name__)

# Banco de dados em memória para usuários
users = []
user_id_counter = 1

class User:
    def __init__(self, name, email):
        global user_id_counter
        self.id = user_id_counter
        self.name = name
        self.email = email
        self.rated_series = []  # Alterado de watched_series para rated_series
        user_id_counter += 1

# Endpoint para obter um usuário específico e suas avaliações
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((user for user in users if user.id == user_id), None)
    if user:
        return jsonify(user.__dict__)
    return jsonify({'error': 'User not found'}), 404

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

# NOVO ENDPOINT: Para um usuário avaliar uma série
@app.route('/users/<int:user_id>/rate', methods=['POST'])
def rate_series(user_id):
    user = next((user for user in users if user.id == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data or 'series_id' not in data or 'rating' not in data:
        return jsonify({'error': 'Missing series_id or rating'}), 400

    series_id = data['series_id']
    rating = data['rating']

    # Remove a avaliação antiga, se existir, para substituí-la pela nova
    user.rated_series = [r for r in user.rated_series if r['series_id'] != series_id]
    
    # Adiciona a nova avaliação
    user.rated_series.append({'series_id': series_id, 'rating': rating})
    
    return jsonify(user.__dict__), 200

if __name__ == '__main__':
    # Rodando na porta 5001 para evitar conflitos
    app.run(debug=True, port=5001)
