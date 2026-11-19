#!/bin/bash
# Aggiorna il sito dopo aver modificato i testi o i dati.
# Doppio clic su questo file. Se macOS lo blocca: tasto destro > Apri.

cd "$(dirname "$0")" || exit 1

echo "=============================================="
echo "  Emiliano Cuti - archivio di inchieste"
echo "  Aggiornamento del sito"
echo "=============================================="
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 non e' installato."
  echo "Scaricalo da https://www.python.org/downloads/ e riprova."
  echo
  read -n 1 -s -r -p "Premi un tasto per chiudere."
  exit 1
fi

if ! python3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >/dev/null 2>&1; then
  echo "Serve Python 3.10 o superiore."
  echo "Aggiorna Python da https://www.python.org/downloads/ e riprova."
  echo
  read -n 1 -s -r -p "Premi un tasto per chiudere."
  exit 1
fi

echo "Ricalcolo l'Atlante..."
python3 build_data.py || {
  echo "Errore in build_data.py: il sito non e' stato aggiornato."
  read -n 1 -s -r -p "Premi un tasto per chiudere."
  exit 1
}

echo "Costruisco le pagine..."
python3 build.py || {
  echo "Errore in build.py: il sito non e' stato aggiornato."
  read -n 1 -s -r -p "Premi un tasto per chiudere."
  exit 1
}

echo
echo "Fatto. Apro il sito..."
open sito/index.html
echo "La cartella da pubblicare e': sito/"
echo
read -n 1 -s -r -p "Premi un tasto per chiudere."
