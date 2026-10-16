from pathlib import Path
from html import escape
import json
from lessons import prefix, twin, table, p
from lessons_structures import structures

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
CSS=(ROOT/'style.css').read_text()
JS=(ROOT/'models.js').read_text()+'\n'+(ROOT/'guide.js').read_text()
GUIDES=[
 dict(slug='prefix-difference',folder='前缀和差分探险',title='前缀和与差分探险指南',subtitle='一张累计账单，两处变化标记。',lessons=prefix,route='先完成 01～08 的一维基础；09～11 为组合与二维选学；12 做独立验收。',links=[('二分：差分判定','../二分探险/二分探险指南.html#lesson-21'),('二分：前缀和应用','../二分探险/二分探险指南.html#lesson-22')]),
 dict(slug='two-pointers',folder='双指针探险',title='双指针探险指南',subtitle='每次向前，都要知道为什么。',lessons=twin,route='01～05 学会两队与两端扫描；06～09 学窗口及适用条件；10 为计数选学；11～12 做复杂度与迁移验收。',links=[('贪心：排序与匹配','../贪心探险/贪心探险指南.html#lesson-7'),('链表：快慢指针','../链表探险/链表探险指南.html#lesson-18')]),
 dict(slug='stack-queue',folder='栈与队列探险',title='栈与队列探险指南',subtitle='下一位该是谁？先把顺序想明白。',lessons=structures,route='01～08 建立栈与普通队列基础；09～12 是按先修能力选择的拓展；13 做独立验收。',links=[('递归：调用栈','../递归探险/递归探险指南.html#lesson-4'),('贪心：优先队列','../贪心探险/贪心探险指南.html#lesson-13')]),
]

def section(i,item,n):
    return f'''<section class="lesson" id="lesson-{i}" aria-labelledby="heading-{i}">
<header><div class="eyebrow">{i:02} / {n:02} · {item['level']}</div><h2 id="heading-{i}">{item['title']}</h2><p class="goal">这一站带走：{item['goal']}</p><p class="prereq">先修：{item['prereq']}</p></header>
{item['body']}
<div class="practice"><h3>停下来，轮到你完成</h3><p>{item['task']}</p>
<details class="hint"><summary>尝试后仍卡住 · 提示一</summary><p>{item['hints'][0]}</p></details>
<details class="hint"><summary>只在需要时 · 提示二</summary><p>{item['hints'][1]}</p></details>
<div class="tests"><h3>三类自测</h3><ul>{''.join('<li>'+x+'</li>' for x in item['tests'])}</ul></div>
<details class="coach"><summary>家长／教练核对 · 请先让孩子尝试</summary><p>{item['coach']}</p></details></div>
<div class="journal"><h3>我的过程与证据</h3><label for="stage-{i}">这一站，我目前：</label><select id="stage-{i}" data-stage="{i}"><option value="">尚未自评</option><option value="hand">能解释并手推</option><option value="help">有提示时能完成</option><option value="independent">能独立实现并自测</option><option value="transfer">能在新情境中迁移</option></select>
<label for="note-{i}">记录手推、变量、测试或待复盘问题；改对后由我自己写反思。</label><textarea id="note-{i}" data-note="{i}" placeholder="未完成时：我试了什么？卡在哪里？&#10;改对后：我错在哪里？为什么会错？下次怎样防？"></textarea><p class="muted">阅读、点实验或展开提示不会自动改变自评。笔记仅保存在当前浏览器，换设备前请导出。</p><div class="print-only print-stage">尚未自评</div><div class="print-only print-note"></div></div>
<nav class="lesson-footer" aria-label="前后站"><a href="{'#home' if i==1 else '#lesson-'+str(i-1)}">← {'学习路线' if i==1 else '上一站'}</a><a href="{'#home' if i==n else '#lesson-'+str(i+1)}">{'回到学习路线' if i==n else '下一站 →'}</a></nav></section>'''

