# -*- coding: utf-8 -*-
"""CoWriter - AI Prompt Tests."""
from __future__ import annotations

from cowriter.ai.prompts import (
    WRITER_SYSTEM_PROMPT, EDITOR_SYSTEM_PROMPT,
    prompt_continue, prompt_rewrite, prompt_expand,
    prompt_summarize, prompt_brainstorm, prompt_translate, prompt_chat,
)


class TestPrompts:

    def test_writer_system_prompt(self):
        s = WRITER_SYSTEM_PROMPT
        assert "writing assistant" in s
        assert s.startswith("You are")

    def test_editor_system_prompt(self):
        assert "editor assistant" in EDITOR_SYSTEM_PROMPT

    def test_prompt_continue(self):
        r = prompt_continue("Once upon a time")
        assert "Once upon a time" in r
        assert "continue writing" in r

    def test_prompt_continue_with_style(self):
        r = prompt_continue("Hello", style="dramatic")
        assert "dramatic" in r

    def test_prompt_rewrite(self):
        r = prompt_rewrite("Some text")
        assert "Some text" in r
        assert "rewrite" in r

    def test_prompt_rewrite_with_instruction(self):
        r = prompt_rewrite("Text", instruction="make it funny")
        assert "make it funny" in r

    def test_prompt_expand(self):
        r = prompt_expand("Brief text")
        assert "Brief text" in r
        assert "expand" in r

    def test_prompt_expand_with_instruction(self):
        r = prompt_expand("X", instruction="add more detail")
        assert "add more detail" in r

    def test_prompt_summarize(self):
        r = prompt_summarize("Long text here")
        assert "Long text here" in r
        assert "summary" in r.lower()

    def test_prompt_summarize_custom_length(self):
        r = prompt_summarize("Text", length="detailed")
        assert "detailed" in r

    def test_prompt_brainstorm(self):
        r = prompt_brainstorm("Story about a wizard")
        assert "Story about a wizard" in r
        assert "ideas" in r

    def test_prompt_brainstorm_with_topic(self):
        r = prompt_brainstorm("Context", topic="magic system")
        assert "magic system" in r

    def test_prompt_translate(self):
        r = prompt_translate("Hello", "French")
        assert "Hello" in r
        assert "French" in r

    def test_prompt_chat_with_context(self):
        r = prompt_chat("Novel about AI", "What should happen next?")
        assert "Novel about AI" in r
        assert "What should happen next?" in r

    def test_prompt_chat_without_context(self):
        r = prompt_chat("", "Just a question")
        assert r == "Just a question"

