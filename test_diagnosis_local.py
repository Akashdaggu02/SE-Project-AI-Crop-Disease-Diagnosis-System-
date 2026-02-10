import requests
import json
import os

# Configuration
BASE_URL = 'http://localhost:5000/api/diagnosis/detect'
# Use a real image from uploads
IMAGE_PATH = 'backend/uploads/chat_anonymous_20260211_001737_tomato.png' 

# Create a dummy image if not exists (fallback)
if not os.path.exists(IMAGE_PATH):
    print(f"Warning: {IMAGE_PATH} not found. Using dummy.")
    IMAGE_PATH = 'tomato.png'
    from PIL import Image
    img = Image.new('RGB', (224, 224), color = 'red')
    img.save(IMAGE_PATH)

def test_diagnosis(crop_name):
    print(f"\nTesting diagnosis for crop: {crop_name}")
    try:
        files = {'image': open(IMAGE_PATH, 'rb')}
        data = {'crop': crop_name, 'language': 'en'}
        
        response = requests.post(BASE_URL, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Success!")
            print(f"Prediction: {result.get('prediction', {}).get('disease', 'Unknown')}")
            print(f"Confidence: {result.get('prediction', {}).get('confidence', 0)}%")
        else:
            print("Failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test Supported Crop (Tomato)
    test_diagnosis('tomato')
    
    # Test Unsupported Crop (Grape) - Should fail currently
    test_diagnosis('grape')
