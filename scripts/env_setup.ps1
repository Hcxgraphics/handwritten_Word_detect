# env_setup.ps1
# ---------------------------------------------------------------------------
# Installs PyTorch 2.4.1 (CUDA 12.1), Detectron2 pre-built wheel, and all libs
# ---------------------------------------------------------------------------

Write-Host "Upgrading pip/setuptools…" -ForegroundColor Cyan
pip install --upgrade pip setuptools wheel ninja

Write-Host "Installing PyTorch 2.4.1 (+cu121)…" -ForegroundColor Cyan
pip install torch torchvision torchaudio `
    --index-url https://download.pytorch.org/whl/cu121     # <-- cu121 wheel[6]

Write-Host "Installing Detectron2 wheel (commit 2a420ed)…" -ForegroundColor Cyan
pip install --extra-index-url https://miropsota.github.io/torch_packages_builder `
    detectron2==0.6+2a420edpt2.4.1cu121                   # pre-built GPU wheel[11]

Write-Host "Installing core Python libraries…" -ForegroundColor Cyan
pip install layoutparser==0.3.2 opencv-python pytesseract pillow numpy `
           scikit-image pdf2image deskew beautifulsoup4 python-docx tqdm pyyaml

Write-Host "DONE environment ready!"
