from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
from werkzeug.utils import secure_filename
import os
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing import image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Load pre-trained MobileNetV2 model
model = MobileNetV2(weights="imagenet")

# Function to classify fruit type using MobileNetV2
def classify_fruit(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    
    predictions = model.predict(img_array)
    decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=1)[0]
    label = decoded_predictions[0][1]
    
    return label

# Function to classify ripeness using K-Means Clustering
def classify_ripeness(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = image.reshape((-1, 3))
    pixels = np.float32(pixels)

    k = 5  # Number of clusters
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    dominant_color = centers[np.argmax(np.bincount(labels.flatten()))]
    
    ripeness = "Unknown"
    if dominant_color[0] > 200 and dominant_color[1] > 100:
        ripeness = "Ripe"
    elif dominant_color[1] > 150 and dominant_color[2] > 150:
        ripeness = "Unripe"
    else:
        ripeness = "Overripe"
    
    return ripeness

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    fruit_type = classify_fruit(filepath)
    ripeness_result = classify_ripeness(filepath)
    
    return jsonify({"fruit": fruit_type, "ripeness": ripeness_result, "image_url": filepath})

if __name__ == '__main__':
    app.run(debug=True)
