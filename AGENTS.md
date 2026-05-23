# Eclipse AGENTS

**Package:** `agentbox`
**Version:** 0.1.0

Use this file with `../AGENTS.md`. It only records Eclipse-specific context.

## Purpose And Entry Points

- Main app: `src/agentbox/main.py`
- Key areas: `src/agentbox/models.py`, `src/agentbox/storage.py`, `src/agentbox/render.py`, `src/agentbox/exporters/`, `src/agentbox/importers/`
- Run locally: `uv run python -m agentbox.main`
- Build through workspace wrappers: `eclipsebuild` or `razorbuild Eclipse`
- Push: `eclipsepush`
- `razorcore` is an editable dependency; re-verify Eclipse after upstream shared-library changes.

## Architecture Rules

- **Library is Source of Truth**: Never allow exporters to modify the library.
- **Pure Exporters**: Exporters only render and write. They don't validate or manage state.
- **Path Safety**: Use `agentbox.paths` for all path resolution. Never use hardcoded strings or `~`.
- **Atomic Operations**: When saving to the library, ensure the directory structure is created before the manifest.
- **Type Safety**: Respect the `LibraryItem` dataclass structure.

## Non-Obvious Rules

- Package name is `agentbox`; display name is `Eclipse`. The `.spec` file, build scripts, and DMG use `Eclipse`. Source imports use `agentbox`.
- Jinja2 templates live in `src/agentbox/templates/` and are bundled via `Eclipse.spec` datas — any new template directory must be added to the spec.
- Exporters are keyed by tool name string (e.g. `"claude_code"`, `"windsurf"`) — the key is the contract, not the class name.
- `agentbox.paths` is the single place path logic lives; never resolve `~` inline in exporters or importers.

## Verification

Baseline:

```bash
uv run ruff check .
uv run ty check src --python-version 3.14
uv run pytest tests/ -q
```

Add focused checks when relevant:

- Exporter output correctness: `uv run pytest tests/test_exporters.py -q`
- Library persistence: `uv run pytest tests/test_storage.py -q`
- Full smoke: `uv run python -m agentbox.main`

## CI Limitations

CI proves lint, type safety, and unit test correctness. It does NOT prove that rendered
output is accepted by target IDEs, or that file system permissions allow writing to IDE config dirs.

## Release Readiness Checklist

Before tagging a release, verify all of the following:
- [ ] `uv run ruff check .` passes with no errors
- [ ] `uv run ty check src --python-version 3.14` passes with no errors
- [ ] `uv run pytest tests/ -q` passes with no failures
- [ ] App launches locally from a clean `uv sync`
- [ ] At least one export flow exercised end-to-end per supported IDE target
- [ ] `pyproject.toml` version matches README badge/display text

### What CI Does Not Prove
> Green CI is necessary but not sufficient for a safe release.
> IDE acceptance of rendered config files cannot be validated by static CI checks.

---

Copyright (c) 2026 RazorBackRoar.

## Universal Safety Rules

Before making changes, read and follow:

../../docs/Agent Pre-Safety Rules.md

---

## App Repository Rules

This is an individual app repository. Keep all changes scoped to this app
unless explicitly requested.
- Do not modify unrelated apps.
- Do not create branches unless explicitly requested.
- Do not switch branches unless explicitly requested.
- Do not create or switch worktrees unless explicitly requested.
- Do not commit unless explicitly requested.
- Do not push unless explicitly requested.
- Do not delete, rename, move, or overwrite unrelated files.
- Preserve existing project style and conventions.
- Keep changes minimal and targeted.

---

## App Environment

Assume:
- Apple Silicon macOS
- Python 3.14
- uv
- ruff
- ty
- pytest

Prefer:
    uv sync
    uv run ruff check .
    uv run ty check .
    uv run pytest

---

## App Workflow

Before editing:

1. Inspect relevant files.
2. Identify existing project commands.
3. Make the smallest safe change.
4. Avoid broad refactors unless explicitly requested.
5. Avoid dependency/config changes unless required.

---

## App Validation

After code changes, suggest or run relevant checks:
    uv run ruff check .
    uv run ty check .
    uv run pytest

If packaging/build files changed, inspect existing build scripts before
suggesting build commands. Do not claim validation passed unless actual command
output confirms it.

---

## Eclipse Notes

Eclipse is a workspace rules/config generator.
Keep it tool-neutral where possible. It may support Codex, Windsurf,
Antigravity, Cursor, Warp, and other agent configuration formats.
Do not make Claude Code the default or primary workflow.

---

## Test Coverage

`tests/` exists but is currently empty — no tests have been written yet.
This is a pre-existing gap, not a regression. The Verification section above
references test file names (`test_exporters.py`, `test_storage.py`) that do
not yet exist. When adding tests, place them under `tests/` and follow the
pytest conventions in `pyproject.toml` (`pythonpath = ["src"]`).


## Behavioral Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use your judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.