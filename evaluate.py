import json
from extract import extract_items

with open("data/answer.json", encoding="utf-8") as f:
    answers = json.load(f)

correct = total = 0

for tid, expected in answers.items():
    with open(f"data/{tid}.txt", encoding="utf-8") as f:
        text = f.read()
    got = extract_items(text)
    used = set()
    print(f"\n{tid}: expected {len(expected)} items, got {len(got)}")

    for exp in expected:
        match = None
        for i, g in enumerate(got):
            if i in used:
                continue
            if g.get("type") == exp["type"] and exp["keyword"].lower() in g.get("task", "").lower():
                match = i
                break

        total += 3                      # type, owner, deadline
        if match is None:
            print(f"  MISSING item: {exp['type']} / {exp['keyword']}")
            continue

        used.add(match)
        g = got[match]
        correct += 1                    # type sari
        for fld in ("owner", "deadline"):
            if str(g.get(fld, "")).lower() == exp[fld].lower():
                correct += 1
            else:
                print(f"  MISS {fld} ({exp['keyword']}): expected {exp[fld]!r}, got {g.get(fld)!r}")

    for i, g in enumerate(got):
        if i not in used:
            total += 3                  # extra item = thappu
            print(f"  EXTRA item: {g.get('type')} | {g.get('task')}")

print(f"\nAccuracy: {correct}/{total} = {100 * correct / total:.0f}%" if total else "No items")