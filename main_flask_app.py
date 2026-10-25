import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from ai_engine import AIEngine
from utils import logger

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-medipulse-secret")

# Initialize central AI Engine
ai_engine = AIEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctor')
def doctor():
    return render_template('doctor.html')

@app.route('/clinic')
def clinic():
    return render_template('clinic.html')

@app.route('/api/lifealert', methods=['POST'])
def api_lifealert():
    """Emergency detection endpoint."""
    data = request.json
    symptoms = data.get('symptoms', '')
    if not symptoms:
        return jsonify({"error": "Symptoms required"}), 400
    
    result = ai_engine.is_emergency(symptoms)
    return jsonify(result)

@app.route('/api/healthsense', methods=['POST'])
def api_healthsense():
    data = request.json
    symptoms = data.get('symptoms', '')
    if not symptoms:
        return jsonify({"error": "Symptoms required"}), 400
    return jsonify(ai_engine.get_healthsense(symptoms))

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    chat_history = data.get('history', '')
    user_input = data.get('input', '')
    if not user_input:
        return jsonify({"error": "Input required"}), 400
    return jsonify(ai_engine.chat_healthgpt(chat_history, user_input))

@app.route('/api/prevent', methods=['POST'])
def api_prevent():
    data = request.json
    focus_area = data.get('focus_area', '')
    return jsonify(ai_engine.get_prevent360(focus_area))

@app.route('/api/truthcheck', methods=['POST'])
def api_truthcheck():
    data = request.json
    query = data.get('query', '')
    return jsonify(ai_engine.get_truthcheck(query))

@app.route('/api/medisafe', methods=['POST'])
def api_medisafe():
    data = request.json
    medicine = data.get('medicine', '')
    return jsonify(ai_engine.get_medisafe(medicine))

@app.route('/api/doctorlens', methods=['POST'])
def api_doctorlens():
    data = request.json
    doctor_name = data.get('doctor_name', '')
    return jsonify(ai_engine.get_doctorlens(doctor_name))

@app.route('/api/carefinder', methods=['POST'])
def api_carefinder():
    data = request.json
    symptoms = data.get('symptoms', '')
    return jsonify(ai_engine.get_carefinder(symptoms))

@app.route('/api/clinicscope', methods=['POST'])
def api_clinicscope():
    data = request.json
    url = data.get('url', '')
    if not url:
        return jsonify({"error": "URL required"}), 400
    return jsonify(ai_engine.get_clinicscope(url))

@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Server Error: {e}")
    return jsonify(error="An internal server error occurred."), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)