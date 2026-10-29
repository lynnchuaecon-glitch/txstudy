(() => {
  'use strict';
  const $ = (selector) => document.querySelector(selector);
  const books = window.SHELF_BOOKS;
  const esc = (value) => String(value).replace(/[&<>"']/g,(c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const topics = [...new Set(books.map(b=>b.topic))];
  const dynasties = [...new Set(books.map(b=>b.dynasty))];
  const params = new URLSearchParams(location.search);
  let topic = topics.includes(params.get('topic')) ? params.get('topic') : 'all';
  $('#search').value = params.get('q') || '';
  $('#dynasty').innerHTML += dynasties.map(d=>`<option value="${esc(d)}">${esc(d)}</option>`).join('');
  $('#dynasty').value = dynasties.includes(params.get('dynasty')) ? params.get('dynasty') : 'all';
  $('#library-total').textContent = `已有 ${books.length} 册 · 持续添新`;
  $('#hero-image').src = books[0].thumbnail;
  $('#topic-filters').innerHTML = ['all',...topics].map(t=>`<button type="button" data-topic="${esc(t)}" aria-pressed="${t===topic}">${t==='all'?'全部故事':esc(t)}</button>`).join('');
  function render(updateURL=true) {
    const query = $('#search').value.trim().toLowerCase();
    const dynasty = $('#dynasty').value;
    const filtered = books.filter(b=>(topic==='all'||b.topic===topic)&&(dynasty==='all'||b.dynasty===dynasty)&&(!query||[b.title,b.author,b.dynasty,b.topic,b.description,...b.keywords].join(' ').toLowerCase().includes(query)));
    $('#result-count').textContent = `显示 ${filtered.length} / ${books.length} 册`;
    $('#reset').hidden = !query && topic==='all' && dynasty==='all';
    $('#empty').hidden = filtered.length>0;
    $('#books').classList.toggle('single',filtered.length===1);
    $('#books').innerHTML = filtered.map(b=>`<a class="book-card" href="${esc(b.href)}" aria-label="阅读《${esc(b.title)}》"><div class="book-heading"><h3><span class="number">${String(b.order).padStart(2,'0')}</span>${esc(b.title)}</h3><div class="book-author"><span>${esc(b.author)}</span>〔${esc(b.dynasty)}〕</div></div><div class="book-art"><img src="${b.thumbnail}" width="720" height="480" loading="lazy" alt="《${esc(b.title)}》水墨封面"><span class="book-seal">${esc(b.topic)}</span></div><div class="book-copy"><p class="excerpt">${esc(b.excerpt)}</p><p class="description">${esc(b.description)}</p><div class="book-meta"><span>${b.sceneCount} 幕水墨 · 原文 · 字词</span><b>翻开这一本 →</b></div></div></a>`).join('');
    document.querySelectorAll('[data-topic]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.topic===topic)));
    if(updateURL){const p=new URLSearchParams();if(query)p.set('q',$('#search').value.trim());if(topic!=='all')p.set('topic',topic);if(dynasty!=='all')p.set('dynasty',dynasty);try{history.replaceState(null,'',location.pathname+(p.size?'?'+p:'')+location.hash);}catch(_) {}}
  }
  $('#topic-filters').addEventListener('click',e=>{const button=e.target.closest('[data-topic]');if(button){topic=button.dataset.topic;render();}});
  $('#search').addEventListener('input',()=>render());
  $('#dynasty').addEventListener('change',()=>render());
  $('#reset').addEventListener('click',()=>{$('#search').value='';$('#dynasty').value='all';topic='all';render();$('#search').focus();});
  $('#search-form').addEventListener('submit',e=>{e.preventDefault();render();});
  render(false);
})();
