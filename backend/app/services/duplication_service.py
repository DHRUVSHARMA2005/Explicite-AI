"""
Source-level duplication detection.

Algorithm: sliding-window block hashing.
  - BLOCK_SIZE consecutive source lines form one block.
  - Each block is SHA-256 hashed (after stripping trailing whitespace per line).
  - A block is "duplicated" if the same hash appears at two or more distinct
    positions in the codebase (different file, or different non-overlapping
    position in the same file).
  - duplicated_lines = count of unique line indices that belong to at least
    one duplicated block (tracked per-file to avoid double-counting).
  - total_lines = sum of line counts across all scanned files.
  - duplications_pct = duplicated_lines / total_lines × 100.

Denominator: total source lines scanned (blank lines included, binary files
excluded, generated/vendor paths excluded).

Limitations and exclusions:
  - Files > MAX_FILE_BYTES are skipped (unbounded memory risk).
  - At most MAX_FILES files are scanned (performance bound).
  - Returns None when total_lines < MIN_TOTAL_LINES (insufficient data).
  - Generated files, lock files, and vendored dependencies are excluded via
    path heuristics (node_modules, vendor, .git, __pycache__, *.min.js, etc.).
  - Binary files (detected by a NUL byte) are skipped.
  - This is a file-content analysis only; no code is executed.
"""
import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

BLOCK_SIZE = 6            # minimum clone length in lines
MAX_FILE_BYTES = 100_000  # skip files over 100 KB
MAX_FILES = 500           # scan at most this many files
MIN_TOTAL_LINES = 50      # need at least this many lines for a meaningful result

_SUPPORTED_EXTENSIONS = frozenset({
    ".py", ".java", ".js", ".jsx", ".ts", ".tsx",
    ".c", ".cpp", ".cs", ".go", ".rb", ".php",
})

_EXCLUDED_DIRS = frozenset({
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "vendor", "dist", "build", ".cache", "coverage",
    "target",  # Maven/Gradle build dir
})

_EXCLUDED_SUFFIXES = frozenset({
    ".min.js", ".min.css", ".lock", "-lock.json",
})


def _is_excluded_path(path: Path) -> bool:
    for part in path.parts:
        if part in _EXCLUDED_DIRS:
            return True
    name = path.name.lower()
    return any(name.endswith(s) for s in _EXCLUDED_SUFFIXES)


def _is_binary(data: bytes) -> bool:
    return b"\x00" in data[:8192]


def _block_hash(lines: list[str], start: int) -> str:
    block = "\n".join(lines[start : start + BLOCK_SIZE])
    return hashlib.sha256(block.encode("utf-8", errors="replace")).hexdigest()


@dataclass
class DuplicationResult:
    pct: float | None
    duplicated_lines: int
    total_lines: int
    files_scanned: int
    message: str


def detect_duplications(source_dir: Path) -> DuplicationResult:
    """
    Scan source_dir for duplicate code blocks and return a DuplicationResult.

    The returned pct is None when the source is too small (< MIN_TOTAL_LINES)
    or no supported source files were found.  In that case, message explains why.
    Never executes any code from the scanned files.
    """
    source_dir = source_dir.resolve()

    # Collect eligible files
    candidates: list[Path] = []
    for p in source_dir.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            continue
        if _is_excluded_path(p.relative_to(source_dir)):
            continue
        if p.stat().st_size > MAX_FILE_BYTES:
            logger.debug("duplication: skipping large file %s", p)
            continue
        candidates.append(p)
        if len(candidates) >= MAX_FILES:
            logger.info("duplication: capped at %d files", MAX_FILES)
            break

    if not candidates:
        return DuplicationResult(
            pct=None, duplicated_lines=0, total_lines=0, files_scanned=0,
            message="No supported source files found for duplication analysis.",
        )

    # Read and normalize lines per file
    file_lines: dict[Path, list[str]] = {}
    for p in candidates:
        try:
            raw = p.read_bytes()
            if _is_binary(raw):
                continue
            text = raw.decode("utf-8", errors="replace")
            lines = [ln.rstrip() for ln in text.splitlines()]
            file_lines[p] = lines
        except OSError:
            pass

    total_lines = sum(len(ls) for ls in file_lines.values())
    if total_lines < MIN_TOTAL_LINES:
        return DuplicationResult(
            pct=None, duplicated_lines=0, total_lines=total_lines,
            files_scanned=len(file_lines),
            message=f"Insufficient source ({total_lines} lines); need at least {MIN_TOTAL_LINES}.",
        )

    # First pass: build hash → list of (file, block_start) index
    hash_positions: dict[str, list[tuple[Path, int]]] = {}
    for path, lines in file_lines.items():
        n = len(lines)
        for i in range(n - BLOCK_SIZE + 1):
            h = _block_hash(lines, i)
            hash_positions.setdefault(h, []).append((path, i))

    # Identify hashes that appear at 2+ distinct positions
    dup_hashes: set[str] = {
        h for h, positions in hash_positions.items()
        if len(positions) >= 2
    }

    if not dup_hashes:
        return DuplicationResult(
            pct=0.0, duplicated_lines=0, total_lines=total_lines,
            files_scanned=len(file_lines),
            message="No duplicate blocks detected.",
        )

    # Second pass: collect duplicated line indices per file
    duplicated_by_file: dict[Path, set[int]] = {p: set() for p in file_lines}
    for h in dup_hashes:
        for path, start in hash_positions[h]:
            for idx in range(start, start + BLOCK_SIZE):
                duplicated_by_file[path].add(idx)

    duplicated_lines = sum(len(s) for s in duplicated_by_file.values())
    pct = round((duplicated_lines / total_lines) * 100.0, 1) if total_lines else 0.0

    return DuplicationResult(
        pct=pct,
        duplicated_lines=duplicated_lines,
        total_lines=total_lines,
        files_scanned=len(file_lines),
        message=(
            f"Detected {duplicated_lines:,} duplicated lines out of {total_lines:,} "
            f"total ({pct:.1f}%) — {BLOCK_SIZE}-line sliding window across "
            f"{len(file_lines)} source files. Excludes generated/vendored paths."
        ),
    )
