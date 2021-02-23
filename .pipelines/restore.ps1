Write-Host "Start build ..."
Write-Host  "Global python paths  ..."
& where.exe python
Write-Host  "Global node/npm paths  ..."
& where.exe node
& where.exe npm

Write-Host "Global python version"
& python -V

Write-Host "Global pip version"
& python -m pip -V

Write-Host "Global node version"
& node -v

Write-Host "Global npm version"
& npm -v

$exitCode = 0;

Write-Host "start: try install latest pip and wheel version"
& python -m ensurepip --default-pip
& python -m pip install --upgrade pip setuptools wheel --no-warn-script-location
Write-Host "done: try install latest pip and wheel version"

Write-Host "start: try install latest npm version"
& npm install npm@latest -g
Write-Host "done: try install latest npm version"

# Do not update $exitCode because we do not want to fail if install latest pip, wheel and npm version fails.

Write-Host 'start: pip install -e ".[test, examples]"'
& python -m pip install -e ".[test, examples]" --no-warn-script-location
Write-Host 'done: pip install -e ".[test, examples]"'
$exitCode += $LASTEXITCODE;

exit $exitCode