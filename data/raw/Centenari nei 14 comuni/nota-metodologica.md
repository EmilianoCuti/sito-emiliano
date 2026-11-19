# Nota metodologica — Centenari nel Sudmilano

**Data di riferimento dei dati:** 1° gennaio 2026 (stima ISTAT).
**Data di elaborazione:** 4 novembre 2026.
**Perimetro:** 14 comuni del Sudmilano — Dresano, Tribiano, Cerro al Lambro, San Zenone al Lambro, Peschiera Borromeo, Vizzolo Predabissi, San Donato Milanese, Pantigliate, Colturano, Melegnano, Carpiano, Mediglia, Paullo, San Giuliano Milanese.

## 1. Fonte primaria

ISTAT, *Popolazione residente per età e sesso al 1° gennaio 2026 (stima)*, file per la provincia di Milano:
`https://demo.istat.it/data/posas/POSAS_2026_it_015_Milano.zip`
(pagina di accesso: `https://demo.istat.it/app/?i=POS&l=it`)

Struttura del file 2026: colonne `Codice comune; Comune; Età; Totale maschi; Totale femmine; Totale`. Le età vanno da 0 a 100; **l’età 100 è la classe aggregata “100 e oltre”**; la riga con età `999` riporta il totale comunale (non va sommata alle altre).

Per le serie storiche 2019-2025 il tracciato contiene anche lo stato civile (20 colonne): il parsing è stato fatto mappando le colonne per nome (`Comune`, `Età`, `Totale maschi`, `Totale femmine`, `Totale`), non per posizione.

## 2. Nota ISTAT sulla stima 2026 (testuale)

> «La popolazione per età e sesso al 1° Gennaio 2026 è una stima in linea con le risultanze censuarie e il bilancio provvisorio 2025. La distribuzione per stato civile non è disponibile. La distribuzione territoriale è in linea con quella del bilancio provvisorio 2025.»

## 3. Definizioni e indicatori

- **Centenario:** persona residente con 100 anni compiuti e più (classe “100 e oltre”).
- **Tasso per 100.000:** `centenari / popolazione residente × 100.000`.
- **Quota 65+:** `residenti con 65 anni e più / popolazione × 100`.
- **Variazione 2019-2026:** differenza assoluta tra i due stock, non un tasso di crescita annuo.

## 4. Limiti

1. **Età aggregata.** ISTAT non pubblica l’età esatta dei singoli centenari: non è possibile sapere, dal solo dato open, quanti hanno 101, 105 o 110 anni.
2. **Stima.** I valori 2026 sono stime coerenti con il bilancio provvisorio 2025, non un conteggio anagrafico certificato al giorno.
3. **Arrotondamenti.** I valori per singolo anno di età sono arrotondati; su basi comunali piccole un’unità di differenza può cambiare sensibilmente le percentuali.
4. **Residenti ≠ presenti.** Chi vive in una Rsa di un altro comune resta conteggiato nel comune di residenza anagrafica. È il caso di Gina Roma (residente a Peschiera Borromeo, ospite a Melegnano).
5. **Data fissa.** Chi compie 100 anni nel corso del 2026 non è incluso nei 46 al 1° gennaio 2026: i 99enni residenti all’inizio dell’anno erano 31.
6. **Confronti nazionali/regionali.** Il dato Italia 2026 (24.700) è una stima diffusa con gli indicatori demografici di marzo 2026; il dato Lombardia (≈4.000) è al 1° gennaio 2025. I tassi di confronto sono ordini di grandezza, non misure omogenee.

## 5. Verifica

- Doppio calcolo indipendente dei totali (script `estrai_posas.py` e `build_dataset.py`): 46 centenari, 171.095 residenti, 26,89 per 100.000.
- Controllo di coerenza interna: somma dei 14 comuni = totale area; somma per sesso = totale (39 + 7 = 46).
- Controllo della serie storica: 23 (2019), 26 (2020), 28 (2021), 26 (2022), 23 (2023), 25 (2024), 34 (2025), 46 (2026).
- Riscontro esterno sul caso più anziano: Gina Roma, 106 anni, articoli de Il Cittadino (28/04/2026) e 7giorni (29/04/2026), concordanti su data di nascita (28 aprile 1920) e residenza (Peschiera Borromeo).
- Riscontro esterno sul record storico: Ida Ortolani, 1912-2024, articolo de Il Cittadino (8/03/2023) + Gerontology Research Group + LongeviQuest.

## 6. Dato non pubblico e come ottenerlo

ANPR non pubblica open data per età a livello comunale; i comuni non tengono un registro pubblico dei centenari. Per il dato fine (singolo anno di età, sesso, età del più anziano) serve una richiesta scritta all’Ufficio Anagrafe del comune, ai sensi della normativa su accesso e riuso dei dati pubblici. Modello: `richiesta-dati-anagrafe.md`.
