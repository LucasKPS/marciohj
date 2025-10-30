
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# URLs dos outros serviços
USER_SERVICE_URL = 'http://localhost:5001'
CONTENT_SERVICE_URL = 'http://localhost:5002'

# Nota mínima para uma série ser considerada 'gostada' pelo usuário
HIGH_RATING_THRESHOLD = 4

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    try:
        # 1. Obter os dados do usuário, incluindo as séries que ele já avaliou.
        user_response = requests.get(f'{USER_SERVICE_URL}/users/{user_id}')
        user_response.raise_for_status() # Lança exceção se o usuário não for encontrado
        user_data = user_response.json()

        # 2. Identificar os gêneros favoritos do usuário com base nas séries bem avaliadas.
        rated_series = user_data.get('rated_series', [])
        if not rated_series:
            # Linha corrigida de "0 usuário" para "O usuário"
            return jsonify({"message": "O usuário ainda não avaliou nenhuma série. Recomende algumas para ele avaliar!"}), 200

        high_rated_series_ids = [
            r['series_id'] for r in rated_series if r['rating'] >= HIGH_RATING_THRESHOLD
        ]

        if not high_rated_series_ids:
            return jsonify({"message": "O usuário não deu nota alta para nenhuma série ainda. As recomendações melhorarão quando ele o fizer."}), 200

        # 3. Obter a lista completa de séries.
        all_series_response = requests.get(f'{CONTENT_SERVICE_URL}/series')
        all_series_response.raise_for_status()
        all_series = all_series_response.json()

        series_map = {s['id']: s for s in all_series}

        # 4. Encontrar os gêneros favoritos.
        favorite_genres = set()
        for series_id in high_rated_series_ids:
            if series_id in series_map:
                favorite_genres.add(series_map[series_id]['genre'])

        if not favorite_genres:
            return jsonify({"message": "Não foi possível identificar os gêneros favoritos."}), 200

        # 5. Filtrar as recomendações.
        user_rated_series_ids = [r['series_id'] for r in rated_series]
        
        recommendations = sorted(
            [   s for s in all_series 
                if s['genre'] in favorite_genres and s['id'] not in user_rated_series_ids
            ],
            key=lambda s: s['rating'],
            reverse=True
        )

        return jsonify(recommendations)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
             return jsonify({'error': 'Usuário não encontrado'}), 404
        return jsonify({'error': f'Erro de comunicação com serviços: {e}'}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Erro de conexão com outros serviços: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)
