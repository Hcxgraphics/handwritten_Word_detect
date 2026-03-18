# import cv2
# import os
# import numpy as np
# import pytesseract
# from skimage.filters import threshold_sauvola
# from deskew import determine_skew
# from skimage.transform import rotate


# # Define input and output directories
# input_folder = r"C:\Users\harshada\OneDrive\Desktop\Dunzo\PersonalTesting\data\Initial_data"
# output_folder = r"C:\Users\harshada\OneDrive\Desktop\Dunzo\PersonalTesting\data\PreProcessed_Frames"

# # Ensure output directory exists
# os.makedirs(output_folder, exist_ok=True)

# # Rescaling dimensions (Modify if needed)
# IMG_WIDTH = 600
# IMG_HEIGHT = 800


# def rescale_image(image):
#     """ Resize the image to a fixed size """
#     return cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT), interpolation=cv2.INTER_AREA)


# def preprocess_for_tesseract(image):
#     """ Enhance image for OCR """
#     # Convert to grayscale
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#     # Apply Sauvola thresholding
#     window_size = 25
#     thresh_sauvola = threshold_sauvola(gray, window_size=window_size)
#     binary_sauvola = (gray > thresh_sauvola).astype("uint8") * 255

#     # Resize to improve OCR accuracy (Tesseract prefers 300 DPI equivalent size)
#     h, w = binary_sauvola.shape
#     scale_factor = max(1.5, 1000 / max(h, w))  # Ensure minimum reasonable size
#     resized = cv2.resize(binary_sauvola, (int(w * scale_factor), int(h * scale_factor)))

#     return resized

# def correct_orientation(image):
#     """ Detects and corrects the orientation of the image using Tesseract OCR """
#     preprocessed = preprocess_for_tesseract(image)

#     try:
#         osd = pytesseract.image_to_osd(preprocessed)
#         angle = int(osd.split("\n")[1].split(":")[-1].strip())  # Extract rotation angle

#         if angle == 90:
#             image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
#         elif angle == 180:
#             image = cv2.rotate(image, cv2.ROTATE_180)
#         elif angle == 270:
#             image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

#     except pytesseract.TesseractError as e:
#         print("Tesseract failed to process image:", str(e))

#     return image

# def correct_orientation(image):
#     """ Detects and corrects the orientation of the image using Tesseract OCR """
#     osd = pytesseract.image_to_osd(image)
#     angle = int(osd.split("\n")[1].split(":")[-1].strip())  # Extract rotation angle

#     if angle == 90:
#         image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
#     elif angle == 180:
#         image = cv2.rotate(image, cv2.ROTATE_180)
#     elif angle == 270:
#         image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

#     return image

# def deskew_image(image):
#     """ Fixes skew after correcting the orientation """
#     image = correct_orientation(image)  # Fix 90° or 180° rotations first

#     angle = determine_skew(image)
#     print(f"Deskew angle: {angle}")  # Debugging
#     if angle:
#         image = rotate(image, angle, cval=255)  # Rotate and fill background with white
#     return image



# def apply_sauvola_threshold(image):
#     """ Apply Sauvola thresholding """
#     window_size = 25  # Window of 25 pixels
#     thresh_sauvola = threshold_sauvola(image, window_size=window_size)
#     binary_sauvola = image > thresh_sauvola
#     return (binary_sauvola * 255).astype(np.uint8)  # Convert boolean to uint8 format


# def preprocess_and_save():
#     """ Process all images from the input folder and save them to the output folder """
#     for filename in os.listdir(input_folder):
#         file_path = os.path.join(input_folder, filename)
#         print(f"Processing file: {filename}")

#         # Read the image in grayscale
#         image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

#         if image is None:
#             print(f"Skipping {filename}: Unable to read")
#             continue

#         # Apply preprocessing steps
#         image = rescale_image(image)
#         image = deskew_image(image)
#         image = apply_sauvola_threshold(image)

#         # Save processed image
#         output_path = os.path.join(output_folder, filename)
#         cv2.imwrite(output_path, image)
#         print(f"Processed and saved: {output_path}")


# if __name__ == "__main__":
#     preprocess_and_save()




import os
import cv2
import numpy as np
import pytesseract
from deskew import determine_skew
from skimage.filters import threshold_sauvola

# Set Tesseract OCR path (Change if installed elsewhere)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Input and Output Directories
INPUT_DIR = r"C:\Users\harshada\OneDrive\Desktop\Dunzo\PersonalTesting\data\Initial_data"
OUTPUT_DIR = r"C:\Users\harshada\OneDrive\Desktop\Dunzo\PersonalTesting\data\PreProcessed_Frames"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def rescale_image(image, max_size=1000):
    """Rescale image while maintaining aspect ratio."""
    h, w = image.shape[:2]
    scale_factor = max_size / max(h, w) if max(h, w) > max_size else 1
    return cv2.resize(image, (int(w * scale_factor), int(h * scale_factor)))

# def correct_orientation(image):
#     """Corrects image orientation using Tesseract OCR."""
#     try:
#         # Convert to grayscale for better OCR
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#         # Resize for better OCR accuracy
#         resized = rescale_image(gray, 1000)

#         # Use Tesseract to detect orientation
#         osd = pytesseract.image_to_osd(resized)
#         angle = int(osd.split("\n")[1].split(":")[-1].strip())

#         # Rotate based on detected angle
#         if angle == 90:
#             image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
#         elif angle == 180:
#             image = cv2.rotate(image, cv2.ROTATE_180)
#         elif angle == 270:
#             image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

#     except pytesseract.TesseractError:
#         print("Tesseract failed to detect orientation. Skipping correction.")

#     return image

def deskew_image(image):
    """Correct skew using the deskew library."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    angle = determine_skew(gray)

    if angle is not None and abs(angle) > 0.5:  # Ignore minor skews
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    return image

def apply_sauvola_threshold(image):
    """Applies Sauvola thresholding for bin"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    window_size = 25
    thresh_sauvola = threshold_sauvola(gray, window_size=window_size)
    binary_sauvola = (gray > thresh_sauvola).astype("uint8") * 255
    return binary_sauvola

def preprocess_and_save():
    """Processes images and saves the preprocessed versions."""
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            file_path = os.path.join(INPUT_DIR, filename)
            print(f"Processing file: {filename}")

            # Read Image
            image = cv2.imread(file_path)

            if image is None:
                print(f"Failed to load {filename}. Skipping...")
                continue

            # # Step 1: Correct Orientation
            # image = correct_orientation(image)

            # Step 2: Deskew Image
            image = deskew_image(image)

            # Step 3: Apply Sauvola Thresholding
            image = apply_sauvola_threshold(image)

            # Save Processed Image
            output_path = os.path.join(OUTPUT_DIR, filename)
            cv2.imwrite(output_path, image)
            print(f"Saved preprocessed image: {output_path}")

if __name__ == "__main__":
    preprocess_and_save()
