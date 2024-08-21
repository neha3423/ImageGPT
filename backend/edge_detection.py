import cv2
import numpy as np
from PIL import Image

class CannyEdgeDetection:
    def __init__(self):
        print("Initializing Canny Edge Detection")
        self.low_threshold = 100
        self.high_threshold = 200

    def predict(self, input_image_path, output_image_path):
        original_image = Image.open(input_image_path)
        grayscale_image = original_image.convert("L")
        grayscale_np = np.array(grayscale_image)
        edges = cv2.Canny(grayscale_np, self.low_threshold, self.high_threshold)
        edges_overlay = np.zeros_like(grayscale_np)
        edges_overlay[edges != 0] = 255  
        cv2.imwrite(output_image_path, edges_overlay)
        print(f"Processed Image, Input Image: {input_image_path}, Output Image: {output_image_path}")
        return output_image_path
