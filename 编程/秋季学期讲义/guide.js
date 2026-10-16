(function(){'use strict';
const $=s=>document.querySelector(s),$$=s=>Array.from(document.querySelectorAll(s)),config=JSON.parse($('#guide-config').textContent),key=config.key;
let state={notes:{},stages:{}},all=false;
const validStages=['','hand','help','independent','transfer'];
function clean(input){const output={notes:{},stages:{}};if(!input||typeof input!=='object')return output;for(let i=1;i<=config.count;i++){if(typeof input.notes?.[i]==='string')output.notes[i]=input.notes[i].slice(0,50000);if(validStages.includes(input.stages?.[i]))output.stages[i]=input.stages[i];}return output;}
let loadFailed=false;
try{const raw=localStorage.getItem(key);if(raw)state=clean(JSON.parse(raw));}catch(e){loadFailed=true;}
function status(t){$('#save-status').textContent=t;}
function progress(){const n=Object.values(state.stages).filter(x=>x==='independent'||x==='transfer').length;$('#progress-fill').style.width=`${n/config.count*100}%`;$('#progress-label').textContent=`自评独立完成或迁移：${n} / ${config.count} 站`;}
function save(){try{localStorage.setItem(key,JSON.stringify(state));status('笔记已保存在当前浏览器；换设备前请导出。');}catch(e){status('此浏览器无法保存笔记，请用“导出笔记”备份。');}progress();}
function apply(){for(let i=1;i<=config.count;i++){$(`#note-${i}`).value=state.notes[i]||'';$(`#stage-${i}`).value=state.stages[i]||'';}progress();}
function fitAnchorOffset(){document.documentElement.style.scrollPaddingTop=($('.toolbar').getBoundingClientRect().height+20)+'px';}
fitAnchorOffset();new ResizeObserver(fitAnchorOffset).observe($('.toolbar'));
apply();if(loadFailed)status('旧笔记无法读取，请先导出当前草稿或导入备份；不要依赖自动保存。');
$$('[data-note]').forEach(e=>e.addEventListener('input',()=>{state.notes[e.dataset.note]=e.value;save();}));
$$('[data-stage]').forEach(e=>e.addEventListener('change',()=>{state.stages[e.dataset.stage]=e.value;save();}));
function go(){let id=location.hash.slice(1)||'home';if(!document.getElementById(id)||!/^home$|^lesson-\d+$/.test(id))id='home';$$('.lesson,#home').forEach(e=>e.hidden=e.id!==id);$$('.toc a').forEach(e=>e.classList.toggle('active',e.getAttribute('href')==='#'+id));document.body.classList.remove('nav-open');$('#menu').setAttribute('aria-expanded','false');if(!all){window.scrollTo(0,0);requestAnimationFrame(()=>{fitAnchorOffset();window.scrollTo(0,0);});}}
window.addEventListener('hashchange',go);go();
$('#menu').addEventListener('click',()=>{const open=document.body.classList.toggle('nav-open');$('#menu').setAttribute('aria-expanded',String(open));});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.body.classList.remove('nav-open');$('#menu').setAttribute('aria-expanded','false');}});
$('#all').addEventListener('click',()=>{all=!all;document.body.classList.toggle('all-mode',all);$('#all').textContent=all?'恢复分站阅读':'展开全文';if(!all)go();});
function preparePrint(){$$('.journal').forEach(e=>{e.querySelector('.print-note').textContent=e.querySelector('textarea').value||'我的手推与反思：\n\n\n';e.querySelector('.print-stage').textContent='自评：'+e.querySelector('select').selectedOptions[0].textContent;});}
window.addEventListener('beforeprint',preparePrint);$('#print').addEventListener('click',()=>{preparePrint();window.print();});
$('#export').addEventListener('click',()=>{const data={type:key,version:1,exportedAt:new Date().toISOString(),...state};const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=config.title+'-学习笔记.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status('已导出笔记；反思与自评保留你的原记录。');});
$('#import').addEventListener('click',()=>$('#import-file').click());
$('#import-file').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>5e6)throw Error('文件过大');const raw=JSON.parse(await file.text());if(raw.type!==key)throw Error('不是这份讲义的笔记');const incoming=clean(raw);for(let i=1;i<=config.count;i++){const a=state.notes[i]||'',b=incoming.notes[i]||'';if(b&&!a)state.notes[i]=b;else if(b&&a!==b&&!a.includes(b))state.notes[i]=a+'\n\n—— 导入的另一份记录 ——\n'+b;if(!state.stages[i]&&incoming.stages[i])state.stages[i]=incoming.stages[i];}apply();save();status('导入完成；冲突笔记两份保留，已有自评优先。');}catch(err){status('未导入：'+err.message+'。原笔记保留。');}e.target.value='';});
const M=window.HandoutModels;
function tiles(a,start=0,active=[],range=[]){return '<div class="tiles">'+a.map((x,i)=>`<div class="tile ${active.includes(i+start)?'active':''} ${range.includes(i+start)?'in-range':''}"><small>${i+start}</small>${x===null?'·':String(x)}</div>`).join('')+'</div>';}
function mount(el,title,intro,options,make,render){el.innerHTML=`<h3>${title}</h3><p>${intro}</p>`+(options?`<label>情境 <select class="lab-select">${options.map((o,i)=>`<option value="${i}">${o}</option>`).join('')}</select></label>`:'')+'<div class="lab-controls"><button class="prev" type="button">上一步</button><button class="next primary" type="button">下一步</button><button class="reset" type="button">从头观察</button><span class="step"></span></div><div class="lab-view"></div><p class="event" aria-live="polite"></p>';
 let index=0,choice=0,steps=make(0);function draw(){el.querySelector('.lab-view').innerHTML=render(steps[index],choice);el.querySelector('.event').textContent=steps[index].text;el.querySelector('.step').textContent=`${index} / ${steps.length-1} 步`;el.querySelector('.prev').disabled=index===0;el.querySelector('.next').disabled=index===steps.length-1;}el.querySelector('.prev').onclick=()=>{index--;draw();};el.querySelector('.next').onclick=()=>{index++;draw();};el.querySelector('.reset').onclick=()=>{index=0;draw();};const select=el.querySelector('select');if(select)select.onchange=()=>{choice=+select.value;steps=make(choice);index=0;draw();};draw();}
