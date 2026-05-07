import json

with open("notebooks/13_LSTM_model.ipynb", encoding="utf-8") as f:
    nb = json.load(f)

targets = {"e5f75187", "4d33e95b", "aeec777f", "6e8bea92"}
for cell in nb["cells"]:
    cid = cell.get("id", "")
    if cid not in targets:
        continue
    src = "".join(cell.get("source", []))
    coral_lines = [
        (i + 1, line)
        for i, line in enumerate(src.split("\n"))
        if "coral" in line.lower()
    ]
    print(f"--- {cid} ---")
    for lineno, line in coral_lines:
        print(f"  L{lineno}: {line}")
    print()
