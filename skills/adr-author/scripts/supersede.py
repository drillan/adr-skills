"""ADR の supersede 関係を設定する（第 1 層スクリプト）。"""

from __future__ import annotations

import argparse
from pathlib import Path

from adrlib import AdrError, find_adr, read_adr, write_adr


def supersede(*, adr_dir: Path, number: str, by: str) -> None:
    """ADR-`number` を ADR-`by` で supersede する。"""
    if number == by:
        raise AdrError(f"ADR-{number} は自分自身を supersede できません。")
    old_path = find_adr(adr_dir, number)
    new_path = find_adr(adr_dir, by)
    old_fm, old_body = read_adr(old_path)
    new_fm, new_body = read_adr(new_path)
    if old_fm.status == "Superseded":
        raise AdrError(f"ADR-{number} は既に Superseded です。")
    old_fm.status = "Superseded"
    old_fm.superseded_by = by
    new_fm.supersedes = number
    write_adr(old_path, old_fm, old_body)
    write_adr(new_path, new_fm, new_body)


def main() -> None:
    parser = argparse.ArgumentParser(description="ADR を supersede する。")
    parser.add_argument("--adr-dir", required=True, type=Path)
    parser.add_argument("--number", required=True)
    parser.add_argument("--by", required=True)
    args = parser.parse_args()
    supersede(adr_dir=args.adr_dir, number=args.number, by=args.by)
    print(f"ADR-{args.number} superseded by ADR-{args.by}")


if __name__ == "__main__":
    main()
