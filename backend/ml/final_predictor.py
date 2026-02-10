from disease_classifier import predict
from severity_estimator import estimate_severity
from stage_classifier import classify_stage

import os

# Get absolute path to the project root's models directory
# current file is in backend/ml/
# so ../../models resolves to project_root/models/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

MODEL_MAP = {
    "tomato": os.path.join(MODELS_DIR, "tomato_disease_model.h5"),
    "rice": os.path.join(MODELS_DIR, "rice_disease_model.h5"),
    "wheat": os.path.join(MODELS_DIR, "wheat_disease_model.h5"),
    "cotton": os.path.join(MODELS_DIR, "cotton_disease_model.h5")
}

CLASS_NAMES = {
    "tomato": [
        "Healthy",
        "Tomato___Bacterial_spot",
        "Tomato___Early_blight",
        "Tomato___Late_blight",
        "Tomato___Leaf_Mold",
        "Tomato___Septoria_leaf_spot",
        "Tomato___Spider_mites Two-spotted_spider_mite",
        "Tomato___Target_Spot",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "Tomato___Tomato_mosaic_virus"
    ],
    "rice": ["Healthy", "BrownSpot", "Hispa", "LeafBlast"],
    "wheat": ["Healthy", "Brown rust", "Yellow rust", "Loose Smut"],
    "cotton": ["Healthy", "Bacterial Blight", "Curl Virus", "Leaf Hopper Jassids"]
}

def full_prediction(image_path, crop):
    # Check if crop is supported
    if crop not in MODEL_MAP:
        raise ValueError(f"Crop '{crop}' is not supported by local models.")

    model_path = MODEL_MAP[crop]
    
    # Check if model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file for {crop} not found at {model_path}")

    disease, confidence = predict(
        image_path,
        model_path,
        CLASS_NAMES[crop]
    )

    severity = estimate_severity(image_path)
    stage = classify_stage(severity)

    return {
        "crop": crop,
        "disease": disease,
        "confidence": round(confidence, 2),
        "severity_percent": severity,
        "stage": stage
    }

def identify_and_predict(image_path):
    """
    Automatically identifies the crop and detects disease by trying all models.
    Returns the result from the model with the highest confidence.
    """
    best_result = None
    highest_confidence = -1.0
    
    print(f"DEBUG: Auto-identifying crop for image: {image_path}")
    
    for crop, model_path in MODEL_MAP.items():
        try:
            print(f"DEBUG: Testing {crop} model...")
            # We use the existing predict function
            disease, confidence = predict(
                image_path,
                model_path,
                CLASS_NAMES[crop]
            )
            
            print(f"DEBUG: {crop} result: {disease} ({confidence}%)")
            
            # naive heuristic: simply pick the highest confidence
            # A better approach would be a dedicated crop classifier, but this works for now
            if confidence > highest_confidence:
                highest_confidence = confidence
                best_result = {
                    "crop": crop,
                    "disease": disease,
                    "confidence": round(confidence, 2)
                }
                
        except Exception as e:
            print(f"DEBUG: Failed to run {crop} model: {e}")
            continue
            
    if best_result:
        # Once we identified the winner, get full details (severity, etc.)
        # We already have disease/confidence, just get severity
        severity = estimate_severity(image_path)
        stage = classify_stage(severity)
        
        best_result["severity_percent"] = severity
        best_result["stage"] = stage
        return best_result
    else:
        raise Exception("Could not identify crop or detect disease with any available model.")
