#!/usr/bin/env python3
"""
Script to extract images from a Word document and map them to image placeholders in markdown files.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
import json
from zipfile import ZipFile
import hashlib

# Required packages: pip install python-docx pillow

try:
    from docx import Document
    from PIL import Image
except ImportError:
    print("Please install required packages:")
    print("pip install python-docx pillow")
    exit(1)


class WordImageExtractor:
    """Extract images from Word documents."""
    
    def __init__(self, word_file_path: str, output_dir: str = "extracted_images"):
        self.word_file_path = Path(word_file_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.image_mapping = {}
        
    def extract_images_from_docx(self) -> Dict[str, str]:
        """
        Extract all images from the Word document.
        Returns a dictionary mapping image names to file paths.
        """
        print(f"Extracting images from: {self.word_file_path}")
        
        # Open the docx file as a zip archive
        with ZipFile(self.word_file_path, 'r') as zip_file:
            # Find all image files in the word/media directory
            image_files = [f for f in zip_file.namelist() if f.startswith('word/media/')]
            
            for idx, image_file in enumerate(image_files, 1):
                # Extract the image
                image_data = zip_file.read(image_file)
                
                # Determine file extension
                ext = os.path.splitext(image_file)[1]
                if not ext:
                    ext = '.png'  # default to PNG if no extension
                
                # Generate a meaningful name
                image_name = f"image_{idx:03d}{ext}"
                output_path = self.output_dir / image_name
                
                # Save the image
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                
                self.image_mapping[image_name] = str(output_path)
                print(f"  Extracted: {image_name}")
        
        # Also try to extract images with captions/alt text using python-docx
        self._extract_with_context()
        
        return self.image_mapping
    
    def _extract_with_context(self):
        """
        Try to extract images with their context (captions, surrounding text).
        This helps in mapping images to their correct placeholders.
        """
        try:
            doc = Document(self.word_file_path)
            
            # Create a context mapping file
            context_mapping = {}
            
            for paragraph in doc.paragraphs:
                # Check if paragraph contains images
                if paragraph._element.xpath('.//pic:pic'):
                    # Get surrounding text for context
                    text = paragraph.text.strip()
                    if text:
                        # Try to match with extracted images
                        for img_name in self.image_mapping.keys():
                            if img_name not in context_mapping:
                                context_mapping[img_name] = []
                            context_mapping[img_name].append(text)
            
            # Save context mapping
            if context_mapping:
                context_file = self.output_dir / "image_context_mapping.json"
                with open(context_file, 'w', encoding='utf-8') as f:
                    json.dump(context_mapping, f, indent=2, ensure_ascii=False)
                print(f"\nContext mapping saved to: {context_file}")
                
        except Exception as e:
            print(f"Note: Could not extract image context: {e}")


class MarkdownImageMapper:
    """Map extracted images to markdown placeholders."""
    
    def __init__(self, md_directory: str, image_mapping: Dict[str, str]):
        self.md_directory = Path(md_directory)
        self.image_mapping = image_mapping
        self.placeholder_pattern = re.compile(
            r'!\[([^\]]*)\]\(([^\)]*)\)|'  # Standard markdown images
            r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>|'  # HTML img tags
            r'\[IMAGE:([^\]]*)\]|'  # Custom placeholder format [IMAGE:name]
            r'<!-- *IMAGE: *([^-]*) *-->'  # HTML comment placeholder
        )
        
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the directory."""
        return list(self.md_directory.rglob("*.md"))
    
    def analyze_placeholders(self) -> Dict[str, List[Tuple[str, int]]]:
        """
        Analyze all markdown files and find image placeholders.
        Returns a dictionary mapping file paths to placeholder locations.
        """
        placeholder_map = {}
        
        md_files = self.find_markdown_files()
        print(f"\nAnalyzing {len(md_files)} markdown files...")
        
        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            matches = self.placeholder_pattern.finditer(content)
            placeholders = []
            
            for match in matches:
                # Extract the placeholder text depending on which group matched
                for group_idx, group in enumerate(match.groups()):
                    if group:
                        placeholders.append((group, match.start(), match.end()))
                        break
            
            if placeholders:
                placeholder_map[str(md_file)] = placeholders
                print(f"  Found {len(placeholders)} placeholders in: {md_file.name}")
        
        return placeholder_map
    
    def suggest_mappings(self, placeholder_map: Dict[str, List[Tuple[str, int]]]) -> Dict[str, str]:
        """
        Suggest mappings between placeholders and extracted images.
        Uses fuzzy matching based on placeholder text.
        """
        suggestions = {}
        
        print("\nSuggesting image mappings...")
        
        for md_file, placeholders in placeholder_map.items():
            for placeholder_text, start, end in placeholders:
                # Clean the placeholder text
                clean_text = placeholder_text.lower().strip()
                clean_text = re.sub(r'[^a-z0-9\s]', '', clean_text)
                
                # Try to match with extracted images
                best_match = None
                best_score = 0
                
                for img_name in self.image_mapping.keys():
                    # Simple scoring based on common words
                    score = self._calculate_similarity(clean_text, img_name.lower())
                    if score > best_score:
                        best_score = score
                        best_match = img_name
                
                if best_match and best_score > 0.3:  # Threshold for match confidence
                    suggestion_key = f"{md_file}:{placeholder_text}"
                    suggestions[suggestion_key] = best_match
                    print(f"  Suggested: '{placeholder_text}' -> {best_match}")
        
        return suggestions
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def apply_mappings(self, mappings: Dict[str, str], backup: bool = True):
        """
        Apply the image mappings to markdown files.
        
        Args:
            mappings: Dictionary mapping placeholder keys to image names
            backup: Whether to create backup files before modifying
        """
        print("\nApplying mappings to markdown files...")
        
        # Group mappings by file
        file_mappings = {}
        for key, img_name in mappings.items():
            md_file, placeholder = key.split(':', 1)
            if md_file not in file_mappings:
                file_mappings[md_file] = {}
            file_mappings[md_file][placeholder] = img_name
        
        for md_file_path, placeholders in file_mappings.items():
            md_file = Path(md_file_path)
            
            # Create backup if requested
            if backup:
                backup_file = md_file.with_suffix('.md.bak')
                shutil.copy2(md_file, backup_file)
                print(f"  Created backup: {backup_file.name}")
            
            # Read the file
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace placeholders
            for placeholder, img_name in placeholders.items():
                img_path = self.image_mapping[img_name]
                
                # Create different replacement patterns
                patterns = [
                    (f'![{placeholder}]([^)]*)', f'![{placeholder}]({img_path})'),
                    (f'\\[IMAGE:{placeholder}\\]', f'![{placeholder}]({img_path})'),
                    (f'<!-- *IMAGE: *{re.escape(placeholder)} *-->', 
                     f'![{placeholder}]({img_path})'),
                ]
                
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            # Write the updated content
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  Updated: {md_file.name}")


