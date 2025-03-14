import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from gtts import gTTS
import base64
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    print("\n" + "="*80)
    print("ERROR: No valid GEMINI_API_KEY found in .env file")
    print("Please follow these steps to get a valid API key:")
    print("1. Go to https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Create a new API key")
    print("4. Copy the API key and paste it in the .env file")
    print("="*80 + "\n")
    raise ValueError("No valid GEMINI_API_KEY found in .env file")

try:
    # Configure the Gemini API
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Initialize the model - try gemini-1.5-pro first, fall back to gemini-pro if needed
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
    except Exception as e:
        print(f"Could not initialize gemini-1.5-pro model: {e}")
        print("Falling back to gemini-pro model")
        model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    raise

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        # Get response from Gemini API
        response = model.generate_content(user_message)
        bot_response = response.text
        
        # Convert response to speech
        tts = gTTS(text=bot_response, lang='en')
        
        # Save audio to a bytes buffer
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # Convert to base64 for sending to the client
        audio_data = base64.b64encode(fp.read()).decode('utf-8')
        
        return jsonify({
            'response': bot_response,
            'audio': audio_data
        })
    
    except Exception as e:
        error_message = str(e)
        print(f"Error in chat endpoint: {error_message}")
        
        # Check if it's an API key error
        if "API_KEY_INVALID" in error_message or "API key not valid" in error_message:
            error_message = "Invalid API key. Please check your .env file and make sure you've added a valid Gemini API key from https://makersuite.google.com/app/apikey"
        
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run(debug=True) 