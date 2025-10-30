
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# URLs dos microserviços
USER_SERVICE_URL = 'http://localhost:5001'
CONTENT_SERVICE_URL = 'http://localhost:5002'
RECOMMENDATION_SERVICE_URL = 'http://localhost:5003'

# Helper para encaminhar requisições e tratar erros de conexão
def forward_request(method, url, json=None):
    try:
        if method == 'GET':
            resp = requests.get(url)
        elif method == 'POST':
            resp = requests.post(url, json=json)
        # Levanta uma exceção para respostas com código de erro (4xx ou 5xx)
        resp.raise_for_status()
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.ConnectionError:
        # O serviço de destino está fora do ar
        return jsonify({'error': 'Service is unavailable'}), 503
    except requests.exceptions.HTTPError as e:
        # O serviço de destino retornou um erro (ex: 404 Not Found, 400 Bad Request)
        # Retornamos o mesmo erro para o cliente final
        return jsonify(e.response.json()), e.response.status_code


@app.route('/users', methods=['GET', 'POST'])
def users_route():
    if request.method == 'GET':
        return forward_request('GET', f'{USER_SERVICE_URL}/users')
    elif request.method == 'POST':
        return forward_request('POST', f'{USER_SERVICE_URL}/users', json=request.get_json())


@app.route('/series', methods=['GET', 'POST'])
def series_route():
    if request.method == 'GET':
        return forward_request('GET', f'{CONTENT_SERVICE_URL}/series')
    elif request.method == 'POST':
        return forward_request('POST', f'{CONTENT_SERVICE_URL}/series', json=request.get_json())


@app.route('/recommendations/<int:user_id>', methods=['GET'])
def recommendations_route(user_id):
    return forward_request('GET', f'{RECOMMENDATION_SERVICE_URL}/recommendations/{user_id}')


# NOVA ROTA: Para avaliar uma série
@app.route('/users/<int:user_id>/rate', methods=['POST'])
def rate_series_route(user_id):
    return forward_request('POST', f'{USER_SERVICE_URL}/users/{user_id}/rate', json=request.get_json())


if __name__ == '__main__':
    # Rodando na porta principal 5000
    app.run(debug=True, port=5000)
