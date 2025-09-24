# Unity Media Tools

A collection of Python scripts for optimizing media assets for Unity projects, especially Unity WebGL builds.

## Scripts

### 🖼️ resize_images.py
Resizes images to have dimensions divisible by 4 (required for efficient texture compression) with a 4K maximum limit.

**Features:**
- Maintains aspect ratio
- Ensures dimensions are divisible by 4
- 4K maximum limit (3840px)
- Supports PNG, JPG, JPEG
- Recursive directory processing
- In-place resizing with quality preservation
- Optional PNG vertical flipping for Unity texture coordinate conversion

**Usage:**
```bash
# Resize all images in a directory (recursive)
python resize_images.py /path/to/images/

# Resize single image
python resize_images.py image.png

# Custom max dimension and quality
python resize_images.py /path/to/images/ --max-dimension 2048 --quality 90

# Process only current directory (no subdirectories)
python resize_images.py /path/to/images/ --no-recursive

# Flip PNG images vertically (useful for Unity texture coordinates)
python resize_images.py /path/to/images/ --flip-png
```

### 🗜️ compress_images.py
Compresses PNG and JPEG images to reduce file size while preserving visual quality.

**Features:**
- Smart compression (only files above size threshold)
- Format-specific optimization
- RGBA to RGB conversion for JPEG
- Progressive JPEG encoding
- Maximum PNG compression
- Default 2MB minimum file size

**Usage:**
```bash
# Compress all images in directory
python compress_images.py /path/to/images/

# Compress single image
python compress_images.py image.png

# Custom quality and size threshold
python compress_images.py /path/to/images/ --quality 90 --min-size 1.0

# Process only current directory
python compress_images.py /path/to/images/ --no-recursive
```

### 🎵 convert_audio.py
Converts audio files to Unity WebGL compatible formats (OGG, MP4/AAC).

**Features:**
- Multiple input formats (MP3, WAV, OGG, M4A, AAC, FLAC)
- Unity WebGL optimized output (OGG recommended)
- Customizable quality/bitrate
- Batch conversion
- File size reporting

**Usage:**
```bash
# Convert all audio to OGG (recommended for Unity WebGL)
python convert_audio.py /path/to/audio/

# Convert to MP4/AAC format
python convert_audio.py /path/to/audio/ --format mp4

# High quality conversion
python convert_audio.py /path/to/audio/ --quality 256k

# Convert to specific output directory
python convert_audio.py /path/to/audio/ --output-dir converted/

# Convert single file
python convert_audio.py audio.mp3
```

### 📝 generate_srt_files.py
Generates SRT subtitle files from audio using OpenAI Whisper speech recognition.

**Features:**
- Automatic speech recognition using Whisper AI
- Multiple model sizes (tiny, base, small, medium, large)
- Language detection or specific language selection
- Batch processing for multiple files
- Progress tracking and summary statistics
- Properly formatted SRT with timestamps
- Skip existing files to avoid reprocessing

**Usage:**
```bash
# Generate SRT for all MP3 files in directory
python generate_srt_files.py /path/to/audio/

# Use specific Whisper model (base is default)
python generate_srt_files.py /path/to/audio/ --model medium

# Specify language (auto-detect by default)
python generate_srt_files.py /path/to/audio/ --language en

# Process single file
python generate_srt_files.py audio.mp3

# Output to different directory
python generate_srt_files.py /path/to/audio/ --output subtitles/
```

## Installation

### Prerequisites
All scripts require Python 3.6+ and the following packages:

```bash
# Basic dependencies for image and audio processing
pip install Pillow pydub

# For SRT generation (optional, only if using generate_srt_files.py)
pip install torch torchvision torchaudio  # PyTorch
pip install git+https://github.com/openai/whisper.git  # OpenAI Whisper
```

For audio conversion and SRT generation, FFmpeg is also required:
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Quick Setup
```bash
# Clone repository
git clone git@github.com:Cosmin-B/unity-media-tools.git
cd unity-media-tools

# Install basic dependencies
pip install Pillow pydub

# Optional: Install Whisper for SRT generation
pip install torch torchvision torchaudio
pip install git+https://github.com/openai/whisper.git

# Make scripts executable (optional)
chmod +x *.py
```

## Unity WebGL Optimization Notes

### Images
- **Dimensions divisible by 4**: Required for efficient texture compression (DXT, ASTC)
- **4K limit**: Prevents memory issues on lower-end devices
- **Compression**: Reduces download size and loading times

### Audio
- **OGG format**: Best compression and WebGL compatibility
- **Avoid MP3**: Can cause compatibility issues in Unity WebGL
- **MP4/AAC**: Good alternative to OGG
- **Bitrate**: 192k is good balance of quality/size, 128k for smaller files

## Typical Workflow

1. **Resize images** to ensure proper dimensions:
   ```bash
   python resize_images.py Assets/Textures/
   ```

2. **Compress images** to reduce file size:
   ```bash
   python compress_images.py Assets/Textures/
   ```

3. **Convert audio** to WebGL-compatible formats:
   ```bash
   python convert_audio.py Assets/Audio/ --format ogg
   ```

4. **Generate subtitles** from audio narration (optional):
   ```bash
   python generate_srt_files.py Assets/Audio/ --model base
   ```

## License

MIT License - feel free to use in your projects!

## Contributing

Pull requests welcome! Please ensure scripts remain generic and don't include project-specific code.