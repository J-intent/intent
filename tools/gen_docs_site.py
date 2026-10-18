#!/usr/bin/env python
# tools/gen_docs_site.py — 静态文档站生成器（C9）
#
# 心学为体：文档是语言的名片——名片不整，人未开口气已短
# 禅道为翼：一次生成，随处可开；无构建，无依赖，无服务器
# 马哲为用：docs/*.md + std/*.intent(经 --doc 同源) → docs/site/index.html
#
# 产物特性：
#   - 单文件 index.html（CSS/JS/数据全内联）— file:// 双击即开
#   - 客户端即时搜索（标题 + 正文索引，无外部服务）
#   - 侧边栏分组导航：规范 / 教程 / 哲学 / 标准库 API
#   - API 页与 CLI --doc 同源（复用 generate_docs），不维护第二份
#
# 用法： python tools/gen_docs_site.py            # 生成 docs/site/index.html
#        python tools/gen_docs_site.py --check    # 只校验转换不写文件

import html
import json
import os
import re
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT, "src"))

DOCS_DIR = os.path.join(PROJECT, "docs")
STD_DIR = os.path.join(PROJECT, "std")
OUT_DIR = os.path.join(DOCS_DIR, "site")
OUT_FILE = os.path.join(OUT_DIR, "index.html")

# ── 页面分组（侧边栏顺序） ──
GROUPS = [
    ("规范", ["spec.md", "roadmap.md", "book_outline.md"]),
    ("教程", None),        # chapter_*.md 自动收集
    ("哲学", ["philosophy_mapper.md"]),
    ("标准库 API", None),  # std/*.intent 自动收集
]


# ═══ Markdown 子集转换器 ═══
# 覆盖项目文档实际语法：标题/代码块/表格/列表/引用/粗体/斜体/行内代码/链接/水平线。
# 不求 CommonMark 全集——未知语法原样转义输出，不崩不乱。

def md_to_html(md: str) -> str:
    lines = md.replace('\r\n', '\n').split('\n')
    out = []
    i = 0
    n = len(lines)
    in_ul = in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append('</ul>')
            in_ul = False
        if in_ol:
            out.append('</ol>')
            in_ol = False

    while i < n:
        line = lines[i]

        # 代码块
        if line.lstrip().startswith('```'):
            close_lists()
            lang = line.strip()[3:].strip()
            buf = []
            i += 1
            while i < n and not lines[i].lstrip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1  # 跳过收尾 ```
            cls = f' class="lang-{html.escape(lang)}"' if lang else ''
            out.append(f'<pre><code{cls}>{html.escape(chr(10).join(buf))}</code></pre>')
            continue

        # 标题
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            close_lists()
            level = len(m.group(1))
            text = _inline(m.group(2).strip())
            out.append(f'<h{level} id="{_slug(m.group(2))}">{text}</h{level}>')
            i += 1
            continue

        # 水平线
        if re.match(r'^\s*(-{3,}|\*{3,}|_{3,})\s*$', line):
            close_lists()
            out.append('<hr>')
            i += 1
            continue

        # 引用块
        if line.lstrip().startswith('>'):
            close_lists()
            buf = []
            while i < n and lines[i].lstrip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            out.append(f'<blockquote>{_inline(chr(10).join(buf).strip())}</blockquote>')
            continue

        # 表格（| 分隔，第二行为对齐行）
        if line.lstrip().startswith('|') and i + 1 < n \
                and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            close_lists()
            header = _split_row(line)
            aligns = _row_aligns(lines[i + 1])
            i += 2
            rows = []
            while i < n and lines[i].lstrip().startswith('|'):
                rows.append(_split_row(lines[i]))
                i += 1
            thead = ''.join(
                f'<th{a}>{c}</th>' for c, a in zip(header, aligns))
            trs = []
            for row in rows:
                tds = ''.join(
                    f'<td{a}>{c}</td>'
                    for c, a in zip(row + [''] * (len(header) - len(row)), aligns))
                trs.append(f'<tr>{tds}</tr>')
            out.append(f'<table><thead><tr>{thead}</tr></thead>'
                       f'<tbody>{"".join(trs)}</tbody></table>')
            continue

        # 无序列表
        if re.match(r'^\s*[-*+]\s+', line):
            if not in_ul:
                close_lists()
                out.append('<ul>')
                in_ul = True
            out.append(f'<li>{_inline(re.sub(chr(94) + r"\s*[-*+]\s+", "", line, count=1).strip())}</li>')
            i += 1
            continue

        # 有序列表
        m = re.match(r'^\s*\d+[.)]\s+(.*)$', line)
        if m:
            if not in_ol:
                close_lists()
                out.append('<ol>')
                in_ol = True
            out.append(f'<li>{_inline(m.group(1).strip())}</li>')
            i += 1
            continue

        # 空行
        if not line.strip():
            close_lists()
            i += 1
            continue

        # 普通段落（连续行合并）
        close_lists()
        buf = [line]
        i += 1
        while i < n and lines[i].strip() \
                and not re.match(r'^\s*(#{1,6}\s|[-*+]\s|\d+[.)]\s|>|\||```)', lines[i]):
            buf.append(lines[i])
            i += 1
        out.append(f'<p>{_inline(chr(10).join(buf).strip())}</p>')

    close_lists()
    return '\n'.join(out)


