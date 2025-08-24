# LLM API Integration Demo

A simple Python script demonstrating basic integration with Google Gemini's free API.

## Setup

1. **Get a free API key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a free API key for Gemini

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key:**
   ```bash
   cp .env.example .env
   # Edit .env and replace 'your_gemini_api_key_here' with your actual API key
   ```

## Usage

Run the script:
```bash
python main.py
```

The script will make a request to Google Gemini API and print a greeting response.

## Features

- ✅ Secure API key handling via environment variables
- ✅ Basic error handling for network and API errors
- ✅ Timeout protection
- ✅ Clear error messages

## Security

- API keys are stored in `.env` file (not tracked by git)
- Environment variables loaded using `python-dotenv`
- No hardcoded secrets in source code

## Demo

Expected output:
```
Making request to Gemini API...

LLM Response:
Hello! I'm Gemini, a friendly AI assistant created by Google. I'm here to help you with a wide variety of tasks...
```
