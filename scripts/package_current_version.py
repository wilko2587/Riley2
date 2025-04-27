
import os
import zipfile
import datetime
import argparse
import importlib.util

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--tests_passed", type=int, default=None)
args = parser.parse_args()
tests_passed = args.tests_passed

def find_version(config_path):
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return getattr(config, "VERSION", None)

def clean_old_versions(versions_dir, keep_last_n=5):
    """Keep only the latest `keep_last_n` zip files."""
    zips = [os.path.join(versions_dir, f) for f in os.listdir(versions_dir) if f.endswith('.zip')]
    zips.sort(key=os.path.getmtime, reverse=True)  # Newest first
    for old_zip in zips[keep_last_n:]:
        try:
            os.remove(old_zip)
            print(f"🗑️ Deleted old version: {os.path.basename(old_zip)}")
        except Exception as e:
            print(f"⚠️ Could not delete {old_zip}: {e}")

def zip_project(base_dir, output_dir, version):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if version:
        zip_filename = f"Riley2_v{version}"
    else:
        zip_filename = "Riley2_vUnknown"

    if tests_passed is not None:
        zip_filename += f"_{tests_passed}tests"

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename += f"_{timestamp}.zip"

    zip_path = os.path.join(output_dir, zip_filename)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            if 'versions' in root.split(os.sep):
                continue
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, base_dir)
                zipf.write(filepath, arcname)

    print(f"✅ Project packaged as {zip_filename}")
    clean_old_versions(output_dir, keep_last_n=5)

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_path = os.path.join(base_dir, 'config.py')
    versions_path = os.path.join(base_dir, 'versions')
    version = find_version(config_path)
    zip_project(base_dir, versions_path, version)
