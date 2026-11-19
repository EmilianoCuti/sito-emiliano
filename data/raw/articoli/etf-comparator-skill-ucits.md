# ETF Comparator, la skill che confronta i veri pari di un ETF UCITS: prova reale e dove acquistarla

<style>
.articolo-testo figure.grafico{margin:2.4rem 0;padding:1.4rem 1.5rem 1.2rem;border:1px solid rgba(23,20,15,.18);background:#f1ebdd}
.articolo-testo figure.grafico .gt{font-family:var(--sans);font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:#a23a24;font-weight:700;margin:0 0 1rem}
.articolo-testo figure.grafico svg{width:100%;height:auto;display:block}
.articolo-testo figure.grafico svg text{font-family:var(--sans)}
.articolo-testo figure.grafico figcaption{font-family:var(--sans);font-size:.82rem;line-height:1.55;color:#6d6457;margin-top:1rem}
</style>

Confrontare due ETF scelti a priori è facile. Rispondere alla domanda vera — tra i fondi che seguono davvero lo stesso indice, quale si adatta a questo investitore, e che cosa ancora non so? — richiede di risolvere il prodotto, costruire il gruppo dei pari e dichiarare i dati mancanti. ETF Comparator è la skill per agenti AI che ho costruito per fare questo: parte da un nome, un ticker, un simbolo TradingView o un ISIN e restituisce una classifica pesata sul profilo dell'investitore, con l'elenco di ciò che non è stato verificato. La versione 1.0.0 è in vendita su Agensi, il marketplace di skill per agenti, a 1 dollaro.

Qui la descrivo per come è fatta nel codice, la eseguo davvero su un prodotto reale e dichiaro i limiti. Nessuna promessa di rendimento: il punteggio misura l'adattamento a un profilo, non la qualità di un investimento.

## Dalla sigla al prodotto: sei passaggi

La skill non chiede di sapere già quali fondi confrontare. Chiede un prodotto, come lo si conosce: `VWCE`, `IE00BK5BQT80`, «iShares Core MSCI World UCITS ETF». Da lì la pipeline copre sei stadi: definizione del profilo, risoluzione del prodotto, ricerca dei pari, raccolta dei dati, punteggio relativo al gruppo, scelta con elenco dei campi non verificati. L'implementazione di riferimento del punteggio è un tool HTML incluso nel pacchetto (`assets/etf-comparator.html`); gli script Python ne riproducono fedelmente l'algoritmo.

<figure class="grafico">
<p class="gt">La pipeline, dallo stadio 0 allo stadio 5</p>
<svg viewBox="0 0 720 200" role="img" aria-label="Pipeline in sei stadi: profilo, risoluzione, pari, dati, punteggio, scelta. Ogni esclusione e ogni campo mancante restano dichiarati nel report.">
<rect x="20" y="40" width="104" height="80" fill="#f7f3ea" stroke="#17140f" stroke-width="1.2"/>
<text x="72" y="66" text-anchor="middle" font-size="13" font-weight="700" fill="#17140f">S0 Profilo</text>
<text x="72" y="86" text-anchor="middle" font-size="10.5" fill="#6d6457">orizzonte, rischio,</text>
<text x="72" y="102" text-anchor="middle" font-size="10.5" fill="#6d6457">fiscalità</text>
<rect x="136" y="40" width="104" height="80" fill="#f7f3ea" stroke="#17140f" stroke-width="1.2"/>
<text x="188" y="66" text-anchor="middle" font-size="13" font-weight="700" fill="#17140f">S1 Risoluzione</text>
<text x="188" y="86" text-anchor="middle" font-size="10.5" fill="#6d6457">nome, ticker, ISIN</text>
<text x="188" y="102" text-anchor="middle" font-size="10.5" fill="#6d6457">→ prodotto esatto</text>
<rect x="252" y="40" width="104" height="80" fill="#f7f3ea" stroke="#17140f" stroke-width="1.2"/>
<text x="304" y="66" text-anchor="middle" font-size="13" font-weight="700" fill="#17140f">S2 Pari</text>
<text x="304" y="86" text-anchor="middle" font-size="10.5" fill="#6d6457">stesso indice,</text>
<text x="304" y="102" text-anchor="middle" font-size="10.5" fill="#6d6457">stessa versione</text>
<rect x="368" y="40" width="104" height="80" fill="#f7f3ea" stroke="#17140f" stroke-width="1.2"/>
<text x="420" y="66" text-anchor="middle" font-size="13" font-weight="700" fill="#17140f">S3 Dati</text>
<text x="420" y="86" text-anchor="middle" font-size="10.5" fill="#6d6457">27 campi da</text>
<text x="420" y="102" text-anchor="middle" font-size="10.5" fill="#6d6457">4 fonti pubbliche</text>
<rect x="484" y="40" width="104" height="80" fill="#f7f3ea" stroke="#17140f" stroke-width="1.2"/>
<text x="536" y="66" text-anchor="middle" font-size="13" font-weight="700" fill="#17140f">S4 Punteggio</text>
<text x="536" y="86" text-anchor="middle" font-size="10.5" fill="#6d6457">0-100 relativo</text>
<text x="536" y="102" text-anchor="middle" font-size="10.5" fill="#6d6457">al gruppo, pesato</text>
<rect x="600" y="40" width="104" height="80" fill="#a23a24" stroke="#a23a24" stroke-width="1.2"/>
<text x="652" y="66" text-anchor="middle" font-size="13" font-weight="700" fill="#f7f3ea">S5 Scelta</text>
<text x="652" y="86" text-anchor="middle" font-size="10.5" fill="#f7f3ea">miglior adattamento</text>
<text x="652" y="102" text-anchor="middle" font-size="10.5" fill="#f7f3ea">+ campi non verificati</text>
<path d="M124,80 L134,80 M130,76 L134,80 L130,84" stroke="#6d6457" stroke-width="1.4" fill="none"/>
<path d="M240,80 L250,80 M246,76 L250,80 L246,84" stroke="#6d6457" stroke-width="1.4" fill="none"/>
<path d="M356,80 L366,80 M362,76 L366,80 L362,84" stroke="#6d6457" stroke-width="1.4" fill="none"/>
<path d="M472,80 L482,80 M478,76 L482,80 L478,84" stroke="#6d6457" stroke-width="1.4" fill="none"/>
<path d="M588,80 L598,80 M594,76 L598,80 L594,84" stroke="#6d6457" stroke-width="1.4" fill="none"/>
<text x="20" y="160" font-size="12.5" fill="#6d6457">Ogni esclusione dal gruppo e ogni campo mancante restano stampati nel report:</text>
<text x="20" y="178" font-size="12.5" fill="#6d6457">il risultato dice anche che cosa non sa, non solo chi vince.</text>
</svg>
<figcaption>I sei stadi della skill, come dichiarati in SKILL.md (pacchetto 1.0.0). Il punteggio è normalizzato tra minimo e massimo del gruppo dei pari: cambiare gruppo cambia il vincitore.</figcaption>
</figure>

## Il gruppo di pari è il punto

Un confronto vale quanto il gruppo su cui è calcolato. La skill ammette come pari solo prodotti UCITS che seguono lo stesso benchmark nella stessa versione del prodotto inserito, e applica il filtro due volte: in ricerca e come verifica prima del punteggio. Ogni esclusione è stampata con il suo motivo.

- Versioni con copertura valutaria (hedged), ESG/SRI/climate, small/mid/mega cap, equal weight, settoriali, smart beta, leveraged/inverse, swap-based, religious e target-maturity: fuori, perché cambiano esposizione o composizione.
- Sottoinsiemi geografici (ex-US, ex-EMU, ex-UK, ex-Japan): fuori. Un FTSE All-World ex-US non entra nel confronto di un All-World pieno: seguirebbe circa il 60% dell'indice e vincerebbe ogni criterio di copertura.
- Seconde classi di azioni dello stesso fondo: fuori. IWDA e IWDD su Borsa Italiana sono lo stesso fondo: valori identici, nessuna informazione.
- Un pari per provider: lo stesso fondo su due piazze non è due pari.
- Con meno di due prodotti che portano dati, il confronto non parte: senza termine di paragone la normalizzazione non ha senso.

La regola che cambia l'esito è esplicita: il benchmark segue il prodotto inserito. Inserisci un ex-US e confronti solo ex-US; il Full World resta fuori, e viceversa. Non è una penalità: sono indici diversi.

## Ventisette campi, quattro fonti

I parametri del modello sono 27, descritti campo per campo con fonte e criterio di verifica in `references/fields-and-sources.md`. Le fonti sono quattro, in ordine di affidabilità per questo campione:

- **albertored/etfdb**: dataset pubblico di 4.566 ETF europei (indice, TER, domicilio, replica, prestito titoli, classe, numero di holdings, AUM, pesi paese e settore, top 10). Fonte primaria, statica su GitHub, senza login né rate limit. Non è ridistribuita con la skill: si scarica a runtime dal repository originale, che non dichiara licenza.
- **yfinance**: conferma e fallback. Da solo non basta: non espone i TER Vanguard (`netExpenseRatio` e `fund_operations` restano vuoti) e non risolve nomi completi o simboli TradingView.
- **ucitscompass.com**: dati da prospetto (domicilio, replica, classe, dimensione, benchmark, inception); è l'unica fonte che espone i TER Vanguard. Lettura a ritmo umano, senza crawling massivo.
- **Financial Modeling Prep**: holdings e composizione geografica. Verificato il 4 ottobre 2026: gli endpoint `etf/*` sono premium e con un piano standard rispondono «Restricted Endpoint». Il modulo resta inerte e non blocca mai il confronto; si attiva da solo se il piano li include.

I campi che nessuna fonte pubblica restano vuoti ed esclusi dal punteggio: mai stimati. Un `0/100` può significare «nessun dato», non «prodotto peggiore», e il report lo dice.

## Prova reale: MSCI World, profilo aggressivo

Ho eseguito la skill il 19 novembre 2026 sul prodotto di partenza IE00B4L5Y983 (iShares Core MSCI World UCITS ETF USD Acc), profilo aggressivo: orizzonte 20 anni, fiscalità italiana, piano di accumulo sì, liquidità bassa, concentrazione media. L'interprete non aveva `tradingview-scraper`: la risoluzione è passata quindi dalla via ISIN tramite yfinance, come dichiarato dalla skill; con la dipendenza installata si parte anche da nome o ticker. Undici candidati, uno escluso dal filtro sul benchmark con motivo stampato; Financial Modeling Prep inerte con il piano disponibile. Dieci pari ammessi su MSCI World; somma dei pesi del profilo 116, concentrata su due criteri (30 e 23).

<figure class="grafico">
<p class="gt">Dieci pari MSCI World, profilo aggressivo — esecuzione del 19 novembre 2026</p>
<svg viewBox="0 0 720 440" role="img" aria-label="Classifica osservata: XDWD 73, ESAN 70, MWDD 70, UBU7 64, FINZ 61, 0SWU 60, H4ZY 51, iShares Core 28, ELFW 15, LYYA 13. Le barre tratteggiate hanno tredici campi non verificati esclusi dal punteggio.">
<text x="112" y="52" text-anchor="end" font-size="13" fill="#17140f">XDWD</text>
<rect x="120" y="36" width="365" height="22" fill="#a23a24"/>
<text x="493" y="52" font-size="14" font-weight="700" fill="#a23a24">73</text>
<text x="112" y="88" text-anchor="end" font-size="13" fill="#17140f">ESAN</text>
<rect x="120" y="72" width="350" height="22" fill="#17140f"/>
<text x="478" y="88" font-size="14" font-weight="700" fill="#17140f">70</text>
<text x="112" y="124" text-anchor="end" font-size="13" fill="#17140f">MWDD</text>
<rect x="120" y="108" width="350" height="22" fill="#17140f"/>
<text x="478" y="124" font-size="14" font-weight="700" fill="#17140f">70</text>
<text x="112" y="160" text-anchor="end" font-size="13" fill="#17140f">UBU7</text>
<rect x="120" y="144" width="320" height="22" fill="#17140f"/>
<text x="448" y="160" font-size="14" font-weight="700" fill="#17140f">64</text>
<text x="112" y="196" text-anchor="end" font-size="13" fill="#17140f">FINZ</text>
<rect x="120" y="180" width="305" height="22" fill="#6d6457" stroke="#17140f" stroke-width="1.2" stroke-dasharray="5 4"/>
<text x="433" y="196" font-size="14" font-weight="700" fill="#17140f">61</text>
<text x="112" y="232" text-anchor="end" font-size="13" fill="#17140f">0SWU</text>
<rect x="120" y="216" width="300" height="22" fill="#17140f"/>
<text x="428" y="232" font-size="14" font-weight="700" fill="#17140f">60</text>
<text x="112" y="268" text-anchor="end" font-size="13" fill="#17140f">H4ZY</text>
<rect x="120" y="252" width="255" height="22" fill="#17140f"/>
<text x="383" y="268" font-size="14" font-weight="700" fill="#17140f">51</text>
<text x="112" y="304" text-anchor="end" font-size="13" fill="#17140f">iShares Core*</text>
<rect x="120" y="288" width="140" height="22" fill="#6d6457" stroke="#17140f" stroke-width="1.2" stroke-dasharray="5 4"/>
<text x="268" y="304" font-size="14" font-weight="700" fill="#17140f">28</text>
<text x="112" y="340" text-anchor="end" font-size="13" fill="#17140f">ELFW</text>
<rect x="120" y="324" width="75" height="22" fill="#6d6457" stroke="#17140f" stroke-width="1.2" stroke-dasharray="5 4"/>
<text x="203" y="340" font-size="14" font-weight="700" fill="#17140f">15</text>
<text x="112" y="376" text-anchor="end" font-size="13" fill="#17140f">LYYA</text>
<rect x="120" y="360" width="65" height="22" fill="#6d6457" stroke="#17140f" stroke-width="1.2" stroke-dasharray="5 4"/>
<text x="193" y="376" font-size="14" font-weight="700" fill="#17140f">13</text>
<rect x="20" y="402" width="14" height="12" fill="#a23a24"/>
<text x="40" y="412" font-size="12" fill="#6d6457">miglior adattamento al profilo</text>
<rect x="250" y="402" width="14" height="12" fill="#17140f"/>
<text x="270" y="412" font-size="12" fill="#6d6457">87/116 pesi con dati verificati</text>
<rect x="470" y="402" width="14" height="12" fill="#6d6457" stroke="#17140f" stroke-width="1.2" stroke-dasharray="5 4"/>
<text x="490" y="412" font-size="12" fill="#6d6457">64/116: 13 campi mancanti, esclusi</text>
<text x="20" y="432" font-size="12" fill="#6d6457">* prodotto di partenza: tra i campi mancanti c'è la ritenuta fiscale (rit), che il modello pesa per un residente italiano.</text>
</svg>
<figcaption>Punteggi osservati nell'esecuzione reale del 19 novembre 2026 (profilo aggressivo, dieci pari MSCI World). Il punteggio è relativo al gruppo e ai dati del momento: non misura qualità assoluta né rendimenti passati. Le barre tratteggiate hanno copertura parziale: il loro punteggio nasce da meno criteri pesati.</figcaption>
</figure>

Il migliore adattamento per il profilo è XDWD (Xtrackers MSCI World UCITS ETF 1C), 73/100. Il prodotto di partenza, iShares Core, arriva ottavo a 28/100: non perché il modello lo giudichi peggiore in assoluto, ma perché su di esso tredici campi non sono verificati dalle fonti — tra cui la ritenuta fiscale — e quindi esclusi dal punteggio (64/116 pesi disponibili contro 87/116 dei sei pari con copertura piena). È esattamente il caveat che la skill dichiara: senza dati il confronto non premia né punisce, semplicemente non valuta quel criterio. Chi legge il report deve completare quei campi dal KID o dal prospetto del provider prima di decidere.

Anche la scheda Agensi mostra un'esecuzione dimostrativa (cinque pari MSCI World, punteggi da 88 a 62, iShares primo). La mia esecuzione reale, con dieci pari e dati del 19 novembre, produce una classifica diversa: il punteggio è relativo al gruppo e alle fonti del momento, e le due esecuzioni non sono confrontabili tra loro. La dimostrativa resta un esempio della scheda, non una quotazione.

## Che cosa non fa

- **Nessun dato di performance.** Confronta struttura, costo e fiscalità, non i rendimenti passati: non sono un criterio del modello.
- **Nessun numero inventato.** Un campo che nessuna fonte fornisce resta vuoto ed escluso, mai stimato: una stima sposterebbe il punteggio e produrrebbe un falso vincitore.
- **Solo UCITS europei.** Il dataset primario copre quelli; gli ETF quotati negli USA sono fuori perimetro.
- **Fiscalità da residente italiano.** Il campo `rit` assume la ritenuta del 15% sui domicili Irlanda e Lussemburgo secondo le regole italiane; per altre residenze il criterio va ri-parametrato.
- **I pesi sono priorità, non calibrazione finanziaria.** Esprimono che cosa conta per l'investitore; non predicono rendimenti.
- **Nessuna consulenza.** Strumento di analisi: prima di investire ogni valore va verificato su prospetto e KID del provider.
- La ricerca per nome può confondere prodotti simili: la skill ricontrolla su ISIN o token distintivi e avvisa quando non ci riesce.

## Dove trovarlo e acquistarlo

La scheda ufficiale, con prezzo, esempio di esecuzione, requisiti e scansione di sicurezza, è qui: <a href="https://www.agensi.io/skills/etf-comparator" target="_blank" rel="noopener noreferrer">agensi.io/skills/etf-comparator</a>. Il prezzo è **1 dollaro, una tantum**. L'acquisto include il codice Python completo, le configurazioni delle dipendenze e l'accesso ai dataset di peer-discovery integrati nella pipeline; il dataset etfdb, come detto, si scarica a runtime dal repository originale e non è ridistribuito nel pacchetto.

Per installarlo e usarlo con il proprio agente:

1. Collega l'agente al MCP di Agensi: la scheda fornisce un prompt da incollare in Claude, ChatGPT, Cursor o qualunque agente che supporti MCP (in alternativa, setup manuale).
2. Accedi ad Agensi dal link che l'agente mostra e clicca Allow.
3. Chiedi il confronto: l'agente carica la skill e la usa sul task. Prima di acquistare una skill chiede sempre conferma.

In locale, dopo l'acquisto: Python 3.10 o superiore, `pip install -r requirements.txt` (yfinance e tradingview-scraper), poi `python scripts/confronta.py --etf "VWCE" --html comparison.html`. Senza tradingview-scraper la risoluzione passa solo da ISIN, come nella mia prova. Il report HTML espone il dettaglio pesato criterio per criterio e l'elenco dei campi saltati.

Trasparenza, come dichiarata in scheda e nel pacchetto: scansione di sicurezza in 8 punti superata prima della messa in vendita; permessi richiesti terminale/shell, lettura e scrittura file, accesso rete, variabili d'ambiente; host consentiti ucitscompass.com, raw.githubusercontent.com, github.com, financialmodelingprep.com. La licenza è una EULA 1.0.0 (novembre 2026): non esclusiva, non trasferibile. Nessuna affiliazione o sponsorizzazione con provider di ETF o con le fonti dati: i nomi di prodotti e indici sono marchi dei rispettivi proprietari, usati solo per identificazione.

Il conto che la skill permette di fare è quello giusto: non «qual è l'ETF migliore», ma «tra i fondi che seguono davvero questo indice, quale si adatta al mio profilo, e che cosa devo ancora verificare a mano». Il resto — prospetto, KID, decisione — resta di chi investe.

*Fonti: scheda ufficiale Agensi di etf-comparator (https://www.agensi.io/skills/etf-comparator, consultata il 19 novembre 2026; messa in vendita e scansione di sicurezza indicate in scheda come avvenute due giorni prima); pacchetto etf-comparator 1.0.0 (SKILL.md, README.md, LICENSE/EULA, references/fields-and-sources.md); esecuzione reale del 19 novembre 2026, profilo aggressivo, IE00B4L5Y983, report HTML e log conservati; dataset pubblico albertored/etfdb. Punteggi e coperture citati come osservati nell'esecuzione, non come valutazioni assolute.*
