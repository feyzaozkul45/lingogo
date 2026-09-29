(function () {
  if (!('speechSynthesis' in window) || typeof SpeechSynthesisUtterance === 'undefined') {
    return;
  }

  document.documentElement.classList.add('tts-supported');

  document.addEventListener('click', function (event) {
    var button = event.target.closest('.speak-btn');
    if (!button) return;

    var text = button.getAttribute('data-text');
    if (!text) return;

    var utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = parseFloat(button.getAttribute('data-rate')) || 1;

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  });
})();
