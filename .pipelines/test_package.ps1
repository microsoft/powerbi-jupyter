$package = Get-Item -Path dist/*.whl
$packPath = $package.FullName
Write-Host "Package full name: $packPath"

$exitCode = 0;

Write-Host "start: verify package name"
$version = [Environment]::GetEnvironmentVariable("PowerBIJupyterVersion", "User")
$expectedPackNamePattern = "^powerbiclient-$version-(.*).whl$"
$packName = $package.Name
if (-Not ($packName -match $expectedPackNamePattern)) {
    Write-Host "Error: expected package name to match pattern: '$expectedPackNamePattern', but got '$packName'"
    $exitCode += 1;
    exit $exitCode
}
Write-Host "done: verify package name"

Write-Host "start: pip install package in test environment"
mkdir testProject
cd .\testProject
python -m pip install "$packPath"
cd ..
rm -r .\testProject\
Write-Host "done: pip install package in test environment"

$exitCode += $LASTEXITCODE;

exit $exitCode
