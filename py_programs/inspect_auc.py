import json

with open("notebooks/13_LSTM_model.ipynb", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    src = "".join(cell.get("source", []))
    if "AUC-ROC" in src and "all_cls_logits" in src:
        lines = src.split("\n")
        for i, line in enumerate(lines):
            if (
                "AUC" in line
                or "cum" in line
                or "P0" in line
                or "P1" in line
                or "P2" in line
                or "y_prob" in line
            ):
                print(f"L{i + 1}: {repr(line)}")
        break
