/* ==========================================================================
   sources.js — Knowledge Sources page behavior
   ========================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var grid = document.getElementById('sourceGrid');
    var emptyState = document.getElementById('sourceEmptyState');
    var searchInput = document.getElementById('sourceSearch');
    var categoryFilter = document.getElementById('filterCategory');
    var jurisdictionFilter = document.getElementById('filterJurisdiction');
    var typeFilter = document.getElementById('filterType');
    var template = document.getElementById('sourceCardTemplate');
    if (!grid) return;

    var allSources = [];

    grid.innerHTML = '<div class="state-box"><div class="spinner dark" style="margin:0 auto 14px;"></div><h4>Loading sources…</h4></div>';

    window.IPSaktiAPI.getSources().then(function (sources) {
      allSources = sources;
      renderSources(allSources);
    });

    [searchInput, categoryFilter, jurisdictionFilter, typeFilter].forEach(function (el) {
      if (!el) return;
      el.addEventListener('input', applyFilters);
      el.addEventListener('change', applyFilters);
    });

    function applyFilters() {
      var term = (searchInput.value || '').toLowerCase();
      var category = categoryFilter.value;
      var jurisdiction = jurisdictionFilter.value;
      var type = typeFilter.value;

      var filtered = allSources.filter(function (src) {
        var matchesTerm = !term || src.name.toLowerCase().indexOf(term) !== -1;
        var matchesCategory = !category || src.category === category;
        var matchesJurisdiction = !jurisdiction || src.jurisdiction === jurisdiction;
        var matchesType = !type || src.type === type;
        return matchesTerm && matchesCategory && matchesJurisdiction && matchesType;
      });

      renderSources(filtered);
    }

    function renderSources(sources) {
      grid.innerHTML = '';
      if (!sources.length) {
        emptyState.style.display = 'block';
        return;
      }
      emptyState.style.display = 'none';

      sources.forEach(function (src) {
        var fragment = template.content.cloneNode(true);
        fragment.querySelector('[data-field="name"]').textContent = src.name;
        fragment.querySelector('[data-field="jurisdiction"]').textContent = src.jurisdiction;
        fragment.querySelector('[data-field="category"]').textContent = src.category;
        fragment.querySelector('[data-field="type"]').textContent = src.type;
        fragment.querySelector('[data-field="version"]').textContent = src.version;
        fragment.querySelector('[data-field="link"]').href = src.url;
        grid.appendChild(fragment);
      });
    }
  });
})();
