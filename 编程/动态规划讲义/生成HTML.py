"""把四册同源内容生成可离线使用的两份独立 HTML。"""
from pathlib import Path
from html import escape
import base64
import json
import re

ROOT = Path(__file__).resolve().parent
TMP = ROOT.parent.parent / 'tmp/dp-handbook'
STUDENT = '动态规划自学讲义.html'
PARENT = '动态规划妈妈陪读指南.html'

CSS = r'''
:root{--ink:#243b39;--muted:#61736e;--accent:#17685b;--paper:#fffefa;--wash:#f2f5f0;--line:#d9e3da;--read-size:18px;color-scheme:light}
*{box-sizing:border-box}body{margin:0;color:var(--ink);background:var(--wash);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}a{color:var(--accent);text-underline-offset:4px}button,input,select,textarea{font:inherit}button,.button{cursor:pointer;border:1px solid var(--line);border-radius:8px;padding:9px 14px;background:white;color:var(--ink);text-decoration:none;display:inline-block}button:hover,.button:hover{background:#e8f1ea}.primary{background:var(--accent);color:white;border-color:var(--accent)}.primary:hover{background:#115246;color:white}:focus-visible{outline:3px solid #bd8b37;outline-offset:3px}[hidden]{display:none!important}.skip{position:absolute;left:-9999px}.skip:focus{left:20px;top:10px;z-index:20;background:white;padding:10px}
header{height:72px;padding:0 24px;background:var(--paper);border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:15px;position:sticky;top:0;z-index:5}.brand{font-size:19px;font-weight:700;text-decoration:none;color:var(--ink)}.brand span{font-size:12px;color:var(--muted);font-weight:400;margin-left:14px}.tools{display:flex;gap:7px;align-items:center}.tools button{font-size:14px;padding:8px 11px}#menu-toggle{display:none}
aside{position:fixed;top:72px;left:0;bottom:0;width:292px;background:var(--paper);border-right:1px solid var(--line);padding:22px 16px;overflow:auto}.side-title{font-size:12px;letter-spacing:.1em;color:var(--muted);font-weight:600;margin:0 10px 13px}#search{width:100%;border:1px solid var(--line);border-radius:8px;background:#f6f7f2;padding:11px;font-size:14px}#search-result{font-size:12px;color:var(--muted);min-height:20px;margin:8px 3px}.nav-group{margin:18px 0}.nav-group h2{font-size:13px;color:var(--muted);margin:0 10px 8px}.nav-link{display:block;font-size:13px;line-height:1.6;padding:8px 10px;margin:3px 0;text-decoration:none;color:var(--ink);border-radius:7px;position:relative}.nav-link:hover{background:var(--wash)}.nav-link[aria-current=page]{background:#e2eee4;color:#134f44;font-weight:600}.nav-link[data-recorded=true]::after{content:' ·';color:var(--accent);font-weight:900}.side-foot{font-size:12px;color:var(--muted);line-height:1.8;border-top:1px solid var(--line);padding:17px 10px;margin-top:24px}
main{margin-left:292px;padding:36px 42px 80px;min-height:calc(100vh - 72px)}.reader-wrap{max-width:880px;margin:0 auto}.crumb{font-size:12px;letter-spacing:.08em;color:var(--muted);margin:0 0 17px}.chapter{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:42px 48px;margin-bottom:24px;scroll-margin-top:100px;font-size:var(--read-size);line-height:1.9}.chapter h1{font-size:clamp(25px,2.5vw,34px);line-height:1.45;margin:0 0 27px;letter-spacing:-.015em}.chapter h2{font-size:1.17em;line-height:1.6;margin:32px 0 12px}.chapter h3{font-size:1.05em}.chapter p{margin:14px 0;overflow-wrap:anywhere}.chapter .lead{font-weight:600;color:var(--accent)}.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:16px}.chapter .sub{font-size:1.2em;color:var(--muted)}.chapter .small{font-size:14px;line-height:1.8;color:var(--muted)}.actions{display:flex;flex-wrap:wrap;gap:10px;margin:25px 0}.actions a{font-size:15px}.callout{border-left:3px solid #88aa8d;background:#f0f5ea;padding:14px 20px;margin:22px 0}.callout p{margin:6px 0}.think{border-left-color:#c49a51;background:#fcf5e7}.think strong{font-size:14px;color:#805b23;display:block;margin-bottom:7px}details{border:1px solid var(--line);border-radius:9px;margin:20px 0;background:#fffefa}summary{padding:13px 17px;cursor:pointer;font-size:15px;font-weight:600;color:var(--accent)}.details-body{padding:1px 21px 18px;border-top:1px solid var(--line)}.formula,pre{background:#f3f5f1;padding:16px 18px;border-radius:8px;overflow:auto;font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace;font-size:.88em;line-height:1.8;white-space:pre-wrap;overflow-wrap:anywhere}.table-wrap{overflow-x:auto;margin:18px 0;border:1px solid var(--line);border-radius:8px}table{border-collapse:collapse;width:100%;font-size:.86em;min-width:420px}th,td{padding:10px 13px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}th{background:#eaf0e7;font-weight:600}td+td,th+th{border-left:1px solid var(--line)}tr:last-child td{border-bottom:0}figure{margin:24px 0}figure img{display:block;max-width:100%;height:auto;border-radius:6px}.task{border-left:3px solid var(--accent);padding:14px 20px;background:#edf5ee;margin:24px 0}.task h3{margin:0 0 9px}.task-lines{font-size:.87em;color:var(--muted)}.source{font-size:14px;word-break:break-all}.chapter-nav{display:flex;justify-content:space-between;gap:20px;margin:24px 0}.chapter-nav button{font-size:14px;max-width:48%;text-align:left;line-height:1.6}
.notes{padding:26px 30px;background:var(--paper);border:1px solid var(--line);border-radius:12px}.notes h2{font-size:19px;margin:0 0 8px}.notes p{font-size:13px;color:var(--muted);line-height:1.8}.notes label{font-size:14px;display:block;margin:18px 0 7px}.notes select{padding:10px;border:1px solid var(--line);border-radius:7px;max-width:100%;background:white}.notes textarea{width:100%;min-height:155px;resize:vertical;border:1px solid var(--line);border-radius:8px;padding:14px;line-height:1.8;font-size:16px;color:var(--ink);background:white}#save-status{min-height:23px}.status-row{display:flex;align-items:center;flex-wrap:wrap;gap:15px}.status-row label{margin:0}.quiet{color:var(--muted);font-size:12px}.nojs{margin:15px;padding:15px;background:#fcf5e7}.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}
@media(min-width:1500px){main{padding-top:48px}}@media(max-width:1050px){aside{width:260px}main{margin-left:260px;padding:26px}.chapter{padding:32px}}@media(max-width:760px){header{height:auto;min-height:64px;padding:12px 16px;flex-wrap:wrap}.brand{font-size:17px}.brand span{display:none}#menu-toggle{display:inline-block}.tools{gap:5px}.tools button{font-size:12px;padding:7px 9px}aside{display:none;top:110px;width:min(340px,90vw);z-index:4;box-shadow:10px 0 25px #203c3120}body.menu-open aside{display:block}main{margin:0;padding:18px 12px 55px}.chapter{padding:25px 21px;border-radius:10px;font-size:var(--read-size)}.notes{padding:22px}.chapter h1{font-size:27px}.chapter-nav button{padding:9px}.table-wrap{margin-right:-2px}.crumb{font-size:11px}.source{font-size:12px}}
@media print{header,aside,.crumb,.chapter-nav,.notes,.actions,.no-print{display:none!important}main{margin:0;padding:0}.chapter{padding:0;border:0;background:white;font-size:11pt;line-height:1.7;margin:0}.chapter h1{font-size:20pt}.chapter h2{break-after:avoid}.callout,.task,pre,tr,figure{break-inside:avoid}a{color:black}details{border:0}.details-body{padding:0;border:0}summary{display:none}body{background:white}.table-wrap{overflow:visible}table{min-width:0}figure img{max-height:180px;margin:auto}p{orphans:3;widows:3}@page{size:A4;margin:18mm}}
'''

