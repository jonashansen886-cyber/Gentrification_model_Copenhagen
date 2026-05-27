import json

path = "notebooks/MAPS/combined_web_map.ipynb"
nb = json.load(open(path, encoding="utf-8"))

for cell in nb["cells"]:
    src = "".join(cell.get("source", []))
    if "Defaults" not in src or "toggleLayer" not in src:
        continue

    # 1. Swap quarter/movement order in defaults (quarters first = bottom, movement on top)
    old_defaults = (
        "        window.toggleLayer('movement', true);   /* add data layer first */\n"
        "        window.toggleLayer('quarters', true);   /* quarters last \u2192 always on top */"
    )
    new_defaults = (
        "        window.toggleLayer('quarters', true);   /* quarters first \u2192 bottom layer */\n"
        "        window.toggleLayer('movement', true);   /* movement layer on top */"
    )
    if old_defaults in src:
        src = src.replace(old_defaults, new_defaults)
        print("  [1] Defaults order swapped OK")
    else:
        print("  [1] WARNING: defaults block not found")

    # 2. GT legend: High → Class 2 (unlikely gentrified)
    src = src.replace(
        "                    html += sw('#E15F1D') + 'High<br>';",
        "                    html += sw('#E15F1D') + 'Class 2 (unlikely gentrified)<br>';",
    )
    # 3. GT legend: Medium → Class 1 (no trend)
    src = src.replace(
        "                    html += sw('#F0E442',';border-color:#ccc') + 'Medium<br>';",
        "                    html += sw('#F0E442',';border-color:#ccc') + 'Class 1 (no trend)<br>';",
    )
    # 4. GT legend: Low → Class 0 (likely gentrified)
    src = src.replace(
        "                    html += sw('#0C8A00') + 'Low<br>';",
        "                    html += sw('#0C8A00') + 'Class 0 (likely gentrified)<br>';",
    )
    print("  [2-4] GT legend labels updated")

    # 5. GT tooltip via humanLabel – add ground_truth branch before fallback
    old_human = (
        "            if (type === 'binary')\n"
        "                return parseInt(val) === 1 ? 'Gentrified' : parseInt(val) === 0 ? 'Not Gentrified' : 'N/A';\n"
        "            return String(val);"
    )
    new_human = (
        "            if (type === 'binary')\n"
        "                return parseInt(val) === 1 ? 'Gentrified' : parseInt(val) === 0 ? 'Not Gentrified' : 'N/A';\n"
        "            if (type === 'ground_truth') {{\n"
        "                var GT_LABELS = {{'Low':'Class 0 (likely gentrified)','Medium':'Class 1 (no trend)','High':'Class 2 (unlikely gentrified)'}};\n"
        "                return GT_LABELS[String(val)] || String(val);\n"
        "            }}\n"
        "            return String(val);"
    )
    if old_human in src:
        src = src.replace(old_human, new_human)
        print("  [5] humanLabel ground_truth branch added OK")
    else:
        print("  [5] WARNING: humanLabel block not found")

    # Rebuild source list
    lines = src.split("\n")
    cell["source"] = [l + "\n" for l in lines[:-1]] + ([lines[-1]] if lines[-1] else [])
    print("Cell updated.")

json.dump(nb, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("Notebook saved.")
