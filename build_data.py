#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Costruisce content/atlante.json incrociando i dataset delle inchieste.

Le fonti stanno in data/raw/ (copia di lavoro dei file su OneDrive).
Ogni indicatore conserva la sua fonte e l'inchiesta da cui proviene:
l'Atlante non inventa nulla, mette in colonna dati già pubblicati.

Uso:  python build_data.py
"""
import csv
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "raw")
OUT = os.path.join(HERE, "content", "atlante.json")

COMUNI = [
    "Carpiano", "Cerro al Lambro", "Colturano", "Dresano", "Mediglia",
    "Melegnano", "Pantigliate", "Paullo", "Peschiera Borromeo",
    "San Donato Milanese", "San Giuliano Milanese", "San Zenone al Lambro",
    "Tribiano", "Vizzolo Predabissi",
]

# nome canonico -> chiavi usate dalle diverse fonti
ALIASES = {
    "san donato m.": "San Donato Milanese",
    "san giuliano m.": "San Giuliano Milanese",
}


def canon(name):
    n = " ".join(name.strip().split())
    low = n.lower()
    if low in ALIASES:
        return ALIASES[low]
    for c in COMUNI:
        if c.lower() == low:
            return c
    # le fonti ANAC/ISTAT usano il maiuscolo
    for c in COMUNI:
        if c.lower() == low.replace("  ", " "):
            return c
    raise ValueError("Comune non riconosciuto: %r" % name)


def read_csv(rel, delimiter=","):
    path = os.path.join(RAW, rel)
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=delimiter))


def num(value):
    if value is None:
        return None
    value = str(value).strip().replace("€", "").replace("%", "")
    if value in ("", "-", "n.d.", "NA", "N/A"):
        return None
    # le fonti usano il punto decimale; alcune il punto come separatore migliaia
    if value.count(",") == 1 and value.count(".") > 1:
        value = value.replace(".", "").replace(",", ".")
    elif value.count(",") == 1 and value.count(".") == 0:
        value = value.replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None


def main():
    data = {c: {} for c in COMUNI}

    # --- Case vuote (ISTAT, censimento abitazioni) -------------------------
    for r in read_csv("Case vuote Sudmilano/dataset-case-vuote-sudmilano-14-comuni.csv", ";"):
        c = canon(r["comune"])
        data[c]["case_vuote_pct"] = num(r["pct_non_occupate_2023"])
        data[c]["case_vuote_var"] = num(r["variazione_pct_non_occupate_2019_2023"])
        data[c]["case_vuote_n"] = num(r["abitazioni_non_occupate_2023"])

    # --- Popolazione (ISTAT, via dataset qualità della vita) --------------
    # Nota: la colonna popolazione del dataset "case vuote" è doppia rispetto
    # al dato ISTAT (342.190 invece di 171.095 sull'area): non va usata.
    for r in read_csv("Qualità della vita 14 comuni Sudmilano/dati/dataset_comunale.csv", ";"):
        c = canon(r["comune"])
        data[c]["pop"] = num(r["pop_2026"])

    # --- Centenari (ISTAT POSAS 2026) -------------------------------------
    for r in read_csv("Centenari nei 14 comuni/centenari-sudmilano-14-comuni.csv", ";"):
        if r["comune"].startswith("TOTALE"):
            continue
        c = canon(r["comune"])
        data[c]["centenari_100k"] = num(r["tasso_100piu_per_100k"])
        data[c]["centenari_n"] = num(r["centenari_100piu_2026"])

    # --- Qualità della vita (indice composito) ----------------------------
    for r in read_csv("Qualità della vita 14 comuni Sudmilano/dati/classifica_indice.csv", ";"):
        c = canon(r["comune"])
        data[c]["indice_qv"] = num(r["indice"])
        data[c]["pos_qv"] = num(r["posizione"])
        data[c]["reddito"] = num(r["redd_complessivo_medio_2024"])
        data[c]["suolo_pct"] = num(r["suolo_pct"])
        data[c]["tasso_inc_2224"] = num(r["tasso_inc_2224"])

    # --- Incidenti stradali (ISTAT/ACI, microdati regionali) --------------
    inc2024 = {}
    for r in read_csv("Incidenti stradali nei 14 comuni/incidenti-serie-2010-2024-14-comuni.csv", ";"):
        if r["anno"] == "2024":
            inc2024[canon(r["comune"])] = num(r["n_incidenti"])
    for c, v in inc2024.items():
        data[c]["incidenti_2024"] = v

    # --- Apparati di velocità (Città metropolitana, set 2026) -------------
    autovelox = {c: 0 for c in COMUNI}
    for r in read_csv("Autovelox nei 14 comuni/rilevatori-14-comuni-tipizzati.csv", ";"):
        if "velocit" in r["tipo"].lower():
            autovelox[canon(r["comune"])] += 1
    for c, v in autovelox.items():
        data[c]["autovelox"] = v

    # --- Mercati (posti dichiarati per 1.000 abitanti) --------------------
    for r in read_csv("Mercati 14 comuni/elaborati/mercati_14_comuni.csv"):
        c = canon(r["comune"])
        data[c]["mercati_posti_1000"] = num(r["posti_per_1000_ab"])
        data[c]["mercati_n"] = num(r["mercati"])

    # --- Biblioteche (documenti e prestiti per abitante) ------------------
    for r in read_csv("Biblioteche 14 comuni/elaborati/biblioteche_14_comuni.csv"):
        c = canon(r["comune"])
        data[c]["biblio_doc_ab"] = num(r["documenti_per_ab"])
        data[c]["biblio_prestiti_ab"] = num(r["prestiti_per_ab"])

    # --- Appalti (ANAC, quota affidamenti diretti 2023-2025) -------------
    for r in read_csv("Appalti nei 14 comuni/tabella-comuni-2023-2025.csv", ";"):
        c = canon(r["comune"])
        data[c]["appalti_ad_pct"] = num(r["ad_pct"])

    # --- Beni confiscati (ANBSC) -----------------------------------------
    for r in read_csv("Criminalità organizzata nei 14 comuni/beni-confiscati-totali-14-comuni.csv", ";"):
        if r["comune"].startswith("TOTALE"):
            continue
        c = canon(r["comune"])
        data[c]["confiscati"] = num(r["totale_confiscati_2022"])

    # --- Aria: giorni di superamento PM10 nel 2025 ------------------------
    for r in read_csv("Qualita aria Paullo/elaborati/indicatori_14_comuni.csv"):
        if r["inquinante"] == "PM10" and r["anno"] == "2025":
            data[canon(r["comune"])]["pm10_giorni"] = num(r["giorni_superamento"])

    # --- Furti con esplosivo 2026 (solo episodi nel perimetro dei 14) -----
    furti = {c: 0 for c in COMUNI}
    for r in read_csv(
        "Furti con esplosivo a banche e Poste nei 14 comuni 2026/episodi-furti-esplosivo-14-comuni-2026.csv",
        ";",
    ):
        if r["perimetro"].strip() == "14 comuni":
            furti[canon(r["comune"])] += 1
    for c, v in furti.items():
        data[c]["furti_2026"] = v

    # --- Addizionale IRPEF su 30.000 € (MEF, anno d'imposta 2025) ---------
    # Ricavata dalla tabella verificata di report_pressione_fiscale.md.
    # Carpiano e Vizzolo Predabissi non sono fra i 12 comuni dell'inchiesta.
    addizionale = {
        "Dresano": 90, "San Giuliano Milanese": 104, "Cerro al Lambro": 106,
        "Pantigliate": 120, "Tribiano": 120, "Paullo": 120,
        "Peschiera Borromeo": 91, "Colturano": 168, "Melegnano": 144,
        "San Donato Milanese": 62, "Mediglia": 240, "San Zenone al Lambro": 240,
    }
    for c, v in addizionale.items():
        data[c]["addizionale_30k"] = v

    indicatori = [
        ("case_vuote_pct", "Case vuote", "Case vuote", "%", "case-vuote-sudmilano", "ISTAT · Censimento delle abitazioni 2023", "ISTAT 2023",
         "Abitazioni non occupate sul totale delle abitazioni.", "dec1", 1),
        ("centenari_100k", "Centenari", "Centenari", "per 100.000", "centenari-sudmilano", "ISTAT · POSAS, 1 gennaio 2026", "ISTAT 2026",
         "Residenti con 100 anni e più ogni 100.000 abitanti.", "dec1", 2),
        ("indice_qv", "Indice qualità della vita", "Indice QV", "0 = media", "qualita-vita-sudmilano", "Elaborazione su 11 indicatori comunali, 2026", "Elaborazione 2026",
         "Indice composito: reddito 30%, servizi 20%, ambiente 20%, sicurezza 15%, demografia 15%.", "dec2", 3),
        ("incidenti_2024", "Incidenti stradali", "Incidenti", "nel 2024", "incidenti-stradali-sudmilano", "ISTAT/ACI · microdati regionali", "ISTAT/ACI 2024",
         "Incidenti con lesioni registrati nel 2024.", "int", 4),
        ("autovelox", "Apparati di velocità", "Autovelox", "impianti", "autovelox-sudmilano", "Città metropolitana di Milano · settembre 2026", "CM Milano 2026",
         "Apparati di velocità media o istantanea, esclusi semaforici e monitoraggi.", "int", 5),
        ("appalti_ad_pct", "Affidamenti diretti", "Affidamenti", "%", "appalti-sudmilano", "ANAC · contratti 2023-2025", "ANAC 2023-25",
         "Quota di affidamenti diretti sul totale dei CIG del triennio.", "dec1", 6),
        ("pm10_giorni", "Giorni oltre il limite PM10", "PM10", "nel 2025", "aria-paullo", "ARPA Lombardia · stime modellistiche", "ARPA 2025",
         "Giorni con media giornaliera sopra 50 µg/m³ (limite: 35).", "int", 7),
        ("mercati_posti_1000", "Posti di mercato", "Mercati", "per 1.000 ab.", "mercati-sudmilano", "Regione Lombardia e Città metropolitana · 2026", "Regione/CM 2026",
         "Posti dichiarati nei mercati settimanali ogni 1.000 abitanti.", "dec2", 8),
        ("biblio_doc_ab", "Documenti in biblioteca", "Biblioteca", "per abitante", "biblioteche-sudmilano", "Anagrafe biblioteche · 2025", "ICCU 2025",
         "Consistenza documentale per abitante.", "dec2", 9),
        ("case_vuote_var", "Variazione case vuote", "Variazione case vuote", "p.p.", "case-vuote-sudmilano", "ISTAT · 2019 → 2023", "ISTAT 2019-23",
         "Variazione in punti percentuali della quota di abitazioni non occupate.", "dec1", 10),
        ("reddito", "Reddito medio", "Reddito medio", "€", "qualita-vita-sudmilano", "MEF · dichiarazioni 2024", "MEF 2024",
         "Reddito complessivo medio per contribuente.", "int", 11),
        ("suolo_pct", "Suolo consumato", "Suolo consumato", "%", "qualita-vita-sudmilano", "ISPRA · Rapporto 2026, dati 2025", "ISPRA 2025",
         "Percentuale di territorio comunale consumata.", "dec1", 12),
        ("tasso_inc_2224", "Incidenti per 1.000 ab.", "Incidenti/1.000 ab.", "2022-24", "incidenti-stradali-sudmilano", "ISTAT/ACI · media 2022-2024", "ISTAT/ACI 2022-24",
         "Incidenti per 1.000 abitanti, media del triennio.", "dec2", 13),
        ("biblio_prestiti_ab", "Prestiti di biblioteca", "Prestiti biblioteca", "per abitante", "biblioteche-sudmilano", "Anagrafe biblioteche · 2025", "ICCU 2025",
         "Prestiti per abitante nell'anno.", "dec2", 14),
        ("confiscati", "Immobili confiscati", "Immobili confiscati", "totale", "criminalita-organizzata-sudmilano", "ANBSC · 2022", "ANBSC 2022",
         "Immobili confiscati in gestione o destinati.", "int", 15),
        ("furti_2026", "Furti con esplosivo", "Furti con esplosivo", "episodi 2026", "furti-esplosivo-sudmilano", "Rassegna stampa · ottobre 2026", "Stampa 2026",
         "Episodi nel perimetro dei 14 comuni; solo casi resi pubblici.", "int", 16),
        ("addizionale_30k", "Addizionale IRPEF su 30.000 €", "Addizionale IRPEF", "€", "fiscalita-sudmilano", "MEF · anno d'imposta 2025", "MEF 2025",
         "Addizionale comunale calcolata su 30.000 € di imponibile. Mancano Carpiano e Vizzolo.", "int", 17),
    ]

    out_indicatori = []
    for key, label, label_breve, unit, inchiesta, fonte, fonte_breve, desc, fmt, order in indicatori:
        out_indicatori.append({
            "id": key, "label": label, "label_breve": label_breve, "unita": unit, "inchiesta": inchiesta,
            "fonte": fonte, "fonte_breve": fonte_breve, "descrizione": desc,
            "formato": fmt, "ordine": order,
        })

    comuni_out = []
    for c in sorted(COMUNI, key=lambda x: x.lower()):
        row = {"nome": c}
        row.update({k: v for k, v in data[c].items()})
        comuni_out.append(row)

    # --- letture: correlazioni calcolate, non raccontate a memoria --------
    def pearson(a, b):
        pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
        if len(pairs) < 4:
            return None, len(pairs)
        xs, ys = zip(*pairs)
        try:
            return statistics.correlation(xs, ys), len(pairs)
        except Exception:
            return None, len(pairs)

    def col(k):
        return [data[c].get(k) for c in COMUNI]

    letture = []
    checks = [
        ("case_vuote_pct", "reddito", "Case vuote e reddito"),
        ("case_vuote_pct", "indice_qv", "Case vuote e indice di qualità della vita"),
        ("biblio_doc_ab", "reddito", "Dotazione delle biblioteche e reddito"),
        ("appalti_ad_pct", "pop", "Affidamenti diretti e dimensione del comune"),
        ("pm10_giorni", "suolo_pct", "PM10 e suolo consumato"),
    ]
    for a, b, label in checks:
        r, n = pearson(col(a), col(b))
        letture.append({"a": a, "b": b, "label": label, "r": None if r is None else round(r, 3), "n": n})

    payload = {
        "comuni": comuni_out,
        "indicatori": out_indicatori,
        "letture": letture,
        "titoli": {},
        "meta": {
            "n_comuni": len(COMUNI),
            "n_indicatori": len(out_indicatori),
            "nota": "Ogni colonna conserva la fonte e l'inchiesta di origine. Dove il dato manca la cella resta vuota: non è uno zero.",
        },
    }

    # titoli delle inchieste, per i rimandi dalla scheda comune
    percorso_inchieste = os.path.join(HERE, "content", "inchieste.json")
    if os.path.exists(percorso_inchieste):
        with open(percorso_inchieste, encoding="utf-8") as fh:
            contenuti = json.load(fh)
        for voce in contenuti.get("inchieste", []):
            payload["titoli"][voce["slug"]] = voce["titolo"]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    # --- controllo di completezza ----------------------------------------
    print("Atlante scritto in", OUT)
    print("Comuni:", len(comuni_out), "| indicatori:", len(out_indicatori))
    for ind in out_indicatori:
        filled = sum(1 for r in comuni_out if r.get(ind["id"]) is not None)
        print("  %-24s %2d/14" % (ind["id"], filled))
    print("Correlazioni:")
    for l in letture:
        print("  %-48s r=%s n=%s" % (l["label"], l["r"], l["n"]))


if __name__ == "__main__":
    main()
