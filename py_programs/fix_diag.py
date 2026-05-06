import json

with open("notebooks/13_LSTM_model.ipynb", encoding="utf-8") as f:
    nb = json.load(f)

target_cell = None
for cell in nb["cells"]:
    src = "".join(cell.get("source", []))
    if "CORAL cumulative logits" in src:
        target_cell = cell
        break

if target_cell is None:
    print("Cell not found - checking for auc block")
    for cell in nb["cells"]:
        src = "".join(cell.get("source", []))
        if "AUC-ROC" in src and "all_cls_logits" in src:
            target_cell = cell
            print("Found cell:", cell.get("id", ""))
            break

if target_cell:
    src = "".join(target_cell["source"])
    old = (
        "# \u2500\u2500 Multi-class AUC-ROC \u2014 convert CORAL cumulative logits to class probs \u2500\u2500\n"
        "# P(y=0) = 1 - \u03c3(l1),  P(y=1) = \u03c3(l1) - \u03c3(l2),  P(y=2) = \u03c3(l2)\n"
        "cum = torch.sigmoid(torch.tensor(all_cls_logits, dtype=torch.float32))  # (N, 2)\n"
        "P0 = (1.0 - cum[:, 0]).unsqueeze(1)\n"
        "P1 = (cum[:, 0] - cum[:, 1]).clamp(min=0).unsqueeze(1)\n"
        "P2 = cum[:, 1].unsqueeze(1)\n"
        "y_prob = torch.cat([P0, P1, P2], dim=1).numpy()   # (N, 3)"
    )
    new = (
        "# \u2500\u2500 Multi-class AUC-ROC \u2014 softmax class probabilities \u2500\u2500\n"
        "y_prob = torch.softmax(torch.tensor(all_cls_logits, dtype=torch.float32), dim=1).numpy()  # (N, 3)"
    )
    if old in src:
        src = src.replace(old, new)
        target_cell["source"] = [src]
        with open("notebooks/13_LSTM_model.ipynb", "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print("Fixed AUC-ROC block")
    else:
        print("Old text not found, trying line search...")
        lines = src.split("\n")
        for i, line in enumerate(lines):
            if "CORAL cumulative" in line or "cum = torch.sigmoid" in line:
                print(f"  L{i + 1}: {repr(line)}")
else:
    print("No target cell found")
