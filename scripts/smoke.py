import argparse
import functools
import json
import os
import subprocess
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pymupdf as fitz


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def run(root, *args, expected=0, env=None):
    result = subprocess.run([sys.executable, "-m", "paper_reading", *map(str, args)], cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if result.returncode != expected:
        raise RuntimeError(f"{args}: exit {result.returncode}\n{result.stdout}\n{result.stderr}")
    return {"args": list(map(str, args)), "exit_code": result.returncode}


def smoke(out, browser):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    source = out / "source.pdf"
    with fitz.open() as doc:
        page = doc.new_page()
        page.insert_textbox(fitz.Rect(40, 30, 550, 360), "Synthetic Workflow Test\nTest Author\nAbstract\n1 Method\n" + "This is a generated integration fixture, not a research paper. " * 24, fontsize=10)
        page.draw_rect(fitz.Rect(70, 410, 230, 490), color=(.1, .4, .5))
        page.draw_rect(fitz.Rect(330, 410, 490, 490), color=(.1, .4, .5))
        page.draw_line(fitz.Point(230, 450), fitz.Point(330, 450))
        page.insert_text((100, 455), "Input")
        page.insert_text((370, 455), "Output")
        page.insert_text((60, 530), "Figure 1. Synthetic pipeline fixture")
        page.insert_text((60, 610), "Table 1. Synthetic values: A 1, B 2")
        page.insert_text((60, 650), "Algorithm 1. Identity mapping")
        page.insert_text((60, 690), "y = x (1)")
        doc.save(source)
    (out / "landing.html").write_text('<html><head><meta name="citation_pdf_url" content="source.pdf"></head></html>', encoding="utf-8")
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(out)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    steps = []
    try:
        steps.append(run(out, "fetch", f"http://127.0.0.1:{server.server_port}/landing.html", "--out", out / "paper.pdf"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    steps.append(run(out, "inspect", out / "paper.pdf", "--out", out / "inspection.json"))
    steps.append(run(out, "render-page", out / "paper.pdf", "--page", 1, "--out", out / "page.png"))
    steps.append(run(out, "crop", out / "paper.pdf", "--page", 1, "--box", 40, 390, 550, 550, "--out", out / "figure1.png"))
    article = {
        "title":"工具链端到端验证页", "authors":"Synthetic Test", "affiliations":"自动生成的测试夹具",
        "contribution":"用于验证 CLI、图表、表格与公式，不是论文精读成果。", "pdf":"paper.pdf", "inspection":"inspection.json",
        "resources":[{"label":"示例链接","url":"https://example.com"}],
        "verification":{"title_authors_abstract_sections":True,"element_locations_reviewed":True,"crops_visually_reviewed":True},
        "figures":[{"id":"fig1","path":"figure1.png","label":"Figure 1","caption":"合成流程图，用于测试局部裁剪与内联。","page":1}],
        "sections":[
            {"id":"overview","title":"测试目的","html":"<p>这是明确标识的合成测试。所有人工核验声明只服务于夹具测试，不能迁移到真实论文。</p>"},
            {"id":"method","title":"输入到输出","html":r'<p>行内变量 \(x\) 与 \(y\)。</p><figure data-asset="fig1"></figure><div class="equation">\[ y = x \tag{1}\]</div><p>Equation 1：恒等映射，测试公式编号。</p><div class="equation">\[ L = \frac{1}{N}\sum_{i=1}^{N}(y_i-\hat y_i)^2 \]</div>'},
            {"id":"results","title":"表格与证据","html":"<table><caption>Table 1 · 合成测试</caption><thead><tr><th>Variant</th><th>Value ↑</th></tr></thead><tbody><tr><td>A</td><td>1</td></tr><tr><td>B</td><td>2</td></tr></tbody></table>"}],
        "audit":[{"item":"范围","status":"合成测试","detail":"不构成任何论文的科学核验。"}]
    }
    article_path = out / "article.json"
    article_path.write_text(json.dumps(article, ensure_ascii=False), encoding="utf-8")
    steps.append(run(out, "build", article_path, "--out", out / "reading.html"))
    steps.append(run(out, "check", out / "reading.html"))
    if browser:
        steps.append(run(out, "browser-check", out / "reading.html", "--out", out / "browser-check.json"))
        steps.append(run(out, "finalize", out / "reading.html", "--qa", out / "browser-check.json", "--out", out / "final.html"))
        malformed = (out / "reading.html").read_text(encoding="utf-8").replace(r"y = x \tag{1}", r"\frac{1} \tag{1}")
        (out / "invalid-math.html").write_text(malformed, encoding="utf-8")
        steps.append(run(out, "browser-check", out / "invalid-math.html", "--out", out / "invalid-math-qa.json", expected=2))
        invalid = json.loads((out / "invalid-math-qa.json").read_text(encoding="utf-8"))
        if invalid["passed"] or not invalid.get("online", {}).get("math_errors"):
            raise RuntimeError("Invalid formula was not detected")
        environment = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=str(out / "missing-browser"))
        steps.append(run(out, "browser-check", out / "reading.html", "--out", out / "missing-browser-qa.json", expected=2, env=environment))
        missing = json.loads((out / "missing-browser-qa.json").read_text(encoding="utf-8"))
        if missing["passed"] or "error" not in missing:
            raise RuntimeError("Missing browser was not detected")
    report = {"passed":True,"browser_tested":browser,"steps":steps}
    (out / "smoke.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="work/smoke")
    parser.add_argument("--browser", action="store_true")
    args = parser.parse_args()
    smoke(args.out, args.browser)
