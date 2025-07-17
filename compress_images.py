#!/usr/bin/env python3
"""
Image compression script for PNG and JPEG files.
Compresses images in-place while preserving quality.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageFile
import argparse

ImageFile.LOAD_TRUNCATED_IMAGES = True

def compress_image(image_path, quality=85, optimize=True, min_size_mb=2):
    """
    Compress an image file in-place.
    
    Args:
        image_path (str): Path to the image file
        quality (int): Quality level for JPEG (1-100, higher is better)
        optimize (bool): Whether to optimize the image
        min_size_mb (float): Minimum file size in MB to compress
    
    Returns:
        tuple: (original_size, compressed_size, compression_ratio)
    """
    try:
        # Get original file size
        original_size = os.path.getsize(image_path)
        original_size_mb = original_size / (1024 * 1024)
        
        # Check if file is above minimum size threshold
        if original_size_mb < min_size_mb:
            print(f"  Skipping: {original_size_mb:.2f} MB (below {min_size_mb}MB threshold)")
            return original_size, original_size, 0  # No compression performed
        
        # Open and process the image
        with Image.open(image_path) as img:
            # Convert RGBA to RGB for JPEG if needed
            if img.mode == 'RGBA' and image_path.lower().endswith(('.jpg', '.jpeg')):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                img = background
            
            # Determine save parameters based on file type
            save_kwargs = {'optimize': optimize}
            
            if image_path.lower().endswith(('.jpg', '.jpeg')):
                save_kwargs['quality'] = quality
                save_kwargs['progressive'] = True
            elif image_path.lower().endswith('.png'):
                # Maximum PNG compression without mode conversion
                save_kwargs['compress_level'] = 9
            
            # Save the compressed image
            img.save(image_path, **save_kwargs)
        
        # Get compressed file size
        compressed_size = os.path.getsize(image_path)
        compression_ratio = (original_size - compressed_size) / original_size * 100
        
        return original_size, compressed_size, compression_ratio
        
    except Exception as e:
        print(f"Error compressing {image_path}: {e}")
        return None, None, None

def compress_images_in_directory(directory, quality=85, recursive=True, min_size_mb=2):
    """
    Compress all PNG and JPEG images in a directory.
    
    Args:
        directory (str): Path to the directory
        quality (int): Quality level for JPEG compression
        recursive (bool): Whether to process subdirectories
        min_size_mb (float): Minimum file size in MB to compress
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Directory {directory} does not exist.")
        return
    
    # Supported image extensions
    image_extensions = {'.png', '.jpg', '.jpeg'}
    
    # Find all image files
    pattern = '**/*' if recursive else '*'
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(directory.glob(f"{pattern}{ext}"))
        image_files.extend(directory.glob(f"{pattern}{ext.upper()}"))
    
    if not image_files:
        print(f"No image files found in {directory}")
        return
    
    print(f"Found {len(image_files)} image files to compress...")
    
    total_original_size = 0
    total_compressed_size = 0
    successful_compressions = 0
    skipped_files = 0
    
    for image_path in image_files:
        print(f"Processing: {image_path.name}")
        
        original_size, compressed_size, compression_ratio = compress_image(
            str(image_path), quality=quality, min_size_mb=min_size_mb
        )
        
        if original_size is not None:
            total_original_size += original_size
            total_compressed_size += compressed_size
            
            # Convert bytes to MB for display
            original_mb = original_size / (1024 * 1024)
            compressed_mb = compressed_size / (1024 * 1024)
            
            print(f"  Original: {original_mb:.2f} MB")
            print(f"  Compressed: {compressed_mb:.2f} MB")
            print(f"  Reduction: {compression_ratio:.1f}%")
            
            if compression_ratio > 0:
                successful_compressions += 1
            else:
                skipped_files += 1
            print()
    
    # Summary
    if successful_compressions > 0 or skipped_files > 0:
        print("="*50)
        print("COMPRESSION SUMMARY")
        print("="*50)
        print(f"Files compressed: {successful_compressions}")
        print(f"Files skipped (below {min_size_mb}MB): {skipped_files}")
        print(f"Total original size: {total_original_size / (1024 * 1024):.2f} MB")
        print(f"Total compressed size: {total_compressed_size / (1024 * 1024):.2f} MB")
        
        if successful_compressions > 0:
            total_savings = total_original_size - total_compressed_size
            total_compression_ratio = (total_savings / total_original_size) * 100
            print(f"Total space saved: {total_savings / (1024 * 1024):.2f} MB")
            print(f"Overall compression: {total_compression_ratio:.1f}%")

def main():
    parser = argparse.ArgumentParser(description='Compress PNG and JPEG images in-place')
    parser.add_argument('path', help='Directory containing images to compress OR path to single image file')
    parser.add_argument('--quality', type=int, default=85, 
                       help='JPEG quality (1-100, default: 85)')
    parser.add_argument('--no-recursive', action='store_true', 
                       help='Do not process subdirectories')
    parser.add_argument('--min-size', type=float, default=2.0, 
                       help='Minimum file size in MB to compress (default: 2.0)')
    
    args = parser.parse_args()
    
    # Validate quality parameter
    if not 1 <= args.quality <= 100:
        print("Quality must be between 1 and 100")
        sys.exit(1)
    
    # Validate min_size parameter
    if args.min_size < 0:
        print("Minimum size must be non-negative")
        sys.exit(1)
    
    path = Path(args.path)
    
    # Check if it's a single file or directory
    if path.is_file():
        # Single file compression
        if path.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
            print(f"Compressing single file: {path.name}")
            original_size, compressed_size, compression_ratio = compress_image(
                str(path), quality=args.quality, min_size_mb=args.min_size
            )
            
            if original_size is not None:
                original_mb = original_size / (1024 * 1024)
                compressed_mb = compressed_size / (1024 * 1024)
                
                print(f"  Original: {original_mb:.2f} MB")
                print(f"  Compressed: {compressed_mb:.2f} MB")
                print(f"  Reduction: {compression_ratio:.1f}%")
            else:
                print("Compression failed")
        else:
            print(f"Unsupported file type: {path.suffix}")
            sys.exit(1)
    elif path.is_dir():
        # Directory compression
        compress_images_in_directory(
            str(path), 
            quality=args.quality,
            recursive=not args.no_recursive,
            min_size_mb=args.min_size
        )
    else:
        print(f"Path does not exist: {path}")
        sys.exit(1)

if __name__ == "__main__":
    main()