$$('[data-lab]').forEach(el=>{switch(el.dataset.lab){
case 'prefix':{const queries=[[2,4],[1,5],[5,5]];mount(el,'实验 · 累计表留下中间一段','原数组 [3,1,4,1,5]；每次只登记一格，最后再查询。',['第 2～4 项','整个区间','最后一项'],c=>M.prefix([3,1,4,1,5],...queries[c]),(s,c)=>'<p>原数组（编号从 1 开始）</p>'+tiles([3,1,4,1,5],1,[],Array.from({length:queries[c][1]-queries[c][0]+1},(_,i)=>i+queries[c][0]))+'<p>累计表 S（含第 0 格）</p>'+tiles(s.s,0,[s.at]));break;}
case 'difference':{const options=[[[2,4,3]],[[2,4,3],[3,5,-1]],[[1,5,2]]];mount(el,'实验 · 从端点标记恢复整排增量','先标记全部修改，再逐项恢复。保留第 6 格，只用于停止边界，不输出到答案。',['第 2～4 格加 3','重叠修改：再把 3～5 格减 1','全段加 2'],c=>M.difference(5,options[c]),s=>'<p>差分 d[1…6]：只记录变化</p>'+tiles(s.d.slice(1),1,[s.at])+'<p>恢复后的 5 格</p>'+tiles(s.a,1,[s.at]));break;}
case 'pair':{const targets=[8,20,2];mount(el,'实验 · 每次移动都要有理由','数组已升序排列为 [1,2,4,6,9]，橙色边框标出当前端点。',['目标和 8','目标和 20','目标和 2'],c=>M.pair([1,2,4,6,9],targets[c]),s=>tiles([1,2,4,6,9],0,[s.l,s.r])+'<p>l='+s.l+'；r='+s.r+'；只有 l&lt;r 才能用两个不同位置。</p>');break;}
case 'window':{const arrays=[[2,1,3,1,1],[0,0,0],[5,-4]],limits=[4,0,1];mount(el,'实验 · 加入、收缩、记录是三个动作','先手推，再点下一步。第三个情境故意违反非负前提，用来观察漏解。',['非负数组，K=4','全零，K=0','反例：含负数，K=1'],c=>M.windowSteps(arrays[c],limits[c]),(s,c)=>tiles(arrays[c],0,[s.l,s.r],Array.from({length:Math.max(0,s.r-s.l+1)},(_,i)=>s.l+i))+`<p>窗口 [${s.l},${s.r}] · sum=${s.sum} · 当前记录 best=${s.best}</p>`+(c===2?'<p>此规则在本例会漏掉完整两项；用全部子段枚举核验。</p>':''));break;}
case 'containers':mount(el,'实验 · 同样的操作，不同的处理顺序','固定操作：进 A、进 B、查看、取出、进 C、取出、取出、再取出。',['栈：后进先出','队列：先进先出'],c=>M.containers(c===0?'stack':'queue'),(s,c)=>'<p>'+(c===0?'左边是栈底，右边是栈顶。':'左边是队首，右边是队尾。')+'</p>'+(s.q.length?tiles(s.q,0,[c===0?s.q.length-1:0]):'<p>当前为空</p>')+'<p>当前元素数：'+s.q.length+'</p>');break;
}});
})();
