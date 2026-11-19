# Nota metodologica — Case vuote Sudmilano

## Perimetro

Quattordici comuni della provincia di Milano: Paullo, Mediglia, Pantigliate, Tribiano,
Peschiera Borromeo, San Giuliano Milanese, San Donato Milanese, Melegnano, San Zenone al Lambro,
Carpiano, Cerro al Lambro, Colturano, Dresano, Vizzolo Predabissi.

Il comune indicato nella richiesta come «Sano Donato Milanese» è stato interpretato come
**San Donato Milanese**.

## Fonti e dataflow

### ISTAT — Censimento permanente delle abitazioni (banca dati SDMX)

Base API: `https://esploradati.istat.it/SDMXWS/rest/data/IT1,<FLOW>,1.0/all?format=jsondata&dimensionAtObservation=AllDimensions`

| Dataflow | Contenuto | Anni | Livello |
|---|---|---|---|
| DF_DCSS_ABITAZIONI_TV_1 | stato di occupazione delle abitazioni convenzionali (NUM_DW_AV, NUM_OCC_DW_AV, NUM_UNOCC_DW_AV) | 2019, 2021, 2023 | comune |
| DF_DCSS_ABITAZIONI_TV_2 | titolo di godimento (proprietà / affitto / altro) | dettaglio solo 2019 | comune |
| DF_DCSS_HCUE_COM_7_COM | occupate e non occupate per tipo di edificio | dettaglio solo 2021 | comune |
| DF_DCSS_HCUE_COM_8_COM | living quarters, convivenze, altri alloggi | 2021, 2023 | comune |
| DF_DCSS_HUDW_2_PROV | abitazioni per epoca di costruzione e stato di occupazione | 2021 | provincia |
| DF_DCSS_HUDW_3_PROV | occupate per classi di superficie e numero di occupanti | 2021 | provincia |
| DF_DCSS_HUDW_4_PROV | densità abitativa (mq per persona) | 2021 | provincia |
| DF_DCSS_HUDW_1_COM | famiglie per titolo di godimento | — | comune |
| DF_DCSS_HUDW_6_COM | famiglie per tipo di alloggio | 2023 | comune |

### ISTAT — Censimento permanente 2023 per sezione di censimento

File regionali scaricati da:
`https://esploradati.istat.it/databrowser/DWL/PERMPOP/SUBCOM/Dati_regionali_2023.zip`
(261 MB, contiene un xlsx per regione; per la Lombardia `R03_Lombardia_2023_sezioni.xlsx`).

Campi utilizzati: `PROCOM`, `COMUNE`, `SEZ21_ID`, `P1` (popolazione), `A2` (abitazioni occupate
da residenti), **`A3` (abitazioni vuote e occupate solo da persone non residenti)**, `A5` (altri
alloggi occupati), `A8` (abitazioni totali), `PF1` (famiglie), `PF3`–`PF8` (famiglie per numero di
componenti), **`PF9` (famiglie coabitanti)**.

### ISTAT — popolazione residente

File POSAS provinciali, anni 2019-2026 (popolazione residente per età e sesso al 1° gennaio).

### Agenzia delle Entrate — OMI

Banca dati delle quotazioni immobiliari, primo semestre 2018, filtrata sulle tipologie
residenziali (abitazioni civili, economiche, signorili, ville e villini, abitazioni tipiche dei
luoghi). I semestri successivi non sono disponibili in formato aperto per l'intero territorio
comunale: il file 2025/2 reperito in open data copre il solo Comune di Milano.

## Verifiche eseguite

1. **Quadratura contabile**: `abitazioni occupate + non occupate = totale` su 42 righe
   (14 comuni × 3 anni). Esito: **0 sbilanci**.
2. **Confronto incrociato fra due pubblicazioni ISTAT indipendenti** — banca dati SDMX
   (`DF_DCSS_ABITAZIONI_TV_1`) e file per sezione di censimento 2023 (somma di A8 e A3 per comune).
   Esito: coincidenza **all'unità** per tutti e 14 i comuni, sia sul totale delle abitazioni sia
   sulle non occupate.
3. **Ricalcolo dell'aggregato**: 7.617 / 81.686 = 9,32%.
4. **Benchmark da stesso dataflow** ai livelli IT / ITC4 / ITC45: 27,17% / 21,16% / 12,43%.

## Avvertenze

- Il Censimento permanente è un'**indagine campionaria**: i valori sono stime e possono presentare
  decimali.
- **«Abitazione non occupata» non equivale ad «abitazione disponibile»**: la categoria comprende
  seconde case, immobili in vendita o in affitto, alloggi in ristrutturazione, abitazioni tenute
  libere per scelta e casi di persone temporaneamente assenti.
- ISTAT segnala che fra il 2021 e il 2023 sono state migliorate le procedure di collegamento fra
  famiglie, abitazioni ed edifici: **parte della variazione osservata può essere di natura tecnica**.
- Le variazioni su basi piccole (Colturano, Vizzolo Predabissi, Dresano) vanno lette con prudenza.
- **Epoca di costruzione e densità abitativa non sono disponibili a livello comunale**: i valori
  provinciali non sono attribuibili ai singoli comuni.
- Le quotazioni OMI del 2018 **non riflettono i prezzi correnti**.

## Dati non pubblici e come ottenerli

| Dato | Perché manca | Come ottenerlo |
|---|---|---|
| Ragioni della non occupazione per comune | ISTAT non le diffonde a livello locale | Microdati del Censimento permanente (richiesta a ISTAT per fini di ricerca) |
| Sovraffollamento comunale | densità abitativa diffusa solo per provincia | Microdati ISTAT |
| Epoca di costruzione per comune | diffusa solo per provincia | Microdati ISTAT |
| ERP: domande, graduatorie, assegnazioni | non pubblicate in forma aggregata | Accesso civico, art. 5 c. 2 D.Lgs. 33/2013 |
| Sfratti avviati ed eseguiti | idem | Accesso civico / Prefettura di Milano |
| Morosità incolpevole, fondo affitti | idem | Accesso civico al singolo comune |
