import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.path.join(os.getcwd(), 'backend', 'ml'))

try:
    from backend.ml.final_predictor import identify_and_predict
    print("Successfully imported identify_and_predict")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

IMAGE_PATH = r"C:\Users\maddy\OneDrive\Desktop\SE-Project-AI-Crop-Disease-Diagnosis-System-\frontend-mobile\assets\images\tomato.png"

if __name__ == "__main__":
    print(f"Testing local diagnosis on: {IMAGE_PATH}")
    if not os.path.exists(IMAGE_PATH):
        print("Image file not found!")
        sys.exit(1)
        
    try:
        result = identify_and_predict(IMAGE_PATH)
        print("Diagnosis Result:")
        print(result)
    except Exception as e:
        print(f"Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
