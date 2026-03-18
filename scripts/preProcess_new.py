import os
import cv2
import numpy as np
import pytesseract
import yaml
from pathlib import Path
from deskew import determine_skew
from skimage.filters import threshold_sauvola
from pdf2image import convert_from_path
from docx import Document

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = REPO_ROOT / "data" / "raw" / "initial_data"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "interim" / "preprocessed_frames"
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "config.yaml"


def load_config(config_path: Path):
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def configure_tesseract(cfg: dict):
    tesseract_exe = cfg.get("system", {}).get("tesseract_exe", "")
    if tesseract_exe:
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe

def rescale_image(image, max_size=1000):
    h, w = image.shape[:2]
    scale = max_size / max(h, w) if max(h, w) > max_size else 1
    return cv2.resize(image, (int(w * scale), int(h * scale)))

def deskew_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    angle = determine_skew(gray)
    if angle is not None and abs(angle) > 0.5:
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(image, matrix, (w, h),
                               flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return image

def apply_sauvola_threshold(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    window_size = 25
    thresh_sauvola = threshold_sauvola(gray, window_size=window_size)
    binary = (gray > thresh_sauvola).astype(np.uint8) * 255
    return binary

def preprocess_image(image):
    image = rescale_image(image)
    image = deskew_image(image)
    image = apply_sauvola_threshold(image)
    return image

def ocr_image_to_text(image):
    # Use --psm 1 for automatic page segmentation (layout model)
    config = r'--oem 3 --psm 1'
    text = pytesseract.image_to_string(image, config=config)
    return text

def save_text_to_txt(text, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

def save_text_to_docx(text, filename):
    doc = Document()
    for line in text.split('\n'):
        doc.add_paragraph(line)
    doc.save(filename)

def process_pdf(pdf_path, output_base, cfg):
    poppler_bin = cfg.get("system", {}).get("poppler_bin", "")
    kwargs = {"dpi": 300}
    if poppler_bin:
        kwargs["poppler_path"] = poppler_bin
    pages = convert_from_path(pdf_path, **kwargs)
    full_text = ""
    for i, page in enumerate(pages):
        image = np.array(page)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        processed = preprocess_image(image)
        text = ocr_image_to_text(processed)
        full_text += text + "\n\n"
    save_text_to_txt(full_text, output_base + '.txt')
    save_text_to_docx(full_text, output_base + '.docx')

def process_images_and_pdfs(input_dir: Path, output_dir: Path, cfg: dict):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        file_name, ext = os.path.splitext(filename)
        ext = ext.lower()
        if ext == '.pdf':
            process_pdf(file_path, os.path.join(output_dir, file_name), cfg)
            print(f"OCR'd PDF: {filename}")
        elif ext in ('.png', '.jpg', '.jpeg', '.tiff', '.bmp'):
            image = cv2.imread(file_path)
            if image is None:
                print(f"Failed to load {filename}")
                continue
            processed = preprocess_image(image)
            text = ocr_image_to_text(processed)
            save_text_to_txt(text, os.path.join(output_dir, file_name + '.txt'))
            save_text_to_docx(text, os.path.join(output_dir, file_name + '.docx'))
            print(f"OCR'd Image: {filename}")
        else:
            print(f"Unsupported file: {filename}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Preprocess and OCR raw handwritten files")
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR), help="Input folder")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output folder")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to YAML config")
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    configure_tesseract(cfg)
    process_images_and_pdfs(Path(args.input_dir), Path(args.output_dir), cfg)
