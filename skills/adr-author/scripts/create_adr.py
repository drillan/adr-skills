"""ADR ファイルを雛形から生成する（第 1 層スクリプト）。"""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path

from adrlib import SLUG_RE, AdrError, next_number


def create_adr(
    *,
    adr_dir: Path,
    title: str,
    slug: str,
    deciders: list[str],
    spec: str | None,
    date: str,
) -> Path:
    """`adr_dir` に新規 ADR ファイルを作成し、そのパスを返す。"""
    if not SLUG_RE.match(slug):
        raise AdrError(f"slug は [a-z0-9-]+ である必要があります: {slug!r}")
    if not deciders:
        raise AdrError("deciders を 1 つ以上指定してください。")
    template_path = adr_dir / "_templates" / "adr_template.md"
    if not template_path.is_file():
        raise AdrError(f"テンプレートが見つかりません: {template_path}")
    number = next_number(adr_dir)
    out_path = adr_dir / f"{number}-{slug}.md"
    if out_path.exists():
        raise AdrError(f"既に存在します: {out_path}")
    text = template_path.read_text(encoding="utf-8")
    text = (
        text.replace("{{ADR}}", number)
        .replace("{{TITLE}}", title)
        .replace("{{DATE}}", date)
        .replace("{{DECIDERS}}", "\n".join(f"  - {d}" for d in deciders))
        .replace("{{SPEC}}", spec if spec else "なし")
    )
    out_path.write_text(text, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="新規 ADR を生成する。")
    parser.add_argument("--adr-dir", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--decider", required=True, action="append", dest="deciders")
    parser.add_argument("--spec", default=None)
    parser.add_argument("--date", default=datetime.date.today().isoformat())
    args = parser.parse_args()
    path = create_adr(
        adr_dir=args.adr_dir,
        title=args.title,
        slug=args.slug,
        deciders=args.deciders,
        spec=args.spec,
        date=args.date,
    )
    print(path)


if __name__ == "__main__":
    main()
