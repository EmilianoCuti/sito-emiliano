/* Archivio di inchieste — comportamenti progressivi.
   Senza JavaScript la pagina resta leggibile: elenco completo, tabella completa. */
(function () {
  "use strict";

  var riduciMovimento = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var normalizza = function (testo) {
    return (testo || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  };

  /* ---------------------------------------------------------------- archivio */
  var archivio = document.querySelector("[data-archivio]");
  if (archivio) {
    var righe = Array.prototype.slice.call(archivio.querySelectorAll("[data-riga]"));
    var campo = document.querySelector("[data-cerca-inchieste]");
    var chips = Array.prototype.slice.call(document.querySelectorAll("[data-tema]"));
    var conteggio = document.querySelector("[data-conteggio]");
    var vuoto = document.querySelector("[data-vuoto]");
    var reset = document.querySelector("[data-azzera]");
    var temaAttivo = "tutti";
    var termine = "";
    var unita = archivio.getAttribute("data-unita") || "inchieste";
    var unitaSingolare = archivio.getAttribute("data-unita-singolare") || "inchiesta";

    var applica = function () {
      var visibili = 0;
      righe.forEach(function (riga) {
        var temi = riga.getAttribute("data-temi") || "";
        var testo = normalizza(riga.getAttribute("data-cerca"));
        var passaTema = temaAttivo === "tutti" || temi.split("|").indexOf(temaAttivo) !== -1;
        var passaTesto = termine === "" || testo.indexOf(termine) !== -1;
        var mostra = passaTema && passaTesto;
        riga.hidden = !mostra;
        if (mostra) visibili += 1;
      });
      if (conteggio) {
        conteggio.textContent = visibili === 1 ? "1 " + unitaSingolare : visibili + " " + unita;
      }
      if (vuoto) vuoto.hidden = visibili !== 0;
      archivio.hidden = visibili === 0;
    };

    if (campo) {
      var timer = null;
      campo.addEventListener("input", function () {
        window.clearTimeout(timer);
        timer = window.setTimeout(function () {
          termine = normalizza(campo.value.trim());
          applica();
        }, riduciMovimento ? 0 : 110);
      });
    }

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        temaAttivo = chip.getAttribute("data-tema");
        chips.forEach(function (altro) {
          altro.setAttribute("aria-pressed", altro === chip ? "true" : "false");
        });
        applica();
      });
    });

    if (reset) {
      reset.addEventListener("click", function () {
        temaAttivo = "tutti";
        termine = "";
        if (campo) campo.value = "";
        chips.forEach(function (chip) {
          chip.setAttribute("aria-pressed", chip.getAttribute("data-tema") === "tutti" ? "true" : "false");
        });
        applica();
        if (campo) campo.focus();
      });
    }

    applica();
  }

  /* ----------------------------------------------------------------- atlante */
  var datiAtlante = document.getElementById("atlante-dati");
  var tabella = document.querySelector("table[data-atlante]");
  if (datiAtlante && tabella) {
    var dati = JSON.parse(datiAtlante.textContent);
    var corpo = tabella.tBodies[0];
    var righeAtlante = Array.prototype.slice.call(corpo.rows);
    var intestazioni = Array.prototype.slice.call(tabella.tHead.rows[0].cells);
    var scheda = document.querySelector("[data-scheda-comune]");
    var schedaTitolo = scheda ? scheda.querySelector("[data-scheda-titolo]") : null;
    var schedaCorpo = scheda ? scheda.querySelector("[data-scheda-corpo]") : null;
    var schedaCorrelati = scheda ? scheda.querySelector("[data-scheda-correlati]") : null;
    var chiudi = scheda ? scheda.querySelector("[data-chiudi-scheda]") : null;
    var campoAtlante = document.querySelector("[data-cerca-comune]");
    var bottoneTutti = document.querySelector("[data-mostra-tutti]");

    var formatta = function (valore, formato) {
      if (valore === null || valore === undefined || valore === "") return "—";
      var n = Number(valore);
      if (!isFinite(n)) return String(valore);
      if (formato === "int") {
        return new Intl.NumberFormat("it-IT", { maximumFractionDigits: 0 }).format(n);
      }
      if (formato === "dec1") {
        return new Intl.NumberFormat("it-IT", { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(n);
      }
      if (formato === "dec2") {
        return new Intl.NumberFormat("it-IT", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);
      }
      return new Intl.NumberFormat("it-IT").format(n);
    };

    var indicePerChiave = {};
    dati.indicatori.forEach(function (ind) { indicePerChiave[ind.id] = ind; });

    var ordine = { chiave: null, verso: 1 };

    var ordina = function (chiave, verso) {
      var numerico = chiave !== "nome";
      righeAtlante.sort(function (a, b) {
        var va = a.getAttribute("data-valore-" + chiave);
        var vb = b.getAttribute("data-valore-" + chiave);
        if (numerico) {
          var na = va === "" ? null : Number(va);
          var nb = vb === "" ? null : Number(vb);
          if (na === null && nb === null) return 0;
          if (na === null) return 1;
          if (nb === null) return -1;
          return (na - nb) * verso;
        }
        return va.localeCompare(vb, "it") * verso;
      });
      righeAtlante.forEach(function (r) { corpo.appendChild(r); });
      intestazioni.forEach(function (th) {
        if (th.getAttribute("data-chiave") === chiave) {
          th.setAttribute("aria-sort", verso === 1 ? "ascending" : "descending");
        } else {
          th.removeAttribute("aria-sort");
        }
      });
    };

    intestazioni.forEach(function (th) {
      var chiave = th.getAttribute("data-chiave");
      if (!chiave) return;
      th.setAttribute("tabindex", "0");
      th.setAttribute("role", "button");
      var attiva = function () {
        var primoVerso = chiave === "nome" ? 1 : -1;
        var verso = ordine.chiave === chiave ? -ordine.verso : primoVerso;
        ordine = { chiave: chiave, verso: verso };
        ordina(chiave, verso);
      };
      th.addEventListener("click", attiva);
      th.addEventListener("keydown", function (evento) {
        if (evento.key === "Enter" || evento.key === " ") {
          evento.preventDefault();
          attiva();
        }
      });
    });

    var filtraRighe = function () {
      var termine = normalizza(campoAtlante ? campoAtlante.value.trim() : "");
      var visibili = 0;
      righeAtlante.forEach(function (riga) {
        var nome = normalizza(riga.getAttribute("data-comune"));
        var mostra = termine === "" || nome.indexOf(termine) !== -1;
        riga.hidden = !mostra;
        if (mostra) visibili += 1;
      });
      var nota = document.querySelector("[data-atlante-conteggio]");
      if (nota) nota.textContent = visibili === 1 ? "1 comune" : visibili + " comuni";
    };

    if (campoAtlante) {
      campoAtlante.addEventListener("input", filtraRighe);
    }

    if (bottoneTutti) {
      bottoneTutti.addEventListener("click", function () {
        var attivo = bottoneTutti.getAttribute("aria-pressed") === "true";
        bottoneTutti.setAttribute("aria-pressed", attivo ? "false" : "true");
        bottoneTutti.textContent = attivo ? "Mostra tutti gli indicatori" : "Mostra solo i principali";
        tabella.classList.toggle("tutti", !attivo);
      });
    }

    var apriScheda = function (nome) {
      if (!scheda) return;
      var comune = dati.comuni.filter(function (c) { return c.nome === nome; })[0];
      if (!comune) return;
      schedaTitolo.textContent = comune.nome;
      schedaCorpo.innerHTML = "";
      dati.indicatori.forEach(function (ind) {
        var valore = comune[ind.id];
        var riga = document.createElement("div");
        riga.className = "scheda-voce";
        var dt = document.createElement("dt");
        dt.innerHTML = ind.label + '<span class="fonte">' + ind.fonte + "</span>";
        var dd = document.createElement("dd");
        dd.textContent = formatta(valore, ind.formato) + (ind.unita && valore !== null && valore !== undefined ? " " + ind.unita : "");
        riga.appendChild(dt);
        riga.appendChild(dd);
        schedaCorpo.appendChild(riga);
      });

      if (schedaCorrelati) {
        var link = [];
        var visti = {};
        dati.indicatori.forEach(function (ind) {
          if (comune[ind.id] === null || comune[ind.id] === undefined) return;
          if (visti[ind.inchiesta]) return;
          visti[ind.inchiesta] = true;
          link.push(ind.inchiesta);
        });
        schedaCorrelati.innerHTML = "";
        var prefisso = schedaCorrelati.getAttribute("data-prefisso") || "";
        link.slice(0, 4).forEach(function (slug, i) {
          if (i > 0) schedaCorrelati.appendChild(document.createTextNode(" · "));
          var a = document.createElement("a");
          a.href = prefisso + "inchieste/" + slug + ".html";
          a.textContent = (dati.titoli && dati.titoli[slug]) || slug.replace(/-/g, " ");
          schedaCorrelati.appendChild(a);
        });
      }

      scheda.hidden = false;
      righeAtlante.forEach(function (r) {
        r.setAttribute("aria-selected", r.getAttribute("data-comune") === nome ? "true" : "false");
      });
      if (window.history && window.history.replaceState) {
        var url = new URL(window.location.href);
        url.searchParams.set("comune", nome);
        window.history.replaceState({}, "", url);
      }
      scheda.scrollIntoView({ behavior: riduciMovimento ? "auto" : "smooth", block: "nearest" });
    };

    var chiudiScheda = function () {
      if (!scheda) return;
      scheda.hidden = true;
      righeAtlante.forEach(function (r) { r.removeAttribute("aria-selected"); });
      if (window.history && window.history.replaceState) {
        var url = new URL(window.location.href);
        url.searchParams.delete("comune");
        window.history.replaceState({}, "", url);
      }
    };

    righeAtlante.forEach(function (riga) {
      riga.addEventListener("click", function () { apriScheda(riga.getAttribute("data-comune")); });
      riga.addEventListener("keydown", function (evento) {
        if (evento.key === "Enter" || evento.key === " ") {
          evento.preventDefault();
          apriScheda(riga.getAttribute("data-comune"));
        }
      });
      riga.setAttribute("tabindex", "0");
      riga.setAttribute("role", "button");
    });

    if (chiudi) chiudi.addEventListener("click", chiudiScheda);

    var iniziale = new URL(window.location.href).searchParams.get("comune");
    if (iniziale) {
      apriScheda(iniziale);
    }

    filtraRighe();
  }
})();
