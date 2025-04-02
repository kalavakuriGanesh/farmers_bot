import requests
from io import BytesIO
import base64
from PIL import Image
import google.generativeai as genai
import os
from datetime import datetime

# OpenWeatherMap API key (replace with yours)
WEATHER_API_KEY = "5e5a99e2ccdbcbae6d474080aa2e6498"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

# Gemini API key (replace with yours from Google AI Studio)
GEMINI_API_KEY = "AIzaSyCNMT-XLICWiwxsq2xBHorLO5kY6toRURk"
genai.configure(api_key=GEMINI_API_KEY)

def clean_text(text):
    """Remove Markdown bold markers (**) and other special characters from text."""
    if isinstance(text, str):
        return text.replace('**', '').replace('*', '').strip()
    return text

def get_weather(location):
    """Fetch weather data from OpenWeatherMap."""
    try:
        params = {'q': location, 'appid': WEATHER_API_KEY, 'units': 'metric'}
        response = requests.get(WEATHER_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': data['main']['temp'],
                'description': clean_text(data['weather'][0]['description']),
                'humidity': data['main']['humidity']
            }
        else:
            return {'error': 'Could not fetch weather data'}
    except Exception as e:
        return {'error': str(e)}

def suggest_crops(weather_data):
    """Suggest crops based on climate conditions."""
    try:
        temp = weather_data['temp']
        humidity = weather_data['humidity']
        conditions = weather_data['description'].lower()
        
        if temp > 30 and humidity > 60:
            return clean_text("Suggested crops: Rice, Sugarcane, Banana")
        elif 20 <= temp <= 30 and humidity > 50:
            return clean_text("Suggested crops: Wheat, Corn, Soybean")
        elif temp < 20 and "rain" in conditions:
            return clean_text("Suggested crops: Barley, Peas, Potatoes")
        else:
            return clean_text("Suggested crops: Cotton, Millet, Sorghum")
    except Exception as e:
        return f"Error suggesting crops: {str(e)}"
    
def image_to_base64(image):
    """Convert uploaded image (FileStorage) to base64 and return both base64 and file path."""
    if image:
        try:
            # Open and process the image
            img = Image.open(image)
            if img.format != 'JPEG':
                img = img.convert('RGB')
            
            # Save to a temporary file
            temp_dir = 'static/temp_images'
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'plant_{timestamp}.jpg'
            filepath = os.path.join(temp_dir, filename)
            
            # Save the image
            img.save(filepath, format="JPEG")
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return {
                'base64': img_base64,
                'filepath': f'/static/temp_images/{filename}',
                'success': True
            }
        except Exception as e:
            return {
                'error': f"Image processing error: {str(e)}",
                'success': False
            }
    return {
        'error': "No image provided",
        'success': False
    }

def predict_disease(crop_type, weather, image):
    """Predict plant disease with image and precautions."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        weather_data = weather if isinstance(weather, str) else "unknown"
        prompt = f"""
        Analyze this {crop_type} plant image and predict potential diseases based on these weather conditions: {weather_data}.
        Provide:
        1. Disease name and description
        2. Symptoms
        3. Prevention measures
        4. Treatment recommendations
        Format the response in a clear, structured way.
        """
        
        if image:
            img_data = image_to_base64(image)
            if not img_data['success']:
                return {'error': img_data['error']}
                
            response = model.generate_content([
                prompt, 
                {"mime_type": "image/jpeg", "data": img_data['base64']}
            ])
            
            # Clean and structure the prediction
            cleaned_prediction = clean_text(response.text)
            return {
                'prediction': cleaned_prediction,
                'image_path': img_data['filepath'],  # Use the saved file path
                'precautions': clean_text("""
                Recommended Precautions:
                1. Regular monitoring of plant health
                2. Proper irrigation management
                3. Use of organic fungicides
                4. Maintain proper plant spacing
                5. Remove infected plant parts
                """),
                'success': True
            }
        else:
            return {
                'error': "No image provided for analysis",
                'success': False
            }
    except Exception as e:
        return {
            'error': f"Gemini API error: {str(e)}",
            'success': False
        }

class ChatModel:
    """Chatbot model with language support."""
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def process_message(self, user_input, language):
        """Process user message in the chosen language with improved formatting."""
        try:
            if language == 'hindi':
                prompt = f"""
                आप एक किसान सहायक हैं। उपयोगकर्ता ने पूछा: '{user_input}'.
                कृपया निम्नलिखित प्रारूप में उत्तर दें:
                1. मुख्य जवाब
                2. अतिरिक्त सुझाव
                3. महत्वपूर्ण टिप्स
                """
            elif language == 'tamil':
                prompt = f"""
                You are a farming assistant. The user asked: '{user_input}'.
                Please respond in Tamil with:
                1. Main answer
                2. Additional suggestions
                3. Important tips
                """
            else:  # Default to English
                prompt = f"""
                You are a farming assistant. The user asked: '{user_input}'.
                Please provide a structured response with:
                1. Main answer
                2. Additional suggestions
                3. Important tips
                """
            response = self.model.generate_content(prompt)
            return clean_text(response.text)
        except Exception as e:
            return clean_text(f"Error processing message: {str(e)}. Please try again!")