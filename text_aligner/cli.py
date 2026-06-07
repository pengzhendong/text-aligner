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
import os
import sys
from functools import partial

import click

from text_aligner.aligner import align


def read_scp(scp_path: str) -> dict:
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


@click.command(help="Text aligner")
@click.argument("ref")
@click.argument("hyp")
@click.argument("output-file", type=click.Path(dir_okay=False), required=False)
@click.option("--space-agnostic", "-s", is_flag=True, default=True, help="Space agnostic")
@click.option("--punctuation-agnostic", "-p", is_flag=True, default=True, help="Punctuation agnostic")
def main(ref, hyp, output_file, space_agnostic, punctuation_agnostic):
    input_is_file = os.path.exists(ref)
    assert os.path.exists(hyp) == input_is_file
    _align = partial(align, space_agnostic=space_agnostic, punctuation_agnostic=punctuation_agnostic)

    fout = sys.stdout
    if output_file is None:
        fout.write("\n")
    else:
        fout = codecs.open(output_file, "w", encoding="utf-8")

    if input_is_file:
        refs = read_scp(ref)
        for line in codecs.open(hyp, encoding="utf-8"):
            arr = line.strip().split(maxsplit=1)
            if len(arr) == 0:
                continue
            utt, text = arr[0], arr[1] if len(arr) > 1 else ""
            fout.write(f"{utt}\t{_align(refs[utt], text)}")
            fout.write("\n")
    else:
        fout.write(_align(ref, hyp))
        fout.write("\n")
