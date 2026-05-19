import json

for nb_name, nb_path in [
    ("XGBoost", "notebooks/05_XGBoost_model.ipynb"),
    ("LSTM", "notebooks/08_LSTM_model.ipynb"),
]:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    print(f"=== {nb_name} ===")
    for i, cell in enumerate(nb["cells"]):
        src = "".join(cell.get("source", []))
        if any(
            kw in src
            for kw in [
                "proba_cph",
                "xgb_proba",
                "lstm_proba",
                "p_gentrified",
                "p_not_gentrified",
            ]
        ):
            cid = cell.get("id", "")
            print(f"Cell {i + 1} id={cid}:")
            print(src[:1000])
            print()
