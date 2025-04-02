from flask import Flask, render_template, request, session, jsonify, send_from_directory
from flask_session import Session
from model import ChatModel, get_weather, suggest_crops, predict_disease
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'static/temp_images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

Session(app)

chat_model = ChatModel()

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'chat_history' not in session:
        session['chat_history'] = []
    if 'language' not in session:
        session['language'] = None

    weather_data = None
    suggested_crops = None
    disease_result = None
    
    if request.method == 'POST':
        # Weather and crop suggestion
        if 'location' in request.form and 'get_weather' in request.form:
            location = request.form.get('location')
            weather_data = get_weather(location)
            if not isinstance(weather_data, dict) or 'error' not in weather_data:
                suggested_crops = suggest_crops(weather_data)
        
        # Disease prediction
        if 'crop_type' in request.form and 'predict_disease' in request.form:
            crop_type = request.form.get('crop_type')
            image = request.files.get('image')
            weather_input = session.get('weather_data', {}).get('description', 'unknown')
            disease_result = predict_disease(crop_type, weather_input, image)
            if disease_result and 'image_path' in disease_result:
                disease_result['image_path'] = disease_result['image_path'].replace('\\', '/')
            session['disease_result'] = disease_result
    
    if weather_data:
        session['weather_data'] = weather_data
    
    return render_template('index.html', 
                         weather_data=weather_data, 
                         suggested_crops=suggested_crops,
                         disease_result=session.get('disease_result'),
                         chat_history=session['chat_history'],
                         language=session['language'])

@app.route('/static/temp_images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form.get('chat_input')
    if user_input:
        if not session.get('language'):
            if user_input.lower() in ['english', 'hindi', 'tamil']:
                session['language'] = user_input.lower()
                response = "Great! I'll proceed in " + user_input + ". How can I assist you?"
            else:
                response = "Please choose a language: English, Hindi, Tamil."
        else:
            response = chat_model.process_message(user_input, session['language'])
        session['chat_history'].append({'user': user_input, 'bot': response})
        session.modified = True
        return jsonify({'user': user_input, 'bot': response})
    return jsonify({'error': 'No input provided'}), 400

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    session['chat_history'] = []
    session['language'] = None
    session.modified = True
    return jsonify({'status': 'Chat cleared'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
    



 