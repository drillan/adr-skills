"""ADR の status を遷移させる（第 1 層スクリプト）。"""

from __future__ import annotations

import argparse
from pathlib import Path

from adrlib import AdrError, find_adr, read_adr, write_adr

ALLOWED_TRANSITIONS: frozenset[tuple[str, str]] = frozenset(
    {
        ("Proposed", "Accepted"),
        ("Proposed", "Deprecated"),
        ("Accepted", "Deprecated"),
    }
)


def set_status(*, adr_dir: Path, number: str, status: str) -> None:
    """ADR-`number` の status を `status` に遷移させる。"""
    if status == "Superseded":
        raise AdrError("Superseded への遷移は supersede.py を使ってください。")
    path = find_adr(adr_dir, number)
    fm, body = read_adr(path)
    if (fm.status, status) not in ALLOWED_TRANSITIONS:
        raise AdrError(f"許可されない遷移です: {fm.status} -> {status}")
    fm.status = status
    write_adr(path, fm, body)


def main() -> None:
    parser = argparse.ArgumentParser(description="ADR の status を遷移させる。")
    parser.add_argument("--adr-dir", required=True, type=Path)
    parser.add_argument("--number", required=True)
    parser.add_argument("--status", required=True)
    args = parser.parse_args()
    set_status(adr_dir=args.adr_dir, number=args.number, status=args.status)
    print(f"ADR-{args.number} -> {args.status}")


if __name__ == "__main__":
    main()
