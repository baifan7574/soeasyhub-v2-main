@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo       MATRIX PRODUCTION PIPELINE - STARTING
echo ========================================================
echo.

:: 1. Verify Configuration
echo [Step 1/5] Verifying Configuration...
python test_config.py
if %errorlevel% neq 0 (
    echo [ERROR] Configuration check failed. Aborting.
    pause
    exit /b %errorlevel%
)
echo [OK] Configuration verified.
echo.

:: 2. Run Scout (Miner)
echo [Step 2/5] Running Matrix Scout (Miner)...
echo This process will run until completion or interruption.
python matrix_scout.py
if %errorlevel% neq 0 (
    echo [ERROR] Scout exited with error.
    pause
    exit /b %errorlevel%
)
echo [OK] Scout run finished.
echo.

:: 3. Run Refiner (Process raw PDFs)
echo [Step 3/5] Running Matrix Refiner...
echo Processing batch of 30 records...
python matrix_refiner.py --batch 30
if %errorlevel% neq 0 (
    echo [ERROR] Refiner failed.
    pause
    exit /b %errorlevel%
)
echo [OK] Refiner finished.
echo.

:: 4. Run Composer (Generate HTML Articles)
echo [Step 4/5] Running Matrix Composer...
echo Generating 10 articles...
python matrix_composer.py --batch 10
if %errorlevel% neq 0 (
    echo [ERROR] Composer failed.
    pause
    exit /b %errorlevel%
)
echo [OK] Composer finished.
echo.

:: 5. Run Reporter (Generate PDF Audits)
echo [Step 5/5] Running Matrix Reporter...
echo Generating 10 PDF audits...
python matrix_reporter.py --batch 10
if %errorlevel% neq 0 (
    echo [ERROR] Reporter failed.
    pause
    exit /b %errorlevel%
)
echo [OK] Reporter finished.
echo.

echo ========================================================
echo       MATRIX PRODUCTION PIPELINE - COMPLETED
echo ========================================================
pause
