#!/usr/bin/env python3
"""Build a self-contained study index for ABC423 through ABC472.

The report intentionally contains concise problem/editorial extracts and knowledge
labels, not full statements or solution code. Official AtCoder pages remain the
source of truth and are linked from every row.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import html
import json
import math
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import requests


FIRST_CONTEST = 423
LAST_CONTEST = 472
LETTERS = "ABCDEFG"
ATCODER = "https://atcoder.jp"
DEFAULT_OUTPUT = Path("AtCoder-ABC近50期-A-G题目归纳.html")
CACHE_DIR = Path("/tmp/atcoder-abc-423-472-cache")
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0 Safari/537.36"
)


BLOCK_TAGS = {
    "p", "div", "section", "h1", "h2", "h3", "h4", "li", "ul", "ol",
    "pre", "br", "tr", "td", "th",
}


def strip_html(source: str) -> str:
    """Convert the small official HTML fragments we use into readable text."""
    source = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", source, flags=re.I | re.S)
    source = re.sub(
        rf"</?(?:{'|'.join(BLOCK_TAGS)})\b[^>]*>", "\n", source, flags=re.I
    )
    source = re.sub(r"<[^>]+>", " ", source)
    source = html.unescape(source)
    source = source.replace("\\(", "").replace("\\)", "")
    source = source.replace("\\[", "").replace("\\]", "")
    source = re.sub(r"[ \t\r\f\v]+", " ", source)
    source = re.sub(r" *\n *", "\n", source)
    source = re.sub(r"\n{2,}", "\n", source)
    return source.strip()


def fetch(url: str, cache_key: str, retries: int = 4) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{cache_key}.html"
    if cache_path.exists() and cache_path.stat().st_size > 500:
        return cache_path.read_text(encoding="utf-8")

    error = None
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": USER_AGENT, "Accept-Language": "en"},
                timeout=30,
            )
            if response.status_code in {403, 429}:
                time.sleep(3 * (2 ** attempt))
                continue
            response.raise_for_status()
            response.encoding = "utf-8"
            cache_path.write_text(response.text, encoding="utf-8")
            return response.text
        except requests.RequestException as exc:
            error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {error}")


def compact_sentences(text: str, limit: int = 520) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"Score\s*:\s*\d+\s*points?", "", text, flags=re.I).strip()
    if len(text) <= limit:
        return text

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chosen: list[str] = []
    for sentence in sentences[:2]:
        if sentence:
            chosen.append(sentence)
    objective = re.compile(
        r"\b(find|determine|count|calculate|compute|print|output|answer|whether|"
        r"minimum|maximum|possible|number of ways)\b",
        re.I,
    )
    for sentence in sentences[2:]:
        if objective.search(sentence):
            chosen.append(sentence)
            break
    result = " ".join(chosen).strip()
    if len(result) > limit:
        result = result[: limit - 1].rsplit(" ", 1)[0] + "…"
    return result


def extract_problem_page(source: str) -> tuple[str, str]:
    statement_match = re.search(
        r"<h3>Problem Statement</h3>(.*?)</section>", source, flags=re.I | re.S
    )
    constraints_match = re.search(
        r"<h3>Constraints</h3>(.*?)</section>", source, flags=re.I | re.S
    )
    if not statement_match:
        raise ValueError("English problem statement was not found")
    statement = compact_sentences(strip_html(statement_match.group(1)))
    constraints = strip_html(constraints_match.group(1)) if constraints_match else ""
    constraints = re.sub(r"\n", " · ", constraints)
    if len(constraints) > 260:
        constraints = constraints[:257].rsplit(" ", 1)[0] + "…"
    return statement, constraints


def extract_task_links(contest: int, source: str) -> dict[str, dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    pattern = re.compile(
        rf'<a\s+href="(/contests/abc{contest}/tasks/(abc{contest}_([a-g])))"[^>]*>'
        r"(.*?)</a>",
        flags=re.I | re.S,
    )
    for match in pattern.finditer(source):
        letter = match.group(3).upper()
        title_text = strip_html(match.group(4))
        title_text = re.sub(rf"^{letter}\s*[-.]\s*", "", title_text).strip()
        found[letter] = {
            "id": match.group(2).lower(),
            "url": ATCODER + match.group(1),
            "title": title_text,
        }
    return found


def extract_editorial_links(source: str) -> dict[str, str]:
    results: dict[str, str] = {}
    headings = list(
        re.finditer(r"<h3>\s*([A-G])\s*-.*?</h3>", source, flags=re.I | re.S)
    )
    for index, heading in enumerate(headings):
        letter = heading.group(1).upper()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(source)
        block = source[heading.end():end]
        anchors = re.findall(
            r'<a\s+href="(/contests/[^"?]+/editorial/\d+)"[^>]*>(.*?)</a>',
            block,
            flags=re.I | re.S,
        )
        if not anchors:
            continue
        english = [href for href, label in anchors if strip_html(label).strip() == "Editorial"]
        selected = english[0] if english else anchors[0][0]
        results[letter] = ATCODER + selected + "?lang=en"
    return results


def extract_editorial_text(source: str) -> str:
    match = re.search(
        r'<hr\s+class="mt-1"[^>]*>\s*(.*?)<div\s+class="clearfix"',
        source,
        flags=re.I | re.S,
    )
    if not match:
        return ""
    text = strip_html(match.group(1))
    text = re.split(r"\bSample code\b", text, maxsplit=1, flags=re.I)[0]
    return text[:12000]


TAG_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("网络流 / 最小割", (r"maximum flow", r"max[- ]flow", r"minimum cut", r"min[- ]cut", r"dinic")),
    ("二分图匹配", (r"bipartite matching", r"maximum matching", r"hall.?s theorem")),
    ("强连通分量", (r"strongly connected", r"\bscc\b", r"kosaraju", r"tarjan")),
    ("树链剖分", (r"heavy.light decomposition", r"\bhld\b")),
    ("点分治", (r"centroid decomposition",)),
    ("LCA / 倍增", (r"lowest common ancestor", r"binary lifting", r"doubling technique")),
    ("后缀数组 / LCP", (r"suffix array", r"lcp array")),
    ("字符串算法", (r"z.algorithm", r"kmp", r"rolling hash", r"aho.corasick", r"failure function")),
    ("字典树", (r"\btrie\b", r"prefix tree")),
    ("卷积 / NTT", (r"convolution", r"number theoretic transform", r"\bntt\b", r"\bfft\b")),
    ("矩阵快速幂", (r"matrix exponentiation", r"matrix power")),
    ("线性递推", (r"linear recurrence", r"kitamasa", r"berlekamp")),
    ("懒标记线段树", (r"lazy segment tree", r"lazy propagation")),
    ("线段树", (r"segment tree",)),
    ("树状数组", (r"binary indexed tree", r"fenwick")),
    ("并查集", (r"disjoint set", r"union.find", r"\bdsu\b")),
    ("最短路", (r"dijkstra", r"bellman.ford", r"floyd.warshall", r"shortest path")),
    ("拓扑排序", (r"topological sort", r"topological order")),
    ("BFS / DFS", (r"breadth.first search", r"depth.first search", r"\bbfs\b", r"\bdfs\b")),
    ("树上 DP", (r"tree dp", r"rerooting", r"re.rooting")),
    ("数位 DP", (r"digit dp",)),
    ("状压 DP", (r"bitmask dp", r"subset dp", r"dp over subsets")),
    ("动态规划", (r"dynamic programming", r"\bdp\[", r"\bdp\b")),
    ("博弈论", (r"grundy", r"nim.sum", r"game theory", r"winning position")),
    ("概率 / 期望", (r"expected value", r"expectation", r"probability", r"randomly")),
    ("组合计数", (r"binomial", r"\bcombinations\b", r"combination (?:count|formula|coefficient)", r"factorial", r"inclusion.exclusion", r"number of ways")),
    ("数论", (r"greatest common divisor", r"\bgcd\b", r"\blcm\b", r"prime factor", r"sieve", r"divisor", r"euler.?s phi")),
    ("模运算", (r"modulo", r"modular", r"998244353", r"1000000007", r"modint")),
    ("计算几何", (r"convex hull", r"cross product", r"computational geometry", r"euclidean distance", r"polygon")),
    ("坐标压缩", (r"coordinate compression", r"compress the coordinates")),
    ("二分答案", (r"binary search on the answer", r"parametric search")),
    ("二分查找", (r"binary search", r"lower.bound", r"upper.bound")),
    ("双指针 / 滑动窗口", (r"two.pointer", r"sliding window", r"尺取")),
    ("前缀和 / 差分", (r"prefix sum", r"cumulative sum", r"difference array", r"\bimos\b")),
    ("优先队列", (r"priority queue", r"\bheap\b")),
    ("单调栈", (r"monotonic stack",)),
    ("有序集合", (r"multiset", r"ordered set", r"balanced binary search tree")),
    ("哈希 / 映射", (r"hash map", r"hash table", r"dictionary", r"frequency map")),
    ("贪心", (r"greedy", r"take .* in .* order")),
    ("排序", (r"sorting", r"sort the", r"sorted order", r"sort\(")),
    ("枚举 / 暴力", (r"brute force", r"enumerat", r"try all", r"all possibilities")),
    ("图论", (r"directed graph", r"undirected graph", r"vertices", r"vertex set", r"edges")),
    ("树", (r"rooted tree", r"subtree", r"tree with", r"tree of")),
    ("网格", (r"\bgrid\b", r"adjacent cells", r"row and column")),
    ("字符串", (r"you are given (?:a )?string", r"given strings? [a-z]", r"substring", r"palindrome", r"lexicograph", r"string obtained")),
    ("模拟", (r"simulation", r"simulate", r"perform the operation", r"repeat the following")),
]


def infer_tags(letter: str, title: str, statement: str, editorial: str) -> list[str]:
    corpus = f"{title}\n{statement}\n{editorial}".lower()
    tags: list[str] = []
    for label, patterns in TAG_RULES:
        if any(re.search(pattern, corpus, flags=re.I) for pattern in patterns):
            tags.append(label)

    # Remove broad labels when a more precise member of the same family exists.
    if "网络流 / 最小割" in tags or "强连通分量" in tags or "最短路" in tags:
        tags = [tag for tag in tags if tag != "图论"]
    if "树上 DP" in tags:
        tags = [tag for tag in tags if tag != "动态规划"]
    if "数位 DP" in tags or "状压 DP" in tags:
        tags = [tag for tag in tags if tag != "动态规划"]
    if "懒标记线段树" in tags:
        tags = [tag for tag in tags if tag != "线段树"]
    if "二分答案" in tags:
        tags = [tag for tag in tags if tag != "二分查找"]
    if "网格" in tags and "字符串" in tags and not re.search(
        r"substring|palindrome|lexicograph|string obtained|replace every character", corpus
    ):
        tags = [tag for tag in tags if tag != "字符串"]

    fallback = {
        "A": ["基础语法 / 条件判断"],
        "B": ["模拟 / 枚举"],
        "C": ["实现 / 枚举"],
        "D": ["算法建模"],
        "E": ["进阶算法"],
        "F": ["进阶算法"],
        "G": ["综合算法"],
    }
    if not tags:
        tags.extend(fallback[letter])
    elif letter in "AB" and all(tag not in tags for tag in ("字符串", "网格", "排序")):
        tags.append("基础实现")
    return tags[:5]


def extract_editorial_hint(text: str, tags: Iterable[str], limit: int = 360) -> str:
    if not text:
        return "官方英文题解暂无可稳定提取的摘要，请从题目链接进入 Editorial 查看。"
    clean = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", clean)
    cues = (
        "we can", "it is sufficient", "thus", "therefore", "hence", "using",
        "the answer", "time complexity", "maintain", "compute", "consider",
        "dynamic programming", "binary search", "greedy", "minimum cut",
    )
    selected: list[str] = []
    for sentence in sentences:
        lowered = sentence.lower()
        if any(cue in lowered for cue in cues) and 25 <= len(sentence) <= 260:
            selected.append(sentence)
        if len(" ".join(selected)) >= limit * 0.72 or len(selected) >= 2:
            break
    if not selected:
        selected = [sentence for sentence in sentences if 25 <= len(sentence) <= 260][:2]
    hint = " ".join(selected).strip()
    if len(hint) > limit:
        hint = hint[: limit - 1].rsplit(" ", 1)[0] + "…"
    return hint or f"重点识别：{'、'.join(tags)}。"


def displayed_difficulty(value: int | None) -> int | None:
    if value is None:
        return None
    if value < 400:
        value = round(400 / math.exp(1 - value / 400))
    return int(value)


def difficulty_band(value: int | None) -> tuple[str, str]:
    if value is None:
        return "暂无", "unknown"
    thresholds = [
        (400, "灰"), (800, "棕"), (1200, "绿"), (1600, "青"),
        (2000, "蓝"), (2400, "黄"), (2800, "橙"), (10**9, "红"),
    ]
    for threshold, label in thresholds:
        if value < threshold:
            return label, label
    return "红", "红"


def load_models() -> dict[str, dict]:
    url = "https://kenkoooo.com/atcoder/resources/problem-models.json"
    cache_path = CACHE_DIR / "problem-models.json"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=45)
        response.raise_for_status()
        models = response.json()
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(models), encoding="utf-8")
        return models
    except (requests.RequestException, json.JSONDecodeError) as exc:
        for fallback in (cache_path, Path("/tmp/atcoder-models.json")):
            if fallback.exists():
                try:
                    print(f"Warning: using cached difficulty data after: {exc}", file=sys.stderr)
                    return json.loads(fallback.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    pass
        print(f"Warning: difficulty data unavailable and no cache exists: {exc}", file=sys.stderr)
        return {}


def scrape_contest(contest: int) -> tuple[int, dict[str, dict[str, str]], dict[str, str]]:
    task_html = fetch(
        f"{ATCODER}/contests/abc{contest}/tasks?lang=en",
        f"abc{contest}-tasks",
    )
    tasks = extract_task_links(contest, task_html)
    editorial_html = fetch(
        f"{ATCODER}/contests/abc{contest}/editorial?lang=en",
        f"abc{contest}-editorial-list",
    )
    editorials = extract_editorial_links(editorial_html)
    return contest, tasks, editorials


def scrape_problem(item: dict) -> dict:
    source = fetch(item["url"] + "?lang=en", item["id"] + "-problem")
    statement, constraints = extract_problem_page(source)
    editorial_text = ""
    if item.get("editorial_url"):
        try:
            editorial_source = fetch(
                item["editorial_url"], item["id"] + "-editorial-detail"
            )
            editorial_text = extract_editorial_text(editorial_source)
        except Exception as exc:  # The report can still use the official task page.
            item["editorial_error"] = str(exc)
    tags = infer_tags(item["letter"], item["title"], statement, editorial_text)
    item.update(
        statement=statement,
        constraints=constraints,
        tags=tags,
        editorial_hint=extract_editorial_hint(editorial_text, tags),
    )
    return item


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_report(problems: list[dict], generated_at: str) -> str:
    tag_counts = Counter(tag for problem in problems for tag in problem["tags"])
    by_letter: dict[str, Counter] = defaultdict(Counter)
    for problem in problems:
        by_letter[problem["letter"]].update(problem["tags"])

    top_tags = tag_counts.most_common(18)
    max_tag_count = max((count for _, count in top_tags), default=1)
    tag_options = "".join(
        f'<option value="{esc(tag)}">{esc(tag)} ({count})</option>'
        for tag, count in sorted(tag_counts.items(), key=lambda pair: (-pair[1], pair[0]))
    )
    contest_options = "".join(
        f'<option value="{contest}">ABC{contest}</option>'
        for contest in range(LAST_CONTEST, FIRST_CONTEST - 1, -1)
    )

    bars = "".join(
        f'''<button class="topic-bar" type="button" data-topic="{esc(tag)}" title="筛选：{esc(tag)}">
          <span>{esc(tag)}</span><i style="width:{count / max_tag_count * 100:.1f}%"></i><b>{count}</b>
        </button>'''
        for tag, count in top_tags
    )

    letter_rows = "".join(
        f'''<tr>
          <th><span class="letter-badge letter-{letter.lower()}">{letter}</span></th>
          <td>{"、".join(f"{esc(tag)} {count}" for tag, count in by_letter[letter].most_common(6))}</td>
          <td>{esc({"A":"基本语法与准确读题","B":"模拟、枚举与基础容器","C":"综合实现与第一层算法","D":"核心算法分界线","E":"进阶数据结构与建模","F":"高阶算法组合","G":"综合难题与专题算法"}[letter])}</td>
        </tr>'''
        for letter in LETTERS
    )

    problem_rows: list[str] = []
    for problem in problems:
        difficulty = problem["difficulty"]
        band_label, band_class = difficulty_band(difficulty)
        difficulty_text = "暂无估值" if difficulty is None else f"{difficulty} · {band_label}"
        tags_html = "".join(
            f'<button class="tag" type="button" data-topic="{esc(tag)}">{esc(tag)}</button>'
            for tag in problem["tags"]
        )
        search_blob = " ".join(
            [problem["title"], problem["statement"], *problem["tags"]]
        ).lower()
        editorial_link = (
            f'<a href="{esc(problem["editorial_url"])}" target="_blank" rel="noopener">官方题解</a>'
            if problem.get("editorial_url") else "<span>题解链接暂无</span>"
        )
        problem_rows.append(
            f'''<article class="problem-row" data-problem="{problem["id"]}" data-contest="{problem["contest"]}" data-letter="{problem["letter"]}" data-tags="{esc("|".join(problem["tags"]))}" data-band="{band_class}" data-status="todo" data-search="{esc(search_blob)}">
              <div class="problem-main">
                <div class="problem-id"><span class="letter-badge letter-{problem["letter"].lower()}">{problem["letter"]}</span><b>ABC{problem["contest"]}</b></div>
                <div class="problem-body">
                  <div class="problem-title"><a href="{esc(problem["url"])}" target="_blank" rel="noopener">{esc(problem["title"])}</a><span class="difficulty diff-{band_class}">{esc(difficulty_text)}</span><span class="practice-pill status-todo">未做</span></div>
                  <p>{esc(problem["statement"])}</p>
                  <div class="tags">{tags_html}</div>
                </div>
                <button class="toggle" type="button" aria-expanded="false" aria-label="展开题目详情" title="展开题目详情">＋</button>
              </div>
              <div class="problem-detail" hidden>
                <div class="reference-grid">
                  <div><b>约束线索</b><p>{esc(problem["constraints"] or "官方页未提取到英文约束。")}</p></div>
                  <div><b>官方题解抓手（英文）</b><p>{esc(problem["editorial_hint"])}</p></div>
                  <div class="source-links"><a href="{esc(problem["url"])}" target="_blank" rel="noopener">官方题目</a>{editorial_link}</div>
                </div>
                <form class="practice-editor" data-problem="{problem["id"]}">
                  <div class="practice-heading"><b>练题记录</b><span class="practice-tools"><span class="save-state" aria-live="polite">自动保存</span><button type="button" class="clear-record">清空本题</button></span></div>
                  <div class="status-segments" role="group" aria-label="ABC{problem["contest"]} {problem["letter"]} 完成状态">
                    <button type="button" class="active" data-value="todo">未做</button>
                    <button type="button" data-value="doing">练习中</button>
                    <button type="button" data-value="ac">AC</button>
                  </div>
                  <label>用时（分钟）<input name="minutes" type="number" inputmode="numeric" min="0" max="9999" step="1" placeholder="0"></label>
                  <label>尝试次数<input name="attempts" type="number" inputmode="numeric" min="0" max="999" step="1" placeholder="0"></label>
                  <label>通过日期<input name="acDate" type="date"></label>
                  <label class="practice-note">复盘备注<input name="note" type="text" maxlength="160" placeholder="卡在哪里、下次检查什么"></label>
                </form>
              </div>
            </article>'''
        )

    report_data = json.dumps(
        {
            "range": [FIRST_CONTEST, LAST_CONTEST],
            "contestCount": 50,
            "problemCount": len(problems),
            "generatedAt": generated_at,
            "source": "AtCoder + AtCoder Problems",
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AtCoder ABC 近50期 A-G 题目归纳</title>
<style>
  :root {{
    --ink:#1f252b; --muted:#66717b; --line:#d9dee2; --paper:#ffffff; --wash:#f4f6f7;
    --red:#b33a3a; --red-soft:#faeeee; --green:#287454; --green-soft:#eaf5ef;
    --cyan:#147a8b; --cyan-soft:#e8f5f7; --gold:#90630f; --gold-soft:#fff6df;
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ margin:0; color:var(--ink); background:var(--paper); font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif; line-height:1.55; letter-spacing:0; }}
  a {{ color:#125d7a; text-decoration-thickness:1px; text-underline-offset:2px; }}
  button,input,select {{ font:inherit; letter-spacing:0; }}
  .topbar {{ position:sticky; top:0; z-index:30; display:flex; align-items:center; justify-content:space-between; gap:16px; min-height:48px; padding:7px max(20px,calc((100vw - 1180px)/2)); color:#fff; background:#20262c; }}
  .brand {{ font-weight:800; white-space:nowrap; }}
  .top-actions {{ display:flex; align-items:center; gap:8px; }}
  .top-actions button {{ border:1px solid #69727b; border-radius:5px; padding:6px 10px; color:#fff; background:transparent; cursor:pointer; }}
  .hero {{ border-bottom:1px solid var(--line); background:var(--wash); }}
  .hero-inner {{ max-width:1180px; margin:auto; padding:38px 20px 32px; }}
  .eyebrow {{ margin:0 0 7px; color:var(--red); font-weight:800; font-size:13px; }}
  h1 {{ max-width:850px; margin:0; font-size:34px; line-height:1.24; }}
  .lede {{ max-width:850px; margin:12px 0 0; color:var(--muted); font-size:15px; }}
  .metrics {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1px; max-width:760px; margin-top:26px; border:1px solid var(--line); background:var(--line); }}
  .metric {{ min-height:78px; padding:12px 14px; background:#fff; }}
  .metric b {{ display:block; font-size:23px; line-height:1.2; }}
  .metric span {{ color:var(--muted); font-size:12px; }}
  main {{ max-width:1180px; margin:auto; padding:28px 20px 72px; }}
  section {{ margin-bottom:38px; }}
  h2 {{ margin:0 0 6px; font-size:22px; }}
  .section-note {{ margin:0 0 16px; color:var(--muted); font-size:13px; }}
  .overview-grid {{ display:grid; grid-template-columns:minmax(0,1.05fr) minmax(420px,1.5fr); gap:28px; }}
  .topic-list {{ display:grid; gap:5px; }}
  .topic-bar {{ position:relative; display:grid; grid-template-columns:minmax(130px,1fr) minmax(80px,1.1fr) 34px; align-items:center; gap:10px; width:100%; min-height:31px; border:0; padding:4px 6px; color:var(--ink); background:transparent; text-align:left; cursor:pointer; }}
  .topic-bar:hover {{ background:var(--wash); }}
  .topic-bar i {{ display:block; height:7px; border-radius:2px; background:var(--cyan); }}
  .topic-bar b {{ text-align:right; font-variant-numeric:tabular-nums; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th,td {{ border:1px solid var(--line); padding:8px 9px; text-align:left; vertical-align:top; }}
  thead th {{ background:var(--wash); }}
  tbody th {{ width:52px; text-align:center; }}
  .guide {{ display:grid; grid-template-columns:repeat(4,1fr); border:1px solid var(--line); }}
  .guide div {{ min-height:104px; padding:14px; border-right:1px solid var(--line); }}
  .guide div:last-child {{ border-right:0; }}
  .guide b {{ display:block; margin-bottom:4px; color:var(--green); }}
  .guide p {{ margin:0; color:var(--muted); font-size:13px; }}
  .difficulty-layout {{ display:grid; grid-template-columns:minmax(0,1.6fr) minmax(250px,.8fr); gap:24px; align-items:start; }}
  .difficulty-table td:first-child {{ width:90px; white-space:nowrap; font-weight:800; }}
  .difficulty-table td:nth-child(2) {{ width:110px; font-variant-numeric:tabular-nums; white-space:nowrap; }}
  .color-key {{ display:inline-block; width:12px; height:12px; margin-right:6px; border:1px solid rgba(0,0,0,.18); border-radius:2px; vertical-align:-1px; }}
  .key-灰 {{ background:#9aa0a6; }} .key-棕 {{ background:#9b5b2b; }} .key-绿 {{ background:#2a8b57; }}
  .key-青 {{ background:#1594a6; }} .key-蓝 {{ background:#356fcb; }} .key-黄 {{ background:#c5a000; }}
  .key-橙 {{ background:#d76d24; }} .key-红 {{ background:#c83c48; }}
  .difficulty-note {{ border-left:4px solid var(--cyan); padding:11px 14px; background:var(--cyan-soft); font-size:13px; }}
  .difficulty-note p {{ margin:0 0 9px; }} .difficulty-note p:last-child {{ margin-bottom:0; }}
  .progress-panel {{ display:grid; grid-template-columns:minmax(240px,1.7fr) repeat(3,minmax(120px,.7fr)) auto; border:1px solid var(--line); background:var(--line); gap:1px; }}
  .progress-main,.progress-stat,.progress-action {{ min-height:86px; padding:13px 15px; background:#fff; }}
  .progress-main b,.progress-stat b {{ display:block; font-size:22px; line-height:1.2; font-variant-numeric:tabular-nums; }}
  .progress-main span,.progress-stat span {{ color:var(--muted); font-size:12px; }}
  .progress-track {{ height:8px; margin-top:12px; overflow:hidden; border-radius:2px; background:#e6eaed; }}
  .progress-track i {{ display:block; width:0; height:100%; background:var(--green); transition:width .2s ease; }}
  .progress-action {{ display:grid; place-items:center; min-width:120px; }}
  .progress-action button {{ border:1px solid #9ca6ad; border-radius:5px; padding:7px 11px; color:var(--ink); background:var(--wash); cursor:pointer; }}
  .storage-note {{ margin:8px 0 0; color:var(--muted); font-size:12px; }}
  .filters {{ position:sticky; top:48px; z-index:20; display:grid; grid-template-columns:minmax(200px,1fr) repeat(5,minmax(108px,auto)) auto; gap:8px; padding:10px; border:1px solid var(--line); background:rgba(255,255,255,.97); box-shadow:0 5px 14px rgba(31,37,43,.07); }}
  .filters input,.filters select {{ width:100%; height:38px; border:1px solid #bdc5ca; border-radius:5px; padding:0 10px; color:var(--ink); background:#fff; }}
  .filters button {{ height:38px; border:1px solid #9ca6ad; border-radius:5px; padding:0 13px; color:var(--ink); background:var(--wash); cursor:pointer; }}
  .result-line {{ display:flex; justify-content:space-between; gap:16px; margin:13px 0 8px; color:var(--muted); font-size:13px; }}
  .problem-list {{ border-top:1px solid var(--line); }}
  .problem-row {{ border-bottom:1px solid var(--line); }}
  .problem-row[hidden] {{ display:none; }}
  .problem-main {{ display:grid; grid-template-columns:90px minmax(0,1fr) 38px; gap:15px; align-items:start; padding:15px 8px; }}
  .problem-row:hover {{ background:#fbfcfc; }}
  .problem-id {{ display:flex; align-items:center; gap:8px; padding-top:2px; font-size:12px; }}
  .letter-badge {{ display:inline-grid; place-items:center; width:28px; height:28px; border-radius:4px; color:#fff; background:#3c4750; font-weight:900; }}
  .letter-a,.letter-b {{ background:var(--green); }}
  .letter-c,.letter-d {{ background:var(--cyan); }}
  .letter-e {{ background:var(--gold); }}
  .letter-f,.letter-g {{ background:var(--red); }}
  .problem-title {{ display:flex; align-items:center; flex-wrap:wrap; gap:8px; min-height:27px; font-size:16px; font-weight:800; }}
  .problem-body p {{ margin:5px 0 8px; color:#46515a; font-size:13px; overflow-wrap:anywhere; }}
  .difficulty {{ border:1px solid currentColor; border-radius:4px; padding:1px 6px; font-size:11px; font-weight:700; white-space:nowrap; }}
  .diff-灰,.diff-unknown {{ color:#6f777d; }} .diff-棕 {{ color:#8b5428; }} .diff-绿 {{ color:#25744c; }}
  .diff-青 {{ color:#087d8c; }} .diff-蓝 {{ color:#235db2; }} .diff-黄 {{ color:#866300; }}
  .diff-橙 {{ color:#b55216; }} .diff-红 {{ color:#b22f3b; }}
  .practice-pill {{ border:1px solid currentColor; border-radius:4px; padding:1px 6px; font-size:11px; font-weight:700; white-space:nowrap; }}
  .status-todo {{ color:#727b82; background:#fff; }} .status-doing {{ color:#8a5b0d; background:var(--gold-soft); }}
  .status-ac {{ color:#226846; background:var(--green-soft); }}
  .tags {{ display:flex; flex-wrap:wrap; gap:5px; }}
  .tag {{ border:1px solid #c9d6d0; border-radius:4px; padding:2px 6px; color:#235e47; background:var(--green-soft); font-size:11px; cursor:pointer; }}
  .toggle {{ display:grid; place-items:center; width:32px; height:32px; border:1px solid var(--line); border-radius:5px; color:#46515a; background:#fff; font-size:19px; cursor:pointer; }}
  .problem-detail {{ padding:14px 53px 16px 113px; border-top:1px dashed var(--line); background:var(--wash); font-size:12px; }}
  .problem-detail[hidden] {{ display:none; }}
  .problem-detail b {{ color:#374149; }}
  .problem-detail p {{ margin:4px 0 0; color:#58636c; overflow-wrap:anywhere; }}
  .reference-grid {{ display:grid; grid-template-columns:1fr 1.8fr auto; gap:20px; }}
  .source-links {{ display:flex; flex-direction:column; gap:7px; min-width:76px; }}
  .practice-editor {{ display:grid; grid-template-columns:auto 130px 120px 150px minmax(200px,1fr); gap:10px; align-items:end; margin-top:15px; padding-top:13px; border-top:1px solid var(--line); }}
  .practice-heading {{ grid-column:1/-1; display:flex; align-items:center; justify-content:space-between; gap:12px; }}
  .practice-tools {{ display:flex; align-items:center; gap:9px; }}
  .save-state {{ color:var(--muted); font-size:11px; }}
  .clear-record {{ border:0; padding:2px 0; color:var(--red); background:transparent; font-size:11px; cursor:pointer; text-decoration:underline; text-underline-offset:2px; }}
  .status-segments {{ display:grid; grid-template-columns:repeat(3,1fr); height:36px; border:1px solid #aeb7bd; border-radius:5px; overflow:hidden; background:#fff; }}
  .status-segments button {{ min-width:68px; border:0; border-right:1px solid #c9d0d5; color:#4d5860; background:#fff; cursor:pointer; }}
  .status-segments button:last-child {{ border-right:0; }}
  .status-segments button.active[data-value="todo"] {{ color:#fff; background:#69737a; }}
  .status-segments button.active[data-value="doing"] {{ color:#fff; background:var(--gold); }}
  .status-segments button.active[data-value="ac"] {{ color:#fff; background:var(--green); }}
  .practice-editor label {{ display:grid; gap:4px; color:#505b63; font-weight:700; }}
  .practice-editor input {{ width:100%; height:36px; min-width:0; border:1px solid #b8c0c5; border-radius:5px; padding:0 8px; color:var(--ink); background:#fff; font-weight:400; }}
  .empty {{ display:none; padding:34px; border:1px dashed var(--line); color:var(--muted); text-align:center; }}
  .method-note {{ border-left:4px solid var(--red); padding:10px 14px; background:var(--red-soft); color:#5f4141; font-size:13px; }}
  footer {{ border-top:1px solid var(--line); padding:22px 20px 34px; color:var(--muted); background:var(--wash); font-size:12px; }}
  footer div {{ max-width:1180px; margin:auto; }}
  @media (max-width:900px) {{
    h1 {{ font-size:28px; }}
    .metrics {{ grid-template-columns:1fr 1fr; }}
    .overview-grid {{ grid-template-columns:1fr; }}
    .difficulty-layout {{ grid-template-columns:1fr; }}
    .guide {{ grid-template-columns:1fr 1fr; }}
    .guide div:nth-child(2) {{ border-right:0; }}
    .guide div:nth-child(-n+2) {{ border-bottom:1px solid var(--line); }}
    .filters {{ position:static; grid-template-columns:1fr 1fr; }}
    .filters input {{ grid-column:1/-1; }}
    .problem-main {{ grid-template-columns:76px minmax(0,1fr) 34px; gap:9px; }}
    .problem-detail {{ padding:14px 20px 16px 93px; }}
    .reference-grid {{ grid-template-columns:1fr; }}
    .source-links {{ flex-direction:row; }}
    .practice-editor {{ grid-template-columns:1fr 1fr; }}
    .status-segments,.practice-note {{ grid-column:1/-1; }}
    .progress-panel {{ grid-template-columns:1fr 1fr; }}
    .progress-main,.progress-action {{ grid-column:1/-1; }}
    .progress-action {{ min-height:58px; }}
  }}
  @media (max-width:560px) {{
    .topbar {{ align-items:flex-start; }} .brand {{ white-space:normal; }}
    .hero-inner {{ padding-top:26px; }} h1 {{ font-size:24px; }}
    .metrics,.guide,.filters {{ grid-template-columns:1fr; }}
    .guide div {{ border-right:0; border-bottom:1px solid var(--line); }}
    .filters input {{ grid-column:auto; }}
    .overview-grid {{ display:block; }} .overview-grid > div + div {{ margin-top:28px; }}
    .problem-main {{ grid-template-columns:42px minmax(0,1fr) 32px; }}
    .problem-id b {{ display:none; }} .problem-detail {{ padding-left:57px; }}
    .problem-title {{ font-size:15px; }}
    .practice-editor,.progress-panel {{ grid-template-columns:1fr; }}
    .practice-editor > *,.progress-main,.progress-action {{ grid-column:1; }}
    .difficulty-table {{ font-size:11.5px; }}
    .difficulty-table th,.difficulty-table td {{ padding:7px 5px; }}
  }}
  @media print {{
    .topbar,.filters,.toggle,.topic-bar i {{ display:none !important; }}
    .hero-inner,main {{ max-width:none; padding-left:10mm; padding-right:10mm; }}
    .problem-row[hidden] {{ display:none; }}
    .problem-main {{ break-inside:avoid; }}
    .problem-detail {{ display:none !important; }}
    a {{ color:inherit; text-decoration:none; }}
  }}
</style>
</head>
<body>
<header class="topbar">
  <div class="brand">AtCoder ABC · 近 50 期题目索引</div>
  <div class="top-actions"><button type="button" id="expandAll">展开当前</button><button type="button" onclick="window.print()">打印 / PDF</button></div>
</header>
<div class="hero">
  <div class="hero-inner">
    <p class="eyebrow">ABC{FIRST_CONTEST} → ABC{LAST_CONTEST} · A～G 全题覆盖</p>
    <h1>近 50 期 AtCoder Beginner Contest 题目归纳与知识图谱</h1>
    <p class="lede">按最近一场已结束的 ABC{LAST_CONTEST} 向前取 50 场。每题提供简化题意、约束线索、知识点、难度估值与官方入口；用于选题和建立知识地图，不替代独立读题与实现。</p>
    <div class="metrics">
      <div class="metric"><b>50</b><span>场比赛</span></div>
      <div class="metric"><b>{len(problems)}</b><span>道 A～G 题目</span></div>
      <div class="metric"><b>{len(tag_counts)}</b><span>类知识标签</span></div>
      <div class="metric"><b>ABC{LAST_CONTEST}</b><span>最近已结束场次</span></div>
    </div>
  </div>
</div>
<main>
  <section>
    <h2>知识点总览</h2>
    <p class="section-note">频次来自对官方题面与官方题解的关键词归纳；点击条目可直接筛出对应题目。一个题目可能计入多个知识点。</p>
    <div class="overview-grid">
      <div><div class="topic-list">{bars}</div></div>
      <div>
        <table>
          <thead><tr><th>题号</th><th>近 50 期高频知识</th><th>训练定位</th></tr></thead>
          <tbody>{letter_rows}</tbody>
        </table>
      </div>
    </div>
  </section>

  <section>
    <h2>怎么使用这份索引</h2>
    <p class="section-note">先选合适的题，再完整读官方题面；不要从知识标签反推代码。</p>
    <div class="guide">
      <div><b>A～B · 稳定区</b><p>练准确读题、条件判断、循环、数组和字符串。目标是快速但不跳步。</p></div>
      <div><b>C · 踮脚区</b><p>重点练手推、枚举范围、数据结构选择和复杂度估算。</p></div>
      <div><b>D · 分界区</b><p>开始系统接触二分、图搜索、贪心、前缀和、DP 等核心模型。</p></div>
      <div><b>E～G · 专题区</b><p>用于长期知识地图。按专题学习，不以短期刷完为目标。</p></div>
    </div>
  </section>

  <section>
    <h2>难度颜色怎么读</h2>
    <p class="section-note">颜色按 AtCoder Problems 的题目难度估值划分。它反映“通常需要多强的综合解题能力”，不是官方评级，也不是孩子能否做出的判定。</p>
    <div class="difficulty-layout">
      <table class="difficulty-table">
        <thead><tr><th>颜色</th><th>难度值</th><th>补题时的参考定位</th></tr></thead>
        <tbody>
          <tr><td><span class="color-key key-灰"></span>灰</td><td>0～399</td><td>入门与基础实现，适合练独立读题和一次写对。</td></tr>
          <tr><td><span class="color-key key-棕"></span>棕</td><td>400～799</td><td>基础算法题，适合作为常规补题主线。</td></tr>
          <tr><td><span class="color-key key-绿"></span>绿</td><td>800～1199</td><td>初级算法综合题，适合当作需要踮脚的挑战。</td></tr>
          <tr><td><span class="color-key key-青"></span>青</td><td>1200～1599</td><td>中级题，建议先补对应专题，再独立建模。</td></tr>
          <tr><td><span class="color-key key-蓝"></span>蓝</td><td>1600～1999</td><td>较难题，用于专题深化，不追求短期刷完。</td></tr>
          <tr><td><span class="color-key key-黄"></span>黄</td><td>2000～2399</td><td>高难题，适合长期知识地图和赛后精读。</td></tr>
          <tr><td><span class="color-key key-橙"></span>橙</td><td>2400～2799</td><td>很难，通常需要多个高级算法的组合。</td></tr>
          <tr><td><span class="color-key key-红"></span>红</td><td>2800 及以上</td><td>顶级难度，作为远期专题资料与思维拓展。</td></tr>
        </tbody>
      </table>
      <div class="difficulty-note">
        <p><b>低难度为何不是负数？</b><br>AtCoder Problems 的原始估值可能低于 0。报告沿用常见显示方式，对原始值低于 400 的题做平滑换算，因此会看到“14 · 灰”“183 · 灰”等正数。</p>
        <p><b>补题优先级不要只看颜色。</b><br>先看孩子是否学过对应知识，再把“能独立完成的稳定题”和“需要一点提示的踮脚题”搭配起来。连续卡住时应缩小任务，而不是继续升难度。</p>
      </div>
    </div>
  </section>

  <section id="practiceProgress">
    <h2>补题进度</h2>
    <p class="section-note">练题记录按题目编号保存在当前浏览器中；在同一浏览器、同一文件路径下重新打开或重新生成本报告，通常会继续读取同一份记录。</p>
    <div class="progress-panel">
      <div class="progress-main"><b id="progressPercent">0%</b><span>总完成率 · <span id="progressFraction">0 / {len(problems)} AC</span></span><div class="progress-track"><i id="progressFill"></i></div></div>
      <div class="progress-stat"><b id="doingCount">0</b><span>练习中</span></div>
      <div class="progress-stat"><b id="totalMinutes">0</b><span>累计分钟</span></div>
      <div class="progress-stat"><b id="recordedCount">0</b><span>已有记录</span></div>
      <div class="progress-action"><button type="button" id="exportRecords">导出记录</button></div>
    </div>
    <p class="storage-note" id="storageState">本机浏览器保存 · 移动/改名文件、切换浏览器或清理浏览器数据前，请先导出 CSV 备份</p>
  </section>

  <section id="problems">
    <h2>逐题索引</h2>
    <p class="section-note">题意和题解抓手保留英文，避免机器翻译损坏数学含义；界面、知识点和训练定位使用中文。点击行尾“＋”查看约束与题解抓手。</p>
    <div class="filters" aria-label="题目筛选器">
      <input id="search" type="search" placeholder="搜索题名、题意或知识点" aria-label="搜索题目">
      <select id="contestFilter" aria-label="按场次筛选"><option value="">全部场次</option>{contest_options}</select>
      <select id="letterFilter" aria-label="按题号筛选"><option value="">A～G 全部</option>{''.join(f'<option value="{x}">{x} 题</option>' for x in LETTERS)}</select>
      <select id="tagFilter" aria-label="按知识点筛选"><option value="">全部知识点</option>{tag_options}</select>
      <select id="bandFilter" aria-label="按难度颜色筛选"><option value="">全部难度</option>{''.join(f'<option value="{x}">{x}色</option>' for x in ('灰','棕','绿','青','蓝','黄','橙','红'))}<option value="unknown">暂无估值</option></select>
      <select id="statusFilter" aria-label="按练题状态筛选"><option value="">全部状态</option><option value="todo">未做</option><option value="doing">练习中</option><option value="ac">已 AC</option></select>
      <button type="button" id="reset">重置</button>
    </div>
    <div class="result-line"><span id="resultCount">显示 {len(problems)} / {len(problems)} 题</span><span>难度为 AtCoder Problems 估值，非官方定级</span></div>
    <div class="problem-list">{''.join(problem_rows)}</div>
    <div class="empty" id="empty">没有符合当前条件的题目，请调整筛选。</div>
  </section>

  <section>
    <h2>数据口径与边界</h2>
    <div class="method-note">本版收录固定范围 ABC{FIRST_CONTEST}～ABC{LAST_CONTEST}。题名、题面、约束和 Editorial 来自 AtCoder 官方页面；难度估值来自 AtCoder Problems。知识标签和短摘要由规则辅助归纳，复杂题可能存在多种正确做法，最终以官方题解为准。</div>
  </section>
</main>
<footer><div>生成时间：{esc(generated_at)}（Asia/Shanghai） · 数据源：<a href="https://atcoder.jp/contests/" target="_blank" rel="noopener">AtCoder</a>、<a href="https://kenkoooo.com/atcoder/" target="_blank" rel="noopener">AtCoder Problems</a></div></footer>
<script type="application/json" id="reportMeta">{report_data}</script>
<script>
(() => {{
  const rows = [...document.querySelectorAll('.problem-row')];
  const STORAGE_KEY = 'atcoder-abc-training-v1';
  const statusLabels = {{ todo: '未做', doing: '练习中', ac: 'AC' }};
  let records = {{}};
  let storageAvailable = true;
  try {{
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{{}}');
    if (stored && typeof stored === 'object' && !Array.isArray(stored)) records = stored;
  }} catch (error) {{
    storageAvailable = false;
    document.querySelector('#storageState').textContent = '浏览器未开放本地保存；本次打开期间仍可记录';
  }}
  const controls = {{
    search: document.querySelector('#search'), contest: document.querySelector('#contestFilter'),
    letter: document.querySelector('#letterFilter'), tag: document.querySelector('#tagFilter'),
    band: document.querySelector('#bandFilter'), status: document.querySelector('#statusFilter')
  }};
  function normalizeRecord(value) {{
    const record = value && typeof value === 'object' ? value : {{}};
    return {{
      status: ['todo', 'doing', 'ac'].includes(record.status) ? record.status : 'todo',
      minutes: record.minutes === undefined ? '' : String(record.minutes),
      attempts: record.attempts === undefined ? '' : String(record.attempts),
      acDate: typeof record.acDate === 'string' ? record.acDate : '',
      note: typeof record.note === 'string' ? record.note.slice(0, 160) : ''
    }};
  }}
  function hasContent(record) {{
    return record.status !== 'todo' || record.minutes !== '' || record.attempts !== '' || record.acDate !== '' || record.note !== '';
  }}
  function persistRecords(form) {{
    if (storageAvailable) {{
      try {{
        localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
        document.querySelector('#storageState').textContent = '本机浏览器已保存 · 移动/改名文件、切换浏览器或清理数据前，请先导出 CSV';
      }} catch (error) {{
        storageAvailable = false;
        document.querySelector('#storageState').textContent = '保存空间不可用；请先导出记录备份';
      }}
    }}
    if (form) form.querySelector('.save-state').textContent = storageAvailable ? '已保存' : '本次暂存';
  }}
  function renderRow(row, hydrateForm = true) {{
    const record = normalizeRecord(records[row.dataset.problem]);
    row.dataset.status = record.status;
    const pill = row.querySelector('.practice-pill');
    pill.className = `practice-pill status-${{record.status}}`;
    pill.textContent = statusLabels[record.status] + (record.minutes !== '' ? ` · ${{record.minutes}} 分` : '');
    const form = row.querySelector('.practice-editor');
    form.querySelectorAll('.status-segments button').forEach(button => button.classList.toggle('active', button.dataset.value === record.status));
    if (hydrateForm) for (const name of ['minutes', 'attempts', 'acDate', 'note']) form.elements[name].value = record[name];
  }}
  function updateProgress() {{
    const values = rows.map(row => normalizeRecord(records[row.dataset.problem])).filter(hasContent);
    const ac = values.filter(record => record.status === 'ac').length;
    const doing = values.filter(record => record.status === 'doing').length;
    const minutes = values.reduce((sum, record) => sum + (Number(record.minutes) || 0), 0);
    const percent = Math.round(ac / rows.length * 100);
    document.querySelector('#progressPercent').textContent = `${{percent}}%`;
    document.querySelector('#progressFraction').textContent = `${{ac}} / ${{rows.length}} AC`;
    document.querySelector('#progressFill').style.width = `${{percent}}%`;
    document.querySelector('#doingCount').textContent = doing;
    document.querySelector('#totalMinutes').textContent = minutes;
    document.querySelector('#recordedCount').textContent = values.length;
  }}
  function saveForm(form) {{
    const row = form.closest('.problem-row');
    const status = form.querySelector('.status-segments button.active')?.dataset.value || 'todo';
    const record = normalizeRecord({{
      status,
      minutes: form.elements.minutes.value,
      attempts: form.elements.attempts.value,
      acDate: form.elements.acDate.value,
      note: form.elements.note.value.trim()
    }});
    if (hasContent(record)) records[row.dataset.problem] = record;
    else delete records[row.dataset.problem];
    persistRecords(form);
    renderRow(row, false);
    updateProgress();
    applyFilters();
  }}
  function applyFilters() {{
    const query = controls.search.value.trim().toLowerCase();
    let visible = 0;
    for (const row of rows) {{
      const matches = (!query || row.dataset.search.includes(query)) &&
        (!controls.contest.value || row.dataset.contest === controls.contest.value) &&
        (!controls.letter.value || row.dataset.letter === controls.letter.value) &&
        (!controls.tag.value || row.dataset.tags.split('|').includes(controls.tag.value)) &&
        (!controls.band.value || row.dataset.band === controls.band.value) &&
        (!controls.status.value || row.dataset.status === controls.status.value);
      row.hidden = !matches;
      if (matches) visible++;
    }}
    document.querySelector('#resultCount').textContent = `显示 ${{visible}} / ${{rows.length}} 题`;
    document.querySelector('#empty').style.display = visible ? 'none' : 'block';
  }}
  Object.values(controls).forEach(control => control.addEventListener(control === controls.search ? 'input' : 'change', applyFilters));
  document.querySelector('#reset').addEventListener('click', () => {{
    Object.values(controls).forEach(control => control.value = ''); applyFilters();
  }});
  function chooseTopic(topic) {{ controls.tag.value = topic; applyFilters(); document.querySelector('#problems').scrollIntoView(); }}
  document.querySelectorAll('[data-topic]').forEach(button => button.addEventListener('click', () => chooseTopic(button.dataset.topic)));
  document.querySelectorAll('.toggle').forEach(button => button.addEventListener('click', () => {{
    const detail = button.closest('.problem-row').querySelector('.problem-detail');
    detail.hidden = !detail.hidden; button.textContent = detail.hidden ? '＋' : '−';
    button.setAttribute('aria-expanded', String(!detail.hidden));
  }}));
  document.querySelectorAll('.practice-editor').forEach(form => {{
    form.addEventListener('submit', event => event.preventDefault());
    form.querySelectorAll('.status-segments button').forEach(button => button.addEventListener('click', () => {{
      form.querySelectorAll('.status-segments button').forEach(candidate => candidate.classList.toggle('active', candidate === button));
      if (button.dataset.value === 'ac' && !form.elements.acDate.value) {{
        const now = new Date();
        form.elements.acDate.value = `${{now.getFullYear()}}-${{String(now.getMonth() + 1).padStart(2, '0')}}-${{String(now.getDate()).padStart(2, '0')}}`;
      }}
      saveForm(form);
    }}));
    form.querySelectorAll('input').forEach(input => input.addEventListener('input', () => saveForm(form)));
    form.querySelector('.clear-record').addEventListener('click', () => {{
      const row = form.closest('.problem-row');
      if (!hasContent(normalizeRecord(records[row.dataset.problem]))) return;
      if (!window.confirm(`确认清空 ABC${{row.dataset.contest}} ${{row.dataset.letter}} 的练题记录吗？`)) return;
      delete records[row.dataset.problem];
      persistRecords(form); renderRow(row); updateProgress(); applyFilters();
    }});
  }});
  document.querySelector('#exportRecords').addEventListener('click', () => {{
    const lines = [['题目', '题名', '状态', '用时（分钟）', '尝试次数', '通过日期', '复盘备注']];
    for (const row of rows) {{
      const record = normalizeRecord(records[row.dataset.problem]);
      if (!hasContent(record)) continue;
      lines.push([
        `${{row.dataset.contest}}${{row.dataset.letter}}`, row.querySelector('.problem-title a').textContent.trim(),
        statusLabels[record.status], record.minutes, record.attempts, record.acDate, record.note
      ]);
    }}
    if (lines.length === 1) {{ alert('还没有可导出的练题记录。'); return; }}
    const csv = '\uFEFF' + lines.map(columns => columns.map(value => `"${{String(value).replaceAll('"', '""')}}"`).join(',')).join('\\n');
    const url = URL.createObjectURL(new Blob([csv], {{ type: 'text/csv;charset=utf-8' }}));
    const link = document.createElement('a');
    link.href = url; link.download = `AtCoder补题记录-${{new Date().toISOString().slice(0, 10)}}.csv`;
    document.body.appendChild(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }});
  let expanded = false;
  document.querySelector('#expandAll').addEventListener('click', event => {{
    expanded = !expanded;
    rows.filter(row => !row.hidden).forEach(row => {{
      const detail = row.querySelector('.problem-detail'); const button = row.querySelector('.toggle');
      detail.hidden = !expanded; button.textContent = expanded ? '−' : '＋'; button.setAttribute('aria-expanded', String(expanded));
    }});
    event.currentTarget.textContent = expanded ? '收起当前' : '展开当前';
  }});
  rows.forEach(renderRow);
  updateProgress();
  applyFilters();
}})();
</script>
</body>
</html>'''


def build(output: Path, workers: int) -> None:
    print(f"Discovering ABC{FIRST_CONTEST}-ABC{LAST_CONTEST} task and editorial links…")
    contest_data: dict[int, tuple[dict, dict]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(scrape_contest, contest)
            for contest in range(FIRST_CONTEST, LAST_CONTEST + 1)
        ]
        for future in concurrent.futures.as_completed(futures):
            contest, tasks, editorials = future.result()
            contest_data[contest] = (tasks, editorials)
            print(f"  ABC{contest}: {len(tasks)} tasks, {len(editorials)} editorial links", flush=True)

    problems: list[dict] = []
    missing: list[str] = []
    for contest in range(FIRST_CONTEST, LAST_CONTEST + 1):
        tasks, editorials = contest_data[contest]
        for letter in LETTERS:
            if letter not in tasks:
                missing.append(f"ABC{contest}-{letter}")
                continue
            problem = dict(tasks[letter])
            problem.update(contest=contest, letter=letter, editorial_url=editorials.get(letter, ""))
            problems.append(problem)

    if missing:
        raise RuntimeError(f"Official task list is incomplete: {', '.join(missing)}")
    expected_problems = 350
    if len(problems) != expected_problems:
        raise RuntimeError(f"Expected 350 problems, got {len(problems)}")

    print(
        f"Fetching {expected_problems} official statements and editorial summaries…"
    )
    completed: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(scrape_problem, problem) for problem in problems]
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            completed.append(future.result())
            if index % 25 == 0 or index == len(problems):
                print(f"  {index}/{len(problems)} problems complete", flush=True)

    models = load_models()
    for problem in completed:
        model = models.get(problem["id"], {})
        problem["difficulty"] = displayed_difficulty(model.get("difficulty"))
    completed.sort(key=lambda row: (-row["contest"], LETTERS.index(row["letter"])))

    generated_at = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    document = render_report(completed, generated_at)
    output.write_text(document, encoding="utf-8")
    print(f"Wrote {output} ({output.stat().st_size:,} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    build(args.output, max(1, min(args.workers, 8)))


if __name__ == "__main__":
    main()
