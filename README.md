# Handwriting Detection For Automated Assignment Grading

End to end OCR focused pipeline for extracting text from handwritten assignment pages and preparing it for automated grading workflows.

The project currently combines:
- Image/PDF preprocessing (deskew + adaptive thresholding)
- Optional line segmentation for page content
- OCR extraction with Tesseract
- Layout-aware block detection hooks (via LayoutParser/Detectron2 config)
- Export of recognized text into `.txt` and `.docx`

## Repository Structure

```text
handwritten_Word_detect/
	assets/
		plots/                       # Evaluation charts (accuracy/confusion matrix)
	configs/
		config.yaml                  # Main runtime configuration
		config_Table.yaml            # Layout model configuration
	data/
		raw/
			initial_data/              # Raw input files (PDF/images)
			paperDataset.zip
		interim/
			preprocessed_frames/       # Preprocessed outputs (txt/docx/images)
			segments/                  # Line-segmented crops
		testing/
			page_dataset/
			words_dataset/
			Page_dataset.zip
			Words_dataset.zip
	docs/
		architecture/                # System architecture and workflow diagrams
	notebooks/
		iam_Trocr.ipynb
		ocr_model_testing_TrOcr.ipynb
	scripts/
		run.py                       # Main OCR entrypoint for single file
		preProcess_new.py            # Batch preprocessing + OCR utility
		preProces_olds.py            # Legacy preprocessing script
		segment_lines.py             # Line segmentation utility
		env_setup.ps1                # Environment setup helper
	src/
		handwriting_grading/
			__init__.py
			main.py                    # OCR pipeline orchestration
			layout.py                  # Layout detector wrapper
			ocr.py                     # OCR helpers/config
			preprocess.py              # Reusable preprocessing ops
			postprocess.py             # Postprocessing helpers
			writer.py                  # DOCX writer
	requirements.txt
```

## Workflow

1. Input assignment page (`.pdf` or image) is loaded.
2. Optional preprocessing improves readability for OCR.
3. Layout detector identifies text/table blocks.
4. OCR extracts text block by block.
5. Output is written to `DOCX` (and optional plain text in helper scripts).
6. Extracted text can be sent to downstream grading/scoring modules.

## Setup

### 1. Create a Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure external tools

Update `configs/config.yaml`:
- `system.tesseract_exe`: absolute path to `tesseract.exe` (or leave blank if on PATH)
- `system.poppler_bin`: Poppler `bin` path for PDF conversion (or leave blank if available)
- `layout.model_config`: points to `configs/config_Table.yaml` by default

## Usage

### Run the main OCR pipeline

```powershell
python scripts/run.py <input-file> -o <output-docx>
```

Example:

```powershell
python scripts/run.py data/raw/initial_data/chem.pdf -o data/interim/preprocessed_frames/chem.docx
```

### Batch preprocess + OCR all files in a folder

```powershell
python scripts/preProcess_new.py --input-dir data/raw/initial_data --output-dir data/interim/preprocessed_frames
```

### Segment lines from preprocessed page images

```powershell
python scripts/segment_lines.py --input-dir data/interim/preprocessed_frames --output-dir data/interim/segments
```

## Notes

- `scripts/preProces_olds.py` is kept for reproducibility of earlier experiments.
- The current pipeline is OCR-centric and can be integrated with plagiarism detection, semantic matching, and rubric-based grading services.

## Future Extensions

- Add a dedicated `tests/` package with unit/integration tests.
- Package `src/handwriting_grading` as an installable module (`pyproject.toml`).
- Add a grading module that scores extracted responses against answer keys.