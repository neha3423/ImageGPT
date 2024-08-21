import cv2
import numpy as np
import os
from flask_cors import CORS

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

def process_images(input_dir, output_dir):
    print(input_dir, output_dir)
    # Parameters for resizing
    resize_width = 800
    resize_height = 600

    os.makedirs(output_dir, exist_ok=True)
    # delete_files_in_directory(output_dir)

    # Get a list of image file names in the input directory
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff','.webp']
    file_names = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    image_files = [f for f in file_names if any(f.lower().endswith(ext) for ext in image_extensions)]
    print("file names , image extensions",file_names,image_files)
    # Function to process and save images
    def process_and_save_image(image, output_path, resize_width, resize_height):
        # Resize the image
        resized_image = cv2.resize(image, (resize_width, resize_height))
        
        # Normalize the pixel values to the range [0, 1]
        normalized_image = resized_image / 255.0
        
        # Convert the normalized image back to the range [0, 255] and ensure it's in uint8 format
        processed_image = (normalized_image * 255).astype(np.uint8)
        
        # Save the processed image in JPEG format
        cv2.imwrite(output_path, processed_image)

    # Process image files
    for idx, image_file in enumerate(image_files):
        input_image_path = os.path.join(input_dir, image_file)
        
        # Load the image
        image = cv2.imread(input_image_path)
        
        if image is None:
            print(f"Error loading image {input_image_path}")
            continue
        
        output_image_path = os.path.join(output_dir, f'frame_{idx:04d}.jpg')
        process_and_save_image(image, output_image_path, resize_width, resize_height)
        print(f"Processed image saved as {output_image_path}")
        return output_image_path

# input_dir="test_images"
# output_dir="processen_frames"
# process_images(input_dir, output_dir)
