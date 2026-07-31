/**
 * Hero-Interaktivitaet: TERRA COTTA
 *
 * 2.5D-Inszenierung des vorhandenen Keyvisuals (Vase, Schale, Becher).
 * Da nur ein flaches Referenzfoto vorliegt (keine freigestellten
 * Einzelobjekte), arbeitet die Szene bewusst mit zwei Bild-Ebenen
 * (Hintergrund/Hauptplatte) statt einer vorgetaeuschten Objekt-Trennung:
 *  - Intro: sanftes Einschweben der Hauptplatte beim ersten Laden
 *  - Pointer-Parallaxe: Hintergrund und Platte verschieben sich gegenlaeufig
 *  - Scroll-Zoom: leichte Annaeherung waehrend der ersten Scroll-Strecke
 *  - Lichtsweep: rein CSS/JS-basierter "Glasurreflex" ueber der Objektregion
 *
 * Vanilla JS, keine Abhaengigkeiten. Wird automatisch deaktiviert bei
 * `prefers-reduced-motion: reduce` und auf Geraeten ohne feinen Zeiger.
 */
(function () {
  "use strict";

  var hero = document.querySelector("[data-hero]");
  if (!hero) return;

  var bg = hero.querySelector("[data-hero-bg]");
  var plate = hero.querySelector("[data-hero-plate]");
  var glow = hero.querySelector("[data-hero-glow]");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canHover = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  if (reduceMotion) {
    hero.classList.add("hero--static");
    return;
  }

  // --- Intro: Hauptplatte schwebt sanft ein -------------------------------
  requestAnimationFrame(function () {
    hero.classList.add("hero--ready");
  });

  // --- Zustand fuer Pointer- und Scrollwerte ------------------------------
  var pointer = { x: 0, y: 0 };
  var targetPointer = { x: 0, y: 0 };
  var scrollProgress = 0;
  var ticking = false;
  var visible = true;

  function updateScrollProgress() {
    var rect = hero.getBoundingClientRect();
    var travel = rect.height * 0.7;
    var passed = Math.min(Math.max(-rect.top, 0), travel);
    scrollProgress = travel > 0 ? passed / travel : 0;
  }

  function onPointerMove(event) {
    var rect = hero.getBoundingClientRect();
    targetPointer.x = (event.clientX - rect.left) / rect.width - 0.5;
    targetPointer.y = (event.clientY - rect.top) / rect.height - 0.5;
  }

  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(function () {
        updateScrollProgress();
        ticking = false;
      });
    }
  }

  var io = new IntersectionObserver(
    function (entries) {
      visible = entries[0].isIntersecting;
    },
    { threshold: 0 }
  );
  io.observe(hero);

  if (canHover) {
    hero.addEventListener("mousemove", onPointerMove);
    hero.addEventListener("mouseleave", function () {
      targetPointer.x = 0;
      targetPointer.y = 0;
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  updateScrollProgress();

  // --- Animationsschleife --------------------------------------------------
  function frame() {
    requestAnimationFrame(frame);
    if (!visible) return;

    pointer.x += (targetPointer.x - pointer.x) * 0.08;
    pointer.y += (targetPointer.y - pointer.y) * 0.08;

    var zoom = 1 + scrollProgress * 0.045;
    var driftX = scrollProgress * -20;

    if (bg) {
      bg.style.transform =
        "translate3d(" + (pointer.x * 6 + driftX * 0.4) + "px," + (pointer.y * 4) + "px,0) scale(1.08)";
    }
    if (plate) {
      plate.style.transform =
        "translate3d(" + (pointer.x * 14 + driftX) + "px," + (pointer.y * 10) + "px,0) scale(" + zoom + ")";
    }
    if (glow) {
      var sweep = Math.min(Math.max(scrollProgress / 0.55, 0), 1);
      var glowX = 30 + sweep * 45 + pointer.x * 10;
      var glowY = 35 + pointer.y * 14;
      glow.style.background =
        "radial-gradient(38em 30em at " + glowX + "% " + glowY + "%, rgba(255,214,160,0.55), transparent 60%)";
    }
  }
  requestAnimationFrame(frame);
})();
