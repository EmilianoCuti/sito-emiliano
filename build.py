#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera il sito statico dell'archivio di Emiliano Cuti.

Sorgenti:  content/*.json, data/raw/*, assets/*
Uscita:    la cartella indicata da --out (default: sito/, dentro questo progetto)

Uso:
    python build.py                 # scrive in sito/
    python build.py --out /tmp/sito # scrive altrove, per una verifica locale
"""
import argparse
import csv
import html
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# markdown è incluso in vendor/: il progetto funziona senza installare pacchetti.
sys.path.insert(0, os.path.join(HERE, "vendor"))

import markdown

OUT_DEFAULT = os.path.join(HERE, "sito")

MESI = ["", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]

DATI = {
    "pressione-fiscale-12-comuni.json": "fiscalita-12-comuni-sud-est-milano/dati_analisi.json",
    "reati-donne-scheda-14-comuni.csv": "Reati contro le donne nei 14 comuni/scheda-14-comuni.csv",
    "beni-confiscati-14-comuni.csv": "Criminalità organizzata nei 14 comuni/beni-confiscati-totali-14-comuni.csv",
    "incidenti-serie-2010-2024-14-comuni.csv": "Incidenti stradali nei 14 comuni/incidenti-serie-2010-2024-14-comuni.csv",
    "strade-14-comuni.csv": "Traffico strade Città metropolitana Milano/strade-14-comuni.csv",
    "autovelox-rilevatori-14-comuni.csv": "Autovelox nei 14 comuni/rilevatori-14-comuni-tipizzati.csv",
    "aria-indicatori-14-comuni.csv": "Qualita aria Paullo/elaborati/indicatori_14_comuni.csv",
    "mercati-14-comuni.csv": "Mercati 14 comuni/elaborati/mercati_14_comuni.csv",
    "biblioteche-14-comuni.csv": "Biblioteche 14 comuni/elaborati/biblioteche_14_comuni.csv",
    "furti-esplosivo-episodi-2026.csv": "Furti con esplosivo a banche e Poste nei 14 comuni 2026/episodi-furti-esplosivo-14-comuni-2026.csv",
    "centenari-14-comuni.csv": "Centenari nei 14 comuni/centenari-sudmilano-14-comuni.csv",
    "appalti-14-comuni-2023-2025.csv": "Appalti nei 14 comuni/tabella-comuni-2023-2025.csv",
    "qualita-vita-classifica.csv": "Qualità della vita 14 comuni Sudmilano/dati/classifica_indice.csv",
    "case-vuote-14-comuni.csv": "Case vuote Sudmilano/dataset-case-vuote-sudmilano-14-comuni.csv",
}


# --------------------------------------------------------------------------- util
def esc(testo):
    return html.escape(str(testo), quote=True)


def data_it(iso):
    anno, mese, giorno = iso.split("-")
    return "%d %s %s" % (int(giorno), MESI[int(mese)], anno)


def data_breve(iso):
    anno, mese, giorno = iso.split("-")
    return "%d %s %s" % (int(giorno), MESI[int(mese)][:3], anno)


def leggi_json(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as fh:
        return json.load(fh)


def numero_it(valore, formato="int"):
    if valore is None:
        return "—"
    try:
        n = float(valore)
    except (TypeError, ValueError):
        return esc(valore)
    if formato == "int":
        return "{:,.0f}".format(n).replace(",", ".")
    if formato == "dec1":
        return "{:,.1f}".format(n).replace(",", "§").replace(".", ",").replace("§", ".")
    if formato == "dec2":
        return "{:,.2f}".format(n).replace(",", "§").replace(".", ",").replace("§", ".")
    return str(valore)


ICONS = {
 "facebook": '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M13.5 21v-7h2.4l.4-3h-2.8V9.1c0-.9.3-1.5 1.6-1.5h1.3V4.9c-.3 0-1.1-.1-2-.1-2 0-3.4 1.2-3.4 3.5V11H8.5v3H11v7h2.5z"/></svg>',
 "linkedin": '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M6.9 8.6H4V20h2.9V8.6zM5.4 4a1.7 1.7 0 100 3.4 1.7 1.7 0 000-3.4zM20 13.4c0-3-1.6-4.4-3.8-4.4-1.7 0-2.5.9-2.9 1.6V8.6H10.4V20h2.9v-6c0-1.3.6-2.1 1.7-2.1s1.6.8 1.6 2.1v6H20v-6.6z"/></svg>',
 "wordpress": '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 100 20 10 10 0 000-20zm-8.5 10c0-1.2.3-2.4.7-3.4L8.9 20a8.5 8.5 0 01-5.4-8zm8.5 8.5c-.8 0-1.6-.1-2.4-.3l2.5-7.3 2.6 7.1c0 .1.1.2.1.3-.9.2-1.8.2-2.8.2zm1.2-12.5c.5 0 1-.1 1-.1.5-.1.4-.8-.1-.8 0 0-1.4.1-2.3.1-.9 0-2.3-.1-2.3-.1-.5 0-.6.7-.1.8 0 0 .5.1 1 .1l1.5 4-2.1 6.2-3.4-10.2c.5 0 1-.1 1-.1.5-.1.4-.8-.1-.8 0 0-1.4.1-2.3.1h-.6A8.5 8.5 0 0118.7 6c-.6.4-1 1-1 1.8 0 .7.4 1.3.8 2 .3.6.5 1.3.5 2.1 0 .9-.3 2-.7 3.4l-1 3.2-3.1-9.5zm4.9 11.4l2.6-7.4c.5-1.2.6-2.2.6-3 0-.3 0-.6-.1-.9a8.5 8.5 0 01-3.1 11.3z"/></svg>',
 "email": '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M3 5h18a1 1 0 011 1v12a1 1 0 01-1 1H3a1 1 0 01-1-1V6a1 1 0 011-1zm9 7.2L4.2 6.5v11h15.6v-11L12 12.2zM5.6 6.5l6.4 4.6 6.4-4.6H5.6z"/></svg>',
}
SOCIAL_LABEL = {"facebook": "Facebook", "linkedin": "LinkedIn", "wordpress": "WordPress"}


def social_html(site, prefix="", compatto=False):
    a = site["autore"]
    voci = []
    for k, url in a.get("social", {}).items():
        voci.append('<a href="%s" target="_blank" rel="noopener noreferrer" aria-label="%s">%s<span>%s</span></a>'
                    % (esc(url), SOCIAL_LABEL.get(k, k), ICONS.get(k, ""), SOCIAL_LABEL.get(k, k)))
    if a.get("email"):
        voci.append('<a href="mailto:%s" aria-label="Email">%s<span>Email</span></a>'
                    % (esc(a["email"]), ICONS["email"]))
    cls = "social social--compatto" if compatto else "social"
    return '<div class="%s">%s</div>' % (cls, "".join(voci))


# --------------------------------------------------------------------------- html
def nome_html(site):
    parti = site["autore"]["nome"].split(" ", 1)
    if len(parti) == 2:
        return esc(parti[0]) + " <br>" + esc(parti[1])
    return esc(parti[0])


def testata(prefix, attivo, site):
    voci = [(s["url"], s["titolo"], s["id"]) for s in site["sezioni"]]
    voci += [("atlante/", "Atlante", "atlante"), ("chi-sono/", "Chi sono", "chi-sono")]
    links = []
    for href, label, chiave in voci:
        corrente = ' aria-current="page"' if chiave == attivo else ""
        links.append('<a href="%s%s"%s>%s</a>' % (prefix, href, corrente, label))
    return (
        '<header class="testata">\n<div class="shell testata-inner">\n'
        '<a class="marchio" href="%sindex.html"><img class="marchio-segno" src="%sassets/logo.svg" width="40" height="40" alt=""><span class="marchio-nome">%s<span class="punto">.</span></span></a>\n'
        '<nav class="nav" aria-label="Sezioni del sito">%s</nav>\n'
        '%s\n'
        '</div>\n</header>\n' % (prefix, prefix, esc(site["autore"]["nome"]), "".join(links), social_html(site, prefix, compatto=True))
    )


def piede(prefix, site):
    f = site["footer"]
    return (
        '<footer class="piede">\n<div class="shell piede-inner">\n'
        '<div><strong>%s</strong> — %s.<br>%s</div>\n'
        '<div>%s</div>\n'
        '</div>\n'
        '<div class="shell piede-social">%s</div>\n'
        '</footer>\n' % (esc(site["autore"]["nome"]), esc(site["autore"]["mestieri"]), esc(f["nota"]), esc(f["colophon"]), social_html(site, prefix))
    )


def pagina(titolo, descrizione, corpo, prefix, attivo, site, classe=""):
    titolo = titolo.replace("{AUTORE}", site["autore"]["nome"])
    descrizione = descrizione.replace("{AUTORE}", site["autore"]["nome"])
    ogimg = ""
    if site["autore"].get("foto"):
        ogimg = '<meta property="og:image" content="%s%s">\n' % (prefix, esc(site["autore"]["foto"]))
    return (
        '<!DOCTYPE html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>%s</title>\n<meta name="description" content="%s">\n'
        '<meta name="author" content="%s">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:locale" content="it_IT">\n'
        '<meta property="og:title" content="%s">\n'
        '<meta property="og:description" content="%s">\n'
        '%s'
        '<link rel="stylesheet" href="%sassets/style.css">\n'
        '<link rel="icon" href="%sassets/favicon.svg" type="image/svg+xml">\n'
        '</head>\n<body class="%s">\n'
        '<a class="salta" href="#contenuto">Salta al contenuto</a>\n'
        '%s'
        '<main id="contenuto">\n%s\n</main>\n'
        '%s'
        '<script src="%sassets/app.js" defer></script>\n'
        '</body>\n</html>\n'
    ) % (esc(titolo), esc(descrizione), esc(titolo), esc(descrizione),
         esc(site["autore"]["nome"]), ogimg,
         prefix, prefix, classe, testata(prefix, attivo, site) if attivo != "home" else "",
         corpo, piede(prefix, site), prefix)


# --------------------------------------------------------------------------- home
def voce(titolo, href, meta, prefix=""):
    return (
        '<a class="voce" href="%s%s">\n'
        '<span class="voce-titolo">%s</span>\n'
        '<span class="voce-meta">%s</span>\n</a>\n' % (prefix, href, esc(titolo), meta)
    )


def home(site, inchieste, articoli, atlante):
    a = site["autore"]
    h = site["home"]
    i3 = h.get("intro_3d", {})
    n_ind = atlante["meta"]["n_indicatori"]

    def conta(sid):
        if sid == "inchieste":
            return len(inchieste)
        return len([x for x in articoli if x.get("sezione") == sid])

    def ultime(sid):
        if sid == "inchieste":
            sel = inchieste[-2:]
            sel.reverse()
            return "".join(voce(i["titolo"], "inchieste/%s.html" % i["slug"],
                                "%s<br><b>%s</b>" % (esc(i["tema"]), data_breve(i["data"]))) for i in sel)
        sel = [x for x in articoli if x.get("sezione") == sid][:2]
        return "".join(voce(x["titolo"], "articoli/%s.html" % x["slug"],
                            "%s<br><b>%s</b>" % (esc(x["tema"]), data_breve(x.get("data", "2026-01-01")))) for x in sel)

    cards = []
    for n, s in enumerate(site["sezioni"], 1):
        cards.append(
            '<section class="sezione">\n'
            '<div class="sezione-testa"><span class="sezione-num">%02d</span>'
            '<h2 class="sezione-titolo"><a href="%s">%s</a></h2>'
            '<span class="sezione-conteggio">%d %s</span></div>\n'
            '<p class="sezione-nota">%s</p>\n%s\n'
            '<a class="rimando" href="%s">Apri %s <span aria-hidden="true">→</span></a>\n</section>'
            % (n, s["url"], esc(s["titolo"]), conta(s["id"]),
               "inchieste" if s["id"] == "inchieste" else "articoli",
               esc(s["descrizione"]), ultime(s["id"]), s["url"], esc(s["titolo"].lower())))
    cards.append(
        '<section class="sezione">\n<div class="sezione-testa"><span class="sezione-num">%02d</span>'
        '<h2 class="sezione-titolo"><a href="atlante/">Atlante</a></h2>'
        '<span class="sezione-conteggio">%d indicatori · 14 comuni</span></div>\n'
        '<p class="sezione-nota">%s</p>\n%s\n'
        '<a class="rimando" href="atlante/">Apri l\'atlante <span aria-hidden="true">→</span></a>\n</section>'
        % (len(site["sezioni"]) + 1, n_ind, esc(site["atlante"]["sommario"]),
           voce(site["atlante"]["titolo"], "atlante/", "Dati incrociati<br><b>%d indicatori</b>" % n_ind)))
    cards.append(
        '<section class="sezione">\n<div class="sezione-testa"><span class="sezione-num">%02d</span>'
        '<h2 class="sezione-titolo"><a href="chi-sono/">Chi sono</a></h2>'
        '<span class="sezione-conteggio">Profilo e contatti</span></div>\n'
        '<p class="sezione-nota">Cronaca, finanza, software e intelligenza artificiale. Il metodo, le fonti e i limiti dichiarati.</p>\n'
        '<a class="rimando" href="chi-sono/">Leggi la biografia <span aria-hidden="true">→</span></a>\n</section>'
        % (len(site["sezioni"]) + 2,))

    parole = "".join('<span>%s</span>' % esc(p) for p in i3.get("parole", []))
    intro = ""
    if i3.get("attivo", True):
        intro = (
            '<section class="intro3d" aria-label="Introduzione">\n'
            '<canvas class="intro3d-canvas" data-intro3d data-parole=\'%s\'></canvas>\n'
            '<div class="intro3d-velo"></div>\n'
            '<div class="shell intro3d-contenuto">\n'
            '<p class="intro3d-occhiello">%s</p>\n'
            '<h1 class="intro3d-nome">%s</h1>\n'
            '<p class="intro3d-mestiere">%s</p>\n'
            '<p class="intro3d-sommario">%s</p>\n'
            '%s\n'
            '<a class="intro3d-scendi" href="#copertina">Entra nell\'archivio <span aria-hidden="true">↓</span></a>\n'
            '</div>\n</section>\n'
            % (json.dumps(i3.get("parole", []), ensure_ascii=False).replace("'", "&#39;"),
               esc(i3.get("occhiello", a["ruolo"])), nome_html(site), esc(a["mestieri"]),
               esc(i3.get("sommario", h.get("sommario", ""))), social_html(site)))

    corpo = intro + (
        '<div class="shell copertina" id="copertina">\n<div class="copertina-griglia">\n'
        '<div class="identita">\n'
        '<div class="copertina-marchio"><img src="assets/logo.svg" width="42" height="42" alt=""></div>\n'
        '<h2 class="nome">%s</h2>\n<p class="mestiere">%s</p>\n'
        '<div class="ritratto"><img src="%s" width="660" height="880" alt="Ritratto di %s"></div>\n'
        '<p class="frase">%s</p>\n%s\n'
        '<p class="colophon-mini">Nessun cookie, nessun tracciamento.</p>\n</div>\n'
        '<div class="indice">\n%s\n</div>\n</div>\n</div>\n'
        '<script src="assets/intro3d.js" defer></script>\n'
        % (nome_html(site), esc(a["mestieri"]), esc(a["ritratto"]), esc(a["nome"]),
           esc(a["frase"]), social_html(site), "".join(cards)))
    return pagina(
        "{AUTORE} — cronaca, finanza, AI, informatica",
        "Archivio di giornalismo: inchieste sul Sudmilano, finanza, intelligenza artificiale e informatica. Metodo, fonti e limiti dichiarati.",
        corpo, "", "home", site, "pagina-home")


# --------------------------------------------------------------------------- archivio
def archivio_inchieste(site, inchieste):
    temi = []
    for i in inchieste:
        if i["tema"] not in temi:
            temi.append(i["tema"])
    temi.sort()

    chips = ['<button class="chip" type="button" data-tema="tutti" aria-pressed="true">Tutti</button>']
    for t in temi:
        chips.append('<button class="chip" type="button" data-tema="%s" aria-pressed="false">%s</button>' % (esc(t), esc(t)))

    righe = []
    for i in reversed(inchieste):
        cerca = " ".join([
            i["titolo"], i["sintesi"], i["tema"], i["territorio"], i["occhiello"],
            i["slug"].replace("-", " "),
            " ".join(n["l"] + " " + n["v"] for n in i["numeri"]),
        ])
        righe.append(
            '<a class="riga" data-riga data-temi="%s" data-cerca="%s" href="%s.html">\n'
            '<span class="riga-data">%s</span>\n'
            '<span><span class="riga-titolo">%s</span>\n'
            '<span class="riga-sommario">%s</span></span>\n'
            '<span class="riga-meta">%s<br><b>%s</b></span>\n</a>\n' % (
                esc(i["tema"]), esc(cerca.lower()), esc(i["slug"]),
                data_breve(i["data"]), esc(i["titolo"]), esc(i["sintesi"]),
                esc(i["tema"]), esc(i["numeri"][0]["v"])))

    corpo = """
<div class="shell">
 <div class="archivio-griglia">
  <aside class="archivio-testata">
   <p class="pagina-occhiello">Archivio · 2026</p>
   <h1 class="archivio-titolo">Inchieste</h1>
   <p class="archivio-sommario">%s</p>
   <p class="archivio-conteggio">%d inchieste · 14 comuni</p>
   <div class="filtri-lato">
    <div class="cerca-wrap">
     <label class="etichetta" for="cerca-inchieste" style="position:absolute;left:-9999px">Cerca nelle inchieste</label>
     <input class="cerca" id="cerca-inchieste" type="search" data-cerca-inchieste placeholder="Cerca: case vuote, appalti, Melegnano…" autocomplete="off">
    </div>
    <div class="chips">%s</div>
    <span class="filtri-conteggio" data-conteggio aria-live="polite">%d inchieste</span>
   </div>
  </aside>
  <div class="archivio-corpo">
   <div class="archivio" data-archivio>
    %s
   </div>
   <div class="vuoto" data-vuoto hidden>
    <h2>Nessun risultato</h2>
    <p>Nessuna inchiesta corrisponde alla ricerca. Prova un tema diverso o azzera i filtri.</p>
    <button class="bottone" type="button" data-azzera>Azzera i filtri</button>
   </div>
  </div>
 </div>
</div>
""" % (esc(site["home"]["introduzione"]), len(inchieste), "".join(chips),
       len(inchieste), "".join(righe))
    return pagina("Inchieste — {AUTORE}", "Quindici inchieste sul Sudmilano: case vuote, appalti, incidenti, ambiente, servizi, criminalità. Cerca per tema o per comune.", corpo, "../", "inchieste", site)


# --------------------------------------------------------------------------- dossier
def dossier(site, i, tutte, articoli):
    idx = tutte.index(i)
    prec = tutte[idx - 1] if idx > 0 else None
    succ = tutte[idx + 1] if idx < len(tutte) - 1 else None
    per_slug = {x["slug"]: x for x in tutte}

    numeri = "".join(
        '<div><div class="numero-v">%s</div><div class="numero-l">%s</div><div class="numero-n">%s</div></div>'
        % (esc(n["v"]), esc(n["l"]), esc(n["n"])) for n in i["numeri"])

    punto = "".join("<p>%s</p>" % esc(p) for p in i["punto"])
    metodo = "".join("<li>%s</li>" % esc(m) for m in i["metodo"])
    fonti = "".join("<li>%s</li>" % esc(f) for f in i["fonti"])
    limiti = "".join("<li>%s</li>" % esc(l) for l in i["limiti"])
    materiali = "".join("<li>%s</li>" % esc(m) for m in i["materiali"])
    correlati = "".join(
        '<li><a href="../inchieste/%s.html"><span>%s</span><span class="tema">%s</span></a></li>'
        % (esc(per_slug[s]["slug"]), esc(per_slug[s]["titolo"]), esc(per_slug[s]["tema"]))
        for s in i["correlati"] if s in per_slug)

    dato = ""
    if i.get("dati"):
        d = i["dati"]
        dato = ('<div class="dati-box"><p class="etichetta">Dati scaricabili</p>'
                '<a class="dato-link" href="../assets/dati/%s" download>%s <span>%s</span></a></div>'
                % (esc(d["file"]), esc(d["label"]), esc(d.get("nota", ""))))

    articoli_collegati = [a for a in articoli if a.get("inchiesta") == i["slug"]]
    blocco_articoli = ""
    if articoli_collegati:
        voci_art = "".join(
            '<li><a href="../articoli/%s.html"><span>%s</span><span class="tema">%s</span></a></li>'
            % (esc(a["slug"]), esc(a["titolo"]), esc(a["formato"]))
            for a in articoli_collegati)
        blocco_articoli = ('<div class="testo"><h2>Gli articoli</h2><ul class="correlati">%s</ul></div>'
                           % voci_art)

    passo = '<div class="passo">'
    if prec:
        passo += '<a href="%s.html"><span class="dir">Precedente</span>%s</a>' % (esc(prec["slug"]), esc(prec["titolo"]))
    else:
        passo += "<span></span>"
    if succ:
        passo += '<a href="%s.html" style="text-align:right"><span class="dir">Successiva</span>%s</a>' % (esc(succ["slug"]), esc(succ["titolo"]))
    passo += "</div>"

    corpo = """
<div class="shell">
 <header class="dossier-testa">
  <p class="pagina-occhiello">Inchiesta · %s</p>
  <h1 class="pagina-titolo">%s</h1>
  <p class="pagina-sommario">%s</p>
 </header>

 <div class="dossier-griglia">
  <aside class="dossier-meta">
   <dl>
    <dt>Data</dt><dd>%s</dd>
    <dt>Tema</dt><dd>%s</dd>
    <dt>Territorio</dt><dd>%s</dd>
   </dl>
   <p><a href="../inchieste/">← Tutte le inchieste</a></p>
  </aside>

  <article class="dossier-corpo">
   <div class="numeri">%s</div>
   <div class="testo">
    <h2>Il punto</h2>
    %s
    <h2>Come è stata fatta</h2>
    <ul>%s</ul>
    <h2>Le fonti</h2>
    <ul class="fonti">%s</ul>
    <h2>I materiali</h2>
    <ul class="materiali">%s</ul>
    %s
   </div>

   <div class="limiti">
    <h2>Cosa non sappiamo</h2>
    <ul>%s</ul>
   </div>

   <div class="testo">
    <h2>Inchieste correlate</h2>
    <ul class="correlati">%s</ul>
   </div>

   %s
   %s
  </article>
 </div>
</div>
""" % (
        esc(i["occhiello"]), esc(i["titolo"]), esc(i["sintesi"]),
        data_it(i["data"]), esc(i["tema"]), esc(i["territorio"]),
        numeri, punto, metodo, fonti, materiali, dato,
        limiti, correlati, blocco_articoli, passo)

    return pagina("%s — {AUTORE}" % i["titolo"], i["sintesi"], corpo, "../", "inchieste", site)


# --------------------------------------------------------------------------- atlante
def atlante(site, dati):
    indicatori = sorted(dati["indicatori"], key=lambda x: x["ordine"])
    core = {"case_vuote_pct", "centenari_100k", "indice_qv", "incidenti_2024",
            "autovelox", "mercati_posti_1000", "biblio_doc_ab", "appalti_ad_pct",
            "pm10_giorni"}
    extra = [x for x in indicatori if x["id"] not in core]
    ordine_colonne = ["pop"] + [x["id"] for x in indicatori if x["id"] in core] + [x["id"] for x in extra]

    def intestazione(chiave, label, unita, fonte, visibile=True):
        cls = "" if visibile else ' class="extra"'
        return ('<th scope="col" data-chiave="%s"%s>%s<span class="sorgente">%s</span></th>'
                % (esc(chiave), cls, esc(label), esc(fonte)))

    th = ['<th scope="col" data-chiave="nome">Comune<span class="sorgente">ISTAT</span></th>',
          '<th scope="col" data-chiave="pop">Abitanti<span class="sorgente">ISTAT 2026</span></th>']
    for x in indicatori:
        th.append(intestazione(x["id"], x.get("label_breve", x["label"]), x["unita"],
                               x.get("fonte_breve", x["fonte"]), x["id"] in core))

    righe = []
    for c in sorted(dati["comuni"], key=lambda x: x["nome"]):
        celle = ['<td class="comune">%s</td>' % esc(c["nome"])]
        celle.append('<td data-chiave="pop">%s</td>' % numero_it(c.get("pop")))
        for x in indicatori:
            valore = c.get(x["id"])
            classi = []
            if x["id"] not in core:
                classi.append("extra")
            if valore is None:
                classi.append("manca")
            cls = ' class="%s"' % " ".join(classi) if classi else ""
            testo = numero_it(valore, x["formato"]) if valore is not None else "—"
            celle.append('<td data-chiave="%s"%s>%s</td>' % (esc(x["id"]), cls, testo))
        attrs = ["data-comune=\"%s\"" % esc(c["nome"])]
        for chiave in ["nome"] + ordine_colonne:
            v = c["nome"] if chiave == "nome" else c.get(chiave)
            attrs.append('data-valore-%s="%s"' % (chiave, "" if v is None else v))
        righe.append('<tr %s>%s</tr>' % (" ".join(attrs), "".join(celle)))

    legenda = "".join(
        '<div><b>%s</b>%s · %s</div>' % (esc(x["label"]), esc(x["fonte"]), esc(x["descrizione"]))
        for x in indicatori)

    letture = "".join(
        '<article><h3>%s</h3><p>%s</p><span class="r">%s</span></article>'
        % (esc(l["titolo"]), esc(l["testo"]), esc(l["r"])) for l in site["atlante"]["letture"])

    intro = "".join("<p>%s</p>" % esc(p) for p in site["atlante"]["introduzione"])

    guida = """
<ol class="guida-atlante">
 <li>Clicca un'intestazione per ordinare la tabella.</li>
 <li>Clicca un comune per il profilo completo, con fonte e descrizione di ogni indicatore.</li>
 <li>Il pulsante «Mostra tutti gli indicatori» aggiunge le colonne fuori dal nucleo principale.</li>
</ol>
"""

    corpo = """
<div class="shell">
 <header class="pagina-testa">
  <p class="pagina-occhiello">%s</p>
  <h1 class="pagina-titolo">%s</h1>
  <p class="pagina-sommario">%s</p>
  <p class="pagina-conteggio">%d comuni · %d indicatori · 12 inchieste collegate</p>
 </header>

 <div class="atlante-intro">
  <div>%s</div>
  <div class="guida-wrap">%s</div>
 </div>

 <div class="atlante-tools">
  <div class="cerca-wrap">
   <label class="etichetta" for="cerca-comune" style="position:absolute;left:-9999px">Cerca un comune</label>
   <input class="cerca" id="cerca-comune" type="search" data-cerca-comune placeholder="Cerca un comune…" autocomplete="off">
  </div>
  <button class="bottone" type="button" data-mostra-tutti aria-pressed="false">Mostra tutti gli indicatori</button>
  <span class="filtri-conteggio" data-atlante-conteggio aria-live="polite">14 comuni</span>
 </div>

 <div class="tabella-wrap">
  <table class="atlante" data-atlante>
   <thead><tr>%s</tr></thead>
   <tbody>%s</tbody>
  </table>
 </div>
 <p class="scorri">Scorri la tabella per tutte le colonne →</p>
 <p class="etichetta" style="margin:10px 0 0">Clicca un'intestazione per ordinare · clicca un comune per il profilo completo</p>

 <section class="scheda-comune" data-scheda-comune hidden>
  <div class="scheda-testa">
   <h2 data-scheda-titolo>Comune</h2>
   <button class="scheda-chiudi" type="button" data-chiudi-scheda>Chiudi</button>
  </div>
  <dl class="scheda-griglia" data-scheda-corpo data-prefisso="../"></dl>
  <p class="scheda-correlati">Inchieste collegate: <span data-scheda-correlati data-prefisso="../"></span></p>
 </section>

 <div class="legenda">%s</div>

 <section class="letture">%s</section>

 <p class="pagina-sommario" style="margin-top:26px;font-size:15px">%s</p>
</div>
<script type="application/json" id="atlante-dati">%s</script>
""" % (
        esc(site["atlante"]["occhiello"]), esc(site["atlante"]["titolo"]),
        esc(site["atlante"]["sommario"]), dati["meta"]["n_comuni"],
        dati["meta"]["n_indicatori"],
        intro,
        guida,
        "".join(th), "".join(righe), legenda, letture,
        esc(site["atlante"]["nota_finale"]),
        json.dumps({"comuni": dati["comuni"], "indicatori": dati["indicatori"],
                    "titoli": dati.get("titoli", {}), "meta": dati["meta"]}, ensure_ascii=False).replace("</", "<\\/"))
    return pagina("Atlante dei quattordici comuni — {AUTORE}",
                  "Diciassette indicatori incrociati per i quattordici comuni del Sudmilano: case vuote, reddito, incidenti, autovelox, servizi, appalti, aria.",
                  corpo, "../", "atlante", site, "pagina-atlante")


# --------------------------------------------------------------------------- articoli
def diretta_card(n, prefix="../"):
    """Una edizione FINANZA OGGI come card della diretta."""
    voci = ""
    for v in n.get("voci", []):
        parti = [x for x in (v.get("ora"), v.get("fonte")) if x]
        coda = (' <span class="diretta-fonte">(%s)</span>' % esc(", ".join(parti))) if parti else ""
        voci += "<li>%s%s</li>\n" % (esc(v.get("testo", "")), coda)
    sintesi = ('<div class="diretta-blocco"><h3>Sintesi mercato</h3><p>%s</p></div>' % esc(n["sintesi"])) if n.get("sintesi") else ""
    prospettiva = ('<div class="diretta-blocco"><h3>Prospettiva</h3><p>%s</p></div>' % esc(n["prospettiva"])) if n.get("prospettiva") else ""
    fonti = ('<p class="diretta-fonti">Fonti: %s</p>' % esc(", ".join(n["fonti"]))) if n.get("fonti") else ""
    finestra = ('<span class="diretta-finestra">finestra %s</span>' % esc(n["finestra"])) if n.get("finestra") else ""
    return """<article class="diretta-card" id="%s">
 <header class="diretta-testa">
  <span class="diretta-badge">Finanza oggi</span>
  <span class="diretta-data">%s · %s</span>
  %s
 </header>
 <ul class="diretta-voci">%s</ul>
 %s
 %s
 %s
</article>""" % (esc(n["slug"]), data_it(n["data"]), esc(n["ora"]), finestra, voci, sintesi, prospettiva, fonti)


VUOTO_DIRETTA = ('<div class="diretta-vuoto"><p>La diretta si popolerà con le edizioni dei cron job '
                 '(10:00 · 14:00 · 18:00) a partire dalla pubblicazione del sito.</p></div>')


def diretta_block(notizie, prefix="../", limite=6):
    """Blocco "News in diretta" in cima alla pagina Finanza (anche vuoto)."""
    if not notizie:
        corpo, link = VUOTO_DIRETTA, ""
    else:
        corpo = "".join(diretta_card(n, prefix) for n in notizie[:limite])
        link = '<p class="diretta-tutte"><a class="bottone" href="diretta.html">Tutte le edizioni →</a></p>'
    return """<div class="shell">
 <section class="diretta" aria-label="News in diretta">
  <div class="diretta-intesta">
   <p class="pagina-occhiello">In diretta</p>
   <h2 class="diretta-titolo">News in diretta</h2>
   <p class="diretta-sotto">Le edizioni di Finanza Oggi dai cron job, dalla più recente.</p>
  </div>
  %s
  %s
 </section>
</div>
""" % (corpo, link)


def diretta_index(site, notizie):
    """Pagina dedicata con tutte le edizioni della diretta (finanza/diretta.html)."""
    if notizie:
        corpo = "".join(diretta_card(n, "../") for n in notizie)
        conta = "%d edizioni" % len(notizie)
    else:
        corpo, conta = VUOTO_DIRETTA, "0 edizioni"
    corpo = """<div class="shell">
 <p class="pagina-occhiello"><a href="index.html">Finanza</a> · In diretta</p>
 <h1 class="archivio-titolo">News in diretta</h1>
 <p class="archivio-sommario">Le edizioni di Finanza Oggi prodotte dai cron job. %s.</p>
 <section class="diretta diretta--pagina" aria-label="Edizioni">
 %s
 </section>
</div>""" % (conta, corpo)
    return pagina("News in diretta — Finanza — {AUTORE}",
                  "Le edizioni di Finanza Oggi dai cron job, in ordine cronologico.",
                  corpo, "../", "finanza", site)


def sezione_index(site, sez, articoli, per_slug, notizie=None):
    items = [a for a in articoli if a.get("sezione") == sez["id"]]
    items.sort(key=lambda a: a.get("data", ""), reverse=True)
    temi = sorted({a["tema"] for a in items})
    chips = ['<button class="chip" type="button" data-tema="tutti" aria-pressed="true">Tutti</button>']
    for t in temi:
        chips.append('<button class="chip" type="button" data-tema="%s" aria-pressed="false">%s</button>' % (esc(t), esc(t)))
    righe = []
    for a in items:
        data = a.get("data") or per_slug.get(a.get("inchiesta"), {}).get("data", "2026-01-01")
        righe.append(
            '<a class="riga" data-riga data-temi="%s" data-cerca="%s" href="../articoli/%s.html">\n'
            '<span class="riga-data">%s</span>\n'
            '<span><span class="riga-titolo">%s</span>\n<span class="riga-sommario">%s</span></span>\n'
            '<span class="riga-meta">%s<br><b>%s</b></span>\n</a>\n'
            % (esc(a["tema"]), esc((a["titolo"] + " " + a["sommario"] + " " + a["tema"]).lower()),
               esc(a["slug"]), data_breve(data), esc(a["titolo"]), esc(a["sommario"]),
               esc(a["tema"]), esc(a["formato"])))
    vuoto = ('<div class="vuoto-sezione"><p>Ancora nessun articolo in questa sezione. '
             'Si popolerà con i prossimi pezzi.</p></div>') if not items else ""
    unita = "articolo" if len(items) == 1 else "articoli"
    corpo = """
<div class="shell">
 <div class="archivio-griglia">
  <aside class="archivio-testata">
   <p class="pagina-occhiello">%s</p>
   <h1 class="archivio-titolo">%s</h1>
   <p class="archivio-sommario">%s</p>
   <p class="archivio-conteggio">%d %s</p>
   <div class="filtri-lato">
    <div class="cerca-wrap">
     <label class="etichetta" for="cerca-sezione" style="position:absolute;left:-9999px">Cerca nella sezione</label>
     <input class="cerca" id="cerca-sezione" type="search" data-cerca-inchieste placeholder="Cerca…" autocomplete="off">
    </div>
    <div class="chips">%s</div>
    <span class="filtri-conteggio" data-conteggio aria-live="polite">%d %s</span>
   </div>
  </aside>
  <div class="archivio-corpo">
   <div class="archivio" data-archivio data-unita="articoli" data-unita-singolare="articolo">%s</div>
   %s
   <div class="vuoto" data-vuoto hidden>
    <h2>Nessun risultato</h2><p>Nessun articolo corrisponde alla ricerca.</p>
    <button class="bottone" type="button" data-azzera>Azzera i filtri</button>
   </div>
  </div>
 </div>
</div>
""" % (esc(sez["occhiello"]), esc(sez["titolo"]), esc(sez["descrizione"]), len(items), unita,
       "".join(chips), len(items), unita, "".join(righe), vuoto)
    if sez["id"] == "finanza" and notizie is not None:
        corpo = diretta_block(notizie, "../") + corpo
    return pagina("%s — {AUTORE}" % sez["titolo"], sez["descrizione"], corpo, "../", sez["id"], site)


def articoli_index(site, articoli, per_slug):
    sez_label = {s["id"]: s["titolo"] for s in site["sezioni"]}
    presenti = [s for s in site["sezioni"] if any(a.get("sezione", "inchieste") == s["id"] for a in articoli)]
    chips = ['<button class="chip" type="button" data-tema="tutti" aria-pressed="true">Tutti</button>']
    for s in presenti:
        chips.append('<button class="chip" type="button" data-tema="%s" aria-pressed="false">%s</button>' % (esc(s["id"]), esc(s["titolo"])))
    righe = []
    for a in articoli:
        sid = a.get("sezione", "inchieste")
        inch = per_slug.get(a.get("inchiesta"))
        data = a.get("data") or (inch["data"] if inch else "2026-01-01")
        righe.append(
            '<a class="riga" data-riga data-temi="%s" data-cerca="%s" href="%s.html">\n'
            '<span class="riga-data">%s</span>\n'
            '<span><span class="riga-titolo">%s</span>\n<span class="riga-sommario">%s</span></span>\n'
            '<span class="riga-meta">%s<br><b>%s</b></span>\n</a>\n' % (
                esc(sid), esc((a["titolo"] + " " + a["sommario"] + " " + a["tema"] + " " + sez_label.get(sid, "")).lower()),
                esc(a["slug"]), data_breve(data), esc(a["titolo"]),
                esc(a["sommario"]), esc(sez_label.get(sid, a["tema"])), esc(a["formato"])))
    corpo = """
<div class="shell">
 <div class="archivio-griglia">
  <aside class="archivio-testata">
   <p class="pagina-occhiello">Testi</p>
   <h1 class="archivio-titolo">Articoli e racconti</h1>
   <p class="archivio-sommario">%s</p>
   <p class="archivio-conteggio">%d testi · cronaca, finanza, AI, informatica</p>
   <div class="filtri-lato">
    <div class="cerca-wrap">
     <label class="etichetta" for="cerca-articoli" style="position:absolute;left:-9999px">Cerca negli articoli</label>
     <input class="cerca" id="cerca-articoli" type="search" data-cerca-inchieste placeholder="Cerca negli articoli…" autocomplete="off">
    </div>
    <div class="chips">%s</div>
    <span class="filtri-conteggio" data-conteggio aria-live="polite">%d testi</span>
   </div>
   <p class="nota-racconti">%s</p>
  </aside>
  <div class="archivio-corpo">
   <div class="archivio" data-archivio data-unita="testi" data-unita-singolare="testo">%s</div>
   <div class="vuoto" data-vuoto hidden>
    <h2>Nessun risultato</h2><p>Nessun testo corrisponde alla ricerca.</p>
    <button class="bottone" type="button" data-azzera>Azzera i filtri</button>
   </div>
  </div>
 </div>
</div>
""" % (esc(site["articoli"]["sommario"]), len(articoli), "".join(chips), len(articoli),
       esc(site["articoli"]["nota_racconti"]), "".join(righe))
    return pagina("Articoli e racconti — {AUTORE}", "Articoli di cronaca, finanza, AI e informatica.", corpo, "../", "articoli", site)


def pulisci_markdown(testo):
    righe = testo.splitlines()
    # via il titolo: è già nell'header della pagina
    while righe and not righe[0].strip():
        righe.pop(0)
    if righe and righe[0].startswith("# "):
        righe.pop(0)
    # via il paragrafo di sintesi in corsivo: è già nell'header della pagina
    blocchi = []
    i = 0
    while i < len(righe):
        while i < len(righe) and not righe[i].strip():
            i += 1
        if i >= len(righe):
            break
        inizio = i
        while i < len(righe) and righe[i].strip():
            i += 1
        blocchi.append((inizio, i))
    for inizio, fine in blocchi[:4]:
        testo_blocco = " ".join(righe[inizio:fine]).strip()
        if (len(testo_blocco) > 160 and testo_blocco.startswith("*")
                and not testo_blocco.startswith("**") and testo_blocco.endswith("*")
                and not testo_blocco.endswith("**")):
            del righe[inizio:fine]
            break
    return "\n".join(righe).strip()


def articolo(site, a, per_slug):
    inch = per_slug.get(a.get("inchiesta"))
    sid = a.get("sezione", "inchieste")
    sez = next((s for s in site["sezioni"] if s["id"] == sid), None)
    data = a.get("data") or (inch["data"] if inch else "2026-01-01")
    with open(os.path.join(HERE, "data", "raw", a["fonte"]), encoding="utf-8") as fh:
        grezzo = fh.read()
    md = pulisci_markdown(grezzo)
    corpo_html = markdown.markdown(md, extensions=["markdown.extensions.tables", "markdown.extensions.sane_lists"])
    corpo_html = re.sub(r"<table>", '<div class="tabella-wrap"><table>', corpo_html)
    corpo_html = re.sub(r"</table>", "</table></div>", corpo_html)
    meta_inch = ('<dt>Inchiesta</dt><dd><a href="../inchieste/%s.html">%s</a></dd>' % (esc(inch["slug"]), esc(inch["titolo"]))) if inch else ""
    if inch:
        fine = ('<p class="etichetta">Dal dossier</p>'
                '<a class="fine-dossier" href="../inchieste/%s.html">%s <span aria-hidden="true">→</span></a>'
                '<p class="fine-nav"><a href="../articoli/">Tutti gli articoli</a> · <a href="../inchieste/">Tutte le inchieste</a></p>'
                % (esc(inch["slug"]), esc(inch["titolo"])))
    else:
        fine = ('<p class="fine-nav"><a href="../%s">Tutti gli articoli di %s</a> · <a href="../articoli/">Tutti gli articoli</a></p>'
                % (esc(sez["url"]) if sez else "articoli/", esc(sez["titolo"].lower()) if sez else ""))
    corpo = """
<div class="shell">
 <header class="dossier-testa">
  <p class="pagina-occhiello">%s · %s</p>
  <h1 class="pagina-titolo pagina-titolo--articolo">%s</h1>
  <p class="pagina-sommario">%s</p>
 </header>
 <div class="articolo-griglia">
  <aside class="dossier-meta">
   <dl>
    <dt>Data</dt><dd>%s</dd>
    <dt>Sezione</dt><dd>%s</dd>
    <dt>Tema</dt><dd>%s</dd>
    <dt>Formato</dt><dd>%s</dd>
    %s
   </dl>
   <p><a href="../articoli/">← Tutti gli articoli</a></p>
  </aside>
  <article class="articolo-testo">
   %s
   <div class="articolo-fine">%s</div>
  </article>
 </div>
</div>
""" % (esc(a["formato"]), esc(sez["titolo"] if sez else a["tema"]), esc(a["titolo"]), esc(a["sommario"]),
       data_it(data), esc(sez["titolo"] if sez else sid), esc(a["tema"]), esc(a["formato"]),
       meta_inch, corpo_html, fine)
    return pagina("%s — {AUTORE}" % a["titolo"], a["sommario"], corpo, "../", "articoli", site)


# --------------------------------------------------------------------------- chi sono
def chi_sono(site):
    c = site["chi_sono"]
    paragrafi = "".join("<p>%s</p>" % esc(p) for p in c["paragrafi"])
    metodo = "".join('<article><h3>%s</h3><p>%s</p></article>' % (esc(m["t"]), esc(m["d"])) for m in c["metodo"])
    corpo = """
<div class="shell">
 <header class="pagina-testa">
  <p class="pagina-occhiello">Profilo</p>
  <h1 class="pagina-titolo">%s</h1>
  <p class="pagina-sommario">Cronaca locale, finanza, intelligenza artificiale e informatica. Un archivio di lavoro prima che un portfolio.</p>
 </header>
 <div class="biografia">
  <figure class="biografia-ritratto">
   <img src="../%s" width="660" height="880" alt="Ritratto di %s">
   <figcaption>%s</figcaption>
  </figure>
  <div class="biografia-testo">
   %s
   <div class="metodo">
    <h2>%s</h2>
    <div class="metodo-griglia">%s</div>
   </div>
   <p class="chiusura-bio">%s</p>
   <div class="contatti">
    <h2>Contatti e profili</h2>
    %s
   </div>
  </div>
 </div>
</div>
""" % (esc(c["titolo"]), esc(site["autore"]["ritratto"]), esc(site["autore"]["nome"]), esc(site["autore"]["frase"]), paragrafi,
       esc(c["metodo_titolo"]), metodo, esc(c["chiusura"]), social_html(site, "../"))
    return pagina("Chi sono — {AUTORE}", "{AUTORE}: giornalista. Cronaca locale, finanza, AI e informatica. Premio Borsa Verde 2007, Università degli Studi di Milano.", corpo, "../", "chi-sono", site)


# --------------------------------------------------------------------------- 404
def non_trovata(site):
    corpo = """
<div class="shell">
 <header class="pagina-testa">
  <p class="pagina-occhiello">Errore 404</p>
  <h1 class="pagina-titolo">Questa pagina non c'è</h1>
  <p class="pagina-sommario">L'indirizzo è sbagliato o la pagina è stata spostata. L'archivio resta qui.</p>
 </header>
 <div class="archivio" style="padding:34px 0 60px">
  <p><a class="rimando" style="margin-left:0" href="/index.html">Torna alla copertina <span aria-hidden="true">→</span></a></p>
  <p><a class="rimando" style="margin-left:0" href="/inchieste/index.html">Tutte le inchieste <span aria-hidden="true">→</span></a></p>
  <p><a class="rimando" style="margin-left:0" href="/atlante/index.html">Atlante dei comuni <span aria-hidden="true">→</span></a></p>
 </div>
</div>
"""
    return pagina("Pagina non trovata — {AUTORE}", "Pagina non trovata.", corpo, "", "404", site)


# --------------------------------------------------------------------------- dati
def scrivi_dati(output, dati):
    cartella = os.path.join(output, "assets", "dati")
    os.makedirs(cartella, exist_ok=True)
    for nome, sorgente in DATI.items():
        percorso = os.path.join(HERE, "data", "raw", sorgente)
        if not os.path.exists(percorso):
            print("  ! dato mancante:", sorgente)
            continue
        shutil.copyfile(percorso, os.path.join(cartella, nome))

    # atlante in forma ordinata
    indicatori = sorted(dati["indicatori"], key=lambda x: x["ordine"])
    with open(os.path.join(cartella, "atlante-comuni.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["comune"] + ["popolazione_2026"] + [x["id"] for x in indicatori])
        for c in sorted(dati["comuni"], key=lambda x: x["nome"]):
            w.writerow([c["nome"], c.get("pop")] + ["" if c.get(x["id"]) is None else c.get(x["id"]) for x in indicatori])
    with open(os.path.join(cartella, "atlante-indicatori.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "indicatore", "unita", "fonte", "inchiesta", "descrizione"])
        for x in indicatori:
            w.writerow([x["id"], x["label"], x["unita"], x["fonte"], x["inchiesta"], x["descrizione"]])


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT_DEFAULT)
    args = ap.parse_args()
    out = os.path.abspath(args.out)

    site = leggi_json("content/site.json")
    contenuti = leggi_json("content/inchieste.json")
    dati = leggi_json("content/atlante.json")
    inchieste = contenuti["inchieste"]
    articoli = contenuti["articoli"]
    per_slug = {i["slug"]: i for i in inchieste}
    notizie = []
    if os.path.exists(os.path.join(HERE, "content", "diretta.json")):
        notizie = leggi_json("content/diretta.json").get("diretta", [])

    if os.path.isdir(out):
        for nome in os.listdir(out):
            if nome in (".DS_Store",):
                continue
            percorso = os.path.join(out, nome)
            if os.path.isdir(percorso):
                shutil.rmtree(percorso)
            else:
                os.remove(percorso)
    os.makedirs(out, exist_ok=True)
    # file vuoto richiesto da GitHub Pages per servire tutti i file
    open(os.path.join(out, ".nojekyll"), "w", encoding="utf-8").close()

    # asset
    os.makedirs(os.path.join(out, "assets"), exist_ok=True)
    for nome in ("style.css", "app.js", "ritratto.svg", "favicon.svg", "logo.svg", "intro3d.js", "emiliano-cuti.jpg", "animazione.gif"):
        sorgente = os.path.join(HERE, "assets", nome)
        if os.path.exists(sorgente):
            shutil.copyfile(sorgente, os.path.join(out, "assets", nome))
    foto = site["autore"].get("foto")
    if foto and os.path.exists(os.path.join(HERE, foto)):
        site["autore"]["ritratto"] = foto

    pagine = []

    def scrivi(rel, contenuto):
        percorso = os.path.join(out, rel)
        os.makedirs(os.path.dirname(percorso), exist_ok=True)
        with open(percorso, "w", encoding="utf-8") as fh:
            fh.write(contenuto)
        pagine.append(rel)

    scrivi("index.html", home(site, inchieste, articoli, dati))
    scrivi("inchieste/index.html", archivio_inchieste(site, inchieste))
    for i in inchieste:
        scrivi("inchieste/%s.html" % i["slug"], dossier(site, i, inchieste, articoli))
    scrivi("atlante/index.html", atlante(site, dati))
    scrivi("articoli/index.html", articoli_index(site, articoli, per_slug))
    for a in articoli:
        scrivi("articoli/%s.html" % a["slug"], articolo(site, a, per_slug))
    for s in site["sezioni"]:
        if s["id"] != "inchieste":
            nd = notizie if s["id"] == "finanza" else None
            scrivi(s["url"] + "index.html", sezione_index(site, s, articoli, per_slug, notizie=nd))
    if any(s["id"] == "finanza" for s in site["sezioni"]):
        scrivi("finanza/diretta.html", diretta_index(site, notizie))
    scrivi("chi-sono/index.html", chi_sono(site))
    scrivi("404.html", non_trovata(site))

    scrivi_dati(out, dati)

    with open(os.path.join(out, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("User-agent: *\nAllow: /\n")

    print("Sito scritto in", out)
    print("Pagine:", len(pagine))
    for p in pagine:
        print("  ", p)
    dimensione = 0
    for radice, _, files in os.walk(out):
        for f in files:
            dimensione += os.path.getsize(os.path.join(radice, f))
    print("Peso totale: %.1f KB" % (dimensione / 1024.0))


if __name__ == "__main__":
    main()
