/* ==========================================================================
   language.js — language selection logic, kept separate from UI markup
   Architected to allow future Bhashini integration on the backend without
   any change to this module's public interface.
   ========================================================================== */

window.IPSaktiLanguage = (function () {
  'use strict';

  var STORAGE_KEY = 'ipsakti_language';

  var SUPPORTED_LANGUAGES = {

    en:   { label: 'English', dir: 'ltr' },
    hi:   { label: 'Hindi', dir: 'ltr' },
    as:   { label: 'Assamese', dir: 'ltr' },
    bn:   { label: 'Bengali', dir: 'ltr' },
    gu:   { label: 'Gujarati', dir: 'ltr' },
    kn:   { label: 'Kannada', dir: 'ltr' },
    ks:   { label: 'Kashmiri', dir: 'rtl' },
    kok:  { label: 'Konkani', dir: 'ltr' },
    mai:  { label: 'Maithili', dir: 'ltr' },
    ml:   { label: 'Malayalam', dir: 'ltr' },
    mr:   { label: 'Marathi', dir: 'ltr' },
    ne:   { label: 'Nepali', dir: 'ltr' },
    or:   { label: 'Odia', dir: 'ltr' },
    pa:   { label: 'Punjabi', dir: 'ltr' },
    sa:   { label: 'Sanskrit', dir: 'ltr' },
    sd:   { label: 'Sindhi', dir: 'rtl' },
    ta:   { label: 'Tamil', dir: 'ltr' },
    te:   { label: 'Telugu', dir: 'ltr' },
    ur:   { label: 'Urdu', dir: 'rtl' },
    bodo: { label: 'Bodo', dir: 'ltr' },
    doi:  { label: 'Dogri', dir: 'ltr' },
    mni:  { label: 'Manipuri', dir: 'ltr' },
    bho:  { label: 'Bhojpuri', dir: 'ltr' },
    mag:  { label: 'Magahi', dir: 'ltr' }

};

  function getCurrentLanguage() {
    try {
      return localStorage.getItem(STORAGE_KEY) || 'en';
    } catch (e) {
      return 'en';
    }
  }

  function setCurrentLanguage(code) {
    if (!SUPPORTED_LANGUAGES[code]) return;
    try { localStorage.setItem(STORAGE_KEY, code); } catch (e) { /* ignore */ }
    document.documentElement.setAttribute('lang', code);
    document.documentElement.setAttribute('dir', SUPPORTED_LANGUAGES[code].dir);
    document.dispatchEvent(new CustomEvent('languagechange', { detail: { language: code } }));
  }
function syncSelectsToStoredLanguage() {
  var current = getCurrentLanguage();

  var selects = document.querySelectorAll(
    '[data-role="language-select"]'
  );

  selects.forEach(function (select) {

    // Clear existing options
    select.innerHTML = '';

    // Create options from SUPPORTED_LANGUAGES
    Object.keys(SUPPORTED_LANGUAGES).forEach(function (code) {

      var option = document.createElement('option');

      option.value = code;
      option.textContent = SUPPORTED_LANGUAGES[code].label;

      select.appendChild(option);
    });

    // Select saved language
    select.value = current;
  });

  setCurrentLanguage(current);
}

  function bindSelects() {
    var selects = document.querySelectorAll('[data-role="language-select"]');
    selects.forEach(function (select) {
      select.addEventListener('change', function () {
        var value = select.value;
        selects.forEach(function (s) { if (s !== select) s.value = value; });
        setCurrentLanguage(value);
      });
    });
  }

  /*
   * translate(key)
   * Placeholder hook for future Bhashini-backed translation of UI strings.
   * Currently a passthrough so the rest of the app can call it safely.
   */
  function translate(key) {
    return key;
  }

  document.addEventListener('DOMContentLoaded', function () {
    syncSelectsToStoredLanguage();
    bindSelects();
  });

  return {
    getCurrentLanguage: getCurrentLanguage,
    setCurrentLanguage: setCurrentLanguage,
    SUPPORTED_LANGUAGES: SUPPORTED_LANGUAGES,
    translate: translate
  };
})();
