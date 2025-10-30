from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory database for series
series = []
series_id_counter = 1

class Series:
    def __init__(self, title, genre, rating):
        global series_id_counter
        self.id = series_id_counter
        self.title = title
        self.genre = genre
        self.rating = rating
        series_id_counter += 1

@app.route('/series', methods=['GET'])
def get_series():
    return jsonify([s.__dict__ for s in series])

@app.route('/series', methods=['POST'])
def create_series():
    data = request.get_json()
    if not data or not 'title' in data or not 'genre' in data or not 'rating' in data:
        return jsonify({'error': 'Missing title, genre, or rating'}), 400
    
    new_series = Series(title=data['title'], genre=data['genre'], rating=data['rating'])
    series.append(new_series)
    return jsonify(new_series.__dict__), 201

if __name__ == '__main__':
    # Running on port 5002 to avoid conflicts with other services
    app.run(debug=True, port=5002)
