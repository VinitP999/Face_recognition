import cv2
import numpy as np
import pickle
import os

def recognize():
    model_path = "models/trained_model.yml"
    labels_path = "models/labels.pkl"

    if not os.path.exists(model_path) or not os.path.exists(labels_path):
        return None  # No trained model found

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_path)

    with open(labels_path, "rb") as f:
        label_dict = pickle.load(f)

    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)

    recognized_patient = None
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y + h, x:x + w]
            label, confidence = recognizer.predict(face)

            if confidence < 100:  # Adjust threshold if needed
                recognized_patient = {"name": label_dict[label], "confidence": confidence}
                cap.release()
                cv2.destroyAllWindows()
                return recognized_patient

        cv2.imshow("Recognizing Face", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return recognized_patient
