import cv2
import numpy as np
import os

dataset_path = r"D:\vinit\Test 2\dataset"

haar_cascade_path = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")

if not os.path.exists(dataset_path):
    print(f"Error: Dataset folder not found at {dataset_path}")
    exit()  

face_cascade = cv2.CascadeClassifier(haar_cascade_path)

if face_cascade.empty():
    print(f"Error loading Haar cascade file. Check path: {haar_cascade_path}")
    exit()

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces, ids = [], []

for file in os.listdir(dataset_path):
    if file.endswith(".jpg"):  
        image_path = os.path.join(dataset_path, file)
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE) 

        user_id = int(file.split("_")[1]) 
        faces.append(img)  
        ids.append(user_id)  

# Check if face is collected
if len(faces) == 0:
    print("No training data found. Add face images first.")
    exit()  

# Convert ids to a numpy array
ids = np.array(ids)

recognizer.train(faces, ids)

model_path = os.path.join(os.path.dirname(__file__), "trained_model.yml")
recognizer.save(model_path)

print("\nModel trained and saved successfully.")
