# Emiliano Cuti — archivio di inchieste

Sito statico dell'archivio di inchieste: copertina, archivio filtrabile, quindici
dossier, un atlante incrociato dei quattordici comuni, sette articoli e la pagina
«Chi sono».

## Requisiti

- Python 3.10 o superiore
- Nessun'altra dipendenza: il componente `markdown` è incluso in `vendor/`
  (licenza BSD-3-Clause, vedi `vendor/LICENSE-markdown.md`).

Nessun'altra dipendenza: il sito non usa database, framework, Node o CDN. I caratteri
sono quelli di sistema (Iowan Old Style, Palatino, Georgia), le immagini sono locali.

## Costruire il sito

```bash
python3 build_data.py   # ricalcola content/atlante.json dai dati in data/raw/
python3 build.py        # scrive le 28 pagine in sito/
```

`build.py` accetta `--out` per scrivere altrove:

```bash
python3 build.py --out /tmp/prova
```

Su macOS e Windows ci sono due script di comodo: `aggiorna.command` e `aggiorna.bat`.
Fanno entrambi i passaggi e aprono `sito/index.html`.

## Struttura

```
content/
  site.json          testi generali: autore, copertina, biografia, Atlante, footer
  inchieste.json     15 inchieste + 7 articoli (metadati e testi brevi)
  atlante.json       generato da build_data.py — non modificare a mano
  _copia-originale/  copia di sicurezza dei tre JSON
data/raw/            dataset CSV/JSON e testi integrali degli articoli in Markdown
assets/              CSS, JS, ritratto, logo, favicon
vendor/              markdown incluso (BSD-3-Clause), nessun pip richiesto
build.py             genera tutte le pagine HTML
build_data.py        incrocia i dataset e scrive content/atlante.json
make_logo.py         rigenera il marchio (opzionale, richiede Georgia e fonttools)
sito/                output: il sito pronto da pubblicare
verifica/            schermate dei controlli
LEGGIMI.md           guida non tecnica per Emiliano
aggiorna.command     script di aggiornamento per macOS
aggiorna.bat         script di aggiornamento per Windows
```

## Modello dei contenuti

`content/site.json`

- `autore`: nome, ruolo, mestieri, frase sotto il ritratto, anno.
- `home`: introduzione della copertina.
- `chi_sono`: titolo, paragrafi della biografia, metodo (coppie titolo/descrizione),
  chiusura.
- `atlante`: testi di testa, introduzione, letture (`titolo`, `testo`, `r`), nota finale.
- `articoli`: testi della pagina archivio.
- `footer`: nota e colophon.

`content/inchieste.json`

- `inchieste`: lista di 15 oggetti con `slug`, `titolo`, `occhiello`, `data`, `tema`,
  `territorio`, `sintesi`, `punto`, `numeri` (`v`, `l`, `n`), `metodo`, `fonti`,
  `limiti`, `dati` (`file`, `label`, `nota`), `materiali`, `correlati`.
- `articoli`: lista di 7 oggetti con `slug`, `titolo`, `sommario`, `inchiesta`, `tema`,
  `fonte`, `formato`.

`slug` e `fonte` sono identificatori: non vanno cambiati senza aggiornare i rimandi.
L'ordine della lista `inchieste` è l'ordine cronologico; la copertina mostra le ultime
due.

## Atlante

`build_data.py` legge i dataset in `data/raw/`, calcola 17 indicatori per 14 comuni e
scrive `content/atlante.json`. La lista degli indicatori e le mappature dei file sono
in `build_data.py` (costante `INDICATORI` e funzioni di lettura). Se cambi un dataset,
mantieni le colonne attese o aggiorna la mappatura.

`build.py` genera anche i CSV scaricabili in `sito/assets/dati/` e la legenda delle
colonne. Le celle vuote sono dati mancanti, non zeri.

Nota: la colonna popolazione del dataset «Case vuote» è doppia rispetto al dato ISTAT
(342.190 invece di 171.095). L'Atlante usa la popolazione del dataset Qualità della vita
(171.095, coerente con il report). La discrepanza è documentata in `VERIFICA.md`.

## Ritratto e marchio

- `assets/ritratto.svg` è un segnaposto tipografico con le iniziali E.C.
- Per usare una foto: salva `assets/ritratto.jpg` (verticale, bianco e nero, almeno
  660 × 880) e ricostruisci. `build.py` la copia e la usa al posto dell'SVG.
- `assets/logo.svg` è il marchio «e rovesciata + c»: tracciati vettoriali ricavati da
  Georgia, nessun font richiesto a runtime. `make_logo.py` lo rigenera (opzionale,
  richiede `fonttools` e il font Georgia).
- `assets/favicon.svg` è la versione 64 × 64 per la scheda del browser.

## Stile

`assets/style.css` contiene le variabili in `:root`:

```css
--carta: #f7f3ea;   /* fondo avorio */
--ink: #17140f;     /* inchiostro */
--ink-2: #3a342b;   /* testo secondario */
--rule: #d7cdbc;    /* fili sottili */
--rosso: #a23a24;   /* rosso ossido */
--serif: "Iowan Old Style", Palatino, Georgia, serif;
--sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
```

La griglia della copertina è `minmax(230px, 300px) 1fr`; sotto i 760 px diventa a una
colonna, con il ritratto affiancato alla frase. Le tabelle dell'Atlante scorrono
orizzontalmente su mobile.

## Pubblicazione

Il sito è statico: pubblica il **contenuto** di `sito/` su Netlify, GitHub Pages,
Cloudflare Pages o qualsiasi hosting. Il file `.nojekyll` è incluso per GitHub Pages.
Tutti i percorsi sono relativi, quindi funziona anche in una sottocartella.

## Verifica

`VERIFICA.md` documenta i controlli: 28 pagine, 0 errori di console, 0 link interni
rotti, 0 risorse esterne, 0 overflow orizzontale a 390 px, immagini con `alt`, `lang="it"`.
Le schermate sono in `verifica/`.

Limiti noti: il ritratto è un segnaposto; non c'è un contatto email; la ricerca
dell'archivio lavora sui campi di sintesi, non sul testo integrale dei report; il sito
è testato su Chromium.

## Origine

Sito costruito per Emiliano Cuti. Testi e dati sono suoi; il codice è modificabile
liberamente. La guida non tecnica è in `LEGGIMI.md`.