def _split_row(line: str) -> list:
    cells = line.strip().strip('|').split('|')
    return [_inline(c.strip()) for c in cells]


def _row_aligns(line: str) -> list:
    aligns = []
    for cell in line.strip().strip('|').split('|'):
        cell = cell.strip()
        if cell.startswith(':') and cell.endswith(':'):
            aligns.append(' style="text-align:center"')
        elif cell.endswith(':'):
            aligns.append(' style="text-align:right"')
        else:
            aligns.append('')
    return aligns


def _inline(text: str) -> str:
    """行内语法：代码/粗体/斜体/链接（先转义后替换，防注入）"""
    text = html.escape(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def _slug(text: str) -> str:
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[\s_-]+', '-', slug).strip('-') or 'section'


def _strip_tags(html_text: str) -> str:
    """搜索索引用纯文本"""
    text = re.sub(r'<[^>]+>', ' ', html_text)
    return re.sub(r'\s+', ' ', text).strip()


# ═══ 页面收集 ═══

def collect_md_pages() -> list:
    """docs/*.md → [{id, title, group, md}]（site/ 目录除外）"""
    pages = []
    used = set()
    for group, names in GROUPS:
        if names is None:
            continue
        for name in names:
            path = os.path.join(DOCS_DIR, name)
            if not os.path.isfile(path):
                continue
            with open(path, 'r', encoding='utf-8') as f:
                md = f.read()
            pages.append({"id": name, "title": _first_heading(md) or name,
                          "group": group, "md": md})
            used.add(name)
    # 教程章自动收集
    chapters = sorted(f for f in os.listdir(DOCS_DIR)
                      if re.match(r'^chapter_\d+.*\.md$', f))
    for name in chapters:
        if name in used:
            continue
        with open(os.path.join(DOCS_DIR, name), 'r', encoding='utf-8') as f:
            md = f.read()
        pages.append({"id": name, "title": _first_heading(md) or name,
                      "group": "教程", "md": md})
    # 未分组的其余 md（防御遗漏）
    for name in sorted(os.listdir(DOCS_DIR)):
        if not name.endswith('.md') or name in used or name in chapters:
            continue
        with open(os.path.join(DOCS_DIR, name), 'r', encoding='utf-8') as f:
            md = f.read()
        pages.append({"id": name, "title": _first_heading(md) or name,
                      "group": "规范", "md": md})
    return pages


def _first_heading(md: str) -> str:
    m = re.search(r'^#\s+(.*)$', md, re.M)
    return m.group(1).strip() if m else ''


def collect_std_pages() -> list:
    """std/*.intent → API 页（复用 CLI --doc 的 generate_docs，同源纪律）"""
    from mini_intent import generate_docs
    pages = []
    if not os.path.isdir(STD_DIR):
        return pages
    names = sorted(f for f in os.listdir(STD_DIR) if f.endswith('.intent'))
    for name in names:
        if name.startswith('_'):
            continue
        path = os.path.join(STD_DIR, name)
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        title = os.path.splitext(name)[0]
        try:
            md = generate_docs(code, title)
        except SyntaxError:
            md = f"# {title}\n\n（源码解析失败，API 页略）"
        pages.append({"id": f"std/{name}", "title": f"std.{title}",
                      "group": "标准库 API", "md": md})
    # std/bim 子目录
    bim_dir = os.path.join(STD_DIR, 'bim')
    if os.path.isdir(bim_dir):
        for name in sorted(f for f in os.listdir(bim_dir)
                           if f.endswith('.intent')):
            if name.startswith('_'):
                continue
            with open(os.path.join(bim_dir, name), 'r', encoding='utf-8') as f:
                code = f.read()
            title = os.path.splitext(name)[0]
            try:
                md = generate_docs(code, title)
            except SyntaxError:
                md = f"# bim.{title}\n\n（源码解析失败，API 页略）"
            pages.append({"id": f"std/bim/{name}", "title": f"bim.{title}",
                          "group": "标准库 API", "md": md})
    return pages


# ═══ 站点渲染 ═══

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Intent 文档站</title>
<style>
:root {
  --bg: #16161c; --panel: #1e1e26; --border: #2c2c38;
  --text: #d8d8e0; --dim: #8a8a99; --accent: #7c9aff;
  --code-bg: #12121a; --hl: #2a2a3a;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: 15px/1.75 -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; }
#app { display: flex; min-height: 100vh; }
#side { width: 264px; flex-shrink: 0; background: var(--panel);
  border-right: 1px solid var(--border); padding: 20px 14px;
  position: sticky; top: 0; height: 100vh; overflow-y: auto; }
#side h1 { font-size: 18px; margin: 0 0 4px; color: var(--accent); }
#side .sub { color: var(--dim); font-size: 12px; margin-bottom: 14px; }
#search { width: 100%; padding: 7px 10px; border-radius: 6px;
  border: 1px solid var(--border); background: var(--bg); color: var(--text);
  margin-bottom: 14px; outline: none; }
