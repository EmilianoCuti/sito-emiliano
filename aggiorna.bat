@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==============================================
echo   Emiliano Cuti - archivio di inchieste
echo   Aggiornamento del sito
echo ==============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo Python 3 non e' installato.
  echo Scaricalo da https://www.python.org/downloads/ e riprova.
  pause
  exit /b 1
)

python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
  echo Serve Python 3.10 o superiore.
  echo Aggiorna Python da https://www.python.org/downloads/ e riprova.
  pause
  exit /b 1
)

echo Ricalcolo l'Atlante...
python build_data.py
if errorlevel 1 (
  echo Errore in build_data.py: il sito non e' stato aggiornato.
  pause
  exit /b 1
)

echo Costruisco le pagine...
python build.py
if errorlevel 1 (
  echo Errore in build.py: il sito non e' stato aggiornato.
  pause
  exit /b 1
)

echo.
echo Fatto. Apro il sito...
start "" "sito\index.html"
echo La cartella da pubblicare e': sito\
pause
