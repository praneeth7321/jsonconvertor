import os
import json
from flask import Flask, render_template, request, redirect, url_for, send_file
from psd_tools import PSDImage

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to clean text (remove \r and extra quotes)
def clean_text(text):
    if text:
        return text.replace('\r', '').strip("'")
    return text

# Function to extract PSD layers
def extract_psd_layers(psd_path):
    psd = PSDImage.open(psd_path)
    layers_data = []

    for layer in psd.descendants():
        if layer.kind == 'type':  # Text Layer
            text_data = layer.engine_dict
            text_content = str(text_data.get("Editor", {}).get("Text", ""))
            text_content = clean_text(text_content)  # Clean text

            font_info = text_data.get("FontSet", [{}])[0]
            font_name = font_info.get("Name", "Unknown")
            font_size = int(text_data.get("FontSize", [48])[0])
            justification = str(text_data.get("Justification", ["center"])[0])

            color_data = text_data.get("FillColor", {}).get("Values", [0, 0, 0])
            if isinstance(color_data[0], float):
                color_code = "0x{:02X}{:02X}{:02X}".format(
                    int(color_data[0] * 255),
                    int(color_data[1] * 255),
                    int(color_data[2] * 255),
                )
            else:
                color_code = "0x{:02X}{:02X}{:02X}".format(
                    int(color_data[0]),
                    int(color_data[1]),
                    int(color_data[2]),
                )

            layers_data.append({
                "type": "text",
                "font": font_name,
                "justification": justification,
                "color": color_code,
                "size": font_size,
                "name": layer.name,
                "x": int(layer.bbox[0]),
                "y": int(layer.bbox[1]),
                "width": int(layer.bbox[2] - layer.bbox[0]),
                "height": int(layer.bbox[3] - layer.bbox[1]),
                "text": text_content  # Cleaned text
            })

        elif layer.kind == 'pixel':  # Image Layer
            layers_data.append({
                "type": "image",
                "name": layer.name,
                "x": int(layer.bbox[0]),
                "y": int(layer.bbox[1]),
                "width": int(layer.bbox[2] - layer.bbox[0]),
                "height": int(layer.bbox[3] - layer.bbox[1]),
                "src": f"../skins/{os.path.splitext(os.path.basename(psd_path))[0]}/{layer.name}.png"
            })

    return {
        "name": os.path.splitext(os.path.basename(psd_path))[0],
        "path": f"{os.path.splitext(os.path.basename(psd_path))[0]}/",
        "info": {
            "description": "Normal",
            "file": os.path.basename(psd_path),
            "date": "Uncalibrated",
            "title": "",
            "author": "",
            "keywords": "",
            "generator": "Team_Growwth"
        },
        "layers": layers_data
    }

@app.route('/')
def upload_page():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_psd():
    if 'psd_file' not in request.files:
        return "No file uploaded", 400

    psd_file = request.files['psd_file']
    if psd_file.filename == '':
        return "No selected file", 400

    file_path = os.path.join(UPLOAD_FOLDER, psd_file.filename)
    psd_file.save(file_path)

    json_data = extract_psd_layers(file_path)

    json_path = os.path.join(UPLOAD_FOLDER, 'extracted.json')
    with open(json_path, 'w', encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

    return redirect(url_for('editor_page'))

@app.route('/editor')
def editor_page():
    json_path = os.path.join(UPLOAD_FOLDER, 'extracted.json')
    if not os.path.exists(json_path):
        return "No extracted JSON found", 404

    with open(json_path, 'r', encoding="utf-8") as f:
        json_data = json.load(f)

    return render_template('editor.html', json_data=json_data)

@app.route('/save_json', methods=['POST'])
def save_json():
    json_path = os.path.join(UPLOAD_FOLDER, 'extracted.json')

    new_data = request.json
    with open(json_path, 'w', encoding="utf-8") as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)

    return {"status": "success", "message": "Changes saved successfully!"}

@app.route('/download_json')
def download_json():
    json_path = os.path.join(UPLOAD_FOLDER, 'extracted.json')
    if not os.path.exists(json_path):
        return "No JSON available to download", 404
    return send_file(json_path, as_attachment=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)