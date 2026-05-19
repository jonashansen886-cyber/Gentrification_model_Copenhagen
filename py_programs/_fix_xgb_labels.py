import json

path = "notebooks/05_XGBoost_model.ipynb"
with open(path, "r", encoding="utf-8") as f:
    nb = json.load(f)

changes = 0

for cell in nb["cells"]:
    cid = cell.get("id", "")
    src = cell.get("source", [])

    # ── Cell 26 (48b5ea43): classification_report + confusion matrix labels ──
    if cid == "48b5ea43":
        new_src = []
        for line in src:
            line = line.replace(
                "target_names=['Stable (0)', 'Gentrifying (1)']",
                "target_names=['Not Gentrified (0)', 'Gentrified (1)']",
            )
            line = line.replace(
                "display_labels=['Stable', 'Gentrifying']",
                "display_labels=['Not Gentrified', 'Gentrified']",
            )
            new_src.append(line)
        if new_src != src:
            cell["source"] = new_src
            changes += 1
            print(f"  Cell 26 (48b5ea43): updated labels")

    # ── Cell 28 (a77ce127): markdown description ──
    if cid == "a77ce127":
        new_src = []
        for line in src:
            line = line.replace(
                "(0 = Stable, 1 = Gentrifying)", "(0 = Not Gentrified, 1 = Gentrified)"
            )
            new_src.append(line)
        if new_src != src:
            cell["source"] = new_src
            changes += 1
            print(f"  Cell 28 (a77ce127): updated markdown description")

    # ── Cell 30 (8f2d773a): formula label ──
    if cid == "8f2d773a":
        new_src = []
        for line in src:
            line = line.replace(
                r"P(\text{Gentrifying} \mid x)", r"P(\text{Gentrified} \mid x)"
            )
            new_src.append(line)
        if new_src != src:
            cell["source"] = new_src
            changes += 1
            print(f"  Cell 30 (8f2d773a): updated formula label")

if changes:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"\nSaved {changes} cell(s) to {path}")
else:
    print("No changes made — check cell IDs or string matches")
