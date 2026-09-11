// Roadrunner Food Bank — Redesign Concept — shared behavior
(function () {
  "use strict";

  // ---- Sticky header height var + shadow on scroll ----
  var header = document.querySelector(".site-header");
  function setHeaderHeight() {
    if (!header) return;
    document.documentElement.style.setProperty("--header-h", header.offsetHeight + "px");
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
    navToggle.addEventListener("click", function () {
      var open = primaryNav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.style.overflow = open ? "hidden" : "";
    });
    primaryNav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        primaryNav.classList.remove("open");
        navToggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      });
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
  var counters = document.querySelectorAll("[data-count-to]");
  function animateCounter(el) {
    var target = parseFloat(el.getAttribute("data-count-to"));
    var suffix = el.getAttribute("data-suffix") || "";
    var decimals = el.getAttribute("data-decimals") ? parseInt(el.getAttribute("data-decimals"), 10) : 0;
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
    if (amountOut) amountOut.textContent = "$" + Number(val).toLocaleString();
    if (mealsOut) mealsOut.textContent = Number(val * 5).toLocaleString() + " meals";
  }
  if (slider) {
    updateCalc(slider.value);
    slider.addEventListener("input", function () { updateCalc(slider.value); });
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
  document.querySelectorAll("form[data-demo-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var success = form.parentElement.querySelector(".form-success") || document.getElementById(form.getAttribute("data-success-target"));
      if (success) {
        success.classList.add("show");
        success.setAttribute("tabindex", "-1");
        success.focus();
      }
      form.reset();
    });
  });

  // ---- Food finder demo (Home + Get Help) ----
  document.querySelectorAll("form[data-finder]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var input = form.querySelector("input");
      var resultEl = form.parentElement.querySelector("[data-finder-result]");
      if (resultEl && input) {
        resultEl.textContent =
          "Showing partner pantries near " + (input.value || "your area") + " — this live map connects to RRFB's partner-agency database.";
        resultEl.classList.add("show");
      }
    });
  });

  // ---- Footer year ----
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
