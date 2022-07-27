try {
    # package.json is in root folder, while version.ps1 runs in .pipelines folder.
    # we will use the npm version as it will be used to set the tag as latest in npm
    $version = (Get-Content "package.json") -join "`n" | ConvertFrom-Json | Select -ExpandProperty "version"
    $buildNumber = "$version"
  
    Write-Host "Build Number is" $buildNumber
  
    # This will allow you to use it from env var in later steps of the same phase
    [Environment]::SetEnvironmentVariable("PowerBIJupyterVersion", $version, "User")
    [Environment]::SetEnvironmentVariable("CustomBuildNumber", $buildNumber, "User")
    Write-Host "##vso[build.updatebuildnumber]${buildNumber}"                         # This will update build number on your build
  }
  catch {
    Write-Error $_.Exception
    exit 1;
  }