JS = r'''
(()=>{'use strict';
const chapters=[...document.querySelectorAll('.chapter')], links=[...document.querySelectorAll('.nav-link')];
const key='family-dp-reader-v1-'+document.body.dataset.edition, labels=['未开始','学过，仍需练习','本次独立完成','隔天重做通过'];
let state={last:'welcome',font:18,records:{}}, available=true, current, timer;
const byId=new Map(chapters.map(s=>[s.id,s]));
try{const raw=localStorage.getItem(key);if(raw){const data=JSON.parse(raw);if(data&&typeof data==='object'){if(byId.has(data.last))state.last=data.last;if(Number.isFinite(data.font))state.font=Math.max(16,Math.min(24,data.font));if(data.records&&typeof data.records==='object'&&!Array.isArray(data.records))for(const id of byId.keys()){const r=data.records[id];if(r&&typeof r.note==='string'&&Number.isInteger(r.stage)&&r.stage>=0&&r.stage<4)state.records[id]={note:r.note,stage:r.stage};}}}localStorage.setItem(key,JSON.stringify(state));}catch(e){available=false;}
const note=document.querySelector('#note'), stage=document.querySelector('#stage'), status=document.querySelector('#save-status');
function message(){status.textContent=available?'已保存在当前浏览器。换设备前请导出学习记录。':'当前浏览器无法保存本机记录。离开前请导出，避免丢失。';}
function persist(){try{localStorage.setItem(key,JSON.stringify(state));available=true;}catch(e){available=false;}message();}
function save(){if(!current)return;state.records[current]={note:note.value,stage:Number(stage.value)};links.forEach(a=>{const r=state.records[a.dataset.target];a.dataset.recorded=!!r&&(r.stage>0||r.note.length>0);});persist();}
function hashId(){try{return decodeURIComponent(location.hash.slice(1));}catch(e){return '';}}
function navigate(id,scroll=true){if(!byId.has(id))id='welcome';if(current&&id!==current){clearTimeout(timer);save();}current=id;state.last=id;chapters.forEach(s=>s.hidden=s.id!==id);const active=byId.get(id);links.forEach(a=>{if(a.dataset.target===id)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');const r=state.records[a.dataset.target];a.dataset.recorded=!!r&&(r.stage>0||r.note.length>0);});const record=state.records[id]||{note:'',stage:0};note.value=record.note;stage.value=String(record.stage);document.querySelector('#note-heading').textContent='我的学习记录 · '+active.dataset.title;document.querySelector('#crumb').textContent=active.dataset.book;document.title=active.dataset.title+' · 动态规划';const index=chapters.indexOf(active);for(const [sel,pos,prefix] of [['#previous',index-1,'上一节'],['#next',index+1,'下一节']]){const b=document.querySelector(sel);b.hidden=pos<0||pos>=chapters.length;if(!b.hidden){b.dataset.target=chapters[pos].id;b.textContent=prefix+' · '+chapters[pos].dataset.title;}}document.body.classList.remove('menu-open');document.querySelector('#menu-toggle').setAttribute('aria-expanded','false');persist();if(scroll)window.scrollTo({top:0,behavior:'instant'});}
document.querySelectorAll('[data-target]').forEach(el=>el.addEventListener('click',e=>{e.preventDefault();const id=el.dataset.target;if(!byId.has(id))return;if(hashId()===id)navigate(id);else location.hash=id;}));
window.addEventListener('hashchange',()=>navigate(hashId()));
note.addEventListener('input',()=>{status.textContent='正在保存…';clearTimeout(timer);timer=setTimeout(save,350);});stage.addEventListener('change',save);window.addEventListener('pagehide',save);
document.querySelector('#search').addEventListener('input',e=>{const q=e.target.value.trim().toLowerCase();let matches=0;links.forEach(a=>{const yes=!q||byId.get(a.dataset.target).textContent.toLowerCase().includes(q);a.hidden=!yes;if(yes)matches++;});document.querySelectorAll('.nav-group').forEach(g=>g.hidden=![...g.querySelectorAll('a')].some(a=>!a.hidden));document.querySelector('#search-result').textContent=q?(matches?'找到 '+matches+' 节，可从目录打开。':'没有匹配章节，试试“背包”或“状态”。'):'可以搜索章节标题或正文关键词。';});
document.querySelector('#menu-toggle').addEventListener('click',e=>{const open=document.body.classList.toggle('menu-open');e.currentTarget.setAttribute('aria-expanded',String(open));});document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.body.classList.remove('menu-open');document.querySelector('#menu-toggle').setAttribute('aria-expanded','false');}});
function font(delta){state.font=Math.max(16,Math.min(24,state.font+delta));document.documentElement.style.setProperty('--read-size',state.font+'px');persist();}document.querySelector('#font-down').addEventListener('click',()=>font(-1));document.querySelector('#font-up').addEventListener('click',()=>font(1));font(0);
function alignSidebar(){document.querySelector('#sidebar').style.top=document.querySelector('header').getBoundingClientRect().height+'px';}alignSidebar();window.addEventListener('resize',alignSidebar);
let before=[];function preparePrint(){before=[...byId.get(current).querySelectorAll('details')].map(d=>[d,d.open]);before.forEach(([d])=>d.open=true);}function restorePrint(){before.forEach(([d,open])=>d.open=open);before=[];}window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',restorePrint);document.querySelector('#print').addEventListener('click',()=>window.print());
document.querySelector('#export').addEventListener('click',()=>{clearTimeout(timer);save();const lines=['动态规划学习记录',new Intl.DateTimeFormat('zh-CN',{timeZone:'Asia/Shanghai',dateStyle:'long',timeStyle:'short'}).format(new Date()),'进度由学习者自行标记，不代替程序验证或教练评估。',''];for(const s of chapters){const r=state.records[s.id];if(r&&(r.note.trim()||r.stage>0))lines.push(s.dataset.book+' / '+s.dataset.title,'进度：'+labels[r.stage],r.note||'（尚未填写笔记）','');}if(lines.length===4)lines.push('尚未填写学习记录。');const url=URL.createObjectURL(new Blob([lines.join('\n')],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='动态规划_'+document.body.dataset.edition+'_学习记录.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
navigate(byId.has(hashId())?hashId():state.last,false);
})();
'''

