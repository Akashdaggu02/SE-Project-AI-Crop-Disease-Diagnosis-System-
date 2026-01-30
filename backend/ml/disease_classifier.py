import cv2
import numpy as np
import tensorflow as tf
import os

def predict(image_path, model_path, class_names):
    try:
        # Input validation
        if not class_names:
            raise ValueError("class_names cannot be empty")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        print(f"Loading model from: {model_path}")
        
        # 1. Load the full model (architecture + weights)
        # This handles Custom CNNs, VGG16, InceptionV3, etc. automatically
        try:
            model = tf.keras.models.load_model(model_path, compile=False)
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
        
        # 2. Inspect Model Input Shape
        input_shape = model.input_shape
        # Input shape usually looks like (None, Height, Width, Channels)
        # Handle case where input_shape is a list (some models)
        if isinstance(input_shape, list):
            input_shape = input_shape[0]
            
        target_h, target_w = input_shape[1], input_shape[2]
        channels = input_shape[3] if len(input_shape) > 3 else 3
        
        print(f"Model expects input shape: {input_shape} (H={target_h}, W={target_w}, C={channels})")

        # 3. Read and preprocess image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found or cannot be read: {image_path}")
        
        # Handle Color Channels
        if channels == 1:
            # Convert to Grayscale
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Expand dims to make it (H, W, 1) later
            img = np.expand_dims(img, axis=-1)
        else:
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize
        img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
        
        # Re-add channel dim if lost during resize (for grayscale openCV resize might return 2D array)
        if channels == 1 and len(img.shape) == 2:
             img = np.expand_dims(img, axis=-1)
             
        # Check if the model already has a Rescaling layer
        # If it does, it expects [0, 255] inputs. If not, it likely expects [0, 1].
        has_rescaling = False
        try:
            def check_rescaling(layers):
                for layer in layers:
                    if isinstance(layer, tf.keras.layers.Rescaling):
                        return True
                    if hasattr(layer, 'layers'):
                        if check_rescaling(layer.layers):
                            return True
                return False
            
            has_rescaling = check_rescaling(model.layers)
            print(f"Model has built-in Rescaling layer: {has_rescaling}")
        except Exception as e:
            print(f"Could not check for Rescaling layer: {e}")
            has_rescaling = False

        if not has_rescaling:
            # Normalize to [0, 1] only if model doesn't handle it
            img = img.astype(np.float32) / 255.0
            print("Applied manual normalization (1/255)")
        else:
            # Verify input range is [0, 255] (Model handles scaling)
            # img is already [0-255] from cv2.resize (if uint8) or we need to ensure float
             img = img.astype(np.float32) # Convert to float but keep scale 0-255
             print("Skipped manual normalization (Model handles it)")
        
        # Add Batch Dimension -> (1, H, W, C)
        img = np.expand_dims(img, axis=0)
        
        # 4. Prediction
        preds = model.predict(img, verbose=0)
        print(f"Raw Predictions: {preds}")
        idx = np.argmax(preds)
        confidence = np.max(preds) * 100
        
        if idx >= len(class_names):
            print(f"Warning: Predicted index {idx} out of bounds for class names (len={len(class_names)})")
            disease_name = "Unknown"
        else:
            disease_name = class_names[idx]
        
        print(f"Prediction: {disease_name} ({confidence:.2f}%)")
        return disease_name, confidence
        
    except Exception as e:
        print(f"Error in predict function: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
