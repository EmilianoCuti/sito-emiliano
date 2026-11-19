# Emiliano Cuti — archivio di inchieste

## Guida alla cartella

Questa cartella contiene **tutto il sito**: i testi, i dati, le immagini, lo stile e il
programma che costruisce le pagine. È autonoma: non dipende da AutoClaw, da Luca o da un
server. Puoi copiarla su un altro computer e funziona lo stesso.

Il sito è **statico**: non ha database, non ha cookie, non ha pubblicità. Per pubblicarlo
basta copiare la cartella `sito/` su un hosting.

---

## In 30 secondi

1. **Vedere il sito**: apri `sito/index.html` con un doppio clic.
2. **Modificare i testi**: apri `content/site.json` o `content/inchieste.json` con un
   editor di testo.
3. **Ricostruire**: doppio clic su `aggiorna.command` (Mac) o `aggiorna.bat` (Windows).
4. **Pubblicare**: trascina la cartella `sito/` su <https://app.netlify.com/drop>.

---

## 1. Com'è fatta la cartella

| File o cartella | Cosa contiene | Si modifica? |
|---|---|---|
| `content/site.json` | Nome, ruolo, frase sotto il ritratto, biografia, testi della copertina, letture dell'Atlante, piè di pagina | **Sì** |
| `content/inchieste.json` | Le 15 inchieste e i 7 articoli: titoli, sintesi, numeri, metodo, fonti, limiti | **Sì** |
| `content/atlante.json` | I 17 indicatori incrociati per i 14 comuni | **No**: si rigenera |
| `content/_copia-originale/` | Copia di sicurezza dei tre file qui sopra | No |
| `data/raw/` | Dataset CSV/JSON e testi integrali degli articoli in Markdown | Sì, con cautela |
| `assets/style.css` | Colori, caratteri, spazi, impaginazione | **Sì** |
| `assets/app.js` | Ricerca, filtri, ordinamento dell'Atlante | Solo se sai cosa fai |
| `assets/ritratto.svg` | Segnaposto del ritratto con le iniziali E.C. | Si sostituisce con una foto |
| `assets/ritratto.jpg` | (Da aggiungere) foto vera, verticale, in bianco e nero | **Sì** |
| `assets/logo.svg` | Marchio «e rovesciata + c» | Sì, se hai un SVG |
| `assets/favicon.svg` | Icona nella scheda del browser | Sì, se hai un SVG |
| `build.py` | Costruisce tutte le pagine HTML | Solo se sai cosa fai |
| `build_data.py` | Ricalcola l'Atlante dai dataset | Solo se cambi i dati |
| `make_logo.py` | Rigenera il marchio dai contorni di Georgia | Non serve: il logo è già pronto |
| `vendor/` | Il componente `markdown` che impagina gli articoli, già incluso | No |
| `aggiorna.command` | Ricostruisce il sito su Mac | No |
| `aggiorna.bat` | Ricostruisce il sito su Windows | No |
| `sito/` | Il sito già costruito, pronto da aprire e pubblicare | **No**: viene rigenerato |
| `verifica/` | Schermate e prove dei controlli | No |
| `LEGGIMI.md` | Questa guida | No |
| `README.md` | Note tecniche per chi mette mano al codice | No |
| `VERIFICA.md` | Cosa è stato controllato e cosa resta da fare | No |

Il sito ha **28 pagine**: copertina, archivio delle inchieste, 15 dossier, Atlante,
archivio degli articoli, 7 articoli, «Chi sono» e la pagina 404.

---

## 2. Vedere il sito

Apri `sito/index.html` con un doppio clic. È la copia già costruita: si vede tutto.
Se modifichi i testi, devi ricostruire (punto 4) per vedere le modifiche.

Il sito funziona anche da `file://` perché usa solo percorsi relativi e non carica
nulla da Internet.

---

## 3. Modificare i testi

