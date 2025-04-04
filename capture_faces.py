import cv2
import os

# Capture function
def capture(patient_name):
    dataset_path = f"dataset/{patient_name}"
    os.makedirs(dataset_path, exist_ok=True)  # ✅ Ensure folder exists

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("❌ ERROR: Camera not detected.")
        return False

    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    count = 0

    print(f"📷 Capturing images for {patient_name}... Press 'q' to stop.")

    while count < 20:  # ✅ Capture 20 images
        success, frame = camera.read()
        if not success:
            print("⚠️ ERROR: Failed to capture frame.")
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            file_path = f"{dataset_path}/{patient_name}_{count}.jpg"
            cv2.imwrite(file_path, face)  # ✅ Save face image
            count += 1

        cv2.imshow("Face Capture", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    print(f"✅ {count} images saved for {patient_name}.")
    return True
