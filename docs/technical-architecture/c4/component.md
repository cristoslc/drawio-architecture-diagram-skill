# Components inside the skill bundle

| Component | File | Responsibility |
|---|---|---|
| Workflow | `SKILL.md` | the order of the steps and the rules that carry the most weight |
| Style rules | `references/house-style.md` | the palette, the type scale, the spacing, the edge rules |
| Format rules | `references/xml-rules.md` | the file format, the cell model, the style strings |
| Renderer | `scripts/render-drawio-svg.sh` | a source becomes a committed artifact |
| Comparator | `scripts/validate-drawio-svg.py` | an artifact and its source are compared, and the comparison self-tests |
