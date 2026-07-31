/**
 * TERRA COTTA - allgemeine Interaktivitaet (Navigation, FAQ, Galerie-Filter).
 * Vanilla JS, keine Abhaengigkeiten, funktioniert unabhaengig von hero.js.
 */
(function () {
  "use strict";

  document.documentElement.classList.remove("no-js");
  document.getElementById("year") &&
    (document.getElementById("year").textContent = new Date().getFullYear());

  // --- Mobiles Menue ---------------------------------------------------
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.querySelector("[data-nav]");
  var scrim = document.querySelector("[data-nav-scrim]");

  function setNav(open) {
    if (!nav || !toggle) return;
    nav.setAttribute("data-open", open ? "true" : "false");
    scrim && scrim.setAttribute("data-open", open ? "true" : "false");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      setNav(toggle.getAttribute("aria-expanded") !== "true");
    });
    scrim && scrim.addEventListener("click", function () { setNav(false); });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () { setNav(false); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setNav(false);
    });
  }

  // --- FAQ-Akkordeon -----------------------------------------------------
  document.querySelectorAll("[data-faq-item]").forEach(function (item) {
    var btn = item.querySelector("[data-faq-q]");
    btn && btn.addEventListener("click", function () {
      var isOpen = item.getAttribute("data-open") === "true";
      item.parentElement.querySelectorAll("[data-faq-item]").forEach(function (other) {
        other.setAttribute("data-open", "false");
        other.querySelector("[data-faq-q]").setAttribute("aria-expanded", "false");
      });
      item.setAttribute("data-open", isOpen ? "false" : "true");
      btn.setAttribute("aria-expanded", isOpen ? "false" : "true");
    });
  });

  // --- Galerie-Filter (Arbeiten-Seite) ------------------------------------
  var filterBar = document.querySelector("[data-filter-bar]");
  if (filterBar) {
    var buttons = filterBar.querySelectorAll("button");
    var items = document.querySelectorAll("[data-gallery] [data-category]");
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        buttons.forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        btn.setAttribute("aria-pressed", "true");
        var filter = btn.getAttribute("data-filter");
        items.forEach(function (item) {
          var show = filter === "alle" || item.getAttribute("data-category") === filter;
          item.style.display = show ? "" : "none";
        });
      });
    });
  }

  // --- Header-Schatten nach Scrollbeginn ----------------------------------
  var header = document.querySelector("[data-site-header]");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }
})();
