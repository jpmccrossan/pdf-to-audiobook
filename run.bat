@echo off
rem Quick start for Windows.
rem   run.bat                 -> opens the desktop app
rem   run.bat book.pdf [...]  -> converts from the command line (see --help)
rem First run creates a virtual environment and installs dependencies.
setlocal
cd /d "%~dp0"

if "%VENV_DIR%"=="" set "VENV_DIR=venv"
if "%TORCH_INDEX_URL%"=="" set "TORCH_INDEX_URL=https://download.pytorch.org/whl/cu128"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "STAMP=%VENV_DIR%\.installed-requirements"

if exist "%PYTHON%" goto :deps

rem --- find a supported Python (Kokoro needs 3.10-3.12) via the py launcher ---
set "PY="
for %%V in (3.12 3.11 3.10) do (
    if not defined PY (
        py -%%V -c "import sys" >nul 2>&1 && set "PY=py -%%V"
    )
)
if not defined PY (
    echo error: Python 3.10-3.12 not found.
    echo Install Python 3.12 from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^).
    exit /b 1
)

echo ==^> Creating virtual environment with %PY% in .\%VENV_DIR%
%PY% -m venv "%VENV_DIR%" || exit /b 1

rem PyPI's Windows torch is CPU-only, so grab the CUDA build if there's an NVIDIA GPU.
where nvidia-smi >nul 2>&1
if %errorlevel%==0 (
    echo ==^> NVIDIA GPU detected - installing CUDA build of PyTorch
    "%PYTHON%" -m pip install --upgrade pip --quiet
    "%PYTHON%" -m pip install torch --index-url %TORCH_INDEX_URL% || exit /b 1
)

:deps
fc /b requirements.txt "%STAMP%" >nul 2>&1
if %errorlevel%==0 goto :run
echo ==^> Installing dependencies ^(first run pulls PyTorch - a few GB, be patient^)
"%PYTHON%" -m pip install --upgrade pip --quiet
"%PYTHON%" -m pip install -r requirements.txt || exit /b 1
copy /y requirements.txt "%STAMP%" >nul

:run
"%PYTHON%" -m pdf_to_audiobook %*
