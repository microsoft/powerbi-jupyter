$exitCode = 0;

Write-Host "start: npm run build"
& npm run build
Write-Host "done: npm run build"
$exitCode += $LASTEXITCODE;

if ($exitCode -ne 0) {
    Write-Host "npm run build failed with code $($LASTEXITCODE)"
    exit $exitCode
}

$PowerBIJupyterRoot = "$PSScriptRoot\..\" | Resolve-Path;
$CopySource = "$PowerBIJupyterRoot\powerbiclient\nbextension\static\*"
$CopyTarget = "$PowerBIJupyterRoot\dist\"

Write-Host "start: Copy required scripts from $CopySource to $CopyTarget"
Copy-Item -Path $CopySource -Destination $CopyTarget
Write-Host "finished: Copy required scripts from $CopySource to $CopyTarget"

if ($exitCode -ne 0) {
    Write-Host "Copy required scripts failed with code $($LASTEXITCODE)"
    exit $exitCode
}

Write-Host "start: Get dist folder files"
& dir "dist"
$hasAnySubdir = (Get-ChildItem -Force -Directory $CopyTarget).Count -gt 0
If ($hasAnySubdir) {
    Write-Host "Error: dist folder has subfolders!"
    $exitCode += 1;
}
Write-Host "Done: Get dist folder files"

exit $exitCode