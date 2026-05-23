# src/agentbox/render.py
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound

from .models import LibraryItem


class TemplateRenderer:
    """Jinja2-based renderer for all Eclipse output formats."""

    def __init__(self, template_dir: Path) -> None:
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,
        )

    def render(
        self,
        template_name: str,
        item: LibraryItem,
        extra: dict | None = None,
    ) -> str:
        """Render a template with the given library item as context."""
        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(
                f"Template '{template_name}' not found in {self.template_dir}"
            ) from None

        # Build the base context from the library item
        context: dict = {
            "item": item,
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "version": item.version,
            "tags": item.tags,
            "targets": item.targets,
            "scope": item.scope,
            "data": item.data,
            "requirements": item.requirements,
            "metadata": item.metadata,
        }

        # Merge any extra context (allows exporters to inject target-specific vars)
        if extra:
            context.update(extra)

        rendered = template.render(**context)

        # Ensure output always ends with a single newline
        return rendered.rstrip() + "\n"

    def template_exists(self, template_name: str) -> bool:
        """Check if a template file exists without raising an exception."""
        try:
            self.env.get_template(template_name)
            return True
        except TemplateNotFound:
            return False
