#!/usr/bin/env python3
"""
Image resizing script to make dimensions divisible by 4 with 4K limit.
Resizes images in-place while maintaining aspect ratio.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageFile
import argparse
import math

ImageFile.LOAD_TRUNCATED_IMAGES = True

def round_to_multiple_of_4(value):
    """Round a value to the nearest multiple of 4."""
    return int(round(value / 4) * 4)

def calculate_new_dimensions(width, height, max_dimension=3840):
    """
    Calculate new dimensions that are:
    1. Divisible by 4
    2. Within 4K limits
    3. Maintain aspect ratio
    
    Args:
        width (int): Original width
        height (int): Original height
        max_dimension (int): Maximum allowed dimension (default: 3840 for 4K)
    
    Returns:
        tuple: (new_width, new_height, needs_resize)
    """
    original_width, original_height = width, height
    
    # Check if we need to scale down due to 4K limit
    scale_factor = 1.0
    if max(width, height) > max_dimension:
        scale_factor = max_dimension / max(width, height)
        width = int(width * scale_factor)
        height = int(height * scale_factor)
    
    # Round to nearest multiple of 4
    new_width = round_to_multiple_of_4(width)
    new_height = round_to_multiple_of_4(height)
    
    # Ensure we don't accidentally exceed the limit due to rounding
    while max(new_width, new_height) > max_dimension:
        if new_width > max_dimension:
            new_width -= 4
        if new_height > max_dimension:
            new_height -= 4
    
    # Ensure minimum dimensions
    new_width = max(new_width, 4)
    new_height = max(new_height, 4)
    
    needs_resize = (new_width != original_width or new_height != original_height)
    
    return new_width, new_height, needs_resize

def resize_image(image_path, max_dimension=3840, quality=85):
    """
    Resize an image to be divisible by 4 with 4K limit.
    
    Args:
        image_path (str): Path to the image file
        max_dimension (int): Maximum allowed dimension
        quality (int): JPEG quality for saving
    
    Returns:
        tuple: (original_size, new_size, dimensions_changed)
    """
    try:
        # Get original file size
        original_file_size = os.path.getsize(image_path)
        
        # Open image and get dimensions
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            
            # Calculate new dimensions
            new_width, new_height, needs_resize = calculate_new_dimensions(
                original_width, original_height, max_dimension
            )
            
            if not needs_resize:
                return original_file_size, original_file_size, False
            
            # Resize image
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Prepare save parameters
            save_kwargs = {'optimize': True}
            if image_path.lower().endswith(('.jpg', '.jpeg')):
                save_kwargs['quality'] = quality
                save_kwargs['progressive'] = True
            elif image_path.lower().endswith('.png'):
                save_kwargs['compress_level'] = 9
            
            # Save resized image
            resized_img.save(image_path, **save_kwargs)
            
        # Get new file size
        new_file_size = os.path.getsize(image_path)
        
        return original_file_size, new_file_size, True
        
    except Exception as e:
        print(f"Error resizing {image_path}: {e}")
        return None, None, False

def resize_images_in_directory(directory, max_dimension=3840, quality=85, recursive=True):
    """
    Resize all images in a directory.
    
    Args:
        directory (str): Path to the directory
        max_dimension (int): Maximum allowed dimension
        quality (int): JPEG quality for saving
        recursive (bool): Whether to process subdirectories
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
    
    print(f"Found {len(image_files)} image files to process...")
    print(f"Maximum dimension: {max_dimension}px")
    print(f"Target: dimensions divisible by 4")
    print()
    
    total_original_size = 0
    total_new_size = 0
    resized_count = 0
    skipped_count = 0
    
    for image_path in image_files:
        print(f"Processing: {image_path.name}")
        
        # Get original dimensions
        try:
            with Image.open(image_path) as img:
                original_width, original_height = img.size
                
            new_width, new_height, needs_resize = calculate_new_dimensions(
                original_width, original_height, max_dimension
            )
            
            if not needs_resize:
                print(f"  Dimensions: {original_width}x{original_height} (already optimal)")
                skipped_count += 1
                continue
            
            print(f"  Original: {original_width}x{original_height}")
            print(f"  New: {new_width}x{new_height}")
            
            # Resize the image
            original_size, new_size, success = resize_image(
                str(image_path), max_dimension, quality
            )
            
            if success and original_size is not None:
                total_original_size += original_size
                total_new_size += new_size
                resized_count += 1
                
                # Show file size impact
                original_mb = original_size / (1024 * 1024)
                new_mb = new_size / (1024 * 1024)
                size_change = ((new_size - original_size) / original_size) * 100
                
                print(f"  File size: {original_mb:.2f} MB → {new_mb:.2f} MB ({size_change:+.1f}%)")
            else:
                print(f"  Failed to resize")
                
        except Exception as e:
            print(f"  Error: {e}")
            
        print()
    
    # Summary
    print("="*50)
    print("RESIZE SUMMARY")
    print("="*50)
    print(f"Files processed: {len(image_files)}")
    print(f"Files resized: {resized_count}")
    print(f"Files skipped (already optimal): {skipped_count}")
    
    if resized_count > 0:
        print(f"Total original size: {total_original_size / (1024 * 1024):.2f} MB")
        print(f"Total new size: {total_new_size / (1024 * 1024):.2f} MB")
        
        if total_original_size > 0:
            size_change = ((total_new_size - total_original_size) / total_original_size) * 100
            print(f"Total size change: {size_change:+.1f}%")

