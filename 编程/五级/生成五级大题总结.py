from pathlib import Path
from html import escape as e
from collections import Counter
from urllib.parse import quote
import json
import re
from 五级大题分析数据 import PROBLEMS, CATEGORIES

ROOT = Path(__file__).resolve().parent
PAGES = []
BYID = {p['id']: p for p in PROBLEMS}

def table(head, rows):
    return '<table><thead><tr>'+''.join('<th>'+x+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'

def box(title, body, kind='method'):
    return f'<div class="box {kind}"><b>{title}</b><div>{body}</div></div>'

def refs(ids):
    return '、'.join(f'<a href="#problem{i}-1">{i:02d} {BYID[i]["title"]}</a>' for i in ids)

def add(title, body, label='家长阅读 · 总览', ident=None, parent=False, topic='', step=''):
    body = re.sub(r'<(?!/?(?:div|span|b|p|h3|ol|li|table|thead|tbody|tr|th|td|code|pre|br|a|strong)(?:\s|/?>))', '&lt;', body)
    PAGES.append(dict(title=title, body=body, label=label, ident=ident or f'page{len(PAGES)+1}', parent=parent, topic=topic, step=step))

add('GESP C++ 五级 · 历次编程大题总结', '''
<div class="eyebrow">读题 → 手推 → 建模 → 实现 → 自测</div>
<div class="cover-title">从一道题的故事<br>找到一类题的方法</div>
<p class="lead">沿着九份试卷的18道编程题，看看小题里学过的知识，怎样组合成一个完整解题过程。</p>
<div class="stats"><div><b>9</b><span>份试卷</span></div><div><b>18</b><span>道大题</span></div><div><b>6</b><span>类主要方法</span></div></div>
'''+box('这份材料怎么读','先看历次总览和方法归组，再按孩子已有基础选择题目。每题都有题意、关键转化、理由、变量职责、复杂度和自测方向；需要展开的题分成两页，沿用同一题号。','intro')+box('家长备课与孩子尝试','第6—7页集中放了每题的第一个思考任务。网页默认收起逐题分析，适合先让孩子独立尝试；本PDF保留全部家长讲解。讲解没有完整可照抄的解题代码。')+'''
<p>本稿整理的是题目需要什么能力，不是对孩子的能力诊断。尚无这些大题的独立作答记录，不预填“已掌握”或“不会”。</p>
<div class="cover-meta">范围：2406、2409、2412、2503、2506、2509、2512、2603、2606<br>配套：《GESP五级小题学习讲义》主题01—28<br>2026年10月9日 · 版本1.0 · 家长备课与分层学习稿</div>
''', label='使用说明', ident='cover')

names={
1:'二维压成一维连续段',2:'分清质因子的种类与次数',3:'把收益集中到目标武器',4:'枚举攻击次数，检查剩余血量',5:'把质因子指数当预算',6:'先固定领先门槛，再选择材料',7:'基准收入＋改换买家的收益差',8:'质因数分解＋模幂判定',9:'份数二分＋配方分配检查',10:'整体平移时差值不变',11:'证明可选数量的上界并达到',12:'二进制分块，统计数量与和',13:'固定代价上限，检查不能动的部分',14:'质因子指数分别调整',15:'有限小数看分母的质因子',16:'预排序，减少重复查找',17:'看每个位置的贡献次数',18:'枚举数对，用GCD判断合法性'}
rows=[]
for a,b in zip(PROBLEMS[::2],PROBLEMS[1::2]):
    rows.append([a['paper'][:2]+'年'+a['paper'][2:]+'月',f'<b>{a["id"]:02d} {a["title"]}</b><br>{names[a["id"]]}',f'<b>{b["id"]:02d} {b["title"]}</b><br>{names[b["id"]]}'])
add('九次考试，大题分别在问什么', '<p>下面按所提供材料的年月排序。01—18是本讲义题号，方便跨页定位；每份试卷各有两道大题。</p>'+table(['材料年月','第一题','第二题'],rows)+box('先看目标，再找算法','有的题要最大个数，有的要最少总费用，有的要最小的“单次最大费用”。目标中一个词的不同，就会改变整个模型。','intro'), ident='timeline')

rows=[]
for cat,(name,desc) in CATEGORIES.items():
    ps=[p for p in PROBLEMS if p['cat']==cat]
    rows.append([f'<b>{cat} · {name}</b><br>{len(ps)}题',refs([p['id'] for p in ps]),desc])
add('同一方法归在一起，跨题比较着学','<p>按每题最主要的建模方法归类，每题只统计一次；实际解法常有交叉。例如《数字选取》既用素数筛，也需要证明选择数量已经最多。</p>'+table(['方法组','对应题号与题名','这组训练什么'],rows)+box('频次怎样用','这九份材料中，数论是最集中的主线。链表、高精度没有以独立大题模型出现，但仍在所提供五级考纲和小题学习范围内；不能据此删掉这些知识。频次不等于未来出题概率。'),ident='groups')

add('同样的知识，到了大题怎样变了样', '''
<h3>A组：不是都写一遍质因数分解就结束</h3>
'''+table(['读题时看到的限制','真正要保存或利用什么','对应题'],[
['恰好两种不同质因子','种类数；同一种因子要除尽','02'],
['不同质数幂的乘积整除n','每种质因子的指数预算','05'],
['乘或除一个质数，最后相等','指数之间的距离与独立性','14'],
['每个数同时加相同偏移','不会随偏移变化的差值','10'],
['幂模质数第一次回到1','周期与p−1的约数关系','08'],
])+'''<h3>B组：贪心必须说清“为什么这样选”</h3><p>《小杨的武器》证明一个上界可以达到；《平均分配》比较改换买家的收益差；《排排坐》比较位置贡献；《武器强化》要先固定门槛，处理强制选择，再比较价格。四题不能用“每次拿最大的”一语带过。</p>
<h3>C组：二分外壳相似，check才是题目本身</h3><p>《奖品兑换》问“k份能否分配出合法配方”，寻找最后一个可行份数；《数字移动》问“上限x下能否配对”，寻找第一个可行上限。先用自然语言把检查规则说清，再讨论边界怎么移动。</p>
'''+box('与小题讲义衔接','数论主要回看主题05—10；贪心回看23—24；二分回看15—17；分治统计回看02—04、18。复杂度主题01贯穿所有大题。每题末尾另列对应主题号。','intro'),ident='transfer')

add('建议学习顺序：先能独立走完，再增加转化', '<p>下面是按知识依赖安排的建议顺序，不是官方难度分级，也不是孩子的能力标签。每阶段可拆成多次；当前CSP学习中的同类题可以替换其中的重复练习。</p>'+table(['阶段','建议顺序','观察的掌握证据'],[
['一 · 基础落地',refs([2,15,16,17,18,3]),'能自己复述目标，定义变量，完成主循环，并处理边界'],
['二 · 方法迁移',refs([4,7,5,11,9,13]),'能解释关键转化，给出反例排除错误策略，自己设计check'],
['三 · 综合建模',refs([1,6,8,10,12,14]),'能发现不变量或拆分状态，说明各子任务怎样合并、为什么不漏'],
])+'''<h3>一题的学习闭环</h3><p>先独立读题并手推一个小例子；说清自己的模型后再定义变量；写出代码后，用能区分旧思路与新思路的例子、边界情况、最小情况验证。改对以后，由孩子自己讲“我哪里想偏了，下次怎样检查”。</p>
<h3>什么情况下才展开家长分析？</h3><p>先判断卡在题意、模型还是实现。针对这个卡点只读相应的一段，读后回到原题继续。已经会说清的部分直接让她自己做，不再拆成逐行填空。</p>
'''+box('不按“今天做完几题”收尾','若已经疲劳，保留一张思路卡：题目要什么、关键例子、尚未想通的一点。下一次从这个问题继续。原根与二进制分块需要额外的数学连接，可以晚一点系统展开。'),ident='route')

for start in (0,9):
    cards=''.join(f'<div class="question"><b>{p["id"]:02d} · {p["title"]} <span>{p["paper"]}</span></b><p>{e(p["first"])}</p></div>' for p in PROBLEMS[start:start+9])
    add(f'孩子起步问题 · {start+1:02d}—{start+9:02d}', '<p class="small">先完整读原题，再选当前这一题的一个任务。这里不是要一次做完的题单，也不要求照着暗示猜算法名称。</p>'+cards,label='孩子可用 · 独立思考任务',ident=f'questions{start+1}')

add('一题一张：把自己的思路留下来', '''
<p>选题号：________　日期：________　题名：____________________________</p>
<h3>1. 题目最后要我输出什么？</h3><div class="writing"><div></div><div></div></div>
<h3>2. 我的小例子与关键判断</h3><p class="small">哪个例子能区分“我原来的想法”和“现在的想法”？</p><div class="writing"><div></div><div></div><div></div></div>
<h3>3. 变量登记表</h3>
'''+table(['变量','代表什么','初值','何时、怎样改变'],[['　','　','　','　'] for _ in range(3)])+'''
<h3>4. 我准备怎样自测？</h3><div class="writing"><div>关键区分例： </div><div>边界情况： </div><div>最小情况： </div></div>
<h3>5. 改对以后再写</h3><p class="small">我错在哪里？为什么会错？下次怎么防？暂未解决时只记“待复盘”，不急着写结论。</p><div class="writing"><div></div><div></div></div>
''',label='孩子可用 · 空白思路卡',ident='card')

first_parent=len(PAGES)
for p in PROBLEMS:
    count=len(p['parts'])
    for part,(heading,body) in enumerate(p['parts'],1):
        top=''
        if part==1:
            top=f'<div class="problem-statement"><b>题目要什么</b><p>{e(p["task"])}</p><div class="small">范围：{e(p["limits"])}</div></div>'+box('这一题的关键转化',e(p['core']),'intro')
        end=''
        if part==count:
            end=table(['变量角色','含义'],[[e(x),e(y)] for x,y in p['vars']])+f'<p class="small"><b>规模与复杂度：</b>{e(p["cost"])}</p>'+box('交还给孩子的自测方向',e(p['tests']),'task')
        else:
            end=box('接着往下读',f'本题还没有结束。下一页 {p["id"]:02d}.{part+1} 继续解释边界、变量或判定理由。','carry')
        src=f'<div class="source">题源：<a href="{quote(p["paper"]+" 五级.pdf")}#page={p["pages"].split("-")[0]}">{p["paper"]} 五级</a> · 编程第{1 if p["id"]%2 else 2}题 · PDF第{p["pages"]}页（含相关参考）<br>方法组 {p["cat"]}：{CATEGORIES[p["cat"]][0]} ｜ 小题讲义主题：{p["small"]}</div>'
        add(f'{p["id"]:02d}.{part}　{heading}',top+body+end+src,label='家长备课 · 按卡点逐段使用',ident=f'problem{p["id"]}-{part}',parent=True,topic=f'大题{p["id"]:02d} · {p["title"]}',step=f'本题第 {part}/{count} 页')

add('题源与使用边界', '''
<p>本稿逐题核对所提供PDF的题面、输入输出、数据范围、样例及参考内容。题意采用概括转述；标为“教练例”或用于比较方法的小例子，不冒充原卷样例。页码指PDF文件中的实际页面序号。</p>
'''+table(['材料','本讲义题号','原PDF相关页'],[[f'<a href="{quote(a["paper"]+" 五级.pdf")}">{a["paper"]} 五级.pdf</a>',f'{a["id"]:02d}、{b["id"]:02d}',f'{a["pages"].split("-")[0]}—{b["pages"].split("-")[-1]}'] for a,b in zip(PROBLEMS[::2],PROBLEMS[1::2])])+'''
<h3>参考解法与本稿路线</h3><p>同一道题可能有多种有效实现。《黑白格》本稿用滑动窗口解释非负计数的单调性；《最大公因数》直接对固定基准取差。它们与原材料的部分实现方式不同，相关页已明确说明，不要求孩子只认一种代码。</p>
<h3>材料中需合并理解的文字</h3><p>2409《小杨的武器》输入说明写“正整数”，但题面、样例和范围允许负数。本稿按完整条件处理负数，并保留n=1与n≥2的区别。</p>
<h3>学习范围与记录</h3><p>分类、学习顺序、复杂度解释及比较例由本稿整理，不代表官方难度评级或未来命题预测。考纲衔接沿用已核对的《GESP五级小题学习讲义》（依据所提供《考纲.pdf》第22—24页）。本稿不据考试年月或讲解页数判断孩子是否掌握。</p>
''',label='来源说明',ident='sources',parent=True)

CSS='''
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#e9edf1;color:#263640;font-family:"PingFang SC","Microsoft YaHei",sans-serif;font-size:15px;line-height:1.72}a{color:#236b80;text-decoration:none}a:hover{text-decoration:underline}.toolbar{position:sticky;top:0;z-index:10;display:flex;gap:12px;align-items:center;padding:12px 20px;background:#213e4c;color:white;box-shadow:0 2px 10px #0002}.toolbar b{white-space:nowrap}.toolbar select{flex:1;max-width:540px}.toolbar button,.toolbar select{padding:7px 10px;border:0;border-radius:4px;font:inherit;font-size:13px}.page{width:210mm;height:297mm;margin:18px auto;background:#fff;padding:11mm 15mm 16mm;position:relative;break-after:page;box-shadow:0 3px 16px #24344319;scroll-margin-top:70px}.page:last-child{break-after:auto}.page-header{display:flex;align-items:center;justify-content:space-between;gap:14px;border-bottom:2px solid #2d7180;padding-bottom:7px;color:#456473;font-size:11px;line-height:1.5}.page-header .topic{font-size:12px;font-weight:600;color:#244f5f}.label{color:#657b85;font-size:11px;margin-top:13px;letter-spacing:.4px}h1{font-size:23px;line-height:1.38;margin:8px 0 17px;font-weight:650;letter-spacing:-.3px}h3{font-size:16px;line-height:1.5;color:#235565;margin:16px 0 5px}p{margin:9px 0}.content{position:relative}table{width:100%;border-collapse:collapse;font-size:13px;line-height:1.55;margin:12px 0;table-layout:auto}th{text-align:left;background:#eaf2f4;color:#245366;font-weight:600}td,th{border:1px solid #d6e0e4;padding:8px 10px;vertical-align:top}th:first-child{min-width:75px}tr{break-inside:avoid}tbody tr:nth-child(even){background:#fafcfc}.box{background:#f1f5f6;border-left:3px solid #70949c;padding:10px 13px;margin:13px 0;break-inside:avoid}.box>b{display:block;color:#315f6d;margin-bottom:3px;font-size:14px}.box div{font-size:14px;line-height:1.65}.intro{background:#edf6f7;border-color:#2f8691}.task{background:#faf5e9;border-color:#bd964e}.task>b{color:#7c622b}.carry{background:#f5f6f7;border-color:#9ca9af}.diagram,.formula{background:#f4f7fa;padding:12px 15px;border-radius:5px;margin:13px 0;line-height:1.8;font-size:14px}.formula{color:#1e5267;text-align:center;font-weight:600}.small{font-size:12px;line-height:1.65;color:#526873}.source{font-size:10.5px;line-height:1.65;color:#72818a;border-top:1px dashed #cdd6db;padding-top:8px;margin-top:13px}.footer{position:absolute;left:15mm;right:15mm;bottom:6mm;display:flex;justify-content:space-between;font-size:10px;color:#798a93;border-top:1px solid #dce4e7;padding-top:6px}.cover-title{font-size:37px;line-height:1.5;color:#204f5e;font-weight:650;margin:23px 0}.eyebrow{font-size:12px;letter-spacing:2px;color:#6c8790;margin-top:30px}.lead{font-size:17px;line-height:1.9}.stats{display:flex;gap:15px;margin:28px 0}.stats>div{flex:1;border-top:2px solid #acc8d0;padding:10px 0}.stats b{display:block;font-size:29px;color:#236779}.stats span{font-size:12px;color:#647c86}.cover-meta{margin-top:28px;color:#75878f;font-size:12px;line-height:1.9}.problem-statement{border-bottom:1px solid #d8e3e6;padding-bottom:10px;margin-bottom:12px}.problem-statement>b{font-size:13px;color:#66808b}.problem-statement p{margin:4px 0;font-size:14px}.question{padding:9px 0;border-bottom:1px solid #dce5e8}.question b{font-size:14px;color:#295a69}.question span{float:right;color:#8a9aa1;font-size:11px;font-weight:400}.question p{font-size:14px;line-height:1.6;margin:5px 0 2px}.writing>div{height:30px;border-bottom:1px solid #dce4e7;font-size:13px;color:#72868d}.parent-section[hidden]{display:none}#timeline table td{padding:10px 9px}#groups table{font-size:12px}#groups table td{padding:9px}#route table td{font-size:12px}#route a{display:inline}#card h3{margin-top:14px}
@page{size:A4;margin:0}@media print{html{scroll-behavior:auto}body{background:#fff}.toolbar{display:none}.page{margin:0;box-shadow:none}.parent-section[hidden]{display:none}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}@media screen and (max-width:850px){.toolbar{flex-wrap:wrap}.toolbar b{width:100%}.page{margin:12px 0}}
'''

def render(p,i):
    header=e(p['topic']) if p['topic'] else 'GESP C++ 五级 · 历次编程大题'
    right=e(p['step']) if p['step'] else '读题 · 建模 · 验证'
    return f'<section class="page" id="{p["ident"]}" data-parent="{str(p["parent"]).lower()}"><div class="page-header"><span class="topic">{header}</span><span>{right}</span></div><div class="label">{p["label"]}</div><h1>{e(p["title"])}</h1><div class="content">{p["body"]}</div><div class="footer"><span>五级大题学习稿 · 先独立尝试，再按卡点阅读</span><span>{i+1:02d} / {len(PAGES):02d}</span></div></section>'

nav='<optgroup label="总览与学习安排">'
for i,p in enumerate(PAGES):
    if i==first_parent:
        nav+='</optgroup><optgroup label="逐题分析 · 打开后可见家长讲解">'
    nav+=f'<option value="{p["ident"]}">{i+1:02d} · {e(p["topic"]+" — " if p["topic"] else "")}{e(p["title"])}</option>'
nav+='</optgroup>'
script='''
const parents=document.getElementById('parents'),toggle=document.getElementById('toggle');
function showParents(show){parents.hidden=!show;toggle.textContent=show?'收起逐题分析':'展开逐题分析（家长）';}
function visit(id){const target=document.getElementById(id);if(!target)return;if(target.dataset.parent==='true')showParents(true);target.scrollIntoView();document.getElementById('nav').value=id;}
toggle.addEventListener('click',()=>showParents(parents.hidden));
document.getElementById('nav').addEventListener('change',e=>{location.hash=e.target.value;visit(e.target.value)});
document.getElementById('print').addEventListener('click',()=>window.print());
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',()=>visit(a.hash.slice(1))));
if(location.hash)visit(location.hash.slice(1));
'''
html='<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GESP五级历次编程大题总结</title><style>'+CSS+'</style></head><body><div class="toolbar"><b>五级历次大题</b><select id="nav" aria-label="跳转页面">'+nav+'</select><button id="toggle">展开逐题分析（家长）</button><button id="print">打印当前内容</button></div><main>'+''.join(render(p,i) for i,p in enumerate(PAGES[:first_parent]))+'<div id="parents" class="parent-section" hidden>'+''.join(render(p,i) for i,p in enumerate(PAGES[first_parent:],first_parent))+'</div></main><script>'+script+'</script></body></html>'
out=ROOT/'GESP五级历次编程大题总结.html'
out.write_text(html,encoding='utf-8')
(ROOT/'五级大题题源索引.json').write_text(json.dumps([dict(id=p['id'],paper=p['paper'],question=1 if p['id']%2 else 2,title=p['title'],category=CATEGORIES[p['cat']][0],pdf_pages=p['pages'],limits=p['limits'],small_topics=p['small'],handout_pages=[i+1 for i,page in enumerate(PAGES) if page['topic']==f'大题{p["id"]:02d} · {p["title"]}']) for p in PROBLEMS],ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(html=str(out),pages=len(PAGES),overview_pages=first_parent,problem_count=len(PROBLEMS),category_counts=dict(Counter(p['cat'] for p in PROBLEMS))),ensure_ascii=False))
