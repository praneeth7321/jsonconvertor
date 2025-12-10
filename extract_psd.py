import os
import json
from psd_tools import PSDImage

def extract_psd_layers(psd_path, output_path):
    psd = PSDImage.open(psd_path)
    extracted_data = {
        "name": os.path.basename(psd_path).replace('.psd', ''),
        "layers": []
    }

    for layer in psd:
        if layer.is_visible():
            layer_data = {
                "name": layer.name,
                "x": layer.bbox[0],
                "y": layer.bbox[1],
                "width": layer.bbox[2] - layer.bbox[0],
                "height": layer.bbox[3] - layer.bbox[1],
            }
            if layer.kind == "type":
                text_data = layer.text
                layer_data.update({
                    "type": "text",
                    "font": text_data.fontset[0].name if text_data.fontset else "Unknown",
                    "justification": text_data.justification if hasattr(text_data, "justification") else "left",
                    "color": f"#{text_data.engine_dict['StyleRun']['RunArray'][0]['FillColor'][1]:06X}" if "StyleRun" in text_data.engine_dict else "#000000",
                    "size": text_data.sizes[0] if text_data.sizes else 24,
                    "text": text_data.text.strip() if text_data.text else "",
                })
            else:
                layer_data["type"] = "image"

            extracted_data["layers"].append(layer_data)

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_data, json_file, indent=4)
