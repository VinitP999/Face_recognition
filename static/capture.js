document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("captureButton").addEventListener("click", function () {
        const name = prompt("Enter patient name:");
        const age = prompt("Enter patient age:");
        const gender = prompt("Enter patient gender:");

        if (!name || !age || !gender) {
            alert("Please enter all details!");
            return;
        }

        fetch("/capture", {  // ✅ FIXED: `/capture_face` → `/capture`
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, age, gender })
        })
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error("Error capturing face:", error));
    });

    document.getElementById("trainModelButton").addEventListener("click", function () {
        fetch("/train_model", { method: "POST" })
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error("Error training model:", error));
    });

    document.getElementById("recognizeButton").addEventListener("click", function () {
        fetch("/recognize_face", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.name) {
                alert(`Recognized: ${data.name}, Age: ${data.age}, Condition: ${data.condition}`);
            } else {
                alert("No match found!");
            }
        })
        .catch(error => console.error("Error recognizing face:", error));
    });
});
