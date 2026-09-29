// Gercek hayat senaryosu: sohbet balonlarini adim adim olusturur.
// Dogru cevapta bir sonraki adima gecilir, yanlista kisa geri bildirimle
// kullanici tekrar dener. Son adim bitince gizli formu gonderip tamamlanmayi
// sunucuya kaydeder (bkz. lessons/views.py scenario_view).
document.addEventListener('DOMContentLoaded', function () {
  var dataEl = document.getElementById('scenario-steps-data');
  var chat = document.getElementById('scenarioChat');
  var finishForm = document.getElementById('scenarioFinishForm');

  if (!dataEl || !chat) {
    return;
  }

  var steps = JSON.parse(dataEl.textContent);

  function shuffle(items) {
    var copy = items.slice();
    for (var i = copy.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = copy[i];
      copy[i] = copy[j];
      copy[j] = tmp;
    }
    return copy;
  }

  function buildSpeakButtons(text) {
    var wrap = document.createElement('span');
    wrap.className = 'speak-buttons';

    [{ label: '🔊', rate: '1', aria: 'İngilizce dinle' }, { label: '🐢', rate: '0.6', aria: 'Yavaş dinle' }].forEach(function (cfg) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'speak-btn';
      btn.setAttribute('data-text', text);
      btn.setAttribute('data-rate', cfg.rate);
      btn.setAttribute('aria-label', cfg.aria);
      btn.textContent = cfg.label;
      wrap.appendChild(btn);
    });

    return wrap;
  }

  function renderStep(index) {
    var step = steps[index];

    var themBubble = document.createElement('div');
    themBubble.className = 'scenario-bubble scenario-bubble--them';

    var speaker = document.createElement('div');
    speaker.className = 'scenario-bubble__speaker';
    speaker.textContent = step.speaker;
    themBubble.appendChild(speaker);

    var lineRow = document.createElement('div');
    lineRow.className = 'scenario-bubble__line';

    var lineText = document.createElement('span');
    lineText.className = 'en';
    lineText.textContent = step.line;
    lineRow.appendChild(lineText);
    lineRow.appendChild(buildSpeakButtons(step.line));

    themBubble.appendChild(lineRow);

    if (step.line_tr) {
      var trToggle = document.createElement('button');
      trToggle.type = 'button';
      trToggle.className = 'scenario-tr-toggle';
      trToggle.textContent = 'Türkçesini göster';

      var trText = document.createElement('div');
      trText.className = 'scenario-bubble__tr tr';
      trText.textContent = step.line_tr;
      trText.hidden = true;

      trToggle.addEventListener('click', function () {
        trText.hidden = !trText.hidden;
        trToggle.textContent = trText.hidden ? 'Türkçesini göster' : 'Türkçesini gizle';
      });

      themBubble.appendChild(trToggle);
      themBubble.appendChild(trText);
    }

    chat.appendChild(themBubble);

    var optionsWrap = document.createElement('div');
    optionsWrap.className = 'scenario-options';

    shuffle(step.options).forEach(function (option) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'scenario-option';
      btn.textContent = option.text;
      btn.addEventListener('click', function () {
        handleAnswer(option, btn, optionsWrap, index);
      });
      optionsWrap.appendChild(btn);
    });

    chat.appendChild(optionsWrap);
    optionsWrap.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }

  function handleAnswer(option, btn, optionsWrap, stepIndex) {
    if (!option.correct) {
      btn.disabled = true;
      btn.classList.add('scenario-option--wrong');

      if (option.feedback) {
        var wrongFeedback = document.createElement('div');
        wrongFeedback.className = 'scenario-feedback scenario-feedback--wrong';
        wrongFeedback.textContent = option.feedback;
        btn.insertAdjacentElement('afterend', wrongFeedback);
      }
      return;
    }

    Array.prototype.slice.call(optionsWrap.children).forEach(function (child) {
      if (child.tagName === 'BUTTON') {
        child.disabled = true;
      }
    });
    btn.classList.add('scenario-option--correct');

    var meBubble = document.createElement('div');
    meBubble.className = 'scenario-bubble scenario-bubble--me';
    meBubble.textContent = option.text;
    chat.appendChild(meBubble);

    if (option.feedback) {
      var okFeedback = document.createElement('div');
      okFeedback.className = 'scenario-feedback scenario-feedback--correct';
      okFeedback.textContent = option.feedback;
      chat.appendChild(okFeedback);
    }

    var isLastStep = stepIndex === steps.length - 1;
    var continueBtn = document.createElement('button');
    continueBtn.type = 'button';
    continueBtn.className = 'btn btn-primary';
    continueBtn.textContent = isLastStep ? 'Bitir 🎉' : 'Devam →';
    continueBtn.addEventListener('click', function () {
      continueBtn.remove();
      if (isLastStep) {
        if (finishForm) {
          finishForm.submit();
        }
      } else {
        renderStep(stepIndex + 1);
      }
    });
    chat.appendChild(continueBtn);
    continueBtn.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }

  if (steps.length) {
    renderStep(0);
  }
});
