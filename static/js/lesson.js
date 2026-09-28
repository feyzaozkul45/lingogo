// Ders sayfasi: kelimeler / ifadeler / grammar / ornek cumleler arasinda stepper.
// JS kapaliysa .no-js kurallari (main.css) tum adimlari alt alta gosterir.
document.addEventListener('DOMContentLoaded', function () {
  var steps = Array.prototype.slice.call(document.querySelectorAll('.lesson-step'));
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.lesson-tabs button'));
  var prevBtn = document.getElementById('lessonPrev');
  var nextBtn = document.getElementById('lessonNext');
  var fill = document.querySelector('.lesson-progressbar__fill');

  if (!steps.length || !tabs.length || steps.length !== tabs.length) {
    return;
  }

  var current = 0;

  function showStep(index) {
    current = index;
    steps.forEach(function (step, i) {
      step.classList.toggle('active', i === index);
    });
    tabs.forEach(function (tab, i) {
      tab.classList.toggle('active', i === index);
    });
    if (prevBtn) {
      prevBtn.disabled = index === 0;
    }
    if (nextBtn) {
      var isLast = index === steps.length - 1;
      nextBtn.disabled = isLast;
      nextBtn.textContent = isLast ? 'Son adım' : 'İleri →';
    }
    if (fill) {
      fill.style.width = Math.round(((index + 1) / steps.length) * 100) + '%';
    }
  }

  tabs.forEach(function (tab, i) {
    tab.addEventListener('click', function () {
      showStep(i);
    });
  });

  if (prevBtn) {
    prevBtn.addEventListener('click', function () {
      if (current > 0) {
        showStep(current - 1);
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      if (current < steps.length - 1) {
        showStep(current + 1);
      }
    });
  }

  showStep(0);
});
