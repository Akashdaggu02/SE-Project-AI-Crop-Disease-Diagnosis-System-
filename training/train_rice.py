import tensorflow as tf
import os
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print(f"TensorFlow Version: {tf.__version__}")

# Constants
BATCH_SIZE = 32
EPOCHS = 30
IMAGE_SIZE = (299, 299) # InceptionV3 uses 299x299

DATASET_DIR = os.path.join('dataset', 'rice')
MODELS_DIR = 'models'

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

print(f"Checking dataset at {DATASET_DIR}...")
train_dir = os.path.join(DATASET_DIR, 'train')
val_dir = os.path.join(DATASET_DIR, 'val')

if not os.path.exists(train_dir) or not os.path.exists(val_dir):
    print(f"Error: Train/Val directories not found in {DATASET_DIR}")
    exit(1)

# Data Generators
print("Setting up Data Generators...")
train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    horizontal_flip=True,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    fill_mode='nearest'
)

val_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

print("Loading Training Data...")
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

print("Loading Validation Data...")
validation_generator = val_datagen.flow_from_directory(
    val_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

num_classes = train_generator.num_classes
print(f"Number of classes: {num_classes}")
print(f"Class indices: {train_generator.class_indices}")

# Model Building
print("Building model with InceptionV3 (Keras Applications)...")
base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=IMAGE_SIZE+(3,))

# Freeze the base model
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.2)(x)
predictions = Dense(num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

model.summary()

model.compile(
   optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), 
   loss='categorical_crossentropy',
   metrics=['accuracy'])

print(f"Starting training for {EPOCHS} epochs...")
history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // train_generator.batch_size,
        epochs=EPOCHS,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // validation_generator.batch_size,
        verbose=1
)

# Save Model
model_name = 'rice_disease_model.h5'
model_path = os.path.join(MODELS_DIR, model_name)
model.save(model_path)
print(f"Model saved to {model_path}")

# Plotting
try:
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    epochs_range = range(len(acc))

    plt.figure(figsize=(8, 8))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    
    plot_path = os.path.join(MODELS_DIR, 'rice_training_plot.png')
    plt.savefig(plot_path)
    print(f"Training plot saved to {plot_path}")
except Exception as e:
    print(f"Error plotting: {e}")
