@echo off
rem Society: Sunlit Valley - Pipinha's Village Edition installer (Windows).
rem Turns a default Society: Sunlit Valley instance into Pipinha's Village Edition.
rem Close Minecraft and the CurseForge app first. Three ways to run it:
rem  a) Put this file and Modpack.zip in the instance folder and double click it.
rem  b) Put this file and the GitHub zip (Code > Download ZIP) in the instance
rem     folder and drag the zip onto this file.
rem  c) From a clone of the GitHub repository, drag the instance folder onto
rem     this file.
setlocal
cd /d "%~dp0"
set "INSTDIR=%~dp0"
set "SELF=%~f0"
set "ARG=%~1"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=[IO.File]::ReadAllText($env:SELF); iex $s.Substring($s.LastIndexOf('#' + 'PS_START'))"
echo.
pause
exit /b

#PS_START
$ErrorActionPreference = 'Stop'
$here = $env:INSTDIR.TrimEnd('\', '/')
$arg = $env:ARG
$tmp = $null

# 1) Find the source folder and the target instance.
if ($arg -and (Test-Path -LiteralPath $arg -PathType Container)) {
    # Mode c: this file lives in a repository clone, the argument is the instance.
    $src = $here
    $inst = $arg.TrimEnd('\', '/')
} else {
    $inst = $here
    $zip = $arg
    if (-not $zip) { $zip = Join-Path $here 'Modpack.zip' }
    if (-not (Test-Path -LiteralPath $zip)) {
        $gh = Get-ChildItem -LiteralPath $here -Filter 'Pipinha-village*.zip' | Select-Object -First 1
        if ($gh) { $zip = $gh.FullName }
    }
    if (-not (Test-Path -LiteralPath $zip)) {
        Write-Host "Zip not found ($zip). Nothing to install."
        return
    }
    Write-Host "Extracting $zip"
    $tmp = Join-Path $inst '.pipinha_install_tmp'
    if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force }
    Expand-Archive -LiteralPath $zip -DestinationPath $tmp -Force
    $src = $tmp
    # The GitHub zip wraps everything in one top folder (Pipinha-village-main).
    if (-not (Test-Path -LiteralPath (Join-Path $src 'mods'))) {
        $top = Get-ChildItem -LiteralPath $src -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'mods') } | Select-Object -First 1
        if ($top) { $src = $top.FullName }
    }
}
if (-not (Test-Path -LiteralPath (Join-Path $src 'mods'))) {
    Write-Host "No mods folder found in $src. Nothing to install."
    return
}

# 2) Replace mods, resource packs and KubeJS with the ones from the source.
# kubejs is wiped too: the source carries the full folder, and files the default
# Sunlit Valley ships but this edition removed (Beach Party recipes and menus)
# would otherwise stay behind.
foreach ($dir in 'mods', 'resourcepacks', 'kubejs') {
    $p = Join-Path $inst $dir
    if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Recurse -Force }
}
Write-Host "Copying files into $inst"
robocopy "$src" "$inst" /E /R:1 /W:1 /NFL /NDL /NJH /NJS /NP /XD .git .github /XF .gitignore .gitattributes install.bat | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed with code $LASTEXITCODE" }
if ($tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force }
Write-Host 'Files installed.'

# 3) Java settings are left untouched: the profile uses the CurseForge default
# (G1 garbage collector). ZGC was removed on 2026-10-14 (owner request) because
# it needs too much RAM. If a "-XX:+Use...GC" flag was added manually before,
# remove it under CurseForge > right click the profile > Profile Options >
# Additional Arguments (leave the field empty to use the default).

Write-Host ''
Write-Host 'Done. Java arguments were not changed (default G1 GC).'
