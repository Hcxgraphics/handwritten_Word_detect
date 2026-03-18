import cv2
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "config.yaml"

cfg = {}
BASE_OCR_CONFIG = "--oem 3 --psm 1 -c preserve_interword_spaces=1"


def configure_ocr(config: dict | None = None, config_path: Path = DEFAULT_CONFIG_PATH):
    global cfg, BASE_OCR_CONFIG

    if config is None:
        cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    else:
        cfg = config

    tesseract_exe = cfg.get("system", {}).get("tesseract_exe", "")
    if tesseract_exe:
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe

    psm = cfg.get("ocr", {}).get("psm", 1)
    preserve_spaces = cfg.get("ocr", {}).get("preserve_spaces", 1)
    BASE_OCR_CONFIG = f"--oem 3 --psm {psm} -c preserve_interword_spaces={preserve_spaces}"


configure_ocr()

def image_to_text(img_bgr) -> str:
    lang = cfg.get("ocr", {}).get("lang", "eng")
    return pytesseract.image_to_string(img_bgr, lang=lang, config=BASE_OCR_CONFIG)

def image_to_hocr(img_bgr) -> BeautifulSoup:
    lang = cfg.get("ocr", {}).get("lang", "eng")
    bin_pdf = pytesseract.image_to_pdf_or_hocr(
        Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)),
        extension="hocr",
        lang=lang,
        config=BASE_OCR_CONFIG)
    return BeautifulSoup(bin_pdf, "html.parser")
