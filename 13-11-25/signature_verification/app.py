from flask import Flask, render_template, request, jsonify
import cv2, numpy as np, base64

app = Flask(__name__)

def ssim(img1, img2):
    """Compute Structural Similarity Index"""
    from skimage.metrics import structural_similarity as compare_ssim
    grayA = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    score, _ = compare_ssim(grayA, grayB, full=True)
    return score

@app.route('/')
def index():
    return render_template('signature.html')

@app.route('/verify-signature', methods=['POST'])
def verify_signature():
    data = request.json
    image_data = data['image']
    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    test_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    known_img = cv2.imread('known_signature.jpg')

    # resize both to same scale
    test_img = cv2.resize(test_img, (300, 150))
    known_img = cv2.resize(known_img, (300, 150))

    score = ssim(known_img, test_img)
    threshold = 0.7  # tweak this value (0.7–0.9 typical)

    if score > threshold:
        return jsonify({"match": True, "score": round(float(score), 3)})
    else:
        return jsonify({"match": False, "score": round(float(score), 3)})

if __name__ == '__main__':
    app.run(debug=True)
