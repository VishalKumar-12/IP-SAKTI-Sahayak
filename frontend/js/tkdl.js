/* ==========================================================================
   tkdl.js — Traditional Knowledge / TKDL Helper page behavior
   ========================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    var form = document.getElementById('tkdlForm');
    var resultArea = document.getElementById('tkdlResultArea');
    var submitBtn = document.getElementById('tkdlSubmit');
    var template = document.getElementById('tkdlResultTemplate');

    if (!form || !resultArea) return;

    form.addEventListener('submit', function (e) {

      e.preventDefault();

      var query =
        document.getElementById('tkdlQuery').value.trim();

      if (!query) return;

      showLoading();

      submitBtn.disabled = true;

      window.IPSaktiAPI
        .checkTraditionalKnowledge(query)
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
        '<h4>Checking traditional knowledge indicators…</h4>' +
        '<p>Searching authorized, publicly available references.</p>' +
        '</div>';
    }


    function showError(error) {

      console.error('TKDL Error:', error);

      resultArea.innerHTML =
        '<div class="state-box state-error">' +
        '<div class="state-icon">⚠️</div>' +
        '<h4>Something went wrong</h4>' +
        '<p>The traditional-knowledge check could not be completed. Please try again.</p>' +
        '</div>';
    }


    function renderResult(data) {

      var fragment =
        template.content.cloneNode(true);

      var root =
        fragment.firstElementChild;


      /* Answer */

      root.querySelector(
        '[data-field="summary"]'
      ).textContent =
        data.answer ||
        'I could not find sufficient information in the available sources.';


      /* Relevance */

      var relevanceEl =
        root.querySelector('[data-field="relevance"]');

      if (relevanceEl) {
        relevanceEl.textContent =
          'TKDL-related information found in the available sources.';
      }


      /* Category */

      var categoryEl =
        root.querySelector('[data-field="category"]');

      if (categoryEl) {
        categoryEl.textContent =
          'Traditional Knowledge / TKDL';
      }


      /* Sources */

      var sourcesEl =
        root.querySelector('[data-field="sources"]');

      sourcesEl.innerHTML = '';


      (data.sources || []).forEach(function (src) {

        var item =
          document.createElement('div');

        item.className =
          'source-item';


        item.innerHTML =
          '<span class="source-icon" aria-hidden="true">📄</span>' +
          '<div><strong></strong><span></span></div>';


        var sourceLink =
          document.createElement('a');

        sourceLink.href =
          src.url || '#';

        sourceLink.target =
          '_blank';

        sourceLink.rel =
          'noopener noreferrer';

        sourceLink.textContent =
          src.title || src.document || 'Unknown source';


        item.querySelector('strong')
          .appendChild(sourceLink);


        var metaParts = [];


        if (
          src.page !== null &&
          src.page !== undefined &&
          src.page !== ''
        ) {
          metaParts.push(
            'Page ' + src.page
          );
        }


        if (src.section) {
          metaParts.push(
            src.section
          );
        }


        item.querySelector('span').textContent =
          metaParts.join(' · ');


        sourcesEl.appendChild(item);
      });


      /* Confidence */

      var confidence =
        data.confidence ?? 0;

      var pct =
        Math.round(confidence * 100);


      root.querySelector(
        '[data-field="confidenceValue"]'
      ).textContent =
        pct + '%';


      var level =
        confidence >= 0.75
          ? 'high'
          : confidence >= 0.50
            ? 'medium'
            : 'low';


      var levelEl =
        root.querySelector(
          '[data-field="confidenceLevel"]'
        );


      levelEl.textContent =
        level.charAt(0).toUpperCase() +
        level.slice(1);


      levelEl.className =
        'confidence-level ' + level;


      var bar =
        root.querySelector(
          '[data-field="confidenceBar"]'
        );


      bar.className =
        'confidence-bar ' + level;


      bar.querySelector('span')
        .style.width =
        pct + '%';


      resultArea.innerHTML =
        '';

      resultArea.appendChild(
        fragment
      );
    }

  });

})();