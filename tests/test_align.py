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

from text_aligner import align


class TestFormatAgnostic:
    def test_cannot_vs_can_not(self):
        assert (
            align("AI cannot replace human creativity", "AI can not replace human creativity.")
            == "AI cannot replace human creativity"
        )
        assert (
            align("AI can not replace human creativity.", "AI cannot replace human creativity")
            == "AI can not replace human creativity."
        )

    def test_goodbye_vs_good_bye(self):
        assert align("good bye", "goodbye") == "good bye"
        assert align("goodbye", "good bye") == "goodbye"

    def test_helloworld(self):
        assert align("hello world", "helloworld") == "hello world"
        assert align("helloworld", "hello world") == "helloworld"

    def test_different_word_boundary(self):
        assert align("an ice", "a nice") == "an ice"
        assert align("a nice", "an ice") == "a nice"

    def test_hyphen_vs_space(self):
        assert align("He is a well-known writer.", "She is a well known writer") == "She is a well-known writer."
        assert align("She is a well known writer", "He is a well-known writer.") == "He is a well known writer"

    def test_trailing_period(self):
        assert align("end.", "end") == "end."
        assert align("end", "end.") == "end"

    def test_comma(self):
        assert align("hello, world", "hello world") == "hello, world"
        assert align("hello world", "hello, world") == "hello world"

    def test_ellipsis_and_question_mark(self):
        assert align("Wait... really?", "Wait really") == "Wait... really?"

    def test_exclamation_suppressed(self):
        assert align("hello", "hello!!!") == "hello"
        assert align("hello!!!", "hello") == "hello!!!"


class TestContentDiff:
    def test_single_word_replace(self):
        assert align("The cat sat.", "The dog sat") == "The dog sat."

    def test_multi_word_replace(self):
        assert align("A big, red car.", "A big blue car") == "A big, blue car."

    def test_contraction_expand(self):
        assert align("Don't stop!", "Do not stop") == "Do not stop!"
        assert align("Do not stop!", "Don't stop") == "Don't stop!"

    def test_different_sentence(self):
        assert align("The quick brown fox", "A lazy dog sleeps") == "A lazy dog sleeps"

    def test_case_difference(self):
        assert align("Hello World", "hello world") == "hello world"
        assert align("hello world", "Hello World") == "Hello World"

    def test_insert_word(self):
        assert align("I went home", "I quickly went home") == "I quickly went home"

    def test_delete_word(self):
        assert align("I quickly went home", "I went home") == "I went home"

    def test_insert_multiple(self):
        assert align("She said hello", "She said hi there") == "She said hi there"

    def test_large_diff(self):
        assert align("rutin berangkat", "routing perangkat") == "routing perangkat"
        assert align("rolando mendoza", "ronald dominosa") == "ronald dominosa"
        assert align("rolando mendoza", "ronald domendoza") == "ronald domendoza"
        assert align("A KE-12 DAN KE-13 1000", "KE-12 DAN KE-13BANGKRUT") == "KE-12 DAN KE-13BANGKRUT"


class TestNumberAndFormat:
    def test_thousands_separator(self):
        assert align("price is 1,000 dollars", "price is 1000 dollars") == "price is 1,000 dollars"

    def test_version_dots(self):
        assert align("version 2.0.1", "version 201") == "version 2.0.1"

    def test_number_not_leaking(self):
        assert align("kurang dari 40.000 jiwa", "rangka di empat puluh ribu jiwa.") == "rangka di empat puluh ribu jiwa"

    def test_trailing_format_transfer(self):
        assert align("Mr. Smith went home.", "Mr Smith went away") == "Mr. Smith went away."


class TestEdgeCases:
    def test_empty_ref(self):
        assert align("", "hello") == "hello"

    def test_empty_hyp(self):
        assert align("hello", "") == ""

    def test_both_empty(self):
        assert align("", "") == ""

    def test_whitespace_only(self):
        assert align("  ", "  ") == ""
        assert align("hello", "  ") == ""

    def test_identical(self):
        assert align("hello world", "hello world") == "hello world"

    def test_chinese_identical(self):
        assert align("你好世界", "你好世界") == "你好世界"

    def test_chinese_ref_has_punctuation(self):
        assert align("你好，世界！", "你好世界") == "你好，世界！"

    def test_chinese_hyp_has_punctuation(self):
        assert align("你好世界", "你好，世界！") == "你好世界"
