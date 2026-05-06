import json

with open("notebooks/13_LSTM_model.ipynb", encoding="utf-8") as f:
    nb = json.load(f)

check_ids = {
    "94d2a90c",
    "6fc4ae62",
    "f2feabef",
    "13de0cab",
    "29874b2c",
    "0a4b9cd4",
    "81245160",
}
errors = []
for cell in nb["cells"]:
    cid = cell.get("id", "")
    if cid not in check_ids:
        continue
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell.get("source", []))
    try:
        compile(src, f"<cell-{cid}>", "exec")
        print(f"  OK  {cid}  ({len(src.splitlines())} lines)")
    except SyntaxError as e:
        print(f"  ERR {cid}: {e}")
        lines = src.splitlines()
        for i, l in enumerate(
            lines[max(0, e.lineno - 3) : e.lineno + 2], max(1, e.lineno - 2)
        ):
            print(f"    {i:3d}: {l}")
        errors.append(cid)

print()
if errors:
    print(f"ERRORS in: {errors}")
else:
    print("All cells OK")

# Also check for remaining coral references
print("\nRemaining coral refs:")
for cell in nb["cells"]:
    src = "".join(cell.get("source", []))
    if "coral_loss" in src or "coral_predict" in src or "coral_to_class_probs" in src:
        cid = cell.get("id", "")
        for line in src.split("\n"):
            if (
                "coral_loss" in line
                or "coral_predict" in line
                or "coral_to_class_probs" in line
            ):
                print(f"  {cid}: {line.strip()}")
