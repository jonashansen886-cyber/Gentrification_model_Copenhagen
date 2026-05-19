import json

with open("notebooks/08_LSTM_model.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)
bad_kw = [
    "Stable vs Gentrifying",
    "R_stable",
    "# Stable recall",
    "Recall Stable",
    "Recall Gentrifying",
    "recall=[stable=",
]
found = False
for i, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    hits = [kw for kw in bad_kw if kw in src]
    if hits:
        cid = cell.get("id", "")
        print(f"Cell {i + 1} id={cid}: {hits}")
        found = True
if not found:
    print("All clear -- no old class label terminology in source code.")