def build_guide(g):
    ls=g['lessons'];n=len(ls)
    navtitle={'prefix-difference':'前缀和与差分','two-pointers':'双指针探险','stack-queue':'栈与队列探险'}[g['slug']]
    config=json.dumps(dict(title=g['title'],key=g['slug']+'-adventure-v1',count=n),ensure_ascii=False)
    toc='<a href="#home"><span class="num">⌂</span>出发与路线</a>'+''.join(f'<a href="#lesson-{i}"><span class="num">{i:02}</span><span>{x["title"]}</span></a>' for i,x in enumerate(ls,1))
    index='<ol class="station-list">'+''.join(f'<li><a href="#lesson-{i}">{x["title"]}</a> <small>· {x["level"]}</small></li>' for i,x in enumerate(ls,1))+'</ol>'
    count_labs=sum(x['body'].count('data-lab=') for x in ls)
    intro=f'''<div id="home"><header class="hero"><div class="eyebrow">ALGORITHM FIELD GUIDE · 秋季学期 / 2026</div><h1>{g['title']}</h1><p>{g['subtitle']}</p><div class="tags"><span class="tag">{n} 站 · 按进度选用</span><span class="tag">{count_labs} 个逐步实验</span><span class="tag">手推 → 实现 → 三类自测</span></div></header>
<section class="intro"><h2>一站可以分几次，关键思考留给你。</h2><p>{g['route']}</p><p>从学校当前题目或一个小任务进入。先说明题意和模型，再决定变量，最后自己写代码。每站只有一个核心任务；卡住时再逐级看提示，不要求一口气答完一串零碎问题。</p><aside class="callout">这里的“基础稳定后选学”是教学分层，不是额外的本学期必做清单。疲劳时停在一张简短思路卡，隔天先手推再重做。</aside><a href="#lesson-1">从第 1 站出发 →</a>
<h3>这份讲义的路线</h3>{index}
<details><summary>家长／教练：怎样使用与验收</summary><p>先完整看题和孩子的尝试，指出已经成立的部分与当前核心问题，再让孩子独立完成一个有意义的任务。正文里的小例子用于解释概念；练习、代码和正式反思由孩子完成。每站的核对默认折叠，只在她尝试后用来判断依据。</p><p>不是每站都要写完整程序；建模站以手推和解释为产出，工具与验收站再接实现。自测至少包括区分新旧思路的例子、最小输入和边界。记录提示程度；讲义已准备不代表孩子已学会。</p></details>
<details><summary>阅读、笔记与打印</summary><p>分站阅读适合一次聚焦；展开全文方便备课。笔记与自评只保存在当前浏览器，导出 JSON 可以备份；导入同一讲义时保留冲突的两份文字，已有自评优先。打印会包含全部站点及当前笔记，实验控件不打印；折叠提示和核对不打印，手动展开的会打印。</p><p>关闭 JavaScript 后仍能阅读全部正文；分站导航、实验与笔记保存需启用 JavaScript。HTML 内嵌样式和脚本，单文件可离线阅读，跳转其他讲义依赖原目录结构。</p></details>
<p class="muted">接续阅读：{' · '.join(f'<a href="{url}">{title}</a>' for title,url in g['links'])}</p></section></div>'''
    html=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{escape(g['subtitle'])}"><title>{g['title']}</title><style>{CSS}</style></head><body>
