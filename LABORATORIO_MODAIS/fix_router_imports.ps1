$file = "E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\apollo_modal_engine.py"
$content = Get-Content $file -Raw
$new_imports = @"
import backend.cloud_tools.engines.stable_audio_engine
import backend.cloud_tools.engines.minimax_engine
import backend.cloud_tools.engines.ace_step_15_engine
"@
$content = $content -replace "import backend\.cloud_tools\.engines\.ace_step_comfy_engine", ("import backend.cloud_tools.engines.ace_step_comfy_engine`n" + $new_imports)
Set-Content -Path $file -Value $content -Encoding UTF8
Write-Output "Imports added."
