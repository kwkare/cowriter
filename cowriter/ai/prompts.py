"""
CoWriter – AI Prompt Templates
==============================
Writing prompt templates for various AI-assisted writing tasks.
"""

from __future__ import annotations

# System prompt for writing assistance
WRITER_SYSTEM_PROMPT = """You are an AI writing assistant integrated into a novel writing tool.
Your role is to help the author with their creative writing project.
Be supportive, offer constructive suggestions, and respect the author's voice and style.
Write in the same language as the surrounding text."""

# System prompt for editing/rewriting
EDITOR_SYSTEM_PROMPT = """You are an AI editor assistant integrated into a novel writing tool.
Your role is to help improve the author's text while preserving their voice.
Focus on clarity, flow, grammar, and style consistency.
Provide suggestions rather than making arbitrary changes."""


def prompt_continue(text_before: str, *, style: str = "") -> str:
    """Prompt for continuing text from cursor position."""
    style_hint = f" Write in a {style} style." if style else ""
    return (
        f"I'm writing a novel and need to continue from where I left off."
        f"{style_hint}\n\n"
        f"Here's the text before the cursor:\n\n{text_before}\n\n"
        f"Please continue writing the next part naturally, matching the tone and style above."
    )


def prompt_rewrite(text: str, *, instruction: str = "") -> str:
    """Prompt for rewriting selected text."""
    instr = f" {instruction}" if instruction else " improve the flow, clarity, and impact."
    return (
        f"Please rewrite the following text to{instr}\n\n"
        f"---\n{text}\n---\n\n"
        f"Keep the same tone and voice. Return only the rewritten text."
    )


def prompt_expand(text: str, *, instruction: str = "") -> str:
    """Prompt for expanding selected text with more detail."""
    instr = f" {instruction}" if instruction else " add more descriptive detail, sensory information, and depth."
    return (
        f"Please expand the following text to{instr}\n\n"
        f"---\n{text}\n---\n\n"
        f"Keep the same tone and voice. Return only the expanded text."
    )


def prompt_summarize(text: str, *, length: str = "short") -> str:
    """Prompt for summarizing text."""
    return (
        f"Please provide a {length} summary of the following text:\n\n"
        f"---\n{text}\n---\n\n"
        f"Return only the summary."
    )


def prompt_brainstorm(context: str, *, topic: str = "") -> str:
    """Prompt for brainstorming ideas."""
    topic_hint = f" about {topic}" if topic else ""
    return (
        f"I'm working on a novel and need ideas{topic_hint}.\n\n"
        f"Here's the context:\n{context}\n\n"
        f"Please give me creative suggestions and possibilities to explore."
    )


def prompt_translate(text: str, target_lang: str) -> str:
    """Prompt for translating text."""
    return (
        f"Please translate the following text into {target_lang}.\n\n"
        f"---\n{text}\n---\n\n"
        f"Return only the translation. Preserve any formatting or special syntax."
    )


def prompt_chat(context: str, message: str) -> str:
    """Prompt for general chat with writing context."""
    if context:
        return (
            f"I'm writing a novel. Here's the current context:\n\n"
            f"{context}\n\n"
            f"My question: {message}"
        )
    return message
