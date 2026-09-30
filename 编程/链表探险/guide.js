'use strict';
const $=id=>document.getElementById(id), KEY='linked-list-adventure-v1';
let state={chapter:0,notes:{},ratings:{}}, allMode=false, persistent=true;
const ratingValues=['','revisit','explain','transfer'];
function validData(v){
 if(!v || typeof v!=='object' || Array.isArray(v))throw Error('格式不正确');
 const clean={chapter:Number.isInteger(v.chapter)&&v.chapter>=0&&v.chapter<=30?v.chapter:0,notes:{},ratings:{}};
 for(let i=1;i<=30;i++){
  if(v.notes&&typeof v.notes[i]==='string')clean.notes[i]=v.notes[i];
  if(v.ratings&&ratingValues.includes(v.ratings[i]))clean.ratings[i]=v.ratings[i];
 }
 return clean;
}
try{const raw=localStorage.getItem(KEY);if(raw)state=validData(JSON.parse(raw));}catch(e){persistent=false;}
function status(t){$('save-status').textContent=t;}
function save(){try{localStorage.setItem(KEY,JSON.stringify(state));persistent=true;status('笔记已保存在当前浏览器。建议定期导出 JSON 备份。');}catch(e){persistent=false;status('浏览器未能保存。笔记仍留在本页，请立即导出备份，勿刷新。');}}
function sync(){
 let explain=0,transfer=0;
 for(let i=1;i<=30;i++){
  $('note-'+i).value=state.notes[i]||'';$('rating-'+i).value=state.ratings[i]||'';
  $('print-note-'+i).textContent=state.notes[i]||'我的手推 / 待复盘：\n\n';
  $('print-rating-'+i).textContent={'':'未自评',revisit:'需要回访',explain:'能解释并手推',transfer:'能独立实现与迁移'}[state.ratings[i]||''];
  if(state.ratings[i]==='explain')explain++;
  if(state.ratings[i]==='transfer')transfer++;
 }
 $('progress-label').textContent=`自评：能解释 ${explain} 站 · 能迁移 ${transfer} 站 / 30`;
 $('progress-fill').style.width=(explain+transfer)/30*100+'%';
}
function show(n,scroll=true){
 if(!Number.isInteger(n)||n<0||n>30)n=0;
 state.chapter=n;$('home').hidden=n!==0;
 document.querySelectorAll('.lesson').forEach(el=>el.hidden=Number(el.dataset.lesson)!==n);
 document.querySelectorAll('[data-nav]').forEach(el=>{const on=Number(el.dataset.nav)===n;el.classList.toggle('active',on);if(on)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});
 $('crumb').textContent=n?`链表 / 第 ${String(n).padStart(2,'0')} 站 / ${$('heading-'+n).textContent}`:'链表 / 出发与路线';
 document.body.classList.remove('nav-open');$('menu').setAttribute('aria-expanded','false');
 if(scroll){if(allMode)$(n?'lesson-'+n:'home').scrollIntoView();else window.scrollTo(0,0);}
}
function navigate(n){location.hash=n?'lesson-'+n:'home';if(state.chapter===n)show(n);}
window.addEventListener('hashchange',()=>{const m=location.hash.match(/^#lesson-(\d+)$/);show(m?+m[1]:0);save();});
document.querySelectorAll('[data-go]').forEach(b=>b.addEventListener('click',()=>navigate(+b.dataset.go)));
$('all').addEventListener('click',()=>{allMode=!allMode;document.body.classList.toggle('all-mode',allMode);$('all').textContent=allMode?'返回分站阅读':'展开全讲义';if(!allMode)show(state.chapter);});
$('menu').addEventListener('click',()=>{const open=document.body.classList.toggle('nav-open');$('menu').setAttribute('aria-expanded',String(open));});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.body.classList.remove('nav-open');$('menu').setAttribute('aria-expanded','false');}});
document.querySelectorAll('[data-note]').forEach(el=>el.addEventListener('input',()=>{state.notes[el.dataset.note]=el.value;$('print-note-'+el.dataset.note).textContent=el.value||'我的手推 / 待复盘：\n\n';save();}));
document.querySelectorAll('[data-rating]').forEach(el=>el.addEventListener('change',()=>{state.ratings[el.dataset.rating]=el.value;save();sync();}));
$('export').addEventListener('click',()=>{
 const data={format:KEY,version:1,exportedAt:new Date().toISOString(),...state};
 const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));
 const a=document.createElement('a');a.href=url;a.download='链表探险笔记-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 status('已发起笔记下载。请检查浏览器下载记录；备份包含笔记与自评。');
});
$('import').addEventListener('click',()=>$('import-file').click());
$('import-file').addEventListener('change',async e=>{
 const file=e.target.files[0];if(!file)return;
 try{
  if(file.size>4000000)throw Error('文件超过 4 MB');
  const raw=JSON.parse(await file.text());if(raw.format!==KEY)throw Error('这不是本讲义导出的笔记');
  const imported=validData(raw);
  // Preserve both texts on conflicts, rather than silently replacing local work.
  for(let i=1;i<=30;i++){
   const incoming=imported.notes[i];if(incoming&&incoming!==state.notes[i])state.notes[i]=state.notes[i]?state.notes[i]+'\n\n——导入的笔记（保留原文）——\n'+incoming:incoming;
   if(!state.ratings[i]&&imported.ratings[i])state.ratings[i]=imported.ratings[i];
  }
  sync();save();status(persistent?'已合并笔记：有冲突的两份文字都保留，原有自评优先。':'已合并，但本地保存失败；请立即导出备份。');
 }catch(error){status('导入未完成：'+error.message+'。原笔记未被替换。');}finally{e.target.value='';}
});
$('print').addEventListener('click',()=>{sync();window.print();});
window.addEventListener('beforeprint',sync);
document.querySelectorAll('[data-quiz]').forEach(form=>form.addEventListener('submit',e=>{
 e.preventDefault();const id=+form.dataset.quiz,selected=form.querySelector('input:checked'),q=QUIZZES[id];
 $('quiz-feedback-'+id).textContent=selected?(+selected.value===q[2]?q[4]:q[3]):'先选一个判断，再说明理由。';
}));
function makeLab(id,title,description,controls){
 const host=$(id);host.innerHTML=`<h3>${title}</h3><p>${description}</p>${controls}<div class="event" id="${id}-event" aria-live="polite"></div><div id="${id}-view"></div>`;
}
function paragraph(host,text,cls=''){const p=document.createElement('p');p.textContent=text;p.className=cls;host.append(p);return p;}
function rows(host,headers,data){
 host.replaceChildren();const wrapper=document.createElement('div');wrapper.className='table-scroll';const table=document.createElement('table'),thead=document.createElement('thead'),tr=document.createElement('tr');
 for(const h of headers){const th=document.createElement('th');th.textContent=h;tr.append(th);}thead.append(tr);table.append(thead);const tbody=document.createElement('tbody');
 for(const row of data){const r=document.createElement('tr');for(const value of row){const td=document.createElement('td');td.textContent=value;r.append(td);}tbody.append(r);}table.append(tbody);wrapper.append(table);host.append(wrapper);
}
function drawChain(host,ids,{current=null,labels={},double=false,end='0',start='入口',cyclic=false}={}){
 const wrap=document.createElement('div');wrap.className='node-chain';
 const card=(id,label)=>{const n=document.createElement('div');n.className='node-card'+(current!==null&&id===current?' current':'');const b=document.createElement('b');b.textContent=label||String(id);n.append(b);if(Object.prototype.hasOwnProperty.call(labels,id)){const s=document.createElement('small');s.textContent=labels[id];n.append(s);}wrap.append(n);};
 const arrow=()=>{const a=document.createElement('span');a.className='arrow';a.textContent=double?'⇄':'→';a.setAttribute('aria-hidden','true');wrap.append(a);};
 card(null,start);for(const id of ids){arrow();card(id,String(id));}arrow();card(null,cyclic?'回到 '+(ids[0]??'起点'):end);host.append(wrap);
}
function fieldTable(host,headers,data){const wrap=document.createElement('div');host.append(wrap);rows(wrap,headers,data);}
makeLab('walk-lab','实验 01 / 游标跟着谁走？','桌上槽位按编号排列，队伍按 nxt 排列。黄色框标出游标；先说出下一位，再点击。',`<label>结构 <select id="w-case"><option value="normal">2→3→1，值 10、20、30</option><option value="single">单结点 7，值 8</option><option value="empty">空链</option><option value="repeat">4→1→7，值 8、5、8</option></select></label><label>任务 <select id="w-mode"><option value="walk">遍历整条链</option><option value="find">找第一个指定值</option></select></label><label>目标值 <input id="w-target" type="number" value="8" step="1" min="-100" max="100"></label><div class="controls"><button id="w-reset">重新开始</button><button id="w-step">访问当前，再走一步</button></div><p id="w-feedback" class="feedback" aria-live="polite"></p>`);
let walk;
function drawWalk(){const host=$('walk-lab-view');host.replaceChildren();const order=walkIds(walk.head,walk.next).ids;drawChain(host,order,{current:walk.done?null:walk.cur,labels:Object.fromEntries(order.map(id=>[id,'value='+walk.values[id]]))});fieldTable(host,['槽位编号','value','nxt'],Object.keys(walk.next).sort((a,b)=>a-b).map(id=>[id,walk.values[id],walk.next[id]]));paragraph(host,'已访问编号：'+(walk.visited.join(' → ')||'尚未访问'));$('walk-lab-event').textContent=walk.message;$('w-step').disabled=walk.done;}
function resetWalk(){const target=$('w-target').valueAsNumber;if(!Number.isInteger(target)||target< -100||target>100){$('w-feedback').textContent='目标值输入 −100～100 的整数。';return;}
 const configs={normal:{head:2,next:{1:0,2:3,3:1},values:{1:30,2:10,3:20}},single:{head:7,next:{7:0},values:{7:8}},empty:{head:0,next:{},values:{}},repeat:{head:4,next:{4:1,1:7,7:0},values:{4:8,1:5,7:8}}};const c=configs[$('w-case').value];walk={...c,cur:c.head,target,mode:$('w-mode').value,visited:[],done:c.head===0,message:c.head===0?'空链：不读取结点；遍历立即结束，查找返回 0。':`cur=${c.head}。先判断它存在，再读取它的值。`};$('w-feedback').textContent='先预测这一轮会访问哪个编号。';drawWalk();}
