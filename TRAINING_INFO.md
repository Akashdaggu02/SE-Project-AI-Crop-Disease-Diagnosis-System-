# Crop Disease Model Training Info

## Potato Model
- **Status**: **COMPLETED**
- **Script**: `training/train_potato.py`
- **Model Path**: `models/potato_disease_model.h5`
- **Accuracy**: ~88% (Training), ~88% (Validation)

## Maize (Corn) Model
- **Status**: **IN PROGRESS**
- **Script**: `training/train_maize.py`
- **Architecture**: VGG16 (Transfer Learning)
- **Model Path**: `models/maize_disease_model.h5`
- **Progress**: Training (5 Epochs scheduled)

## Tomato Model
- **Status**: **IN PROGRESS**
- **Script**: `training/train_tomato.py`
- **Architecture**: Custom CNN + Quantization Aware Training (QAT)
- **Output**: 
  - `models/tomato_disease_model.h5`
  - `models/tomato_disease_model.tflite` (Optimized for Mobile)
- **Dataset**: `dataset/tomato`
- **Progress**: Script started, initializing training.

### Details
- Maize training is likely finishing up.
- Tomato training includes an additional step of QAT (Quantization Aware Training) and TFLite conversion as requested.
