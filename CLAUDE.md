# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Photo Sorting Application - A tkinter-based GUI tool designed specifically for sorting photos for LoRA (Low-Rank Adaptation) training datasets. Users can quickly categorize images into different directories using custom keyboard hotkeys.

## Running the Application

```bash
python photosorter.py
```

**Requirements:**
- Python 3.x
- tkinter (usually bundled with Python)
- Pillow (PIL fork for image handling)

Install dependencies:
```bash
pip install Pillow
```

## Architecture

### Single-file Application Structure

The entire application is contained in `photosorter.py` with two main classes:

**RoundedButton (lines 8-69)**
- Custom tkinter Canvas widget creating rounded, modern-looking buttons
- Handles hover states, press/release animations
- Used throughout the UI for consistent styling

**PhotoSorterApp (lines 71-257)**
- Main application controller managing:
  - Image loading and display with aspect-ratio preservation
  - Target directory management with custom hotkey bindings
  - File movement operations using `shutil.move()`
  - Undo history (last 5 moves) via `move_history` list
  - Keyboard navigation (arrow keys for browsing, single-key hotkeys for sorting)

### Key Data Structures

- `image_paths`: List of absolute paths to images in the loaded folder
- `target_dirs`: Dict mapping `{dir_name: {'path': str, 'hotkey': str}}`
- `move_history`: List of tuples `[(src_path, dst_dir), ...]` for undo functionality (max 100)
- `current_image_index`: Integer tracking which image is displayed
- `flagged_images`: List of flagged image paths for later review
- `config_file`: Path to JSON config ("photosorter_config.json")
- `last_folder`: Path to last opened folder (auto-loads on startup)
- `show_metadata`: Boolean toggle for metadata overlay

### UI Layout

```
┌─────────────────────────────────────┐
│ Sidebar (200px) │  Image Display    │
│  - Dir List     │  (Canvas, black)  │
│  - Add Dir Btn  │                   │
└─────────────────────────────────────┘
│     Control Buttons (bottom)        │
│  [Load Folder] [Undo]               │
│  Progress Label                     │
└─────────────────────────────────────┘
```

## LoRA Training Context

This tool is built for preparing training datasets for LoRA models. Typical workflow:
1. User has a large collection of images
2. Images need to be sorted into categories (e.g., "face", "full_body", "landscape", "discard")
3. Quick keyboard-based sorting is essential for processing hundreds/thousands of images
4. Undo functionality helps correct mistakes without manual file management

## New Features (v2.0.0)

### Session Persistence
- Configuration saved to `photosorter_config.json` in working directory
- Automatically loads last session on startup
- Target directories and hotkeys preserved between sessions

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| Left/Right Arrow | Navigate between images |
| 1-9 | Move to directory by position |
| Q/W/E/R/A/S | Default Quick Setup hotkeys |
| Spacebar | Skip to next image |
| Delete | Move to trash folder |
| Ctrl+Z | Undo last move |
| i | Toggle metadata overlay |
| f | Flag/unflag current image |
| Shift+F | View flagged images only |

### UI Enhancements
- Live directory counts in sidebar
- Next image preview (150x150px, bottom-right)
- Metadata overlay showing dimensions, file size, aspect ratio
- Flagged image indicator (orange badge)
- Quick Setup button for LoRA templates

## Code Patterns

- Dark theme UI: `#2D2D2D` background, `#3C3F41` for components, white text
- Font: Segoe UI throughout for Windows-native appearance
- Image resizing: Uses `Image.LANCZOS` for high-quality thumbnail generation
- Error handling: Try/except blocks with messagebox error dialogs

## Future Enhancement Ideas

Completed in v2.0.0:
- ✅ Session persistence
- ✅ Image metadata display
- ✅ Preview next image
- ✅ Keyboard shortcut improvements
- ✅ Flag system for review

Still open for consideration:
- Batch operations (multi-select, tag multiple images)
- Grid preview mode
- Keyboard shortcut reference overlay (help screen)
- Recursive folder scanning
- Image filtering by dimensions/aspect ratio
- Copy mode (duplicate instead of move)
- EXIF data display
- Custom Quick Setup templates
