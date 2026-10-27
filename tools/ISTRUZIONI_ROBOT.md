# Istruzioni per il robot che aggiunge motori

Ogni esecuzione aggiunge **20 motori verificati** a `_data/motori.yml`, presi dall'inizio di `tools/coda.txt`.
**Questo robot scrive solo l'italiano**: le traduzioni EN/FR/CS le fa un robot separato (`tools/ISTRUZIONI_TRADUZIONI.md`).
Non aspettare le traduzioni e non bloccare la pubblicazione per mancanza di traduzioni. Non aggiungere `traduzioni_obbligatorie`.
L'obiettivo finale è coprire tutte le famiglie di motori d'automobile prodotte dal 1980 a oggi, di ogni costruttore.

## Procedura

1. Leggi `tools/coda.txt`. Prendi le prime righe non commentate.
   - Salta (e cancella dalla coda) le righe che indicano "saltare", che riguardano motori solo da competizione o elettrici,
     o che corrispondono a un motore già presente in `_data/motori.yml` (confronta nome, codice e alias, non solo lo slug).
   - Continua finché hai 20 motori validi o la coda è vuota.
2. Per ogni motore fai ricerche sul web (fonti preferite: costruttore e cartelle stampa, Wikipedia in inglese e tedesco,
   riviste tecniche). Verifica almeno: anni di produzione, cilindrata, alesaggio e corsa, compressione, potenze e coppie
   delle versioni principali, auto che lo montano. **Se un dato non è confermabile, non inserirlo**: ometti la riga o la
   versione, oppure scrivi un valore prudente nel testo. Mai inventare.
3. Scrivi la voce in coda a `_data/motori.yml` seguendo esattamente lo schema delle voci esistenti (guarda ad esempio
   `ferrari-f154` e `bmw-s58`). Tutti i campi elencati in `tools/valida.py` sono obbligatori. `limitatore` e `affidabilita` si omettono se non esistono prove sufficienti: mai inventare un regime di taglio o un indice di affidabilità.
   - `fine:` vuoto se il motore è ancora in produzione (verifica sul web).
   - `angolo:` obbligatorio per architetture V e W (gradi tra le bancate).
   - `architettura:` deve essere uno degli `id` di `_data/architetture.yml`. Se serve un'architettura nuova
     (es. "Boxer 12", "W12", "V16"), aggiungila a quel file con nome e testo tecnico di due frasi, più `nome_en`, `testo_en`, `nome_fr`, `testo_fr`, `nome_cs`, `testo_cs`.
   - Lo `slug` è minuscolo con trattini: costruttore-codice (es. `bmw-n55`).
   - Ogni testo in un elenco che contiene "due punti seguiti da spazio" va tra virgolette doppie.
   - In `modelli` ogni riga contiene **una sola marca** e inizia con il nome della marca (es. "Porsche Cayenne V6"):
     così la scheda segnala automaticamente le auto di altre marche. Se il motore equipaggia auto di marche diverse
     dal costruttore, elencale sempre in righe separate.
3a. **Affidabilità.** Se supportata da difetti documentati, la voce può avere il campo `affidabilita` (il limitatore resta facoltativo):
     ```
       affidabilita:
         indice: 72
         motivo: "Una frase sul difetto principale che determina il punteggio."
         provvisorio: true   # solo se il motore ha meno di 5 anni o è prodotto in pochissimi esemplari
     ```
   L'indice si assegna con i criteri della tabella in `metodo.md` (sezione "Indice di affidabilità"), basandosi solo su
   difetti documentati (richiami, bollettini tecnici, fonti specializzate): 90–100 nessun difetto strutturale ricorrente;
   75–89 solo difetti minori; 60–74 un difetto noto costoso ma prevenibile; 40–59 difetti ricorrenti che danneggiano il
   motore; 0–39 difetti di progetto diffusi con rotture gravi. Confronta il valore con motori simili già presenti
   per mantenere la scala coerente.
