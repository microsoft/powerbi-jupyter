$exitCode = 0;

# TODO: Run front-end test script when available

# Run python kernel test scripts
Write-Host "start: pytest powerbiclient"
& python -m pytest powerbiclient --cov -v
Write-Host "done: pytest powerbiclient"
$exitCode += $LASTEXITCODE;

exit $exitCode;