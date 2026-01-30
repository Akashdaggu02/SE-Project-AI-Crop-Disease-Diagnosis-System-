import tensorflow as tf
from tensorflow.keras.applications.resnet_v2 import ResNet152V2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
import os
import matplotlib.pyplot as plt
import numpy as np

# Define Constants
IMAGE_SIZE = (300, 300) # User snippet used (img_h, img_w) variables but defined 300
BATCH_SIZE = 32
EPOCHS = 20
DATASET_DIR = os.path.join('dataset', 'cotton')
MODELS_DIR = 'models'

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

print(f"Checking dataset at {DATASET_DIR}...")
train_dir = os.path.join(DATASET_DIR, 'train')
val_dir = os.path.join(DATASET_DIR, 'val')

if not os.path.exists(train_dir) or not os.path.exists(val_dir):
    print(f"Error: Train/Val directories not found in {DATASET_DIR}")
    exit(1)

# Data Augmentation & Loading
print("Setting up Data Generators...")
datagen = ImageDataGenerator(
    rescale = 1./255,
    horizontal_flip = True,
    vertical_flip = True,
    # validation_split = 0.2 # User snippet used validation_split on a single dir, 
                             # but here we have separate 'train' and 'val' dirs usually?
                             # Let's check. list_dir showed 'train' and 'val' folders.
                             # User snippet flow_from_directory used '/content/drive/My Drive/data/train' for training
                             # and '/content/drive/My Drive/data/val' for validation.
                             # So I should simply use flow_from_directory on train_dir and val_dir directly 
                             # without 'subset' if they are separate folders.
                             # However, user snippet used 'subset' arguments. 
                             # "train = datagen.flow_from_directory(..., subset='training')"
                             # "valid = datagen.flow_from_directory(..., subset='validation')"
                             # BUT they pointed to DIFFERENT directories in the snippet: 'data/train' and 'data/val'.
                             # That is contradictory usage of ImageDataGenerator if they are separate folders. 
                             # Usually validation_split is used when you have ONE folder.
                             # If I have split folders, I don't need validation_split in ImageDataGenerator 
                             # UNLESS I want to further split train?
                             # I will assume standard structure: train_dir is for training, val_dir is for validation.
                             # I will remove 'subset' and 'validation_split' to be safe and standard.
)


print("Loading Training Data...")
train_generator = datagen.flow_from_directory(
    train_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    seed=88
)

print("Loading Validation Data...")
val_generator = datagen.flow_from_directory(
    val_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    seed=88
)

num_classes = train_generator.num_classes
print(f"Number of classes: {num_classes}")
print(f"Class indices: {train_generator.class_indices}")

# Model Building (ResNet152V2)
print("Building ResNet152V2 Model...")
in_layer = layers.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3))
resnet = ResNet152V2(include_top=False, weights='imagenet', input_tensor=in_layer)

# Freeze layers
for layer in resnet.layers:
    layer.trainable = False

# Custom Head
# User snippet had bug: "inter = tf.keras.layers.GlobalMaxPooling2D()(xception.output)"
# Fixed to use resnet.output
x = layers.GlobalMaxPooling2D()(resnet.output)
x = layers.Flatten()(x)
# User had Dense(4), we use Dense(num_classes)
output = layers.Dense(num_classes, activation='softmax')(x)

model = models.Model(inputs=resnet.inputs, outputs=output)

# LR Scheduler
initial_lr = 0.01
lr_scheduler = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_lr,
    decay_steps=25,
    decay_rate=0.96,
    staircase=True
)

# Optimizer
optim = tf.keras.optimizers.Adam(learning_rate=lr_scheduler)

model.compile(optimizer=optim, loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# Callbacks
callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max', patience=10, verbose=1),
    tf.keras.callbacks.ModelCheckpoint(
        os.path.join(MODELS_DIR, 'cotton_best_model.h5'), 
        monitor='val_accuracy', 
        mode='max', 
        save_weights_only=False, # Saving full model is usually better/easier for loading later
        save_best_only=True,
        verbose=1
    )
]

print(f"Starting training for {EPOCHS} epochs...")
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    verbose=1
)

# Save Final Model
model_name = 'cotton_disease_model.h5'
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

    plt.figure(figsize=(12, 7))
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
    
    plot_path = os.path.join(MODELS_DIR, 'cotton_training_plot.png')
    plt.savefig(plot_path)
    print(f"Training plot saved to {plot_path}")
except Exception as e:
    print(f"Error plotting: {e}")
