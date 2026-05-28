from pathlib import Path

import pytest
from agentbox.models import LibraryItem, RenderTarget
from agentbox.render import TemplateRenderer
from agentbox.storage import load_manifest, save_manifest
from jinja2 import TemplateNotFound


def test_save_and_load_manifest_roundtrip(tmp_path: Path) -> None:
    item = LibraryItem(
        id="example-item",
        type="agent",
        name="Example Item",
        tags=["alpha", "beta"],
        targets=["codex"],
        renders=[RenderTarget(target="codex", render_as="AGENTS.md")],
        data={"body": "hello"},
    )
    manifest_path = tmp_path / "manifest.json"

    save_manifest(item, manifest_path)
    loaded = load_manifest(manifest_path)

    assert loaded.id == "example-item"
    assert loaded.type == "agent"
    assert loaded.name == "Example Item"
    assert loaded.tags == ["alpha", "beta"]
    assert loaded.targets == ["codex"]
    assert loaded.renders[0].render_as == "AGENTS.md"
    assert loaded.data == {"body": "hello"}
    assert loaded.root_dir == tmp_path


def test_template_renderer_renders_and_reports_missing_template(tmp_path: Path) -> None:
    template_path = tmp_path / "sample.j2"
    template_path.write_text("{{ name }} {{ data.value }}", encoding="utf-8")
    renderer = TemplateRenderer(tmp_path)
    item = LibraryItem(
        id="render-item",
        type="doc",
        name="Render Item",
        data={"value": "ok"},
    )

    assert renderer.template_exists("sample.j2")
    rendered = renderer.render("sample.j2", item)
    assert rendered == "Render Item ok\n"

    with pytest.raises(TemplateNotFound):
        renderer.render("missing.j2", item)