$('w-step').onclick=()=>{if(walk.done)return;const id=walk.cur;walk.visited.push(id);if(walk.mode==='find'&&walk.values[id]===walk.target){walk.done=true;walk.message=`命中第一个目标：返回编号 ${id}，不是返回数值 ${walk.target}。请说明先后依据。`;}
 else {walk.cur=walk.next[id];walk.done=walk.cur===0;walk.message=walk.done?(walk.mode==='find'?'走到 0 仍未命中：返回 0。':'走到 0：遍历结束。'):`访问 ${id} 号后，cur ← nxt[${id}] = ${walk.cur}。下一轮检查 ${walk.cur} 号。`;}drawWalk();};
$('w-reset').onclick=resetWalk;for(const id of ['w-case','w-mode','w-target'])$(id).onchange=resetWalk;resetWalk();
makeLab('insert-lab','实验 02 / 两次写入之间发生了什么？','p=1，q=2，新结点 u=3。每按一次只执行一次写入；先画出你预测的箭头。',`<label>写入方案 <select id="i-mode"><option value="safe">先让 u 保存 p 的旧后继</option><option value="unsafe">先改 p，未保存旧后继</option><option value="saved">预先保存 q，再先改 p</option></select></label><div class="controls"><button id="i-reset">重置</button><button id="i-step">执行下一次写入</button></div>`);
let insertStep=0;
function drawInsert(){const mode=$('i-mode').value,s=insertionState(mode,insertStep),host=$('insert-lab-view');host.replaceChildren();drawChain(host,s.ids,{labels:{1:'p',2:'旧 q',3:'新 u'},end:s.cycle===null?'0':'回到 '+s.cycle+'（出现环）'});fieldTable(host,['编号','nxt 当前值'],[1,2,3].map(i=>[i,s.next[i]]));paragraph(host,'从入口不可达的已分配结点：'+([1,2,3].filter(x=>!s.ids.includes(x)).join('、')||'无')+'。新 u 在接入前不可达是正常的。');for(const line of s.log)paragraph(host,line,'log');$('insert-lab-event').textContent=insertStep===0?'尚未写入。入口链为 p→q→0，u 独立。':insertStep===1?'完成第 1 次写入。第 2 次将读到哪个值？':s.cycle!==null?'出现自环，旧 q 从入口不可达。回到第一次覆盖旧信息的位置。':'两次写入完成，得到 p→u→q→0。请解释旧 q 怎样被保住。';$('i-step').disabled=insertStep>=2;}
$('i-step').onclick=()=>{if(insertStep<2)insertStep++;drawInsert();};$('i-reset').onclick=()=>{insertStep=0;drawInsert();};$('i-mode').onchange=$('i-reset').onclick;drawInsert();
makeLab('double-lab','实验 03 / 正着走、倒着走，要讲同一条队伍','H=0，T=1。新编号从 5 分配；插入目标可以是 H 或活跃结点，删除对象只能是真实活跃结点。',`<label>在谁后面 <select id="d-after"></select></label><button id="d-insert">插入一位</button><label>删除编号 <input id="d-id" type="number" value="3" min="0" max="24" step="1"></label><div class="controls"><button id="d-remove">删除指定结点</button><button id="d-reset">回到初始链</button></div><p id="d-feedback" class="feedback" aria-live="polite"></p>`);
let double=new DoubleModel(),serial=5;
function drawDouble(){const host=$('double-lab-view');host.replaceChildren();drawChain(host,double.forward(),{double:true,start:'H',end:'T'});paragraph(host,'反向：T → '+[...double.backward(),'H'].join(' → '));fieldTable(host,['结点','pre','nxt'],[0,...double.forward(),1].map(id=>[id===0?'H':id===1?'T':id,id===0?'不使用':double.prev[id],id===1?'不使用':double.next[id]]));const selected=+$('d-after').value;$('d-after').replaceChildren();for(const id of [0,...double.forward()]){const op=document.createElement('option');op.value=id;op.textContent=id===0?'H（最前面）':String(id);$('d-after').append(op);}if(selected===0||double.alive.has(selected))$('d-after').value=selected;$('double-lab-event').textContent=`活跃 ${double.alive.size} 位；双向一致性${double.check()?'通过':'失败'}。检查：每个右邻居是否认得自己的左邻居？`;$('d-insert').disabled=serial>24;}
$('d-insert').onclick=()=>{if(serial>24)return;const u=serial++;const {p,q}=double.insert(+$('d-after').value,u);$('d-feedback').textContent=`插入 ${u}：先保存 q=${q}；设置 pre[${u}]=${p}、nxt[${u}]=${q}，再让两位旧邻居指向 ${u}。`+(serial>24?'本轮槽位用完，可重置再试。':'');drawDouble();};
$('d-remove').onclick=()=>{const u=$('d-id').valueAsNumber;try{const {p,q}=double.remove(u);$('d-feedback').textContent=`删除 ${u}：nxt[${p}]=${q}，pre[${q}]=${p}。目标已离开活跃链。`;drawDouble();}catch(e){$('d-feedback').textContent=e.message;}};
$('d-reset').onclick=()=>{double=new DoubleModel();serial=5;$('d-feedback').textContent='已重建 2、3、4 三个真实结点。';drawDouble();};drawDouble();
makeLab('circle-lab','实验 04 / 报数棒交给下一位','一轮只删除一人。n 人，首轮从 1 报 1，每次数到 k 出列，剩一人即停。先在纸上标出下一位。',`<label>人数 n <input id="j-n" type="number" min="1" max="10" value="5" step="1"></label><label>报数 k <input id="j-k" type="number" min="1" max="100" value="3" step="1"></label><div class="controls"><button id="j-reset">重新围圈</button><button id="j-prev">上一轮</button><button id="j-next">下一轮出列</button></div><p id="j-feedback" class="feedback" aria-live="polite"></p>`);
let ringEvents=circleEvents(5,3),ringIndex=0;
function drawCircle(){const e=ringEvents[ringIndex],host=$('circle-lab-view');host.replaceChildren();drawChain(host,e.alive,{current:e.cur,cyclic:true,start:'本轮起点'});paragraph(host,'已经出列：'+(e.removed.join(' → ')||'无人'));$('circle-lab-event').textContent=e.text+(e.alive.length===1?` 只剩 ${e.alive[0]}，本任务停止；若继续画圆环，它仍指向自己。`:'');$('j-prev').disabled=ringIndex===0;$('j-next').disabled=ringIndex===ringEvents.length-1;}
function resetCircle(){const n=$('j-n').valueAsNumber,k=$('j-k').valueAsNumber;if(!Number.isInteger(n)||n<1||n>10||!Number.isInteger(k)||k<1||k>100){$('j-feedback').textContent='n 输入 1～10、k 输入 1～100 的整数。';return;}ringEvents=circleEvents(n,k);ringIndex=0;$('j-feedback').textContent='先预测，再看下一轮；图从当前报 1 的人开始展示。';drawCircle();}
$('j-reset').onclick=resetCircle;$('j-n').onchange=resetCircle;$('j-k').onchange=resetCircle;$('j-prev').onclick=()=>{if(ringIndex>0)ringIndex--;drawCircle();};$('j-next').onclick=()=>{if(ringIndex<ringEvents.length-1)ringIndex++;drawCircle();};drawCircle();
makeLab('undo-lab','实验 05 / 记住现场，按栈撤销','从 2、3、4、5 开始。建议先删 3，再删 2，观察记录中的邻居；然后逐个撤销。',`<label>删除编号 <input id="u-id" type="number" min="0" max="5" step="1" value="3"></label><div class="controls"><button id="u-delete">删除并记录</button><button id="u-undo">撤销最近删除</button><button id="u-reset">重建队伍</button></div><p id="u-feedback" class="feedback" aria-live="polite"></p>`);
let undoModel=new DoubleModel([2,3,4,5]),undoStack=[];
function drawUndo(){const host=$('undo-lab-view');host.replaceChildren();drawChain(host,undoModel.forward(),{double:true,start:'H',end:'T'});fieldTable(host,['记录顺序','被删编号','当时左邻','当时右邻'],undoStack.map((r,i)=>[i===undoStack.length-1?'栈顶 / 下一条撤销':i+1,r.u,r.p===0?'H':r.p,r.q===1?'T':r.q]));$('undo-lab-event').textContent=undoStack.length?`待撤销 ${undoStack.length} 次。下一次只能恢复 ${undoStack.at(-1).u}，先说出它要接回哪两位之间。`:'记录栈为空，没有待撤销删除。';}
$('u-delete').onclick=()=>{try{const r=undoModel.remove($('u-id').valueAsNumber);undoStack.push(r);$('u-feedback').textContent=`记录 (${r.u}, ${r.p}, ${r.q}) 后跨接；结点槽位保留，尚未释放。`;drawUndo();}catch(e){$('u-feedback').textContent=e.message;}};
$('u-undo').onclick=()=>{if(!undoStack.length){$('u-feedback').textContent='空栈：不做操作。';return;}const r=undoStack.at(-1);try{undoModel.restore(r);undoStack.pop();$('u-feedback').textContent=`恢复 ${r.u}，接回原邻居之间；双向一致性${undoModel.check()?'通过':'失败'}。`;drawUndo();}catch(e){$('u-feedback').textContent=e.message;}};
$('u-reset').onclick=()=>{undoModel=new DoubleModel([2,3,4,5]);undoStack=[];$('u-feedback').textContent='已重建，删除记录清空。';drawUndo();};drawUndo();
sync();const initial=location.hash.match(/^#lesson-(\d+)$/);show(initial?+initial[1]:location.hash==='#home'?0:state.chapter,false);status(persistent?'笔记仅保存在当前浏览器；尚未学习的站点保持未自评。':'本地存储不可用。仍可阅读与填写，但请导出备份后再关闭。');