### 3.1 Regole del JSON

I file `.json` sono testo semplice. Valgono tre regole:

- Le parole stanno fra **virgolette doppie**: `"come questa"`.
- Fra un campo e l'altro c'è una **virgola**, ma **non** dopo l'ultimo.
- Le liste stanno fra parentesi quadre `[ ... ]`; gli oggetti fra graffe `{ ... }`.

Usa un editor di testo che salvi in formato semplice: VS Code, Sublime Text, TextEdit
(Impostazioni > Formato > Testo semplice). **Non usare Word.**

Prima di una modifica importante, copia il file: se qualcosa si rompe, ripristini la
copia. In `content/_copia-originale/` c'è già la versione iniziale.

### 3.2 Testi generali — `content/site.json`

| Campo | Cosa cambia |
|---|---|
| `autore.nome` | Il nome nel titolo, nel piè di pagina e nelle schede |
| `autore.ruolo` | La riga rossa sotto il nome («Giornalista») |
| `autore.mestieri` | La riga «Cronaca locale, comunicazione istituzionale» |
| `autore.frase` | La frase sotto il ritratto: «Scrivo ciò che gli altri ignorano…» |
| `autore.anno` | L'anno nel piè di pagina |
| `home.introduzione` | Il paragrafo introduttivo della copertina |
| `chi_sono.paragrafi` | **La biografia completa**, un paragrafo per elemento della lista |
| `chi_sono.metodo` | Le voci di «Come lavoro»: `t` = titolo, `d` = descrizione |
| `chi_sono.chiusura` | La frase finale della pagina «Chi sono» |
| `atlante.titolo`, `occhiello`, `sommario` | I testi di testa dell'Atlante |
| `atlante.introduzione` | I paragrafi introduttivi dell'Atlante |
| `atlante.letture` | Le tre letture: `titolo`, `testo`, `r` (es. «r = 0,63 · n = 14») |
| `atlante.nota_finale` | La nota in fondo all'Atlante |
| `articoli.titolo`, `sommario`, `nota_racconti` | I testi della pagina «Articoli e racconti» |
| `footer.nota`, `colophon` | Le due righe del piè di pagina |

Per cambiare la biografia, modifica **`chi_sono.paragrafi`**: è una lista, un elemento
per ogni paragrafo. Non serve toccare altro.

### 3.3 Inchieste e articoli — `content/inchieste.json`

Il file ha due liste: `inchieste` (15) e `articoli` (7).

Ogni **inchiesta** ha questi campi:

| Campo | Cosa è |
|---|---|
| `slug` | L'indirizzo della pagina. **Non cambiarlo**: rompe i link |
| `titolo` | Il titolo del dossier |
| `occhiello` | La categoria sopra il titolo |
| `data` | La data, in formato `2026-09-03` |
| `tema` | Il tema per i filtri dell'archivio (es. «Mobilità») |
| `territorio` | I comuni o l'area dell'inchiesta |
| `sintesi` | Il paragrafo di presentazione |
| `punto` | La frase o le frasi del «punto» principale (lista) |
| `numeri` | I numeri chiave: `v` = valore, `l` = etichetta, `n` = nota |
| `metodo` | Come è stata fatta l'inchiesta (lista di frasi) |
| `fonti` | Le fonti (lista) |
| `limiti` | Cosa non è stato possibile sapere (lista) |
| `dati` | Il dataset scaricabile: `file`, `label`, `nota` |
| `materiali` | I materiali allegati (lista) |
| `correlati` | Gli `slug` delle inchieste collegate (lista) |

Ogni **articolo** ha: `slug`, `titolo`, `sommario`, `inchiesta` (lo slug del dossier
collegato), `tema`, `fonte` (il file Markdown del testo integrale) e `formato`.

**Non cambiare `slug` né `fonte`**: sono indirizzi e percorsi. Se aggiungi un'inchiesta,
scegli uno `slug` nuovo, tutto minuscolo, con i trattini al posto degli spazi.

