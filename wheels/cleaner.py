"""Regex post-processing cleaner for markdown text."""

import re


class Cleaner:
    """Cleans markdown text with regex transformations."""

    @staticmethod
    def clean(text: str) -> str:
        """
        Clean text with regex transformations.

        Removes BOM, normalizes line endings, collapses blank lines,
        and strips trailing whitespace while preserving code blocks.
        """
        # Step 1: Remove UTF-8 BOM if present
        if text.startswith('\ufeff'):
            text = text[1:]

        # Step 2: Normalize line endings (\r\n, \r -> \n)
        text = re.sub(r'\r\n|\r|\n', '\n', text)

        # Step 3: Preserve code blocks (```...```) with placeholders
        code_blocks: list[str] = []
        code_block_pattern = re.compile(r'(```[\s\S]*?```)')

        def replace_code_block(match: re.Match) -> str:
            code_blocks.append(match.group(1))
            return f'<!--CB{len(code_blocks) - 1}-->'

        text = code_block_pattern.sub(replace_code_block, text)

        # Step 4: Collapse 3+ consecutive blank lines to 2
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Step 5: Strip trailing whitespace on lines
        text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)

        # Step 6: Restore code blocks
        for i, block in enumerate(code_blocks):
            text = text.replace(f'<!--CB{i}-->', block)

        return text