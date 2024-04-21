from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/handle_message": {"origins": "*"}})

@app.route('/handle_message', methods=['POST']) # execute handle_message when sent a POST request.

def handle_message(message: str): 
    message = request.json['message']
    print(message)
    # response = chatbot_function(message) # placeholder for chatbot function in agent.py
    # return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)