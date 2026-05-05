"""Fast lane converter using markitdown subprocess."""

import subprocess
import sys
from pathlib import Path


class FastLane:
    """Wrapper for markitdown subprocess conversion."""

    def convert(self, input_path: Path, output_path: Path) -> bool:
        """
        Run markitdown to convert input_path to output_path.

        Args:
            input_path: Path to input file
            output_path: Path to output markdown file

        Returns:
            True on success, False on failure
        """
        if not self._check_markitdown_available():
            return False

        try:
            result = subprocess.run(
                ["markitdown", str(input_path), "-o", str(output_path)],
                capture_output=True,
                timeout=60,
            )
            if result.returncode == 0:
                return True
            else:
                print(f"markitdown conversion failed: {result.stderr}", file=sys.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("markitdown timed out after 60 seconds", file=sys.stderr)
            return False
        except FileNotFoundError:
            print("markitdown not found in PATH", file=sys.stderr)
            return False

    def _check_markitdown_available(self) -> bool:
        """Check if markitdown is available in PATH."""
        try:
            subprocess.run(
                ["markitdown", "--version"],
                capture_output=True,
                timeout=10,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False