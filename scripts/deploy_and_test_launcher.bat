@echo off
echo Running deployBounce.py...
python scripts/deployBounce.py

echo ✅ Deployment succeeded. Running tests...
python scripts/run_tests_and_package.py

echo ✅ Running version packaging...
python scripts/package_current_version.py

echo 🎉 All steps completed.
pause
