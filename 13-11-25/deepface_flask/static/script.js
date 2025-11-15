const video = document.getElementById("video");
const resultText = document.getElementById("result");

navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => video.srcObject = stream)
  .catch(err => console.error("Camera Error:", err));

document.getElementById("capture").addEventListener("click", async () => {
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  const imageData = canvas.toDataURL("image/jpeg");

  resultText.innerText = "Verifying...";

  try {
    const response = await axios.post("/verify", { image: imageData });
    const data = response.data;

    if (data.match) {
      resultText.innerText = `✅ Access Granted (distance: ${data.distance.toFixed(3)})`;
      resultText.style.color = "green";
    } else if (data.match === false) {
      resultText.innerText = `❌ Access Denied (distance: ${data.distance.toFixed(3)})`;
      resultText.style.color = "red";
    } else {
      resultText.innerText = "Error: " + data.error;
      resultText.style.color = "orange";
    }
  } catch (error) {
    console.error(error);
    resultText.innerText = "Server Error";
    resultText.style.color = "orange";
  }
});