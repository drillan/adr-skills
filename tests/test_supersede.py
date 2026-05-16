import pytest
from pathlib import Path

from adrlib import AdrError, parse_frontmatter
from supersede import supersede


def _adr(number: str, status: str = "Accepted") -> str:
    return (
        "---\n"
        f'adr: "{number}"\n'
        'title: "X"\n'
        f"status: {status}\n"
        "date: 2026-05-16\n"
        "deciders:\n"
        "  - driller\n"
        "supersedes: null\n"
        "superseded_by: null\n"
        "---\n"
        "\n"
        f"# ADR-{number}: X\n"
    )


@pytest.fixture
def adr_dir(tmp_path: Path) -> Path:
    (tmp_path / "0001-old.md").write_text(_adr("0001"), encoding="utf-8")
    (tmp_path / "0002-new.md").write_text(_adr("0002", "Proposed"), encoding="utf-8")
    return tmp_path


def test_supersede_links_both_adrs(adr_dir: Path) -> None:
    supersede(adr_dir=adr_dir, number="0001", by="0002")
    old, _ = parse_frontmatter((adr_dir / "0001-old.md").read_text(encoding="utf-8"))
    new, _ = parse_frontmatter((adr_dir / "0002-new.md").read_text(encoding="utf-8"))
    assert old.status == "Superseded"
    assert old.superseded_by == "0002"
    assert new.supersedes == "0001"


def test_supersede_keeps_old_file(adr_dir: Path) -> None:
    supersede(adr_dir=adr_dir, number="0001", by="0002")
    assert (adr_dir / "0001-old.md").exists()


def test_supersede_rejects_already_superseded(adr_dir: Path) -> None:
    supersede(adr_dir=adr_dir, number="0001", by="0002")
    with pytest.raises(AdrError):
        supersede(adr_dir=adr_dir, number="0001", by="0002")


def test_supersede_rejects_missing_adr(adr_dir: Path) -> None:
    with pytest.raises(AdrError):
        supersede(adr_dir=adr_dir, number="0001", by="0099")


def test_supersede_rejects_self_supersede(adr_dir: Path) -> None:
    with pytest.raises(AdrError):
        supersede(adr_dir=adr_dir, number="0001", by="0001")


def test_supersede_rejects_missing_old_adr(adr_dir: Path) -> None:
    with pytest.raises(AdrError):
        supersede(adr_dir=adr_dir, number="0099", by="0002")
