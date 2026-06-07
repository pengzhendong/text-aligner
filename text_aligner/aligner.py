# Copyright (c) 2026 Zhendong Peng (pzd17@tsinghua.org.cn)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from functools import partial
from unicodedata import category

from rapidfuzz.distance import Levenshtein


def is_agnostic(char: str, space_agnostic: bool = True, punctuation_agnostic: bool = True):
    """Check if a character is a format character (space or punctuation) that can be ignored during alignment."""
    cat = category(char)
    if space_agnostic and cat == "Zs":
        return True
    if punctuation_agnostic and cat[0] in ("P", "S"):
        return True
    return False


def _merge_opcodes(opcodes):
    """Merge consecutive non-equal opcodes into a single replace."""
    merged = []
    for opcode in opcodes:
        if opcode.tag == "equal":
            merged.append(("equal", opcode.src_start, opcode.src_end, opcode.dest_start, opcode.dest_end))
        else:
            if merged and merged[-1][0] != "equal":
                prev = merged[-1]
                merged[-1] = ("replace", prev[1], opcode.src_end, prev[3], opcode.dest_end)
            else:
                merged.append(("replace", opcode.src_start, opcode.src_end, opcode.dest_start, opcode.dest_end))
    return merged


def _split_content_format(chars, is_agnostic_fn):
    """Split characters into content and format arrays.

    Returns (content, fmt) where:
      - content[i] is the i-th non-agnostic character
      - fmt[i] is the list of agnostic characters immediately before content[i]
      - fmt[len(content)] is trailing agnostic characters after the last content character
    """
    content = []
    fmt = [[]]
    for char in chars:
        if is_agnostic_fn(char):
            fmt[-1].append(char)
        else:
            content.append(char)
            fmt.append([])
    return content, fmt


def _align_chars(ref_str, hyp_str, is_agnostic_fn):
    """Character-level alignment: use hyp content with ref formatting."""
    ref_content, ref_fmt = _split_content_format(list(ref_str), is_agnostic_fn)
    hyp_content, hyp_fmt = _split_content_format(list(hyp_str), is_agnostic_fn)

    result = []
    for opcode in Levenshtein.opcodes(ref_content, hyp_content):
        op, i1, i2, j1, j2 = opcode.tag, opcode.src_start, opcode.src_end, opcode.dest_start, opcode.dest_end
        if op == "equal":
            for k in range(i2 - i1):
                result.extend(ref_fmt[i1 + k])
                result.append(hyp_content[j1 + k])
        elif op == "delete":
            pass
        elif op in ("insert", "replace"):
            for k in range(j2 - j1):
                result.extend(hyp_fmt[j1 + k])
                result.append(hyp_content[j1 + k])

    result.extend(ref_fmt[len(ref_content)])
    return "".join(result).strip()


def align(reference: str, hypothesis: str, space_agnostic: bool = True, punctuation_agnostic: bool = True):
    """Align hypothesis text to reference text, preserving reference formatting.

    Two-level alignment:
      1. Word-level: align normalized words (format chars stripped) via Levenshtein
      2. Char-level: for matched words, inherit ref's formatting with hyp's content

    Args:
        reference: The reference text whose formatting should be preserved.
        hypothesis: The hypothesis text whose content should be kept.
        space_agnostic: If True, treat space differences as formatting (not content).
        punctuation_agnostic: If True, treat punctuation differences as formatting.

    Returns:
        Aligned text with hyp content and ref formatting.
    """
    ref_text = re.sub(r"\s+", " ", reference).strip()
    hyp_text = re.sub(r"\s+", " ", hypothesis).strip()
    if not ref_text:
        return hyp_text
    if not hyp_text:
        return ""
    _agnostic = partial(is_agnostic, space_agnostic=space_agnostic, punctuation_agnostic=punctuation_agnostic)

    ref_words = ref_text.split(" ")
    hyp_words = hyp_text.split(" ")

    def normalize(word):
        return "".join(c for c in word if not _agnostic(c))

    ref_norm = [normalize(w) for w in ref_words]
    hyp_norm = [normalize(w) for w in hyp_words]

    result_words = []
    for op, i1, i2, j1, j2 in _merge_opcodes(Levenshtein.opcodes(ref_norm, hyp_norm)):
        if op == "equal":
            for k in range(i2 - i1):
                result_words.append(_align_chars(ref_words[i1 + k], hyp_words[j1 + k], _agnostic))
        elif op == "delete":
            pass
        elif op == "insert":
            result_words.extend(hyp_words[j1:j2])
        elif op == "replace":
            ref_chunk = " ".join(ref_words[i1:i2])
            hyp_chunk = " ".join(hyp_words[j1:j2])
            if normalize(ref_chunk) == normalize(hyp_chunk):
                result_words.append(_align_chars(ref_chunk, hyp_chunk, _agnostic))
            else:
                result_words.extend(hyp_words[j1:j2])

    # Append ref's trailing format (punctuation after the last word) to the last result word
    ref_last_trailing = "".join(c for c in ref_words[-1] if _agnostic(c) and ref_words[-1].endswith(c))
    if ref_last_trailing:
        _, ref_last_fmt = _split_content_format(list(ref_words[-1]), _agnostic)
        trailing = "".join(ref_last_fmt[-1])
        if trailing and result_words:
            last = result_words[-1]
            _, last_fmt = _split_content_format(list(last), _agnostic)
            if not last_fmt[-1]:
                result_words[-1] = last + trailing

    return " ".join(w for w in result_words if w)
