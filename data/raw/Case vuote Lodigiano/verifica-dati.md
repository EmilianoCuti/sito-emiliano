# VERIFICA — Case vuote nel Lodigiano (26 novembre 2026)

## Errori corretti
1. **Popolazione raddoppiata** (critico). Le colonne popolazione_2019 e popolazione_2026 sono il doppio del reale (probabile somma della riga «Totale» POSAS insieme a maschi e femmine). Riscontro: Lodi 91.286 nel dataset contro 45.643 ISTAT al 1/1/2026; provincia 462.962 contro circa 231.000 (ISTAT 2025: 230.447). Corretti: popolazione 2019 e 2026, abitanti_per_abitazione_occupata (Lodi da 4,37 a 2,19, ora coerente con persone_per_abitazione 2,16), una_casa_vuota_ogni_X_abitanti (Lodi da 22,3 a 11,1). Le variazioni percentuali di popolazione non cambiano (+2,0%). Il report HTML e il vecchio articolo contengono ancora i valori errati (anche «462.962 residenti» e la tabella).
2. **Comuni sotto il 10%**: dossier e nota metodologica dicono 18, il dataset ne dà 7 (8 con Massalengo a 10,1%). Il valore corretto è 7.
3. **Benchmark di anni diversi**: Lodi 2023 confrontata con Italia e Lombardia 2021. Verificati: Italia 27,2% (ISTAT, 9.581.772 su 35.271.829); Lombardia 21,2% (78,8% occupate). Per il 2023 la Lombardia è intorno al 20% (Il Giorno, 11/3/2026, su dati ISTAT). Il confronto omogeneo è Lodi 2021: 18,5%.
4. Titolo «senza residenti stabili» e «case vuote»: il dato include le occupate solo da non residenti. Usare «non occupate da residenti».
5. Brembio: 20,0 abitanti per casa vuota, non 20,1 (arrotondamento).

## Da riconciliare (non risolvibile con i file ricevuti)
- **Base 2019**: il dossier indica 121.775 abitazioni totali nel 2019 (18,92%). Ma le percentuali comunali 2019 del dataset implicano circa 118.500 abitazioni, cioè circa 19,4%. Serve riscaricare NUM_DW_AV 2019 dal dataflow DF_DCSS_ABITAZIONI_TV_1. Finché non è chiarito, nel testo compaiono solo i valori assoluti 2019.
- Calo provinciale: −10,4% di non occupate in Lodi contro circa −2,8% in Lombardia (1.198.870 → 1.165.630). Differenza molto ampia: verificare l'effetto delle nuove procedure di collegamento ISTAT.
- Non verificati in modo indipendente: Milano 12,4%, Sudmilano 9,3% (media semplice o ponderata?), massimo Sudmilano 15,5%, epoca di costruzione (32,6% 1961-1980; pre-1918 24,2%), densità 4,9% contro 1,9%, 2.148 sezioni, valori OMI.

## Controlli superati
Totali 119.383 / 98.738 / 20.645; occupate+non occupate = totale in tutti i 60 comuni; percentuali, variazioni, coabitanti e famiglie ricalcolati senza scarti; nessun duplicato; 9 comuni sopra 25%.
