from pathlib import Path

from check_adr import find_unrecorded_specs


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_find_unrecorded_specs_reports_missing(tmp_path: Path) -> None:
    adr_dir = tmp_path / "adr"
    specs_dir = tmp_path / "specs"
    _write(specs_dir / "2026-01-01-alpha-design.md", "# alpha")
    _write(specs_dir / "2026-02-02-beta-design.md", "# beta")
    _write(
        adr_dir / "0001-a.md",
        "# ADR\n- spec: docs/superpowers/specs/2026-01-01-alpha-design.md\n",
    )
    unrecorded = find_unrecorded_specs(adr_dir=adr_dir, specs_dir=specs_dir)
    assert unrecorded == [specs_dir / "2026-02-02-beta-design.md"]


def test_find_unrecorded_specs_empty_when_all_recorded(tmp_path: Path) -> None:
    adr_dir = tmp_path / "adr"
    specs_dir = tmp_path / "specs"
    _write(specs_dir / "2026-01-01-alpha-design.md", "# alpha")
    _write(
        adr_dir / "0001-a.md",
        "# ADR\n- spec: docs/superpowers/specs/2026-01-01-alpha-design.md\n",
    )
    assert find_unrecorded_specs(adr_dir=adr_dir, specs_dir=specs_dir) == []
