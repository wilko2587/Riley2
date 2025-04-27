Write-Host "Running deployBounce.py..." -ForegroundColor Cyan
python scripts/deployBounce.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment aborted or failed. Exiting." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "✅ Deployment succeeded. Running tests..." -ForegroundColor Green
python -m tests.run_tests_and_package
Write-Host "✅ Running version packaging..."
python scripts/package_current_version.py


Write-Host "🏁 All steps completed." -ForegroundColor Cyan
pause