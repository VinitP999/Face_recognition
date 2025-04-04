import os
import cv2
import numpy as np
import pickle

def train():
    dataset_path = "dataset"
    model_path = "models/trained_model.yml"
    labels_path = "models/labels.pkl"

    if not os.path.exists(dataset_path) or not os.listdir(dataset_path):
        print("⚠️ No dataset found for training!")
        return False

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    images, labels = [], []
    label_dict = {}
    current_id = 0

    for person_name in os.listdir(dataset_path):
        person_folder = os.path.join(dataset_path, person_name)
        if not os.path.isdir(person_folder):
            continue

        for image_file in os.listdir(person_folder):
            image_path = os.path.join(person_folder, image_file)
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

            if image is None:
                print(f"❌ ERROR: Could not read {image_path}")
                continue

            faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)
            if len(faces) == 0:
                print(f"⚠️ WARNING: No face detected in {image_path}")
                continue

            for (x, y, w, h) in faces:
                face_resized = cv2.resize(image[y:y+h, x:x+w], (100, 100))
                images.append(face_resized)
                labels.append(current_id)

        if len(images) == 0:
            print(f"⚠️ No valid images found for {person_name}, skipping.")
            continue

        label_dict[current_id] = person_name
        current_id += 1

    if len(images) == 0:
        print("⚠️ No valid faces detected! Training aborted.")
        return False

    images = np.array(images, dtype="uint8")
    labels = np.array(labels, dtype="int32")

    recognizer.train(images, labels)
    recognizer.save(model_path)

    with open(labels_path, "wb") as f:
        pickle.dump(label_dict, f)

    print("✅ Model training completed successfully!")
    return True

if __name__ == "__main__":
    train()
