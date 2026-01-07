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

from edit_distance import SequenceMatcher


def agnostic(char: str, space_agnostic: bool = True, punctuation_agnostic: bool = True):
    cat = category(char)
    if space_agnostic and cat == "Zs":
        return True
    if punctuation_agnostic and cat[0] in ("P", "S"):
        return True
    return False


def align(reference: str, hypothesis: str, space_agnostic: bool = True, punctuation_agnostic: bool = True):
    ref_chars = list(re.sub(r"\s+", " ", reference))
    hyp_chars = list(re.sub(r"\s+", " ", hypothesis))
    opcodes = SequenceMatcher(ref_chars, hyp_chars).get_opcodes()
    _agnostic = partial(agnostic, space_agnostic=space_agnostic, punctuation_agnostic=punctuation_agnostic)

    chars = []
    prev_ref_agnostic_idx = -1
    for k, (op, i, _, j, _) in enumerate(opcodes):
        if op == "equal":
            chars.append(hyp_chars[j])
        else:
            if i < len(ref_chars) and _agnostic(ref_chars[i]):
                if i != prev_ref_agnostic_idx:
                    prev_ref_agnostic_idx = i
                    chars.append(ref_chars[i])
            if op == "insert":
                if _agnostic(hyp_chars[j]):
                    if k + 1 < len(opcodes) and opcodes[k + 1][0] != "equal":
                        chars.append(hyp_chars[j])
                else:
                    chars.append(hyp_chars[j])
            elif op == "replace" and not _agnostic(hyp_chars[j]):
                chars.append(hyp_chars[j])
    return re.sub(r"\s+", " ", "".join(chars).strip())
