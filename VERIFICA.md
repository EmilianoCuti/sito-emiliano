# Verifica del sito — 18 novembre 2026

Progetto: sito statico di Emiliano Cuti (cartella `sito/`)
Build: `build.py` (28 pagine) + `build_data.py` (Atlante, 17 indicatori)
Peso del sito: 388 KB, 51 file, nessuna risorsa esterna.

## Controlli automatici

| Controllo | Esito |
|---|---|
| Generazione delle 28 pagine | OK |
| Crawl di tutte le 28 pagine | 0 errori di console, 0 eccezioni JavaScript |
| Link interni (href relativi) | 0 link rotti |
| Richieste verso origini esterne | 0 (nessun CDN, font o immagine remota) |
| Riferimenti `http(s)://` in `src`, `href`, `url()` | 0 |
| Immagini senza `alt` | 0 su 2 |
| `id` duplicati nelle pagine | 0 |
| `lang="it"` su tutte le pagine | sì |
| Overflow orizzontale a 390 px | 0 pagine (articolo lungo incluso) |
| Tabelle larghe su mobile | contenitore con scorrimento, indicatore «Scorri la tabella» |
| Peso massimo di una pagina | 32 KB di HTML (articolo lungo) |
| Marchio `logo.svg` | presente in 28/28 pagine e nella favicon |
| Frase sotto il ritratto | presente in copertina e in «Chi sono» |
| Biografia completa | solo nella pagina «Chi sono», non in copertina |

## Interazioni provate (Chromium, 1440 px e 390 px)

| Azione | Risultato |
|---|---|
| Ricerca «melegnano» nell'archivio | 1 inchiesta, contatore aggiornato |
| Ricerca «zzzzz» | stato vuoto visibile, archivio nascosto, pulsante «Azzera i filtri» |
| Azzeramento filtri | 15 inchieste |
| Filtro tema «Mobilità» | 3 inchieste |
| Atlante, clic su «Case vuote» | ordina in modo decrescente: Colturano (15,5%) |
| Secondo clic sulla stessa colonna | inverte: Cerro al Lambro (5,6%) |
| Ordinamento da tastiera (Invio su intestazione) | funziona, `aria-sort="descending"` |
| Clic sulla riga «Mediglia» | scheda con 17 indicatori, URL `?comune=Mediglia` |
| Apertura diretta `?comune=Paullo` | scheda di Paullo aperta al caricamento |
| Pulsante «Mostra tutti gli indicatori» | 19 colonne visibili |
| Ricerca comune «Mediglia» | 1 comune, contatore aggiornato |

## Controlli sui dati

| Controllo | Esito |
|---|---|
| Popolazione dei 14 comuni | 171.095 (ISTAT 2026) — coincide con il report Qualità della vita |
| Indicatori dell'Atlante | 17, tutti con fonte e inchiesta di origine |
| Colonne senza dato | solo `addizionale_30k` (12/14: mancano Carpiano e Vizzolo, dichiarato) |
| «Case vuote»: colonna popolazione | non usata: nel dataset di origine è doppia (342.190 invece di 171.095) |
| Somma abitazioni 2023 | 81.686, coerente con il dossier |
| Incidenti 2024 (somma CSV) | 470 incidenti, 644 feriti, 4 morti (3 entro 24h + 1 entro 30gg) |
| Correlazioni delle «letture» | calcolate su 14 unità: r = 0,00 · 0,63 · −0,41 |

## Prove visive

Le immagini sono in `verifica/`:

1. `01-copertina-desktop.png` — copertina 1440 px
2. `02-archivio-desktop.png` — archivio con filtri
3. `03-atlante-desktop.png` — atlante, 11 colonne principali
4. `04-dossier-desktop.png` — dossier con numeri, metodo, limiti
5. `05-articolo-desktop.png` — articolo lungo
6. `06-copertina-mobile.png` — copertina 390 px
7. `07-dossier-mobile.png` — dossier 390 px
8. `08-archivio-nessun-risultato.png` — stato vuoto della ricerca
9. `09-atlante-scheda-comune.png` — scheda comune aperta

## Non verificato / limiti noti

- **Ritratto**: `assets/ritratto.svg` è una lastra tipografica con le iniziali, non una foto.
  Va sostituita con `assets/ritratto.jpg` (verticale, bianco e nero) e ricostruita.
- **Contatti**: non c'è un indirizzo email o un modulo, perché non è stato fornito.
- **Ricerca**: lavora sui campi di sintesi dei 15 dossier (titolo, sintesi, tema, territorio,
  numeri), non sul testo integrale dei report.
- **Browser**: testato solo su Chromium 1134 (Playwright). Safari e Firefox non provati.
- **Dati**: fotografia dell'archivio OneDrive al 18 novembre 2026; valgono le avvertenze
  metodologiche di ciascuna inchiesta (in particolare: i valori di Paullo sono stime,
  «casa non occupata» non significa «casa disponibile», i furti sono solo casi pubblici).
- **Deploy**: il sito è statico e si pubblica su qualsiasi hosting (Netlify, GitHub Pages,
  Cloudflare Pages, FTP). La cartella da pubblicare è `sito/`.
