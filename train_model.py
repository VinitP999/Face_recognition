import cv2
import numpy as np
import os

# Define the path to the dataset
dataset_path = r"D:\vinit\Test 2\dataset"

# Path to the Haar cascade classifier file
haar_cascade_path = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")

# Check if dataset folder exists
if not os.path.exists(dataset_path):
    print(f"Error: Dataset folder not found at {dataset_path}")
    exit()

# Load the Haar cascade classifier
face_cascade = cv2.CascadeClassifier(haar_cascade_path)

if face_cascade.empty():
    print(f"Error loading Haar cascade file. Check path: {haar_cascade_path}")
    exit()

# Initialize LBPH face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

faces, ids = [], []

# Iterate through all images in the dataset
for file in os.listdir(dataset_path):
    if file.endswith(".jpg"):
        image_path = os.path.join(dataset_path, file)
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        # Extract user ID from filename (assumes format user_<id>_<count>.jpg)
        user_id = int(file.split("_")[1])
        faces.append(img)
        ids.append(user_id)

# Check if any face data is available
if len(faces) == 0:
    print("No training data found. Add face images first.")
    exit()

# Train the recognizer using face images and their corresponding IDs
ids = np.array(ids)
recognizer.train(faces, ids)

# Save the trained model to file
model_path = os.path.join(os.path.dirname(__file__), "trained_model.yml")
recognizer.save(model_path)

print("\nModel trained and saved successfully.")
