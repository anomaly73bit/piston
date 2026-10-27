# Istruzioni per il robot delle traduzioni (EN, FR, CS)

Ogni esecuzione traduce **20 motori** in inglese, francese e ceco. L'italiano in `_data/motori.yml` è il testo di
riferimento e non va modificato.

## Procedura

1. `python3 tools/traduci.py --mancanti 20` elenca i prossimi motori senza traduzione valida.
2. Per ciascuno: `python3 tools/traduci.py --modello <slug>` stampa i testi italiani da tradurre e il loro `_source_hash`.
3. Scrivi `_data/traduzioni/manuali/<slug>.json` in questa forma (vedi `toyota-2jz-gte.json` come esempio):
   ```
   {"_source_hash": "<hash del modello>", "en": {...}, "fr": {...}, "cs": {...}}
   ```
   Ogni lingua ha **esattamente gli stessi campi e lo stesso numero di elementi** del blocco `it` del modello,
   nello stesso ordine.
4. Ogni 5 motori: `python3 tools/traduci.py`, `python3 tools/valida.py`, poi commit e push su `main`
   con messaggio "Traduzioni EN FR CS: <slug>, ...". Alla fine esegui anche `python3 tools/anteprima.py`.

## Regole di traduzione

- Traduci tu il testo, frase per frase, come un redattore tecnico madrelingua. Non usare traduttori automatici.
- Numeri, unità, codici motore, sigle (VTEC, VANOS, IMS, EGR...), nomi di modelli e anni restano identici.
  Le unità restano CV, Nm, cc, mm; "giri/min" diventa rpm (EN), tr/min (FR), ot/min (CS).
- Decimali: punto in inglese, virgola in francese e ceco.
- Registro tecnico come l'italiano, senza aggiunte, senza enfasi, senza omettere informazioni.
- Terminologia di riferimento:

| Italiano | EN | FR | CS |
|---|---|---|---|
| basamento | cylinder block | bloc-moteur | blok motoru |
| testata | cylinder head | culasse | hlava válců |
| albero motore | crankshaft | vilebrequin | klikový hřídel |
| biella | connecting rod | bielle | ojnice |
| bronzine | bearing shells | coussinets | ložiskové pánve |
| distribuzione (a cinghia / a catena) | timing belt / timing chain drive | distribution par courroie / chaîne | rozvod řemenem / řetězem |
| fasatura variabile | variable valve timing | calage variable | proměnné časování ventilů |
| punterie | tappets / lifters | poussoirs | zdvihátka |
| guide valvole | valve guides | guides de soupapes | vodítka ventilů |
| canne | cylinder liners / bores | chemises / fûts | vložky válců |
| sovralimentazione | forced induction / boost | suralimentation | přeplňování |
| aspirato | naturally aspirated | atmosphérique | atmosférický |
| iniezione diretta / indiretta | direct / port injection | injection directe / indirecte | přímé / nepřímé vstřikování |
| limitatore | rev limiter | rupteur | omezovač otáček |
| superquadro / sottoquadro | oversquare / undersquare | supercarré / longue course | krátkozdvihový / dlouhozdvihový |
| Benzina / Gasolio | Petrol / Diesel | Essence / Gazole | Benzín / Nafta |
| Ghisa / Alluminio | Cast iron / Aluminium | Fonte / Aluminium | Litina / Hliník |
| motore interferente | interference engine | moteur à interférence | motor s kolizí ventilů a pístů |

## Se qualcosa va storto

Se `valida.py` non passa, correggi il file della traduzione; non toccare `_data/motori.yml`.
Se l'italiano di un motore cambia, il suo `_source_hash` non coincide più: rigenera il modello e aggiorna la traduzione.
