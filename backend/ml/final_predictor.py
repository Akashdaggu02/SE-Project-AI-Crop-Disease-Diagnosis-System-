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

    severity = estimate_severity(image_path)
    stage = classify_stage(severity)

    return {
        "crop": crop,
        "disease": disease,
        "confidence": round(confidence, 2),
        "severity_percent": severity,
        "stage": stage
    }
