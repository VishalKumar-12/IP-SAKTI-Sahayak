/* ==========================================================================
   voice.js — microphone input for the chat composer
   Uses the Web Speech API when the browser supports it; otherwise the
   button informs the user the feature is unavailable in their browser.
   ========================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var micBtn = document.getElementById('micBtn');
    var input = document.getElementById('chatInput');
    if (!micBtn || !input) return;

    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognizing = false;
    var recognition = null;

    if (SpeechRecognition) {
      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.addEventListener('result', function (event) {
        var transcript = event.results[0][0].transcript;
        input.value = (input.value ? input.value + ' ' : '') + transcript;
        input.dispatchEvent(new Event('input'));
      });

      recognition.addEventListener('end', function () {
        recognizing = false;
        micBtn.classList.remove('active');
        micBtn.setAttribute('aria-pressed', 'false');
      });

      recognition.addEventListener('error', function () {
        recognizing = false;
        micBtn.classList.remove('active');
        micBtn.setAttribute('aria-pressed', 'false');
      });
    }

    micBtn.addEventListener('click', function () {
      if (!recognition) {
        micBtn.title = 'Voice input is not supported in this browser';
        micBtn.classList.add('active');
        setTimeout(function () { micBtn.classList.remove('active'); }, 900);
        return;
      }

      if (recognizing) {
        recognition.stop();
        return;
      }

      try {
        var lang = window.IPSaktiLanguage ? window.IPSaktiLanguage.getCurrentLanguage() : 'en';
        var langMap = { en: 'en-IN', hi: 'hi-IN', ur: 'ur-IN', bho: 'hi-IN', mai: 'hi-IN', mag: 'hi-IN' };
        recognition.lang = langMap[lang] || 'en-IN';
        recognition.start();
        recognizing = true;
        micBtn.classList.add('active');
        micBtn.setAttribute('aria-pressed', 'true');
      } catch (e) {
        recognizing = false;
      }
    });
  });
})();
