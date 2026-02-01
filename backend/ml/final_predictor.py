from disease_classifier import predict
from severity_estimator import estimate_severity
from stage_classifier import classify_stage

MODEL_MAP = {
    "grape": "../models/grape_disease_model.h5",
    "maize": "../models/maize_disease_model.h5",
    "potato": "../models/potato_disease_model.h5",
    "rice": "../models/rice_disease_model.h5",
    "tomato": "../models/tomato_disease_model.h5"
}

CLASS_NAMES = {
    "grape": [
        "Black Rot",
        "ESCA",
        "Healthy",
        "Leaf Blight"
    ],
    "maize": [
        "Blight",
        "Common_Rust",
        "Gray_Leaf_Spot",
        "Healthy"
    ],
    "potato": [
        "Early Blight",
        "Late Blight",
        "Healthy"
    ],
    "rice": [
        "Bacterial leaf blight",
        "Brown spot",
        "Leaf smut"
    ],
    "tomato": [
        "Healthy",
        "Bacterial spot",
        "Early blight",
        "Late blight",
        "Leaf Mold",
        "Septoria leaf spot",
        "Spider mites Two-spotted spider mite",
        "Target Spot",
        "Tomato Yellow Leaf Curl Virus",
        "Tomato mosaic virus"
    ]
}

def full_prediction(image_path, crop):
    disease, confidence = predict(
        image_path,
        MODEL_MAP[crop],
        CLASS_NAMES[crop]
    )

    # If the crop is rice and confidence is low (not strongly classified as a disease),
    # classify as Healthy.
    if crop == 'rice' and confidence < 60.0:
        disease = 'Healthy'
        # Since we are defaulting to Healthy, we can set confidence to high or keep it.
        # Setting to 0.0 or a high value? If it's "Healthy" by default, usually we imply it's safe.
        # Let's keep the confidence or set to a standard value? 
        # For this requirement, "classify to healthy" implies the result is Healthy.
        pass

    severity = estimate_severity(image_path)
    stage = classify_stage(severity)

    return {
        "crop": crop,
        "disease": disease,
        "confidence": float(round(confidence, 2)),
        "severity_percent": float(severity),
        "stage": stage
    }
