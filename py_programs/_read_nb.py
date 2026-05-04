import json, sys

path = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "notebooks/OLD_05_machine_learning_model.ipynb"
)
nb = json.load(open(path, "r", encoding="utf-8"))
for i, c in enumerate(nb["cells"]):
    ct = c["cell_type"]
    src = "".join(c["source"])
    print(f"=== CELL {i} ({ct}) ===")
    print(src)
    print()
