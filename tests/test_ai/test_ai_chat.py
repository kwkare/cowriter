# -*- coding: utf-8 -*-
"""CoWriter - AI Chat Session Tests."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from cowriter.ai.chat import AIChatSession
from cowriter.ai.provider import OpenAIProvider


class TestAIChatSession:

    def _run_async(self, coro):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def test_init_empty(self):
        provider = MagicMock(spec=OpenAIProvider)
        session = AIChatSession(provider)
        assert session.messages == []
        assert session.context == ""

    def test_add_message(self):
        provider = MagicMock(spec=OpenAIProvider)
        session = AIChatSession(provider)
        session.add_message("user", "Hello")
        assert session.messages == [{"role": "user", "content": "Hello"}]

    def test_set_context(self):
        provider = MagicMock(spec=OpenAIProvider)
        session = AIChatSession(provider)
        session.set_context("Story context here")
        assert session.context == "Story context here"

    def test_send_without_context(self):
        provider = MagicMock(spec=OpenAIProvider)
        provider.chat = AsyncMock(return_value="AI response text")
        session = AIChatSession(provider)
        result = self._run_async(session.send("Hello"))
        assert result == "AI response text"
        assert len(session.messages) == 2
        assert session.messages[0]["role"] == "user"
        assert session.messages[1]["role"] == "assistant"

    def test_send_with_context(self):
        provider = MagicMock(spec=OpenAIProvider)
        provider.chat = AsyncMock(return_value="Reply")
        session = AIChatSession(provider)
        session.set_context("Story context")
        self._run_async(session.send("What next?"))
        prompt = session.messages[0]["content"]
        assert "Story context" in prompt

    def test_stream_send(self):
        provider = MagicMock(spec=OpenAIProvider)
        async def mock_stream(*a, **kw):
            yield "Hello "
            yield "world"
        provider.stream_chat = mock_stream
        session = AIChatSession(provider)
        collected = []
        async def run():
            async for chunk in session.stream_send("Hi"):
                collected.append(chunk)
        self._run_async(run())
        assert "".join(collected) == "Hello world"
        assert len(session.messages) == 2
        assert session.messages[1]["content"] == "Hello world"

    def test_clear(self):
        provider = MagicMock(spec=OpenAIProvider)
        session = AIChatSession(provider)
        session.add_message("user", "Hi")
        session.set_context("Some context")
        session.clear()
        assert session.messages == []
        assert session.context == ""

    def test_messages_returns_copy(self):
        provider = MagicMock(spec=OpenAIProvider)
        session = AIChatSession(provider)
        session.add_message("user", "Hi")
        msgs = session.messages
        msgs.append({"role": "user", "content": "extra"})
        assert len(session.messages) == 1

