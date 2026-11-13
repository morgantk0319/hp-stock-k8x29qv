import json, os, requests
from pathlib import Path

HANDLES = [
    "almost-perfect-lark-baby-carrier",
    "almost-perfect-sprout-newborn-carrier",
    "almost-perfect-meh-dai",
]
NTFY_TOPIC = os.environ["NTFY_TOPIC"]
STATE = Path("state.json")

def in_stock(handle):
    url = f"https://www.hopeandplum.co/products/{handle}.js"
    data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30).json()
    return sorted(
        v.get("public_title") or v["title"]
        for v in data["variants"]
        if v["available"] and "short" in (v.get("public_title") or v["title"]).lower()
    )

old = json.loads(STATE.read_text()) if STATE.exists() else None
new = {h: in_stock(h) for h in HANDLES}

if old is not None:
    for h in HANDLES:
        added = set(new[h]) - set(old.get(h, []))
        removed = set(old.get(h, [])) - set(new[h])
        if added or removed:
            msg = f"{h}\nBack in stock: {sorted(added)}\nSold out: {sorted(removed)}"
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode())

STATE.write_text(json.dumps(new, indent=2))
