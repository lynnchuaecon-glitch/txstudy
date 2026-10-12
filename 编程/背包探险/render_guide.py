from html import escape
import json
GROUPS=[(1,7,'营地 A · 从选择到状态'),(8,10,'营地 B · 读懂时间与边界'),(11,20,'营地 C · 条件变了怎样想'),(21,25,'营地 D · 提高组选学'),(26,30,'营地 E · 调试、实战与陪练')]
def group(i):return next(g for a,b,g in GROUPS if a<=i<=b)
def render(lessons, root):
 css=(root/'style.css').read_text()
 js=(root/'guide.js').read_text()
 nav=[];sections=[];N=len(lessons)
 for i,l in enumerate(lessons,1):
  if any(a==i for a,b,g in GROUPS):nav.append('<p class="nav-group">'+group(i)+'</p>')
  nav.append(f'<a href="#lesson-{i}"><span>{i:02d}</span>{escape(l["title"].split("：")[0])}</a>')
  sections.append(f'''<section class="lesson" id="lesson-{i}" aria-labelledby="heading-{i}">
<header class="lesson-head"><p class="kicker">{group(i)} <span>{i:02d} / {N}</span></p><h2 id="heading-{i}">{escape(l['title'])}</h2><p class="goal">这一站带走：{l['goal']}</p><p class="prereq">先修：{l['prereq']}</p></header>
{l['body']}
<div class="practice"><h3>停下来，轮到你想</h3><p>{l['task']}</p><details class="hint"><summary>已经尝试，仍卡住时再看提示</summary><p>{l['hint']}</p></details></div>
<p class="evidence"><strong>这一站的学习证据：</strong>{l['evidence']}</p>
<div class="journal"><label for="note-{i}">我的手推、解释与待复盘</label><textarea id="note-{i}" data-note="{i}" placeholder="由我自己记录。未改对先记待复盘；改对后再写错在哪里、为什么、下次怎么查。"></textarea><div class="print-lines"></div><div class="selfcheck screen-only"><label for="rating-{i}">我的自评</label><select id="rating-{i}" data-rating="{i}"><option value="">暂未自评</option><option value="revisit">需要回访</option><option value="explain">能解释并手推</option><option value="independent">能独立实现与验证</option><option value="transfer">能迁移到新问题</option></select></div></div>
<footer class="lesson-footer screen-only">{'<a href="#lesson-'+str(i-1)+'">← 上一站</a>' if i>1 else '<a href="#home">← 路线首页</a>'}{'<a class="primary" href="#lesson-'+str(i+1)+'">下一站 →</a>' if i<N else '<a class="primary" href="#home">回到路线首页</a>'}</footer></section>''')
 toc=''.join(f'<li><a href="#lesson-{i}"><span>{i:02d}</span> {escape(l["title"])}</a></li>' for i,l in enumerate(lessons,1))
 intro=f'''<section id="home"><header class="hero"><div><p class="eyebrow">THE KNAPSACK EXPEDITION / C++ 学习远征</p><h1>背包探险指南</h1><p class="hero-sub">从一次“拿或不拿”<br>走向提高组的状态设计</p><p>有限的空间里，怎样保留最好的可能？<br>先手推、再建模，让每一格都说得出理由。</p><div class="tags"><span>30 个递进站点</span><span>6 个互动实验</span><span>父女共同探究</span></div></div><div class="hero-art" aria-hidden="true"><div class="bag-label">容量 W = 6</div><div class="bag"><div class="bag-handle"></div><div class="bag-item a">A · 重 2<br><strong>值 3</strong></div><div class="bag-item c">C · 重 4<br><strong>值 5</strong></div></div><p>空间是限制<br>价值是目标</p></div></header>
<div class="intro"><p class="eyebrow">给孩子，也给陪她思考的爸爸</p><h2>先学会问：这一格到底记着什么？</h2><p>本讲从生活中的选择开始，慢慢推导动态规划。不预设已经学过背包、树或单调队列。基础语法是起点；提高内容按先修能力选读，一站可以拆成几次。</p><p>你会看到讲解例子与推导，也会遇到需要停下来独立完成的任务。先预测，再操作实验；先解释，再写代码。提示默认折叠，没有可直接提交的完整 C++ 题解。</p>
<div class="route"><a href="#lesson-1"><small>第一层 · 01—10</small><b>建立模型</b><span>方案 → 状态 → 转移<br>旧层、新层与恰好要求</span></a><a href="#lesson-11"><small>第二层 · 11—20</small><b>改变条件</b><span>次数、目标、组与维度<br>恢复名单与最优计数</span></a><a href="#lesson-21"><small>第三层 · 21—25</small><b>提高选学</b><span>依赖与树合并<br>队列、位集与折半</span></a></div>
<aside class="callout"><strong>第一次只走一个小闭环</strong><p>推荐先用三张卡片完成第 1—3 站中的一个完整任务。首次可用 20—35 分钟观察状态；如果能独立枚举，就继续研究状态，不反复问已经会的细节。今天不必走到一维模板，更不必读完提高部分。</p></aside>
<p><a href="#lesson-29">爸爸先读：陪练与分层验收</a> · <a href="#lesson-28">真实题目路线</a> · <a href="#lesson-30">方法卡与空白反思</a></p><p class="context-note">本次学习背景：2026-10-11 开始父女一起参加 ABC 479；B 题在爸爸讲解后孩子自己 AC，C 题基本没有时间看。B 的考点是最长连续段，讲义以“状态含义”连接到背包，不据此诊断具体错因。<a href="https://atcoder.jp/contests/abc479/tasks/abc479_b">核实原题</a>。</p>
<div class="storage-note screen-only"><p id="storage-status" role="status">笔记与自评只保存在当前浏览器，建议定期导出；不会自动标记掌握。</p><label class="import-label">导入备份 <input id="import-notes" type="file" accept="application/json,.json"></label></div></div>
<div class="full-toc"><h2>整条路线</h2><ol>{toc}</ol></div>
<div class="print-intro">打印版包含完整正文与独立任务；互动实验请在 HTML 中操作，练习提示保持折叠。空白处由孩子自己记录。编制与题源核对：2026-10-12。</div></section>'''
 html=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="父女共学背包主题讲义：从枚举、状态、0/1背包逐层深入到树上背包、单调队列、位集与折半搜索。"><title>背包探险指南 · 从 0 到提高组</title><style>{css}</style></head><body>
