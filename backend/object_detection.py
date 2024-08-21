import torch
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

class YOLODetection:
    def __init__(self,device='cpu'):
        self.device = device
        self.weights_path = r'./checkpoints/best.pt'
        self.model = YOLO(self.weights_path).to(device)

    def predict(self, image_path, output_path):
        # Perform prediction
        results = self.model(image_path)

        # Process results to draw bounding boxes and labels on image
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        
        # Optional: Load a font
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except IOError:
            font = ImageFont.load_default()

        for pred in results[0].boxes:
            # Extract coordinates
            x1, y1, x2, y2 = pred.xyxy[0].tolist()
            # Draw bounding box
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
            # Example of accessing class index and confidence score
            class_index = int(pred.cls)
            confidence_score = float(pred.conf)
            label = f"{self.model.names[class_index]} {confidence_score:.2f}"
            print(f"Predicted Class Index: {class_index}, Confidence Score: {confidence_score}")
            # Add label and confidence score
            #label = f"{self.model.names[int(pred.cls)]} {float(pred.conf):.2f}"
            text_bbox = draw.textbbox((x1, y1), label, font=font)
            text_background = [text_bbox[0], text_bbox[1], text_bbox[2], text_bbox[3]]
            draw.rectangle(text_background, fill="red")
            draw.text((x1, y1), label, fill="white", font=font)

        #return image
        output_path=image.save(output_path)
        return output_path
