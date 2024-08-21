from flask import Flask, request, jsonify,send_file
import os
import logging
from flask_cors import CORS,cross_origin
import preprocess_backend
from werkzeug.utils import secure_filename
from mimetypes import guess_type
import base64
from io import BytesIO
from image_captioning import ImageCaptioning
from edge_detection import CannyEdgeDetection
from object_detection import YOLODetection
from scene_classification import ResNetAID
import torch
from PIL import Image
import cv2
import io
from datetime import datetime
import shutil



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
os.makedirs('uploads', exist_ok=True)
os.makedirs('processed_frames', exist_ok=True)
logging.basicConfig(level=logging.INFO)
basedir = os.path.abspath(os.path.dirname(__file__))
device = 'cuda' if torch.cuda.is_available() else 'cpu'

def delete_files_in_directory(directory_path):
   try:
     files = os.listdir(directory_path)
     for file in files:
       file_path = os.path.join(directory_path, file)
       if os.path.isfile(file_path):
         os.remove(file_path)
     print("All files deleted successfully.")
   except OSError:
     print("Error occurred while deleting files.")

@app.route('/preprocess_backend', methods=['POST'])
@cross_origin()
def preprocess_image():
    delete_files_in_directory('uploads')
    delete_files_in_directory('processed_frames')
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected image"}), 400

    # Ensure the filename is secure
    filename = secure_filename(image.filename)
    upload_folder = os.path.join(basedir, 'uploads')

    # Create the uploads folder iit doesn't exist
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    input_image_path = os.path.join(upload_folder, filename)
    print(input_image_path)
    # Save the image to the specified path
    with open(input_image_path, 'wb') as f:
        f.write(image.read())   

    try:
        

        # output_image_path = os.path.join('processed_frames', f'processed_{image.filename}')
        processed_image_path = preprocess_backend.process_images('uploads', 'processed_frames')
    except ValueError as e:
        logging.error(f"Processing error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    if not os.path.exists(input_image_path):
        return jsonify({"error": "Image not found"}), 404
    
    mimetype, _ = guess_type(processed_image_path)
    return send_file(processed_image_path, mimetype=mimetype)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
image_captioning_object = ImageCaptioning(device)

@app.route('/image_captioning', methods=['POST'])
@cross_origin()
def image_captioning():
#     if request.method == 'OPTIONS':
#         logging.info("Handling preflight request for /blip")
#         return jsonify({'status': 'OK'}), 200
    
    logging.info("Received request for image captioning")
    data = request.get_json()

    if 'image' not in data:
        logging.error("No image part in the request")
        return jsonify({"error": "No image part"}), 400
    else:
        logging.info(data)
        logging.info(" image part in the request")

    image = data['image'][0] #here , iam considering only single image case 
    
    # if image.filename == '':
    #     logging.error("No selected image in the request")
    #     return jsonify({"error": "No selected image"}), 400
    # print(image)
    # logging.info(image)
    inline_data = image['inlineData']
    img_data = inline_data['data']
    mime_type = inline_data['mimeType']

    # Decode base64 string to image
    img_bytes = base64.b64decode(img_data)
    img = Image.open(BytesIO(img_bytes))
    # img.save(img_filename, 'JPEG')
    # logging.info(f"Saved image {img_filename}")
    upload_folder = os.path.join(basedir, 'uploads')
    img_filename = 'image.jpg'
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    input_image_path = os.path.join(upload_folder, img_filename)
    img.save(input_image_path)
    logging.info('Image saved')
    

    try:
        caption = image_captioning_object.inference(input_image_path)
        
    except Exception as e:
        logging.error(f"Error in image captioning: {e}")
        return jsonify({"error": "An error occurred during image captioning"}), 500

    logging.info(f"Image captioning successful: {caption}")
    #return caption
    return jsonify({"caption": caption})


@app.route('/scene_classification', methods=['POST'])
@cross_origin()
def classify_scene():
    scene_classification_object = ResNetAID(device)
#     if request.method == 'OPTIONS':
#         logging.info("Handling preflight request for /blip")
#         return jsonify({'status': 'OK'}), 200
    
    logging.info("Received request for Scene Classification")
    data = request.get_json()

    if 'image' not in data:
        logging.error("No image part in the request")
        return jsonify({"error": "No image part"}), 400
    else:
        logging.info(data)
        logging.info("Image part in the request")

    image = data['image'][0] #here , iam considering only single image case 
    
    # if image.filename == '':
    #     logging.error("No selected image in the request")
    #     return jsonify({"error": "No selected image"}), 400
    # print(image)
    # logging.info(image)
    inline_data = image['inlineData']
    img_data = inline_data['data']
    mime_type = inline_data['mimeType']

    # Decode base64 string to image
    img_bytes = base64.b64decode(img_data)
    img = Image.open(BytesIO(img_bytes))
    # img.save(img_filename, 'JPEG')
    # logging.info(f"Saved image {img_filename}")
    upload_folder = os.path.join(basedir, 'uploads')
    img_filename = 'image.jpg'
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    input_image_path = os.path.join(upload_folder, img_filename)
    img.save(input_image_path)
    logging.info('Image saved')

    try:
        output_text = scene_classification_object.predict(input_image_path)
        
    except Exception as e:
        logging.error(f"Error in image captioning: {e}")
        return jsonify({"error": "An error occurred during scene classification"}), 500

    logging.info(f"Scene Classification successful: {output_text}")
    #return caption
    return jsonify({"output_text": output_text})

# Initialize CannyEdgeDetection
canny_detector = CannyEdgeDetection()
@app.route('/edge_detection', methods=['POST'])
@cross_origin()
def detect_edges():
    logging.info("Received request for edge detection")
    data = request.get_json()

    
    if 'image' not in data:
        return jsonify({'error': 'No file part in the request'}), 400
    
    
    image = data['image'][0] #here , iam considering only single image case 
    
    
    inline_data = image['inlineData']
    img_data = inline_data['data']
    mime_type = inline_data['mimeType']

    img_bytes = base64.b64decode(img_data)
    img = Image.open(BytesIO(img_bytes))
    # img.save(img_filename, 'JPEG')
    # logging.info(f"Saved image {img_filename}")
    upload_folder = os.path.join(basedir, 'uploads')
    output_folder = os.path.join(basedir,'processed_images')
    shutil.rmtree(upload_folder)

    os.makedirs('uploads', exist_ok=True)

    # delete_files_in_directory(output_folder)
    img_filename = 'edge_image.jpg'
    now = datetime.now()

# Format the timestamp
    timestamp = now.strftime('%Y%m%d_%H%M%S')

    # Add the timestamp to the filename
    base, extension = img_filename.rsplit('.', 1)
    img_filename = f"{base}_{timestamp}.{extension}"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    input_image_path = os.path.join(upload_folder, img_filename)
    img.save(input_image_path)
    logging.info('Image saved')

    try:
        
        # Specify output image path
        now = datetime.now()

        # Format the timestamp
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        img_filename = "processed.jpg"
        # Add the timestamp to the filename
        base, extension = img_filename.rsplit('.', 1)
        output_image_name = f"{base}_{timestamp}.{extension}"
        output_image_path = os.path.join(basedir, 'processed_images', output_image_name)
        
            # Perform edge detection
        processed_image_path = canny_detector.predict(input_image_path, output_image_path)
    except Exception as e:
        logging.error(f"Error in edge detection: {e}")
        return jsonify({"error": "An error occurred during edge detection"}), 500
    logging.info(f"Edge Detection successful")

    # Return the processed image as a response
    return send_file(output_image_path, mimetype='image/jpeg')

detector = YOLODetection(device)
@app.route('/object_detection', methods=['POST'])
@cross_origin()
def detect_object():
    logging.info("Received request for object detection")
    data = request.get_json()

    
    if 'image' not in data:
        return jsonify({'error': 'No file part in the request'}), 400
    
    
    image = data['image'][0] #here , iam considering only single image case 
    
    
    inline_data = image['inlineData']
    img_data = inline_data['data']
    mime_type = inline_data['mimeType']

    img_bytes = base64.b64decode(img_data)
    img = Image.open(BytesIO(img_bytes))
    # img.save(img_filename, 'JPEG')
    # logging.info(f"Saved image {img_filename}")
    upload_folder = os.path.join(basedir, 'uploads')
    output_folder = os.path.join(basedir,'processed_images')
    shutil.rmtree(upload_folder)

    os.makedirs('uploads', exist_ok=True)

    # delete_files_in_directory(output_folder)
    img_filename = 'object_image.jpg'
    now = datetime.now()

# Format the timestamp
    timestamp = now.strftime('%Y%m%d_%H%M%S')

    # Add the timestamp to the filename
    base, extension = img_filename.rsplit('.', 1)
    img_filename = f"{base}_{timestamp}.{extension}"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    input_image_path = os.path.join(upload_folder, img_filename)
    img.save(input_image_path)
    logging.info('Image saved')

    try:
        
        # Specify output image path
        now = datetime.now()

        # Format the timestamp
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        img_filename = "processed.jpg"
        # Add the timestamp to the filename
        base, extension = img_filename.rsplit('.', 1)
        output_image_name = f"{base}_{timestamp}.{extension}"
        output_image_path = os.path.join(basedir, 'processed_images', output_image_name)
        
        # Initialize YOLODetector
        

        # Perform object detection
        processed_image_path = detector.predict(input_image_path, output_image_path)
    except Exception as e:
        logging.error(f"Error in object detection: {e}")
        return jsonify({"error": "An error occurred during object detection"}), 500
    logging.info(f"Object Detection successful")

    # Return the processed image as a response
    return send_file(output_image_path, mimetype='image/jpeg')

# @app.route('/object_detection', methods=['POST'])
# @cross_origin()
# def object_detection():
#     if 'image' not in request.files:
#         return jsonify({'error': 'No file part in the request'}), 400
    
#     file = request.files['image']

#     if file.filename == '':
#         return jsonify({"error": "No selected image"}), 400
    
#     # Save the uploaded image to disk
#     filename = secure_filename(file.filename)
#     upload_folder = os.path.join(app.root_path, 'uploads')

#     if not os.path.exists(upload_folder):
#         os.makedirs(upload_folder)

#     input_image_path = os.path.join(upload_folder, filename)
#     file.save(input_image_path)

#     try:
#         # Specify output image path
#         output_image_path = os.path.join(app.root_path, 'processed_images', f'processed_{filename}')
        
#         # Example: Path to your YOLO weights
#         device = 'cuda' if torch.cuda.is_available() else 'cpu'

#         # Initialize YOLODetector
#         detector = YOLODetection(device)

#         # Perform object detection
#         processed_image_path = detector.predict(input_image_path, output_image_path)
#     except Exception as e:
#         return jsonify({"error": f"An error occurred during object detection: {str(e)}"}), 500

#     # Return the processed image as a response
#     return send_file(processed_image_path, mimetype='image/jpeg',as_attachment=True)

# scene_classification = ResNetAID(device)
# @app.route('/scene_classification', methods=['POST'])
# @cross_origin()
# def classify_scene():
#     logging.info("Received request for Scene Classification")

#     if 'image' not in request.files:
#         logging.error("No image part in the request")
#         return jsonify({"error": "No image part"}), 400

#     image = request.files['image']
#     if image.filename == '':
#         logging.error("No selected image in the request")
#         return jsonify({"error": "No selected image"}), 400

#     filename = secure_filename(image.filename)
#     upload_folder = os.path.join(basedir, 'uploads')

#     if not os.path.exists(upload_folder):
#         os.makedirs(upload_folder)

#     input_image_path = os.path.join(upload_folder, filename)
#     image.save(input_image_path)
    

#     try:
#         output_text = scene_classification.predict(input_image_path)
        
#     except Exception as e:
#         logging.error(f"Error in image captioning: {e}")
#         return jsonify({"error": "An error occurred during image captioning"}), 500

#     logging.info(f"Image captioning successful: {output_text}")
#     #return caption
#     return jsonify({"Scene": output_text})




@app.route("/")
def hello():
    return "hello"

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False)