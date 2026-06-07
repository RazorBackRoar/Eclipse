from __future__ import annotations

import json
from pathlib import Path

import pytest

from eclipse.catalog import (
    CATALOG,
    CATEGORIES,
    CATEGORY_IDS,
    ExportPreset,
    ExportPresetStore,
    UserTemplateStore,
    category_label,
    template_by_id,
    templates_for_category,
)


# ── CATALOG integrity ─────────────────────────────────────────────────────────────

def test_catalog_is_non_empty() -> None:
    assert len(CATALOG) > 0


def test_catalog_all_ids_are_unique() -> None:
    ids = [e.id for e in CATALOG]
    assert len(ids) == len(set(ids))


def test_catalog_all_entries_have_required_fields() -> None:
    for entry in CATALOG:
        assert entry.id
        assert entry.category
        assert entry.filename
        assert entry.display_name
        assert entry.default_content is not None


def test_catalog_categories_are_known() -> None:
    known = set(CATEGORY_IDS)
    for entry in CATALOG:
        assert entry.category in known, f"Unknown category in catalog: {entry.category}"


# ── category_label ────────────────────────────────────────────────────────────────

def test_category_label_known_id() -> None:
    assert category_label("general") == "General"
    assert category_label("python") == "Python"
    assert category_label("claude") == "Claude"


def test_category_label_unknown_returns_id() -> None:
    assert category_label("nonexistent-cat") == "nonexistent-cat"


# ── templates_for_category ────────────────────────────────────────────────────────

def test_templates_for_category_returns_matching() -> None:
    entries = templates_for_category("python")
    assert len(entries) > 0
    for e in entries:
        assert e.category == "python"


def test_templates_for_category_unknown_returns_empty() -> None:
    assert templates_for_category("not-a-real-category") == []


def test_templates_for_category_general_includes_readme() -> None:
    entries = templates_for_category("general")
    filenames = [e.filename for e in entries]
    assert "README.md" in filenames


# ── template_by_id ────────────────────────────────────────────────────────────────

def test_template_by_id_found() -> None:
    entry = template_by_id("general-readme")
    assert entry is not None
    assert entry.id == "general-readme"
    assert entry.filename == "README.md"


def test_template_by_id_not_found_returns_none() -> None:
    assert template_by_id("does-not-exist") is None


def test_template_by_id_cursor_has_folder_info() -> None:
    entry = template_by_id("cursor-cursor")
    assert entry is not None
    assert entry.hidden_folder == ".cursor"
    assert entry.normal_folder == "cursor"


# ── UserTemplateStore ─────────────────────────────────────────────────────────────

def test_user_template_store_fresh_returns_default(tmp_path: Path) -> None:
    store = UserTemplateStore(tmp_path / "edits.json")
    content = store.get_content("general-readme")
    assert content  # non-empty
    default = template_by_id("general-readme")
    assert default is not None
    assert content == default.default_content


def test_user_template_store_unknown_id_returns_empty(tmp_path: Path) -> None:
    store = UserTemplateStore(tmp_path / "edits.json")
    assert store.get_content("completely-unknown-id") == ""


def test_user_template_store_set_and_get(tmp_path: Path) -> None:
    store = UserTemplateStore(tmp_path / "edits.json")
    store.set_content("general-readme", "# My Custom README\n")
    assert store.get_content("general-readme") == "# My Custom README\n"


def test_user_template_store_is_edited(tmp_path: Path) -> None:
    store = UserTemplateStore(tmp_path / "edits.json")
    assert not store.is_edited("general-readme")
    store.set_content("general-readme", "custom content")
    assert store.is_edited("general-readme")


def test_user_template_store_reset_to_default(tmp_path: Path) -> None:
    store = UserTemplateStore(tmp_path / "edits.json")
    store.set_content("general-readme", "custom")
    store.reset_to_default("general-readme")
    assert not store.is_edited("general-readme")
    # After reset, should return the default content
    default = template_by_id("general-readme")
    assert default is not None
    assert store.get_content("general-readme") == default.default_content


def test_user_template_store_reset_nonexistent_is_noop(tmp_path: Path) -> None:
    store = UserTemplateStore(tmp_path / "edits.json")
    store.reset_to_default("nonexistent")  # should not raise


