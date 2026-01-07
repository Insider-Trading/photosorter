# PhotoSorter v2.0.0 - Production Release

🎉 **Major update!** PhotoSorter is now a professional, standalone Windows application optimized for LoRA training dataset preparation.

## 📦 Download & Install

**[Download PhotoSorter.exe](../../releases/download/v2.0.0/PhotoSorter.exe)** (~26MB)

No installation required! Just download and run. No Python, no dependencies, no hassle.

## ✨ What's New in v2.0

### 🚀 Standalone Executable
- Single-file Windows executable
- Zero dependencies or installation
- Portable - run from anywhere
- Just 26MB download

### 💾 Session Persistence
- Configuration auto-saves to `photosorter_config.json`
- Target directories and hotkeys remembered
- Last folder automatically loads on startup
- Never lose your setup again

### ⌨️ Enhanced Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| ← → | Navigate images |
| 1-9 | Quick move to directory (by position) |
| Custom | Your assigned hotkeys |
| Spacebar | Skip to next |
| Delete | Move to trash |
| Ctrl+Z | Undo last move |
| F | Flag/unflag image |
| Shift+F | View flagged only |
| I | Toggle metadata |
| H or ? | Show help |

### 📊 Metadata Overlay
Toggle with `I` key:
- Filename
- Dimensions (width × height)
- File size
- Aspect ratio
- Image number / total

### 🎯 Directory Management
- **Multi-select delete**: Ctrl+Click or Shift+Click multiple directories
- Right-click context menu
- Red "Remove Selected" button
- Single confirmation dialog (no spam!)
- Safe removal (files stay intact)

### 🖼️ Next Image Preview
- 150×150px thumbnail in bottom-right
- Maintain sorting rhythm
- See what's coming next

### 🚩 Flag System
- Press `F` to flag uncertain images
- Visual orange "FLAGGED" badge
- Press `Shift+F` to review all flagged
- Keep sorting flow uninterrupted

### ⚡ Quick Setup
- One-click LoRA category creation
- Pre-configured hotkeys:
  - **Q** - Face
  - **W** - Full Body
  - **E** - Upper Body
  - **R** - Landscape
  - **A** - Keep
  - **S** - Discard
- Automatic folder creation

### 🔄 Improved Undo
- 100 undo operations (up from 5)
- Perfect for long sorting sessions

### 🎨 Refined UI
- Modern dark theme
- Optimized metadata overlay spacing
- Live directory image counts
- Smooth progress bar

## 🐛 Bug Fixes
- Fixed `tk.END` constant error
- Directory list updates correctly
- Metadata overlay sizing improved
- Config saving reliability enhanced

## 📋 System Requirements
- Windows 10/11
- ~50MB disk space
- No other dependencies

## 🚦 Getting Started

1. **Download** PhotoSorter.exe
2. **Run** the executable
3. Click **"Load Folder"** to select your images
4. Use **"Quick Setup"** or **"+ Add Directory"** to create sorting categories
5. Start sorting with keyboard hotkeys!

## 💡 Tips for LoRA Dataset Preparation

1. Use **Quick Setup** for instant LoRA categories
2. Press **F** to flag borderline images
3. Use **Shift+F** at the end to review flagged images
4. Press **I** to check aspect ratios quickly
5. Directory counters help track dataset balance

## 🆘 Troubleshooting

**Windows Security Warning?**
- Click "More info" → "Run anyway"
- This is normal for unsigned executables

**Config not saving?**
- Run from a writable location (not Program Files)
- Recommended: Documents or Desktop

**Performance issues?**
- Close other image-heavy applications
- Consider batch sizes of 500-1000 images

## 📝 Configuration File

PhotoSorter creates `photosorter_config.json` in the same directory:

```json
{
  "target_dirs": {
    "Face": {"path": "C:/path/to/face", "hotkey": "q"}
  },
  "last_folder": "C:/path/to/images"
}
```

## 🔗 Links

- [GitHub Repository](https://github.com/YOUR_USERNAME/photosorter)
- [Report Issues](https://github.com/YOUR_USERNAME/photosorter/issues)
- [Full Changelog](CHANGELOG.md)

## 🙏 Acknowledgments

Built for the LoRA training community. Happy sorting! 🚀
