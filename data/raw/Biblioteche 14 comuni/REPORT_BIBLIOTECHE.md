# Le biblioteche comunali nei 14 comuni del Sudmilano

Inchiesta n. 8 dell'archivio. Dati aperti della Città metropolitana di Milano e
della Regione Lombardia, consultati il 1 ottobre 2026.

## Sintesi

Tutti i 14 comuni hanno almeno una biblioteca: **18 sedi** complessive. Nessun
comune dell'area è senza.

Il dato che conta non è la presenza, che è universale, ma la **dotazione**. Per
patrimonio documentale per abitante, cinque comuni dell'area sono nella metà
inferiore dei 131 comuni della città metropolitana. **Mediglia è l'ultimo in
assoluto**: 4.490 documenti per 12.313 abitanti, **0,365 per abitante** contro
una mediana di 2,08. Cinque volte meno della mediana, con un costo di
funzionamento dichiarato di 47.378 euro e 32.352 euro di spese per il personale.

Il limite più importante dell'inchiesta è che il dataset non distingue il
personale **per sede**: nei comuni con più sedi, tutte riportano lo stesso
numero di dipendenti. Quindi il personale è confrontabile **a livello di
comune**, non di sede, e le tabelle lo trattano così.

Il secondo limite è dichiarato nel capitolo sui dati mancanti: il campo
`numero_visite_annuali` vale zero in 199 comuni su 214 della città
metropolitana, quindi non è usabile in nessun modo. La fruizione è misurata
qui con i prestiti, che sono dati reali.

## Le fonti

Tre dataset su `dati.lombardia.it` (Socrata, senza autenticazione):

1. **`ex8z-wf22` — Biblioteche comunali CM Milano**, 215 righe, **187 sedi
   distinte**. È la fonte primaria e contiene tutti gli indicatori: superficie,
   personale di ruolo e FTE, consistenza documentale, prestiti, iscritti,
   postazioni pubbliche, spese di funzionamento e di personale, accessibilità,
   sezioni speciali, wifi, riproduzioni digitali.
2. **`7x6q-jhbd` — Anagrafe Biblioteche Comunali Lombarde**, 1.308 righe
   scaricate (**1.428 nel file, di cui 120 con dati ridotti**). Fonte
   indipendente per anno di fondazione, natura, ente appartenente e secolo
   dell'edificio.
3. **`u9gu-9wf3` — Popolazione residente al 31.12.2022**, 133 righe, presenti
   tutti i 14 comuni. Serve come denominatore di ogni rapporto.

## Una trappola meccanica che ho dovuto scardinare

Le 215 righe del dataset CM **non sono 215 biblioteche**. Sono **187 sedi**,
perché 27 sedi hanno più di una riga.

Le righe multiple **non sono duplicati**: sono la stessa sede con **orari di
apertura diversi**, distinguibili per il progressivo `prog` e dai 26 campi
`lun_*`/`mar_*`/`mer_*`/`gio_*`/`ven_*`/`sab_*`. Verificato programmaticamente:
le righe di una stessa sede differiscono **solo** su quei campi orari, mai sui
dati. Zero sedi presentano incongruenze.

Deduplicare per `codice_istat` — che identifica la sede, non la riga — avrebbe
distrutto 28 sedi in più o prodotto numeri senza senso. Il codice ISTAT serve
per il join con la popolazione, non per contare le biblioteche.

Sulla stessa fonte c'è un campo che sembra un problema ed è invece una scelta
amministrativa: **`personale_ruolo = 0`** compare in **26 sedi su 215** della
città metropolitana. Nel caso di Tribiano significa che la biblioteca non ha
dipendenti in ruolo ma ha **1 persona non di ruolo retribuita** (0,39 FTE). Non
è una biblioteca senza personale: è una biblioteca con personale fuori ruolo.

## Il quadro dei 14 comuni

