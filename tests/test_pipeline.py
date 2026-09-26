import json
import io
import pymupdf as fitz
import pytest
from paper_reading.core import build, dump, fetch, inspect_pdf, render, check_html, finalize, digest


@pytest.fixture
def case(tmp_path):
    pdf = tmp_path / "paper.pdf"
    with fitz.open() as doc:
        p = doc.new_page()
        p.insert_textbox(fitz.Rect(40, 30, 550, 400), "Test Paper\nAuthor\nAbstract\n" + "Evidence and method text. " * 60)
        p.draw_rect(fitz.Rect(60, 420, 500, 600))
        p.insert_text((70, 620), "Figure 1. Synthetic test only")
        doc.save(pdf)
    inspect_pdf(pdf, tmp_path / "inspection.json")
    render(pdf, 1, tmp_path / "fig.png", [40, 410, 530, 640])
    article = {"title":"Test", "authors":"Test", "affiliations":"Test", "contribution":"Synthetic fixture",
       "pdf":"paper.pdf", "inspection":"inspection.json", "resources":[],
       "verification":dict(title_authors_abstract_sections=True,element_locations_reviewed=True,crops_visually_reviewed=True),
       "figures":[dict(id="fig1",path="fig.png",label="Figure 1",caption="Synthetic",page=1)],
       "sections":[dict(id="method",title="Method",html='<p>Test</p><figure data-asset="fig1"></figure><div class="equation">\\[x = 1\\]</div>')],"audit":[]}
    return tmp_path, article


def test_roundtrip(case):
    path, data = case
    dump(path / "article.json", data)
    build(path / "article.json", path / "out.html")
    html = (path / "out.html").read_text(encoding="utf-8")
    assert "data:image/png;base64," in html
    assert r"\[x = 1\]" in html
    assert not check_html(html)


def test_missing_figures_blocked(case):
    path, data = case
    data["figures"] = []
    dump(path / "article.json", data)
    with pytest.raises(ValueError, match="缺少图表"):
        build(path / "article.json", path / "out.html")
    assert not (path / "out.html").exists()


def test_tampered_crop_blocked(case):
    path, data = case
    with (path / "fig.png").open("ab") as f:
        f.write(b"tamper")
    dump(path / "article.json", data)
    with pytest.raises(ValueError, match="来源凭证"):
        build(path / "article.json", path / "out.html")


def test_full_page_crop_blocked(case):
    path, _ = case
    with pytest.raises(ValueError, match="整页"):
        render(path / "paper.pdf", 1, path / "bad.png", [0,0,595,842])


def test_bad_local_pdf(tmp_path):
    source = tmp_path / "bad.pdf"
    source.write_bytes(b"not pdf")
    with pytest.raises(ValueError, match="不是可读 PDF"):
        fetch(str(source), tmp_path / "out.pdf")


def test_unreviewed_blocked(case):
    path, data = case
    data["verification"]["element_locations_reviewed"] = False
    dump(path / "article.json", data)
    with pytest.raises(ValueError, match="证据门槛"):
        build(path / "article.json", path / "out.html")


def test_external_image_and_bad_math():
    errors = check_html('<img src="https://example.com/image.png"><p>\\[x</p>')
    assert len(errors) == 2


@pytest.mark.parametrize("html", [r"\[\frac{1}{2\]", r"\[\]", r"\[x \left(\]", r"\[x \tag{1}\tag{2}\]", r"\[x &lt; y\]"])
def test_invalid_math(html):
    assert check_html(html)


def test_input_overwrite_rejected(case):
    path, data = case
    dump(path / "article.json", data)
    original = (path / "paper.pdf").read_bytes()
    with pytest.raises(ValueError, match="覆盖"):
        build(path / "article.json", path / "paper.pdf")
    assert (path / "paper.pdf").read_bytes() == original


def test_schema_failure(case):
    path, data = case
    data["sections"] = []
    dump(path / "article.json", data)
    with pytest.raises(ValueError, match="字段错误"):
        build(path / "article.json", path / "out.html")


@pytest.mark.parametrize("html", ['<video src="https://example.com/a"></video>', '<p onclick="alert(1)">x</p>', '<a href="javascript:alert(1)">x</a>'])
def test_active_content_blocked(case, html):
    path, data = case
    data["sections"][0]["html"] += html
    dump(path / "article.json", data)
    with pytest.raises(ValueError):
        build(path / "article.json", path / "out.html")


def test_pdf_version_mismatch(case):
    path, data = case
    with (path / "paper.pdf").open("ab") as stream:
        stream.write(b"\nchanged")
    dump(path / "article.json", data)
    with pytest.raises(ValueError, match="版本"):
        build(path / "article.json", path / "out.html")


def test_missing_local_pdf(tmp_path):
    with pytest.raises(ValueError, match="不存在"):
        fetch(str(tmp_path / "missing.pdf"), tmp_path / "out.pdf")


def test_blank_pdf_blocked(tmp_path):
    with fitz.open() as doc:
        doc.new_page()
        doc.save(tmp_path / "blank.pdf")
    report = inspect_pdf(tmp_path / "blank.pdf", tmp_path / "inspection.json")
    assert report["text_chars"] == 0


def test_local_fetch(case):
    path, _ = case
    fetch(path / "paper.pdf", path / "copy.pdf")
    assert (path / "copy.pdf").read_bytes() == (path / "paper.pdf").read_bytes()


