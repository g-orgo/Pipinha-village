@echo off
rem Pipinha's Village installer (Windows). Same behavior as install.sh.
rem Close your launcher and Minecraft first. Three ways to run it:
rem  a) Put this file and Modpack.zip in the profile folder and double click it.
rem  b) Put this file and the GitHub zip (Code > Download ZIP) in the profile
rem     folder and drag the zip onto this file.
rem  c) From a clone of the GitHub repository, drag the profile folder onto
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

Write-Host 'Close your launcher and Minecraft before running this installer.'

# 1) Find the source folder, the zip and the target instance.
$isRepoMode = [bool]($arg -and (Test-Path -LiteralPath $arg -PathType Container))
if ($isRepoMode) {
    # Repository clone mode: this file lives in the clone, the argument is the profile.
    $src = $here
    $target = $arg.TrimEnd('\', '/')
    $zip = $null
} else {
    $target = $here
    $zip = $null
    if ($arg -and (Test-Path -LiteralPath $arg -PathType Leaf)) { $zip = $arg }
    if (-not $zip -and (Test-Path -LiteralPath (Join-Path $here 'Modpack.zip') -PathType Leaf)) {
        $zip = Join-Path $here 'Modpack.zip'
    }
    if (-not $zip) {
        $gh = Get-ChildItem -LiteralPath $here -Filter 'Pipinha-village*.zip' -File | Select-Object -First 1
        if ($gh) { $zip = $gh.FullName }
    }
    if (-not $zip) {
        Write-Host 'Zip not found (no Modpack.zip next to this file). Nothing to install.'
        return
    }
}

# 2) Version check before anything is touched.
$meta = $null
$gotMc = $null
$gotLoader = $null
$wantLoader = $null
$cfFile = Join-Path $target 'minecraftinstance.json'
$prismFile = Join-Path $target 'mmc-pack.json'
if (Test-Path -LiteralPath $cfFile -PathType Leaf) {
    $j = Get-Content -LiteralPath $cfFile -Raw | ConvertFrom-Json
    $meta = 'CurseForge minecraftinstance.json'
    $gotMc = $j.gameVersion
    $gotLoader = $j.baseModLoader.name
    $wantLoader = 'neoforge-21.1.265'
} elseif (Test-Path -LiteralPath $prismFile -PathType Leaf) {
    $j = Get-Content -LiteralPath $prismFile -Raw | ConvertFrom-Json
    $meta = 'Prism/MultiMC mmc-pack.json'
    $comps = @($j.components)
    $mcC = $comps | Where-Object { $_.uid -eq 'net.minecraft' } | Select-Object -First 1
    $nfC = $comps | Where-Object { $_.uid -eq 'net.neoforged' } | Select-Object -First 1
    $gotMc = $mcC.version
    $gotLoader = $nfC.version
    $wantLoader = '21.1.265'
}
if ($meta) {
    if ($gotMc -ne '1.21.1' -or $gotLoader -ne $wantLoader) {
        Write-Host "Profile mismatch ($meta): found Minecraft '$gotMc' and loader '$gotLoader'."
        Write-Host "Expected Minecraft '1.21.1' and loader '$wantLoader'."
        $ans = Read-Host 'Continue anyway? [y/N]'
        if ($ans -notmatch '^(y|yes)$') {
            Write-Host 'Aborted. Nothing was changed.'
            return
        }
    }
} else {
    Write-Host 'No launcher metadata found (Modrinth App or another launcher).'
    Write-Host 'Make sure the profile is Minecraft 1.21.1 with NeoForge 21.1.265.'
}

# 3) Game folder: Prism/MultiMC keep the game in minecraft or .minecraft next to instance.cfg.
$gameDir = $target
if (Test-Path -LiteralPath (Join-Path $target 'instance.cfg') -PathType Leaf) {
    if (Test-Path -LiteralPath (Join-Path $target 'minecraft') -PathType Container) {
        $gameDir = Join-Path $target 'minecraft'
    } elseif (Test-Path -LiteralPath (Join-Path $target '.minecraft') -PathType Container) {
        $gameDir = Join-Path $target '.minecraft'
    }
}
Write-Host "Game folder: $gameDir"

try {
    # 4) Extract the zip (or use the repository clone) and find the pack root.
    if (-not $isRepoMode) {
        Write-Host "Extracting $zip"
        # Short temp path: keeps deep datapack paths under the 260 character limit.
        $tmp = Join-Path $env:TEMP 'pipinha_install_tmp'
        if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force }
        # ZipFile is much faster than Expand-Archive on a zip with tens of thousands of files.
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [IO.Compression.ZipFile]::ExtractToDirectory($zip, $tmp)
        $src = $tmp
        # The GitHub zip wraps everything in one top folder (Pipinha-village-1.21.1).
        if (-not (Test-Path -LiteralPath (Join-Path $src 'mods'))) {
            $top = Get-ChildItem -LiteralPath $src -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'mods') } | Select-Object -First 1
            if ($top) { $src = $top.FullName }
        }
    }
    foreach ($need in 'mods', 'kubejs') {
        if (-not (Test-Path -LiteralPath (Join-Path $src $need) -PathType Container)) {
            Write-Host "No $need folder in $src. Nothing was changed."
            return
        }
    }

    # 5) Replace mods, kubejs, resource packs and moonlight datapacks with the pack's.
    foreach ($dir in 'mods', 'kubejs', 'resourcepacks', 'moonlight-global-datapacks') {
        $p = Join-Path $gameDir $dir
        if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Recurse -Force }
    }
    Write-Host "Copying files into $gameDir"
    $xd = @('.git', '.github', (Join-Path $src 'docs'), (Join-Path $src 'tools'), (Join-Path $src 'custom-mods'))
    $xf = @('.gitignore', '.gitattributes', (Join-Path $src 'options.txt'), (Join-Path $src 'install.bat'),
        (Join-Path $src 'install.sh'), (Join-Path $src 'README.md'), (Join-Path $src 'AGENTS.md'),
        (Join-Path $src 'CLAUDE.md'), (Join-Path $src 'HANDOFF.md'))
    robocopy "$src" "$gameDir" /E /R:1 /W:1 /NFL /NDL /NJH /NJS /NP /XD $xd /XF $xf | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed with code $LASTEXITCODE" }

    # 6) options.txt: keep the player's file, only the resource pack lines come from the pack.
    $packOpt = Join-Path $src 'options.txt'
    $gameOpt = Join-Path $gameDir 'options.txt'
    $utf8 = New-Object Text.UTF8Encoding($false)
    if (Test-Path -LiteralPath $packOpt -PathType Leaf) {
        if (-not (Test-Path -LiteralPath $gameOpt -PathType Leaf)) {
            Copy-Item -LiteralPath $packOpt -Destination $gameOpt
        } else {
            $packLines = [IO.File]::ReadAllLines($packOpt, [Text.Encoding]::UTF8)
            $rp = $packLines | Where-Object { $_ -like 'resourcePacks:*' } | Select-Object -First 1
            $irp = $packLines | Where-Object { $_ -like 'incompatibleResourcePacks:*' } | Select-Object -First 1
            $out = New-Object 'System.Collections.Generic.List[string]'
            $rpDone = $false
            $irpDone = $false
            foreach ($line in [IO.File]::ReadAllLines($gameOpt, [Text.Encoding]::UTF8)) {
                if ($line -like 'resourcePacks:*') {
                    if ($rp) { $out.Add($rp) }
                    $rpDone = $true
                } elseif ($line -like 'incompatibleResourcePacks:*') {
                    if ($irp) { $out.Add($irp) }
                    $irpDone = $true
                } else {
                    $out.Add($line)
                }
            }
            if (-not $rpDone -and $rp) { $out.Add($rp) }
            if (-not $irpDone -and $irp) { $out.Add($irp) }
            [IO.File]::WriteAllLines($gameOpt, $out, $utf8)
        }
    }
} finally {
    # 7) Remove the temp folder, also when something failed.
    if ($tmp -and (Test-Path -LiteralPath $tmp)) { Remove-Item -LiteralPath $tmp -Recurse -Force }
}

Write-Host ''
Write-Host 'Done. Files installed.'
Write-Host 'Recommended: 8 GB of allocated memory in the profile (no more on a 16 GB PC).'
Write-Host 'Java settings were not changed.'
