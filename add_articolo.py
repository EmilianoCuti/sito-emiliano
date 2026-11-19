#!/usr/bin/env python3
"""Pubblica un nuovo articolo nel sito, da Hermes o da riga di comando.

Scrive il Markdown in data/raw/, registra la voce in content/inchieste.json
(chiave "articoli") e rigenera il sito. Le sezioni valide sono quelle definite
in content/site.json (cronaca/inchieste, finanza, ai, informatica).

Esempi:
  python add_articolo.py --sezione finanza --titolo "ETF e mercati" \
      --sommario "Una sintesi." --tema "Mercati" --file pezzo.md
  python add_articolo.py --sezione ai --titolo "Provare un modello" \
      --sommario "Sintesi." --tema "Modelli" --testo "# Titolo\n\nCorpo."
  python add_articolo.py --sezione inchieste --titolo "..." --sommario "..." \
      --tema "Casa" --inchiesta case-vuote-sudmilano --file pezzo.md
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))


def slugify(testo):
    t = unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode("ascii")
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return re.sub(r"-{2,}", "-", t) or "articolo"


def prossimo_slug(slug, esistenti):
    if slug not in esistenti:
        return slug
    n = 2
    while "%s-%d" % (slug, n) in esistenti:
        n += 1
    return "%s-%d" % (slug, n)


def _leggi(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return json.load(fh)


def aggiungi_articolo(root, sezione, titolo, sommario, tema, formato, data,
                      markdown, slug=None, inchiesta=None):
    """Registra un articolo e scrive il suo Markdown. Ritorna la voce creata."""
    site = _leggi(root, "content/site.json")
    valide = {s["id"] for s in site.get("sezioni", [])}
    if sezione not in valide:
        raise ValueError("Sezione non valida: %r. Valide: %s" % (sezione, ", ".join(sorted(valide))))
    contenuti = _leggi(root, "content/inchieste.json")
    articoli = contenuti.setdefault("articoli", [])
    if inchiesta is not None:
        slug_inchieste = {i["slug"] for i in contenuti.get("inchieste", [])}
        if inchiesta not in slug_inchieste:
            raise ValueError("Inchiesta non valida: %r" % inchiesta)
    slug = prossimo_slug(slug or slugify(titolo), {a["slug"] for a in articoli})
    fonte = "articoli/%s.md" % slug
    percorso = os.path.join(root, "data", "raw", fonte)
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, "w", encoding="utf-8") as fh:
        fh.write(markdown if markdown.endswith("\n") else markdown + "\n")
    voce = {"slug": slug, "titolo": titolo, "sommario": sommario, "tema": tema,
            "formato": formato, "sezione": sezione, "data": data, "fonte": fonte}
    if inchiesta is not None:
        voce["inchiesta"] = inchiesta
    articoli.append(voce)
    with open(os.path.join(root, "content", "inchieste.json"), "w", encoding="utf-8") as fh:
        json.dump(contenuti, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return voce


def main():
    ap = argparse.ArgumentParser(description="Pubblica un articolo nel sito.")
    ap.add_argument("--sezione", required=True, help="inchieste | finanza | ai | informatica")
    ap.add_argument("--titolo", required=True)
    ap.add_argument("--sommario", required=True)
    ap.add_argument("--tema", required=True)
    ap.add_argument("--formato", default="Articolo")
    ap.add_argument("--data", default=datetime.date.today().isoformat(), help="AAAA-MM-GG")
    ap.add_argument("--slug", default=None)
    ap.add_argument("--inchiesta", default=None, help="slug dell'inchiesta collegata (solo cronaca)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", help="percorso del Markdown sorgente")
    g.add_argument("--testo", help="Markdown inline")
    ap.add_argument("--no-build", action="store_true", help="non rigenerare il sito")
    args = ap.parse_args()

    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            markdown = fh.read()
    else:
        markdown = args.testo

    voce = aggiungi_articolo(ROOT, args.sezione, args.titolo, args.sommario, args.tema,
                             args.formato, args.data, markdown, args.slug, args.inchiesta)
    print("Articolo registrato:", voce["slug"], "| sezione:", voce["sezione"])
    print("Markdown:", os.path.join("data", "raw", voce["fonte"]))
    if not args.no_build:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "build.py")], cwd=ROOT)
        if r.returncode != 0:
            sys.exit(r.returncode)
    print("URL articolo: articoli/%s.html" % voce["slug"])


if __name__ == "__main__":
    main()