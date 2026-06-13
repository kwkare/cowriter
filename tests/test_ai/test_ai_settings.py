# -*- coding: utf-8 -*-
"""CoWriter - AI Settings Tests."""

from __future__ import annotations

from cowriter.ai.settings import AISettings


class TestAISettings:

    def test_default_settings(self):
        s = AISettings()
        assert s.provider_type == "ollama"
        assert s.openai_model == "gpt-4o"
        assert s.anthropic_model == "claude-3-5-sonnet-20241022"
        assert s.ollama_model == "qwen2.5:7b"
        assert s.temperature == 0.7
        assert s.max_tokens == 2048
        assert s.enable_streaming is True
        assert s.enable_autocomplete is False

    def test_to_dict_roundtrip(self):
        orig = AISettings(
            provider_type="openai",
            openai_api_key="sk-test123",
            openai_model="gpt-4o-mini",
            openai_base_url="https://custom.example.com/v1",
            temperature=0.3,
            max_tokens=4096,
            enable_streaming=False,
            enable_autocomplete=True,
        )
        data = orig.to_dict()
        restored = AISettings.from_dict(data)
        assert restored.provider_type == "openai"
        assert restored.openai_api_key == "sk-test123"
        assert restored.openai_model == "gpt-4o-mini"
        assert restored.openai_base_url == "https://custom.example.com/v1"
        assert restored.temperature == 0.3
        assert restored.max_tokens == 4096
        assert restored.enable_streaming is False
        assert restored.enable_autocomplete is True

    def test_from_dict_partial(self):
        s = AISettings.from_dict({"provider_type": "anthropic"})
        assert s.provider_type == "anthropic"
        assert s.anthropic_api_key == ""
        assert s.anthropic_model == "claude-3-5-sonnet-20241022"
        assert s.temperature == 0.7

    def test_from_dict_empty(self):
        s = AISettings.from_dict({})
        assert s.provider_type == "ollama"
        assert s.temperature == 0.7

    def test_get_provider_config_openai(self):
        s = AISettings(provider_type="openai", openai_api_key="sk-abc",
                        openai_model="gpt-4o", openai_base_url="https://api.openai.com/v1")
        cfg = s.get_provider_config()
        assert cfg["api_key"] == "sk-abc"
        assert cfg["model"] == "gpt-4o"
        assert cfg["base_url"] == "https://api.openai.com/v1"

    def test_get_provider_config_anthropic(self):
        s = AISettings(provider_type="anthropic",
                        anthropic_api_key="sk-ant-test",
                        anthropic_model="claude-3-opus-20240229")
        cfg = s.get_provider_config()
        assert cfg["api_key"] == "sk-ant-test"
        assert cfg["model"] == "claude-3-opus-20240229"
        assert "base_url" not in cfg

    def test_get_provider_config_ollama(self):
        s = AISettings(provider_type="ollama",
                        ollama_model="llama3.1:8b",
                        ollama_base_url="http://192.168.1.100:11434")
        cfg = s.get_provider_config()
        assert cfg["model"] == "llama3.1:8b"
        assert cfg["base_url"] == "http://192.168.1.100:11434"
        assert "api_key" not in cfg

    def test_type_coercion_on_load(self):
        s = AISettings.from_dict({"temperature": "0.5", "max_tokens": "1024",
                                   "enable_streaming": False})
        assert s.temperature == 0.5
        assert s.max_tokens == 1024
        assert s.enable_streaming is False

    def test_bool_string_is_not_coerced(self):
        # Note: bool("false") is True in Python because it's a non-empty string
        s = AISettings.from_dict({"enable_streaming": "false"})
        assert s.enable_streaming is True  # unchanged default
