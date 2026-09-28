// Roadrunner Food Bank — Redesign Concept — shared behavior
(function () {
  "use strict";

  // Translation helper from js/i18n.js (falls back to the English given here
  // if that script didn't load).
  function tr(key, english) {
    return typeof window.t === "function" ? window.t(key, english) : english;
  }

  // ---- Sticky header height var + shadow on scroll ----
  var header = document.querySelector(".site-header");
  // --header-bottom is where the header ends on screen (it sits below the
  // utility bar until that scrolls away), so the mobile menu opens right under it.
  function setHeaderHeight() {
    if (!header) return;
    document.documentElement.style.setProperty("--header-bottom", header.getBoundingClientRect().bottom + "px");
  }
  setHeaderHeight();
  window.addEventListener("resize", setHeaderHeight);
  window.addEventListener("scroll", function () {
    if (!header) return;
    header.classList.toggle("scrolled", window.scrollY > 8);
  });

  // ---- Mobile nav toggle ----
  var navToggle = document.querySelector(".nav-toggle");
  var primaryNav = document.querySelector(".primary-nav");
  if (navToggle && primaryNav) {
    var scrim = document.createElement("div");
    scrim.className = "nav-scrim";
    document.body.appendChild(scrim);
    primaryNav.id = primaryNav.id || "primary-nav";
    navToggle.setAttribute("aria-controls", primaryNav.id);

    function setNav(open) {
      if (open) setHeaderHeight();
      primaryNav.classList.toggle("open", open);
      scrim.classList.toggle("show", open);
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      navToggle.setAttribute("aria-label", open ? tr("js.close-menu", "Close menu") : tr("js.open-menu", "Open menu"));
      document.body.style.overflow = open ? "hidden" : "";
    }
    navToggle.setAttribute("aria-label", tr("js.open-menu", "Open menu"));
    document.addEventListener("i18n:change", function () {
      setNav(primaryNav.classList.contains("open"));
    });
    navToggle.addEventListener("click", function () {
      setNav(!primaryNav.classList.contains("open"));
    });
    scrim.addEventListener("click", function () { setNav(false); });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 1140 && primaryNav.classList.contains("open")) setNav(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && primaryNav.classList.contains("open")) {
        setNav(false);
        navToggle.focus();
      }
    });
    primaryNav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { setNav(false); });
    });
  }

  // ---- Reveal on scroll ----
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }

  // ---- Animated counters ----
  var prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var counters = document.querySelectorAll("[data-count-to]");
  function animateCounter(el) {
    var target = parseFloat(el.getAttribute("data-count-to"));
    var suffix = el.getAttribute("data-suffix") || "";
    var decimals = el.getAttribute("data-decimals") ? parseInt(el.getAttribute("data-decimals"), 10) : 0;
    if (prefersReducedMotion) {
      el.textContent = target.toFixed(decimals) + suffix;
      return;
    }
    var duration = 1400;
    var start = null;
    function step(ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var val = target * eased;
      el.textContent = val.toFixed(decimals) + suffix;
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target.toFixed(decimals) + suffix;
    }
    requestAnimationFrame(step);
  }
  if ("IntersectionObserver" in window && counters.length) {
    var cio = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            cio.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.4 }
    );
    counters.forEach(function (el) { cio.observe(el); });
  }

  // ---- Accordion (Get Help FAQ) ----
  document.querySelectorAll(".accordion-item button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var expanded = btn.getAttribute("aria-expanded") === "true";
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      btn.setAttribute("aria-expanded", expanded ? "false" : "true");
      if (panel) panel.style.maxHeight = expanded ? null : panel.scrollHeight + "px";
    });
  });

  // ---- Impact calculator (Ways to Give) ----
  var slider = document.getElementById("give-slider");
  var amountOut = document.getElementById("calc-amount");
  var mealsOut = document.getElementById("calc-meals");
  function updateCalc(val) {
    var locale = window.i18nLang && window.i18nLang() === "es" ? "es-US" : "en-US";
    if (amountOut) amountOut.textContent = "$" + Number(val).toLocaleString(locale);
    if (mealsOut) mealsOut.textContent = Number(val * 5).toLocaleString(locale) + " " + tr("js.meals", "meals");
  }
  if (slider) {
    updateCalc(slider.value);
    slider.addEventListener("input", function () { updateCalc(slider.value); });
    document.addEventListener("i18n:change", function () { updateCalc(slider.value); });
    document.querySelectorAll(".chip[data-amount]").forEach(function (chip) {
      chip.addEventListener("click", function () {
        document.querySelectorAll(".chip[data-amount]").forEach(function (c) { c.classList.remove("active"); });
        chip.classList.add("active");
        slider.value = chip.getAttribute("data-amount");
        updateCalc(slider.value);
      });
    });
  }

  // ---- Demo form handling (no backend — this is a pitch concept) ----
  // Includes a basic bot-resistance pattern: a visually hidden honeypot field
  // that real visitors never fill in, plus a render-timestamp field that
  // catches submissions completed implausibly fast. Wire the real submit
  // handler (Formspree, Netlify Forms, a custom endpoint, etc.) in here —
  // both checks below should run BEFORE that request is sent.
  document.querySelectorAll("form[data-demo-form]").forEach(function (form) {
    var timestampField = form.querySelector(".form-rendered-at");
    if (timestampField) timestampField.value = String(Date.now());

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      var honeypot = form.querySelector('input[name="website"]');
      if (honeypot && honeypot.value.trim() !== "") {
        // Silently drop likely-bot submissions — no error shown, so the
        // bot gets no signal that it was caught.
        form.reset();
        return;
      }
      if (timestampField && timestampField.value) {
        var elapsed = Date.now() - Number(timestampField.value);
        if (elapsed < 1500) {
          form.reset();
          return;
        }
      }

      var success = form.parentElement.querySelector(".form-success") || document.getElementById(form.getAttribute("data-success-target"));
      if (success) {
        success.classList.add("show");
        success.setAttribute("tabindex", "-1");
        success.focus();
      }
      form.reset();
      if (timestampField) timestampField.value = String(Date.now());
    });
  });

  // ---- Food finder demo (Home + Get Help) ----
  document.querySelectorAll("form[data-finder]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var input = form.querySelector("input");
      var resultEl = form.parentElement.querySelector("[data-finder-result]");
      if (resultEl && input) {
        resultEl.dataset.zip = input.value.trim();
        showFinderResult(resultEl);
      }
    });
  });
  function showFinderResult(el) {
    el.textContent =
      tr("js.finder-showing", "Showing partner pantries near") + " " +
      (el.dataset.zip || tr("js.finder-your-area", "your area")) + " — " +
      tr("js.finder-live-map", "this live map connects to RRFB's partner-agency database.");
    el.classList.add("show");
  }
  // Re-render a shown result after a language switch (the toggle resets the
  // element to its translated placeholder hint first).
  document.addEventListener("i18n:change", function () {
    document.querySelectorAll("[data-finder-result]").forEach(function (el) {
      if (el.dataset.zip !== undefined) showFinderResult(el);
    });
  });

  // ---- Footer year ----
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