def test_user_template_store_save_and_reload(tmp_path: Path) -> None:
    path = tmp_path / "edits.json"
    store = UserTemplateStore(path)
    store.set_content("general-readme", "persisted content")

    store2 = UserTemplateStore(path)
    assert store2.get_content("general-readme") == "persisted content"


def test_user_template_store_handles_corrupt_json(tmp_path: Path) -> None:
    path = tmp_path / "edits.json"
    path.write_text("{ not valid json", encoding="utf-8")
    store = UserTemplateStore(path)
    # Should fall back gracefully to defaults
    assert store.get_content("general-readme")


def test_user_template_store_backup_retention(tmp_path: Path) -> None:
    """Saving more than 5 times should only keep 5 backups."""
    import time
    from unittest.mock import patch

    from eclipse import paths

    backups_dir = tmp_path / "backups"

    with patch.object(paths, "backups_root", return_value=backups_dir):
        path = tmp_path / "edits.json"
        store = UserTemplateStore(path)

        for i in range(8):
            store.set_content("general-readme", f"content-{i}")
            time.sleep(0.01)  # ensure distinct timestamps

        backups = list(backups_dir.glob("user_templates_*.json"))
        assert len(backups) <= 5


# ── ExportPresetStore ─────────────────────────────────────────────────────────────

def test_export_preset_store_save_and_retrieve(tmp_path: Path) -> None:
    path = tmp_path / "presets.json"
    store = ExportPresetStore(path)

    store.save_preset(
        name="MyPreset",
        template_ids=["general-readme", "python-pyproject"],
        destination="/tmp/out",
        use_hidden=False,
    )

    preset = store.get_preset("MyPreset")
    assert preset is not None
    assert preset.name == "MyPreset"
    assert "general-readme" in preset.template_ids
    assert preset.destination == "/tmp/out"
    assert preset.use_hidden is False


def test_export_preset_store_missing_returns_none(tmp_path: Path) -> None:
    store = ExportPresetStore(tmp_path / "presets.json")
    assert store.get_preset("missing") is None


def test_export_preset_store_get_preset_names(tmp_path: Path) -> None:
    path = tmp_path / "presets.json"
    store = ExportPresetStore(path)
    store.save_preset("Beta", ["general-readme"], "/out", False)
    store.save_preset("Alpha", ["python-ruff"], "/out2", True)

    names = store.get_preset_names()
    assert names == ["Alpha", "Beta"]  # sorted


def test_export_preset_store_overwrite_existing(tmp_path: Path) -> None:
    path = tmp_path / "presets.json"
    store = ExportPresetStore(path)
    store.save_preset("P", ["general-readme"], "/old", False)
    store.save_preset("P", ["python-ruff"], "/new", True)

    preset = store.get_preset("P")
    assert preset is not None
    assert preset.destination == "/new"
    assert preset.use_hidden is True


def test_export_preset_store_persists_to_disk(tmp_path: Path) -> None:
    path = tmp_path / "presets.json"
    store = ExportPresetStore(path)
    store.save_preset("Keep", ["general-notes"], "/out", False)

    store2 = ExportPresetStore(path)
    assert store2.get_preset("Keep") is not None


def test_export_preset_store_handles_corrupt_json(tmp_path: Path) -> None:
    path = tmp_path / "presets.json"
    path.write_text("not-json", encoding="utf-8")
    store = ExportPresetStore(path)
    assert store.get_preset_names() == []


def test_export_preset_store_use_hidden_true(tmp_path: Path) -> None:
    path = tmp_path / "presets.json"
    store = ExportPresetStore(path)
    store.save_preset("Hidden", ["cursor-cursor"], "/out", use_hidden=True)
    preset = store.get_preset("Hidden")
    assert preset is not None
    assert preset.use_hidden is True


# ── CATEGORIES structure ──────────────────────────────────────────────────────────

def test_categories_have_required_keys() -> None:
    for cat in CATEGORIES:
        assert "id" in cat
        assert "label" in cat
        assert "group" in cat


def test_category_ids_match_categories() -> None:
    ids_from_list = [c["id"] for c in CATEGORIES]
    assert CATEGORY_IDS == ids_from_list
