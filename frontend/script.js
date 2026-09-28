/**
 * Ангел и Демон — Frontend Logic
 * Чистый Vanilla JS для Telegram Mini App
 */

// Инициализация Telegram WebApp
const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
  if (tg.setHeaderColor) tg.setHeaderColor('#000000');
  if (tg.setBackgroundColor) tg.setBackgroundColor('#000000');
  if (tg.enableClosingConfirmation) {
    tg.enableClosingConfirmation();
  }
}

// Утилита для тактильного отклика (Haptic Feedback)
function triggerHaptic(type = 'light') {
  if (!tg?.HapticFeedback) return;
  try {
    if (type === 'light') tg.HapticFeedback.impactOccurred('light');
    else if (type === 'medium') tg.HapticFeedback.impactOccurred('medium');
    else if (type === 'heavy') tg.HapticFeedback.impactOccurred('heavy');
    else if (type === 'success') tg.HapticFeedback.notificationOccurred('success');
    else if (type === 'error') tg.HapticFeedback.notificationOccurred('error');
  } catch (e) {
    console.debug('Haptic feedback error:', e);
  }
}

// Базовые заголовки запросов к API
function getHeaders() {
  const headers = {
    'Content-Type': 'application/json'
  };
  if (tg?.initData) {
    headers['X-Telegram-Init-Data'] = tg.initData;
  }
  return headers;
}

// Состояние приложения
const state = {
  currentDilemmaId: null,
  selectedSkin: 'classic',
  unlockedSkins: ['classic'],
  judgeSpheres: 1,
  karmaAngel: 0,
  karmaDemon: 0
};

// DOM Элементы
const el = {
  angelPercent: document.getElementById('angel-percent'),
  demonPercent: document.getElementById('demon-percent'),
  karmaBarFill: document.getElementById('karma-bar-fill'),
  spheresCount: document.getElementById('spheres-count'),
  spheresBadge: document.getElementById('spheres-badge'),
  dilemmaInput: document.getElementById('dilemma-input'),
  skinPills: document.getElementById('skin-pills'),
  judgeToggle: document.getElementById('judge-toggle'),
  submitBtn: document.getElementById('submit-btn'),
  loader: document.getElementById('loader'),
  resultsSection: document.getElementById('results-section'),
  angelText: document.getElementById('angel-text'),
  demonText: document.getElementById('demon-text'),
  judgeCard: document.getElementById('judge-card'),
  judgeText: document.getElementById('judge-text'),
  chooseAngelBtn: document.getElementById('choose-angel-btn'),
  chooseDemonBtn: document.getElementById('choose-demon-btn'),
  historyList: document.getElementById('history-list'),
  shopModal: document.getElementById('shop-modal'),
  closeShopBtn: document.getElementById('close-shop-btn')
};

// -----------------------------------------------------------------------------
// РАСЧЕТ И ОТРИСОВКА КАРМЫ
// -----------------------------------------------------------------------------
function updateKarmaBar(angel = state.karmaAngel, demon = state.karmaDemon) {
  state.karmaAngel = angel;
  state.karmaDemon = demon;
  const total = angel + demon;

  let angelPct = 50;
  let demonPct = 50;

  if (total > 0) {
    angelPct = Math.round((angel / total) * 100);
    demonPct = 100 - angelPct;
  }

  el.angelPercent.textContent = `${angelPct}%`;
  el.demonPercent.textContent = `${demonPct}%`;
  el.karmaBarFill.style.width = `${angelPct}%`;
}

function updateSpheres(count) {
  state.judgeSpheres = count;
  el.spheresCount.textContent = count;
}

// -----------------------------------------------------------------------------
// ОТРИСОВКА СКИНОВ И ИСТОРИИ
// -----------------------------------------------------------------------------
function renderSkins() {
  const pills = el.skinPills.querySelectorAll('.skin-pill');
  pills.forEach((pill) => {
    const skinName = pill.dataset.skin;
    const isUnlocked = state.unlockedSkins.includes(skinName);

    if (isUnlocked) {
      pill.classList.remove('locked');
      if (skinName === 'office') pill.textContent = '👔 Офис';
      if (skinName === 'gopnik') pill.textContent = '🧢 Гопник';
      if (skinName === 'classic') pill.textContent = '🔘 Классика';
    } else {
      pill.classList.add('locked');
    }

    if (skinName === state.selectedSkin) {
      pill.classList.add('active');
    } else {
      pill.classList.remove('active');
    }
  });
}

