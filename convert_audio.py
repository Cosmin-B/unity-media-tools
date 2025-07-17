#!/usr/bin/env python3
"""
Audio conversion script for Unity WebGL compatibility.
Converts MP3 and WAV files to OGG and MP4 formats using Pydub.
"""

import os
import sys
from pathlib import Path
import argparse
import time

try:
    from pydub import AudioSegment
    from pydub.utils import which
except ImportError:
    print("Error: pydub is not installed. Please install it with:")
    print("pip install pydub")
    sys.exit(1)

def check_ffmpeg():
    """Check if FFmpeg is available."""
    if not which("ffmpeg"):
        print("Error: FFmpeg is not installed or not in PATH.")
        print("Please install FFmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False
    return True

def get_file_size_mb(file_path):
    """Get file size in MB."""
    return os.path.getsize(file_path) / (1024 * 1024)

def convert_audio_file(input_path, output_format="ogg", quality="192k", output_dir=None):
    """
    Convert an audio file to the specified format.
    
    Args:
        input_path (str): Path to input audio file
        output_format (str): Output format ('ogg', 'mp4', 'aac')
        quality (str): Audio quality/bitrate (e.g., '192k', '128k', '320k')
        output_dir (str): Output directory (defaults to same as input)
    
    Returns:
        str: Path to converted file, or None if failed
    """
    try:
        input_path = Path(input_path)
        
        # Determine output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = input_path.parent
        
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Construct output filename
        output_filename = f"{input_path.stem}.{output_format}"
        full_output_path = output_path / output_filename
        
        # Skip if output file already exists
        if full_output_path.exists():
            print(f"  Output file already exists: {output_filename}")
            return str(full_output_path)
        
        # Load audio file
        print(f"  Loading audio file...")
        if input_path.suffix.lower() == '.mp3':
            audio = AudioSegment.from_mp3(str(input_path))
        elif input_path.suffix.lower() == '.wav':
            audio = AudioSegment.from_wav(str(input_path))
        elif input_path.suffix.lower() == '.ogg':
            audio = AudioSegment.from_ogg(str(input_path))
        else:
            # Try generic loading
            audio = AudioSegment.from_file(str(input_path))
        
        # Export to target format
        print(f"  Converting to {output_format.upper()}...")
        
        export_params = {
            'format': output_format,
            'bitrate': quality
        }
        
        # Format-specific parameters
        if output_format == 'ogg':
            export_params['codec'] = 'libvorbis'
        elif output_format == 'mp4':
            export_params['codec'] = 'aac'
        elif output_format == 'aac':
            export_params['codec'] = 'aac'
        
        audio.export(str(full_output_path), **export_params)
        
        return str(full_output_path)
        
    except Exception as e:
        print(f"  Error converting {input_path}: {e}")
        return None

def convert_audio_directory(directory, output_format="ogg", quality="192k", output_dir=None, recursive=True):
    """
    Convert all audio files in a directory.
    
    Args:
        directory (str): Input directory path
        output_format (str): Output format ('ogg', 'mp4', 'aac')
        quality (str): Audio quality/bitrate
        output_dir (str): Output directory (defaults to same as input)
        recursive (bool): Process subdirectories
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Directory {directory} does not exist.")
        return
    
    # Supported input audio extensions
    audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'}
    
    # Find all audio files
    pattern = '**/*' if recursive else '*'
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(directory.glob(f"{pattern}{ext}"))
        audio_files.extend(directory.glob(f"{pattern}{ext.upper()}"))
    
    # Filter out files that are already in the target format
    audio_files = [f for f in audio_files if f.suffix.lower() != f'.{output_format}']
    
    if not audio_files:
        print(f"No audio files found in {directory}")
        return
    
    print(f"Found {len(audio_files)} audio files to convert...")
    print(f"Output format: {output_format.upper()}")
    print(f"Quality: {quality}")
    if output_dir:
        print(f"Output directory: {output_dir}")
    print()
    
    successful_conversions = 0
    failed_conversions = 0
    total_original_size = 0
    total_converted_size = 0
    
    for audio_file in audio_files:
        print(f"Processing: {audio_file.name}")
        
        # Get original file size
        original_size = get_file_size_mb(audio_file)
        total_original_size += original_size
        
        # Convert the file
        start_time = time.time()
        output_path = convert_audio_file(
            str(audio_file),
            output_format=output_format,
            quality=quality,
            output_dir=output_dir
        )
        conversion_time = time.time() - start_time
        
        if output_path:
            # Get converted file size
            converted_size = get_file_size_mb(output_path)
            total_converted_size += converted_size
            
            # Calculate size change
            size_change = ((converted_size - original_size) / original_size) * 100
            
            print(f"  Original: {original_size:.2f} MB")
            print(f"  Converted: {converted_size:.2f} MB ({size_change:+.1f}%)")
            print(f"  Time: {conversion_time:.1f}s")
            print(f"  Output: {Path(output_path).name}")
            
            successful_conversions += 1
        else:
            failed_conversions += 1
        
        print()
    
    # Summary
    print("="*60)
    print("AUDIO CONVERSION SUMMARY")
    print("="*60)
    print(f"Files processed: {len(audio_files)}")
    print(f"Successful conversions: {successful_conversions}")
    print(f"Failed conversions: {failed_conversions}")
    
    if successful_conversions > 0:
        print(f"Total original size: {total_original_size:.2f} MB")
        print(f"Total converted size: {total_converted_size:.2f} MB")
        
        if total_original_size > 0:
            total_size_change = ((total_converted_size - total_original_size) / total_original_size) * 100
            print(f"Total size change: {total_size_change:+.1f}%")

def main():
    parser = argparse.ArgumentParser(
        description='Convert audio files for Unity WebGL compatibility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all MP3/WAV files to OGG
  python3 convert_audio.py archive/
  
  # Convert to MP4 with high quality
  python3 convert_audio.py archive/ --format mp4 --quality 256k
  
  # Convert single file
  python3 convert_audio.py archive/audio.mp3
  
  # Convert to specific output directory
  python3 convert_audio.py archive/ --output-dir converted/
  
  # Convert only current directory (no subdirectories)
  python3 convert_audio.py archive/ --no-recursive

Unity WebGL Notes:
  - OGG format is recommended for best compression and WebGL compatibility
  - MP4/AAC also works well in Unity WebGL
  - Avoid MP3 in Unity WebGL due to compatibility issues
  - WAV files work but are much larger than OGG/MP4
        """
    )
    
    parser.add_argument('path', help='Audio file or directory to convert')
    parser.add_argument('--format', '-f', choices=['ogg', 'mp4', 'aac'], default='ogg',
                       help='Output format (default: ogg)')
    parser.add_argument('--quality', '-q', default='192k',
                       help='Audio quality/bitrate (default: 192k)')
    parser.add_argument('--output-dir', '-o', 
                       help='Output directory (default: same as input)')
    parser.add_argument('--no-recursive', action='store_true',
                       help='Do not process subdirectories')
    
    args = parser.parse_args()
    
    # Check if FFmpeg is available
    if not check_ffmpeg():
        sys.exit(1)
    
    path = Path(args.path)
    
    # Check if it's a single file or directory
    if path.is_file():
        # Single file conversion
        if path.suffix.lower() in {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'}:
            print(f"Converting single file: {path.name}")
            print(f"Output format: {args.format.upper()}")
            print(f"Quality: {args.quality}")
            print()
            
            original_size = get_file_size_mb(path)
            start_time = time.time()
            
            output_path = convert_audio_file(
                str(path),
                output_format=args.format,
                quality=args.quality,
                output_dir=args.output_dir
            )
            
            conversion_time = time.time() - start_time
            
            if output_path:
                converted_size = get_file_size_mb(output_path)
                size_change = ((converted_size - original_size) / original_size) * 100
                
                print(f"Original: {original_size:.2f} MB")
                print(f"Converted: {converted_size:.2f} MB ({size_change:+.1f}%)")
                print(f"Time: {conversion_time:.1f}s")
                print(f"Output: {Path(output_path).name}")
                print("Conversion completed successfully!")
            else:
                print("Conversion failed!")
                sys.exit(1)
        else:
            print(f"Unsupported file type: {path.suffix}")
            sys.exit(1)
    elif path.is_dir():
        # Directory conversion
        convert_audio_directory(
            str(path),
            output_format=args.format,
            quality=args.quality,
            output_dir=args.output_dir,
            recursive=not args.no_recursive
        )
    else:
        print(f"Path does not exist: {path}")
        sys.exit(1)

if __name__ == "__main__":
    main()