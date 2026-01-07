# Text Aligner

[![PyPI](https://img.shields.io/pypi/v/text-aligner)](https://pypi.org/project/text-aligner)
[![License](https://img.shields.io/github/license/pengzhendong/text-aligner)](LICENSE)

A Python library for aligning texts based on edit distance algorithms. This tool is particularly useful for comparing and aligning reference texts with hypothesis texts, such as in speech recognition evaluation.

## Features

- **Edit Distance Alignment**: Uses sequence matching algorithms to align texts based on similarity
- **Space Agnostic Mode**: Option to ignore differences in spacing during alignment
- **Punctuation Agnostic Mode**: Option to ignore differences in punctuation during alignment

## Installation

```bash
pip install text-aligner
```

## Usage

### Command Line Interface

```bash
# Align two individual text strings
align-text "AI cannot replace human creativity" "AI can not replace human creativity."
# Output: AI cannot replace human creativity

align-text "AI can not replace human creativity." "AI cannot replace human creativity"
# Output: AI can not replace human creativity.

align-text "He is a well-known writer." "She is a well known writer"
# Output: She is a well-known writer.

align-text "She is a well known writer" "He is a well-known writer."
# Output: He is a well known writer

# Align texts from scp format files (e.g., `utt_id text`)
align-text ref.txt hyp.txt output.txt
```

## Options

- `-s, --space-agnostic`: Ignore differences in spacing (default: True)
- `-p, --punctuation-agnostic`: Ignore differences in punctuation (default: True)
- `output-file`: Optional output file path (default: stdout)

## License

[Apache License 2.0](LICENSE)
