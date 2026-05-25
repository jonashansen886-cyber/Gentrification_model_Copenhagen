"""Patch notebook 08 to add historical DB25 code names."""

import json

NB_PATH = "notebooks/08_LSTM_model.ipynb"

HISTORICAL_BLOCK = [
    "\n",
    "    # Historical codes no longer active in the current DB25 classification\n",
    "    _historical_names = {\n",
    '        "642020": "Non-financial holding companies (outdated code after)",\n',
    '        "851210": "General medical practitioners (outdated code after)",\n',
    '        "742040": "Architectural activities (outdated code after)",\n',
    '        "620200": "Computer and IT consultancy activities (outdated code after)",\n',
    "    }\n",
    "\n",
    "    def _get_name(code):\n",
    '        """Return English name; fall back to historical lookup, then generic label."""\n',
    "        if code in name_map:\n",
    "            return name_map[code]\n",
    '        return _historical_names.get(code, "(outdated code)")\n',
    "\n",
]

with open(NB_PATH, encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell.get("id") != "630e13bd":
        continue

    src = list(cell["source"])

    # 1. Find the closing ))  of the name_map dict and insert the block after it
    inserted = False
    new_src = []
    for i, line in enumerate(src):
        new_src.append(line)
        if (
            not inserted
            and line.strip() == "))"
            and "name_map" in "".join(src[max(0, i - 6) : i])
        ):
            new_src.extend(HISTORICAL_BLOCK)
            inserted = True

    if not inserted:
        print("ERROR: Could not find insertion point!")
    else:
        print(f"Inserted historical block after line {i}")

    # 2. Replace name_map.get calls with _get_name
    replaced = 0
    final_src = []
    for line in new_src:
        if 'name_map.get(code, "(outdated code)")' in line:
            line = line.replace(
                'name_map.get(code, "(outdated code)")', "_get_name(code)"
            )
            replaced += 1
        elif 'name_map.get(c, "(outdated code)")' in line:
            line = line.replace('name_map.get(c, "(outdated code)")', "_get_name(c)")
            replaced += 1
        final_src.append(line)

    print(f"Replaced {replaced} name_map.get calls")
    cell["source"] = final_src
    break

with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Done. File saved.")
