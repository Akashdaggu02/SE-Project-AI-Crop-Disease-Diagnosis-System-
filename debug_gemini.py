import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load env from backend/.env
env_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(env_path)

api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
print(f"Loaded API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("Error: API Key not found!")
    exit(1)

genai.configure(api_key=api_key)

try:
    print("Listing available models...")
    working_model = None
    
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Found model: {m.name}")
            try:
                print(f"  Testing {m.name}...")
                model = genai.GenerativeModel(m.name)
                response = model.generate_content("Hello")
                print(f"  SUCCESS with {m.name}")
                working_model = m.name
                # We prefer flash if available, so keep looking if it's not flash
                if 'flash' in m.name:
                    break
            except Exception as e:
                print(f"  Failed with {m.name}: {e}")

    if working_model:
        print(f"\nRECOMMENDED MODEL: {working_model}")
    else:
        print("\nNO WORKING MODELS FOUND.")
        
except Exception as e:
    print(f"Error listing models: {e}")
