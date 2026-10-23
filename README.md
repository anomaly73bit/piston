# Piston

Enciclopedia dei motori d'automobile dal 1980 a oggi, costruita con Jekyll e pronta per GitHub Pages.

Ogni scheda motore contiene: scheda tecnica, disegno del cilindro in scala (alesaggio × corsa), limitatore,
versioni con potenza e coppia, auto che lo montano, storia, punti deboli, limiti di elaborazione e curiosità.
Il catalogo ha ricerca e filtri (costruttore, architettura, alimentazione, aspirazione, decennio), e ci sono pagine
per costruttori, architetture, cronologia, confronto fino a tre motori e glossario.

## Struttura

```
_data/motori.yml        tutti i dati dei motori (unica fonte)
_data/architetture.yml  testi delle architetture
_data/glossario.yml     voci del glossario
_motori/                una pagina per motore (generata, solo front matter)
_layouts/motore.html    template della scheda
_includes/cilindro.html disegno SVG del cilindro in scala
assets/                 CSS, JS (catalogo, confronto), motori.json per il confronto
tools/genera_pagine.py  crea/aggiorna le pagine in _motori/ dai dati
tools/anteprima.py      anteprima senza Ruby (solo per controllo)
```

## Aggiungere un motore

1. Copia una voce in `_data/motori.yml` e cambia i valori. Lo `slug` deve essere unico.
   Se un testo in un elenco contiene "due punti seguiti da spazio", mettilo tra virgolette.
2. Lancia `python3 tools/genera_pagine.py` (serve `pip install pyyaml`).
3. Pubblica: GitHub Pages ricostruisce il sito da solo.

## Pubblicare su GitHub Pages

1. Crea il repository `piston` su GitHub e carica questi file.
2. In *Settings > Pages* scegli *Deploy from a branch*, ramo `main`, cartella `/ (root)`.
3. Il sito sarà su `https://anomaly73bit.github.io/piston/`.
   Per un dominio tuo: imposta `baseurl: ""` e `url` in `_config.yml` e aggiungi il file `CNAME`.

## In locale

```
bundle install
bundle exec jekyll serve
```

Senza Ruby: `pip install python-liquid pyyaml markdown && python3 tools/anteprima.py`, poi apri `_anteprima/index.html`
con un piccolo server (`python3 -m http.server -d _anteprima`).

## Nota sui dati

I valori sono compilati da fonti pubbliche e vanno verificati sulla documentazione del costruttore prima di usi tecnici.
