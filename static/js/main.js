// Kücük genel etkilesimler: menü dışına tıklayınca kapanması, flash mesajların otomatik kaybolması.
document.addEventListener('DOMContentLoaded', function () {
  var navToggle = document.querySelector('.nav-toggle');
  if (navToggle) {
    document.addEventListener('click', function (event) {
      if (navToggle.open && !navToggle.contains(event.target)) {
        navToggle.open = false;
      }
    });
  }

  // Sadece ust menudeki gecici sistem mesajlari (Django messages) otomatik kaybolur;
  // sayfa icerigi olan bildirimler (ör. quiz sonucundaki "kayit ol" cagrisi) kalir.
  document.querySelectorAll('.flash-messages .flash').forEach(function (flash) {
    setTimeout(function () {
      flash.style.opacity = '0';
      setTimeout(function () { flash.remove(); }, 300);
    }, 4000);
  });
});
