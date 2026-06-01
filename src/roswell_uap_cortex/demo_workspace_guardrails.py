"""Guardrails for synthetic demo workspaces."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import DemoWorkspace


@dataclass(slots=True)
class DemoWorkspaceGuardrails:
    """Keep demo inputs synthetic and clearly bounded."""

    allowed_source_prefixes: tuple[str, ...] = ("synthetic://", "unknown:")

    def validate_workspace(self, workspace: DemoWorkspace) -> None:
        if not workspace.manifest.synthetic_only:
            raise ValueError("demo workspace must be marked synthetic_only")
        for raw in workspace.raw_inputs:
            source = raw.source_uri or f"unknown:{raw.input_id}"
            if not source.startswith(self.allowed_source_prefixes):
                raise ValueError(f"demo workspace source is not synthetic: {source}")
            if "real uap" in raw.raw_text.casefold():
                raise ValueError("demo workspace must not include real UAP data")
