"""Abstract base class for file converters.

Converters must implement:
- convert(input_path: Path) -> str: Convert file to markdown string
- supported_extensions -> List[str]: List of supported file extensions (e.g., [".pdf", ".docx"])
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class BaseConverter(ABC):
    """Abstract interface for file-to-markdown converters."""

    @abstractmethod
    def convert(self, input_path: Path) -> str:
        """Convert the input file to markdown format.

        Args:
            input_path: Path to the input file to convert.

        Returns:
            Markdown content as a string.

        Raises:
            FileNotFoundError: If the input file does not exist.
            ValueError: If the file format is not supported.
        """
        ...

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions.

        Returns:
            List of file extensions this converter handles (e.g., [".pdf", ".docx"]).
            Include the leading dot.
        """
        ...