<a class="skip" href="#main">跳到正文</a><aside class="sidebar" id="sidebar"><div class="eyebrow">THINK · MODEL · VERIFY</div><h2>{navtitle}</h2><p>一轮只推进一个核心任务。</p><div class="progress"><span id="progress-fill"></span></div><div class="progress-label" id="progress-label">尚未自评</div><nav class="toc" aria-label="站点目录">{toc}</nav><div class="side-end"><a href="../秋季学期讲义/秋季学期讲义总入口.html">← 秋季学期讲义总入口</a></div></aside>
<main class="main" id="main"><div class="toolbar"><button id="menu" class="menu-button" aria-controls="sidebar" aria-expanded="false">目录</button><button id="all">展开全文</button><button id="print">打印／存为 PDF</button><button id="export">导出笔记</button><button id="import">导入笔记</button><input id="import-file" type="file" accept=".json,application/json" hidden><span class="status" id="save-status" role="status">先手推，再点实验；笔记可导出备份。</span></div><div class="content">{intro}{''.join(section(i,x,n) for i,x in enumerate(ls,1))}<footer class="footer">2026-10-16 整理 · 对照家长提供的秋季学期清单补齐材料。例子与任务为本地原创教学设计；不替代实际学习证据。</footer></div></main><script type="application/json" id="guide-config">{config}</script><script>{JS}</script></body></html>'''
    dest=BASE/g['folder']/(g['title']+'.html');dest.parent.mkdir(exist_ok=True);dest.write_text(html)
    return dest

def build_index():
    rows=[
      ['递归','必讲（当前） · 2～3 次','<a href="../递归探险/递归探险指南.html">递归探险指南</a>','已有原理、边界、返回与递推衔接；跟学校当前题目验证。'],
      ['高精度加减乘','可跳 · 0～1 次','<a href="../高精度加法-从数楼梯出发.html">加法专篇</a>；<a href="../五级/GESP五级小题学习讲义.html#lesson25-step1">五级 T25～T27</a>','专题内已补 <a href="../五级/GESP五级小题学习讲义.html#lesson26-practice">减法</a>、<a href="../五级/GESP五级小题学习讲义.html#lesson27-practice">乘法</a> 独立实现与验收。'],
      ['二分','必讲·多练 · 3～5 次','<a href="../二分探险/二分探险指南.html">二分探险指南</a>','已有整数二分、边界和二分答案；组合应用可先回读新基础讲义。'],
      ['nlogn 排序','可跳 · 0～1 次','<a href="../五级/GESP五级小题学习讲义.html#lesson18-step1">五级 T18～T22</a>','专题内已补 <a href="../五级/GESP五级小题学习讲义.html#lesson19-practice">归并</a>、<a href="../五级/GESP五级小题学习讲义.html#lesson20-practice">快排</a> 验收；快排最坏 O(n²)，标题不代表所有输入保证。'],
      ['筛法','可跳 · 0～2 次','<a href="../五级/GESP五级小题学习讲义.html#lesson9-step1">五级 T09～T10</a>','专题内已补 <a href="../五级/GESP五级小题学习讲义.html#lesson9-practice">埃氏筛</a>、<a href="../五级/GESP五级小题学习讲义.html#lesson10-practice">线性筛</a> 验收。'],
      ['前缀和、差分','必讲 · 2～3 次','<a href="../前缀和差分探险/前缀和与差分探险指南.html">新建基础讲义 · 12 站</a>','01～08 一维基础；09～11 选学；12 验收。'],
      ['双指针／栈队列','必讲 · 合计 2～3 次','<a href="../双指针探险/双指针探险指南.html">新建双指针 · 12 站</a><br><a href="../栈与队列探险/栈与队列探险指南.html">新建栈与队列 · 13 站</a>','分开准备材料，共用学校给出的参考课时；站数不等于课时或作业量。'],
    ]
    cards=''.join(f'<a href="../{g["folder"]}/{g["title"]}.html"><small>{len(g["lessons"])} 个学习单元</small><b>{g["title"]}</b><p>{g["subtitle"]}</p></a>' for g in GUIDES)
    html=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>秋季学期讲义总入口</title><style>{CSS}</style></head><body class="index-page"><main class="main"><div class="toolbar"><span class="eyebrow">2026 秋季 · 家庭与学校同步</span><button onclick="window.print()">打印清单</button></div><div class="content"><header class="hero"><div class="eyebrow">LEARNING ROUTE / 2026.10.16</div><h1>秋季学期讲义总入口</h1><p>跟着学校当前专题，找到需要的那一站。<br>资料补齐了，学习从一个小闭环开始。</p><div class="tags"><span class="tag">3 套新讲义 · 37 站</span><span class="tag">6 项补充已并入五级原讲义</span><span class="tag">5 个逐步实验</span></div></header><section class="intro"><h2>先选今天学校正在讲的内容</h2><p>下表的优先级、参考课时来自家长于 2026-10-16 提供的老师授课清单；它们是学校的安排参考，不是新增家庭课量。沿用“先必讲、后可跳”的次序，具体进度看孩子的独立表现。</p>{table(['学校内容','老师安排','讲义入口','本次补充与使用范围'],rows)}<aside class="callout">“已有讲义／本次新建”描述材料状态，不表示孩子已经学习或掌握。每份新讲义的自评和反思初始为空；一次只推进一个当前核心任务。</aside></section><section class="intro"><h2>这次新增的阅读入口</h2><div class="route">{cards}</div></section><section class="intro"><h2>前置基础补好，再接回综合题</h2><ol><li>先完成一维前缀和与差分，再接二分中的“订单第一次失败”与“最大平均值”。</li><li>先完成有序合并、双指针匹配与窗口，再接归并排序、贪心匹配和滑动窗口问题。</li><li>先完成栈与普通队列，再接递归返回、括号、基础 BFS；单调栈与单调队列放在先修稳定以后。</li></ol><p>原来把前缀和、栈队列初学放到 1 月的安排已调整为本学期随学校同步；1 月保留查漏与搜索衔接。每周沿用既有总量，学校讲到哪一项，就替换当前主专题，不叠加三套新作业。</p><details><summary>给家长的验收方式</summary><p>先看一份手推和变量表，再看独立实现。请孩子说明为什么不漏答案、何时停止、哪些输入不能用当前方法。至少验证关键区分例、最小输入和边界；隔几天换一个小情境复做。若仍需提示，记录提示程度，回到核心卡点。</p><p>高精度、排序和筛法先读五级原讲义，再做同一专题中的“独立实现与自测”页。老师标为“可跳”只说明本学期课堂安排；家庭按已定阶段目标查漏，不据此认定这些知识无需学习，也不在此新增未经核对的考试承诺。</p></details></section><footer class="footer">新增内容为原创教学材料；教师清单是本次范围依据。已有链表、贪心、背包、动态规划讲义继续保留，按需要取用。</footer></div></main></body></html>'''
    (ROOT/'秋季学期讲义总入口.html').write_text(html)

if __name__=='__main__':
    paths=[build_guide(g) for g in GUIDES];build_index()
    print(json.dumps({'files':[str(x) for x in paths],'new_lessons':sum(len(g['lessons']) for g in GUIDES[:3]),'integrated_practice_topics':[9,10,19,20,26,27]},ensure_ascii=False))
