$exitCode = 0;

Write-Host "start: python setup.py bdist_wheel"
& python setup.py bdist_wheel
Write-Host "done: python setup.py bdist_wheel"
$exitCode += $LASTEXITCODE;

Write-Host "start: Get content of current folder"
& dir
Write-Host "done: Get content of current folder"

exit $exitCode