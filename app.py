import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from gtts import gTTS
import base64
import io
from dotenv import load_dotenv
import json
import time

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
        print("Successfully initialized gemini-1.5-pro model")
    except Exception as e:
        print(f"Could not initialize gemini-1.5-pro model: {e}")
        print("Falling back to gemini-pro model")
        model = genai.GenerativeModel('gemini-pro')
        print("Successfully initialized gemini-pro model")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    raise

app = Flask(__name__)

# Store conversation history
conversation_history = []
MAX_HISTORY_LENGTH = 10

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history
    
    data = request.json
    user_message = data.get('message', '')
    voice_lang = data.get('voice', 'en')
    speech_rate = data.get('rate', 1.0)
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        # Add user message to conversation history
        conversation_history.append({"role": "user", "parts": [user_message]})
        
        # Trim history if it gets too long
        if len(conversation_history) > MAX_HISTORY_LENGTH * 2:  # Keep pairs of messages
            conversation_history = conversation_history[-MAX_HISTORY_LENGTH*2:]
        
        # Prepare conversation for Gemini
        gemini_messages = []
        for msg in conversation_history:
            if msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["parts"][0]]})
            else:
                gemini_messages.append({"role": "model", "parts": [msg["parts"][0]]})
        
        # Get response from Gemini API with conversation history
        try:
            # First try with conversation history
            chat = model.start_chat(history=gemini_messages[:-1])
            response = chat.send_message(user_message)
            bot_response = response.text
        except Exception as history_error:
            print(f"Error with conversation history: {history_error}")
            print("Falling back to single message mode")
            # Fallback to single message if history fails
            response = model.generate_content(user_message)
            bot_response = response.text
        
        # Add bot response to conversation history
        conversation_history.append({"role": "assistant", "parts": [bot_response]})
        
        # Convert response to speech
        try:
            tts = gTTS(text=bot_response, lang=voice_lang, slow=False)
            
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
        except Exception as tts_error:
            print(f"Error in text-to-speech: {tts_error}")
            # Return text response without audio if TTS fails
            return jsonify({
                'response': bot_response,
                'error': f"Text-to-speech failed: {str(tts_error)}"
            })
    
    except Exception as e:
        error_message = str(e)
        print(f"Error in chat endpoint: {error_message}")
        
        # Check if it's an API key error
        if "API_KEY_INVALID" in error_message or "API key not valid" in error_message:
            error_message = "Invalid API key. Please check your .env file and make sure you've added a valid Gemini API key from https://makersuite.google.com/app/apikey"
        
        return jsonify({'error': error_message}), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    global conversation_history
    conversation_history = []
    return jsonify({'status': 'success', 'message': 'Conversation history cleared'})

@app.route('/voices', methods=['GET'])
def get_voices():
    # Return a list of supported languages for gTTS
    voices = [
        {"code": "en", "name": "English"},
        {"code": "en-us", "name": "English (US)"},
        {"code": "en-uk", "name": "English (UK)"},
        {"code": "en-au", "name": "English (Australia)"},
        {"code": "en-in", "name": "English (India)"},
        {"code": "fr", "name": "French"},
        {"code": "es", "name": "Spanish"},
        {"code": "de", "name": "German"},
        {"code": "it", "name": "Italian"},
        {"code": "ja", "name": "Japanese"},
        {"code": "ko", "name": "Korean"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "ru", "name": "Russian"},
        {"code": "zh-cn", "name": "Chinese (Mandarin)"}
    ]
    return jsonify(voices)

if __name__ == '__main__':
    app.run(debug=True) 