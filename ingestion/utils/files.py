"""File helpers shared by the generators and loaders."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

BATCH_ID_PATTERN = re.compile(r"^B\d{6}$")
_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class FileInfo:
    """Facts about a written file; later stored in the file registry."""

    path: Path
    record_count: int
    size_bytes: int
    sha256: str


def validate_batch_id(batch_id: str) -> str:
    """Batch IDs look like B000000 (initial load) and B000001, B000002, ..."""
    if not BATCH_ID_PATTERN.match(batch_id):
        raise ValueError(f"Invalid batch id {batch_id!r}; expected B followed by 6 digits")
    return batch_id


def landing_path(root: Path, entity: str, kind: str, batch_id: str, extension: str = "csv") -> Path:
    """data/landing/<entity>/<kind>/<entity>_<batch_id>.<extension>"""
    validate_batch_id(batch_id)
    return root / entity / kind / f"{entity}_{batch_id}.{extension}"


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(frame: pd.DataFrame, path: Path) -> FileInfo:
    """Write a UTF-8, LF-terminated CSV so identical data gives identical bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")
    return FileInfo(
        path=path,
        record_count=len(frame),
        size_bytes=path.stat().st_size,
        sha256=sha256_of_file(path),
    )
