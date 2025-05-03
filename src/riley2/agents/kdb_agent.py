import json
import os
import logging
from pathlib import Path
from riley2.core.logger_utils import logger

KDB_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"

def load_kdb():
    logger.debug(f"Loading knowledge database from {KDB_PATH}")
    if not KDB_PATH.exists():
        logger.warning("Knowledge database file does not exist. Returning empty database.")
        return {}
    try:
        with open(KDB_PATH, "r", encoding="utf-8") as f:
            kdb = json.load(f)
            logger.info(f"Loaded knowledge database with {len(kdb)} categories.")
            return kdb
    except Exception as e:
        logger.error(f"Error loading knowledge database: {e}")
        return {}

def save_kdb(kdb):
    logger.debug(f"Saving knowledge database to {KDB_PATH}")
    try:
        KDB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(KDB_PATH, "w", encoding="utf-8") as f:
            json.dump(kdb, f, indent=2)
        logger.info("Knowledge database saved successfully.")
    except Exception as e:
        logger.error(f"Error saving knowledge database: {e}")

def kdb_query(args):
    topic = args.get("topic", "").lower()
    logger.debug(f"Querying knowledge database for topic: {topic}")
    if not topic:
        logger.warning("No topic specified for query.")
        return "Please specify a topic to search for."
    kdb = load_kdb()
    results = []
    for key, entries in kdb.items():
        for entry in entries:
            if topic in entry.lower():
                results.append(f"{key}: {entry}")
    logger.info(f"Query found {len(results)} matching entries.")
    return "\n".join(results) if results else "No relevant entries found."

def kdb_add_entry(args):
    category = args.get("category", "general")
    entry = args.get("entry", "").strip()
    logger.debug(f"Adding entry to category '{category}': {entry}")
    if not entry:
        logger.warning("Entry content missing.")
        return "Entry content missing."
    kdb = load_kdb()
    kdb.setdefault(category, []).append(entry)
    save_kdb(kdb)
    logger.info(f"Added entry to '{category}': {entry}")
    return f"Added entry to '{category}': {entry}"

def kdb_edit_entry(args):
    category = args.get("category", "general")
    index = args.get("index")
    new_entry = args.get("entry", "").strip()
    logger.debug(f"Editing entry in category '{category}' at index {index} to: {new_entry}")
    kdb = load_kdb()
    if category not in kdb or index is None or index >= len(kdb[category]):
        logger.warning("Invalid category or index for edit.")
        return "Invalid category or index."
    old_entry = kdb[category][index]
    kdb[category][index] = new_entry
    save_kdb(kdb)
    logger.info(f"Updated entry [{index}] in '{category}':\n- Old: {old_entry}\n- New: {new_entry}")
    return f"Updated entry [{index}] in '{category}':\n- Old: {old_entry}\n- New: {new_entry}"

def kdb_delete_entry(args):
    category = args.get("category", "general")
    index = args.get("index")
    logger.debug(f"Deleting entry in category '{category}' at index {index}")
    kdb = load_kdb()
    if category not in kdb or index is None or index >= len(kdb[category]):
        logger.warning("Invalid category or index for deletion.")
        return "Invalid category or index."
    removed = kdb[category].pop(index)
    if not kdb[category]:
        del kdb[category]
    save_kdb(kdb)
    logger.info(f"Deleted entry from '{category}': {removed}")
    return f"Deleted entry from '{category}': {removed}"
