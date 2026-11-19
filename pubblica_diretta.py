#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pubblica_diretta.py — pubblica l'edizione corrente di Finanza Oggi nella sezione
"News in diretta" del sito e avvia il deploy su GitHub Pages.

Tutto in uno script (niente ragionamento del modello):
  1. legge il post pronto (default: tools/fb_post_text.txt, l'edizione corrente)
  2. add_diretta.aggiungi_post -> content/diretta.json (dedup per data+ora)
  3. build.py -> rigenera sito/
  4. git add feed+sito, commit, push origin main
  5. GitHub Actions rigenera e deploya su Pages (costo zero)

Data e ora sono ricavate dall'intestazione del post (FINANZA OGGI — ... , HH:MM):
non serve passarle. Pubblica SOLO l'edizione corrente: niente backfill storico.

Uso (lo chiama il cron di Finanza Oggi dopo il gate grammaticale):
  python pubblica_diretta.py
  python pubblica_diretta.py --post <file> --no-push   # test locale (commit, non push)

Esito: "PUBBLICA DIRETTA: OK ..." oppure "PUBBLICA DIRETTA: FAIL ...".
Canale indipendente da Facebook/WordPress: un errore qui non li blocca.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import add_diretta as AD  # noqa: E402

DEFAULT_POST = r"C:\Users\emili\AppData\Local\hermes\tools\fb_post_text.txt"
# Il push usa la config git globale: per github.com c'è l'helper gh con percorso
# assoluto (gh auth setup-git), che autentica senza prompt anche in un cron background.
# NON azzerare credential.helper: toglierebbe anche l'helper gh e manderebbe git in
# prompt su /dev/tty (inesistente in background). GIT_TERMINAL_PROMPT=0 è la rete di
# sicurezza: se le credenziali mancano, il push fallisce subito invece di appendersi.
NOPROMPT = {"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never"}


def git(root, *args, env=None):
    e = None
    if env:
        e = dict(os.environ)
        e.update(env)
    return subprocess.run(["git", *args], cwd=root, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=e)


def msg_commit(voce):
    return "diretta: Finanza Oggi %s %s" % (voce["data"], voce["ora"])


def aggiorna_e_builda(post, root, data=None, ora=None):
    """Feed + rebuild. Restituisce (voce, notizie). Solleva su errore."""
    voce, notizie = AD.aggiungi_post(post, data=data, ora=ora, root=root)
    r = subprocess.run([sys.executable, os.path.join(root, "build.py")],
                       cwd=root, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError("build.py fallito: %s" % (r.stderr or r.stdout).strip())
    return voce, notizie


def pubblica(post, root, push=True, data=None, ora=None):
    """Pipeline completa. Restituisce (exit_code, messaggio)."""
    if not os.path.exists(post):
        return 1, "PUBBLICA DIRETTA: FAIL post mancante %s" % post
    try:
        voce, notizie = aggiorna_e_builda(post, root, data=data, ora=ora)
    except Exception as e:  # noqa: BLE001
        return 1, "PUBBLICA DIRETTA: FAIL feed/build: %s" % e
    riga = "Edizione in diretta: %s %s (%d voci); totale %d" % (
        voce["data"], voce["ora"], len(voce["voci"]), len(notizie))

    git(root, "add", "content/diretta.json", "sito")
    if git(root, "diff", "--cached", "--quiet").returncode == 0:
        return 0, riga + "\nPUBBLICA DIRETTA: OK nessuna modifica (edizione gia presente)"
    c = git(root, "commit", "-m", msg_commit(voce))
    if c.returncode != 0:
        return 1, riga + "\nPUBBLICA DIRETTA: FAIL commit: %s" % (c.stderr or c.stdout).strip()
    if not push:
        return 0, riga + "\nPUBBLICA DIRETTA: OK commit locale (no-push)"
    p = git(root, "push", "origin", "main", env=NOPROMPT)
    if p.returncode != 0:
        # rete/remote mosso: un solo tentativo di riallineamento, poi ritenta il push
        git(root, "pull", "--rebase", "origin", "main", env=NOPROMPT)
        p = git(root, "push", "origin", "main", env=NOPROMPT)
    if p.returncode != 0:
        return 1, riga + "\nPUBBLICA DIRETTA: FAIL push: %s" % (p.stderr or p.stdout).strip()
    return 0, riga + "\nPUBBLICA DIRETTA: OK push su main -> deploy GitHub Pages avviato"


def main():
    ap = argparse.ArgumentParser(description="Pubblica l'edizione corrente nella diretta del sito.")
    ap.add_argument("--post", default=DEFAULT_POST, help="file del post (default: fb_post_text.txt)")
    ap.add_argument("--data", help="data ISO YYYY-MM-DD (default: dall'intestazione)")
    ap.add_argument("--ora", help="ora HH:MM (default: dall'intestazione)")
    ap.add_argument("--root", default=HERE, help="radice del progetto sito (default: questo)")
    ap.add_argument("--no-push", action="store_true", help="commit locale senza push (test)")
    a = ap.parse_args()
    code, msg = pubblica(a.post, a.root, push=not a.no_push, data=a.data, ora=a.ora)
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())