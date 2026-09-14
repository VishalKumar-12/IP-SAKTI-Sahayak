/* ==========================================================================
   app.js — shared behavior across every page
   (nav toggle, mobile menu, jurisdiction sync, chat sidebar toggle)
   ========================================================================== */

(function () {
  'use strict';

  function initNavToggle() {
    var toggle = document.getElementById('navToggle');
    var links = document.getElementById('navLinks');
    var tools = document.getElementById('navTools');
    if (!toggle || !links) return;

    toggle.addEventListener('click', function () {
      var isOpen = links.classList.toggle('open');
      if (tools) tools.classList.toggle('mobile-open', isOpen);
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    // Close mobile menu when a nav link is clicked
    links.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        links.classList.remove('open');
        if (tools) tools.classList.remove('mobile-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  function initJurisdictionSync() {
    var selects = document.querySelectorAll('[data-role="jurisdiction-select"]');
    if (!selects.length) return;

    var STORAGE_KEY = 'ipsakti_jurisdiction';
    var saved = null;
    try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) { /* storage unavailable */ }

    if (saved) {
      selects.forEach(function (s) {
        if ([].some.call(s.options, function (o) { return o.value === saved; })) {
          s.value = saved;
        }
      });
    }

    selects.forEach(function (select) {
      select.addEventListener('change', function () {
        var value = select.value;
        try { localStorage.setItem(STORAGE_KEY, value); } catch (e) { /* ignore */ }
        selects.forEach(function (s) { if (s !== select) s.value = value; });
        document.dispatchEvent(new CustomEvent('jurisdictionchange', { detail: { jurisdiction: value } }));
      });
    });
  }

  function initChatSidebarToggle() {
    var toggle = document.getElementById('sidebarToggle');
    var sidebar = document.getElementById('chatSidebar');
    if (!toggle || !sidebar) return;

    toggle.addEventListener('click', function () {
      var isOpen = sidebar.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    document.addEventListener('click', function (e) {
      if (window.innerWidth > 768) return;
      if (sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) &&
          e.target !== toggle) {
        sidebar.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initNavToggle();
    initJurisdictionSync();
    initChatSidebarToggle();
  });
})();
