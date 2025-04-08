# Markdown to Anki Converter

A Python utility that converts Markdown notes into Anki-compatible flashcards.

## Overview

This tool helps you automatically generate Anki flashcards from your existing Markdown notes. It can detect several common patterns in Markdown files and transform them into question/answer pairs or cloze deletions.

## Installation

1. Download the `md_to_anki.py` script to your computer
2. Make the script executable (Unix/Linux/macOS):
   ```bash
   chmod +x md_to_anki.py
   ```
3. Ensure you have Python 3.6+ installed

## Usage

Basic usage:
```bash
./md_to_anki.py input.md output.csv
```

Advanced options:
```bash
./md_to_anki.py input.md output.csv --format=tsv --tags="ruby,programming" --cloze
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--format=FORMAT` | Output format: `csv` or `tsv` (default: `csv`) |
| `--delimiter=CHAR` | Custom delimiter for CSV (default: `,` for CSV, `\t` for TSV) |
| `--tags=TAGS` | Add these tags to all cards (comma-separated) |
| `--cloze` | Force generation of cloze deletion cards |

## Markdown Formatting Guidelines

The script automatically detects and converts these patterns:

### 1. Section-Based Cards (H2 Headers)

```markdown
## What is a Ruby class?
A Ruby class is a blueprint for creating objects that share similar attributes and methods.

## What is the difference between `puts` and `print` in Ruby?
- `puts` adds a newline after output
- `print` does not add a newline
```

This creates cards with:
- Front: "What is a Ruby class?"
- Back: "A Ruby class is a blueprint for creating objects that share similar attributes and methods."

### 2. Bullet Point Cards (Main bullets + sub-bullets)

```markdown
- What are the core principles of OOP?
  - Encapsulation
  - Inheritance
  - Polymorphism
  - Abstraction

- Explain the Ruby method visibility options
  - Public: Available to all objects
  - Protected: Available to the class and its subclasses
  - Private: Only available within the class definition
```

This creates cards with:
- Front: "What are the core principles of OOP?"
- Back: "Encapsulation\nInheritance\nPolymorphism\nAbstraction"

### 3. Code Block Cards

```markdown
This code implements a binary search algorithm:

```ruby
def binary_search(array, target)
  low = 0
  high = array.length - 1
  
  while low <= high
    mid = (low + high) / 2
    if array[mid] == target
      return mid
    elsif array[mid] < target
      low = mid + 1
    else
      high = mid - 1
    end
  end
  
  return nil
end
```
```

This creates cards with:
- Front: "What does this ruby code do?\n[code block]"
- Back: "This code implements a binary search algorithm."

### 4. Cloze Deletion Cards

For text with bold or code-formatted sections:

```markdown
In Ruby, an **iterator** is a method that repeatedly invokes a block of code.

The `yield` keyword in Ruby is used to invoke a block passed to a method.
```

This creates cloze cards where the bold/backtick text is replaced with cloze deletions:
- Card: "In Ruby, a {{c1::iterator}} is a method that repeatedly invokes a block of code."
- Card: "The {{c1::yield}} keyword in Ruby is used to invoke a block passed to a method."

## Importing into Anki

1. Open Anki
2. Click "Import File" (or press Ctrl+Shift+I / Cmd+Shift+I)
3. Select your generated CSV/TSV file
4. Configure the import settings:
   - For basic cards:
     - Note Type: Basic
     - Field mapping: Field 1 = Front, Field 2 = Back, Field 3 = Tags (if included)
   - For cloze cards:
     - Note Type: Cloze
     - Field mapping: Field 1 = Text, Field 2 = Tags (if included)
5. Click "Import"

## Tips for Effective Cards

1. **Keep content atomic**: One concept per card
2. **Use clear formatting**: Make questions stand out with headers
3. **Include context**: Especially for code examples
4. **Use bold text strategically**: Highlight key terms for cloze deletions
5. **Organize with bullet points**: Create structured Q&A pairs

## Troubleshooting

- If your CSV doesn't import correctly, try using TSV format (`--format=tsv`)
- If you have commas in your content, use TSV or a custom delimiter
- If cards aren't being detected properly, consider using explicit formatting
- If cloze deletions aren't working, make sure to use **bold text** or `backticks`

## Examples

### Example 1: Ruby Syntax Notes

```markdown
## What is a Symbol in Ruby?
A Symbol is an immutable name, string, or identifier. They are prefixed with a colon, like `:name`.

## How do you define a class method in Ruby?
```ruby
class MyClass
  def self.class_method
    # method body
  end
end
```

## What is the difference between `==` and `equal?` in Ruby?
- `==` checks if two objects have the same value
- `equal?` checks if two objects are the same object (identical object_id)
```

### Example 2: Data Structure Notes with Cloze Deletions

```markdown
A **stack** is a last-in, first-out (LIFO) data structure.

A **queue** is a first-in, first-out (FIFO) data structure.

In a **binary search tree**, each node has at most two children.
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

This project was developed with assistance from Anthropic's Claude AI assistant, which helped with:
- Documentation writing and organization
- Code structure suggestions
- Troubleshooting and debugging assistance

Claude was used as a development aid while all final implementation decisions and code review were performed by the human developer.

## Disclaimer

This tool is provided as-is with no warranties or guarantees. It is currently in development and may contain bugs or limitations. Please report any issues you encounter.
