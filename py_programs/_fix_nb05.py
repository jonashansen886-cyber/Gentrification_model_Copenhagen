import json

nb = json.load(open("notebooks/05_XGBoost_model.ipynb", "r", encoding="utf-8"))

# ── Cell 0: fix intro markdown ────────────────────────────────────────────────
nb["cells"][0]["source"] = (
    "# Notebook 05 \u2013 XGBoost Machine Learning Model\n"
    "\n"
    "This notebook trains an XGBoost classifier to predict gentrification pressure levels for Copenhagen neighborhoods.\n"
    "\n"
    "**Key differences from OLD_05:**\n"
    "- Target variable: `combined_class_idx` from `classified_combined.gpkg` (0=Low/gentrified, 1=Medium, 2=High)\n"
    "- Input: GT_V2 only (trend + start/end values + volatility features)\n"
    "- Future predictions for 2025, 2030, 2035 by linearly extrapolating `_end_value` features using `_reg_2015_2020` slopes\n"
    "\n"
    "**Note on `first_low_period`:** This temporal field is computed and shown for analysis, "
    "but is **excluded from model training** to avoid label leakage "
    "(it is non-null only for class-0 clusters, which would perfectly reveal the target).\n"
    "\n"
    "Predictions are saved in `results/models/`."
)

# ── Cell 9: fix section 3 markdown ───────────────────────────────────────────
nb["cells"][9]["source"] = (
    "## 3. Temporality Feature Engineering\n"
    "\n"
    "`first_low_period` records the earliest period a cluster was classified Low (gentrified). "
    "It is encoded as an ordinal integer (1\u20136) for inspection:\n"
    "- `'1990_1995'` \u2192 1, `'1995_2000'` \u2192 2, ..., `'2015_2020'` \u2192 6\n"
    "- `None` / NaN (never classified Low) \u2192 0\n"
    "\n"
    "> **Important:** `first_low_period_encoded` is added to `data` for analysis purposes only.  \n"
    "> It is **not included in the training feature matrix X** because it is non-zero exclusively "
    "for class-0 clusters, which constitutes label leakage and produces artificially perfect class-0 metrics."
)

# ── Cell 12: add first_low_period_encoded to DROP_COLS + fix print ───────────
src12 = "".join(nb["cells"][12]["source"])

src12 = src12.replace(
    "DROP_COLS = {'cluster_id', 'combined_class_idx', 'combined_class', 'avg_mean',\n"
    "             'first_low_period', 'geometry'}",
    "DROP_COLS = {'cluster_id', 'combined_class_idx', 'combined_class', 'avg_mean',\n"
    "             'first_low_period', 'first_low_period_encoded', 'geometry'}",
)

src12 = src12.replace(
    "print(f\"\\nFeatures include 'first_low_period_encoded': {'first_low_period_encoded' in X.columns}\")",
    "print(f\"\\n'first_low_period_encoded' excluded from X (leak prevention): {'first_low_period_encoded' not in X.columns}\")",
)

nb["cells"][12]["source"] = src12

json.dump(
    nb,
    open("notebooks/05_XGBoost_model.ipynb", "w", encoding="utf-8"),
    indent=1,
    ensure_ascii=False,
)
print("Done – 3 cells updated.")