def parse(cn, vol):
    lines=(ROOT/f'内容{cn}.txt').read_text().splitlines()
    title=lines[0].split(' ',1)[1];sub=lines[1].split(' ',1)[1]
    groups=[{'id':f'v{vol}-intro','title':'本册导读','blocks':[]}]
    index=2;count=0
    while index<len(lines):
        line=lines[index];index+=1
        if not line:continue
        if line.startswith('@h1 '):
            count+=1;groups.append({'id':f'v{vol}-c{count}','title':line[4:],'blocks':[]});continue
        if line.startswith('@table '):
            rows=[line[7:].split('|')]
            while lines[index]!='@endtable':rows.append(lines[index].split('|'));index+=1
            index+=1;block=('table',rows)
        elif line.startswith('@code ') or line=='@sample':
            label='样例输入与输出' if line=='@sample' else line[6:];buf=[]
            while lines[index]!='@endcode':buf.append(lines[index]);index+=1
            index+=1;block=('code',(label,'\n'.join(buf)))
        elif line.startswith('@'):
            tag,body=line[1:].split(' ',1);block=(tag,body)
        else:block=('p',line)
        groups[-1]['blocks'].append(block)
    for g in groups:g.update(book=sub,vol=vol)
    return groups

def text(body):
    # The printed first-chapter cross-reference points to chapter 1 in error;
    # the actual task check is chapter 3 of the parent booklet.
    return escape(body.replace('核验见第四册第1章。','核验见第四册第3章“章节独立任务核验”。'))

