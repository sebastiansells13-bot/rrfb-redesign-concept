// English/Spanish toggle — same approach as the toggle on julia-ketsaa-remax
// and 21st-century-care, adapted for this build-less static site: the
// dictionary lives in js/i18n-data.js (window.I18N_DATA) instead of a JSON
// island a template would inline.
//
// Client-side only — there's no separate /es/ URL per page, so this is a
// visitor convenience, not a Spanish-language SEO strategy. The choice
// persists per visitor via localStorage ("lang").
//
// Markup contract (scripts/i18n.py adds these and checks nothing is missed):
//   data-i18n="key"       → element's text content is replaced. Only on
//                           elements whose sole child is text.
//   data-i18n-html="key"  → element's inner HTML is replaced, for copy that
//                           mixes text with inline tags (<a>, <strong>…).
//   data-i18n-attr="placeholder:key;aria-label:key" → attributes replaced.
//   data-i18n-skip        → never translated (org name, addresses, emails).
// The English copy in the page is cached on first use, so switching back to
// English restores exactly what the HTML shipped with.
//
// Exposes window.t(key[, fallback]) and window.i18nLang() for js/main.js.
(function () {
  "use strict";
  var dict = window.I18N_DATA || {};

  function i18nLang() {
    try {
      return localStorage.getItem("lang") === "es" ? "es" : "en";
    } catch (err) {
      return "en";
    }
  }

  // t("key") → the string in the current language, falling back to English,
  // then to `fallback`, then to the key itself.
  function t(key, fallback) {
    var entry = dict[key];
    if (!entry) return fallback !== undefined ? fallback : key;
    return (i18nLang() === "es" && entry.es) || entry.en;
  }

  window.i18nLang = i18nLang;
  window.t = t;

  function lookup(key, lang, english) {
    var entry = dict[key];
    return lang === "es" && entry && entry.es ? entry.es : english;
  }

  function applyAll(lang) {
    document.documentElement.lang = lang;

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      if (el.dataset.i18nEn === undefined) el.dataset.i18nEn = el.textContent;
      el.textContent = lookup(el.dataset.i18n, lang, el.dataset.i18nEn);
    });

    document.querySelectorAll("[data-i18n-html]").forEach(function (el) {
      if (el.dataset.i18nEn === undefined) el.dataset.i18nEn = el.innerHTML;
      el.innerHTML = lookup(el.dataset.i18nHtml, lang, el.dataset.i18nEn);
    });

    document.querySelectorAll("[data-i18n-attr]").forEach(function (el) {
      el.dataset.i18nAttr.split(";").forEach(function (pair) {
        var parts = pair.split(":");
        var attr = parts[0];
        var cacheKey = "i18nEnAttr" + attr.replace(/(^|-)([a-z])/g, function (m, d, c) { return c.toUpperCase(); });
        if (el.dataset[cacheKey] === undefined) el.dataset[cacheKey] = el.getAttribute(attr) || "";
        el.setAttribute(attr, lookup(parts[1], lang, el.dataset[cacheKey]));
      });
    });

    document.querySelectorAll("[data-lang-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.dataset.langToggle === lang));
    });

    document.documentElement.classList.remove("i18n-pending");
    document.dispatchEvent(new CustomEvent("i18n:change", { detail: { lang: lang } }));
  }

  function setLanguage(lang) {
    try {
      localStorage.setItem("lang", lang);
    } catch (err) {
      // Private browsing / storage blocked — still apply for this page view.
    }
    applyAll(lang);
  }

  document.querySelectorAll("[data-lang-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      setLanguage(btn.dataset.langToggle);
    });
  });

  // Apply on load only when needed — English is what the HTML already says.
  if (i18nLang() === "es") applyAll("es");
  else document.documentElement.classList.remove("i18n-pending");
})();
