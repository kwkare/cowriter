"""
CoWriter – AI Chat
==================
Chat-based AI assistant for interactive writing help.
"""

from __future__ import annotations

import logging
from typing import AsyncIterator

from cowriter.ai.provider import AIProvider
from cowriter.ai.prompts import WRITER_SYSTEM_PROMPT, prompt_chat

logger = logging.getLogger(__name__)


class AIChatSession:
    """A single chat session with context tracking."""

    def __init__(self, provider: AIProvider) -> None:
        self._provider = provider
        self._messages: list[dict[str, str]] = []
        self._context: str = ""

    @property
    def messages(self) -> list[dict[str, str]]:
        return list(self._messages)

    @property
    def context(self) -> str:
        return self._context

    def set_context(self, context: str) -> None:
        """Set the current writing context (chapter outline, etc.)."""
        self._context = context

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the chat history."""
        self._messages.append({"role": role, "content": content})

    async def send(self, message: str) -> str:
        """Send a message and get a response."""
        context = self._context
        prompt = prompt_chat(context, message) if context else message
        self.add_message("user", prompt)
        response = await self._provider.chat(
            self._messages, system=WRITER_SYSTEM_PROMPT
        )
        self.add_message("assistant", response)
        return response

    async def stream_send(
        self, message: str
    ) -> AsyncIterator[str]:
        """Send a message and stream the response.
        Uses stream_chat to preserve multi-turn conversation history."""
        context = self._context
        prompt = prompt_chat(context, message) if context else message
        self.add_message("user", prompt)

        collected = ""
        async for chunk in self._provider.stream_chat(
            self._messages, system=WRITER_SYSTEM_PROMPT
        ):
            collected += chunk
            yield chunk

        self.add_message("assistant", collected)

    def clear(self) -> None:
        """Clear the chat history."""
        self._messages.clear()
        self._context = ""
