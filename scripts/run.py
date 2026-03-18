from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
	sys.path.insert(0, str(SRC_DIR))

from handwriting_grading.main import process_file


def main():
	import argparse

	parser = argparse.ArgumentParser(description="Run OCR pipeline for a PDF/image input")
	parser.add_argument("input", help="Path to PDF or image")
	parser.add_argument("-o", "--output", default="output.docx", help="Output DOCX path")
	parser.add_argument(
		"-c",
		"--config",
		default=str(REPO_ROOT / "configs" / "config.yaml"),
		help="Path to YAML config",
	)
	args = parser.parse_args()

	process_file(Path(args.input), Path(args.output), Path(args.config))


if __name__ == "__main__":
	main()
