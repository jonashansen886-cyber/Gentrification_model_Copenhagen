import json

with open("notebooks/05_XGBoost_model.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)
for cell in nb["cells"]:
    cid = cell.get("id", "")
    if cid in ("48b5ea43", "a77ce127", "8f2d773a"):
        ct = cell.get("cell_type", "")
        print(f"=== id={cid} type={ct} ===")
        print("".join(cell.get("source", [])))
        print()
