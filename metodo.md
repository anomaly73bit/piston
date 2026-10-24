---
layout: default
title: Come sono raccolti i dati
permalink: /metodo/
---
<section class="pagina riga stretta testo-lungo" markdown="1">

# Come sono raccolti i dati

Ogni scheda descrive una **famiglia di motore**, non una singola versione: per esempio l'EA888 Volkswagen raccoglie quattro generazioni e potenze da 160 a oltre 330 CV. Le versioni più significative sono elencate nella tabella dedicata.

## Fonti

I valori sono compilati da documentazione pubblica dei costruttori, cartelle stampa e letteratura tecnica. Potenze e coppie sono indicate in CV (PS) e newton metro come dichiarate per il mercato indicato; tra Giappone, Europa e Stati Uniti possono cambiare.

## Cosa significano i campi

- **Cilindrata, alesaggio e corsa** si riferiscono alla versione principale indicata nel testo della scheda.
- **Potenza** è l'intervallo tra la versione meno e quella più potente della famiglia.
- **Limitatore** è il valore tipico di serie.
- **Limiti ed elaborazioni** raccoglie le soglie comunemente riportate da preparatori e appassionati. Sono indicazioni di massima, non garanzie.

## Indice di affidabilità {#affidabilita}

Il termometro in ogni scheda riporta un **indice da 0 a 100**. Non è una statistica di guasto, che per la maggior parte dei motori non è pubblica: è una valutazione redazionale basata su difetti documentati, richiami, bollettini tecnici e gravità delle conseguenze.

| Indice | Fascia | Criterio |
|---|---|---|
| 90–100 | Ottima | Nessun difetto strutturale ricorrente; percorrenze molto elevate documentate |
| 75–89 | Buona | Solo difetti minori o di accessori, risolvibili con manutenzione ordinaria |
| 60–74 | Discreta | Almeno un difetto noto costoso, prevenibile con interventi preventivi |
| 40–59 | Problematica | Difetti ricorrenti che possono danneggiare il motore anche con manutenzione regolare |
| 0–39 | Critica | Difetti di progetto diffusi con rotture gravi frequenti |

L'indice valuta l'affidabilità del motore di serie, non i costi di manutenzione. Quando i dati di lungo periodo sono scarsi (motori recenti o prodotti in pochi esemplari) la valutazione è indicata come provvisoria.

## Segnalare un errore o aggiungere un motore

Tutti i dati stanno in un unico file, `_data/motori.yml`. Per aggiungere un motore si copia una voce esistente, si cambiano i valori e si lancia `python3 tools/genera_pagine.py`, che crea la pagina della scheda. Il sito si aggiorna da solo alla pubblicazione su GitHub Pages.

</section>