3b. **Foto (facoltativa, di norma da saltare).** Le foto le cerca il flusso automatico `foto.yml`. Solo se ne hai già una verificata, puoi indicare da Wikimedia Commons una foto che mostri **il motore stesso** (non l'auto intera), di quella famiglia.
   - Accetta solo licenze libere: CC0, pubblico dominio, CC BY, CC BY-SA. Leggi la licenza e l'autore sulla pagina del file.
   - Se non trovi una foto adatta e verificata, non aggiungere il campo: le schede funzionano anche senza.
   - Usa la miniatura a 800 px di larghezza (URL `https://upload.wikimedia.org/wikipedia/commons/thumb/.../800px-...`)
     e controlla che l'indirizzo risponda.
   - Formato:
     ```
       foto:
         url: "https://upload.wikimedia.org/wikipedia/commons/thumb/x/xy/Nome.jpg/800px-Nome.jpg"
         pagina: "https://commons.wikimedia.org/wiki/File:Nome.jpg"
         autore: "Nome dell'autore come indicato su Commons"
         licenza: "CC BY-SA 4.0"
         descrizione: "Toyota 2JZ-GTE nel vano della Supra A80"
     ```
     Il campo va subito dopo `limitatore:`.
4. Lancia `python3 tools/genera_pagine.py` e poi `python3 tools/valida.py`. Correggi finché la validazione passa.
5. Controlla i template: `pip install python-liquid pyyaml markdown --break-system-packages -q` e
   `python3 tools/anteprima.py` deve terminare senza errori. Poi cancella la cartella `_anteprima/`.
6. Cancella da `tools/coda.txt` le righe elaborate (aggiunte o saltate).
   **Se la coda scende sotto le 100 righe, allungala**: scegli i costruttori meno rappresentati in `_data/motori.yml`
   (contali), cerca sul web l'elenco delle loro famiglie di motori prodotte dal 1980 a oggi (pagine "List of ... engines"
   di Wikipedia e simili) e aggiungi in fondo alla coda almeno 150 righe nuove, nel formato `nome | indicazioni`.
   Una riga = una famiglia di motore con scheda propria; raggruppa le varianti minime nella stessa riga.
   Niente doppioni con `_data/motori.yml` o con righe già in coda; niente motori solo da competizione o elettrici.
   Includi anche costruttori europei minori, asiatici (Hyundai, Kia, case cinesi e indiane con motori propri) e americani.
7. L'utente ha autorizzato gli aggiornamenti automatici sul ramo `main` (25 ottobre 2026). Esegui il commit solo dopo verifica delle fonti e della validazione. Commit con messaggio "Aggiunti motori: <nomi>" e push sul ramo `main`.

## Stile dei testi

- Italiano, registro **tecnico**: dati costruttivi, soluzioni tecniche, date, risultati sportivi documentati.
- Niente aggettivi enfatici, soprannomi, frasi da rivista, giudizi estetici sul suono, aneddoti da film.
  Da evitare: "leggenda", "icona", "mitico", "cuore", "canto del cigno", "inconfondibile", "il migliore di sempre".
- `storia`: 3–4 frasi, cosa ha di tecnicamente particolare e dove è stato usato.
- `in_breve`: 3 dati chiave verificati, `valore` corto (numero, sigla o parola) e `testo` di una riga.
- `punti_deboli`: difetti documentati e ricorrenti, con il componente coinvolto.
- `limiti`: soglie di potenza indicative con il componente critico.
- `curiosita`: 1–2 fatti tecnici o storici verificabili.
- Unità: CV (PS), Nm, cc, mm, giri/min. Decimali con la virgola nei testi.

## Se qualcosa va storto

Se la validazione o l'anteprima non passano dopo i tentativi di correzione, non fare push: annulla le modifiche
e lascia la coda invariata.


## Traduzioni

Non tradurre in questa esecuzione. Le pagine EN/FR/CS dei motori nuovi mostrano il testo italiano con un avviso
finché il robot delle traduzioni non le completa.

## Foto

Non cercare foto: le aggiunge automaticamente il flusso GitHub `foto.yml` (Wikimedia Commons) in `_data/foto.yml`.

## Efficienza

- Lavora a blocchi di 5 motori: scrivi, `genera_pagine.py`, `valida.py`, commit e push. Così il lavoro fatto non va perso
  se l'esecuzione si interrompe.
- Due o tre ricerche mirate per motore sono di norma sufficienti (Wikipedia EN/DE e una fonte tecnica). Non aprire decine di pagine.
