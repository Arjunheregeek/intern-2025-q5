import os
import requests
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        print("Please check your .env file and ensure it contains GEMINI_API_KEY=your_api_key")
        return
    
    # Gemini API endpoint - using gemini-1.5-flash (free tier model)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # Request payload
    payload = {
        "contents": [{
            "parts": [{
                "text": "Say hello and introduce yourself as a friendly AI assistant."
            }]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Making request to Gemini API...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # Extract the generated text from the response
            if 'candidates' in data and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    text = candidate['content']['parts'][0]['text']
                    print(f"\nLLM Response:\n{text}")
                else:
                    print("Error: Unexpected response structure in candidate content")
                    print(f"Full response: {data}")
            else:
                print("Error: No candidates found in API response")
                print(f"Full response: {data}")
        else:
            print(f"API Error: {response.status_code}")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"Error message: {error_data['error'].get('message', 'Unknown error')}")
                else:
                    print(f"Response: {response.text}")
            except:
                print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Please check your internet connection.")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Please check your internet connection.")
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
