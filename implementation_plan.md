# Implementation Plan - Grape & Rice Training

## Goal
Train disease classification models for Grape (using user-provided custom CNN) and Rice (using InceptionV3), and ensure all training scripts are running correctly.

## Proposed Changes
### Training Scripts
#### [NEW] [train_grape.py](file:///d:/SE ROJECT/AI-Crop-Diagnosis/training/train_grape.py)
- Implement the custom CNN architecture provided by the user.
- Use `dataset/Grape` (classes: `Black Rot`, `ESCA`, `Healthy`, `Leaf Blight`).
- Save model to `models/grape_disease_model.h5`.

#### [EXISTING] [train_rice.py](file:///d:/SE ROJECT/AI-Crop-Diagnosis/training/train_rice.py)
- Already refactored to use `tf.keras.applications.InceptionV3` to avoid TF Hub version issues.
- Will be executed.

## Verification Plan
### Automated Verification
- Run `python training/train_grape.py` and monitor for successful start and model saving.
- Run `python training/train_rice.py` and monitor for successful start and model saving.
- Check `TRAINING_INFO.md` for status updates.

### Manual Verification
- Verify that `.h5` files are created in `models/` directory after training completes.
