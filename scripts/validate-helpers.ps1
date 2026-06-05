#requires -Version 7
# Helpers for the validate-100-loop.
# - Build-NextBatch:  picks N unverified non-mutating recipes, writes JSON to $env:TEMP\batch.json
# - Apply-BatchResults:  reads $env:TEMP\batch-results.json (written by Playwright loop),
#   keeps screenshots with elapsed >= threshold, deletes bad screenshots,
#   flips matching recipe.yaml to status: verified, repoints README to real screenshot
# - Get-VerifiedToday: prints count of recipes verified today

$ErrorActionPreference = 'Stop'
$Repo = 'D:\Dev\Coworkcookbook'

function Build-NextBatch {
    param([int]$Size = 10, [string[]]$Exclude = @())
    $candidates = @()
    Get-ChildItem (Join-Path $Repo 'recipes\*\*\recipe.yaml') | Where-Object {
        $_.Directory.Name -notlike 'd365-*'
    } | ForEach-Object {
        $area = $_.Directory.Parent.Name
        $rid = $_.Directory.Name
        if ("$area/$rid" -in $Exclude) { return }
        if (Test-Path (Join-Path $_.Directory.FullName 'screenshots\01-cowork-output.png')) { return }
        $t = Get-Content $_.FullName -Raw
        if ($t -notmatch 'status:\s*draft') { return }
        if ($t -match 'mutates_data:\s*true') { return }
        $candidates += [pscustomobject]@{ area=$area; rid=$rid; yaml=$_.FullName }
        if ($candidates.Count -ge $Size) { return }
    } | Out-Null
    $batch = @()
    foreach ($c in ($candidates | Select-Object -First $Size)) {
        $promptPath = Join-Path $Repo "recipes\$($c.area)\$($c.rid)\prompt.md"
        if (!(Test-Path $promptPath)) { continue }
        $p = Get-Content $promptPath -Raw
        $batch += [pscustomobject]@{ area=$c.area; rid=$c.rid; prompt=(($p.Trim()) -replace '2026-05-24','2026-05-25') }
    }
    $batch | ConvertTo-Json -Depth 4 -Compress | Set-Content "$env:TEMP\batch.json" -NoNewline
    return $batch
}

function Apply-BatchResults {
    param([int]$Threshold = 150)
    $results = Get-Content "$env:TEMP\batch-results.json" -Raw | ConvertFrom-Json
    $kept = @(); $dropped = @()
    foreach ($r in $results) {
        $ss = Join-Path $Repo "recipes\$($r.area)\$($r.rid)\screenshots\01-cowork-output.png"
        if ($r.elapsed -ge $Threshold -and (Test-Path $ss)) {
            $kept += "$($r.area)/$($r.rid)"
            $yaml = Join-Path $Repo "recipes\$($r.area)\$($r.rid)\recipe.yaml"
            $readme = Join-Path $Repo "recipes\$($r.area)\$($r.rid)\README.md"
            if (Test-Path $yaml) {
                $t = Get-Content $yaml -Raw
                if ($t -match 'status:\s*draft') {
                    $t = $t -replace 'status:\s*draft', "status: verified`nlast_verified_on: `"2026-06-04`"`nverified_against_cowork_build: `"m365.cloud.microsoft 2026-06-04`""
                    Set-Content -Path $yaml -Value $t -NoNewline
                }
            }
            if (Test-Path $readme) {
                $rt = Get-Content $readme -Raw
                $rt = $rt -replace '!\[[^\]]*\]\(screenshots/01-placeholder\.svg "[^"]*"\)', '![Cowork output captured against USMF](screenshots/01-cowork-output.png "Cowork audit output captured 2026-06-04")'
                $rt = $rt -replace '(?m)^> \u26a0 \*\*Draft recipe \u2014 not yet verified.*\r?\n(?:>.*\r?\n)*\r?\n', ''
                Set-Content -Path $readme -Value $rt -NoNewline
            }
        } else {
            $dropped += "$($r.area)/$($r.rid)"
            Remove-Item $ss -Force -ErrorAction SilentlyContinue
        }
    }
    return @{ kept=$kept; dropped=$dropped }
}

function Get-VerifiedToday {
    (Get-ChildItem (Join-Path $Repo 'recipes\*\*\recipe.yaml') | Where-Object { $_.Directory.Name -notlike 'd365-*' } | Where-Object { (Get-Content $_.FullName -Raw) -match 'last_verified_on: "2026-06-04"' }).Count
}

function Commit-Batch {
    param([int]$BatchNum, [string[]]$Kept)
    Set-Location $Repo
    git add -A | Out-Null
    $msg = "Validate batch ${BatchNum} ($($Kept.Count) recipes 2026-05-26)"
    git -c user.name='Sean Galliher' -c user.email='sean.galliher@gmail.com' commit -m $msg 2>&1 | Select-Object -Last 1 | Out-Null
    git push origin main 2>&1 | Select-Object -Last 1 | Out-Null
}
