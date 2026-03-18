from pathlib import Path
from typing import Any, Dict

import cv2
import numpy as np
import yaml
from pdf2image import convert_from_path
from tqdm import tqdm

from . import layout, ocr, writer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "config.yaml"


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def _load_pages(in_path: Path, cfg: Dict[str, Any]):
    if in_path.suffix.lower() == ".pdf":
        poppler_bin = cfg.get("system", {}).get("poppler_bin", "")
        kwargs = {"dpi": 300}
        if poppler_bin:
            kwargs["poppler_path"] = poppler_bin
        return convert_from_path(str(in_path), **kwargs)

    image = cv2.imread(str(in_path))
    if image is None:
        raise ValueError(f"Cannot read input file: {in_path}")
    return [image]


def process_file(in_path: Path, out_path: Path, config_path: Path = DEFAULT_CONFIG_PATH):
    cfg = load_config(config_path)
    ocr.configure_ocr(cfg)

    pages = _load_pages(in_path, cfg)
    detector = layout.LayoutDetector(cfg)
    text_blocks = []

    for pg in tqdm(pages, desc="Pages"):
        img_rgb = np.array(pg) if not isinstance(pg, np.ndarray) else cv2.cvtColor(pg, cv2.COLOR_BGR2RGB)
        for block in detector.detect_blocks(img_rgb):
            x1, y1, x2, y2 = map(int, block.coordinates)
            crop = img_rgb[y1:y2, x1:x2, :]
            txt = ocr.image_to_text(crop)
            text_blocks.append(("table" if block.type == "Table" else "text", txt))

    writer.write_docx(text_blocks, out_path)
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="PDF or image path")
    ap.add_argument("-o", "--output", default="output.docx")
    ap.add_argument("-c", "--config", default=str(DEFAULT_CONFIG_PATH), help="Path to YAML config")
    args = ap.parse_args()
    process_file(Path(args.input), Path(args.output), Path(args.config))
