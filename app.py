from flask import Flask, render_template, Response, request, redirect, url_for, session, jsonify
import cv2
import os
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

model_path = "trained_model.yml"
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Load recognizer
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
if os.path.exists(model_path):
    face_recognizer.read(model_path)

# Load users from file
users = {}
if os.path.exists("users.txt"):
    with open("users.txt", "r") as file:
        for line in file:
            data = line.strip().split(",")
            if len(data) >= 5:
                uid, name, age, gender = data[0], data[1], data[2], data[3]
                history = data[4]
                recognized_at = data[5] if len(data) > 5 else ""
                users[int(uid)] = {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "history": history,
                    "recognized_at": recognized_at
                }

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/login', methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == "admin" and password == "admin":
        session['admin'] = True
        return redirect('/dashboard')
    return render_template("login.html", error="Invalid credentials")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect('/')
    return render_template("dashboard.html")

@app.route('/capture', methods=["GET", "POST"])
def capture():
    if 'admin' not in session:
        return redirect('/')
    if request.method == "POST":
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        history = request.form['history']
        user_id = max(users.keys(), default=0) + 1

        cam = cv2.VideoCapture(0)
        count = 0
        os.makedirs("dataset", exist_ok=True)

        while True:
            ret, frame = cam.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                count += 1
                face = gray[y:y+h, x:x+w]
                cv2.imwrite(f"dataset/user_{user_id}_{count}.jpg", face)
            if count >= 20:
                break

        cam.release()
        cv2.destroyAllWindows()

        users[user_id] = {
            "name": name,
            "age": age,
            "gender": gender,
            "history": history,
            "recognized_at": ""
        }

        with open("users.txt", "w") as file:
            for uid, u in users.items():
                file.write(f"{uid},{u['name']},{u['age']},{u['gender']},{u['history']},{u.get('recognized_at', '')}\n")

        # Retrain model
        faces, ids = [], []
        for file in os.listdir("dataset"):
            if file.endswith(".jpg"):
                uid = int(file.split("_")[1])
                gray = cv2.imread(os.path.join("dataset", file), cv2.IMREAD_GRAYSCALE)
                faces.append(gray)
                ids.append(uid)

        if faces:
            face_recognizer.train(faces, np.array(ids))
            face_recognizer.save(model_path)

        return redirect('/dashboard')
    return render_template("capture.html")

@app.route('/recognize')
def recognize():
    if 'admin' not in session:
        return redirect('/')
    return render_template("recognize.html")

@app.route('/recognize-face')
def recognize_face_route():
    cam = cv2.VideoCapture(0)
    recognized_user_id = None

    while True:
        success, frame = cam.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            label, confidence = face_recognizer.predict(face)
            if confidence < 60 and label in users:
                recognized_user_id = label
                break

        if recognized_user_id:
            break

    cam.release()
    cv2.destroyAllWindows()

    user_data = None
    if recognized_user_id:
        user_data = users[recognized_user_id].copy()
        recognized_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_data["recognized_at"] = recognized_time
        users[recognized_user_id]["recognized_at"] = recognized_time

        with open("users.txt", "w") as file:
            for uid, u in users.items():
                file.write(f"{uid},{u['name']},{u['age']},{u['gender']},{u['history']},{u.get('recognized_at', '')}\n")

    return render_template("recognize.html", user=user_data)

@app.route('/video')
def video():
    if 'admin' not in session:
        return redirect('/')

    def generate():
        cam = cv2.VideoCapture(0)
        while True:
            success, frame = cam.read()
            if not success:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                label, confidence = face_recognizer.predict(face)
                if confidence < 60 and label in users:
                    name = users[label]['name']
                    cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        cam.release()

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/database')
def database():
    if 'admin' not in session:
        return redirect('/')
    all_users = []
    for uid, info in users.items():
        user = info.copy()
        user['id'] = uid
        all_users.append(user)
    return render_template("database.html", users=all_users)

@app.route('/edit/<int:user_id>', methods=["GET", "POST"])
def edit_user(user_id):
    if 'admin' not in session:
        return redirect('/')
    user = users.get(user_id)
    if not user:
        return redirect('/database')

    if request.method == "POST":
        users[user_id].update({
            "name": request.form["name"],
            "age": request.form["age"],
            "gender": request.form["gender"],
            "history": request.form["history"]
        })

        with open("users.txt", "w") as f:
            for uid, u in users.items():
                f.write(f"{uid},{u['name']},{u['age']},{u['gender']},{u['history']},{u.get('recognized_at', '')}\n")

        return redirect("/database")

    return render_template("edit_user.html", user=user)

@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    if 'admin' not in session:
        return redirect('/')

    if user_id in users:
        del users[user_id]

        with open("users.txt", "w") as f:
            for uid, u in users.items():
                f.write(f"{uid},{u['name']},{u['age']},{u['gender']},{u['history']},{u.get('recognized_at', '')}\n")

        for file in os.listdir("dataset"):
            if file.startswith(f"user_{user_id}_") and file.endswith(".jpg"):
                os.remove(os.path.join("dataset", file))

        # Retrain model
        faces, ids = [], []
        for file in os.listdir("dataset"):
            if file.endswith(".jpg"):
                uid = int(file.split("_")[1])
                gray = cv2.imread(os.path.join("dataset", file), cv2.IMREAD_GRAYSCALE)
                faces.append(gray)
                ids.append(uid)

        if faces:
            face_recognizer.train(faces, np.array(ids))
            face_recognizer.save(model_path)

    return redirect("/database")

if __name__ == "__main__":
    app.run(debug=True)
