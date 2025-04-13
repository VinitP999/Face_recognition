const video = document.getElementById('video');
const captureBtn = document.getElementById('capture');
const message = document.getElementById('message');

// Start the webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Error accessing webcam: ", err);
    });

// Capture and send image to backend
captureBtn.addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append("image", blob);

        fetch('/login', { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    message.textContent = `Access Granted: ${data.name}`;
                    message.style.color = "green";
                } else {
                    message.textContent = "Access Denied";
                    message.style.color = "red";
                }
            })
            .catch(error => console.error('Error:', error));
    }, 'image/jpeg');
});
