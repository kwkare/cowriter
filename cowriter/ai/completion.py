"""
CoWriter – AI Completion
========================
Handles text completion, rewriting, expansion, and summarization.
"""

from __future__ import annotations

import logging
from typing import AsyncIterator

from cowriter.ai.provider import AIProvider
from cowriter.ai.prompts import (
    EDITOR_SYSTEM_PROMPT,
    WRITER_SYSTEM_PROMPT,
    prompt_continue,
    prompt_expand,
    prompt_rewrite,
    prompt_summarize,
)

logger = logging.getLogger(__name__)


class AICompletion:
    """High-level completion operations for writing assistance."""

    def __init__(self, provider: AIProvider) -> None:
        self._provider = provider

    @property
    def provider(self) -> AIProvider:
        return self._provider

    def complete(self, text_before: str, *, style: str = "") -> str:
        """Continue writing from the cursor position."""
        prompt = prompt_continue(text_before, style=style)
        return self._provider.complete(
            prompt, system=WRITER_SYSTEM_PROMPT
        )

    async def stream_complete(
        self, text_before: str, *, style: str = ""
    ) -> AsyncIterator[str]:
        """Stream continuation from cursor position."""
        prompt = prompt_continue(text_before, style=style)
        async for chunk in self._provider.stream_complete(
            prompt, system=WRITER_SYSTEM_PROMPT
        ):
            yield chunk

    def rewrite(
        self, text: str, *, instruction: str = ""
    ) -> str:
        """Rewrite selected text with optional instruction."""
        prompt = prompt_rewrite(text, instruction=instruction)
        return self._provider.complete(
            prompt, system=EDITOR_SYSTEM_PROMPT
        )

    def expand(
        self, text: str, *, instruction: str = ""
    ) -> str:
        """Expand selected text with more detail."""
        prompt = prompt_expand(text, instruction=instruction)
        return self._provider.complete(
            prompt, system=WRITER_SYSTEM_PROMPT
        )

    def summarize(
        self, text: str, *, length: str = "short"
    ) -> str:
        """Summarize selected text."""
        prompt = prompt_summarize(text, length=length)
        return self._provider.complete(
            prompt, system=EDITOR_SYSTEM_PROMPT
        )
