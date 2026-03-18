# pipeline/preprocess.py
from pathlib import Path
import cv2, numpy as np
from deskew import determine_skew
from skimage.filters import threshold_sauvola

MAX_SIZE = 1800  # px – high DPI for OCR

def rescale(img, max_size=MAX_SIZE):
    h, w = img.shape[:2]
    sf = max_size / max(h, w) if max(h, w) > max_size else 1.0
    return cv2.resize(img, (int(w*sf), int(h*sf)), interpolation=cv2.INTER_AREA)

def deskew(img):
    angle = determine_skew(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    if angle and abs(angle) > 0.5:
        h, w = img.shape[:2]
        M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h),
                             flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REPLICATE)
    return img

def sauvola(img, window=25):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = threshold_sauvola(gray, window_size=window)
    return ((gray > thresh)*255).astype("uint8")

def preprocess(img_path: Path):
    img = cv2.imread(str(img_path))
    if img is None:
        raise ValueError(f"Cannot read {img_path}")
    img = rescale(img)
    img = deskew(img)
    bin_img = sauvola(img)
    return img, bin_img