### 3.4 Testi integrali degli articoli — `data/raw/`

I testi completi dei 7 articoli sono file `.md` (Markdown) dentro `data/raw/`, nelle
cartelle delle rispettive inchieste. Il percorso è indicato nel campo `fonte` di ogni
articolo.

Il Markdown è semplice:

```markdown
## Un titolo di sezione

Un paragrafo. Le righe vuote separano i paragrafi.

**Grassetto**, *corsivo*, [un link](https://esempio.it).
```

Dopo aver modificato un `.md`, ricostruisci il sito.

### 3.5 Aggiungere o togliere un'inchiesta

- **Aggiungere**: copia un oggetto esistente in `content/inchieste.json`, incollalo dopo
  la virgola, cambia `slug` e i testi. La pagina, la voce in archivio e i rimandi si
  creano da soli.
- **Togliere**: cancella l'oggetto (e la virgola che lo separa). Controlla che nessun
  altro dossier lo citi in `correlati`.
- La copertina mostra le **ultime due** inchieste: l'ordine è quello della lista.

---

## 4. Ricostruire il sito

Dopo aver modificato i testi, il sito va ricostruito. Non basta salvare: le pagine
HTML sono generate dai file JSON.

### Mac

Doppio clic su **`aggiorna.command`**. Se macOS lo blocca: tasto destro > **Apri**, oppure
apri il Terminale e scrivi:

```bash
bash aggiorna.command
```

### Windows

Doppio clic su **`aggiorna.bat`**.

### Cosa fa

