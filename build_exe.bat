@echo off
echo ========================================
echo Building PhotoSorter Executable
echo ========================================
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist photosorter.spec del photosorter.spec

echo Cleaning old builds...
echo.

REM Build the executable
echo Building executable with PyInstaller...
python -m PyInstaller --onefile --windowed --icon=NONE ^
    --name "PhotoSorter" ^
    --add-data "photosorter_config.json;." ^
    --noconsole ^
    --clean ^
    photosorter.py

echo.
echo ========================================
if exist "dist\PhotoSorter.exe" (
    echo Build completed successfully!
    echo Executable location: dist\PhotoSorter.exe
    echo.
    echo You can now run: dist\PhotoSorter.exe
) else (
    echo Build failed! Check the output above for errors.
)
echo ========================================
pause