#search:focus { border-color: var(--accent); }
.gtitle { color: var(--dim); font-size: 11px; text-transform: uppercase;
  letter-spacing: .08em; margin: 14px 0 6px; }
.nav a { display: block; padding: 5px 9px; color: var(--text);
  text-decoration: none; border-radius: 6px; font-size: 13.5px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nav a:hover { background: var(--hl); }
.nav a.active { background: var(--accent); color: #101018; }
#main { flex: 1; padding: 36px 48px 80px; max-width: 900px; }
#main h1 { font-size: 26px; border-bottom: 1px solid var(--border);
  padding-bottom: 10px; }
#main h2 { font-size: 20px; margin-top: 34px; }
#main h3 { font-size: 17px; margin-top: 26px; }
#main h4, #main h5, #main h6 { font-size: 15px; margin-top: 20px; }
a { color: var(--accent); }
code { background: var(--code-bg); padding: 2px 6px; border-radius: 4px;
  font-family: Consolas, "Cascadia Code", monospace; font-size: 13px; }
pre { background: var(--code-bg); border: 1px solid var(--border);
  border-radius: 8px; padding: 14px 16px; overflow-x: auto; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 14px 0; }
th, td { border: 1px solid var(--border); padding: 7px 12px;
  text-align: left; font-size: 13.5px; }
th { background: var(--panel); }
blockquote { border-left: 3px solid var(--accent); margin: 12px 0;
  padding: 4px 16px; color: var(--dim); background: var(--panel);
  border-radius: 0 8px 8px 0; }
hr { border: none; border-top: 1px solid var(--border); margin: 28px 0; }
#hits { margin-bottom: 14px; }
#hits .hit { padding: 9px 12px; border: 1px solid var(--border);
  border-radius: 8px; margin-bottom: 8px; cursor: pointer; }
#hits .hit:hover { background: var(--hl); }
#hits .hit .t { color: var(--accent); font-weight: 600; }
#hits .hit .s { color: var(--dim); font-size: 12.5px;
  overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; }
#hits .hit mark { background: #4a3f1f; color: #e8d48a; }
.empty { color: var(--dim); text-align: center; margin-top: 60px; }
@media (max-width: 760px) {
  #app { flex-direction: column; }
  #side { width: 100%; height: auto; position: static; }
  #main { padding: 24px; }
}
</style>
</head>
<body>
<div id="app">
  <aside id="side">
    <h1>Intent 文档站</h1>
    <div class="sub">心学为体 · 禅道为翼 · 马哲为用</div>
    <input id="search" type="search" placeholder="搜索文档…（标题与正文）">
    <nav id="nav" class="nav"></nav>
  </aside>
  <main id="main"></main>
</div>
<script>
const PAGES = __PAGES_JSON__;
const IDX = PAGES.map(p => ({id: p.id, title: p.title,
  text: (p.title + " " + p.text).toLowerCase()}));
const nav = document.getElementById("nav");
const main = document.getElementById("main");
const search = document.getElementById("search");

function renderNav(filterIds) {
  nav.innerHTML = "";
  const groups = {};
  for (const p of PAGES) {
    if (filterIds && !filterIds.has(p.id)) continue;
    (groups[p.group] = groups[p.group] || []).push(p);
  }
  for (const g of Object.keys(groups)) {
    const t = document.createElement("div");
    t.className = "gtitle"; t.textContent = g;
    nav.appendChild(t);
    for (const p of groups[g]) {
      const a = document.createElement("a");
      a.href = "#" + p.id; a.textContent = p.title; a.dataset.id = p.id;
      a.onclick = () => showPage(p.id);
      nav.appendChild(a);
    }
  }
}

function showPage(id) {
  const p = PAGES.find(x => x.id === id);
  if (!p) return;
  main.innerHTML = p.html;
  document.querySelectorAll(".nav a").forEach(a =>
    a.classList.toggle("active", a.dataset.id === id));
  history.replaceState(null, "", "#" + id);
  window.scrollTo(0, 0);
}

