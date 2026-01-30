import tensorflow as tf
from tensorflow.keras import models, layers
import tensorflow_model_optimization as tfmot
import matplotlib.pyplot as plt
import os
import numpy as np

# Define Constants
IMAGE_SIZE = 256
BATCH_SIZE = 32
EPOCHS = 10 # Adjusted for reasonable training time
MODELS_DIR = 'models'
DATASET_DIR = os.path.join('dataset', 'tomato')

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

print(f"Checking dataset at {DATASET_DIR}...")
train_dir = os.path.join(DATASET_DIR, 'train')
val_dir = os.path.join(DATASET_DIR, 'val')

if not os.path.exists(train_dir) or not os.path.exists(val_dir):
    print(f"Error: Train/Val directories not found in {DATASET_DIR}")
    # Fallback: check if structure is different
    exit(1)

# Dataset Loading
print("Loading Training/Validation Data...")
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    train_dir,
    shuffle=True,
    image_size=(IMAGE_SIZE, IMAGE_SIZE),
    batch_size=BATCH_SIZE
)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    val_dir,
    shuffle=True,
    image_size=(IMAGE_SIZE, IMAGE_SIZE),
    batch_size=BATCH_SIZE
)

class_names = train_ds.class_names
n_classes = len(class_names)
print(f"Classes ({n_classes}): {class_names}")

# Optimization
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# Model Architecture
resize_and_rescale = tf.keras.Sequential([
  layers.Resizing(IMAGE_SIZE, IMAGE_SIZE),
  layers.Rescaling(1./255),
])

data_augmentation = tf.keras.Sequential([
  layers.RandomFlip("horizontal_and_vertical"),
  layers.RandomRotation(0.2),
])

input_shape = (BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, 3)

print("Building CNN Model...")
model = models.Sequential([
    resize_and_rescale,
    data_augmentation,
    layers.Conv2D(32, kernel_size=(3,3), activation='relu', input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64,  kernel_size=(3,3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64,  kernel_size=(3,3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(n_classes, activation='softmax'),
])

model.build(input_shape=input_shape)
model.summary()

model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
    metrics=['accuracy']
)

print(f"Starting training for {EPOCHS} epochs...")
history = model.fit(
    train_ds,
    batch_size=BATCH_SIZE,
    validation_data=val_ds,
    epochs=EPOCHS,
    verbose=1
)

# Save Keras Model
model_name = 'tomato_disease_model.h5'
model_path = os.path.join(MODELS_DIR, model_name)
model.save(model_path)
print(f"Model saved to {model_path}")

# Plotting
try:
    plt.figure(figsize=(8, 8))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    plot_path = os.path.join(MODELS_DIR, 'tomato_training_plot.png')
    plt.savefig(plot_path)
    print(f"Training plot saved to {plot_path}")
except Exception as e:
    print(f"Error plotting: {e}")


# --- Quantization Aware Training (QAT) ---
print("\n--- Starting Quantization Aware Training ---")

# --- Quantization Aware Training (QAT) ---
print("\n--- Starting Quantization Aware Training ---")

# Apply QAT to the whole model
# tfmot.quantization.keras.quantize_model automatically handles compatible layers
# and leaves others alone.
try:
    quant_aware_model = tfmot.quantization.keras.quantize_model(model)
    quant_aware_model.summary()

    quant_aware_model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
        metrics=['accuracy']
    )

    # Fine-tune with QAT - typically needs fewer epochs
    print("Fine-tuning with QAT for 2 epochs...")
    q_history = quant_aware_model.fit(
        train_ds,
        batch_size=BATCH_SIZE,
        validation_data=val_ds,
        epochs=2,
        verbose=1
    )
except Exception as e:
    print(f"Error during QAT setup/training: {e}")
    # Fallback to standard model for TFLite conversion if QAT fails
    quant_aware_model = model

# Converting to TFLite
print("\n--- Converting to TFLite ---")
converter = tf.lite.TFLiteConverter.from_keras_model(quant_aware_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

try:
    quantized_tflite_model = converter.convert()
    tflite_path = os.path.join(MODELS_DIR, 'tomato_disease_model.tflite')
    with open(tflite_path, 'wb') as f:
        f.write(quantized_tflite_model)
    print(f"Quantized TFLite model saved to {tflite_path}")
except Exception as e:
    print(f"Error converting to TFLite: {e}")

print("Done.")
