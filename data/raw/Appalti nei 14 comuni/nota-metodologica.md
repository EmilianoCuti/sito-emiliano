# Nota metodologica — Appalti e affidamenti nei 14 comuni del Sudmilano

**Data di elaborazione:** 4 novembre 2026
**Periodo coperto:** 1 gennaio 2019 – 31 dicembre 2025
**Unità di analisi:** contratto (CIG) attribuito a una stazione appaltante comunale

---

## 1. Perimetro

Quattordici amministrazioni comunali della rete «Fuori dal Silenzio»:

Dresano, Tribiano, Cerro al Lambro, San Zenone al Lambro, Peschiera Borromeo, Vizzolo Predabissi, San Donato Milanese, Pantigliate, Colturano, Melegnano, Carpiano, Mediglia, Paullo, San Giuliano Milanese.

Il perimetro è definito dalla **stazione appaltante**, non dal luogo di esecuzione. Un contratto firmato dal Comune di Melegnano per lavori a Lodi entra nel conteggio di Melegnano; un contratto firmato da ARIA o da una CUC per conto di Melegnano **non** entra, perché la stazione appaltante è un altro soggetto.

Codici fiscali usati per il filtro (15, perché Peschiera Borromeo ha un codice cessato e uno attivo):

| Comune | Codice fiscale |
|---|---|
| Carpiano | 84501650158 |
| Cerro al Lambro | 84503860151 |
| Colturano | 84503720157 |
| Dresano | 84503760153 |
| Mediglia | 84503580155 |
| Melegnano | 84507510158 |
| Pantigliate | 80108750151 |
| Paullo | 84503130159 |
| Peschiera Borromeo | 05802370154 (cessato) · 80101570150 (attivo) |
| San Donato Milanese | 00828590158 |
| San Giuliano Milanese | 00798940151 |
| San Zenone al Lambro | 84504020151 |
| Tribiano | 84503590154 |
| Vizzolo Predabissi | 84503700159 |

Tenuti separati e non inclusi nelle tabelle per comune due organismi sovracomunali con sede nell'area, che gestiscono servizi per più amministrazioni:

- **Unione dei Comuni Sud Est Milano Parco dell'Addetta** — CF 08961840967 (2 CIG nel periodo)
- **Azienda Sociale Sud Est Milano** — CF 97529770154 (131 CIG nel periodo)

---

## 2. Fonti

Tutte le fonti sono open data ufficiali, scaricate il 4 novembre 2026 dal portale ANAC (`https://dati.anticorruzione.it/opendata`).

| Dataset | Cosa contiene | File scaricati | Dimensione |
|---|---|---|---|
| **CIG** (annuale, 2019–2025) | un record per CIG: oggetto, importi, procedura, stazione appaltante, luogo, esito | 84 file mensili `.zip` (uno per mese/anno) | ~6 GB compressi |
| **Aggiudicazioni** | per CIG: data, importo di aggiudicazione, ribasso, numero offerte ammesse/escluse | 1 file cumulativo | 724 MB |
| **Aggiudicatari** | per CIG: codice fiscale, ragione sociale, ruolo, tipo soggetto | 1 file cumulativo | 763 MB |
| **Stazioni appaltanti** | anagrafica enti con CF/P.IVA e sede | 1 file | 12 MB |
| **ANBSC — aziende in amministrazione** | aziende sequestrate/confiscate con P.IVA, sede, settore | endpoint JSON `benidestinati.anbsc.it/api/data/beni/aziende/in_amministrazione` | 3.457 record |
| **VIES — Commissione europea** | ragione sociale e indirizzo IVA degli operatori | API REST `ec.europa.eu/taxation_customs/vies/rest-api` | 206 interrogazioni |

I file CIG sono stati scaricati in streaming: ogni mese viene aperto, filtrato e cancellato. Non è conservata copia dei grezzi (sono rigenerabili in circa 20 minuti dagli URL pubblici, vedi §7).

---

## 3. Estrazione e consolidamento

1. **Filtro** su `cf_amministrazione_appaltante` ∈ (15 codici) **oppure** `denominazione_amministrazione_appaltante` che inizia con `COMUNE DI <nome>`.
2. **Consolidamento** in un unico file `cig_14comuni.csv`, con deduplica per CIG: se lo stesso CIG compare in più mesi (aggiornamenti successivi), resta la versione con `data_pubblicazione` più recente.
3. **Join** con aggiudicazioni e aggiudicatari tramite CIG.
4. **Classificazione della procedura** in sei categorie leggibili a partire da `tipo_scelta_contraente`.

Risultato: **2.801 CIG**, di cui **2.722 validi** ai fini economici.

---

## 4. Pulizia degli importi

La banca dati è compilata dalle stazioni appaltanti e contiene errori materiali. Sono stati esclusi dagli aggregati economici **79 record** (6,39 miliardi di euro dichiarati), secondo tre regole dichiarate:

| Regola | Motivo | Record |
|---|---|---|
| Affidamento diretto con importo > 300.000 € | la soglia di legge è 140.000 € (servizi/forniture) e 150.000 € (lavori): l'importo è implausibile o è quello di una convenzione | 77 |
| Contratto con CIG di accordo quadro e importo > 1.000.000 € | importo della convenzione, non del singolo affidamento | 2 |
| Importo ≤ 0 | dato assente | 0 |

Tutti i record esclusi sono elencati in `anomalie-importi.csv` con CIG, oggetto e importo dichiarato. **Attenzione:** due soli CIG (B70D7E6DE8 e B73B5363F7, Comune di Vizzolo Predabissi, 2.627.503.530 € ciascuno) valgono 5,26 miliardi, l'82,2% dell'intero importo escluso. Il totale «6,39 miliardi esclusi» non descrive quindi un fenomeno diffuso: descrive due righe fuori scala. **Nessun importo è stato corretto d'ufficio**: la correzione avrebbe nascosto un fatto (l'errore di dichiarazione), che è a sua volta un'informazione.

