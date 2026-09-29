// Okuma sayfasi: "Turkcesini goster" / "gizle" gecisi.
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('readingTrToggle');
  var text = document.getElementById('readingTrText');

  if (!toggle || !text) {
    return;
  }

  toggle.addEventListener('click', function () {
    text.hidden = !text.hidden;
    toggle.textContent = text.hidden ? 'Türkçesini göster' : 'Türkçesini gizle';
  });
});