| Comune | Abitanti | Sedi | Sup. m² | Pers. | Documenti | Doc./ab. | Prest./ab. | Spese €/ab. |
|---|---|---|---|---|---|---|---|---|
| Dresano | 3.066 | 1 | 270 | 1 | 11.417 | 3,72 | 1,33 | 2,45 |
| Colturano | 2.047 | 1 | 75 | 1 | 5.465 | 2,67 | 0,28 | 5,83 |
| San Zenone al Lambro | 4.420 | 1 | 160 | 1 | 11.787 | 2,67 | 1,15 | 10,30 |
| Vizzolo Predabissi | 3.894 | 1 | 241 | 1 | 10.028 | 2,58 | 0,70 | 9,44 |
| Paullo | 11.099 | 1 | 275 | 3 | 25.306 | 2,28 | 0,77 | 12,24 |
| Pantigliate | 5.777 | 1 | 250 | 2 | 11.895 | 2,06 | 1,38 | 7,91 |
| Melegnano | 18.018 | 1 | 1.224 | 5 | 35.829 | 1,99 | 1,28 | 12,74 |
| Peschiera Borromeo | 24.355 | 2 | 190 | 8 | 46.946 | 1,93 | 1,05 | 8,24 |
| San Donato Milanese | 32.142 | 3 | 1.324 | 18 | 56.327 | 1,75 | 0,84 | 12,55 |
| Tribiano | 3.721 | 1 | 80 | 0 | 4.813 | 1,29 | 0,33 | 8,48 |
| San Giuliano Milanese | 39.604 | 2 | 820 | 10 | 45.284 | 1,14 | 0,55 | 8,45 |
| Cerro al Lambro | 5.145 | 1 | 60 | 1 | 5.782 | 1,12 | 0,26 | 4,45 |
| Carpiano | 4.135 | 1 | 135 | 2 | 4.013 | 0,97 | 0,21 | 4,96 |
| **Mediglia** | 12.313 | 1 | 200 | 1 | **4.490** | **0,37** | **0,08** | 3,85 |

*Documenti = consistenza totale (stampati + multimediali). Spese per abitante
sulle spese di funzionamento dichiarate, non su quelle del personale. Mediana
della città metropolitana: 2,08 documenti per abitante.*

## I due casi che meritano attenzione

**Mediglia è l'ultimo comune della città metropolitana per dotazione
documentale.** 4.490 documenti, di cui 4.486 stampati e **4 multimediali**. Con
12.313 abitanti è 0,365 per abitante: il secondo peggio è Noviglio a 0,427,
quinto Carpiano a 0,970. La mediana dei 131 comuni è 2,08.

Il dato che rende la cosa seria è che Mediglia **non è povera in assoluto**.
Spende **47.378 euro** di funzionamento di cui **32.352 di personale** per una
sede da 200 m², e ha 50 postazioni pubbliche — più di Cerro al Lambro, Colturano
e Vizzolo. Ha una sola persona di ruolo a tempo pieno (1,00 FTE). Il costo della
biblioteca èci, il patrimonio che lo giustifica no. E la sede è dichiarata
**non accessibile**.

**San Donato Milanese ha 18 dipendenti di ruolo su tre sedi**, il dato più alto
dell'area, ma è anche quello con i documenti per abitante più bassi fra i comuni
grandi (1,75). La spiegazione è nel campo dedicato: delle tre sedi, la sede
decentrata di Poasco ha **1.324 m² di superficie aggregata** con personale
condiviso. Il personale è il più alto dell'area e il patrimonio documentale è
nella parte bassa della graduatoria comunale: è la sede periferica a trainare
il dato, non il centro.

## Accessibilità e dotazione tecnologica

Delle 18 sedi, **17 sono dichiarate accessibili**. L'unica eccezione è
**Mediglia**, che è anche il caso peggiore per dotazione documentale.

Il wifi è disponibile in **9 sedi su 18**. Assente in Cerro al Lambro, Colturano,
Dresano, Melegnano, San Zenone al Lambro, Tribiano e Vizzolo Predabissi. Il
campo `riproduzioni_digitali` è "No" per tutte le 18 sedi: nessuna offre
riproduzione digitale.

I totale postazioni pubbliche dell'area è **724**, con una distribuzione molto
diseguale: Melegnano da sola ne ha 137, mentre Peschiera Borromeo ha 50 nella
sede centrale e **3** nella sede decentrata di San Bovio.

## Gli anni di fondazione

Dall'anagrafe regionale, che è fonte indipendente: le 18 sedi dell'area sono
nate fra il **1957** (Peschiera Borromeo, la più antica) e il **2012** (Dresano,
la più recente). Le più vecchie sono Melegnano 1968, San Giuliano 1970, San
Zenone al Lambro 1970, Mediglia 1972.

Undici sedi su 18 sono in edifici del Novecento o precedenti; sette sono in
edifici di nuova costruzione o restaurati.

## Lo stato dei dati mancanti

| Campo | Sedi prive di dato su 215 |
|---|---|
| `spese_funzionamento_tot` | **44** |
| `spese_personale` | **32** |
| `tot_consistenza_documenti` | 1 |
| `iscritti_al_prestito` | 1 |
| `totale_postazioni_pubblico` | 1 |
| `numero_visite_annuali` | 1 |

