'use strict';
const $=id=>document.getElementById(id), KEY='binary-adventure-v1';
let state={chapter:0,notes:{},ratings:{}}, allMode=false, persistent=true;
const ratingValues=['','revisit','explain','transfer'];
function validData(v){
 if(!v || typeof v!=='object' || Array.isArray(v))throw Error('格式不正确');
 const clean={chapter:Number.isInteger(v.chapter)&&v.chapter>=0&&v.chapter<=30?v.chapter:0,notes:{},ratings:{}};
 for(let i=1;i<=30;i++){
  if(v.notes&&typeof v.notes[i]==='string')clean.notes[i]=v.notes[i].slice(0,50000);
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
 $('crumb').textContent=n?`二分 / 第 ${String(n).padStart(2,'0')} 站 / ${$('heading-'+n).textContent}`:'二分 / 出发与路线';
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
 const a=document.createElement('a');a.href=url;a.download='二分探险笔记-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
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
makeLab('boundary-lab','实验 01 / 两根界桩，由你移动','先看中点的值，判断它是否符合条件；只有移动了正确的界桩，实验才向下一轮走。',`<label>数组 <select id="b-array"><option value="normal">[2,4,4,7,9]</option><option value="pair">[4,4]</option><option value="single">[4]</option><option value="empty">[] 空数组</option></select></label><label>找第一个 ≥ <input id="b-x" type="number" value="4" min="-100" max="100" step="1"></label><div class="controls"><button id="b-reset">重新开始</button><button id="b-false">中点是假 → 移假界桩</button><button id="b-true">中点是真 → 移真界桩</button></div><p id="b-feedback" class="feedback" aria-live="polite"></p>`);
let boundary={a:[2,4,4,7,9],x:4,lo:-1,hi:5,log:[]};
function drawBoundary(){
 const {a,x,lo,hi,log}=boundary,n=a.length,done=hi-lo<=1,mid=done?null:lo+Math.floor((hi-lo)/2),host=$('boundary-lab-view');host.replaceChildren();
 const tiles=document.createElement('div');tiles.className='tiles';
 for(let i=-1;i<=n;i++){
  const tile=document.createElement('div');tile.className='tile'+(i<=lo?' false':i>=hi?' true':'')+(i===mid?' mid':'')+(i<0||i===n?' sentinel':'');
  const value=document.createElement('span');value.textContent=i<0?'虚拟假':i===n?'虚拟真':a[i];const label=document.createElement('small');label.textContent=`i=${i}`+(i===lo?' · lo':'')+(i===hi?' · hi':'')+(i===mid?' · mid':'');tile.append(value,label);tiles.append(tile);
 }
 host.append(tiles);const history=document.createElement('ol');history.className='log';for(const line of log){const li=document.createElement('li');li.textContent=line;history.append(li);}host.append(history);
 $('boundary-lab-event').textContent=done?`两桩相邻：lo=${lo}，hi=${hi}。${hi===n?'边界等于 n：没有实际元素满足条件。':`第一个 ≥${x} 的下标为 ${hi}，对应值为 ${a[hi]}。`}请解释为什么能结束。`:`lo=${lo}，hi=${hi}，距离=${hi-lo}；mid=${mid}，a[mid]=${a[mid]}。它是否 ≥${x}？黄色边框是本轮中点。`;
 $('b-false').disabled=done;$('b-true').disabled=done;
}
function resetBoundary(){const arrays={normal:[2,4,4,7,9],pair:[4,4],single:[4],empty:[]},x=$('b-x').valueAsNumber;
 if(!Number.isInteger(x)||x< -100||x>100){$('b-feedback').textContent='请输入 −100～100 的整数。';return;}
 const a=arrays[$('b-array').value];boundary={a,x,lo:-1,hi:a.length,log:[]};$('b-feedback').textContent='先预测，再移动。';drawBoundary();}
function moveBoundary(choice){const b=boundary;if(b.hi-b.lo<=1)return;const mid=b.lo+Math.floor((b.hi-b.lo)/2),truth=b.a[mid]>=b.x;
 if(choice!==truth){$('b-feedback').textContent=`再比较：${b.a[mid]} ≥ ${b.x} 成立吗？先确定真假，再决定界桩身份。`;return;}
 const old=b.hi-b.lo;if(truth)b.hi=mid;else b.lo=mid;b.log.push(`检测 i=${mid}：${truth?'真，hi':'假，lo'} ← ${mid}；距离 ${old} → ${b.hi-b.lo}`);$('b-feedback').textContent='移动保持了界桩身份；请继续判断下一轮。';drawBoundary();}
$('b-reset').onclick=resetBoundary;$('b-array').onchange=resetBoundary;$('b-x').onchange=resetBoundary;$('b-false').onclick=()=>moveBoundary(false);$('b-true').onclick=()=>moveBoundary(true);drawBoundary();
makeLab('halve-lab','实验 02 / 折半的工作账单','输入候选个数，先估计缩到 1 个需要多少轮。这里模拟每轮最坏留下向上取整的一半，不是某个具体 C++ 模板的精确比较次数。',`<label>候选个数 <input id="h-n" type="number" value="1024" min="1" max="1000000000" step="1"></label><button id="h-run">查看规模链</button>`);
$('h-run').onclick=()=>{let n=$('h-n').valueAsNumber;if(!Number.isInteger(n)||n<1||n>1e9){$('halve-lab-event').textContent='请输入 1～10⁹ 的整数。';return;}const chain=[n];while(n>1){n=Math.ceil(n/2);chain.push(n);}const host=$('halve-lab-view');host.replaceChildren();paragraph(host,chain.join(' → '),'log');$('halve-lab-event').textContent=`折半 ${chain.length-1} 轮缩到 1 个候选。若每轮扫描 10 万个元素，还要乘上每轮的工作量。`;};$('halve-lab-event').textContent='尚未展开。先写下你的估计。';
makeLab('cuts-lab','实验 03 / 固定长度上限，不先猜答案','木条固定为 [6,7]。改变 x 和允许刀数 K，检查每根至少需要几刀。先画切点，再核对账单。',`<label>长度上限 x <input id="c-x" type="number" value="3" min="1" max="12" step="1"></label><label>最多刀数 K <input id="c-k" type="number" value="3" min="0" max="20" step="1"></label><button id="c-run">只检查这个 x</button>`);
$('c-run').onclick=()=>{const x=$('c-x').valueAsNumber,k=$('c-k').valueAsNumber;if(!Number.isInteger(x)||x<1||x>12||!Number.isInteger(k)||k<0||k>20){$('cuts-lab-event').textContent='x 输入 1～12 的整数，K 输入 0～20 的整数。';return;}const data=[6,7].map(a=>[a,Math.ceil(a/x),Math.floor((a-1)/x)]),total=data.reduce((s,r)=>s+r[2],0);rows($('cuts-lab-view'),['原长度','至少段数','至少刀数'],data);$('cuts-lab-event').textContent=`合计至少 ${total} 刀；允许 ${k} 刀：${total<=k?'可行':'不可行'}。把 x 改大 1，再预测总刀数会向哪个方向变化。`;};$('cuts-lab-event').textContent='尚未检查。这里先验证裁判，不直接求最优答案。';
makeLab('spacing-lab','实验 04 / 固定距离，观察贪心放置','坐标 [1,2,4,8,9]，要求种 3 棵。先自己摆放，再看“每次放最早合法位置”的过程。',`<label>最小间距 d <input id="s-d" type="number" value="3" min="0" max="9" step="1"></label><button id="s-run">展开这一种距离</button>`);
$('s-run').onclick=()=>{const d=$('s-d').valueAsNumber;if(!Number.isInteger(d)||d<0||d>9){$('spacing-lab-event').textContent='请输入 0～9 的整数。';return;}const a=[1,2,4,8,9],chosen=[a[0]],data=[[1,'种第一棵','已种 1 棵']];for(const p of a.slice(1)){const gap=p-chosen.at(-1),take=gap>=d;if(take)chosen.push(p);data.push([p,`距上一棵 ${gap}，${take?'满足，种下':'不足，跳过'}`,`已种 ${chosen.length} 棵`]);}rows($('spacing-lab-view'),['位置','这一步的依据','数量'],data);$('spacing-lab-event').textContent=`贪心可种 ${chosen.length} 棵：${chosen.length>=3?'达到 3 棵，可行':'不足 3 棵，不可行'}。要求是能选出 3 棵，因此更多也可行。请用“不晚于其他方案”解释裁判的可靠性。`;};$('spacing-lab-event').textContent='尚未摆放。先尝试 d=3，再尝试 d=4。';
makeLab('average-lab','实验 05 / 前缀最小值从哪里来？','固定数组 [1,5,2,6]，L=2。此处只检查候选平均值 x；j 的合法范围随 r 扩大。',`<label>候选平均值 x <input id="a-x" type="number" value="4" min="-10" max="10" step="0.5"></label><button id="a-run">核对前缀账单</button>`);
$('a-run').onclick=()=>{const x=$('a-x').valueAsNumber;if(!Number.isFinite(x)||x< -10||x>10){$('average-lab-event').textContent='请输入 −10～10 的数。';return;}const a=[1,5,2,6],s=[0];for(const v of a)s.push(s.at(-1)+v-x);let min=Infinity,ok=false;const data=[];for(let r=2;r<=a.length;r++){min=Math.min(min,s[r-2]);const diff=s[r]-min;ok ||= diff>=0;data.push([r,`0～${r-2}`,s[r].toFixed(2),min.toFixed(2),diff.toFixed(2),diff>=0?'可行子段存在':'此 r 暂无']);}rows($('average-lab-view'),['右端前缀 r','合法 j','s[r]','最小 s[j]','最大差','本轮判断'],data);$('average-lab-event').textContent=`b=[${a.map(v=>(v-x).toFixed(2)).join(', ')}]；${ok?'存在':'不存在'}长度至少 2、平均值至少 ${x} 的子段。核对时不要把 j=r 加入。`;};$('average-lab-event').textContent='尚未计算。请先列 b 与 s，再查看。';
sync();const initial=location.hash.match(/^#lesson-(\d+)$/);show(initial?+initial[1]:location.hash==='#home'?0:state.chapter,false);status(persistent?'笔记仅保存在当前浏览器；尚未学习的站点保持未自评。':'本地存储不可用。仍可阅读与填写，但请导出备份后再关闭。');
