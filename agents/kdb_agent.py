import json
import os
from pathlib import Path

KDB_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"

def load_kdb():
    if not KDB_PATH.exists():
        return {}
    with open(KDB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_kdb(kdb):
    KDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(KDB_PATH, "w", encoding="utf-8") as f:
        json.dump(kdb, f, indent=2)

def kdb_query(args):
    kdb = load_kdb()
    topic = args.get("topic", "").lower()
    if not topic:
        return "Please specify a topic to search for."
    results = []
    for key, entries in kdb.items():
        for entry in entries:
            if topic in entry.lower():
                results.append(f"{key}: {entry}")
    return "\n".join(results) if results else "No relevant entries found."

def kdb_add_entry(args):
    kdb = load_kdb()
    category = args.get("category", "general")
    entry = args.get("entry", "").strip()
    if not entry:
        return "Entry content missing."
    kdb.setdefault(category, []).append(entry)
    save_kdb(kdb)
    return f"Added entry to '{category}': {entry}"

def kdb_edit_entry(args):
    kdb = load_kdb()
    category = args.get("category", "general")
    index = args.get("index")
    new_entry = args.get("entry", "").strip()
    if category not in kdb or index is None or index >= len(kdb[category]):
        return "Invalid category or index."
    old_entry = kdb[category][index]
    kdb[category][index] = new_entry
    save_kdb(kdb)
    return f"Updated entry [{index}] in '{category}':\n- Old: {old_entry}\n- New: {new_entry}"

def kdb_delete_entry(args):
    kdb = load_kdb()
    category = args.get("category", "general")
    index = args.get("index")
    if category not in kdb or index is None or index >= len(kdb[category]):
        return "Invalid category or index."
    removed = kdb[category].pop(index)
    if not kdb[category]:
        del kdb[category]
    save_kdb(kdb)
    return f"Deleted entry from '{category}': {removed}"
