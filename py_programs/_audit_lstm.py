import json

with open("notebooks/08_LSTM_model.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)
keywords = ["Stable", "Gentrifying", "R_stable", "R_gent", "stable=", "gent="]
for i, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    hits = [kw for kw in keywords if kw in src]
    if hits:
        cid = cell.get("id", "")
        print(f"=== Cell {i + 1} (id={cid}) keywords={hits} ===")
        print(src[:800])
        print()
