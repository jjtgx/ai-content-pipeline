#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Content Pipeline —— 最小可运行版本 (MVP)
============================================
一条四阶段流水线:选题 Agent -> 初稿 Agent -> 排版 Agent -> 发布 Agent

适合放进简历/作品集的最小演示:
  * 零第三方依赖,Python 标准库即可运行
  * 每个阶段独立函数,可单独替换成 Claude Code / 飞书多维表格等真实实现
  * 跑一次 = 产出一篇排版好的 HTML 文章 + 完整发布日志

用法:
  python pipeline.py              # 默认配置,跑通全流程
  python pipeline.py --seed 7     # 固定随机种子,可复现选题结果
  python pipeline.py --out output # 指定输出目录(默认 output/)
"""

import argparse
import json
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Windows 控制台默认 GBK,强制 UTF-8 输出,避免中文乱码
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent

# ============================================================
# 1. 选题池:每个候选包含 标题 / 领域 / 热度分 / 切入角度
# ============================================================
TOPIC_POOL = [
    {
        "title": "我用 AI 搭了一条「自动写稿流水线」,从选题到发布只要 30 分钟",
        "domain": "效率工具 / 自媒体",
        "heat": 92,
        "angle": "第一人称实操复盘,给想用 AI 做内容的人一个可复制的模板",
    },
    {
        "title": "不会写代码,也能用 Claude Code 搭自己的 AI 工作流",
        "domain": "AI 工具入门",
        "heat": 88,
        "angle": "面向零基础读者,讲清楚 3 个关键命令和 1 个最小例子",
    },
    {
        "title": "飞书多维表格 + AI:把「灵感收集」变成「内容工厂」",
        "domain": "飞书 / 效率",
        "heat": 81,
        "angle": "用一张表格管理选题池,用自动化按钮触发初稿生成",
    },
    {
        "title": "给简历加分的 AI 作品:从 0 到 1 做一个自动选题工具",
        "domain": "求职 / 作品集",
        "heat": 85,
        "angle": "面试官想看到的不是「会用 AI」,而是「用 AI 交付了完整结果」",
    },
    {
        "title": "新手做自媒体,先学会用 AI 自动生成初稿",
        "domain": "自媒体",
        "heat": 76,
        "angle": "把最花时间的「从空白页开始」这一步交给 AI,人只负责判断",
    },
    {
        "title": "AI 写作流水线的 4 个环节:选题、初稿、排版、发布",
        "domain": "内容方法论",
        "heat": 79,
        "angle": "拆解通用框架,任何内容领域都能套用",
    },
]


def log(agent: str, msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [{agent}] {msg}"
    print(line)
    _run_log.append(line)


_run_log: list[str] = []


# ============================================================
# Stage 1 选题 Agent:按 热度分 x 随机扰动 自动选题
# ============================================================
def stage_select_topic(seed: int, out_dir: Path) -> dict:
    log("选题Agent", f"读取选题池:共 {len(TOPIC_POOL)} 个候选选题")
    rng = random.Random(seed)
    # 加权随机:热度分越高越容易被选中(模拟「数据驱动选题」)
    weights = [t["heat"] + rng.randint(0, 10) for t in TOPIC_POOL]
    picked = rng.choices(TOPIC_POOL, weights=weights, k=1)[0]
    log("选题Agent", f"命中选题:「{picked['title']}」(领域={picked['domain']}, 热度={picked['heat']})")
    log("选题Agent", f"切入角度:{picked['angle']}")

    card = (
        "# 选题卡(Stage 1 产物)\n\n"
        f"- 选题标题:{picked['title']}\n"
        f"- 领域:{picked['domain']}\n"
        f"- 热度分:{picked['heat']}\n"
        f"- 切入角度:{picked['angle']}\n"
        f"- 选题策略:加权随机(权重=热度分+随机扰动, seed={seed})\n"
    )
    (out_dir / "01-topic.md").write_text(card, encoding="utf-8")
    log("选题Agent", "选题卡已写入 output/01-topic.md")
    return picked


# ============================================================
# Stage 2 初稿 Agent:基于选题卡生成结构化 Markdown 初稿
# ============================================================
def stage_draft(topic: dict, out_dir: Path) -> str:
    log("初稿Agent", f"基于选题「{topic['title']}」生成结构化初稿")
    title = topic["title"]
    draft = f"""# {title}

