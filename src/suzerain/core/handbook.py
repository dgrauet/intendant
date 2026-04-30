"""Parse the handbook + ADR Markdown files into queryable structures."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Matches: ### XX001 — Title text
_RULE_HEADING_RE = re.compile(r"^###\s+([A-Z]{2}\d{3})\s+[—-]\s+(.+?)\s*$")

# Matches: **Severity:** required · **Stacks:** python · **ADR:** [slug](path)
_META_LINE_RE = re.compile(r"^\*\*Severity:\*\*\s+(\w+)")
_STACKS_RE = re.compile(r"\*\*Stacks:\*\*\s+([^·\n]+?)(?:\s*·|\s*$)")
_ADR_RE = re.compile(r"\*\*ADR:\*\*\s+\[([^\]]+)\]")


@dataclass(frozen=True)
class RuleSection:
    rule_id: str
    title: str
    severity: str  # "required" | "recommended" | "optional"
    stacks: tuple[str, ...] = ()
    adr_ref: str | None = None
    body: str = ""
    source_file: Path | None = None


class Handbook:
    """Loader for handbook + ADR markdown files."""

    def __init__(self, root: Path) -> None:
        if not root.is_dir():
            raise FileNotFoundError(f"handbook root not found: {root}")
        self.root = root
        self._handbook_dir = root / "handbook"
        self._adr_dir = root / "adr"
        self._cache: dict[str, RuleSection] | None = None

    def _load(self) -> dict[str, RuleSection]:
        if self._cache is not None:
            return self._cache
        rules: dict[str, RuleSection] = {}
        if not self._handbook_dir.is_dir():
            self._cache = rules
            return rules
        for md_file in sorted(self._handbook_dir.glob("*.md")):
            rules.update(_parse_file(md_file))
        self._cache = rules
        return rules

    def list_rules(self) -> list[str]:
        return sorted(self._load().keys())

    def get_rule(self, rule_id: str) -> RuleSection | None:
        return self._load().get(rule_id)

    def get_adr(self, adr_slug: str) -> str | None:
        path = self._adr_dir / f"{adr_slug}.md"
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8")


def _parse_file(path: Path) -> dict[str, RuleSection]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    rules: dict[str, RuleSection] = {}
    i = 0
    while i < len(lines):
        match = _RULE_HEADING_RE.match(lines[i])
        if not match:
            i += 1
            continue
        rule_id, title = match.group(1), match.group(2).strip()
        # Capture body until next ### or ## heading (or EOF)
        body_lines: list[str] = []
        j = i + 1
        while j < len(lines):
            if lines[j].startswith("### ") or lines[j].startswith("## "):
                break
            body_lines.append(lines[j])
            j += 1
        body = "\n".join(body_lines).strip()
        severity, stacks, adr_ref = _extract_meta(body)
        rules[rule_id] = RuleSection(
            rule_id=rule_id,
            title=title,
            severity=severity,
            stacks=stacks,
            adr_ref=adr_ref,
            body=body,
            source_file=path,
        )
        i = j
    return rules


def _extract_meta(body: str) -> tuple[str, tuple[str, ...], str | None]:
    severity = "optional"
    stacks: tuple[str, ...] = ()
    adr_ref: str | None = None
    for line in body.splitlines():
        sev_match = _META_LINE_RE.search(line)
        if sev_match:
            severity = sev_match.group(1)
            stacks_match = _STACKS_RE.search(line)
            if stacks_match:
                raw = stacks_match.group(1).strip()
                stacks = tuple(s.strip() for s in raw.split(",")) if raw else ()
            adr_match = _ADR_RE.search(line)
            if adr_match:
                adr_ref = adr_match.group(1)
            break
    return severity, stacks, adr_ref
