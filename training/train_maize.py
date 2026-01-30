import tensorflow as tf
from tensorflow.keras.layers import Input, Lambda, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
import numpy as np
from glob import glob
import matplotlib.pyplot as plt
import os

# Define Constants
IMAGE_SIZE = [224, 224] # VGG16 uses 224x224
BATCH_SIZE = 32
EPOCHS = 5
DATASET_PATH = os.path.join('dataset', 'Maize')
MODELS_DIR = 'models'

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

print(f"Checking dataset at {DATASET_PATH}...")
if not os.path.exists(DATASET_PATH):
    print(f"Error: Dataset directory not found at {DATASET_PATH}")
    # Fallback check for 'Corn' if 'Maize' doesn't exist
    if os.path.exists(os.path.join('dataset', 'Corn')):
        print("Found 'Corn' directory instead. Using that.")
        DATASET_PATH = os.path.join('dataset', 'Corn')
    else:
        exit(1)

# Get number of classes
folders = glob(os.path.join(DATASET_PATH, '*'))
print(f"Found {len(folders)} classes: {[os.path.basename(f) for f in folders]}")

# Load VGG16
# weights='imagenet' will download weights if not present
print("Loading VGG16 model...")
vgg = VGG16(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)

# Freeze VGG weights
for layer in vgg.layers:
    layer.trainable = False

# Add custom head
x = Flatten()(vgg.output)
prediction = Dense(len(folders), activation='softmax')(x)

# Create Model
model = Model(inputs=vgg.input, outputs=prediction)
model.summary()

# Compile
model.compile(
  loss='categorical_crossentropy',
  optimizer='adam',
  metrics=['accuracy']
)

# Data Generators
# Using ImageDataGenerator with validation split since we assume a flat structure or single folder per class
# The user's snippet used separate train/test folders, but our local structure might validly be just class folders.
# We will use validation_split=0.2 to create a validation set automatically.

print("Setting up Data Generators...")
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    fill_mode='nearest',
    validation_split=0.2
)

print("Loading Training Set...")
training_set = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(224, 224),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

print("Loading Validation Set...")
validation_set = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(224, 224),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=True
)

print(f"Starting training for {EPOCHS} epochs...")
history = model.fit(
  training_set,
  validation_data=validation_set,
  epochs=EPOCHS,
  steps_per_epoch=len(training_set),
  validation_steps=len(validation_set)
)

# Plotting
try:
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='train loss')
    plt.plot(history.history['val_loss'], label='val loss')
    plt.legend()
    plt.title('Loss')

    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='train acc')
    plt.plot(history.history['val_accuracy'], label='val acc')
    plt.legend()
    plt.title('Accuracy')
    
    plot_path = os.path.join(MODELS_DIR, 'maize_training_plot.png')
    plt.savefig(plot_path)
    print(f"Training plot saved to {plot_path}")
except Exception as e:
    print(f"Error plotting: {e}")

# Save Model
model_name = 'maize_disease_model.h5'
model_path = os.path.join(MODELS_DIR, model_name)
model.save(model_path)
print(f"Model saved to {model_path}")
