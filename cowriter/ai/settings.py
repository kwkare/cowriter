"""
CoWriter – AI Settings
======================
Configuration model for AI provider settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ProviderType = Literal["openai", "anthropic", "ollama"]


@dataclass
class AISettings:
    """Settings for the AI writing assistant."""

    # Provider selection
    provider_type: ProviderType = "ollama"

    # OpenAI / compatible settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = "https://api.openai.com/v1"

    # Anthropic settings
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Ollama (local) settings
    ollama_model: str = "qwen2.5:7b"
    ollama_base_url: str = "http://localhost:11434"

    # Generation parameters
    temperature: float = 0.7
    max_tokens: int = 2048

    # Feature toggles
    enable_streaming: bool = True
    enable_autocomplete: bool = False

    def to_dict(self) -> dict[str, object]:
        """Serialize settings to a dictionary."""
        return {
            "provider_type": self.provider_type,
            "openai_api_key": self.openai_api_key,
            "openai_model": self.openai_model,
            "openai_base_url": self.openai_base_url,
            "anthropic_api_key": self.anthropic_api_key,
            "anthropic_model": self.anthropic_model,
            "ollama_model": self.ollama_model,
            "ollama_base_url": self.ollama_base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "enable_streaming": self.enable_streaming,
            "enable_autocomplete": self.enable_autocomplete,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> AISettings:
        """Deserialize settings from a dictionary."""
        return cls(
            provider_type=str(data.get("provider_type", "ollama")),  # type: ignore
            openai_api_key=str(data.get("openai_api_key", "")),
            openai_model=str(data.get("openai_model", "gpt-4o")),
            openai_base_url=str(data.get("openai_base_url", "https://api.openai.com/v1")),
            anthropic_api_key=str(data.get("anthropic_api_key", "")),
            anthropic_model=str(data.get("anthropic_model", "claude-3-5-sonnet-20241022")),
            ollama_model=str(data.get("ollama_model", "qwen2.5:7b")),
            ollama_base_url=str(data.get("ollama_base_url", "http://localhost:11434")),
            temperature=float(data.get("temperature", 0.7)),
            max_tokens=int(data.get("max_tokens", 2048)),
            enable_streaming=bool(data.get("enable_streaming", True)),
            enable_autocomplete=bool(data.get("enable_autocomplete", False)),
        )

    def get_provider_config(self) -> dict[str, object]:
        """Get the configuration dict for the selected provider."""
        if self.provider_type == "openai":
            return {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "base_url": self.openai_base_url,
            }
        elif self.provider_type == "anthropic":
            return {
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model,
            }
        else:  # ollama
            return {
                "model": self.ollama_model,
                "base_url": self.ollama_base_url,
            }
