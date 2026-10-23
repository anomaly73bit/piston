// Filtri e ordinamento del catalogo: lavora sulle righe già presenti nella pagina.
(function () {
  var righe = Array.prototype.slice.call(document.querySelectorAll('#righe .voce'));
  var lista = document.getElementById('righe');
  var conteggio = document.getElementById('conteggio');
  var vuoto = document.getElementById('vuoto');
  var campi = {
    testo: document.getElementById('f-testo'),
    costruttore: document.getElementById('f-costruttore'),
    architettura: document.getElementById('f-architettura'),
    alimentazione: document.getElementById('f-alimentazione'),
    aspirazione: document.getElementById('f-aspirazione'),
    decennio: document.getElementById('f-decennio'),
    produzione: document.getElementById('f-produzione')
  };
  var ordine = { chiave: 'inizio', verso: 1 };

  // "Benzina / Ibrido" -> ["benzina", "ibrido"]
  function parti(valore) {
    return valore.toLowerCase().split('/').map(function (s) { return s.trim(); });
  }

  function corrisponde(r) {
    var d = r.dataset;
    var q = campi.testo.value.trim().toLowerCase();
    if (q && q.split(/\s+/).some(function (p) { return d.testo.indexOf(p) === -1; })) return false;
    if (campi.costruttore.value && d.costruttore !== campi.costruttore.value) return false;
    if (campi.architettura.value && d.architettura !== campi.architettura.value) return false;
    if (campi.alimentazione.value && parti(d.alimentazione).indexOf(campi.alimentazione.value.toLowerCase()) === -1) return false;
    if (campi.aspirazione.value) {
      var asp = parti(d.aspirazione), scelto = campi.aspirazione.value.toLowerCase();
      if (scelto === 'biturbo' && asp.indexOf('quadriturbo') !== -1) asp.push('biturbo');
      if (asp.indexOf(scelto) === -1) return false;
    }
    if (campi.decennio.value) {
      var dec = Math.floor(Number(d.inizio) / 10) * 10;
      if (String(dec) !== campi.decennio.value) return false;
    }
    if (campi.produzione.checked && d.produzione !== '1') return false;
    return true;
  }

  // Spiega perché un motore compare quando la ricerca trova solo un'auto che lo monta.
  function motivo(r, q) {
    var nota = r.querySelector('.voce-montato');
    if (!nota) return;
    var parole = q ? q.split(/\s+/) : [];
    var proprio = parole.length && parole.every(function (p) { return r.dataset.proprio.indexOf(p) !== -1; });
    if (!parole.length || proprio) { nota.hidden = true; return; }
    var auto = r.dataset.modelli.split('|').filter(function (m) {
      var t = m.toLowerCase();
      return parole.some(function (p) { return t.indexOf(p) !== -1; });
    });
    nota.textContent = auto.length ? 'Montato su: ' + auto.join(', ') : '';
    nota.hidden = !auto.length;
  }

  function aggiorna() {
    var visibili = 0;
    var q = campi.testo.value.trim().toLowerCase();
    righe.forEach(function (r) {
      var ok = corrisponde(r);
      r.hidden = !ok;
      if (ok) { visibili++; motivo(r, q); }
    });
    // In ricerca, i motori che corrispondono per nome o costruttore vanno prima di quelli trovati tramite un'auto.
    if (q) {
      var parole = q.split(/\s+/);
      var primi = righe.filter(function (r) { return parole.every(function (p) { return r.dataset.proprio.indexOf(p) !== -1; }); });
      var altri = righe.filter(function (r) { return primi.indexOf(r) === -1; });
      primi.concat(altri).forEach(function (r) { lista.appendChild(r); });
    } else {
      righe.forEach(function (r) { lista.appendChild(r); });
    }
    conteggio.textContent = visibili === 1 ? '1 motore' : visibili + ' motori';
    vuoto.hidden = visibili !== 0;
    salvaURL();
  }

  function ordina() {
    var k = ordine.chiave;
    righe.sort(function (a, b) {
      var x = a.dataset[k], y = b.dataset[k];
      if (k !== 'nome') { x = Number(x); y = Number(y); }
      return (x > y ? 1 : x < y ? -1 : 0) * ordine.verso;
    });
    righe.forEach(function (r) { lista.appendChild(r); });
    document.querySelectorAll('[data-ordina]').forEach(function (b) {
      b.setAttribute('aria-pressed', b.dataset.ordina === k ? 'true' : 'false');
      b.dataset.verso = b.dataset.ordina === k ? (ordine.verso === 1 ? 'su' : 'giu') : '';
    });
  }

  // I filtri restano nell'indirizzo, così una ricerca si può condividere.
  function salvaURL() {
    var p = new URLSearchParams();
    Object.keys(campi).forEach(function (k) {
      var c = campi[k];
      if (c.type === 'checkbox') { if (c.checked) p.set(k, '1'); }
      else if (c.value) p.set(k, c.value);
    });
    var s = p.toString();
    history.replaceState(null, '', s ? '?' + s : location.pathname);
  }

  function leggiURL() {
    var p = new URLSearchParams(location.search);
    Object.keys(campi).forEach(function (k) {
      if (!p.has(k)) return;
      var c = campi[k];
      if (c.type === 'checkbox') c.checked = true; else c.value = p.get(k);
    });
  }

  document.querySelectorAll('[data-ordina]').forEach(function (b) {
    b.addEventListener('click', function () {
      if (ordine.chiave === b.dataset.ordina) ordine.verso *= -1;
      else { ordine.chiave = b.dataset.ordina; ordine.verso = b.dataset.ordina === 'nome' ? 1 : (b.dataset.ordina === 'inizio' ? 1 : -1); }
      ordina();
    });
  });
  Object.keys(campi).forEach(function (k) {
    campi[k].addEventListener(k === 'testo' ? 'input' : 'change', aggiorna);
  });

  leggiURL();
  ordina();
  aggiorna();
})();
