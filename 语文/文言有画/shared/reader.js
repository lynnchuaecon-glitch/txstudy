(() => {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => [...document.querySelectorAll(s)];
  const art = (id) => window.BOOK_IMAGES ? window.BOOK_IMAGES[id] : `assets/${id}.jpg`;
  const storageKey = `wenyan-youhua.${BOOK.slug}.v1`;
  const total = BOOK.scenes.length;
  const defaults = { pinyin: true, large: false, scene: 0, line: '', thought: '' };
  let state = { ...defaults };
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || '{}');
    if (saved && typeof saved === 'object') {
      for (const key of Object.keys(defaults)) if (typeof saved[key] === typeof defaults[key]) state[key] = saved[key];
    }
  } catch (_) { /* File and privacy modes can block browser storage. */ }
  state.scene = Number.isInteger(state.scene) && state.scene >= 0 && state.scene < total ? state.scene : 0;
  let currentScene = 0;
  let currentView = 'cover';
  const esc = (value) => String(value).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const displayWord = (key) => BOOK.words[key][2] || key;
  const plain = (text) => text.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, key, label) => label || displayWord(key));
  const keysIn = (text) => [...text.matchAll(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g)].map((m) => m[1]);
  const annotated = (text) => text.replace(/([“‘（《「『]*)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]([，。；：！？、”’）〉》」』]*)/g, (_, before, key, label, after) => {
    const [pronunciation] = BOOK.words[key];
    return `<span class="annotated-unit">${esc(before)}<button type="button" class="word" data-word="${esc(key)}" aria-label="${esc(label || displayWord(key))}：查看拼音和释义"><ruby>${esc(label || displayWord(key))}<rt>${esc(pronunciation)}</rt></ruby></button>${esc(after)}</span>`;
  });
  const persist = () => {
    try { localStorage.setItem(storageKey, JSON.stringify(state)); return true; } catch (_) { return false; }
  };
  const contexts = {};
  BOOK.scenes.forEach((scene, index) => keysIn(scene.text).forEach((key) => {
    if (!contexts[key]) contexts[key] = [];
    if (!contexts[key].includes(index)) contexts[key].push(index);
  }));
  function applyPreferences() {
    document.body.classList.toggle('no-pinyin', !state.pinyin);
    document.body.classList.toggle('large-text', state.large);
    $$('.pinyin-toggle').forEach((b) => { b.setAttribute('aria-pressed', String(state.pinyin)); b.textContent = `注音 · ${state.pinyin ? '开' : '关'}`; });
    $$('.size-toggle').forEach((b) => { b.setAttribute('aria-pressed', String(state.large)); b.textContent = state.large ? '标准字' : '大字'; });
  }
  $('#scene-cards').innerHTML = BOOK.scenes.map((s, i) => `<a href="#scene-${i+1}" class="scene-card"><img src="${art(s.id)}" alt="${esc(s.alt)}" width="1536" height="1024" loading="lazy"><p><span>${s.id}</span>${s.short}</p></a>`).join('');
  $('#scene-selector').innerHTML = BOOK.scenes.map((s, i) => `<a href="#scene-${i+1}">${s.id} ${s.short}</a>`).join('');
  $('#page-dots').innerHTML = BOOK.scenes.map((s, i) => `<a href="#scene-${i+1}" aria-label="第${i+1}幕：${s.short}"></a>`).join('');
  $('#word-scene').innerHTML += BOOK.scenes.map((s,i) => `<option value="${i}">${s.id} ${s.short}</option>`).join('');
  const textGroups = BOOK.textGroups;
  $('#fulltext-body').innerHTML = textGroups.map((group) => {
    const appendix = Number.isInteger(BOOK.appendixScene) && group.includes(BOOK.appendixScene);
    return `${appendix ? `<h2 class="appendix-heading">${esc(BOOK.appendixTitle || '附读')}</h2>` : ''}<p class="original${appendix ? ' appendix-poem' : ''}">${group.map((i) => annotated(BOOK.scenes[i].text)).join('')}</p>`;
  }).join('') + (BOOK.colophon ? `<p class="original colophon">${esc(BOOK.colophon)}</p>` : '');

  function renderScene(index) {
    currentScene = index;
    state.scene = index;
    persist();
    const scene = BOOK.scenes[index];
    $('#scene-kicker').textContent = `${BOOK.title} · 第 ${scene.id} 幕 / 共 ${total} 幕`;
    $('#scene-title').textContent = scene.title;
    $('#scene-image').src = art(scene.id);
    $('#scene-image').alt = scene.alt;
    $('#art-button').setAttribute('aria-label', `放大查看：${scene.short}`);
    $('#picture-number').textContent = scene.id;
    $('#picture-caption').textContent = scene.place;
    $('#scene-question').textContent = scene.look;
    $('#scene-text').innerHTML = annotated(scene.text) + (index === total - 1 && BOOK.colophon ? `<br><small class="colophon">${esc(BOOK.colophon)}</small>` : '');
    $('#scene-text').classList.toggle('appendix-poem', index === BOOK.appendixScene);
    $('#focus-words').innerHTML = scene.focus.map((key) => `<button type="button" data-word="${esc(key)}">${esc(displayWord(key))} · ${esc(BOOK.words[key][0])}</button>`).join('');
    $('#scene-translation').textContent = scene.translation;
    $('#scene-beauty').textContent = scene.beauty;
    $('#scene-parent').textContent = scene.parent;
    $$('.reading-folds details').forEach((d) => { d.open = false; });
    $('#prev-page').href = index === 0 ? '#cover' : `#scene-${index}`;
    $('#prev-page').textContent = index === 0 ? '← 封面' : '← 上一幕';
    $('#next-page').href = index === total-1 ? '#after' : `#scene-${index+2}`;
    $('#next-page').textContent = index === total-1 ? '留下余韵 →' : '下一幕 →';
    $('#page-position').textContent = `${scene.id} / ${String(total).padStart(2,'0')}`;
    $$('#page-dots a, #scene-selector a').forEach((a) => {
      if (a.getAttribute('href') === `#scene-${index+1}`) a.setAttribute('aria-current','page');
      else a.removeAttribute('aria-current');
    });
    $('#scene-selector').hidden = true;
    $('#contents-toggle').setAttribute('aria-expanded','false');
  }
  function renderWords() {
    const query = $('#word-search').value.trim().toLowerCase();
    const sceneFilter = $('#word-scene').value;
    const simplify = (v) => v.normalize('NFD').replace(/[\u0300-\u036f]/g,'');
    const entries = Object.entries(BOOK.words).filter(([key, data]) => {
      const matchScene = sceneFilter === 'all' || contexts[key].includes(Number(sceneFilter));
      const searchable = `${displayWord(key)} ${data[0]} ${data[1]}`.toLowerCase();
      return matchScene && (!query || searchable.includes(query) || simplify(searchable).includes(simplify(query)));
    });
    $('#word-count').textContent = `${entries.length} 则字词 · 拼音、意思与原文相伴`;
    $('#word-list').innerHTML = entries.length ? entries.map(([key, data]) => {
      const index = contexts[key].find((i) => sceneFilter === 'all' || i === Number(sceneFilter));
      const label = BOOK.contextLabels?.[key] ? `（${BOOK.contextLabels[key]}）` : '';
      return `<article class="word-entry"><header><h2>${esc(displayWord(key))}</h2><small>${esc(data[0])}</small></header><p>${esc(data[1])}</p>${label ? `<p class="word-use">${label}</p>` : ''}<a href="#scene-${index+1}">回到第 ${BOOK.scenes[index].id} 幕 · ${BOOK.scenes[index].short} →</a></article>`;
    }).join('') : '<p class="empty-state">暂时没有找到。可以换一个字，或选择“全篇”再试试。</p>';
  }
  function showWord(key) {
    const word = BOOK.words[key];
    if (!word) return;
    $('#word-title').textContent = displayWord(key);
    $('#word-pronunciation').textContent = word[0];
    $('#word-definition').textContent = word[1];
    let index = currentView === 'reader' && contexts[key].includes(currentScene) ? currentScene : contexts[key][0];
    const sentence = BOOK.scenes[index].text.split(/(?<=[。！？])/).find((s) => keysIn(s).includes(key));
    $('#word-context').textContent = '放回原句：' + plain(sentence || BOOK.scenes[index].text);
    $('#word-dialog').showModal();
  }
  function route(initial = false) {
    const hash = location.hash.slice(1) || 'cover';
    if (hash === 'main') { $('#main').focus(); return; }
    const matched = /^scene-([1-9]\d*)$/.exec(hash);
    const sceneMatch = matched && Number(matched[1]) <= total ? matched : null;
    const views = {cover:'cover',contents:'cover',text:'fulltext',words:'glossary',after:'after',sources:'sources'};
    const view = sceneMatch ? 'reader' : (views[hash] || 'cover');
    currentView = view;
    $$('.view').forEach((section) => { section.hidden = section.id !== view; });
    const activeNav = sceneMatch ? 'scene' : hash;
    $$('.masthead nav a').forEach((a) => {
      if (a.dataset.nav === activeNav) a.setAttribute('aria-current','page');
      else a.removeAttribute('aria-current');
    });
    if (sceneMatch) renderScene(Number(sceneMatch[1])-1);
    if (view === 'glossary') renderWords();
    document.title = sceneMatch ? `${BOOK.scenes[currentScene].short} · ${BOOK.title} · 文言有画` : `${BOOK.title} · 文言有画`;
    if (hash === 'contents') $('#contents').scrollIntoView({behavior:'auto'});
    else if (!initial) {
      window.scrollTo({top:0,behavior:'instant'});
      const heading = $(`#${view} h1`);
      if (heading) { heading.setAttribute('tabindex','-1'); heading.focus({preventScroll:true}); }
    }
  }
  document.addEventListener('click',(event) => {
    const wordButton = event.target.closest('[data-word]');
    if (wordButton) showWord(wordButton.dataset.word);
  });
  $$('.pinyin-toggle').forEach((b) => b.addEventListener('click',() => { state.pinyin = !state.pinyin; applyPreferences(); persist(); }));
  $$('.size-toggle').forEach((b) => b.addEventListener('click',() => { state.large = !state.large; applyPreferences(); persist(); }));
  $('#contents-toggle').setAttribute('aria-controls','scene-selector');
  $('#contents-toggle').setAttribute('aria-expanded','false');
  $('#contents-toggle').addEventListener('click',() => { const nav = $('#scene-selector'); nav.hidden = !nav.hidden; $('#contents-toggle').setAttribute('aria-expanded',String(!nav.hidden)); });
  $('#word-search').addEventListener('input', renderWords);
  $('#word-scene').addEventListener('change', renderWords);
  $('#print-button').addEventListener('click',() => window.print());
  $('#art-button').addEventListener('click',() => {
    const scene = BOOK.scenes[currentScene];
    $('#large-art').src = art(scene.id);
    $('#large-art').alt = scene.alt;
    $('#large-art-caption').textContent = `第${scene.id}幕 · ${scene.short} — ${scene.place}`;
    $('#art-dialog').showModal();
  });
  $$('dialog').forEach((dialog) => {
    dialog.querySelector('.dialog-close').addEventListener('click',() => dialog.close());
    dialog.addEventListener('click',(e) => { if (e.target !== dialog) return; const r=dialog.getBoundingClientRect(); if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom) dialog.close(); });
  });
  document.addEventListener('keydown',(e) => {
    if(currentView !== 'reader' || $('dialog[open]') || e.ctrlKey || e.metaKey || e.altKey || e.shiftKey || /INPUT|TEXTAREA|SELECT|BUTTON/.test(e.target.tagName) || e.target.isContentEditable) return;
    if(e.key === 'ArrowLeft'){ e.preventDefault(); location.hash = currentScene === 0 ? 'cover' : `scene-${currentScene}`; }
    if(e.key === 'ArrowRight'){ e.preventDefault(); location.hash = currentScene === total-1 ? 'after' : `scene-${currentScene+2}`; }
  });
  $('#my-line').value = state.line;
  $('#my-thought').value = state.thought;
  let saveTimer;
  const saveNotes = () => {
    state.line = $('#my-line').value;
    state.thought = $('#my-thought').value;
    const ok = persist();
    $('#save-status').textContent = ok ? '已保存在当前浏览器。换设备前可导出一份。' : '当前浏览器无法保存，请用右侧按钮导出。';
  };
  ['#my-line','#my-thought'].forEach((id) => $(id).addEventListener('input',() => { clearTimeout(saveTimer); state.line=$('#my-line').value;state.thought=$('#my-thought').value;$('#save-status').textContent='正在保存…';saveTimer=setTimeout(saveNotes,250); }));
  window.addEventListener('pagehide',saveNotes);
  $('#export-note').addEventListener('click',() => {
    saveNotes();
    const content = `文言有画 · ${BOOK.title}\n\n我想留住的一句原文\n${state.line}\n\n这句话让我看见、想到，或疑惑的是\n${state.thought}\n`;
    const url = URL.createObjectURL(new Blob(['\ufeff'+content],{type:'text/plain;charset=utf-8'}));
    const link = document.createElement('a'); link.href=url;link.download=`${BOOK.title}-我自己的话.txt`;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  if(state.scene>0){const start=$('.cover-copy .primary');start.href=`#scene-${state.scene+1}`;start.innerHTML=`续读第 ${state.scene+1} 幕 <span aria-hidden="true">→</span>`;}
  const catalog = window.WENYAN_LIBRARY || [];
  const bookIndex = catalog.findIndex(book => book.id === BOOK.slug);
  const relativeLink = (book) => '../' + encodeURIComponent(book.directory) + '/' + encodeURIComponent(book.file);
  const collection = document.createElement('nav');
  collection.className = 'collection-nav';
  collection.setAttribute('aria-label','系列书架导航');
  collection.innerHTML = `<a href="../打开书架.html">← 返回书架</a><span>文言有画 · ${esc(BOOK.volume)}</span><div>${bookIndex>0 ? `<a href="${relativeLink(catalog[bookIndex-1])}">上一篇 · ${esc(catalog[bookIndex-1].title)}</a>` : ''}${bookIndex>=0 && bookIndex<catalog.length-1 ? `<a href="${relativeLink(catalog[bookIndex+1])}">下一篇 · ${esc(catalog[bookIndex+1].title)} →</a>` : ''}</div>`;
  $('.masthead').insertAdjacentElement('afterend',collection);
  const nextBook = document.createElement('div');
  nextBook.className = 'collection-end';
  nextBook.innerHTML = `<span>这一册读到这里，愿意时再选一篇。</span><a href="../打开书架.html">回书架看看 →</a>`;
  $('#after .after-body').appendChild(nextBook);
  window.addEventListener('hashchange',()=>route(false));
  applyPreferences();
  renderWords();
  route(true);
})();