def block_html(kind, body):
    if kind=='h2':return '<h2>'+text(body)+'</h2>'
    if kind=='intro':return '<p class="lead">'+text(body)+'</p>'
    if kind=='formula':return '<div class="formula" aria-label="关系式">'+text(body)+'</div>'
    if kind=='code':return '<h3>'+text(body[0])+'</h3><pre><code>'+text(body[1])+'</code></pre>'
    if kind=='table':
        return '<div class="table-wrap" tabindex="0" aria-label="可横向滚动的表格"><table><thead><tr>'+''.join('<th scope="col">'+text(x)+'</th>' for x in body[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+text(x)+'</td>' for x in row)+'</tr>' for row in body[1:])+'</tbody></table></div>'
    if kind=='diagram':
        alt={'recursion':'求第5级分为求第4级和第3级，展开后第3级和第2级被重复询问。','dag':'点1分别指向点2与点3，点2与点3分别指向点4。','tree':'节点1权值5，连节点2权值4与节点3权值3，节点2再连节点4权值6。'}[body]
        data=base64.b64encode((TMP/(body+'.png')).read_bytes()).decode()
        return f'<figure><img src="data:image/png;base64,{data}" alt="{alt}" width="1500" height="430"></figure>'
    if kind=='url':return '<p class="source"><a href="'+escape(body,quote=True)+'" target="_blank" rel="noopener noreferrer">'+text(body)+'</a></p>'
    if kind=='task':return '<details class="exercise-hint"><summary>独立检查提醒 · 先尝试，再按需展开</summary><div class="details-body"><p>'+text(body)+'</p></div></details><div class="task"><h3>停在这里，完成自己的作品</h3><p class="task-lines">写下状态和来源，设计关键测试；出现错误时，找出第一次偏差与修改依据。可以用纸笔，也可以记录在本页下方。</p></div>'
    if kind=='p':
        if '先停下来想：' in body:return '<div class="callout think"><strong>先停下来想</strong><p>'+text(body.replace('先停下来想：','',1))+'</p></div>'
        return '<p>'+text(body)+'</p>'
    raise ValueError(kind)

