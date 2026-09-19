from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Lead Hunter API is running"})

@app.route('/hunt', methods=['POST'])
def hunt_leads():
    # Your lead hunting logic here
    return jsonify({"status": "success", "leads": []})
