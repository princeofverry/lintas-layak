from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageDraw
import io
import logging
from ultralytics import YOLO

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load YOLOv8 model
model = YOLO('api/ultralytics/best.pt')

# Define class names
CLASS_NAMES = {0: 'pothole'}


@app.route('/detect', methods=['POST'])
def detect():
    logging.debug("Request method: %s", request.method)
    if 'image' not in request.files:
        logging.error("No image provided in the request")
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']
    logging.debug("File received: %s", file.filename)
    img = Image.open(io.BytesIO(file.read()))

    # Perform detection
    results = model(img)

    # Draw detections on the image
    draw = ImageDraw.Draw(img)
    detections = []
    for result in results:
        logging.debug("Result: %s", result)
        for box in result.boxes:
            logging.debug("Box: %s", box)
            class_id = int(box.cls[0].item())
            detection = {
                "xmin": box.xyxy[0][0].item(),
                "ymin": box.xyxy[0][1].item(),
                "xmax": box.xyxy[0][2].item(),
                "ymax": box.xyxy[0][3].item(),
                "confidence": box.conf[0].item(),
                "class": class_id,
                "name": CLASS_NAMES.get(class_id, "unknown")
            }
            detections.append(detection)
            # Draw rectangle
            draw.rectangle([detection['xmin'], detection['ymin'],
                           detection['xmax'], detection['ymax']], outline="blue", width=2)
            # Draw label
            draw.text((detection['xmin'], detection['ymin']),
                      f"{detection['name']} {detection['confidence']:.2f}", fill="red")

    logging.debug("Detections: %s", detections)

    # Save the image with annotations to a bytes buffer
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return jsonify({
        "detections": detections,
        "num_potholes": len(detections),
        "image": img_bytes.getvalue().hex()
    })


if __name__ == '__main__':
    app.run(debug=True)
