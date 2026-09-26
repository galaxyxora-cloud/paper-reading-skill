import re
from pathlib import Path

from bs4 import BeautifulSoup

from .core import check_html, digest, dump, guard_output


def browser_check(path, out):
    from playwright.sync_api import sync_playwright

    path, out = Path(path).resolve(), Path(out).resolve()
    guard_output(out, path)
    out.parent.mkdir(parents=True, exist_ok=True)
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    formulas = re.findall(r"\\\[(.*?)\\\]|\\\((.*?)\\\)", soup.get_text(), re.S)
    expected_math = len(formulas)
    result = {"html_sha256": digest(path), "static_errors": check_html(html), "online": {}, "offline": {}, "screenshots": [], "passed": False}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.goto(path.as_uri(), wait_until="domcontentloaded", timeout=45000)
                if expected_math:
                    try:
                        page.wait_for_function("window.MathJax && MathJax.startup && MathJax.startup.document && document.querySelectorAll('mjx-container').length > 0", timeout=45000)
                        page.evaluate("async () => { await MathJax.startup.promise; }")
                        result["online"]["mathjax_loaded"] = True
                    except Exception as exc:
                        result["online"].update(mathjax_loaded=False, error=str(exc)[:300])
                else:
                    result["online"]["mathjax_loaded"] = None
                result["online"]["math_expected"] = expected_math
                result["online"]["math_containers"] = page.locator("mjx-container").count()
                result["online"]["math_errors"] = page.locator('[data-mjx-error], mjx-merror, [data-mml-node="merror"]').count()
                result["online"]["empty_math"] = page.locator("mjx-container").evaluate_all("nodes => nodes.filter(n => n.getBoundingClientRect().height < 2 || !n.querySelector('svg')).length")
                result["online"]["anchors_ok"] = page.locator('nav a').evaluate_all("nodes => nodes.length > 0 && nodes.every(n => document.getElementById(n.hash.slice(1)))")
                for label, width in [("desktop", 1440), ("laptop", 1024), ("mobile", 390)]:
                    page.set_viewport_size({"width": width, "height": 1000})
                    result["online"][label + "_overflow"] = page.evaluate("document.documentElement.scrollWidth > innerWidth + 2")
                    result["online"][label + "_nav_overlap"] = page.evaluate("innerWidth > 900 && document.querySelector('nav').getBoundingClientRect().right > document.querySelector('main').getBoundingClientRect().left + 1")
                    shot = out.with_name(out.stem + "-" + label + ".png")
                    page.screenshot(path=str(shot), full_page=True)
                    result["screenshots"].append(str(shot))
                offline = browser.new_context(offline=True)
                op = offline.new_page()
                op.goto(path.as_uri(), wait_until="load")
                result["offline"] = op.evaluate(r"""() => ({
                    text_chars: document.querySelector('main').innerText.length,
                    images_ok: [...document.images].every(x => x.complete && x.naturalWidth > 0),
                    math_containers: document.querySelectorAll('mjx-container').length,
                    source: document.body.innerText
                })""")
                source = result["offline"].pop("source")
                result["offline"]["latex_preserved"] = all((a or b).strip() in source for a, b in formulas)
                result["passed"] = (not result["static_errors"]
                    and (expected_math == 0 or result["online"].get("mathjax_loaded", False))
                    and result["online"]["math_containers"] == expected_math
                    and result["online"]["math_errors"] == 0
                    and result["online"]["empty_math"] == 0
                    and result["online"]["anchors_ok"]
                    and not any(v for k, v in result["online"].items() if k.endswith(("_overflow", "_nav_overlap")))
                    and result["offline"]["images_ok"]
                    and result["offline"]["text_chars"] > 0
                    and result["offline"]["latex_preserved"]
                    and result["offline"]["math_containers"] == 0)
            finally:
                browser.close()
    except Exception as exc:
        result["error"] = str(exc)
    dump(out, result)
    return result