function renderHistory(historyItems = []) {
  if (!historyItems || historyItems.length === 0) {
    el.historyList.innerHTML = '<p class="history-empty">Дилемм пока нет. Задай свой первый вопрос!</p>';
    return;
  }

  el.historyList.innerHTML = '';
  historyItems.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'history-item';

    let sideLabel = '⏳ Не решено';
    let sideClass = '';
    if (item.chosen_side === 'angel') {
      sideLabel = '🕊 Ангел';
      sideClass = 'angel';
    } else if (item.chosen_side === 'demon') {
      sideLabel = '🔥 Демон';
      sideClass = 'demon';
    }

    const dateStr = item.created_at ? item.created_at.slice(0, 16).replace('T', ' ') : '';

    const topRow = document.createElement('div');
    topRow.className = 'history-item-top';

    const dateSpan = document.createElement('span');
    dateSpan.textContent = dateStr;

    const sideSpan = document.createElement('span');
    sideSpan.className = `history-side-tag ${sideClass}`;
    sideSpan.textContent = sideLabel;

    topRow.appendChild(dateSpan);
    topRow.appendChild(sideSpan);

    const questionP = document.createElement('p');
    questionP.className = 'history-item-question';
    questionP.textContent = item.text;

    card.appendChild(topRow);
    card.appendChild(questionP);
    el.historyList.appendChild(card);
  });
}

// -----------------------------------------------------------------------------
// ЗАГРУЗКА ПРОФИЛЯ ПРИ СТАРТЕ
// -----------------------------------------------------------------------------
async function loadProfile() {
  try {
    const res = await fetch('/api/me', {
      method: 'GET',
      headers: getHeaders()
    });

    if (!res.ok) {
      throw new Error(`Ошибка загрузки: ${res.status}`);
    }

    const data = await res.json();
    if (data.user) {
      updateKarmaBar(data.user.karma_angel, data.user.karma_demon);
      updateSpheres(data.user.judge_spheres);
      state.unlockedSkins = data.user.unlocked_skins || ['classic'];
      renderSkins();
    }
    if (data.history) {
      renderHistory(data.history);
    }
  } catch (err) {
    console.error('Ошибка получения профиля:', err);
  }
}

// -----------------------------------------------------------------------------
// ВЫБОР СКИНА
// -----------------------------------------------------------------------------
el.skinPills.addEventListener('click', (e) => {
  const pill = e.target.closest('.skin-pill');
  if (!pill) return;

  const skinName = pill.dataset.skin;
  if (!state.unlockedSkins.includes(skinName)) {
    triggerHaptic('medium');
    openShopModal();
    return;
  }

  triggerHaptic('light');
  state.selectedSkin = skinName;
  renderSkins();
});

// -----------------------------------------------------------------------------
// ОТПРАВКА ДИЛЕММЫ НА РАССУЖДЕНИЕ
// -----------------------------------------------------------------------------
el.submitBtn.addEventListener('click', async () => {
  const text = el.dilemmaInput.value.trim();

  if (text.length < 3) {
    triggerHaptic('error');
    alert('Опиши дилемму подробнее (минимум 3 символа).');
    el.dilemmaInput.focus();
    return;
  }

  const useJudge = el.judgeToggle.checked;
  if (useJudge && state.judgeSpheres < 1) {
    triggerHaptic('error');
    alert('Недостаточно сфер Судьи! Пополни баланс в магазине.');
    openShopModal();
    return;
  }

  // Переводим UI в режим загрузки
  triggerHaptic('medium');
  el.submitBtn.disabled = true;
  el.loader.classList.remove('hidden');
  el.resultsSection.classList.add('hidden');

  try {
    const res = await fetch('/api/dilemma', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        text: text,
        skin: state.selectedSkin,
        use_judge: useJudge
      })
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || 'Не удалось получить ответ сущностей');
    }

    const data = await res.json();
    state.currentDilemmaId = data.id;

    if (data.judge_spheres !== undefined) {
      updateSpheres(data.judge_spheres);
    }

    // Заполняем карточки ответов
    el.angelText.textContent = data.angel_answer;
    el.demonText.textContent = data.demon_answer;

    // Сбрасываем кнопки выбора
    el.chooseAngelBtn.disabled = false;
    el.chooseAngelBtn.textContent = '🕊 Послушать Ангела';
    el.chooseDemonBtn.disabled = false;
    el.chooseDemonBtn.textContent = '🔥 Сделать как Демон';

    // Карточка Судьи
    if (data.judge_answer) {
      el.judgeText.textContent = data.judge_answer;
      el.judgeCard.classList.remove('hidden');
    } else {
      el.judgeCard.classList.add('hidden');
    }

    triggerHaptic('success');
    el.resultsSection.classList.remove('hidden');

    // Плавный скролл к результатам
    el.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Обновляем список истории
    loadProfile();
  } catch (err) {
    triggerHaptic('error');
    console.error('Ошибка дилеммы:', err);
    alert(err.message || 'Произошла непредвиденная ошибка при генерации.');
  } finally {
    el.loader.classList.add('hidden');
    el.submitBtn.disabled = false;
  }
});