def main():
    parser = argparse.ArgumentParser(description='Resize images to be divisible by 4 with 4K limit')
    parser.add_argument('path', help='Directory containing images to resize OR path to single image file')
    parser.add_argument('--max-dimension', type=int, default=3840, 
                       help='Maximum dimension in pixels (default: 3840 for 4K)')
    parser.add_argument('--quality', type=int, default=85, 
                       help='JPEG quality (1-100, default: 85)')
    parser.add_argument('--no-recursive', action='store_true', 
                       help='Do not process subdirectories')
    
    args = parser.parse_args()
    
    # Validate parameters
    if not 1 <= args.quality <= 100:
        print("Quality must be between 1 and 100")
        sys.exit(1)
    
    if args.max_dimension < 4:
        print("Maximum dimension must be at least 4")
        sys.exit(1)
    
    # Ensure max_dimension is divisible by 4
    if args.max_dimension % 4 != 0:
        args.max_dimension = round_to_multiple_of_4(args.max_dimension)
        print(f"Adjusted max dimension to {args.max_dimension} (nearest multiple of 4)")
    
    path = Path(args.path)
    
    # Check if it's a single file or directory
    if path.is_file():
        # Single file resize
        if path.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
            print(f"Resizing single file: {path.name}")
            
            # Get original dimensions
            try:
                with Image.open(path) as img:
                    original_width, original_height = img.size
                    
                new_width, new_height, needs_resize = calculate_new_dimensions(
                    original_width, original_height, args.max_dimension
                )
                
                print(f"Original: {original_width}x{original_height}")
                print(f"New: {new_width}x{new_height}")
                
                if not needs_resize:
                    print("Image already has optimal dimensions")
                    return
                
                original_size, new_size, success = resize_image(
                    str(path), args.max_dimension, args.quality
                )
                
                if success and original_size is not None:
                    original_mb = original_size / (1024 * 1024)
                    new_mb = new_size / (1024 * 1024)
                    size_change = ((new_size - original_size) / original_size) * 100
                    
                    print(f"File size: {original_mb:.2f} MB → {new_mb:.2f} MB ({size_change:+.1f}%)")
                    print("Resize completed successfully")
                else:
                    print("Resize failed")
                    
            except Exception as e:
                print(f"Error processing file: {e}")
                
        else:
            print(f"Unsupported file type: {path.suffix}")
            sys.exit(1)
    elif path.is_dir():
        # Directory resize
        resize_images_in_directory(
            str(path), 
            max_dimension=args.max_dimension,
            quality=args.quality,
            recursive=not args.no_recursive
        )
    else:
        print(f"Path does not exist: {path}")
        sys.exit(1)

if __name__ == "__main__":
    main()