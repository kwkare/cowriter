# -*- coding: utf-8 -*-
"""CoWriter - AI Provider Tests."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

from cowriter.ai.provider import (
    AnthropicProvider, OllamaProvider, OpenAIProvider, create_provider,
)


class TestOpenAIProvider:

    def test_provider_name(self):
        p = OpenAIProvider(api_key='test')
        assert p.provider_name == 'OpenAI'

    def test_model_name(self):
        p = OpenAIProvider(api_key='test', model='gpt-4o-mini')
        assert p.model_name == 'gpt-4o-mini'

    @patch('httpx.Client')
    def test_complete_success(self, mock_cls):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {'choices': [{'message': {'content': 'Hello'}}]}
        mock_cli = MagicMock()
        mock_cli.post.return_value = mock_resp
        mock_cls.return_value.__enter__.return_value = mock_cli
        p = OpenAIProvider(api_key='sk-test')
        assert p.complete('Say hello') == 'Hello'

    @patch('httpx.Client')
    def test_complete_with_system(self, mock_cls):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {'choices': [{'message': {'content': 'OK'}}]}
        mock_cli = MagicMock()
        mock_cli.post.return_value = mock_resp
        mock_cls.return_value.__enter__.return_value = mock_cli
        p = OpenAIProvider(api_key='sk-test')
        p.complete('Hi', system='Be helpful')
        _, kwargs = mock_cli.post.call_args
        msgs = kwargs['json']['messages']
        assert msgs[0] == {'role': 'system', 'content': 'Be helpful'}

    @patch('httpx.AsyncClient')
    def test_chat_success(self, mock_cls):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {'choices': [{'message': {'content': 'Reply'}}]}
        mock_cli = AsyncMock()
        mock_cli.post = AsyncMock(return_value=mock_resp)
        mock_cls.return_value.__aenter__.return_value = mock_cli
        p = OpenAIProvider(api_key='sk-test')
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(p.chat([{'role': 'user', 'content': 'Hi'}]))
        finally:
            loop.close()
        assert result == 'Reply'

    @patch('httpx.AsyncClient')
    def test_stream_complete(self, mock_cls):
        chunks = [
            'data: ' + json.dumps({'choices': [{'delta': {'content': 'Hello '}}]}),
            'data: ' + json.dumps({'choices': [{'delta': {'content': 'world'}}]}),
            'data: [DONE]',
        ]
        async def mock_aiter():
            for c in chunks:
                yield c
        mock_resp = MagicMock()
        mock_resp.aiter_lines = mock_aiter
        stream_ctx = MagicMock()
        stream_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        stream_ctx.__aexit__ = AsyncMock(return_value=None)
        client = MagicMock()
        client.stream = MagicMock(return_value=stream_ctx)
        mock_cls.return_value.__aenter__.return_value = client
        p = OpenAIProvider(api_key='sk-test')
        collected = []
        async def run():
            async for chunk in p.stream_complete('Hi'):
                collected.append(chunk)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run())
        finally:
            loop.close()
        assert ''.join(collected) == 'Hello world'

    def test_create_from_settings(self):
        p = OpenAIProvider.from_settings({
            'api_key': 'sk-factory', 'model': 'gpt-4-turbo',
            'base_url': 'https://custom.example.com',
        })
        assert p._api_key == 'sk-factory'


class TestAnthropicProvider:

    def test_provider_name(self):
        p = AnthropicProvider(api_key='test')
        assert p.provider_name == 'Anthropic'

    @patch('httpx.Client')
    def test_complete_success(self, mock_cls):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {'content': [{'text': 'Anthropic response'}]}
        mock_cli = MagicMock()
        mock_cli.post.return_value = mock_resp
        mock_cls.return_value.__enter__.return_value = mock_cli
        p = AnthropicProvider(api_key='sk-ant-test')
        assert p.complete('Tell me') == 'Anthropic response'


class TestOllamaProvider:

    def test_provider_name(self):
        assert OllamaProvider().provider_name == 'Ollama'

    @patch('httpx.Client')
    def test_complete_success(self, mock_cls):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {'response': 'Ollama reply'}
        mock_cli = MagicMock()
        mock_cli.post.return_value = mock_resp
        mock_cls.return_value.__enter__.return_value = mock_cli
        p = OllamaProvider(model='llama3.1:8b')
        assert p.complete('Hi') == 'Ollama reply'


class TestCreateProvider:

    def test_create_openai(self):
        assert isinstance(create_provider('openai', {'api_key': 'x'}), OpenAIProvider)

    def test_create_anthropic(self):
        assert isinstance(create_provider('anthropic', {'api_key': 'x'}), AnthropicProvider)

    def test_create_ollama(self):
        assert isinstance(create_provider('ollama', {}), OllamaProvider)

    def test_unknown_raises(self):
        import pytest
        with pytest.raises(ValueError, match='Unknown provider'):
            create_provider('nonexistent', {})