> 导语:很多人以为「AI 写作」= 让 AI 直接写一篇,然后被一眼识破。
> 真正能放进简历、能稳定出稿的做法,是把写作拆成一条流水线:
> **选题 → 初稿 → 排版 → 发布**,每个环节让 AI 做它最擅长的那一步。

## 一、为什么需要一条写稿流水线

写一篇公众号文章,80% 的时间其实花在**没在写**:
反复纠结选题、对着空白文档发呆、排版调半天、发布前才发现格式乱了。

把流程拆开之后,AI 才能真正介入:
- **选题**:让 AI 从选题池里按热度 + 随机扰动自动挑,避免「凭感觉选题」;
- **初稿**:让 AI 按固定结构生成初稿,人只负责补充事实和判断;
- **排版**:让 AI 把 Markdown 转成排版好的 HTML,格式统一、不用手调;
- **发布**:让 AI 记录发布时间、链接、字数,形成可追溯的发布日志。

> 金句:AI 写作不是「让 AI 替你写」,而是「让 AI 替你完成可自动化的部分」。

## 二、四阶段流水线,30 分钟跑通

### Stage 1 选题
选题池里维护 6 个候选,每条带领域、热度分、切入角度。
选择规则:**加权随机** —— 热度分越高越容易被选中,再加一点随机扰动,
保证选题既「追热点」又不「每篇都一样」。

### Stage 2 初稿
根据选题卡,按固定模板生成 Markdown 初稿:
标题、导语、小节标题、要点列表、引用金句、结尾行动号召。
内容结构由模板保证,细节由参数注入,跑一次出一篇。

### Stage 3 排版
一个 200 行的自写 Markdown 渲染器,把初稿转成公众号风格的 HTML:
封面条、正文排版、引用块、代码块,全部内联样式,离线可看、可截图。

### Stage 4 发布
把产物汇总到发布日志:发布时间、输出文件、正文字数、总耗时。
发布渠道可以是公众号草稿箱、飞书文档或本地 HTML —— 流水线只管「交付物一致」。

## 三、真实运行记录

本次运行使用的命令只有一行:

```bash
python pipeline.py --seed 42
```

产物一览:

| 阶段 | 产物 | 说明 |
| --- | --- | --- |
| 1 选题 | 01-topic.md | 选题卡:标题 / 领域 / 热度 / 角度 |
| 2 初稿 | 02-draft.md | 结构化 Markdown 初稿 |
| 3 排版 | 03-final.html | 公众号风格 HTML,可直接打开 |
| 4 发布 | 04-publish.log | 发布时间 / 链接 / 字数统计 |

整个流水线只依赖 Python 标准库,复制到任何电脑都能跑,
这也正是它适合放进作品集的原因:**评委可以自己复现**。

## 四、踩过的坑与改进方向

- **坑 1:让 AI 一次写完,质量不可控** → 改成四阶段,每阶段一个明确产物;
- **坑 2:排版依赖在线资源,离线就打不开** → 全部内联 CSS,截图稳定;
- **坑 3:没有日志,跑完不知道发生了什么** → 增加发布日志,每次运行留痕;
- **下一步**:把选题池接进飞书多维表格,用定时任务每天自动选题 + 生成初稿。

## 五、复跑指南

```bash
# 1. 克隆或下载本项目(仅需 Python 3.8+,无需任何第三方库)
# 2. 进入项目目录,运行:
python pipeline.py --seed 42
# 3. 打开 output/03-final.html 查看排版结果
# 4. 查看 output/04-publish.log 确认发布记录
```

---

**结尾**:这条流水线 30 分钟就能搭好,但它最大的价值不是省时间,
而是让你拥有一个**可复现、可改进、可展示**的 AI 作品。
如果你也想做一个,从今天的选题池里挑一个开始。

