$exitCode = 0;

# TODO: support python kernel testing in CDPX pipeline without using prepack script
# Run python kernel test scripts
# Write-Host "start: pytest powerbiclient"
# & python -m pytest powerbiclient --cov -v
# Write-Host "done: pytest powerbiclient"
# $exitCode += $LASTEXITCODE;

exit $exitCode;