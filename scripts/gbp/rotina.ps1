# Rotina diaria do Perfil do Google, disparada pelo Agendador de Tarefas.
# Roda o Claude sem interface com a skill perfil-google e so libera a ferramenta
# scripts/gbp/gbp.py, leitura de arquivos e escrita em tmp/gbp. Ao final mostra
# uma notificacao do Windows com a primeira linha do relatorio do dia.
#
# Registrar a tarefa (uma vez):  .\scripts\gbp\rotina.ps1 -Registrar
# Rodar agora, a mao:            .\scripts\gbp\rotina.ps1

param([switch]$Registrar)

$ErrorActionPreference = "Stop"
$Gestao = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$NomeTarefa = "Sir Fisher - Perfil do Google"

if ($Registrar) {
    $acao = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSCommandPath`"" `
        -WorkingDirectory $Gestao
    $gatilho = New-ScheduledTaskTrigger -Daily -At "10:00"
    $config = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Hours 1) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $NomeTarefa -Action $acao -Trigger $gatilho -Settings $config `
        -Description "Responde avaliacoes e cuida da ficha do Sir Fisher no Google (gestao/docs/ROTINA_PERFIL_GOOGLE.md)" `
        -Force | Out-Null
    Write-Output "Tarefa '$NomeTarefa' registrada: todo dia as 10h (roda depois, se o PC estiver desligado nesse horario)."
    exit 0
}

Set-Location $Gestao
$env:PYTHONIOENCODING = "utf-8"
$hoje = Get-Date
$data = $hoje.ToString("yyyy-MM-dd")
$pasta = Join-Path $Gestao "tmp\gbp\rotina"
New-Item -ItemType Directory -Force $pasta | Out-Null
$log = Join-Path $pasta "$data.log"
$relatorio = Join-Path $pasta "$data.md"

$tarefas = @("diaria")
if ($hoje.DayOfWeek -eq "Monday") { $tarefas += "segunda-feira" }
if ($hoje.Day -eq 1) { $tarefas += "dia 1 do mes" }
$dias = @{Monday="segunda-feira";Tuesday="terca-feira";Wednesday="quarta-feira";Thursday="quinta-feira";Friday="sexta-feira";Saturday="sabado";Sunday="domingo"}
$prompt = "Execute a rotina do Perfil do Google seguindo a skill perfil-google (.claude/skills/perfil-google/SKILL.md; leia esse arquivo primeiro). Hoje e $data, $($dias[[string]$hoje.DayOfWeek]). Partes da rotina de hoje: $($tarefas -join ', '). Escreva o relatorio em tmp/gbp/rotina/$data.md."

$claude = (Get-Command claude -ErrorAction SilentlyContinue).Source
if (-not $claude) { $claude = Join-Path $env:USERPROFILE ".local\bin\claude.exe" }

$permitidas = @(
    "Bash(python scripts/gbp/gbp.py:*)",
    "PowerShell(python scripts/gbp/gbp.py:*)",
    "Read", "Glob", "Grep",
    "Edit(tmp/gbp/**)"
)
"=== $(Get-Date -Format s) inicio ($($tarefas -join ', '))" | Out-File -Append -Encoding utf8 $log
# No PowerShell 5.1, qualquer linha do Claude na saida de erro (avisos) vira
# ErrorRecord; com "Stop" isso derrubaria a rotina. Avisos vao so para o log.
$ErrorActionPreference = "Continue"
& $claude -p $prompt --allowedTools @permitidas --max-turns 80 2>&1 |
    ForEach-Object { "$_" } | Out-File -Append -Encoding utf8 $log
"=== $(Get-Date -Format s) fim (codigo $LASTEXITCODE)" | Out-File -Append -Encoding utf8 $log

$resumo = "A rotina rodou, mas nao deixou relatorio. Veja $log"
if (Test-Path $relatorio) {
    $linha = (Get-Content $relatorio -Encoding utf8 -TotalCount 1) -replace "^RESUMO:\s*", ""
    if ($linha) { $resumo = $linha }
}
$titulo = if ($resumo -match "^ATEN") { "Perfil do Google: atencao" } else { "Perfil do Google" }

try {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent(
        [Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $textos = $xml.GetElementsByTagName("text")
    $textos.Item(0).AppendChild($xml.CreateTextNode($titulo)) | Out-Null
    $textos.Item(1).AppendChild($xml.CreateTextNode($resumo)) | Out-Null
    $aviso = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier(
        "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe").Show($aviso)
} catch {
    "notificacao falhou: $_" | Out-File -Append -Encoding utf8 $log
}
