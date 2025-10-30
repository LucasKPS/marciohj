
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# URLs dos outros serviços
USER_SERVICE_URL = 'http://localhost:5001'
CONTENT_SERVICE_URL = 'http://localhost:5002'

# Nota mínima para uma série ser considerada 'gostada' pelo usuário
HIGH_RATING_THRESHOLD = 4

@app.route('/recommendations/genre/<string:genre>', methods=['GET'])
def get_recommendation_by_genre(genre):
    """Retorna a série mais bem avaliada para um determinado gênero."""
    try:
        # 1. Obter a lista completa de séries do serviço de conteúdo.
        all_series_response = requests.get(f'{CONTENT_SERVICE_URL}/series')
        all_series_response.raise_for_status()
        all_series = all_series_response.json()

        # 2. Filtrar as séries pelo gênero fornecido (case-insensitive).
        candidates = [
            s for s in all_series
            if s['genre'].lower() == genre.lower()
        ]

        # 3. Verificar se foram encontradas séries para o gênero.
        if not candidates:
            return jsonify({"message": f"Nenhuma série encontrada para o gênero '{genre}'."}), 404

        # 4. Ordenar os candidatos pela maior avaliação e retornar a lista.
        sorted_candidates = sorted(candidates, key=lambda s: s['rating'], reverse=True)
        return jsonify(sorted_candidates)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Erro de comunicação com o serviço de conteúdo: {e}'}), 500

# A rota antiga baseada no ID do usuário é mantida para não quebrar outras funcionalidades.
@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations_by_user(user_id):
    try:
        user_response = requests.get(f'{USER_SERVICE_URL}/users/{user_id}')
        user_response.raise_for_status()
        user_data = user_response.json()

        rated_series = user_data.get('rated_series', [])
        if not rated_series:
            return jsonify({"message": "O usuário ainda não avaliou nenhuma série. Recomende algumas para ele avaliar!"}), 200

        high_rated_series_ids = [r['series_id'] for r in rated_series if r['rating'] >= HIGH_RATING_THRESHOLD]
        if not high_rated_series_ids:
            return jsonify({"message": "O usuário não deu nota alta para nenhuma série ainda. As recomendações melhorarão."}), 200

        all_series_response = requests.get(f'{CONTENT_SERVICE_URL}/series')
        all_series_response.raise_for_status()
        all_series = all_series_response.json()

        series_map = {s['id']: s for s in all_series}
        favorite_genres = {series_map[sid]['genre'] for sid in high_rated_series_ids if sid in series_map}

        if not favorite_genres:
            return jsonify({"message": "Não foi possível identificar os gêneros favoritos."}), 200

        user_rated_series_ids = {r['series_id'] for r in rated_series}
        recommendations = sorted(
            [s for s in all_series if s['genre'] in favorite_genres and s['id'] not in user_rated_series_ids],
            key=lambda s: s['rating'],
            reverse=True
        )
        return jsonify(recommendations)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        return jsonify({'error': f'Erro de comunicação com serviços: {e}'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Erro de conexão: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)
