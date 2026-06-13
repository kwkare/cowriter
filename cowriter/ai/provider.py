"""
CoWriter – AI Provider Abstraction
===================================
Abstract interface for AI model providers (OpenAI, Anthropic, Ollama, etc.).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import AsyncIterator, Protocol

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI model providers."""

    @abstractmethod
    async def complete(
        self, prompt: str, *, system: str | None = None, **kwargs: object
    ) -> str:
        """Send a completion request and return the full response."""
        ...

    @abstractmethod
    async def stream_complete(
        self, prompt: str, *, system: str | None = None, **kwargs: object
    ) -> AsyncIterator[str]:
        """Send a completion request and stream the response chunks."""
        ...

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        system: str | None = None,
        **kwargs: object,
    ) -> str:
        """Send a chat conversation and return the full response."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the current model identifier."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the human-readable provider name."""
        ...


class OpenAIProvider(AIProvider):
    """OpenAI-compatible API provider (GPT-4o, GPT-4, etc.)."""

    def __init__(
        self,
        api_key: str = "",
        model: str = "gpt-4o",
        base_url: str = "https://api.openai.com/v1",
        **kwargs: object,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._kwargs = kwargs
        logger.info("OpenAI provider initialized with model: %s", model)

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    async def complete(
        self, prompt: str, *, system: str | None = None, **kwargs: object
    ) -> str:
        """Send prompt to OpenAI-compatible API and return response."""
        import httpx

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, object] = {
            "model": self._model,
            "messages": messages,
            **self._kwargs,
            **kwargs,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return str(data["choices"][0]["message"]["content"])

    async def stream_complete(
        self, prompt: str, *, system: str | None = None, **kwargs: object
    ) -> AsyncIterator[str]:
        """Stream response from OpenAI-compatible API."""
        import httpx

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, object] = {
            "model": self._model,
            "messages": messages,
            "stream": True,
            **self._kwargs,
            **kwargs,
        }

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk.strip() == "[DONE]":
                            break
                        try:
                            import json
                            data = json.loads(chunk)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            if content := delta.get("content"):
                                yield content
                        except json.JSONDecodeError:
                            continue

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        system: str | None = None,
        **kwargs: object,
    ) -> str:
        """Send chat messages and return response."""
        import httpx

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        full_messages: list[dict[str, str]] = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        payload: dict[str, object] = {
            "model": self._model,
            "messages": full_messages,
            **self._kwargs,
            **kwargs,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return str(data["choices"][0]["message"]["content"])

    @classmethod
    def from_settings(cls, settings: dict[str, object]) -> OpenAIProvider:
        """Create provider from a settings dictionary."""
        return cls(
            api_key=str(settings.get("api_key", "")),
            model=str(settings.get("model", "gpt-4o")),
            base_url=str(settings.get("base_url", "https://api.openai.com/v1")),
        )


class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider."""

    def __init__(
        self,
        api_key: str = "",
        model: str = "claude-3-5-sonnet-20241022",
        **kwargs: object,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._kwargs = kwargs
        logger.info("Anthropic provider initialized with model: %s", model)

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def provider_name(self) -> str:
        return "Anthropic"

    async def complete(
        self, prompt: str, *, system: str | None = None, **kwargs: object
    ) -> str:
        """Send prompt to Anthropic API."""
        import httpx

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload: dict[str, object] = {
            "model": self._model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
            **self._kwargs,
            **kwargs,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return str(data["content"][0]["text"])

    async def stream_complete(
        self, prompt: str, *, system: str | None = None, **kwargs: object
    ) -> AsyncIterator[str]:
        """Stream response from Anthropic API."""
        import httpx

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload: dict[str, object] = {
            "model": self._model,
            "max_tokens": 4096,
            "stream": True,
            "messages": [{"role": "user", "content": prompt}],
            **self._kwargs,
            **kwargs,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=120.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        try:
                            import json
                            data = json.loads(chunk)
                            if data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})
                                if text := delta.get("text"):
                                    yield text
                        except json.JSONDecodeError:
                            continue

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        system: str | None = None,
        **kwargs: object,
    ) -> str:
        """Send chat messages to Anthropic API."""
        import httpx

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload: dict[str, object] = {
            "model": self._model,
            "max_tokens": 4096,
            "messages": messages,
            **self._kwargs,
            **kwargs,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return str(data["content"][0]["text"])

    @classmethod
    def from_settings(cls, settings: dict[str, object]) -> AnthropicProvider:
        """Create provider from a settings dictionary."""
        return cls(
            api_key=str(settings.get("api_key", "")),
            model=str(settings.get("model", "claude-3-5-sonnet-20241022")),
        )


class OllamaProvider(AIProvider):
    """Local Ollama provider for running models locally."""

    def __init__(
        self,
        model: str = "qwen2.5:7b",
        base_url: str = "http://localhost:11434",
        **kwargs: object,
    ) -> None:
        self._model = model
        self._base_url = base_url
        self._kwargs = kwargs
        logger.info("Ollama provider initialized with model: %s", model)

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def provider_name(self) -> str:
        return "Ollama"

    async def complete(
        self, prompt: str, *, system: str | None = None, **kwargs: object
    ) -> str:
        """Send prompt to local Ollama instance."""
        import httpx

        payload: dict[str, object] = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            **self._kwargs,
            **kwargs,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return str(data.get("response", ""))

    async def stream_complete(
        self, prompt: str, *, system: str | None = None, **kwargs: object
    ) -> AsyncIterator[str]:
        """Stream response from local Ollama instance."""
        import httpx
        import json

        payload: dict[str, object] = {
            "model": self._model,
            "prompt": prompt,
            "stream": True,
            **self._kwargs,
            **kwargs,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/api/generate",
                json=payload,
                timeout=300.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if text := data.get("response"):
                                yield text
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        system: str | None = None,
        **kwargs: object,
    ) -> str:
        """Send chat messages to local Ollama instance."""
        import httpx

        payload: dict[str, object] = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            **self._kwargs,
            **kwargs,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/api/chat",
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return str(data["message"]["content"])

    @classmethod
    def from_settings(cls, settings: dict[str, object]) -> OllamaProvider:
        """Create provider from a settings dictionary."""
        return cls(
            model=str(settings.get("model", "qwen2.5:7b")),
            base_url=str(settings.get("base_url", "http://localhost:11434")),
        )


def create_provider(provider_type: str, settings: dict[str, object]) -> AIProvider:
    """Factory function to create an AI provider from type and settings."""
    providers = {
        "openai": OpenAIProvider.from_settings,
        "anthropic": AnthropicProvider.from_settings,
        "ollama": OllamaProvider.from_settings,
    }
    if factory := providers.get(provider_type.lower()):
        return factory(settings)
    raise ValueError(f"Unknown provider type: {provider_type}")
