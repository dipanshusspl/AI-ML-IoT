const video = document.getElementById("video");
const statusText = document.getElementById("status");

navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
    statusText.innerText = "Camera Ready. Please blink!";
  })
  .catch(err => {
    console.error("Camera Error:", err);
    statusText.innerText = "Cannot access camera.";
  });

// Send frame every 1.5 seconds
setInterval(async () => {
  if (!video.srcObject) return;

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  const imageData = canvas.toDataURL("image/jpeg");

  try {
    const response = await axios.post("/verify", { image: imageData });
    const data = response.data;

    if (data.status === "blink") {
      statusText.innerText = "✅ Blink detected — Face is LIVE!";
      statusText.style.color = "green";
    } else if (data.status === "open") {
      statusText.innerText = "🙂 Eyes open — waiting for blink...";
      statusText.style.color = "blue";
    } else {
      statusText.innerText = "No face detected.";
      statusText.style.color = "red";
    }
  } catch (error) {
    console.error(error);
    statusText.innerText = "Server Error.";
  }
}, 1500);
