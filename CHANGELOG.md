# Changelog

All notable changes to the Photo Sorting Application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.0] - 2026-01-07

### 🎉 Major Release - Production Ready

This release transforms the Photo Sorter into a professional, standalone application optimized for LoRA training dataset preparation.

### Added - Phase 1 & 2 Improvements
- **Session Persistence**: Configuration automatically saved to `photosorter_config.json`
  - Target directories and hotkeys persist between sessions
  - Last opened folder automatically loads on startup
  - No more manual setup each time!

- **Enhanced Hotkey Panel**: Directory list now shows real-time information
  - Live image counts for each target directory
  - Number keys [1-9] displayed for quick access
  - Format: `[1] Face (Q) - 23 images`

- **Improved Keyboard Shortcuts**:
  - `Ctrl+Z`: Undo last move (more intuitive)
  - `Delete`: Quick move to trash folder (auto-created)
  - `1-9`: Move to corresponding directory by position
  - `Spacebar`: Skip to next image
  - `i`: Toggle image metadata overlay
  - `f`: Flag/unflag current image for review
  - `Shift+F`: View only flagged images

- **Image Metadata Overlay** (Toggle with 'i' key):
  - Filename
  - Dimensions (width x height)
  - File size in KB
  - Aspect ratio (useful for LoRA training requirements)

- **Next Image Preview**:
  - Small thumbnail preview (150x150px) in bottom-right corner
  - Shows "NEXT" label
  - Helps maintain sorting rhythm and context

- **Flag System for Uncertain Images**:
  - Press 'f' to flag images you're uncertain about
  - Visual "FLAGGED" indicator (orange badge)
  - Press Shift+F to filter and review all flagged images
  - Helps maintain sorting flow without getting stuck

- **Quick Setup Templates**:
  - New "Quick Setup" button (green)
  - One-click creation of common LoRA training categories:
    - Face (Q), Full Body (W), Upper Body (E)
    - Landscape (R), Keep (A), Discard (S)
  - Automatically creates folders and assigns hotkeys

- **Directory Management**:
  - Multi-select delete: Ctrl+Click or Shift+Click to select multiple directories
  - Right-click context menu for quick directory removal
  - Red "- Remove Selected" button for intuitive deletion
  - Single confirmation dialog (no annoying multiple popups)
  - Safely removes from app only - files remain untouched

- **Improved Undo System**:
  - Increased from 5 to 100 undo operations
  - More forgiving for longer sorting sessions

- **Auto-Create Directories**:
  - Target directories automatically created if they don't exist
  - No more errors when moving to new folders

- **Help System**:
  - In-app keyboard shortcuts overlay (press H or ?)
  - Clean, modern help panel showing all available shortcuts
  - Organized by category: Navigation, Sorting, Organization, Display

### Fixed
- Line 206 bug: Fixed `END` constant to use `tk.END` properly
- Directory list now updates correctly when adding new directories
- Directory counts refresh after each move operation
- Metadata overlay sizing and spacing improved (narrower width, better vertical spacing)

### Changed
- Undo history limit increased from 5 to 100 moves
- Configuration now saves automatically on window close
- Directory panel shows live counts and number key shortcuts
- **Standalone Executable**: Now distributed as single-file Windows executable (~26MB)
  - No Python installation required
  - No dependencies needed
  - Just download and run!

### Distribution
- Added PyInstaller build configuration
- Created `build_exe.bat` for easy rebuilding
- Comprehensive BUILD_INSTRUCTIONS.md for developers
- Updated README.md with download instructions

## [1.0.0] - 2024 (Baseline)

### Features
- Load photos from selected directory
- View photos one at a time with aspect ratio preservation
- Sort photos into predefined directories using custom hotkeys
- Navigate between photos using arrow keys (Left/Right)
- Undo last 5 sorting actions
- Modern dark UI with rounded buttons
- Support for PNG, JPG, JPEG, BMP, GIF formats

### Known Issues
- Line 206: Uses `END` without `tk.` prefix, causes NameError
- No session persistence - must reconfigure directories each session
- Limited to 5 undo operations
