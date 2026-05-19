import json

with open("notebooks/08_LSTM_model.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)
for cid in ["08f010f7", "c9058ef3", "aeec777f"]:
    for i, cell in enumerate(nb["cells"]):
        if cell.get("id") == cid:
            print(f"=== Cell {i + 1} (id={cid}) ===")
            print("".join(cell.get("source", [])))
            print()
