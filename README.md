# Speaking Chatbot with Gemini API

This is a web-based chatbot that uses Google's Gemini API to generate responses and converts them to speech.

## Features

- Text-based chat interface
- Voice output for chatbot responses
- Powered by Google's Gemini API

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Get a Gemini API key:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the API key

4. Create a `.env` file in the project root directory with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. Run the application:
   ```
   python app.py
   ```
6. Open your browser and navigate to `http://localhost:5000`

## Troubleshooting API Key Issues

If you see an error like "API key not valid", please check:

1. You've created the API key specifically for Gemini at [Google AI Studio](https://makersuite.google.com/app/apikey)
2. You've copied the entire API key correctly into the `.env` file
3. The API key is active and not restricted by IP or other settings

## How to Use

1. Type your message in the input field
2. Press Enter or click the Send button
3. The chatbot will respond with text and speech

## Requirements

- Python 3.7+
- Google Gemini API key 