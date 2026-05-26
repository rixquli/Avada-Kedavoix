$ErrorActionPreference = 'Stop'

Set-Location $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
  $venvCreated = $false

  foreach ($version in @('3.13', '3.10')) {
    & py -$version -m venv .venv
    if ($LASTEXITCODE -eq 0) {
      $venvCreated = $true
      break
    }
  }

  if (-not $venvCreated) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
      exit $LASTEXITCODE
    }
  }
}

& $venvPython -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

& $venvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

& $venvPython -m PyInstaller --clean --noconfirm AvadaKedavoix.spec
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}