import json, sys

path = "notebooks/08_LSTM_model.ipynb"
with open(path, "r", encoding="utf-8") as f:
    nb = json.load(f)

changes = 0

for cell in nb["cells"]:
    cid = cell.get("id", "")
    src = cell.get("source", [])

    # ── Cell 17 (08f010f7): Training loop ──
    if cid == "08f010f7":
        new_src = []
        for line in src:
            # Fix "Stable recall" comment
            line = line.replace(
                "# Stable recall (monitoring)",
                "# Not Gentrified recall (class 0, monitoring)",
            )
            # Fix R_stable in print string
            line = line.replace(
                "R_stable: {val_r0:.3f}  R_gent:", "R_not_gent: {val_r0:.3f}  R_gent:"
            )
            new_src.append(line)
        if new_src != src:
            cell["source"] = new_src
            changes += 1
            print(f"  Cell 17 (08f010f7): updated")

    # ── Cell 23 (aeec777f): 5-Fold CV ──
    if cid == "aeec777f":
        new_src = []
        for line in src:
            # Fix header print
            line = line.replace(
                "binary: Stable vs Gentrifying", "binary: Not Gentrified vs Gentrified"
            )
            # Fix fold recall format
            line = line.replace(
                "recall=[stable={fold_r[0]:.3f}, gent={fold_r[1]:.3f}]",
                "recall=[not_gent={fold_r[0]:.3f}, gent={fold_r[1]:.3f}]",
            )
            # Fix summary labels
            line = line.replace(
                '("r0","Recall Stable (0)"),("r1","Recall Gentrifying (1)")',
                '("r0","Recall Not Gentrified (0)"),("r1","Recall Gentrified (1)")',
            )
            new_src.append(line)
        if new_src != src:
            cell["source"] = new_src
            changes += 1
            print(f"  Cell 23 (aeec777f): updated")

if changes:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"\nSaved {changes} cell(s) to {path}")
else:
    print("No changes made — check cell IDs or string matches")
    sys.exit(1)
