import pytest
from pathlib import Path

from adrlib import AdrError, parse_frontmatter
from create_adr import create_adr

TEMPLATE = (
    "---\n"
    'adr: "{{ADR}}"\n'
    'title: "{{TITLE}}"\n'
    "status: Proposed\n"
    "date: {{DATE}}\n"
    "deciders:\n"
    "{{DECIDERS}}\n"
    "supersedes: null\n"
    "superseded_by: null\n"
    "---\n"
    "\n"
    "# ADR-{{ADR}}: {{TITLE}}\n"
    "\n"
    "## 関連ドキュメント\n"
    "\n"
    "- spec: {{SPEC}}\n"
)


@pytest.fixture
def adr_dir(tmp_path: Path) -> Path:
    templates = tmp_path / "_templates"
    templates.mkdir()
    (templates / "adr_template.md").write_text(TEMPLATE, encoding="utf-8")
    return tmp_path


def test_create_adr_writes_numbered_file(adr_dir: Path) -> None:
    path = create_adr(
        adr_dir=adr_dir,
        title="2 層モデルを採用する",
        slug="two-layer-model",
        deciders=["driller"],
        spec="docs/superpowers/specs/2026-05-16-adr-skills-design.md",
        date="2026-05-16",
    )
    assert path == adr_dir / "0001-two-layer-model.md"
    fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    assert fm.adr == "0001"
    assert fm.title == "2 層モデルを採用する"
    assert fm.status == "Proposed"
    assert fm.deciders == ["driller"]
    assert "docs/superpowers/specs/2026-05-16-adr-skills-design.md" in body


def test_create_adr_increments_number(adr_dir: Path) -> None:
    (adr_dir / "0001-x.md").write_text("placeholder", encoding="utf-8")
    path = create_adr(
        adr_dir=adr_dir,
        title="次の決定",
        slug="next-one",
        deciders=["driller"],
        spec=None,
        date="2026-05-16",
    )
    assert path.name == "0002-next-one.md"


def test_create_adr_rejects_bad_slug(adr_dir: Path) -> None:
    with pytest.raises(AdrError):
        create_adr(
            adr_dir=adr_dir,
            title="X",
            slug="Bad_Slug",
            deciders=["driller"],
            spec=None,
            date="2026-05-16",
        )


def test_create_adr_rejects_missing_template(tmp_path: Path) -> None:
    with pytest.raises(AdrError):
        create_adr(
            adr_dir=tmp_path,
            title="X",
            slug="x",
            deciders=["driller"],
            spec=None,
            date="2026-05-16",
        )
