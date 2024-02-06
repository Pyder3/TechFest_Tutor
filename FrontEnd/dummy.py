from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/validate', methods=['POST'])
def validate_code():
    data = request.json
    # question_number = data.get('questionNumber')
    user_code = data.get('code')
    
    # Dummy validation logic
    is_correct = random.choice([True, False])
    is_optimal = random.choice([True, False]) if is_correct else False

    if not is_correct:
        return jsonify({'correct': False, 'hint': 'Try using a loop here.'})
    elif is_correct and not is_optimal:
        return jsonify({'correct': True, 'optimal': False})
    else:
        return jsonify({'correct': True, 'optimal': True})

@app.route('/correctCode', methods=['POST'])
def get_correct_code():
    data = request.json
    question_number = data.get('questionNumber')
    
    # Dummy correct code
    correct_code = "def add(a, b):\n    return a + b"
    
    return jsonify({'correctCode': correct_code})

if __name__ == '__main__':
    app.run(debug=True)
