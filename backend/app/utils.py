"""Tiny helpers."""
import re


def message_to_text(message) -> str:
    """
    A model reply's `.content` is usually a string, but Gemini can return a
    list of content blocks. This always gives back plain text.
    """
    content = message.content
    if isinstance(content, str):
        return content
    return "".join(
        block if isinstance(block, str) else block.get("text", "")
        for block in content
    )


def make_file_name(topic: str) -> str:
    """'Quantum Computing 101!' -> 'quantum-computing-101.md'"""
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return f"{slug[:60] or 'report'}.md"