// -----------------------------------------------------------------------------
// ВЫБОР СТОРОНЫ (ГОЛОСОВАНИЕ)
// -----------------------------------------------------------------------------
async function handleChoice(side) {
  if (!state.currentDilemmaId) return;

  triggerHaptic('heavy');
  el.chooseAngelBtn.disabled = true;
  el.chooseDemonBtn.disabled = true;

  if (side === 'angel') {
    el.chooseAngelBtn.textContent = '✔ Выбор сделан';
  } else {
    el.chooseDemonBtn.textContent = '✔ Выбор сделан';
  }

  try {
    const res = await fetch('/api/choose', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        dilemma_id: state.currentDilemmaId,
        side: side
      })
    });

    if (!res.ok) {
      throw new Error('Не удалось зафиксировать выбор');
    }

    const data = await res.json();
    if (data.karma) {
      updateKarmaBar(data.karma.karma_angel, data.karma.karma_demon);
    }
    triggerHaptic('success');
    loadProfile();
  } catch (err) {
    triggerHaptic('error');
    console.error('Ошибка фиксации выбора:', err);
  }
}

el.chooseAngelBtn.addEventListener('click', () => handleChoice('angel'));
el.chooseDemonBtn.addEventListener('click', () => handleChoice('demon'));

// -----------------------------------------------------------------------------
// МАГАЗИН И МОДАЛЬНАЯ ШТОРКА
// -----------------------------------------------------------------------------
function openShopModal() {
  triggerHaptic('light');
  el.shopModal.classList.remove('hidden');
}

function closeShopModal() {
  el.shopModal.classList.add('hidden');
}

el.spheresBadge.addEventListener('click', openShopModal);
el.closeShopBtn.addEventListener('click', closeShopModal);

el.shopModal.addEventListener('click', (e) => {
  if (e.target === el.shopModal) {
    closeShopModal();
  }
});

// Обработка клика по покупке за Telegram Stars
el.shopModal.querySelectorAll('.buy-btn').forEach((btn) => {
  btn.addEventListener('click', async () => {
    triggerHaptic('medium');
    const item = btn.dataset.item;
    btn.disabled = true;

    try {
      const res = await fetch('/api/create-invoice', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ item })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Не удалось сформировать счет на оплату');
      }

      const data = await res.json();
      if (!data.invoice_link) {
        throw new Error('Ссылка на счет не получена');
      }

      // Открываем нативное окно оплаты Telegram Stars
      if (tg?.openInvoice) {
        tg.openInvoice(data.invoice_link, (status) => {
          if (status === 'paid') {
            triggerHaptic('success');
            if (tg?.showAlert) {
              tg.showAlert('Оплата прошла успешно! Баланс обновлен.');
            }
            loadProfile();
            closeShopModal();
          } else if (status === 'failed') {
            triggerHaptic('error');
            if (tg?.showAlert) {
              tg.showAlert('Оплата не была завершена.');
            }
          }
        });
      } else {
        window.open(data.invoice_link, '_blank');
      }
    } catch (err) {
      triggerHaptic('error');
      console.error('Ошибка создания инвойса:', err);
      if (tg?.showAlert) {
        tg.showAlert(err.message || 'Ошибка при открытии счета');
      } else {
        alert(err.message || 'Ошибка при открытии счета');
      }
    } finally {
      btn.disabled = false;
    }
  });
});

// Запуск при старте
document.addEventListener('DOMContentLoaded', () => {
  loadProfile();
});
