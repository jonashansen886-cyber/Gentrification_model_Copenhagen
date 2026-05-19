import json

bad = [
    "Stable (0)",
    "Gentrifying (1)",
    "Stable vs Gentrifying",
    "= Stable",
    "= Gentrifying",
    "display_labels=['Stable",
    "target_names=['Stable",
]
with open("notebooks/05_XGBoost_model.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)
found = False
for i, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    hits = [kw for kw in bad if kw in src]
    if hits:
        cid = cell.get("id", "")
        print(f"Cell {i + 1} id={cid}: {hits}")
        found = True
if not found:
    print("All clear -- no old class label terminology in source code.")
