
import os
import zipfile
import shutil
import datetime

# Configuration
DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TARGET_DIR = os.path.join(DEV_DIR, 'Riley2')
DOWNLOADS_DIR = os.path.expanduser('~/Downloads')
BACKUPS_DIR = os.path.join(DEV_DIR, 'backups')

PROTECTED_DIRS = ['logs', 'secrets', 'versions']
PROTECTED_FILES = [os.path.join('data', 'kdb.json')]

def find_latest_riley2_zip(downloads_dir):
    zips = [f for f in os.listdir(downloads_dir) if f.lower().endswith('.zip') and 'riley2' in f.lower()]
    if not zips:
        return None
    zips.sort(key=lambda f: os.path.getmtime(os.path.join(downloads_dir, f)), reverse=True)
    return os.path.join(downloads_dir, zips[0])

def backup_current_state():
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUPS_DIR, f"deployment_backup_{timestamp}.zip")
    shutil.make_archive(backup_path.replace('.zip', ''), 'zip', TARGET_DIR)
    print(f"✅ Backup created at: {backup_path}")

def clean_target_dir():
    for item in os.listdir(TARGET_DIR):
        item_path = os.path.join(TARGET_DIR, item)
        rel_path = os.path.relpath(item_path, TARGET_DIR)
        if rel_path in PROTECTED_DIRS or rel_path in PROTECTED_FILES:
            continue
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)
    print(f"🧹 Cleaned target directory except protected items.")

def extract_new_version(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            # Skip protected dirs/files during extraction if necessary
            if any(member.startswith(p + '/') for p in PROTECTED_DIRS):
                continue
            if any(member == p for p in PROTECTED_FILES):
                continue
            zip_ref.extract(member, DEV_DIR)
    print(f"📦 Extracted new version from {os.path.basename(zip_path)}")

if __name__ == "__main__":
    print("🚀 Starting deployment...")

    latest_zip = find_latest_riley2_zip(DOWNLOADS_DIR)
    if not latest_zip:
        print("❌ No Riley2 zip found in Downloads.")
        exit(1)

    print(f"Found: {latest_zip}")
    proceed = input("Proceed with this file? [Y/n]: ").strip().lower()
    if proceed not in ('', 'y', 'yes'):
        print("❌ Deployment cancelled.")
        exit(1)

    backup_current_state()
    clean_target_dir()
    extract_new_version(latest_zip)

    print("✅ Deployment completed successfully.")
