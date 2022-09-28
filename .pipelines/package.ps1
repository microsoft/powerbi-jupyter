$exitCode = 0;

Write-Host "start: python setup.py bdist_wheel"
& python setup.py bdist_wheel
Write-Host "done: python setup.py bdist_wheel"
$exitCode += $LASTEXITCODE;

if ($exitCode -ne 0) {
    Write-Host "Failed to create wheel file"
    exit $exitCode
}

Write-Host "start: Get content of current folder"
& dir
Write-Host "done: Get content of current folder"

$exitCode += $LASTEXITCODE;

Write-Host "start: test package"
& .\.pipelines\test_package.ps1
Write-Host "done: test package"

$exitCode += $LASTEXITCODE;

exit $exitCode