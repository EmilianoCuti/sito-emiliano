/* Introduzione 3D — canvas 2D con proiezione prospettica manuale.
   Nessuna dipendenza, nessuna GPU richiesta. Rispetta prefers-reduced-motion
   (fallback statico) e si ferma quando la sezione non è visibile o la scheda
   è in background, per non pesare sulla CPU. */
(function () {
  "use strict";
  var canvas = document.querySelector("canvas[data-intro3d]");
  if (!canvas || !canvas.getContext) return;
  var sezione = canvas.closest(".intro3d");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) { if (sezione) sezione.classList.add("intro3d--static"); return; }

  var parole = ["Cronaca", "Finanza", "AI", "Informatica"];
  try { parole = JSON.parse(canvas.getAttribute("data-parole")) || parole; } catch (e) {}

  var ctx = canvas.getContext("2d");
  var W = 0, H = 0, DPR = 1;
  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = Math.max(1, Math.round(W * DPR));
    canvas.height = Math.max(1, Math.round(H * DPR));
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  resize();
  window.addEventListener("resize", resize);

  // Punti su una sfera (griglia lat/lon) + nodi-parola ai vertici di un tetraedro.
  var R = 1;
  var punti = [];
  var LAT = 7, LON = 12;
  for (var i = 1; i < LAT; i++) {
    var phi = Math.PI * i / LAT;
    for (var j = 0; j < LON; j++) {
      var th = 2 * Math.PI * j / LON;
      punti.push([Math.sin(phi) * Math.cos(th), Math.cos(phi), Math.sin(phi) * Math.sin(th)]);
    }
  }
  var tet = [[1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]];
  var nodi = parole.map(function (p, k) {
    var v = tet[k % tet.length];
    var n = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
    return { p: p, v: [v[0] / n * 1.28, v[1] / n * 1.28, v[2] / n * 1.28] };
  });

  var ay = 0, ax = -0.18, mx = 0, my = 0, tmx = 0, tmy = 0;
  if (sezione) {
    sezione.addEventListener("pointermove", function (e) {
      var r = sezione.getBoundingClientRect();
      tmx = ((e.clientX - r.left) / r.width - 0.5) * 0.6;
      tmy = ((e.clientY - r.top) / r.height - 0.5) * 0.4;
    });
    sezione.addEventListener("pointerleave", function () { tmx = 0; tmy = 0; });
  }

  function ruota(v, sy, cy, sx, cx) {
    var x = v[0] * cy + v[2] * sy;
    var z = -v[0] * sy + v[2] * cy;
    var y = v[1] * cx - z * sx;
    z = v[1] * sx + z * cx;
    return [x, y, z];
  }
  function proj(v, scala) {
    var f = 3.2 / (3.2 + v[2]);
    return [W / 2 + v[0] * f * scala, H / 2 + v[1] * f * scala, f];
  }

  var visibile = true, attivo = true;
  if ("IntersectionObserver" in window && sezione) {
    new IntersectionObserver(function (v) { visibile = v[0].isIntersecting; }, { threshold: 0.02 }).observe(sezione);
  }
  document.addEventListener("visibilitychange", function () { attivo = !document.hidden; });

  var ultimo = 0;
  function frame(t) {
    requestAnimationFrame(frame);
    if (!visibile || !attivo) { ultimo = t; return; }
    if (t - ultimo < 33) return; // ~30 fps, basta per una rotazione lenta
    ultimo = t;
    ay += 0.0045;
    mx += (tmx - mx) * 0.05; my += (tmy - my) * 0.05;
    var sy = Math.sin(ay + mx), cy = Math.cos(ay + mx);
    var sx = Math.sin(ax + my), cx = Math.cos(ax + my);
    var scala = Math.min(W, H) * 0.30;
    ctx.clearRect(0, 0, W, H);

    // filamenti della sfera
    var pr = punti.map(function (v) { return proj(ruota(v, sy, cy, sx, cx), scala); });
    ctx.lineWidth = 1;
    for (var a = 0; a < pr.length; a++) {
      for (var b = a + 1; b < pr.length; b++) {
        var dx = punti[a][0] - punti[b][0], dy = punti[a][1] - punti[b][1], dz = punti[a][2] - punti[b][2];
        var d2 = dx * dx + dy * dy + dz * dz;
        if (d2 < 0.16) {
          var al = 0.10 * Math.min(pr[a][2], pr[b][2]);
          ctx.strokeStyle = "rgba(247,243,234," + al.toFixed(3) + ")";
          ctx.beginPath(); ctx.moveTo(pr[a][0], pr[a][1]); ctx.lineTo(pr[b][0], pr[b][1]); ctx.stroke();
        }
      }
    }
    // nodi-parola
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    nodi.forEach(function (n, k) {
      var p = proj(ruota(n.v, sy, cy, sx, cx), scala);
      var dim = Math.max(13, 26 * p[2]);
      var op = Math.max(0.35, Math.min(1, p[2]));
      ctx.font = "600 " + dim.toFixed(1) + "px Georgia, 'Times New Roman', serif";
      ctx.fillStyle = k === 0 ? "rgba(226,120,90," + op.toFixed(3) + ")" : "rgba(247,243,234," + op.toFixed(3) + ")";
      ctx.fillText(n.p, p[0], p[1]);
    });
  }
  requestAnimationFrame(frame);
})();