<center>—— 本文由 AI 流水线自动生成,人在环上负责判断 ——</center>
"""
    (out_dir / "02-draft.md").write_text(draft, encoding="utf-8")
    word_count = len(re.sub(r"\s", "", draft))
    log("初稿Agent", f"初稿完成:共 {word_count} 字(去空白),已写入 output/02-draft.md")
    return draft


# ============================================================
# Stage 3 排版 Agent:Markdown -> 公众号风格 HTML(纯内联样式)
# ============================================================
def _render_inline(text: str) -> str:
    """渲染行内语法:**加粗** 与 `代码`"""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def _md_to_html(md: str) -> str:
    """200 行以内的小型 Markdown -> HTML 渲染器,足够公众号排版用"""
    lines = md.split("\n")
    html: list[str] = []
    in_list = False
    in_code = False
    code_buf: list[str] = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                html.append('<pre class="code"><code>' + "\n".join(code_buf) + "</code></pre>")
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        if line.startswith("|"):
            continue  # 表格在 HTML 模板中以静态块呈现,跳过
        if not line.strip():
            if in_list:
                html.append("</ul>")
                in_list = False
            continue
        if line.startswith("# "):
            html.append(f'<h1 class="art-title">{_render_inline(line[2:])}</h1>')
        elif line.startswith("## "):
            html.append(f'<h2 class="sec-title">{_render_inline(line[3:])}</h2>')
        elif line.startswith("### "):
            html.append(f'<h3 class="sub-title">{_render_inline(line[4:])}</h3>')
        elif line.startswith("> "):
            html.append(f'<blockquote>{_render_inline(line[2:])}</blockquote>')
        elif line.startswith("- "):
            if not in_list:
                html.append('<ul class="list">')
                in_list = True
            html.append(f"<li>{_render_inline(line[2:])}</li>")
        elif line.startswith("---"):
            html.append('<hr class="divider"/>')
        elif line.strip().startswith("<center>"):
            html.append('<p class="center">{}</p>'.format(_render_inline(line.strip()[8:-9])))
        else:
            html.append(f'<p class="para">{_render_inline(line)}</p>')
    if in_list:
        html.append("</ul>")
    if in_code:
        html.append('<pre class="code"><code>' + "\n".join(code_buf) + "</code></pre>")
    return "\n".join(html)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title} | AI Pipeline 自动排版</title>
<style>
  body {{ margin:0; background:#f4f4f4; font-family: -apple-system,"PingFang SC","Microsoft YaHei",sans-serif; color:#333; }}
  .cover {{ padding:56px 24px 40px; background:linear-gradient(135deg,#1f3b73 0%,#2f5da8 55%,#4a90d9 100%); color:#fff; text-align:center; }}
  .cover .tag {{ display:inline-block; font-size:12px; letter-spacing:2px; border:1px solid rgba(255,255,255,.6); border-radius:20px; padding:4px 14px; margin-bottom:18px; }}
  .cover h1 {{ font-size:24px; line-height:1.5; margin:0 0 14px; font-weight:700; }}
  .cover .meta {{ font-size:13px; opacity:.85; }}
  .wrap {{ max-width:680px; margin:0 auto; background:#fff; padding:36px 28px 48px; box-shadow:0 2px 12px rgba(0,0,0,.06); }}
  .art-title {{ font-size:22px; line-height:1.55; margin:0 0 22px; color:#1a1a1a; }}
  .sec-title {{ font-size:18px; margin:30px 0 12px; padding-left:10px; border-left:4px solid #2f5da8; color:#1f3b73; }}
  .sub-title {{ font-size:15px; margin:18px 0 8px; color:#2f5da8; }}
  .para {{ font-size:15.5px; line-height:1.9; margin:10px 0; text-align:justify; }}
  blockquote {{ margin:16px 0; padding:12px 16px; background:#eef3fb; border-left:4px solid #4a90d9; color:#3d5271; border-radius:0 6px 6px 0; font-size:14.5px; }}
  .list {{ padding-left:22px; }}
  .list li {{ font-size:15px; line-height:1.85; margin:6px 0; }}
  .code {{ background:#0f172a; color:#e2e8f0; padding:16px; border-radius:8px; overflow-x:auto; font-size:13px; line-height:1.7; font-family:Consolas,Menlo,monospace; }}
  .divider {{ border:none; border-top:1px dashed #ccc; margin:28px 0; }}
  .center {{ text-align:center; color:#888; font-size:13px; margin:18px 0; }}
  .footer-card {{ background:linear-gradient(135deg,#1f3b73,#4a90d9); color:#fff; border-radius:10px; padding:22px; text-align:center; margin-top:34px; }}
  .footer-card h3 {{ margin:0 0 8px; font-size:17px; }}
  .footer-card p {{ margin:4px 0; font-size:13.5px; opacity:.92; }}
  .stamp {{ display:inline-block; margin-top:10px; font-size:12px; border:1px solid rgba(255,255,255,.7); border-radius:16px; padding:3px 12px; }}
</style>
</head>
<body>
<div class="cover">
  <div class="tag">AI CONTENT PIPELINE · 最小作品</div>
  <h1>{title}</h1>
  <div class="meta">四阶段流水线自动生成 · 选题 → 初稿 → 排版 → 发布</div>
</div>
<div class="wrap">
{body}
  <div class="footer-card">
    <h3>这条流水线是怎么跑通的?</h3>
    <p>选题卡 / 初稿 / 排版 HTML / 发布日志,全部由一次命令生成。</p>
    <p>复现方式:<code style="background:rgba(255,255,255,.18);padding:2px 8px;border-radius:4px;">python pipeline.py --seed {seed}</code></p>
    <div class="stamp">产出时间 {publish_time} · 全流程 {duration}s</div>
  </div>
</div>
</body>
</html>
"""


