from __future__ import annotations

import base64
import hashlib
import json
import re
import os
import tempfile
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

import pymupdf as fitz
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jsonschema import Draft202012Validator


def write_atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            name = stream.name
            stream.write(data)
        os.replace(name, path)
    finally:
        if name and Path(name).exists():
            Path(name).unlink()


def guard_output(out, *inputs):
    output = Path(out).resolve()
    if output in {Path(p).resolve() for p in inputs}:
        raise ValueError("输出路径不得覆盖输入文件")


def validate_article(data):
    schema = json.loads((Path(__file__).parent / "schemas/article.schema.json").read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: str(list(e.path)))
    if errors:
        error = errors[0]
        raise ValueError("article.json 字段错误 " + ".".join(map(str, error.path)) + ": " + error.message)


def dump(path, value):
    path = Path(path)
    write_atomic(path, json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pdf_valid(data):
    if not data.lstrip().startswith(b"%PDF-"):
        return False
    try:
        with fitz.open(stream=data, filetype="pdf") as doc:
            return len(doc) > 0 and not doc.needs_pass
    except Exception:
        return False


def fetch(source, out):
    source = str(source)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    attempts = []
    if urlparse(source).scheme not in ("http", "https"):
        if not Path(source).is_file():
            raise ValueError("本地 PDF 不存在或 URL 不是 HTTP(S)")
        guard_output(out, source)
        data = Path(source).read_bytes()
        if not pdf_valid(data):
            raise ValueError("本地文件不是可读 PDF")
        write_atomic(out, data)
        dump(str(out) + ".fetch.json", {"source": source, "sha256": digest(out)})
        return
    queue, seen = [source], set()
    match = re.search(r"arxiv\.org/(?:pdf|abs)/(\d{4}\.\d{4,5}(?:v\d+)?|[a-z-]+/\d{7}(?:v\d+)?)", source)
    if match:
        queue += ["https://arxiv.org/abs/" + match[1], "https://arxiv.org/pdf/" + match[1]]
    while queue and len(seen) < 12:
        url = queue.pop(0)
        if url in seen or urlparse(url).scheme not in ("https", "http"):
            continue
        seen.add(url)
        try:
            with urlopen(Request(url, headers={"User-Agent": "PaperReadingKit/0.1"}), timeout=30) as response:
                data = response.read(100 * 1024 * 1024 + 1)
                final_url = response.url
            if len(data) > 100 * 1024 * 1024:
                raise ValueError("超过 100 MiB 下载上限")
            if pdf_valid(data):
                write_atomic(out, data)
                attempts.append({"url": url, "result": "pdf", "final_url": final_url})
                dump(str(out) + ".fetch.json", {"attempts": attempts, "sha256": digest(out)})
                return
            soup = BeautifulSoup(data, "html.parser")
            links = []
            for tag in soup.select('meta[name="citation_pdf_url"], a[href]'):
                link = tag.get("content") or tag.get("href", "")
                if tag.name == "meta" or re.search(r"\.pdf(?:[?#]|$)|/pdf/", link) or tag.get_text(strip=True).lower() == "pdf":
                    links.append(urljoin(final_url, link))
            queue[0:0] = links
            attempts.append({"url": url, "result": "html", "pdf_links": links})
        except Exception as exc:
            attempts.append({"url": url, "result": "error", "message": str(exc)})
    dump(str(out) + ".fetch.json", {"attempts": attempts})
    raise ValueError("PDF 获取失败；见 .fetch.json，尝试浏览器或用户提供的官方页面")


def inspect_pdf(pdf, out):
    guard_output(out, pdf)
    pages = []
    with fitz.open(pdf) as doc:
        if doc.needs_pass:
            raise ValueError("PDF 加密，需要可读取版本")
        for i, page in enumerate(doc):
            text = page.get_text(sort=True)
            candidates = []
            for block in page.get_text("blocks", sort=True):
                if len(block) < 7 or block[6] != 0:
                    continue
                value = block[4]
                kinds = [kind for kind, pattern in {
                    "figure": r"\b(?:Figure|Fig\.)\s*\d+",
                    "table": r"\bTable\s*\d+",
                    "algorithm": r"\bAlgorithm\s*\d+",
                    "equation": r"\(\d+[a-z]?\)",
                    "section": r"(?m)^\d+(?:\.\d+)*\.?\s+[A-Z]",
                }.items() if re.search(pattern, value)]
                if kinds:
                    candidates.append({"kinds": kinds, "bbox": list(block[:4]), "text": value})
            pages.append({"page": i + 1, "width": page.rect.width, "height": page.rect.height,
                          "text": text, "candidates": candidates})
        result = {"pdf_sha256": digest(pdf), "metadata": doc.metadata, "pages": pages,
                  "text_chars": sum(len(p["text"].strip()) for p in pages),
                  "warning": "候选定位需要人工核验；元数据不是标题/作者的充分证据"}
    dump(out, result)
    return result


def render(pdf, page, out, box=None, dpi=160):
    guard_output(out, pdf)
    if Path(out).suffix.lower() != ".png":
        raise ValueError("页面和裁剪输出扩展名必须为 .png")
    if not 72 <= dpi <= 400:
        raise ValueError("dpi 必须在 72–400")
    with fitz.open(pdf) as doc:
        if not 1 <= page <= len(doc):
            raise ValueError("页码越界")
        p = doc[page - 1]
        rect = fitz.Rect(box) if box else p.rect
        if rect.is_empty or not p.rect.contains(rect):
            raise ValueError("裁剪坐标无效或超出页面")
        if box and rect.get_area() / p.rect.get_area() > .92:
            raise ValueError("拒绝近似整页裁剪；请选取局部图表")
        write_atomic(out, p.get_pixmap(dpi=dpi, clip=rect, alpha=False).tobytes("png"))
    if box:
        dump(str(out) + ".crop.json", {"pdf_sha256": digest(pdf), "image_sha256": digest(out),
             "page": page, "box": list(box), "dpi": dpi})


def check_html(html):
    soup = BeautifulSoup(html, "html.parser")
    errors = []
    if soup.select("iframe,object,embed"):
        errors.append("禁止嵌入 PDF/外部对象")
    for img in soup.find_all("img"):
        if not img.get("src", "").startswith("data:image/png;base64,"):
            errors.append("图片未内联为 PNG")
    for link in soup.select("a[href]"):
        href = link["href"]
        if href.startswith("#"):
            if not soup.find(id=href[1:]):
                errors.append("断开的章节锚点: " + href)
        elif urlparse(href).scheme not in ("http", "https") or link.get("target") != "_blank":
            errors.append("外部链接格式或 target 无效")
    text = soup.get_text()
    all_ids = [tag["id"] for tag in soup.select("[id]")]
    if len(all_ids) != len(set(all_ids)):
        errors.append("重复 HTML id")
    for a, b in [(r"\(", r"\)"), (r"\[", r"\]")]:
        if text.count(a) != text.count(b):
            errors.append("公式定界符不匹配")
    for formula in re.findall(r"\\\[(.*?)\\\]|\\\((.*?)\\\)", text, re.S):
        value = "".join(formula)
        if not value.strip():
            errors.append("空公式")
        depth = 0
        for token in re.findall(r"(?<!\\)[{}]", value):
            depth += 1 if token == "{" else -1
            if depth < 0:
                break
        if depth != 0:
            errors.append("公式花括号不匹配")
        if "<" in value or ">" in value:
            errors.append("公式含裸露比较符")
        if value.count(r"\left") != value.count(r"\right"):
            errors.append("left/right 不匹配")
        if len(re.findall(r"\\tag\{", value)) > 1:
            errors.append("单公式重复 tag")
    return errors


def build(article, out):
    article = Path(article)
    data = json.loads(article.read_text(encoding="utf-8"))
    validate_article(data)
    base = article.parent
    pdf = base / data["pdf"]
    guard_output(out, article, pdf, base / data["inspection"], *[base / f["path"] for f in data["figures"]])
    report = json.loads((base / data["inspection"]).read_text(encoding="utf-8"))
    if report["pdf_sha256"] != digest(pdf):
        raise ValueError("PDF 与解析报告版本不一致")
    with fitz.open(pdf) as doc:
        if doc.needs_pass or sum(len(p.get_text().strip()) for p in doc) < 500:
            raise ValueError("正文不足，必须先完成 OCR/正文读取")
    verify = data["verification"]
    for key in ("title_authors_abstract_sections", "element_locations_reviewed"):
        if verify.get(key) is not True:
            raise ValueError("未通过人工证据门槛: " + key)
    figures = data.get("figures", [])
    if not figures:
        if verify.get("figure_exception") not in ("none_in_pdf", "not_visible_in_pdf") or not verify.get("exception_reason"):
            raise ValueError("缺少图表裁剪，不得生成最终 HTML")
    elif verify.get("crops_visually_reviewed") is not True:
        raise ValueError("裁剪尚未目视检查")
    assets = {}
    for fig in figures:
        path = base / fig["path"]
        provenance = json.loads(Path(str(path) + ".crop.json").read_text(encoding="utf-8"))
        if provenance["pdf_sha256"] != digest(pdf) or provenance["image_sha256"] != digest(path) or provenance["page"] != fig["page"]:
            raise ValueError("图表来源凭证不匹配")
        raw = path.read_bytes()
        if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("图表必须是 PNG")
        if fig["id"] in assets:
            raise ValueError("重复图表 id")
        wrapper = BeautifulSoup("<figure><img/><figcaption></figcaption></figure>", "html.parser")
        wrapper.img["src"] = "data:image/png;base64," + base64.b64encode(raw).decode()
        wrapper.img["alt"] = fig["label"]
        wrapper.figcaption.string = f'{fig["label"]} · PDF 第 {fig["page"]} 页。{fig["caption"]}'
        assets[fig["id"]] = str(wrapper)
    ids, used = set(), set()
    for section in data["sections"]:
        if not re.fullmatch(r"[a-z][a-z0-9-]*", section["id"]) or section["id"] in ids:
            raise ValueError("章节 id 无效/重复")
        ids.add(section["id"])
        soup = BeautifulSoup(section["html"], "html.parser")
        allowed = {"p","h3","h4","h5","ul","ol","li","table","thead","tbody","tfoot","tr","th","td","caption","div","span","strong","em","b","i","a","br","hr","figure","blockquote","code","pre","sup","sub","dl","dt","dd"}
        for tag in soup.find_all(True):
            if tag.name not in allowed:
                raise ValueError("正文含不支持标签: " + tag.name)
            if any(k not in {"id","class","href","target","rel","data-asset","colspan","rowspan","scope","title"} for k in tag.attrs):
                raise ValueError("正文含不支持属性")
            if tag.name == "a" and tag.get("href", "").startswith(("https://", "http://")):
                tag["target"] = "_blank"
                tag["rel"] = "noopener noreferrer"
        for placeholder in soup.select("figure[data-asset]"):
            key = placeholder["data-asset"]
            if key not in assets:
                raise ValueError("未知图表: " + key)
            used.add(key)
            placeholder.replace_with(BeautifulSoup(assets[key], "html.parser"))
        section["html"] = str(soup)
    if set(assets) != used:
        raise ValueError("存在未插入正文的图表")
    for resource in data.get("resources", []):
        if urlparse(resource["url"]).scheme not in ("http", "https"):
            raise ValueError("资源必须使用 HTTP(S)")
    env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"), autoescape=select_autoescape())
    html = env.get_template("reading.html").render(**data)
    errors = check_html(html)
    if errors:
        raise ValueError("；".join(errors))
    write_atomic(out, html.encode("utf-8"))


def finalize(source, qa, out):
    guard_output(out, source, qa)
    report = json.loads(Path(qa).read_text(encoding="utf-8"))
    if report.get("passed") is not True or report.get("html_sha256") != digest(source):
        raise ValueError("浏览器验收未通过或 HTML 已更改；请重新检查")
    data = Path(source).read_bytes()
    if check_html(data.decode("utf-8")):
        raise ValueError("最终 HTML 静态检查失败")
    write_atomic(out, data)
