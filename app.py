import os
from flask import Flask, request, jsonify, render_template
from inference_sdk import InferenceHTTPClient

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="DEbxWv4B4sXByBVSaiaN"
)
MODEL_ID = "apple-ripeness-pj4d3/3"

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

    # Ambil nilai confidence dari query string, default ke 0.5
    confidence = float(request.args.get("confidence", 0.5))

    # Panggil Roboflow API menggunakan SDK
    result = CLIENT.infer(filepath, model_id=MODEL_ID, confidence=confidence)

    ripeness_translation = {
        "100%_ripeness": "Tingkat Kematangan 100%",
        "75%_ripeness": "Tingkat Kematangan 75%",
        "50%_ripeness": "Tingkat Kematangan 50%",
        "20%_ripeness": "Apel Masih Mentah",
        "rotten_apple": "Apel Busuk"
    }

    if "predictions" in result and len(result["predictions"]) > 0:
        prediction = result["predictions"][0]
        ripeness_en = prediction.get("class", "Tidak Diketahui")
        ripeness = ripeness_translation.get(ripeness_en, "Tidak Diketahui")
    else:
        ripeness = "Tidak Diketahui"

    return jsonify({"ripeness": ripeness, "image_url": filepath})

if __name__ == "__main__":
    app.run(debug=True)
