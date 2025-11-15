from flask import Flask, render_template, request, jsonify
import numpy as np
import base64
import cv2
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from numpy.linalg import norm

app = Flask(__name__)

# Load pretrained CNN (VGG16) and extract feature layer
base_model = VGG16(weights='imagenet', include_top=True)
model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

# Helper: compute image embedding
def get_embedding(img_array):
    img_array = cv2.resize(img_array, (224, 224))
    img_array = image.img_to_array(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    embedding = model.predict(img_array)
    return embedding[0]

# Load and encode reference signature
KNOWN_SIGNATURE_PATH = "known_signature.jpg"
ref_img = cv2.imread(KNOWN_SIGNATURE_PATH)
ref_embedding = get_embedding(ref_img)
print("Reference signature embedding ready.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    image_data = data['image']
    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    try:
        # Get embedding of captured signature
        capture_embedding = get_embedding(frame)

        # Compute cosine similarity
        cosine_similarity = np.dot(ref_embedding, capture_embedding) / (norm(ref_embedding) * norm(capture_embedding))
        print("Similarity:", cosine_similarity)

        # Threshold (tune between 0.7 and 0.9)
        if cosine_similarity > 0.61:
            result = {"verified": True, "similarity": float(cosine_similarity)}
        else:
            result = {"verified": False, "similarity": float(cosine_similarity)}

    except Exception as e:
        result = {"error": str(e)}

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)