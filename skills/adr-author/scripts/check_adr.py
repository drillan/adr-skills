"""spec と ADR の対応を点検する（第 1 層スクリプト）。生成は行わない。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def find_unrecorded_specs(*, adr_dir: Path, specs_dir: Path) -> list[Path]:
    """どの ADR からも参照されていない design spec を返す。"""
    referenced: set[str] = set()
    if adr_dir.is_dir():
        for adr in adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md"):
            text = adr.read_text(encoding="utf-8")
            for spec in specs_dir.glob("*-design.md"):
                if spec.name in text:
                    referenced.add(spec.name)
    unrecorded = [
        spec
        for spec in sorted(specs_dir.glob("*-design.md"))
        if spec.name not in referenced
    ]
    return unrecorded


def main() -> None:
    parser = argparse.ArgumentParser(description="spec と ADR の対応を点検する。")
    parser.add_argument("--adr-dir", required=True, type=Path)
    parser.add_argument("--specs-dir", required=True, type=Path)
    args = parser.parse_args()
    unrecorded = find_unrecorded_specs(adr_dir=args.adr_dir, specs_dir=args.specs_dir)
    if unrecorded:
        print("ADR 未記録の spec:")
        for spec in unrecorded:
            print(f"  - {spec}")
        sys.exit(1)
    print("すべての spec が ADR に対応しています。")


if __name__ == "__main__":
    main()