**`numero_visite_annuali` è da scartare**: non è un campo con buchi, è un campo
compilato solo sporadicamente. Su 214 righe compilate, **199 valgono zero**. I
valori non nulli sono 15 righe su **8 comuni** della città metropolitana, e
nessuno dei 14 comuni dell'area è fra questi: il più alto è Cinisello Balsamo
con 496.837. Trattarlo come dato sarebbe concludere che 199 biblioteche non
registrano visitatori, cosa che il dataset non consente di distinguere da una
mancata rilevazione. La fruizione qui è misurata con i prestiti, che sono
compilati per tutte le sedi.

Le spese di funzionamento mancano su 44 sedi della città metropolitana, quelle
del personale su 32. Nell'area tutte le 18 sedi hanno il dato di funzionamento
compilato, quindi i rapporti €/abitante sono calcolabili per tutti i 14 comuni.

Un campo da usare con cautela: **`spese_personale` è 0 per Dresano** pur avendo
un dipendente di ruolo (0,03 FTE) e 7.518 euro di spese totali. Uno zero in
questo campo non significa che non ci sia personale.

## Cosa non è stato possibile stabilire

1. **Il personale per sede nei comuni con più sedi.** Il dataset riporta lo
   stesso numero per tutte le sedi dello stesso comune. Il confronto è quindi
   valido fra comuni, non fra sedi.
2. **Le visite.** Nessun dato utilizzabile.
3. **L'utenza.** Gli iscritti al prestito ci sono, ma non c'è nessun campo che
   dica chi sono e quanto vengono: manca del tutto la domanda sociale.
4. **L'evoluzione.** Il dataset è uno snapshot. Non c'è serie storica, quindi non
   si può dire se Mediglia sta perdendo dotazione o se è sempre stata così. Se un
   comune è ultimo oggi, non sappiamo da quanto.
5. **Il punto su cui chiedere conto.** Che un comune come Mediglia abbia 0,37
   documenti per abitante con 47mila euro di spesa annua è un fatto del dataset.
   Se sia una scelta o un disinteresse è una domanda politica, e questa inchiesta
   non la può rispondere: risponde su quanto, non sul perché.

## Cosa servirebbe per chiudere le lacune

- I bilanci di spesa dei comuni, per confrontare la spesa dichiarata con quella
  effettivamente sostenuta
- Le delibere di istituzione e i regolamenti di accesso, per verificare i
  orari dichiarati (che sono 46-48 settimane l'anno, mai 52)
- Una serie storica, almeno biennale, per stabilire la dinamica

## Fonti

1. **Biblioteche comunali** — Città metropolitana di Milano, dataset
   `ex8z-wf22`, `https://www.dati.lombardia.it/resource/ex8z-wf22.csv` —
   consultato il 1 ottobre 2026. 215 righe, 187 sedi distinte.
2. **Anagrafe Biblioteche Comunali Lombarde** — Regione Lombardia, dataset
   `7x6q-jhbd`, `https://www.dati.lombardia.it/resource/7x6q-jhbd.csv` —
   consultato il 1 ottobre 2026. 1.308 righe.
3. **Popolazione residente al 31.12.2022** — Città metropolitana di Milano,
   dataset `u9gu-9wf3`,
   `https://www.dati.lombardia.it/resource/u9gu-9wf3.csv` — consultato il
   1 ottobre 2026. 133 righe.

## Avvertenze sull'uso dei dati

1. **215 righe non sono 215 biblioteche**: sono 187 sedi. Le righe multiple
   differiscono solo sugli orari di apertura.
2. **Il personale è per comune, non per sede.** Nei comuni con più sedi tutte
   riportano lo stesso valore.
3. **`numero_visite_annuali` non è un dato mancante ma un campo compilato a
   spot**: 199 valori zero su 214 righe compilate, i 15 valori non nulli su 8
   comuni, nessuno nell'area. Non usabile per confrontare.
4. **`personale_ruolo = 0`** significa assenza di dipendenti in ruolo, non
   assenza di personale: 26 sedi su 215 hanno personale non di ruolo retribuito.
5. **`spese_personale = 0`** non significa zero spesa (caso di Dresano).
6. La normalizzazione usa la popolazione al **31 dicembre 2022**.
7. Gli orari dichiarati coprono 46-48 settimane l'anno, non 52: le chiusure
   estive non sono distinte.
8. Il campo `codice_comune` del dataset popolazione non è il codice ISTAT ma un
   progressivo interno: il join è sul nome normalizzato.

## Riproducibilità

- `raw/biblioteche_cm_milano.csv`, `raw/anagrafe_biblioteche.csv`,
  `raw/popolazione_2022.csv`
- `script/elabora.py` — raggruppamento sedi, aggregazione, graduatoria CM
- `script/grafici.py` — i quattro grafici
- `elaborati/biblioteche_14_comuni.csv`, `elaborati/graduatoria_cm_biblioteche.csv`,
  `elaborati/log_elaborazione.txt`