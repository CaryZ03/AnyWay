param(
    [ValidateSet('agent','plugin','knowledge','workflow','llm','aiagent','all')]
    [string]$App = 'all',
    [switch]$Quiet
)

# choose python: VIRTUAL_ENV > CONDA_PREFIX > PATH
if (-not [string]::IsNullOrWhiteSpace($env:VIRTUAL_ENV)) {
    $python = Join-Path $env:VIRTUAL_ENV 'Scripts\python.exe'
} elseif (-not [string]::IsNullOrWhiteSpace($env:CONDA_PREFIX)) {
    $python = Join-Path $env:CONDA_PREFIX 'python.exe'
} else {
    $cmdPython = Get-Command python -ErrorAction SilentlyContinue
    if ($cmdPython) { $python = $cmdPython.Source } else { $python = 'python' }
}

Write-Host "=== 运行 $App 模块的单元+集成测试 === (python: $python)" -ForegroundColor Cyan

switch ($App) {
    'agent'     { $pytestArgs = 'apps/agent/tests' }
    'plugin'    { $pytestArgs = 'apps/plugin/tests' }
    'knowledge' { $pytestArgs = 'apps/knowledge/tests' }
    'workflow'  { $pytestArgs = 'apps/workflow/tests' }
    'llm'       { $pytestArgs = 'apps/llm/tests' }
    'aiagent'   { $pytestArgs = 'aiagent/tests' }
    'all'       { $pytestArgs = '.' }
}

$argList = @('-m','pytest', $pytestArgs)
if ($Quiet) { $argList += '-q' }

$proc = Start-Process -FilePath $python -ArgumentList $argList -NoNewWindow -Wait -PassThru
exit $proc.ExitCode
