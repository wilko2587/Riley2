# FINAL fixed scripts/run_tests_and_package.py with formatted Test Summary table

import unittest
import os
import zipfile
import sys
from datetime import datetime

# Setup dynamic paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
PACKAGE_DIR = os.path.join(BASE_DIR, 'packages')
TESTS_DIR = os.path.join(BASE_DIR, 'tests')

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PACKAGE_DIR, exist_ok=True)

# Ensure BASE_DIR is in sys.path for correct imports
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Run all tests dynamically
def run_tests():
    print("\n🚀 Running all tests...\n")

    loader = unittest.TestLoader()
    suite = loader.discover(TESTS_DIR, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    total_tests = result.testsRun
    failed_tests = len(result.failures) + len(result.errors)
    passed_tests = total_tests - failed_tests

    duration_str = datetime.now().strftime('%H:%M:%S')
    print_test_summary(total_tests, passed_tests, failed_tests, duration_str)

    return failed_tests == 0

# Pretty print the test summary
def print_test_summary(total_tests, passed_tests, failed_tests, duration_str):
    print("\n📊 Test Summary:")
    border = "+------------------+--------------+"
    print(border)
    print(f"| {'Metric':<16} | {'Value':<12} |")
    print(border)
    print(f"| {'Tests Run':<16} | {total_tests:<12} |")
    print(f"| {'Tests Passed':<16} | {passed_tests:<12} |")
    print(f"| {'Tests Failed':<16} | {failed_tests:<12} |")
    print(f"| {'Duration':<16} | {duration_str:<12} |")
    print(border)

# Package the project into a timestamped ZIP
def package_project():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"Riley2_v2.3e_{timestamp}.zip"
    package_path = os.path.join(PACKAGE_DIR, package_name)

    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith(".py") and not root.endswith("packages") and not root.endswith("logs"):
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, BASE_DIR)
                    zipf.write(filepath, arcname)

    print(f"✅ Project packaged as {package_name}")

if __name__ == "__main__":
    all_tests_passed = run_tests()
    if all_tests_passed:
        print("\n✅ All tests passed! Proceeding to package project...")
        package_project()
    else:
        print("\n❌ Tests failed. Fix issues before packaging.")