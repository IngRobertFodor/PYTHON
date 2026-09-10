@echo off
SETLOCAL

echo ============================================================
echo  Land Research Invest - Zastavenie servera
echo ============================================================
echo.
echo Zastavujem server na porte 5001...
echo.

powershell -NoProfile -Command "$pids = Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if ($pids) { $pids | ForEach-Object { $n = (Get-Process -Id $_ -ErrorAction SilentlyContinue).ProcessName; Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue; Write-Host \"  [OK] Zastaveny proces: PID $_ ($n)\" }; Start-Sleep 1; Write-Host ''; Write-Host '[OK] Server zastaveny.' } else { Write-Host '[INFO] Nic nebezalo na porte 5001 - server uz bol zastaveny.' }"

echo.
echo Mozete zavriet toto okno.
echo.
timeout /t 4 >nul
