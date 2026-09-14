/* ==========================================================================
   abs.js — ABS Helper page behavior
   ========================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('absForm');
    var resultArea = document.getElementById('absResultArea');
    var submitBtn = document.getElementById('absSubmit');
    var template = document.getElementById('absResultTemplate');

    if (!form || !resultArea) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var resource = document.getElementById('bioResource').value.trim();
      if (!resource) return;

      var resourceType =
        form.querySelector('input[name="resourceType"]:checked').value;

      var purpose =
        form.querySelector('input[name="purpose"]:checked').value;

      var jurisdiction =
        document.getElementById('absJurisdiction').value;

      showLoading();
      submitBtn.disabled = true;

      window.IPSaktiAPI.analyzeABS({
        resource: resource,
        resourceType: resourceType,
        purpose: purpose,
        jurisdiction: jurisdiction
      })
        .then(renderResult)
        .catch(showError)
        .finally(function () {
          submitBtn.disabled = false;
        });
    });

    function showLoading() {
      resultArea.innerHTML =
        '<div class="state-box">' +
        '<div class="spinner dark" style="margin:0 auto 14px;"></div>' +
        '<h4>Analyzing ABS considerations…</h4>' +
        '<p>Checking biodiversity and traditional-knowledge frameworks.</p>' +
        '</div>';
    }

    function showError(error) {
      console.error('ABS Error:', error);

      resultArea.innerHTML =
        '<div class="state-box state-error">' +
        '<div class="state-icon">⚠️</div>' +
        '<h4>Something went wrong</h4>' +
        '<p>The ABS analysis could not be completed. Please try again.</p>' +
        '</div>';
    }

    function renderResult(data) {
      var fragment = template.content.cloneNode(true);
      var root = fragment.firstElementChild;

      root.querySelector('[data-field="summary"]').textContent =
        data.access ||
        'I could not find sufficient information in the available sources.';

      root.querySelector('[data-field="resource"]').textContent =
        'Resource: ' + (data.resource || '');

      root.querySelector('[data-field="access"]').textContent =
        data.access || '';

      root.querySelector('[data-field="benefitSharing"]').textContent =
        data.benefit_sharing || '';

      root.querySelector('[data-field="traditionalKnowledge"]').textContent =
        data.traditional_knowledge || '';

      root.querySelector('[data-field="framework"]').textContent =
        data.framework || '';

      var sourcesEl =
        root.querySelector('[data-field="sources"]');

      sourcesEl.innerHTML = '';

      (data.sources || []).forEach(function (src) {
        var item = document.createElement('div');

        item.className = 'source-item';

        item.innerHTML =
          '<span class="source-icon" aria-hidden="true">📄</span>' +
          '<div><strong></strong><span></span></div>';

        var sourceLink = document.createElement('a');

        sourceLink.href = src.url || '#';
        sourceLink.target = '_blank';
        sourceLink.rel = 'noopener noreferrer';
        sourceLink.textContent =
          src.document || 'Unknown source';

        item.querySelector('strong').appendChild(sourceLink);

        var metaParts = [];

        if (src.section) {
          metaParts.push(src.section);
        }

        if (
          src.page !== null &&
          src.page !== undefined &&
          src.page !== ''
        ) {
          metaParts.push('Page ' + src.page);
        }

        item.querySelector('span').textContent =
          metaParts.join(' · ');

        sourcesEl.appendChild(item);
      });

      var confidence = data.confidence ?? 0;
      var pct = Math.round(confidence * 100);

      root.querySelector('[data-field="confidenceValue"]').textContent =
        pct + '%';

      var level = data.confidence_level || 'low';

      var levelEl =
        root.querySelector('[data-field="confidenceLevel"]');

      levelEl.textContent =
        level.charAt(0).toUpperCase() + level.slice(1);

      levelEl.className =
        'confidence-level ' + level;

      var bar =
        root.querySelector('[data-field="confidenceBar"]');

      bar.className =
        'confidence-bar ' + level;

      bar.querySelector('span').style.width =
        pct + '%';

      resultArea.innerHTML = '';
      resultArea.appendChild(fragment);
    }
  });
})();