def section(g, parent):
    parts=[f'<section class="chapter" id="{g["id"]}" data-title="{escape(g["title"],quote=True)}" data-book="{escape(g["book"],quote=True)}">',f'<div class="eyebrow">{text(g["book"])}</div>',f'<h1 tabindex="-1">{text(g["title"])}</h1>']
    gate=False;has_gate=False
    parent_check=parent and re.match(r'第[3-7]章',g['title'])
    for kind,body in g['blocks']:
        if gate and kind=='h2' and ('独立任务' in body or parent_check):parts.append('</div></details>');gate=False
        parts.append(block_html(kind,body))
        if parent_check and kind=='h2':
            parts.append('<details><summary>孩子尝试后，查看核验依据与局部提示</summary><div class="details-body">');gate=True
        elif not parent and g['vol']<3 and not has_gate and kind=='p' and '先停下来想：' in body:
            parts.append('<details class="derivation"><summary>留下自己的想法后，展开后续推导</summary><div class="details-body">');gate=True;has_gate=True
    if gate:parts.append('</div></details>')
    parts.append('</section>');return '\n'.join(parts)

def build(parent=False):
    edition='妈妈陪读' if parent else '孩子自学'
    groups=parse('四',4) if parent else sum([parse(cn,v) for v,cn in enumerate('一二三',1)],[])
    byvol={v:[g for g in groups if g['vol']==v] for v in sorted({g['vol'] for g in groups})}
    nav='<div class="nav-group"><h2>开始之前</h2><a class="nav-link" href="#welcome" data-target="welcome">怎样使用电脑讲义</a></div>'
    for v,gg in byvol.items():
        nav+='<div class="nav-group"><h2>'+text(gg[0]['book'])+'</h2>'+''.join(f'<a class="nav-link" href="#{g["id"]}" data-target="{g["id"]}">{text(g["title"])}</a>' for g in gg)+'</div>'
    if parent:
        welcome=f'''<section class="chapter" id="welcome" data-title="妈妈的阅读入口" data-book="陪伴孩子 · 检查理解"><div class="eyebrow">动态规划 / 妈妈陪读</div><h1 tabindex="-1">听她讲清楚，<br>让她自己做出来。</h1><p>这里完整保留第四册。先读前两章，理解检查方法与提示边界；孩子尝试后，再按章节或题号打开核验依据。</p><div class="callout"><p>“妈妈能听懂”检验讲解是否清楚。独立建模、程序验证、陌生变式和隔天重做，是另外几份必要的证据。</p></div><div class="actions"><a class="button primary" href="#v4-c1" data-target="v4-c1">从妈妈册第1章开始</a><a class="button" href="{STUDENT}">打开孩子自学讲义</a></div><p class="small">核验依据默认折叠。这里是独立的家长文档，建议由妈妈保管；折叠只是阅读安排，不是访问限制。</p><h2>关于本机记录</h2><p class="small">记录自动保存在当前浏览器；换浏览器、移动文件或清除浏览器数据后可能无法找回。用右上角“导出记录”保存文本副本。</p></section>'''
    else:
        welcome='''<section class="chapter" id="welcome" data-title="怎样使用电脑讲义" data-book="从纸笔模型到独立解决问题"><div class="eyebrow">动态规划 / 离线自学讲义</div><h1 tabindex="-1">把过去记清楚，<br>把下一步想明白。</h1><p>从零开始，沿着24章讲解与24道原创练习，学习状态、来源、边界、验证和迁移。今天只需要推进一个完整问题。</p><div class="actions"><a class="button primary" href="#v1-c1" data-target="v1-c1">先看学习路线</a><a class="button" href="#v1-c2" data-target="v1-c2">从第1章开始</a><a class="button" href="#v3-c1" data-target="v3-c1">进入独立练习</a></div><h2>一节课，分三次行动</h2><div class="callout"><p><strong>先想：</strong>读题，用纸笔画一个小例子，写下自己的猜想。</p><p><strong>再读：</strong>展开推导，找出与你原来想法不同的地方。</p><p><strong>独立做：</strong>合上讲解，完成任务、写码、自测，再记下真正的卡点。</p></div><p>递归还不稳也能开始。先读第一册第1—3章，再用第4章连接递归和记忆化。提高组章节需要更长的练习过程，不按翻过的页数判断掌握。</p><h2>这份电脑讲义怎样用</h2><p>左侧目录可以搜索正文；“A− / A+”调整字号；每节下方可以记草稿、卡点和进度。再次打开时会回到上次阅读的一节。</p><p class="small">文件无需联网即可阅读。记录自动保存在当前浏览器；换设备、移动文件或清除浏览器数据后可能无法找回，请用右上角“导出记录”保存文本副本。右上角可打印当前一节。</p><p class="small">进度由你自己标记。读完、独立完成、隔天重做通过是不同进展，标记不会代替实际程序测试。妈妈核验依据放在另一份文档中。</p></section>'''
    other=STUDENT if parent else PARENT
    otherlabel='孩子自学讲义' if parent else '妈妈陪读入口'
    html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>动态规划 · EDITION</title><style>STYLE</style></head><body data-edition="EDITION"><a class="skip" href="#reader">跳到正文</a><header><a class="brand" href="#welcome" data-target="welcome">动态规划 <span>EDITION · 离线阅读</span></a><div class="tools"><button id="menu-toggle" aria-controls="sidebar" aria-expanded="false">目录</button><button id="font-down" aria-label="缩小正文字号">A−</button><button id="font-up" aria-label="增大正文字号">A+</button><button id="export">导出记录</button><button id="print">打印本节</button></div></header><aside id="sidebar" aria-label="讲义目录"><p class="side-title">一步一步，留下自己的作品</p><label class="visually-hidden" for="search">搜索章节和正文</label><input id="search" type="search" placeholder="搜索章节或关键词" autocomplete="off"><p id="search-result" aria-live="polite">可以搜索章节标题或正文关键词。</p><nav>NAV</nav><div class="side-foot">第一、二册：24章讲解<br>第三册：24道独立练习<br>第四册：妈妈陪读与核验<br><br><a href="OTHER">OTHERLABEL</a><br>2026年10月12日 · HTML版</div></aside><main id="reader"><div class="reader-wrap"><p class="crumb" id="crumb">从纸笔模型到独立解决问题</p><noscript><p class="nojs">浏览器未启用脚本，以下仍可连续阅读完整内容；本机记录、搜索和字号调整需要启用脚本。</p></noscript>CONTENT<div class="chapter-nav"><button id="previous" data-target="">上一节</button><button id="next" data-target="">下一节</button></div><section class="notes" aria-labelledby="note-heading"><h2 id="note-heading">我的学习记录</h2><p>先记录你的真实想法。不会的地方可以直接写“我卡在……”，不用把讲义的话当作自己的反思。</p><div class="status-row"><label for="stage">本节进度</label><select id="stage"><option value="0">未开始</option><option value="1">学过，仍需练习</option><option value="2">本次独立完成</option><option value="3">隔天重做通过</option></select><span class="quiet">由学习者自行标记</span></div><label for="note">我的草稿、卡点、测试与重做记录</label><textarea id="note" placeholder="写下今天想通了什么、还卡在哪里，或下一次准备验证的例子。"></textarea><p id="save-status" role="status" aria-live="polite"></p></section></div></main><script>SCRIPT</script></body></html>'''
    replacements={'EDITION':edition,'STYLE':CSS,'NAV':nav,'OTHERLABEL':otherlabel,'OTHER':other,'CONTENT':welcome+'\n'+'\n'.join(section(g,parent) for g in groups),'SCRIPT':JS}
    # Replace only tokens in the template, never recursively in content.
    html=re.sub(r'EDITION|STYLE|NAV|OTHERLABEL|OTHER|CONTENT|SCRIPT',lambda m:replacements[m[0]],html)
    path=ROOT/(PARENT if parent else STUDENT);path.write_text(html,encoding='utf-8')
    return {'file':path.name,'sections':len(groups)+1,'source_volumes':[4] if parent else [1,2,3],'bytes':path.stat().st_size}

if __name__=='__main__':
    result=[build(),build(True)]
    print(json.dumps(result,ensure_ascii=False,indent=2))
