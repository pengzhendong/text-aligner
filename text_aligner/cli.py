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

from text_aligner.text_aligner import align
from text_aligner.utils import read_scp


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

    results = []
    if input_is_file:
        refs = read_scp(ref)
        for line in codecs.open(hyp, encoding="utf-8"):
            arr = line.strip().split(maxsplit=1)
            if len(arr) == 0:
                continue
            utt, text = arr[0], arr[1] if len(arr) > 1 else ""
            results.append(f"{utt}\t{_align(refs[utt], text)}")
    else:
        results.append(_align(ref, hyp))

    fout = sys.stdout
    if output_file is None:
        fout.write("\n")
    else:
        fout = codecs.open(output_file, "w", encoding="utf-8")
    for result in results:
        fout.write(result)
        fout.write("\n")
