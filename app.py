from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import cv2
import os
import database
import capture_faces
import train_model
import recognize
import traceback
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Route for login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "admin123":
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# Admin Dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")
@app.route("/capture", methods=["POST"])
def capture():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        if request.is_json:
            data = request.get_json()
        else:
            return jsonify({"error": "❌ Invalid JSON format!"}), 400

        print("🔹 Received JSON Data:", data)

        if not data:
            return jsonify({"error": "❌ No JSON data received!"}), 400

        patient_name = data.get("name", "").strip()
        patient_age = data.get("age", "").strip()
        patient_condition = data.get("condition", "").strip()

        if not patient_name or not patient_age or not patient_condition:
            return jsonify({"error": "⚠️ Missing required fields (name, age, condition)!"}), 400

        # ✅ Save patient info in the database
        database.save_patient(patient_name, patient_age, patient_condition)

        # ✅ Capture and store face images in dataset
        saved = capture_faces.capture(patient_name)

        if saved:
            return jsonify({"message": f"✅ Face for {patient_name} captured successfully!"})
        else:
            return jsonify({"error": "❌ Failed to capture face! Please check the camera."}), 500

    except Exception as e:
        print(f"⚠️ ERROR in capture(): {traceback.format_exc()}")
        return jsonify({"error": "❌ Face capture failed due to an internal error!"}), 500
    
    
# Train Model
@app.route("/train_model", methods=["POST"])
def train():
    try:
        if not os.path.exists("dataset") or not os.listdir("dataset"):
            return jsonify({"error": "No dataset found! Add images before training."}), 400

        success = train_model.train()
        if success:
            return jsonify({"message": "✅ Model training completed successfully!"})
        else:
            return jsonify({"error": "Training failed! No valid images found."}), 400

    except Exception as e:
        print(f"⚠️ ERROR in train_model(): {traceback.format_exc()}")
        return jsonify({"error": f"Training failed due to error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
