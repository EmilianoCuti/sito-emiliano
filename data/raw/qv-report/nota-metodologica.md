# Nota metodologica — Indice di qualità della vita nei 14 comuni del Sudmilano

Data di chiusura: 5 novembre 2026. Tutti i calcoli sono riproducibili con gli script nella cartella `script\`.

## 1. Perché un indice nostro

Nessuna delle classifiche nazionali sulla qualità della vita scende al livello del singolo comune non capoluogo: Il Sole 24 Ore e ItaliaOggi misurano le 107 province, Legambiente i 106 capoluoghi, l'ISTAT misura il BES a scala provinciale. L'unico indice composito comunale disponibile, quello di vulnerabilità sociale e materiale dell'ISTAT, si basa sul censimento 2011. Per confrontare i 14 comuni del Sudmilano è quindi necessario costruire un indice, dichiarando fonti, indicatori e pesi.

## 2. Universo e popolazione

14 comuni della provincia di Milano: Carpiano, Cerro al Lambro, Colturano, Dresano, Mediglia, Melegnano, Pantigliate, Paullo, Peschiera Borromeo, San Donato Milanese, San Giuliano Milanese, San Zenone al Lambro, Tribiano, Vizzolo Predabissi.

Popolazione al 1° gennaio 2026: 171.095 abitanti (somma dei 14 comuni, fonte ISTAT POSAS 2026). Superficie 163 km². Densità 1.050 abitanti/km².

## 3. Indicatori, fonti e orientamento

| Dimensione | Indicatore | Fonte | Anno | Verso |
|---|---|---|---|---|
| Reddito | Reddito complessivo medio per contribuente | MEF, dichiarazioni IRPEF | 2024 | + |
| Reddito | Quota contribuenti con reddito complessivo oltre 55.000 euro | MEF | 2024 | + |
| Reddito | Crescita del reddito complessivo medio | MEF | 2010-2024 | + |
| Demografia | Indice di vecchiaia (over 65 ogni 100 under 15) | ISTAT POSAS | 2026 | − |
| Demografia | Quota residenti 0-14 anni | ISTAT POSAS | 2026 | + |
| Servizi e cultura | Prestiti bibliotecari locali per abitante | Anagrafe biblioteche (ICCU) | 2025 | + |
| Servizi e cultura | Iscritti in biblioteca sul totale dei residenti | Anagrafe biblioteche | 2025 | + |
| Ambiente | Suolo consumato sul territorio comunale | ISPRA | 2025 | − |
| Ambiente | Suolo consumato per abitante | ISPRA / ISTAT | 2025 | − |
| Sicurezza stradale | Incidenti stradali per 1.000 abitanti | ISTAT, rilevazione incidentalità | media 2022-2024 | − |
| Sicurezza stradale | Feriti per 1.000 abitanti | ISTAT | media 2022-2024 | − |

Verso "+" significa che un valore alto è considerato positivo; "−" che un valore alto è considerato negativo e viene quindi invertito prima del calcolo.

## 4. Metodo

1. Per ogni indicatore si calcola lo **z-score** rispetto alla media dei 14 comuni: z = (x − media) / deviazione standard (deviazione standard di popolazione). Unità di misura diverse diventano così comparabili.
2. Gli z-score degli indicatori con verso "−" vengono moltiplicati per −1.
3. Il punteggio di dimensione è la **media semplice** degli z-score orientati della dimensione.
4. L'**indice** è la media ponderata delle cinque dimensioni: Reddito 30%, Servizi e cultura 20%, Ambiente 20%, Sicurezza stradale 15%, Demografia 15%.
5. La somma degli z-score dei 14 comuni è zero per costruzione: l'indice misura una posizione relativa all'interno dell'area, non un livello assoluto.

## 5. Verifica di robustezza

| Prova | Correlazione di rango con la classifica principale |
|---|---|
| Tutti gli 11 indicatori a peso uguale | 0,93 |
| Esclusa la dimensione Reddito | 0,74 |
| Esclusa la dimensione Servizi e cultura | 0,68 |
| Esclusa la dimensione Ambiente | 0,86 |
| Esclusa la dimensione Sicurezza | 0,84 |
| Esclusa la dimensione Demografia | 0,83 |
| Pesi alternativi (Demografia 30%, Reddito 20%) | 0,84 |

La testa (Colturano, Dresano, Peschiera Borromeo) e la coda (Cerro al Lambro, Vizzolo Predabissi) restano stabili in tutte le prove. Il centro della classifica cambia: posizioni dal quarto al dodicesimo sono intercambiabili entro l'errore.

## 6. Controlli automatici eseguiti

- Somma delle popolazioni comunali = 171.095 (confronto con la somma del file POSAS 2026).
- Somma dei prestiti bibliotecari 2025 = 96.306.
- Somma degli incidenti 2024 = 470, con 4 morti e 644 feriti (coerente con il dossier sull'incidentalità dell'area).
- Quota over 55.000 euro dell'area calcolata ponderando per contribuenti = 10,0%.
- Doppia lettura del reddito (complesso e imponibile): le due graduatorie interne coincidono.
- Conteggio righe delle tabelle del report: 14 comuni in ciascuna tabella.

## 7. Limiti dichiarati

- **Numerosità**: 14 unità e popolazioni da 2.000 abitanti rendono fragili i tassi (un incidente in più sposta la posizione).
- **Buchi**: reati per comune non disponibili in open data; nessuna centralina PM10 nei 14 comuni; quotazioni immobiliari OMI non acquisite; nessun indicatore sanitario comunale; tempi di percorrenza non misurati.
- **Stima demografica**: POSAS 2026 è una stima, non un dato anagrafico.
- **Pesi**: la classifica dipende dai pesi dichiarati al punto 4; chi non dichiara i pesi rende la classifica non verificabile.
