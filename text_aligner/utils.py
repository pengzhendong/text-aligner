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

import codecs
from typing import Dict


def read_scp(scp_path: str) -> Dict[str, str]:
    """
    Read the scp file and return a dictionary of utterance to text.

    Args:
        scp_path: The path to the scp file.
    Returns:
        The dictionary of utterance to text.
    """
    utt2text = {}
    for line in codecs.open(scp_path, encoding="utf-8"):
        arr = line.strip().split(maxsplit=1)
        if len(arr) == 0:
            continue
        utt, text = arr[0], arr[1] if len(arr) > 1 else ""
        if utt in utt2text and text != utt2text[utt]:
            raise ValueError(f"Conflicting text found:\n{utt}\t{text}\n{utt}\t{utt2text[utt]}")
        utt2text[utt] = text
    return utt2text
