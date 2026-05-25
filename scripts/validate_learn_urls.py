"""Validate and normalize learn_url fields in taxonomy/business-processes.yaml.

- Extracts the first https://learn.microsoft.com/... URL from each value.
- Normalizes `Dynamics365` -> `dynamics365` in path segments.
- HEAD-checks each URL; reports 404s/redirects with suggested replacements.
- Writes back normalized file when --apply is passed.
"""
from __future__ import annotations
import argparse
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "taxonomy" / "business-processes.yaml"

URL_RE = re.compile(r"https://learn\.microsoft\.com/[^\s\]'\"]+", re.IGNORECASE)
LEARN_LINE_RE = re.compile(r"^(?P<indent>\s*)learn_url:\s*(?P<val>.*)$")


def extract_first_url(raw: str) -> str | None:
    m = URL_RE.search(raw)
    if not m:
        return None
    url = m.group(0).rstrip(".,;)")
    # Normalize "/Dynamics365/" capitalization
    url = re.sub(r"/Dynamics365/", "/dynamics365/", url)
    return url


def head_check(url: str, timeout: float = 10.0) -> tuple[int, str]:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 link-check"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.url
    except urllib.error.HTTPError as e:
        # Retry GET for sites that block HEAD
        if e.code in (403, 405):
            try:
                req2 = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 link-check"})
                with urllib.request.urlopen(req2, timeout=timeout) as resp:
                    return resp.status, resp.url
            except Exception as e2:
                return getattr(e2, "code", 0) or -1, str(e2)
        return e.code, str(e)
    except Exception as e:
        return -1, str(e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write normalized YAML back")
    ap.add_argument("--check", action="store_true", help="HEAD-check each URL")
    args = ap.parse_args()

    text = YAML_PATH.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    changes: list[tuple[int, str, str]] = []  # (lineno, old_url_raw, new_url)
    out_lines = list(lines)
    seen_urls: list[tuple[int, str]] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        m = LEARN_LINE_RE.match(line)
        if not m:
            i += 1
            continue
        indent = m.group("indent")
        val_start = m.group("val").strip()
        # Collect a possible multi-line continuation (folded/literal blocks).
        block = val_start
        j = i + 1
        consumed = 1
        # If value is empty (block scalar marker like > or |), gather indented lines.
        if val_start in ("|", ">", "|-", ">-", "|+", ">+") or val_start == "":
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() == "" or nxt.startswith(indent + "  "):
                    block += "\n" + nxt.rstrip("\n")
                    j += 1
                    consumed += 1
                else:
                    break
        # Also handle quoted strings that wrap across multiple lines visually — yaml
        # single-quoted strings are single-line in this file, so we don't merge.

        new_url = extract_first_url(block)
        if new_url is None:
            i += consumed
            continue

        # Reconstruct the value with single quotes; if the URL contains a single
        # quote that's fine here it won't.
        new_line = f"{indent}learn_url: '{new_url}'\n"
        if new_line != line or consumed > 1:
            changes.append((i + 1, block.strip(), new_url))
            # Replace the original block with single normalized line.
            out_lines[i] = new_line
            for k in range(1, consumed):
                out_lines[i + k] = ""  # blank out continuation lines

        seen_urls.append((i + 1, new_url))
        i += consumed

    print(f"Found {len(seen_urls)} learn_url entries; {len(changes)} normalized.")
    for ln, old, new in changes:
        snippet = old.replace("\n", " \\n ")[:140]
        print(f"  line {ln}:")
        print(f"    OLD: {snippet}")
        print(f"    NEW: {new}")

    if args.check:
        print("\nHEAD-checking unique URLs...")
        unique = sorted({u for _, u in seen_urls})
        bad: list[tuple[str, int, str]] = []
        for u in unique:
            status, info = head_check(u)
            tag = "OK " if 200 <= status < 400 else "BAD"
            print(f"  [{tag}] {status} {u}")
            if not (200 <= status < 400):
                bad.append((u, status, info))
        print(f"\n{len(unique) - len(bad)}/{len(unique)} OK; {len(bad)} broken.")
        if bad:
            for u, s, info in bad:
                print(f"  BROKEN {s}: {u}\n    {info}")

    if args.apply and changes:
        # Drop blanked continuation lines
        final = "".join(l for l in out_lines if l != "")
        YAML_PATH.write_text(final, encoding="utf-8")
        print(f"\nWrote {YAML_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
