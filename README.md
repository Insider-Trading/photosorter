# Photo Sorting Application

A modern, keyboard-driven application for sorting photos into directories. Built specifically for organizing LoRA training datasets.

## Download & Run

**No installation required!** Just download and run:

1. Download `PhotoSorter.exe` from the releases
2. Double-click to run
3. Start sorting!

The application is a standalone executable (~26MB) that runs on Windows without requiring Python or any dependencies.

## Features

### Core Functionality
- Load photos from any directory
- View photos one at a time with smooth navigation
- Sort photos into custom directories using keyboard hotkeys
- Undo last 100 moves with Ctrl+Z
- Session persistence (automatically remembers your setup)

### Keyboard Shortcuts
- **Arrow Keys** - Navigate between images
- **1-9** - Quick sort to directory by position
- **Custom Hotkeys** - Assign any key to directories
- **Spacebar** - Skip to next image
- **Delete** - Move to trash
- **F** - Flag/unflag for review
- **Shift+F** - View only flagged images
- **I** - Toggle metadata overlay
- **H or ?** - Show keyboard shortcuts help

### UI Features
- Modern dark theme optimized for long sessions
- Metadata overlay (dimensions, file size, aspect ratio)
- Next image preview
- Live directory counters
- Visual progress tracking
- Quick Setup for LoRA training workflows

## For Developers

### Requirements

- Python 3.x
- Required Python packages:
  - `tkinter` (usually included with Python)
  - `Pillow` (for image handling)
