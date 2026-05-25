"""Remove stranded pptx/sharepoint continuation lines left behind after URL normalization."""
import re
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "taxonomy" / "business-processes.yaml"
text = p.read_text(encoding="utf-8")
lines = text.split("\n")
out = []
i = 0
removed = 0
while i < len(lines):
    out.append(lines[i])
    if re.match(r"\s*learn_url:", lines[i]):
        j = i + 1
        # Skip blank or orphan continuation lines (pptx/sharepoint/[https with closing apostrophe).
        while j < len(lines):
            nxt = lines[j]
            if nxt.strip() == "":
                j += 1
                removed += 1
                continue
            if (".pptx" in nxt) or ("sharepoint.com" in nxt) or nxt.startswith("[https") or nxt.endswith("]'"):
                j += 1
                removed += 1
                continue
            break
        i = j
    else:
        i += 1

p.write_text("\n".join(out), encoding="utf-8")
print(f"removed {removed} orphan lines")
