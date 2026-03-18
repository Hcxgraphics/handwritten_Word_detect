# pipeline/postprocess.py
from bs4 import BeautifulSoup
from typing import List, Tuple

def _xy_from_bbox(bbox_str: str) -> Tuple[int, int, int, int]:
    # bbox "x1 y1 x2 y2"
    return tuple(map(int, bbox_str.split()[1:5]))

def extract_sub_super(hocr: BeautifulSoup) -> List[Tuple[str, str]]:
    """
    Return list of (word, position) where position ∈ {'sub','super','normal'}
    Heuristic: baseline attr + font size diff as in research notes[10][18].
    """
    words = []
    for span in hocr.find_all("span", class_="ocrx_word"):
        title = span.get("title", "")
        if "bbox" not in title:
            continue
        baseline = [s for s in title.split(";") if "baseline" in s]
        x_size = [s for s in title.split(";") if "x_size" in s]
        word = span.get_text()
        # Simple baseline threshold
        pos = "normal"
        if baseline:
            base_val = float(baseline[0].split()[1])
            pos = "super" if base_val < -1.0 else ("sub" if base_val > 1.0 else "normal")
        words.append((word, pos))
    return words
