#!/usr/bin/env python3
"""
Generate SRT subtitle files from MP3 audio files using OpenAI Whisper.
Processes all MP3 files in the archive folder and creates corresponding SRT files.
"""

import os
import sys
from pathlib import Path
import whisper
import argparse
from typing import List, Tuple
import time

def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def write_srt_file(segments: List[dict], output_path: Path) -> None:
    """Write segments to SRT file format."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, start=1):
            # Write subtitle number
            f.write(f"{i}\n")
            
            # Write timestamp
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            f.write(f"{start_time} --> {end_time}\n")
            
            # Write text
            text = segment['text'].strip()
            f.write(f"{text}\n")
            
            # Add blank line between subtitles
            f.write("\n")

def process_audio_file(audio_path: Path, model, output_dir: Path = None, language: str = None) -> Tuple[bool, str]:
    """
    Process a single audio file and generate SRT.
    
    Args:
        audio_path: Path to the audio file
        model: Loaded Whisper model
        output_dir: Directory for output files (defaults to same as input)
        language: Language code (e.g., 'en' for English, None for auto-detect)
    
    Returns:
        Tuple of (success, message)
    """
    try:
        # Determine output path
        if output_dir:
            srt_path = output_dir / f"{audio_path.stem}.srt"
        else:
            srt_path = audio_path.parent / f"{audio_path.stem}.srt"
        
        # Check if SRT already exists
        if srt_path.exists():
            return True, f"SRT already exists: {srt_path.name}"
        
        # Transcribe audio
        print(f"  🎙️ Transcribing: {audio_path.name}")
        
        # Use transcribe with specific options
        result = model.transcribe(
            str(audio_path),
            language=language,
            task="transcribe",
            verbose=False,
            word_timestamps=False  # We only need segment timestamps for SRT
        )
        
        # Check if we got segments
        if not result.get('segments'):
            return False, "No speech detected in audio"
        
        # Write SRT file
        write_srt_file(result['segments'], srt_path)
        
        # Get some stats
        num_segments = len(result['segments'])
        total_text = ' '.join(seg['text'].strip() for seg in result['segments'])
        word_count = len(total_text.split())
        
        return True, f"Created {srt_path.name} ({num_segments} segments, {word_count} words)"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def find_mp3_files(directory: Path) -> List[Path]:
    """Find all MP3 files in directory."""
    mp3_files = list(directory.glob("*.mp3"))
    mp3_files.extend(directory.glob("*.MP3"))
    return sorted(mp3_files)

def main():
    parser = argparse.ArgumentParser(description="Generate SRT files from MP3 audio using Whisper")
    parser.add_argument(
        "input_path",
        nargs="?",
        default="archive",
        help="Path to MP3 file or directory containing MP3 files (default: archive)"
    )
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Language code (e.g., 'en' for English, 'auto' for auto-detect)"
    )
    parser.add_argument(
        "--output",
        help="Output directory for SRT files (defaults to same as input)"
    )
    
    args = parser.parse_args()
    
    # Handle language
    language = None if args.language == "auto" else args.language
    
    # Load model
    print(f"📦 Loading Whisper model: {args.model}")
    print("  (This may take a moment on first run to download the model)")
    model = whisper.load_model(args.model)
    print(f"✅ Model loaded successfully\n")
    
    # Get input path
    input_path = Path(args.input_path)
    
    # Handle output directory
    output_dir = Path(args.output) if args.output else None
    if output_dir and not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created output directory: {output_dir}\n")
    
    # Process files
    if input_path.is_file():
        # Single file mode
        if input_path.suffix.lower() != '.mp3':
            print(f"❌ Error: {input_path} is not an MP3 file")
            sys.exit(1)
        
        print(f"🎵 Processing single file: {input_path}")
        success, message = process_audio_file(input_path, model, output_dir, language)
        
        if success:
            print(f"  ✅ {message}")
        else:
            print(f"  ❌ {message}")
            sys.exit(1)
    
    elif input_path.is_dir():
        # Directory mode
        mp3_files = find_mp3_files(input_path)
        
        if not mp3_files:
            print(f"❌ No MP3 files found in: {input_path}")
            sys.exit(1)
        
        print(f"🎵 Found {len(mp3_files)} MP3 files in: {input_path}\n")
        
        # Process each file
        successful = 0
        failed = 0
        skipped = 0
        
        start_time = time.time()
        
        for i, mp3_file in enumerate(mp3_files, 1):
            print(f"[{i}/{len(mp3_files)}] Processing: {mp3_file.name}")
            success, message = process_audio_file(mp3_file, model, output_dir, language)
            
            if success:
                if "already exists" in message:
                    print(f"  ⏭️ {message}")
                    skipped += 1
                else:
                    print(f"  ✅ {message}")
                    successful += 1
            else:
                print(f"  ❌ {message}")
                failed += 1
            
            print()  # Add blank line between files
        
        # Print summary
        elapsed_time = time.time() - start_time
        print("=" * 60)
        print("📊 Summary:")
        print(f"  ✅ Successfully processed: {successful}")
        print(f"  ⏭️ Skipped (already exist): {skipped}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⏱️ Total time: {elapsed_time:.1f} seconds")
        
        if failed > 0:
            sys.exit(1)
    
    else:
        print(f"❌ Error: {input_path} not found")
        sys.exit(1)

if __name__ == "__main__":
    main()