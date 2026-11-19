#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_diretta.py — alimenta la sezione "News in diretta" della Finanza.

La diretta pubblica SOLO i post dei cron job (edizioni FINANZA OGGI 10/14/18),
a partire dalla pubblicazione del sito. Niente archivio storico: il feed parte
vuoto e si popola con le nuove edizioni.

Uso (lo chiamerà il cron, dopo la pubblicazione del sito):
  python add_diretta.py --post "C:/.../fb_post_2026-11-20_1000.txt"
  python add_diretta.py --post file.txt --data 2026-11-20 --ora 10:00 --no-build

Opzionale/manuale (NON usato per il backfill iniziale):
  python add_diretta.py --import-archive "C:/.../hermes/tools"

I post vengono analizzati (intestazione, bullet con orario e fonte, sintesi,
prospettiva, fonti) e salvati in content/diretta.json, ordinati dal più recente.
Deduplica per (data, ora): una nuova edizione con la stessa chiave sostituisce
la precedente. Dopo l'aggiornamento rigenera il sito (build.py), salvo --no-build.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIRETTA_REL = os.path.join("content", "diretta.json")

MESI = {
    "gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04",
    "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08",
    "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12",
}
RE_NOME = re.compile(r"^fb_post_(\d{4}-\d{2}-\d{2})_(\d{4})\.txt$")
RE_FINESTRA = re.compile(r"finestra\s+(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", re.I)
RE_ORA_HEADER = re.compile(r",\s*(\d{1,2}:\d{2})")
RE_DATA_HEADER = re.compile(r"(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})")
RE_CODA = re.compile(r"\((\d{1,2}:\d{2}),\s*([^)]+)\)\s*$")


def da_nome_file(nome):
    """(data ISO, ora HH:MM) da un nome canonico fb_post_DATA_ORA.txt, altrimenti None.

    Il pattern stretto esclude backup e varianti (_backup, _v2, _prev, ...).
    """
    m = RE_NOME.match(os.path.basename(nome))
    if not m:
        return None
    data, hhmm = m.group(1), m.group(2)
    return data, "%s:%s" % (hhmm[:2], hhmm[2:])


def _data_da_header(testo):
    m = RE_DATA_HEADER.search(testo)
    if not m:
        return None
    giorno, mese_nome, anno = m.group(1), m.group(2).lower(), m.group(3)
    mese = MESI.get(mese_nome)
    if not mese:
        return None
    return "%s-%s-%02d" % (anno, mese, int(giorno))


def parse_post(testo, data=None, ora=None):
    """Analizza un post FINANZA OGGI in un record strutturato per la diretta."""
    righe = testo.splitlines()
    intestazione = ""
    for r in righe:
        if "FINANZA OGGI" in r:
            intestazione = r.strip()
            break

    finestra = ""
    m = RE_FINESTRA.search(intestazione or testo)
    if m:
        finestra = "%s-%s" % (m.group(1), m.group(2))
    if not ora:
        m = RE_ORA_HEADER.search(intestazione)
        if m:
            ora = m.group(1)
    if not data:
        data = _data_da_header(intestazione or testo)
    if not data or not ora:
        raise ValueError("data/ora non ricavabili dal post (passare --data/--ora)")
    if len(ora) == 4 and ":" not in ora:
        ora = "%s:%s" % (ora[:2], ora[2:])

    voci, sintesi, prospettiva, fonti = [], [], [], []
    sezione = "voci"
    for r in righe:
        s = r.strip()
        if not s:
            continue
        if "SINTESI MERCATO" in s:
            sezione = "sintesi"
            continue
        if "PROSPETTIVA" in s:
            sezione = "prospettiva"
            continue
        if re.match(r"^[—\-]\s*Fonti:", s):
            resto = re.sub(r"^[—\-]\s*Fonti:\s*", "", s)
            fonti = [f.strip() for f in resto.split(",") if f.strip()]
            continue
        if s.startswith("•") or s.startswith("- "):
            bullet = s.lstrip("•- ").strip()
            if sezione == "voci":
                m = RE_CODA.search(bullet)
                if m:
                    voci.append({
                        "testo": bullet[:m.start()].strip(),
                        "ora": m.group(1),
                        "fonte": m.group(2).strip(),
                    })
                else:
                    voci.append({"testo": bullet, "ora": "", "fonte": ""})
            elif sezione == "sintesi":
                sintesi.append(bullet)
            elif sezione == "prospettiva":
                prospettiva.append(bullet)

    return {
        "slug": "%s-%s" % (data, ora.replace(":", "")),
        "data": data,
        "ora": ora,
        "finestra": finestra,
        "voci": voci,
        "sintesi": " ".join(sintesi).strip(),
        "prospettiva": " ".join(prospettiva).strip(),
        "fonti": fonti,
        "testo": testo.strip(),
    }