function showHits(q) {
  const hits = [];
  for (const e of IDX) {
    const at = e.text.indexOf(q);
    if (at >= 0) {
      const start = Math.max(0, at - 30);
      const snip = e.text.slice(start, at + q.length + 60);
      hits.push({page: PAGES.find(x => x.id === e.id),
        before: snip.slice(0, at - start), match: q,
        after: snip.slice(at - start + q.length)});
    }
    if (hits.length >= 20) break;
  }
  main.innerHTML = "";
  const box = document.createElement("div");
  box.id = "hits";
  if (!hits.length) {
    box.innerHTML = '<div class="empty">没有匹配「' + q + '」的文档</div>';
  }
  for (const h of hits) {
    const d = document.createElement("div");
    d.className = "hit";
    d.onclick = () => showPage(h.page.id);
    d.innerHTML = '<div class="t"></div><div class="s"></div>';
    d.querySelector(".t").textContent = h.page.title;
    const s = d.querySelector(".s");
    s.append(document.createTextNode(h.before));
    s.append(Object.assign(document.createElement("mark"),
      {textContent: h.match}));
    s.append(document.createTextNode(h.after));
    box.appendChild(d);
  }
  main.appendChild(box);
}

search.addEventListener("input", () => {
  const q = search.value.trim().toLowerCase();
  if (!q) {
    const id = location.hash.slice(1);
    if (id && PAGES.some(p => p.id === id)) { showPage(id); return; }
    main.innerHTML = '<div class="empty">左侧选择章节，或输入关键词搜索</div>';
    renderNav(null);
    document.querySelectorAll(".nav a").forEach(a => a.classList.remove("active"));
    return;
  }
  const ids = new Set(IDX.filter(e => e.text.includes(q)).map(e => e.id));
  renderNav(ids);
  showHits(q);
});

renderNav(null);
const initial = location.hash.slice(1);
if (initial && PAGES.some(p => p.id === initial)) {
  showPage(initial);
} else {
  main.innerHTML = '<div class="empty">左侧选择章节，或输入关键词搜索</div>';
}
</script>
</body>
</html>
"""


def render_site(pages: list) -> str:
    payload = [{"id": p["id"], "title": p["title"], "group": p["group"],
                "html": md_to_html(p["md"]), "text": _strip_tags(md_to_html(p["md"]))}
               for p in pages]
    return PAGE_TEMPLATE.replace('__PAGES_JSON__',
                                 json.dumps(payload, ensure_ascii=False))


def write_api_pages() -> int:
    """--api: 每模块一页落盘 docs/api/<module>.md（E2）

    与 CLI --doc 同源（复用 generate_docs），站点 API 页与本地参考
    永远一致——单一事实源纪律。
    """
    api_dir = os.path.join(DOCS_DIR, 'api')
    os.makedirs(api_dir, exist_ok=True)
    pages = collect_std_pages()
    count = 0
    for p in pages:
        # id 形如 std/re.intent / std/bim/pipe.intent → api/re.md / api/bim.pipe.md
        rel = p['id'][len('std/'):-len('.intent')].replace('/', '.')
        out_path = os.path.join(api_dir, f'{rel}.md')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(p['md'])
        count += 1
    # 索引页
    lines = ['# 标准库参考', '',
             '> 每模块一页，由 `python tools/gen_docs_site.py --api` 生成，',
             '> 与 CLI `python src/mini_intent.py --doc std/<mod>.intent` 同源。', '',
             '| 模块 | 页 |', '|---|---|']
    for p in pages:
        rel = p['id'][len('std/'):-len('.intent')].replace('/', '.')
        lines.append(f"| {p['title']} | [{rel}.md]({rel}.md) |")
    with open(os.path.join(api_dir, 'index.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"✅ 标准库参考已生成: docs/api/ ({count} 模块 + index)")
    return 0


def main() -> int:
    if '--api' in sys.argv:
        return write_api_pages()
    check_only = '--check' in sys.argv
    pages = collect_md_pages() + collect_std_pages()
    if not pages:
        print("❌ 没有收集到任何文档页面")
        return 1
    site = render_site(pages)
    if check_only:
        print(f"✅ 转换校验通过: {len(pages)} 页, {len(site)} 字节")
        return 0
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(site)
    print(f"✅ 文档站已生成: {os.path.relpath(OUT_FILE, PROJECT)} "
          f"({len(pages)} 页, {len(site) // 1024} KB)")
    print(f"   分组: " + ", ".join(
        f"{g} {sum(1 for p in pages if p['group'] == g)}" for g in
        dict.fromkeys(p['group'] for p in pages)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
