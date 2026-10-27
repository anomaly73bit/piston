// Confronto fino a tre motori, letto da motori.json.
(function () {
  var form = document.getElementById('scelte');
  var out = document.getElementById('confronto');
  var base = form.dataset.base;
  var dati = {};

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function virgola(n) { return String(n).replace('.', ','); }

  // Stessa scala del disegno usato nelle schede (1 unità = 1 mm).
  function cilindro(m) {
    if (m.architettura === 'Rotativo' || !m.alesaggio) {
      return '<svg class="cilindro" viewBox="0 0 170 150" role="img" aria-label="Rotore Wankel"><path class="camicia" d="M75 22c34 0 52 18 52 53s-18 53-52 53-52-18-52-53 18-53 52-53z"/><path class="volume" d="M75 34 Q101 68 111 98 Q75 110 39 98 Q49 68 75 34z"/><circle class="asse" cx="75" cy="78" r="5"/><text x="75" y="146" text-anchor="middle">rotore</text></svg>';
    }
    var a = m.alesaggio, c = m.corsa, x1 = 75 - a / 2, x2 = 75 + a / 2, y2 = 24 + c;
    return '<svg class="cilindro" viewBox="0 0 170 150" role="img" aria-label="Alesaggio ' + a + ' mm, corsa ' + c + ' mm">' +
      '<rect class="volume" x="' + x1 + '" y="24" width="' + a + '" height="' + c + '"/>' +
      '<line class="camicia" x1="' + x1 + '" y1="20" x2="' + x1 + '" y2="' + (y2 + 8) + '"/>' +
      '<line class="camicia" x1="' + x2 + '" y1="20" x2="' + x2 + '" y2="' + (y2 + 8) + '"/>' +
      '<rect class="pistone" x="' + (x1 + 1.5) + '" y="' + (y2 - 10) + '" width="' + (a - 3) + '" height="10"/>' +
      '<line class="quota" x1="' + x1 + '" y1="12" x2="' + x2 + '" y2="12"/>' +
      '<text x="75" y="9" text-anchor="middle">' + virgola(a) + '</text>' +
      '<line class="quota" x1="' + (x2 + 9) + '" y1="24" x2="' + (x2 + 9) + '" y2="' + y2 + '"/>' +
      '<text x="' + (x2 + 12) + '" y="' + (c / 2 + 28) + '">' + virgola(c) + '</text></svg>';
  }

  var T = {"it": {"cilindrata": "Cilindrata", "pmax": "Potenza massima", "pmin": "Potenza minima", "cmax": "Coppia massima", "lim": "Limitatore", "spec": "Potenza specifica", "aff": "Affidabilità", "arch": "Architettura", "asp": "Aspirazione", "alim": "Alimentazione", "comp": "Compressione", "inie": "Iniezione", "blocco": "Materiale basamento", "testa": "Materiale testata", "distr": "Distribuzione", "prod": "Produzione", "giri": "giri/min", "cvl": "CV/litro", "vuoto": "Scegli almeno due motori per vedere il confronto.", "oggi": "oggi", "nd": "n.d.", "errore": "Impossibile caricare i dati dei motori. Ricarica la pagina.", "locale": "it-IT"}, "en": {"cilindrata": "Displacement", "pmax": "Maximum power", "pmin": "Minimum power", "cmax": "Maximum torque", "lim": "Rev limiter", "spec": "Specific output", "aff": "Reliability", "arch": "Layout", "asp": "Induction", "alim": "Fuel", "comp": "Compression", "inie": "Injection", "blocco": "Block material", "testa": "Head material", "distr": "Valvetrain", "prod": "Production", "giri": "rpm", "cvl": "CV/litre", "vuoto": "Choose at least two engines to see the comparison.", "oggi": "present", "nd": "n/a", "errore": "Could not load the engine data. Reload the page.", "locale": "en-GB"}, "fr": {"cilindrata": "Cylindrée", "pmax": "Puissance maximale", "pmin": "Puissance minimale", "cmax": "Couple maximal", "lim": "Rupteur", "spec": "Puissance spécifique", "aff": "Fiabilité", "arch": "Architecture", "asp": "Alimentation en air", "alim": "Carburant", "comp": "Compression", "inie": "Injection", "blocco": "Matériau du bloc", "testa": "Matériau de la culasse", "distr": "Distribution", "prod": "Production", "giri": "tr/min", "cvl": "CV/litre", "vuoto": "Choisissez au moins deux moteurs pour voir la comparaison.", "oggi": "aujourd'hui", "nd": "n.c.", "errore": "Impossible de charger les données des moteurs. Rechargez la page.", "locale": "fr-FR"}, "cs": {"cilindrata": "Zdvihový objem", "pmax": "Nejvyšší výkon", "pmin": "Nejnižší výkon", "cmax": "Nejvyšší točivý moment", "lim": "Omezovač otáček", "spec": "Měrný výkon", "aff": "Spolehlivost", "arch": "Uspořádání", "asp": "Plnění", "alim": "Palivo", "comp": "Komprese", "inie": "Vstřikování", "blocco": "Materiál bloku", "testa": "Materiál hlavy", "distr": "Rozvod", "prod": "Výroba", "giri": "ot/min", "cvl": "CV/litr", "vuoto": "Pro porovnání vyberte alespoň dva motory.", "oggi": "dosud", "nd": "neuvedeno", "errore": "Data motorů se nepodařilo načíst. Obnovte stránku.", "locale": "cs-CZ"}};
  var L = T[form.dataset.lingua] || T.it;
  var metriche = [
    { k: 'cilindrata', t: L.cilindrata, u: 'cc' },
    { k: 'cv_max', t: L.pmax, u: 'CV' },
    { k: 'cv_min', t: L.pmin, u: 'CV' },
    { k: 'nm_max', t: L.cmax, u: 'Nm' },
    { k: 'limitatore', t: L.lim, u: L.giri },
    { k: 'cv_litro', t: L.spec, u: L.cvl },
    { k: 'aff', t: L.aff, u: '/100' }
  ];
  var testi = [
    { k: 'architettura', t: L.arch },
    { k: 'aspirazione', t: L.asp },
    { k: 'alimentazione', t: L.alim },
    { k: 'compressione', t: L.comp },
    { k: 'iniezione', t: L.inie },
    { k: 'blocco', t: L.blocco },
    { k: 'testa', t: L.testa },
    { k: 'distribuzione', t: L.distr },
    { k: 'periodo', t: L.prod }
  ];

  function disegna() {
    var scelti = ['m1', 'm2', 'm3'].map(function (n) { return dati[form.elements[n].value]; }).filter(Boolean);
    var p = new URLSearchParams();
    scelti.forEach(function (m) { p.append('m', m.slug); });
    history.replaceState(null, '', p.toString() ? '?' + p : location.pathname);
    if (scelti.length < 2) { out.innerHTML = '<p class="vuoto">' + L.vuoto + '</p>'; return; }

    scelti.forEach(function (m) {
      m.cv_litro = Math.round(m.cv_max / (m.cilindrata / 1000));
      m.periodo = m.inizio + '–' + (m.fine || L.oggi);
      m.aff = m.affidabilita ? m.affidabilita.indice : 0;
    });
    var col = 'style="--colonne:' + scelti.length + '"';
    var h = '<div class="confronto-teste" ' + col + '>';
    scelti.forEach(function (m) {
      h += '<div><a href="' + base + m.slug + '/"><strong>' + esc(m.nome) + '</strong></a><span>' + esc(m.costruttore) + '</span>' + cilindro(m) + '</div>';
    });
    h += '</div>';
    metriche.forEach(function (x) {
      var max = Math.max.apply(null, scelti.map(function (m) { return m[x.k] || 0; }));
      h += '<div class="confronto-riga" ' + col + '><h3>' + (x.k === 'aff' ? 'Affidabilità (stima editoriale)' : x.t) + '</h3>';
      scelti.forEach(function (m) {
        var v = m[x.k] || 0, pct = max ? (v / max * 100) : 0;
        h += '<div class="barra' + (v === max ? ' prima' : '') + '"><span style="width:' + pct.toFixed(1) + '%"></span><b>' + (v ? v.toLocaleString(L.locale) : L.nd) + ' <small>' + x.u + '</small></b></div>';
      });
      h += '</div>';
    });
    testi.forEach(function (x) {
      h += '<div class="confronto-riga testo" ' + col + '><h3>' + x.t + '</h3>';
      scelti.forEach(function (m) { h += '<p>' + esc(m[x.k] == null ? L.nd : m[x.k]) + '</p>'; });
      h += '</div>';
    });
    out.innerHTML = h;
  }

  fetch(form.dataset.json).then(function (r) { return r.json(); }).then(function (lista) {
    lista.forEach(function (m) { dati[m.slug] = m; });
    var iniziali = new URLSearchParams(location.search).getAll('m');
    iniziali.slice(0, 3).forEach(function (s, i) { if (dati[s]) form.elements['m' + (i + 1)].value = s; });
    form.addEventListener('change', disegna);
    disegna();
  }).catch(function () {
    out.innerHTML = '<p class="vuoto">' + L.errore + '</p>';
  });
})();