def create_mapping_file(placeholder_map: Dict, suggestions: Dict, output_file: str = "image_mappings.json"):
    """
    Create a mapping configuration file that can be manually edited.
    """
    config = {
        "placeholders": placeholder_map,
        "suggestions": suggestions,
        "manual_mappings": {},
        "instructions": (
            "Edit the 'manual_mappings' section to override suggestions. "
            "Format: {'file:placeholder': 'image_name'}"
        )
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nMapping configuration saved to: {output_file}")
    print("Edit this file to adjust mappings, then run with --apply-mappings flag")


def main():
    parser = argparse.ArgumentParser(
        description="Extract images from Word document and map to markdown placeholders"
    )
    parser.add_argument(
        "word_file",
        help="Path to the Word document (Logic Builder Guide.docx)"
    )
    parser.add_argument(
        "md_directory",
        help="Directory containing markdown files"
    )
    parser.add_argument(
        "--output-dir",
        default="extracted_images",
        help="Directory to save extracted images (default: extracted_images)"
    )
    parser.add_argument(
        "--mapping-file",
        default="image_mappings.json",
        help="Path to mapping configuration file"
    )
    parser.add_argument(
        "--apply-mappings",
        action="store_true",
        help="Apply mappings from the configuration file"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup files when applying mappings"
    )
    
    args = parser.parse_args()
    
    # Step 1: Extract images from Word document
    extractor = WordImageExtractor(args.word_file, args.output_dir)
    image_mapping = extractor.extract_images_from_docx()
    
    if not image_mapping:
        print("No images found in the Word document.")
        return
    
    print(f"\nExtracted {len(image_mapping)} images to: {args.output_dir}")
    
    # Step 2: Analyze markdown files
    mapper = MarkdownImageMapper(args.md_directory, image_mapping)
    placeholder_map = mapper.analyze_placeholders()
    
    if not placeholder_map:
        print("No image placeholders found in markdown files.")
        return
    
    # Step 3: Create or load mappings
    if args.apply_mappings and os.path.exists(args.mapping_file):
        # Load existing mappings
        with open(args.mapping_file, 'r') as f:
            config = json.load(f)
        
        # Use manual mappings if available, otherwise use suggestions
        mappings = config.get("manual_mappings", {})
        if not mappings:
            mappings = config.get("suggestions", {})
        
        if mappings:
            mapper.apply_mappings(mappings, backup=not args.no_backup)
            print("\nMapping complete!")
        else:
            print("No mappings found in configuration file.")
    else:
        # Generate suggestions and save configuration
        suggestions = mapper.suggest_mappings(placeholder_map)
        create_mapping_file(placeholder_map, suggestions, args.mapping_file)
        
        print("\nNext steps:")
        print(f"1. Review and edit the mapping file: {args.mapping_file}")
        print("2. Run again with --apply-mappings flag to apply the mappings")


if __name__ == "__main__":
    main()