1. Controlla che ci sia Python 3.10 o superiore (se manca o è troppo vecchio,
   chiede di installarlo da <https://www.python.org/downloads/>).
2. Ricalcola l'Atlante dai dati (`build_data.py`).
3. Costruisce le 28 pagine (`build.py`) nella cartella `sito/`.
4. Apre `sito/index.html`.

Non serve connessione a Internet: il componente che impagina gli articoli
(`markdown`) è già incluso nella cartella `vendor/`.

### A mano

```bash
python3 build_data.py
python3 build.py
```

L'uscita è sempre `sito/`. Per scrivere altrove: `python3 build.py --out /tmp/prova`.

Se il sito non cambia, controlla di aver salvato il file e di aver ricostruito. Se
compare un errore, leggi il numero di riga: quasi sempre è una virgola o una virgoletta
nel JSON.

---

## 5. Cambiare la foto

1. Salva una foto **verticale**, in **bianco e nero**, come `assets/ritratto.jpg`
   (meglio se almeno 660 × 880 pixel).
2. Ricostruisci.

`build.py` usa automaticamente `ritratto.jpg` al posto del segnaposto `ritratto.svg`.
Per tornare al segnaposto, cancella `assets/ritratto.jpg` e ricostruisci.

La foto è mostrata in bianco e nero anche se il file è a colori: è una scelta dello
stile del sito.

---

## 6. Cambiare logo, colori e caratteri

### Logo

Il marchio è `assets/logo.svg`: una «e» rovesciata a sinistra e una «c» a destra, con
una barra centrale corta. È usato sopra il nome in copertina, nell'intestazione delle
pagine interne e nella favicon (`assets/favicon.svg`).

Per modificarlo basta sostituire i due SVG con altri dello stesso tipo. Per rigenerarlo
dai contorni di Georgia serve `fonttools` e il font Georgia installato:

```bash
python3 -m pip install fonttools
python3 make_logo.py
```

Non è necessario: il logo già pronto funziona.

### Colori e caratteri

Apri `assets/style.css`: in cima c'è il blocco `:root` con le variabili del sito.

```css
:root {
  --carta: #f7f3ea;   /* fondo avorio */
  --ink: #17140f;     /* inchiostro */
  --ink-2: #3a342b;   /* testo secondario */
  --rule: #d7cdbc;    /* fili sottili */
  --rosso: #a23a24;   /* rosso ossido: numeri di sezione e link */
  --serif: "Iowan Old Style", Palatino, Georgia, serif;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}
```

Cambia i **valori**, non i nomi delle classi. Per esempio, un rosso più scuro:
`--rosso: #7d2b1b;`. Poi ricostruisci.

---

## 7. Pubblicare

Il sito è statico: la cartella `sito/` è tutto ciò che serve. Non servono database,
PHP, Node o un server applicativo.

### Netlify Drop (il più semplice)

1. Vai su <https://app.netlify.com/drop>.
2. Trascina la cartella **`sito/`** (non la cartella intera del progetto).
3. Ottieni un indirizzo pubblico. Crea un account gratuito per conservarlo.
4. Per il dominio: **Domain management** > **Add a domain**.

### GitHub Pages

1. Crea un repository su GitHub.
2. Carica il **contenuto** di `sito/` (non la cartella `sito/` stessa).
3. **Settings** > **Pages** > **Deploy from a branch** > `main` / root.
4. Il file `.nojekyll` è già incluso: serve a GitHub per servire tutti i file.

### Cloudflare Pages

1. **Create a project** > **Direct upload**.
2. Carica la cartella `sito/`.

### Altri hosting

Copia il contenuto di `sito/` via FTP nella cartella pubblica del tuo hosting. I percorsi
sono tutti relativi: funziona anche in una sottocartella.

---

## 8. Cosa non toccare

- **`slug`** e **`fonte`**: sono indirizzi e percorsi. Se li cambi, i link si rompono.
- **`content/atlante.json`**: è generato da `build_data.py`. Modifica i dati in
  `data/raw/`, non il file generato.
- **`sito/`**: è il risultato della costruzione. Se lo modifichi a mano, la prossima
  ricostruzione cancella le modifiche.
- **`build.py`** e **`build_data.py`**: sono il motore. Vanno bene se sai programmare;
  altrimenti chiedi a Luca.
- **`content/_copia-originale/`**: è la copia di sicurezza. Non modificarla.

---

## 9. Se qualcosa si rompe

- **Il JSON non si carica**: il messaggio dice la riga. Quasi sempre manca una virgola,
  c'è una virgola di troppo o una virgoletta non chiusa. Confronta con
  `content/_copia-originale/`.
- **Il sito non cambia**: hai salvato? Hai ricostruito? Guarda la data dei file in
  `sito/`.
- **La pagina è bianca**: apri la console del browser (F12) e leggi l'errore; spesso è
  un percorso sbagliato in un `href` o `src`.
- **Hai rovinato un file**: copia il file da `content/_copia-originale/` e ricostruisci.
- **Prima di modifiche grosse**: copia tutta la cartella con un altro nome, per esempio
  `sito-emiliano-2026-11-18/`.

Il sito già costruito in `sito/` continua a funzionare anche se i sorgenti sono rotti.

---

## 10. Dati, Atlante e verifica

- L'Atlante incrocia **17 indicatori** da **12 inchieste** per **14 comuni**. Ogni
  colonna dichiara fonte e inchiesta; le celle vuote sono dati mancanti, non zeri.
- I dataset scaricabili sono in `sito/assets/dati/`; i sorgenti in `data/raw/`.
- La popolazione usata è ISTAT 2026: **171.095 abitanti** sui 14 comuni. La colonna
  popolazione del dataset «Case vuote» è doppia e **non** viene usata.
- `VERIFICA.md` elenca i controlli fatti (28 pagine, 0 link rotti, 0 risorse esterne,
  0 overflow a 390 px) e i limiti noti.
- `verifica/` contiene le schermate di collaudo.

---

## 11. Contatti

Per assistenza tecnica: **Luca**.

I testi e i dati sono di Emiliano Cuti. Il codice si può modificare liberamente.
