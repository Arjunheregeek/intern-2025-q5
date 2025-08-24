import os
import requests
from dotenv import load_dotenv

class GeminiAPIClient:
    """Simple Gemini API client for chatbot."""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
    
    def call_api(self, prompt: str) -> str:
        """Call Gemini API and return response text."""
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and data['candidates']:
                    candidate = data['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        return candidate['content']['parts'][0]['text'].strip()
                
                raise Exception("Invalid response structure")
            else:
                raise Exception(f"API error: {response.status_code}")
                
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")