def unisci(notizie, voce):
    """Aggiunge/sostituisce per (data, ora) e riordina dal più recente."""
    per_chiave = {(n["data"], n["ora"]): n for n in notizie}
    per_chiave[(voce["data"], voce["ora"])] = voce
    return sorted(per_chiave.values(), key=lambda n: (n["data"], n["ora"]), reverse=True)


def carica_diretta(root=HERE):
    path = os.path.join(root, DIRETTA_REL)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return json.load(fh).get("diretta", [])


def salva_diretta(notizie, root=HERE):
    path = os.path.join(root, DIRETTA_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"diretta": notizie}, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


def aggiungi_post(file_post, data=None, ora=None, root=HERE):
    with open(file_post, encoding="utf-8") as fh:
        testo = fh.read()
    if not data or not ora:
        dn = da_nome_file(file_post)
        if dn:
            data = data or dn[0]
            ora = ora or dn[1]
    voce = parse_post(testo, data=data, ora=ora)
    notizie = unisci(carica_diretta(root), voce)
    salva_diretta(notizie, root)
    return voce, notizie


def importa_archivio(cartella, root=HERE):
    """Importa in blocco i post canonici di una cartella (uso manuale)."""
    notizie = carica_diretta(root)
    aggiunte = 0
    for nome in sorted(os.listdir(cartella)):
        dn = da_nome_file(nome)
        if not dn:
            continue
        try:
            with open(os.path.join(cartella, nome), encoding="utf-8") as fh:
                voce = parse_post(fh.read(), data=dn[0], ora=dn[1])
        except (ValueError, OSError):
            continue
        notizie = unisci(notizie, voce)
        aggiunte += 1
    salva_diretta(notizie, root)
    return aggiunte, notizie


def main():
    p = argparse.ArgumentParser(description="Alimenta la sezione News in diretta (post dei cron).")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--post", help="file del post della nuova edizione (es. fb_post_DATA_ORA.txt)")
    g.add_argument("--import-archive", help="cartella con post canonici da importare (manuale)")
    p.add_argument("--data", help="data ISO YYYY-MM-DD (default: dal nome file/intestazione)")
    p.add_argument("--ora", help="ora HH:MM (default: dal nome file/intestazione)")
    p.add_argument("--no-build", action="store_true", help="non rigenerare il sito dopo l'aggiornamento")
    a = p.parse_args()

    if a.post:
        voce, notizie = aggiungi_post(a.post, data=a.data, ora=a.ora)
        print("Edizione aggiunta: %s %s (%d voci)" % (voce["data"], voce["ora"], len(voce["voci"])))
    else:
        aggiunte, notizie = importa_archivio(a.import_archive)
        print("Edizioni importate: %d" % aggiunte)
    print("Totale edizioni in diretta: %d" % len(notizie))

    if not a.no_build:
        r = subprocess.run([sys.executable, os.path.join(HERE, "build.py")], cwd=HERE)
        if r.returncode != 0:
            print("ATTENZIONE: build.py non è andato a buon fine.", file=sys.stderr)
            return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
