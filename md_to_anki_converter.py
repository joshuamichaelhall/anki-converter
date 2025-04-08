#!/usr/bin/env python3
"""
md_to_anki.py - Convert Markdown notes to Anki-importable format

This script parses a Markdown file and converts it to a CSV file that can be
imported into Anki. It looks for specific patterns to create question/answer pairs.

Usage:
    python md_to_anki.py input.md output.csv

Options:
    --format=FORMAT    Output format (csv or tsv, default: csv)
    --delimiter=CHAR   Custom delimiter character for CSV (default: comma)
    --tags=TAGS        Add these tags to all cards (comma-separated)
    --cloze            Generate cloze deletion cards instead of basic cards
"""

import re
import csv
import argparse
import sys
from pathlib import Path


def parse_markdown_h2_sections(md_content):
    """Parse markdown content into sections based on H2 headers."""
    # Split the content by H2 headers
    sections = re.split(r'(?m)^##\s+(.*?)$', md_content)
    
    # The first element is text before any H2, which we'll ignore if it's empty
    if not sections[0].strip():
        sections.pop(0)
    
    # Now we have [header1, content1, header2, content2, ...]
    result = []
    for i in range(0, len(sections), 2):
        if i + 1 < len(sections):
            result.append((sections[i].strip(), sections[i+1].strip()))
    
    return result


def parse_markdown_bullet_points(md_content):
    """Parse markdown content into question/answer pairs based on bullet points."""
    cards = []
    
    # Split content into lines
    lines = md_content.split("\n")
    
    current_question = None
    current_answer = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a main bullet point (potential question)
        if line.startswith("- ") or line.startswith("* "):
            # If we have a question and answer accumulated, add them
            if current_question and current_answer:
                cards.append((current_question, "\n".join(current_answer)))
            
            # Start a new question
            current_question = line[2:].strip()
            current_answer = []
        
        # Check if this is a sub-bullet (answer component)
        elif line.startswith("  - ") or line.startswith("  * "):
            if current_question:  # Only add if we have a question
                current_answer.append(line[4:].strip())
    
    # Add the last card if there is one
    if current_question and current_answer:
        cards.append((current_question, "\n".join(current_answer)))
    
    return cards


def parse_markdown_code_blocks(md_content):
    """Parse markdown content for code blocks to create cards."""
    cards = []
    
    # Find all code blocks with language specifiers
    code_blocks = re.findall(r'```(\w+)\n(.*?)```', md_content, re.DOTALL)
    
    for lang, code in code_blocks:
        # Create a "What does this code do?" card
        question = f"What does this {lang} code do?\n```{lang}\n{code.strip()}\n```"
        
        # Look for comments or context before the code block
        block_position = md_content.find(f"```{lang}\n{code}")
        start_of_paragraph = md_content.rfind("\n\n", 0, block_position)
        
        if start_of_paragraph != -1:
            context = md_content[start_of_paragraph:block_position].strip()
            if context and not context.startswith("```"):
                answer = context
                cards.append((question, answer))
    
    return cards


def create_cloze_cards(md_content):
    """Create cloze deletion cards from markdown content with highlighted text."""
    cards = []
    
    # Find all paragraphs
    paragraphs = re.split(r'\n\s*\n', md_content)
    
    for paragraph in paragraphs:
        # Skip headers and short content
        if paragraph.startswith('#') or len(paragraph) < 20:
            continue
            
        # Find highlighted text (bold or backticks)
        highlights = re.findall(r'\*\*(.*?)\*\*|`(.*?)`', paragraph)
        
        if highlights:
            # Create a cloze card with the first highlight
            cloze_text = paragraph
            count = 1
            
            for highlight in highlights:
                # Get the highlighted text (either from bold or backtick match)
                highlighted_text = next(h for h in highlight if h)
                
                # Replace with cloze deletion
                pattern = r'\*\*' + re.escape(highlighted_text) + r'\*\*'
                if not re.search(pattern, cloze_text):
                    pattern = r'`' + re.escape(highlighted_text) + r'`'
                
                cloze_text = re.sub(pattern, f"{{{{c{count}::{highlighted_text}}}}}", cloze_text, 1)
                count += 1
            
            # Only add if we actually created cloze deletions
            if "{{c" in cloze_text:
                cards.append((cloze_text, ""))
    
    return cards


def detect_card_format(md_content):
    """Try to determine the most appropriate parsing method for the markdown content."""
    if re.search(r'(?m)^##\s+', md_content):
        # Has H2 headers - likely section-based notes
        return "sections"
    elif re.search(r'(?m)^- |^\* ', md_content) and re.search(r'(?m)^  - |^  \* ', md_content):
        # Has bullet points with sub-bullets
        return "bullets"
    elif re.search(r'```\w+\n', md_content):
        # Has code blocks
        return "code"
    else:
        # Default to looking for bold text for cloze deletions
        return "cloze"


def convert_md_to_anki(md_content, output_format="csv", cloze_mode=False, tag_list=None):
    """Convert markdown content to Anki importable format."""
    cards = []
    
    # Detect the best parsing method if not explicitly using cloze mode
    if cloze_mode:
        format_method = "cloze"
    else:
        format_method = detect_card_format(md_content)
    
    # Parse using the appropriate method
    if format_method == "sections":
        sections = parse_markdown_h2_sections(md_content)
        cards.extend(sections)
    elif format_method == "bullets":
        cards.extend(parse_markdown_bullet_points(md_content))
    elif format_method == "code":
        cards.extend(parse_markdown_code_blocks(md_content))
    elif format_method == "cloze":
        cards.extend(create_cloze_cards(md_content))
    
    return cards, format_method


def write_cards_to_file(cards, output_file, output_format="csv", delimiter=",", tag_list=None, card_type="Basic"):
    """Write cards to a CSV/TSV file importable by Anki."""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=delimiter)
        
        tags = "" if tag_list is None else tag_list
        
        if card_type == "Cloze":
            # For cloze cards, we only need the text field and tags
            for front, _ in cards:
                writer.writerow([front, tags])
        else:
            # For basic cards, we need front, back, and tags
            for front, back in cards:
                writer.writerow([front, back, tags])


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown notes to Anki-importable format")
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("output", help="Output file (CSV/TSV)")
    parser.add_argument("--format", choices=["csv", "tsv"], default="csv", help="Output format")
    parser.add_argument("--delimiter", default=None, help="Custom delimiter for CSV")
    parser.add_argument("--tags", default="", help="Tags to add to all cards (comma-separated)")
    parser.add_argument("--cloze", action="store_true", help="Generate cloze deletion cards")
    
    args = parser.parse_args()
    
    # Set delimiter based on format if not specified
    if args.delimiter is None:
        args.delimiter = "\t" if args.format == "tsv" else ","
    
    # Read input file
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
        return 1
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1
    
    # Convert markdown to cards
    cards, detected_format = convert_md_to_anki(md_content, args.format, args.cloze, args.tags)
    
    # Write cards to output file
    try:
        card_type = "Cloze" if args.cloze or detected_format == "cloze" else "Basic"
        write_cards_to_file(cards, args.output, args.format, args.delimiter, args.tags, card_type)
        
        print(f"Converted {len(cards)} cards from {args.input} to {args.output}")
        print(f"Detected format: {detected_format}")
        print(f"Card type: {card_type}")
        
        if card_type == "Cloze":
            print("Note: Import this file with the Cloze note type in Anki")
        else:
            print("Note: Import this file with the Basic note type in Anki")
            
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
