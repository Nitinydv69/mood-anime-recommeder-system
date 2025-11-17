# scripts/storage.py
"""
Simple text-based storage for likes and dislikes shared by CLI and Streamlit.
Each line in the file is just an anime title (no headers).
"""

from pathlib import Path

DATA_DIR = Path("data")
LIKES_FILE = DATA_DIR / "likes.txt"
DISLIKES_FILE = DATA_DIR / "dislikes.txt"


def ensure_data_dir() -> None:
    """Make sure data/ exists."""
    DATA_DIR.mkdir(exist_ok=True)


def _append(path: Path, title: str) -> None:
    """Append a single title to a file (newline separated)."""
    ensure_data_dir()
    with path.open("a", encoding="utf-8") as f:
        f.write(title.strip() + "\n")


def _load(path: Path) -> set[str]:
    """Load all titles from a file into a set. Ignore empty lines."""
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def like(title: str) -> None:
    """Add title to likes."""
    _append(LIKES_FILE, title)


def dislike(title: str) -> None:
    """Add title to dislikes."""
    _append(DISLIKES_FILE, title)


def load_likes() -> set[str]:
    return _load(LIKES_FILE)


def load_dislikes() -> set[str]:
    return _load(DISLIKES_FILE)
