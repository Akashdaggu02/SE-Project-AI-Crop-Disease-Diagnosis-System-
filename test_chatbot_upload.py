import requests
import os

BASE_URL = "http://localhost:5000/api/chatbot"
IMAGE_PATH = r"C:\Users\maddy\OneDrive\Desktop\SE-Project-AI-Crop-Disease-Diagnosis-System-\frontend-mobile\assets\images\tomato.png"

def test_chatbot_upload():
    print(f"Testing chatbot upload with image: {IMAGE_PATH}")
    
    if not os.path.exists(IMAGE_PATH):
        print("Error: Image file not found.")
        return

    # 1. Upload Image
    print("\n1. Uploading image...")
    try:
        with open(IMAGE_PATH, 'rb') as img_file:
            files = {'image': img_file}
            response = requests.post(f"{BASE_URL}/upload", files=files)
            
        print(f"Upload Status Code: {response.status_code}")
        print(f"Upload Response: {response.json()}")
        
        if response.status_code != 200:
            print("Upload failed.")
            return
            
        file_path = response.json().get('file_path')
        print(f"Uploaded File Path: {file_path}")
        
    except Exception as e:
        print(f"Upload Exception: {e}")
        return

    # 2. Send Message with Image
    print("\n2. Sending message with image...")
    payload = {
        "message": "Start diagnosis for this crop.",
        "language": "en",
        "image_path": file_path
    }
    
    try:
        response = requests.post(f"{BASE_URL}/message", json=payload)
        print(f"Message Status Code: {response.status_code}")
        print(f"Message Response: {response.json()}")
        
    except Exception as e:
         print(f"Message Exception: {e}")

if __name__ == "__main__":
    test_chatbot_upload()
