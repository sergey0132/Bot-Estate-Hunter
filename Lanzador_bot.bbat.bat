@echo off
TITLE Cazador de Pisos - BOT AUTOMATICO
COLOR 0A

echo ==========================================
echo      INICIANDO PROTOCOLO DE CAZA... 🏠🔫
echo ==========================================

:: 1. ABRIR EDGE EN MODO DEBUG
echo [1/2] Abriendo Microsoft Edge en puerto 9222...
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium\EdgeProfile"

timeout /t 5 /nobreak >nul

:: 2. ARRANCAR EL SCRIPT DE PYTHON
echo [2/2] Localizando el "Cerebro" (Python)...

:: Comprobamos si el script está en la carpeta actual
if exist "Real_Estate_Hunter.py" (
    echo ✅ Script detectado en la carpeta actual.
    python "Real_Estate_Hunter.py"
) else (
    echo ⚠️ No se encuentra el script en esta carpeta.
    echo 🔧 IMPORTANTE: Si el .bat no esta en la misma carpeta, cambia la ruta abajo:
    cd /d "TU_RUTA_AQUI"
    python "Real_Estate_Hunter.py"
)

echo.
echo ⚠️ El proceso ha terminado.
pause