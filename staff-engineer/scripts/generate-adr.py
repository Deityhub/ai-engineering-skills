#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADR Generator — Creates Architecture Decision Records from templates.
Supports MADR (Markdown ADR) format with YAML frontmatter.
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path
from string import Template
from typing import Dict, List, Optional


ADR_TEMPLATE = Template("""---
adr: ${adr_id}
title: ${title}
status: ${status}  # proposed | accepted | rejected | deprecated | superseded
date: ${date}
deciders: ${deciders}
tags: ${tags}
---

## Context

${context}

## Decision

${decision}

## Consequences

### Positive
${positive}

### Negative
${negative}

### Neutral
${neutral}

## Related
${related}
""")

SUPERSEDE_TEMPLATE = Template("""---
adr: ${adr_id}
title: ${title}
status: superseded
date: ${date}
deciders: ${deciders}
tags: ${tags}
superseded-by: ${superseded_by}
---

## Context

${context}

## Decision

${decision}

## Consequences

### Positive
${positive}

### Negative
${negative}

### Neutral
${neutral}

## Superseded By

${superseded_by} — ${superseded_reason}

## Related
${related}
""")


class ADRGenerator:
    def __init__(self, adr_dir: Path = Path("docs/adr")):
        self.adr_dir = adr_dir
        self.adr_dir.mkdir(parents=True, exist_ok=True)

    def _next_id(self) -> str:
        existing = list(self.adr_dir.glob("*.md"))
        nums = []
        for f in existing:
            m = re.match(r"(\d{4})-", f.name)
            if m:
                nums.append(int(m.group(1)))
        return f"{max(nums, default=0) + 1:04d}"

    def _sanitize_filename(self, title: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

    def generate(
        self,
        title: str,
        context: str,
        decision: str,
        positive: List[str],
        negative: List[str],
        neutral: List[str],
        tags: List[str],
        deciders: List[str],
        status: str = "proposed",
        related: List[str] = None,
    ) -> Path:
        adr_id = self._next_id()
        filename = f"{adr_id}-{self._sanitize_filename(title)}.md"
        path = self.adr_dir / filename

        content = ADR_TEMPLATE.substitute(
            adr_id=adr_id,
            title=title,
            status=status,
            date=datetime.date.today().isoformat(),
            deciders=", ".join(deciders),
            tags=", ".join(tags),
            context=context.strip(),
            decision=decision.strip(),
            positive="\n".join(f"- {p}" for p in positive) or "- (none)",
            negative="\n".join(f"- {n}" for n in negative) or "- (none)",
            neutral="\n".join(f"- {n}" for n in neutral) or "- (none)",
            related="\n".join(f"- {r}" for r in (related or [])) or "- (none)",
        )

        path.write_text(content, encoding="utf-8")
        return path

    def supersede(self, old_adr_path: Path, new_adr_path: Path, reason: str) -> None:
        old_content = old_adr_path.read_text(encoding="utf-8")
        # Extract frontmatter
        fm_match = re.match(r"^---\n(.*?)\n---", old_content, re.DOTALL)
        if not fm_match:
            raise ValueError("Old ADR missing frontmatter")
        fm = fm_match.group(1)

        # Parse frontmatter (simple YAML-like)
        meta = {}
        for line in fm.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()

        old_id = meta.get("adr", "unknown")
        new_id_match = re.match(r"(\d{4})-", new_adr_path.name)
        new_id = new_id_match.group(1) if new_id_match else "unknown"

        # Update old ADR
        new_content = SUPERSEDE_TEMPLATE.substitute(
            adr_id=old_id,
            title=meta.get("title", "Unknown"),
            date=datetime.date.today().isoformat(),
            deciders=meta.get("deciders", ""),
            tags=meta.get("tags", ""),
            context=re.sub(r"^---\n.*?\n---", "", old_content, flags=re.DOTALL).split("## Decision")[0].strip(),
            decision=re.search(r"## Decision\n(.*?)\n## Consequences", old_content, re.DOTALL).group(1).strip() if re.search(r"## Decision\n(.*?)\n## Consequences", old_content, re.DOTALL) else "",
            positive="\n".join(l for l in re.findall(r"### Positive\n(.*?)\n###", old_content, re.DOTALL)[0].split("\n") if l.strip().startswith("-")) if "### Positive" in old_content else "- (none)",
            negative="\n".join(l for l in re.findall(r"### Negative\n(.*?)\n###", old_content, re.DOTALL)[0].split("\n") if l.strip().startswith("-")) if "### Negative" in old_content else "- (none)",
            neutral="\n".join(l for l in re.findall(r"### Neutral\n(.*?)\n##", old_content, re.DOTALL)[0].split("\n") if l.strip().startswith("-")) if "### Neutral" in old_content else "- (none)",
            superseded_by=f"[{new_id}]({new_adr_path.name})",
            superseded_reason=reason,
            related=re.search(r"## Related\n(.*?)$", old_content, re.DOTALL).group(1).strip() if re.search(r"## Related\n(.*?)$", old_content, re.DOTALL) else "- (none)",
        )
        old_adr_path.write_text(new_content, encoding="utf-8")

    def list_adrs(self, status: str = None) -> List[Dict]:
        adrs = []
        for f in sorted(self.adr_dir.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if fm_match:
                meta = {}
                for line in fm_match.group(1).split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meta[k.strip()] = v.strip()
                meta["file"] = f.name
                if status is None or meta.get("status") == status:
                    adrs.append(meta)
        return adrs


def main():
    parser = argparse.ArgumentParser(description="Generate Architecture Decision Records")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate
    gen = subparsers.add_parser("generate", help="Create a new ADR")
    gen.add_argument("--title", required=True, help="ADR title")
    gen.add_argument("--context", required=True, help="Context/problem statement")
    gen.add_argument("--decision", required=True, help="Decision made")
    gen.add_argument("--positive", nargs="*", default=[], help="Positive consequences")
    gen.add_argument("--negative", nargs="*", default=[], help="Negative consequences")
    gen.add_argument("--neutral", nargs="*", default=[], help="Neutral consequences")
    gen.add_argument("--tags", nargs="*", default=[], help="Tags (comma or space separated)")
    gen.add_argument("--deciders", nargs="*", default=["Team"], help="Decision makers")
    gen.add_argument("--status", default="proposed", choices=["proposed", "accepted", "rejected", "deprecated"])
    gen.add_argument("--related", nargs="*", default=[], help="Related ADR IDs or URLs")
    gen.add_argument("--adr-dir", default="docs/adr", help="ADR directory")

    # supersede
    sup = subparsers.add_parser("supersede", help="Mark an ADR as superseded")
    sup.add_argument("old_adr", help="Path to ADR being superseded")
    sup.add_argument("new_adr", help="Path to new ADR that supersedes it")
    sup.add_argument("--reason", required=True, help="Reason for superseding")

    # list
    lst = subparsers.add_parser("list", help="List ADRs")
    lst.add_argument("--status", choices=["proposed", "accepted", "rejected", "deprecated", "superseded"])
    lst.add_argument("--adr-dir", default="docs/adr")

    args = parser.parse_args()

    generator = ADRGenerator(Path(args.adr_dir))

    if args.command == "generate":
        path = generator.generate(
            title=args.title,
            context=args.context,
            decision=args.decision,
            positive=args.positive,
            negative=args.negative,
            neutral=args.neutral,
            tags=args.tags,
            deciders=args.deciders,
            status=args.status,
            related=args.related,
        )
        print(f"Created ADR: {path}")
        sys.exit(0)

    elif args.command == "supersede":
        generator.supersede(Path(args.old_adr), Path(args.new_adr), args.reason)
        print(f"Superseded {args.old_adr} -> {args.new_adr}")
        sys.exit(0)

    elif args.command == "list":
        adrs = generator.list_adrs(args.status)
        if not adrs:
            print("No ADRs found")
        else:
            for adr in adrs:
                print(f"{adr.get('adr', '?')}: {adr.get('title', 'Untitled')} [{adr.get('status', '?')}] ({adr['file']})")
        sys.exit(0)


if __name__ == "__main__":
    main()