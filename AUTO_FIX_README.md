# 🔧 SadTalker Auto-Fix Feature

## Overview

The Enhanced SadTalker batch script now includes an **automatic model download system** that can detect missing or corrupted checkpoint files and download them automatically during execution.

## ✨ Features

### 🚀 Automatic Model Detection
- **Real-time Validation**: Checks all required model files before execution
- **File Integrity**: Validates file sizes to detect 0-byte corrupted files
- **Smart Fallback**: Downloads missing files only when needed

### 📥 Intelligent Download System
- **Multiple Sources**: Tries GitHub, HuggingFace, and Google Drive URLs
- **Progress Tracking**: Shows download progress with file sizes
- **Validation**: Verifies downloaded files before proceeding
- **Resume Support**: Skips files that already exist and are valid

### 🔄 Seamless Integration
- **No Manual Steps**: Works transparently during normal execution
- **Graceful Fallback**: Falls back to manual instructions if auto-fix is disabled
- **Clean Logging**: Clear progress feedback throughout the process

## 📋 Required Model Files

The system automatically downloads these critical SadTalker checkpoints:

| File | Size | Description |
|------|------|-------------|
| `arcface_model.pth` | ~275 MB | Face Recognition Model |
| `facerecon_model.pth` | ~85 MB | Face Reconstruction Model |
| `auido2pose_00140-model.pth` | ~91 MB | Audio-to-Pose Model |
| `auido2exp_00300-model.pth` | ~33 MB | Audio-to-Expression Model |
| `facevid2vid_00189-model.pth.tar` | ~2 GB | Main Animation Model |

**Total Download Size**: ~2.5 GB

## 🎯 Usage

### Option 1: Auto-Fix Flag (Recommended)
```batch
run_sadtalker_enhanced.bat --auto-fix --driven_audio speech.wav --source_image face.jpg --result_dir output
```

### Option 2: Manual Download
```batch
python download_correct_models.py
```

### Option 3: Validation Only
```batch
python download_correct_models.py --validate-only
```

## 🔍 How It Works

### 1. **Checkpoint Validation**
```
🔍 CHECKPOINT VALIDATION
========================
Checking critical model files...
✅ VALID: Arcface Model - checkpoints\arcface_model.pth (288,860,037 bytes)
❌ MISSING: Face Reconstruction Model - checkpoints\facerecon_model.pth
```

### 2. **Auto-Fix Trigger** (if `--auto-fix` flag is used)
```
🔧 AUTO-FIX ENABLED: Attempting to download missing model files...
================================================================================
📥 Executing: python download_correct_models.py
🔍 Processing: Face Reconstruction Model
📥 Face Reconstruction Model from github.com...
✅ SUCCESS: Valid (89,100,000 bytes)
```

### 3. **Re-validation**
```
🔄 Re-validating checkpoint files...
✅ All checkpoint files validated successfully after download!
🚀 Proceeding with SadTalker execution...
```

## ⚙️ Configuration Options

### Batch Script Flags
```batch
--auto-fix          # Enable automatic model downloading
--cpu               # Use CPU mode (slower, more compatible)
--verbose           # Enable detailed logging
```

### Download Script Options
```batch
python download_correct_models.py --help

Options:
  --checkpoints-dir DIR    # Custom checkpoint directory (default: ./checkpoints)
  --force                  # Re-download even if files exist
  --validate-only          # Only check files, don't download
  --model MODEL_NAME       # Download specific model only
```

## 🔧 Advanced Usage

### Download Specific Model Only
```batch
python download_correct_models.py --model facerecon_model.pth
```

### Force Re-download All Models
```batch
python download_correct_models.py --force
```

### Custom Checkpoint Directory
```batch
python download_correct_models.py --checkpoints-dir "D:\MyModels\SadTalker"
```

## 📊 Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| `0` | Success | All models downloaded/validated |
| `1` | Error | Missing files, network issues, or validation failures |
| `124` | Timeout | Download took longer than 15 minutes |
| `130` | Interrupted | User cancelled download (Ctrl+C) |

## 🛠️ Troubleshooting

### ❌ Problem: Downloads Keep Failing
**Solution:**
```batch
# Try different source priority
python download_correct_models.py --force

# Check specific model
python download_correct_models.py --model facevid2vid_00189-model.pth.tar
```

### ❌ Problem: Files Downloaded but Still "Missing"
**Solution:**
```batch
# Validate file integrity
python download_correct_models.py --validate-only

# Check for 0-byte files
dir checkpoints\*.pth
```

### ❌ Problem: Network/Firewall Issues
**Solution:**
1. **Corporate Networks**: May need to download manually from browser
2. **VPN Issues**: Try disabling VPN temporarily
3. **Manual Download**: Download files directly from GitHub releases

### ❌ Problem: Disk Space Issues
**Solution:**
```batch
# Check available space (needs ~3GB free)
dir /s checkpoints\

# Clean temporary files
del checkpoints\*.tmp
```

## 🔒 Security & Reliability

### File Validation
- **Size Checks**: Validates expected file sizes with 10% tolerance
- **Integrity**: Detects 0-byte corrupted downloads
- **Atomic Operations**: Uses temporary files to prevent partial downloads

### Source Verification
- **GitHub Releases**: Primary source (most reliable)
- **HuggingFace**: Secondary source (academic community)
- **Google Drive**: Fallback source (original authors)

### Network Safety
- **HTTPS Only**: All downloads use secure connections
- **Timeout Protection**: 15-minute maximum per operation
- **Progress Tracking**: Real-time download monitoring

## 📈 Performance Tips

### Faster Downloads
1. **Use GitHub**: Usually fastest source
2. **Good Internet**: Stable high-speed connection recommended
3. **Local Storage**: Download to SSD for better performance

### Reliability Tips
1. **Use --auto-fix**: Automated retry logic
2. **Check Space**: Ensure 3GB+ free disk space
3. **Stable Network**: Avoid downloading on unstable connections

## 🧪 Testing

### Test Auto-Fix Functionality
```batch
python test_auto_fix.py
```

### Validate Current Setup
```batch
python download_correct_models.py --validate-only
```

### Test Batch Integration
```batch
run_sadtalker_enhanced.bat --auto-fix --help
```

## 📝 Example Complete Workflow

```batch
# 1. Check current status
python download_correct_models.py --validate-only

# 2. Run with auto-fix enabled
run_sadtalker_enhanced.bat --auto-fix \
  --driven_audio "examples/driven_audio/chinese_news.wav" \
  --source_image "examples/source_image/art_0.png" \
  --result_dir "results" \
  --enhancer gfpgan \
  --preprocess full \
  --still

# 3. If successful, video will be generated
# 4. If downloads needed, they happen automatically
# 5. Process continues seamlessly
```

## 🔗 Related Documentation

- [`ENHANCED_BATCH_README.md`](ENHANCED_BATCH_README.md) - Enhanced batch script features
- [`ENHANCED_BATCH_SUMMARY.md`](ENHANCED_BATCH_SUMMARY.md) - Technical implementation details
- [`../SadTalker/README.md`](../SadTalker/README.md) - Main SadTalker documentation

## 💡 Tips & Best Practices

1. **Always use --auto-fix** for production deployments
2. **Pre-download models** in controlled environments
3. **Monitor disk space** before starting large downloads
4. **Test with --validate-only** first to check current status
5. **Keep backups** of working model files

---

✅ **Auto-fix is now enabled by default in all SadTalker operations!** 