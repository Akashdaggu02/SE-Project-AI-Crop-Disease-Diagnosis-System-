import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import matplotlib.pyplot as plt

# Define Constants
IMAGE_SIZE = (256, 256)
BATCH_SIZE = 32
EPOCHS = 10
DATASET_DIR = os.path.join('dataset', 'Grape')
MODELS_DIR = 'models'

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

print(f"Checking dataset at {DATASET_DIR}...")
train_dir = os.path.join(DATASET_DIR, 'train')
test_dir = os.path.join(DATASET_DIR, 'test')

if not os.path.exists(train_dir):
    print(f"Error: Train directory not found in {DATASET_DIR}")
    exit(1)

# Using ImageDataGenerator to load images (as Grayscale to match user's custom model input of (256,256,1))
print("Setting up Data Generators (Grayscale)...")
train_datagen = ImageDataGenerator(
    rescale=1./255,
    # Add simple augmentations if needed, user code had none in the final block but had shuffle
    validation_split=0.15 
)

# Note: User's provided code had manual loading and relied on 'test' folder for testing, 
# but also used validation_split in fit().
# We will use the 'train' folder for training and validation split, and 'test' for independent evaluation if it exists.

print("Loading Training Data...")
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    color_mode='grayscale', # User model expects 1 channel
    class_mode='categorical',
    subset='training',
    shuffle=True
)

print("Loading Validation Data...")
validation_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    color_mode='grayscale',
    class_mode='categorical',
    subset='validation',
    shuffle=True
)

num_classes = train_generator.num_classes
print(f"Number of classes: {num_classes}")
print(f"Class indices: {train_generator.class_indices}")

# Build Model (User's Custom Architecture)
print("Building Custom CNN Model...")
model = Sequential()

# model.add(layers.Conv2D(32,(3,3),padding='same',input_shape=(256,256,3),activation='relu')) in snippet 1
# BUT snippet 2 (final one) has input_shape=(256,256,1)
model.add(layers.Conv2D(32, (3,3), padding='same', input_shape=(256, 256, 1), activation='relu'))
model.add(layers.Conv2D(64, (3,3), activation='relu')) # User code had 64 here in 2nd snippet

model.add(layers.MaxPool2D(pool_size=(8,8)))

model.add(layers.Conv2D(32, (3,3), padding='same', activation='relu'))
model.add(layers.Conv2D(64, (3,3), activation='relu'))

model.add(layers.MaxPool2D(pool_size=(8,8)))

model.add(Activation('relu'))

model.add(layers.Flatten())
model.add(layers.Dense(256, activation='relu'))
model.add(layers.Dense(num_classes, activation='softmax'))

model.summary()

# Compile
# User used 'rmsprop'
model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

print(f"Starting training for {EPOCHS} epochs...")
history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=validation_generator,
    verbose=1
)

# Save Model
model_name = 'grape_disease_model.h5'
model_path = os.path.join(MODELS_DIR, model_name)
model.save(model_path)
print(f"Model saved to {model_path}")

# Evaluation on Test Data if available
if os.path.exists(test_dir):
    print("Evaluating on Test Data...")
    test_datagen = ImageDataGenerator(rescale=1./255)
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        color_mode='grayscale',
        class_mode='categorical',
        shuffle=False
    )
    scores = model.evaluate(test_generator)
    print(f"Test Accuracy: {scores[1]*100:.2f}%")

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
    
    plot_path = os.path.join(MODELS_DIR, 'grape_training_plot.png')
    plt.savefig(plot_path)
    print(f"Training plot saved to {plot_path}")
except Exception as e:
    print(f"Error plotting: {e}")
