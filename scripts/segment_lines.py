import os
import cv2
import pytesseract
import numpy as np
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = REPO_ROOT / "data" / "interim" / "preprocessed_frames"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "interim" / "segments"
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "config.yaml"


def load_config(config_path: Path):
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def configure_tesseract(cfg: dict):
    tesseract_exe = cfg.get("system", {}).get("tesseract_exe", "")
    if tesseract_exe:
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe

def refine_segmentation(image):
    """Applies preprocessing to improve text line detection."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive thresholding to enhance contrast
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # Use dilation to connect text components
    kernel = np.ones((3, 30), np.uint8)  # Adjust kernel for better line detection
    dilated = cv2.dilate(binary, kernel, iterations=1)

    return dilated

def segment_lines(image_path, output_folder):
    """Segments lines from an image using contours and Tesseract."""
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error loading image: {image_path}")
        return

    refined = refine_segmentation(image)

    # Find contours
    contours, _ = cv2.findContours(refined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours top-to-bottom
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    for idx, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        
        # Ignore small noise
        if h < 20 or w < 50:
            continue
        
        segment = image[y:y+h, x:x+w]
        segment_path = os.path.join(output_folder, f"segment_{idx}.png")
        cv2.imwrite(segment_path, segment)
        print(f"Segment saved: {segment_path}")

def process_all_images(input_dir: Path, output_dir: Path):
    """Processes all images in the input directory."""
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_dir, filename)
            image_output_folder = os.path.join(output_dir, os.path.splitext(filename)[0])
            os.makedirs(image_output_folder, exist_ok=True)

            print(f"Processing: {filename}")
            segment_lines(image_path, image_output_folder)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Segment preprocessed page images into line crops")
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR), help="Input folder")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output folder")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to YAML config")
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    configure_tesseract(cfg)
    process_all_images(Path(args.input_dir), Path(args.output_dir))