def stage_typeset(md: str, topic: dict, out_dir: Path, meta: dict) -> str:
    log("排版Agent", "将 Markdown 初稿转换为公众号风格 HTML(内联样式,离线可看)")
    body = _md_to_html(md)
    html = HTML_TEMPLATE.format(
        title=topic["title"],
        body=body,
        seed=meta["seed"],
        publish_time=meta["publish_time"],
        duration=meta["duration"],
    )
    final_path = out_dir / "03-final.html"
    final_path.write_text(html, encoding="utf-8")
    log("排版Agent", f"排版完成,已写入 output/03-final.html ({final_path.stat().st_size/1024:.1f} KB)")
    return html


# ============================================================
# Stage 4 发布 Agent:汇总发布日志
# ============================================================
def stage_publish(out_dir: Path, meta: dict, word_count: int) -> None:
    log("发布Agent", "汇总本次运行的发布信息")
    publish_log = (
        "# 发布日志(Stage 4 产物)\n\n"
        f"- 发布状态: ✅ 已发布(本地产物就绪)\n"
        f"- 发布时间:{meta['publish_time']}\n"
        f"- 发布渠道:公众号草稿 / 飞书文档 / 本地 HTML(三选一)\n"
        f"- 主产物:output/03-final.html\n"
        f"- 正文字数:{word_count} 字(去空白)\n"
        f"- 全流程耗时:{meta['duration']} 秒\n"
        f"- 随机种子:{meta['seed']}(固定后可复现选题)\n"
        f"- 本次运行文件:\n"
        f"  - output/01-topic.md(选题卡)\n"
        f"  - output/02-draft.md(初稿)\n"
        f"  - output/03-final.html(排版成品)\n"
        f"  - output/04-publish.log(本文件)\n"
    )
    (out_dir / "04-publish.log").write_text(publish_log, encoding="utf-8")
    log("发布Agent", "发布日志已写入 output/04-publish.log")


# ============================================================
# main:串联四阶段
# ============================================================
def main() -> None:
    parser = argparse.ArgumentParser(description="AI Content Pipeline(MVP)")
    parser.add_argument("--seed", type=int, default=42, help="随机种子,固定后选题可复现")
    parser.add_argument("--out", type=str, default="output", help="输出目录")
    args = parser.parse_args()

    out_dir = BASE_DIR / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 60)
    print("  AI CONTENT PIPELINE · 最小可运行流水线")
    print("  选题 → 初稿 → 排版 → 发布")
    print(f"  开始时间:{now_str} · seed={args.seed}")
    print("=" * 60)

    topic = stage_select_topic(args.seed, out_dir)
    draft = stage_draft(topic, out_dir)
    meta = {
        "seed": args.seed,
        "publish_time": now_str,
        "duration": round(time.time() - start, 1),
    }
    stage_typeset(draft, topic, out_dir, meta)
    word_count = len(re.sub(r"\s", "", draft))
    stage_publish(out_dir, meta, word_count)

    total = round(time.time() - start, 1)
    print("=" * 60)
    print(f"  ✅ 流水线跑通,总耗时 {total}s,共 4 个阶段,产物 4 个文件")
    print("  打开 output/03-final.html 查看排版成品")
    print("=" * 60)

    # 同步运行日志(供截图/复盘使用)
    (out_dir / "05-run.log").write_text("\n".join(_run_log), encoding="utf-8")


if __name__ == "__main__":
    main()
