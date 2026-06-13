# -*- coding: utf-8 -*-
"""CoWriter - AI Completion Tests."""
from __future__ import annotations

from unittest.mock import MagicMock

from cowriter.ai.completion import AICompletion
from cowriter.ai.provider import OpenAIProvider


class TestAICompletion:

    def _run_async(self, coro):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def test_complete_calls_provider(self):
        provider = MagicMock(spec=OpenAIProvider)
        provider.complete.return_value = "Continued text."
        completion = AICompletion(provider)
        result = completion.complete("Once upon a time")
        assert result == "Continued text."
        provider.complete.assert_called_once()

    def test_complete_passes_style(self):
        provider = MagicMock(spec=OpenAIProvider)
        provider.complete.return_value = "X"
        completion = AICompletion(provider)
        completion.complete("Text", style="poetic")
        args = provider.complete.call_args[0][0]
        assert "poetic" in args

    def test_rewrite(self):
        provider = MagicMock(spec=OpenAIProvider)
        provider.complete.return_value = "Rewritten"
        completion = AICompletion(provider)
        result = completion.rewrite("Old text")
        assert result == "Rewritten"

    def test_rewrite_with_instruction(self):
        provider = MagicMock(spec=OpenAIProvider)
        provider.complete.return_value = "X"
        completion = AICompletion(provider)
        completion.rewrite("Text", instruction="make it shorter")
        args = provider.complete.call_args[0][0]
        assert "make it shorter" in args

    def test_expand(self):
        provider = MagicMock(spec=OpenAIProvider)
        provider.complete.return_value = "Expanded text."
        completion = AICompletion(provider)
        result = completion.expand("Short")
        assert result == "Expanded text."

    def test_summarize(self):
        provider = MagicMock(spec=OpenAIProvider)
        provider.complete.return_value = "Summary."
        completion = AICompletion(provider)
        result = completion.summarize("Long text", length="short")
        assert result == "Summary."

    def test_provider_property(self):
        provider = MagicMock(spec=OpenAIProvider)
        completion = AICompletion(provider)
        assert completion.provider is provider

    def test_stream_complete(self):
        provider = MagicMock(spec=OpenAIProvider)
        async def mock_stream(*a, **kw):
            yield "Chunk1"
            yield "Chunk2"
        provider.stream_complete = mock_stream
        completion = AICompletion(provider)
        collected = []
        async def run():
            async for chunk in completion.stream_complete("Hi"):
                collected.append(chunk)
        self._run_async(run())
        assert collected == ["Chunk1", "Chunk2"]