def test_no_figures_exception(case):
    path, data = case
    data["figures"] = []
    data["verification"].update(figure_exception="none_in_pdf", exception_reason="Synthetic no-figure contract test")
    data["sections"][0]["html"] = "<p>No visible figures in this contract test.</p>"
    dump(path / "article.json", data)
    build(path / "article.json", path / "out.html")
    assert (path / "out.html").exists()


def test_unverified_example():
    path = __import__("pathlib").Path(__file__).parents[1] / "examples/article.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert not any(data["verification"].values())


def test_finalize_rejects_stale_report(case):
    path, data = case
    dump(path / "article.json", data)
    build(path / "article.json", path / "draft.html")
    dump(path / "qa.json", {"passed":True,"html_sha256":digest(path / "draft.html")})
    finalize(path / "draft.html", path / "qa.json", path / "final.html")
    with (path / "draft.html").open("a", encoding="utf-8") as stream:
        stream.write(" changed")
    with pytest.raises(ValueError, match="已更改"):
        finalize(path / "draft.html", path / "qa.json", path / "final.html")


def test_failed_finalize(case):
    path, _ = case
    (path / "draft.html").write_text("<p>test</p>", encoding="utf-8")
    dump(path / "qa.json", {"passed":False,"html_sha256":digest(path / "draft.html")})
    with pytest.raises(ValueError, match="未通过"):
        finalize(path / "draft.html", path / "qa.json", path / "final.html")


def test_arxiv_failure_then_page_fallback(case, monkeypatch):
    import paper_reading.core as core
    path, _ = case
    seen = []
    class Response(io.BytesIO):
        def __init__(self, value, url):
            super().__init__(value)
            self.url = url
    def opener(request, timeout):
        seen.append(request.full_url)
        if request.full_url.endswith("/pdf/1234.56789"):
            raise OSError("HTTP 503 test")
        if "/abs/" in request.full_url:
            return Response(b'<a href="/download/paper.pdf">PDF</a>', request.full_url)
        return Response((path / "paper.pdf").read_bytes(), request.full_url)
    monkeypatch.setattr(core, "urlopen", opener)
    fetch("https://arxiv.org/pdf/1234.56789", path / "download.pdf")
    assert seen == ["https://arxiv.org/pdf/1234.56789", "https://arxiv.org/abs/1234.56789", "https://arxiv.org/download/paper.pdf"]
    assert (path / "download.pdf").read_bytes() == (path / "paper.pdf").read_bytes()


def test_network_failure_logs(tmp_path, monkeypatch):
    import paper_reading.core as core
    def opener(request, timeout):
        raise OSError("Network unavailable test")
    monkeypatch.setattr(core, "urlopen", opener)
    with pytest.raises(ValueError, match="获取失败"):
        fetch("https://example.com/paper.pdf", tmp_path / "paper.pdf")
    report = json.loads((tmp_path / "paper.pdf.fetch.json").read_text(encoding="utf-8"))
    assert report["attempts"][0]["result"] == "error"
    assert not (tmp_path / "paper.pdf").exists()


@pytest.mark.parametrize("page,box", [(0,None),(2,None),(1,[-10,0,20,20])])
def test_invalid_crop_requests(case, page, box):
    path, _ = case
    with pytest.raises(ValueError):
        render(path / "paper.pdf", page, path / "invalid.png", box)


def test_workspace_state_roundtrip(tmp_path):
    from paper_reading.core import init_workspace, check_state
    task = tmp_path / "task"
    data = init_workspace("https://example.com/paper.pdf", task)
    assert data["stage"] == "initialized"
    report = check_state(task / "state.json")
    assert report["passed"]
    assert report["next_actions"]


def test_workspace_refuses_nonempty_directory(tmp_path):
    from paper_reading.core import init_workspace
    task = tmp_path / "task"
    task.mkdir()
    (task / "keep.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="非空"):
        init_workspace("paper.pdf", task)
    assert (task / "keep.txt").read_text(encoding="utf-8") == "keep"


def test_state_check_detects_missing_artifact_and_evidence(tmp_path):
    from paper_reading.core import init_workspace, check_state, dump
    task = tmp_path / "task"
    data = init_workspace("paper.pdf", task)
    data["artifacts"]["pdf"] = {"kind": "pdf", "path": "paper.pdf", "status": "ready"}
    data["claims"].append({"id": "cl-main", "text": "Claim", "status": "supported", "confidence": "high", "evidence_ids": ["ev-missing"]})
    dump(task / "state.json", data)
    report = check_state(task / "state.json")
    assert not report["passed"]
    assert any("产物不存在" in item for item in report["errors"])
    assert any("未知证据" in item for item in report["errors"])


def test_finalized_state_requires_verified_html(tmp_path):
    from paper_reading.core import init_workspace, check_state, dump
    task = tmp_path / "task"
    data = init_workspace("paper.pdf", task)
    data["stage"] = "finalized"
    dump(task / "state.json", data)
    report = check_state(task / "state.json")
    assert not report["passed"]
    assert any("final-html" in item for item in report["errors"])


def test_state_check_rejects_outside_artifact(tmp_path):
    from paper_reading.core import init_workspace, check_state, dump
    task = tmp_path / "task"
    data = init_workspace("paper.pdf", task)
    data["artifacts"]["outside"] = {"kind": "other", "path": "../outside.txt", "status": "planned"}
    dump(task / "state.json", data)
    report = check_state(task / "state.json")
    assert not report["passed"]
    assert any("越出任务目录" in item for item in report["errors"])