Il campo usato è `importo_lotto` (rinominato `importo` nel dataset consolidato). Differisce da `importo_gara` in 74 righe: chi ricalcola su `importo_gara` ottiene totali diversi. Il valore è quello del **lotto**, non dell'intera gara: per le gare multilotto la somma dei lotti può eccedere l'importo della gara.

---

## 5. Definizione degli indicatori

| Indicatore | Formula | Campo |
|---|---|---|
| **Quota affidamenti diretti (numero)** | CIG con `tipo_scelta_contraente` che inizia per «AFFIDAMENTO DIRETTO» / CIG validi | tipo_scelta_contraente |
| **Quota affidamenti diretti (valore)** | somma importi AD / somma importi validi | importo |
| **Quota sopra i 40.000 €** | stessa formula, sui soli CIG con importo ≥ 40.000 € | importo |
| **Gare con una sola offerta** | procedure aperte/negoziate con `numero_offerte_ammesse` ≤ 1 / procedure con dato | numero_offerte_ammesse |
| **Ribasso mediano** | mediana di `ribasso_aggiudicazione` sulle procedure competitive, valori 0–100 | ribasso_aggiudicazione |
| **Concentrazione top 5** | importo ai primi 5 operatori / importo aggiudicato con operatore noto | join aggiudicatari |
| **HHI** | somma dei quadrati delle quote di importo per operatore, ×10.000 | join aggiudicatari |
| **Operatori ricorrenti** | operatori con ≥ 3 comuni e ≥ 5 aggiudicazioni | join aggiudicatari |
| **Fuori regione** | aggiudicazioni con provincia VIES non lombarda / aggiudicazioni con provincia nota | VIES |
| **Frazionamento** | ≥ 4 affidamenti diretti nello stesso comune, anno e prime 3 cifre CPV, per > 100.000 € | cod_cpv |

Per i raggruppamenti temporanei l'importo è ripartito in parti uguali tra i componenti, per evitare doppi conteggi.

---

## 6. Copertura e limiti

| Dato | Copertura | Effetto |
|---|---|---|
| Contratti con almeno un aggiudicatario | 2.368 / 2.801 (85%) | le analisi sugli operatori coprono l'85% dei contratti |
| Contratti con esito di aggiudicazione | 2.379 / 2.801 (85%) | ribassi e numero offerte calcolati sul sottoinsieme |
| Aggiudicatari con provincia nota (VIES) | 206 operatori, 32,3% dell'importo | «fuori regione» è un campione, non un censimento |
| Contratti sotto i 40.000 € prima del 2023 | **non coperti** (erano in SmartCIG) | la serie 2019–2022 non è confrontabile con 2023–2025 |

**Altri limiti da dichiarare:**

- **Centrali di committenza.** Se un comune acquista tramite ARIA, CUC o provincia, il contratto è registrato a nome della centrale. La quota di affidamento diretto del comune può risultare sottostimata.
- **Importi.** Il valore è quello dichiarato dalla stazione appaltante, non verificato su fatture o contratti.
- **Interdittive antimafia.** Non esiste un elenco pubblico nominativo: l'incrocio con i provvedimenti interdittivi **non è stato possibile**. È la richiesta principale da fare (vedi `richiesta-accesso-civico.md`).
- **Anomalia non è reato.** Un affidamento diretto entro soglia è legale; un ribasso nullo è legale; un fornitore ricorrente è legale. Gli indicatori servono a selezionare i casi da verificare documentalmente.

---

## 7. Come riprodurre i numeri

Tutti gli script sono in `/Volumes/Repos/openclaw-tools/anac-appalti/`:

```bash
# 1. scarica e filtra i 84 file mensili CIG 2019-2025 (~20 min)
bash fetch_all.sh cig 2019 2025

# 2. consolida in un unico dataset
python3 build_dataset.py

# 3. calcola gli indicatori
python3 analyze.py
python3 analyze_comp.py

# 4. sede legale degli operatori (VIES)
python3 vies_lookup.py

# 5. genera il report HTML e i CSV di consegna
python3 build_report.py
```

Output intermedi in `dataset/`, report in `.cluster/0fb3b1c6-.../DELIVERY/`.

Per aggiornare al 2026: il dataset annuale CIG 2026 sarà pubblicato da ANAC a gennaio 2027. Il comando è lo stesso (`bash fetch_all.sh cig 2026 2026`), ma il file `cig-2026` non esiste ancora: fino ad allora si possono usare i delta mensili del dataset `cig` (copertura parziale).

---

## 8. Verifiche effettuate

- **Doppio calcolo indipendente** dei tre numeri chiave (CIG totali, quota AD 2023–2025, importo valido) con script separato: esito in `subagent_05_verifica.md`.
- **Conteggio di controllo:** la somma dei CIG per anno (183+243+295+242+350+715+773) coincide con il totale 2.801 registrati.
- **Confronto con benchmark nazionale** ANAC su universo omologo (≥ 40.000 €): 69,8% vs 54,3% (2024).
- **Verifica dei falsi positivi** nell'incrocio con l'elenco ANBSC: il caso omonimo è stato scartato dopo controllo della partita IVA su VIES.
- **Controllo dei ribassi**: 461 procedure competitive con ribasso utilizzabile; 6 valori negativi (fino a −500.000) esclusi come errori di dichiarazione; mediana 7,0%, 107 gare a ribasso nullo, 66 sopra il 30%.
