import os
from flask import Flask, request, jsonify, render_template
from inference_sdk import InferenceHTTPClient

app = Flask(__name__)

# Inisialisasi Roboflow Client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="DEbxWv4B4sXByBVSaiaN"  # Gantilah dengan API Key-mu sendiri
)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"})
    
    # Simpan file yang diunggah
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Kirim gambar ke Roboflow untuk analisis
    model_id = "fruit-ripeness-ffuvb/1"
    result = CLIENT.infer(filepath, model_id=model_id)

    # Ambil hasil klasifikasi
    if "predictions" in result and len(result["predictions"]) > 0:
        prediction = result["predictions"][0]
        ripeness = prediction.get("class", "Unknown")  # Nama tingkat kematangan buah
    else:
        ripeness = "Unknown"

    # Kirim respons ke frontend
    return jsonify({"ripeness": ripeness, "image_url": filepath})

if __name__ == "__main__":
    app.run(debug=True)
