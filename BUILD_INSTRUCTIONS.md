# Building PhotoSorter Executable

## Quick Build

### Windows
Simply run the build script:
```bash
build_exe.bat
```

The executable will be created in the `dist/` folder as `PhotoSorter.exe`

## Manual Build

If you prefer to build manually:

```bash
python -m PyInstaller --onefile --windowed --name "PhotoSorter" --noconsole --clean photosorter.py
```

## Requirements

- Python 3.x
- PyInstaller (`pip install pyinstaller`)
- Pillow (`pip install Pillow`)

## Distribution

The built executable (`dist/PhotoSorter.exe`) is completely standalone and can be:
- Copied to any Windows machine (no Python required)
- Run directly without installation
- Placed anywhere on the system

The executable is approximately 26MB in size due to bundled Python runtime and dependencies.

## Configuration

The application will create a `photosorter_config.json` file in the same directory as the executable to save:
- Target directories
- Hotkey mappings
- Last opened folder

## Troubleshooting

**Build Fails:**
- Ensure PyInstaller is installed: `pip install pyinstaller`
- Try cleaning old builds: Delete `build/` and `dist/` folders
- Run with admin privileges if permission errors occur

**Executable Won't Run:**
- Windows may flag it as untrusted (first-time run warning)
- Click "More info" → "Run anyway"
- Add to Windows Defender exceptions if needed

**Configuration Not Saving:**
- Ensure the executable has write permissions in its directory
- Don't run from Program Files (use Documents or Desktop)