<a class="skip" href="#content">跳到学习内容</a><aside class="sidebar screen-only"><a class="brand" href="#home">THE KNAPSACK EXPEDITION</a><h2>背包探险指南</h2><p>有限的空间，无限的思考。</p><nav class="toc" aria-label="学习站点">{''.join(nav)}</nav><p id="progress">已自评 0 / {N} 站 · 不等于掌握率</p><a class="back-guide" href="../贪心探险/贪心探险指南.html">回看贪心探险 →</a></aside>
<main><div class="toolbar screen-only"><button id="menu" aria-expanded="false" aria-controls="mobile-nav">目录</button><span id="crumb">路线首页</span><div class="actions"><a href="#home">首页</a><button id="all-mode" aria-pressed="false">全文阅读</button><button id="export-notes">导出笔记</button><button id="print-guide">打印讲义</button></div></div><nav id="mobile-nav" class="screen-only" aria-label="手机目录" hidden>{''.join(nav)}</nav><div class="content" id="content"><noscript><p>当前未启用 JavaScript，可完整阅读正文，互动实验与笔记保存暂不可用。</p></noscript>{intro}{''.join(sections)}<p class="page-footer">孩子错题库 · 背包探险 / 2026-10-12<br>学习材料已准备，不代表知识已掌握。示例与任务由本讲编制，外部题源在对应站点链接。</p></div></main><script>{js}</script></body></html>'''
 (root/'背包探险指南.html').write_text(html)
 (root/'lessons.json').write_text(json.dumps(lessons,ensure_ascii=False,indent=2))
 print(f'Built {N} lessons; {len(html.encode())} bytes')
