$exitCode = 0;

# TODO: Run front-end test script when available

# Run python kernel test scripts
Write-Host "start: pytest powerbi_client"
& python -m pytest powerbi_client --cov -v
Write-Host "done: pytest powerbi_client"
$exitCode += $LASTEXITCODE;

exit $exitCode;