# Paper Deep Reading Skill

以正文、公式和图表证据为基础，把论文 PDF 制作成中文精读单文件 HTML。适用于能读取 SKILL.md、执行 Python 和启动浏览器的智能体。智能体负责科学内容与来源核验，工具负责文件处理、验证和生成；不绑定任何模型 API。

版本：0.2.0。需要 Python 3.10+；建议 Python 3.12。使用独立虚拟环境，不使用系统 Python 的共享依赖。

## 安装与环境验证

解压源码或克隆仓库，进入包含本文件和 `pyproject.toml` 的目录。以下安装需要网络；后续读取本地 PDF 和生成 HTML 不需要网络，公式在线排版检查需要访问 MathJax CDN。

Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install ".[test,qa]"
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m paper_reading doctor
```

若没有 `py` 命令，用已安装 Python 的完整路径替换。直接调用虚拟环境中的解释器，无需激活脚本或修改 PowerShell 执行策略。

macOS/Linux：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install ".[test,qa]"
.venv/bin/python -m playwright install chromium
.venv/bin/python -m paper_reading doctor
```

Linux 缺少浏览器系统依赖时，按 Playwright 提示运行 `python -m playwright install --with-deps chromium`，可能需要管理员权限。下面统一以 `python` 表示这个虚拟环境的解释器；没有激活环境时用其完整路径替换，所有命令必须使用同一解释器。

开发者修改源码后需重新 `pip install ".[test,qa]"`；需要实时使用源码可改成 `pip install -e ".[test,qa]"`。

## 安装 Skill

将 Skill 放到目标智能体的技能根目录。脚本参数是根目录，脚本会自动添加 `paper-deep-reading` 子目录；不会覆盖已有 Skill。

```bash
python scripts/install_skill.py --target "你的技能根目录"
```

Codex 常见位置是 `~/.codex/skills`。其他智能体使用各自配置的目录。脚本会完整复制 SKILL.md、agents 和 references。Python 工具库另外安装在虚拟环境中，单独复制 Skill 不会自动安装库。给智能体明确的 Python 解释器路径，或将虚拟环境激活后启动智能体。

调用示例：

> 使用 $paper-deep-reading 精读这个 PDF，先确认全文与关键图表可读取，再制作单文件 HTML。使用指定虚拟环境的 Python，完成 browser-check 和 finalize 后交付。

## 标准流程

1. **环境与输入**：运行 doctor，确认 PDF 链接或本地文件，为每篇论文建立独立任务目录。
2. **获取与解析**：优先提供的 URL，必要时网页 PDF 链接/arXiv 回退；保存下载日志与逐页解析报告。
3. **核验与裁剪**：智能体阅读正文、定位元素、渲染原页后裁剪；核验裁剪、公式与表格数值，不能只读摘要。
4. **写作**：按 Skill 的理解路径填 article.json，核查资源、接收信息；人工核验字段只能在真实检查后设为 true。
5. **草稿与检查**：build → check → browser-check，查看三种视口截图，修复问题后重跑。
6. **最终交付**：finalize 核对通过的 QA 报告与 HTML 哈希后复制成品，交付单文件和准确自检。

```bash
python -m paper_reading fetch https://arxiv.org/pdf/论文编号 --out work/paper.pdf
python -m paper_reading inspect work/paper.pdf --out work/inspection.json
python -m paper_reading render-page work/paper.pdf --page 3 --out work/page3.png
python -m paper_reading crop work/paper.pdf --page 3 --box 40 70 550 400 --out work/figure1.png
python -m paper_reading build work/article.json --out work/reading.draft.html
python -m paper_reading check work/reading.draft.html
python -m paper_reading browser-check work/reading.draft.html --out work/browser-check.json
python -m paper_reading finalize work/reading.draft.html --qa work/browser-check.json --out work/reading.html
```

论文编号和裁剪坐标必须根据实际输入替换。article.json 由智能体从 [输入模板](examples/article.json) 创建，模板默认不通过核验。字段规范见 [数据契约](skills/paper-deep-reading/references/tooling.md)，写作要求见 [文章规范](skills/paper-deep-reading/references/writing.md)。`paper-read` 与 `python -m paper_reading` 等价，后者不依赖脚本 PATH。

任何正文/附录修改都要重建并重验；finalize 会拒绝旧报告。API 位于 `paper_reading.core`，提供 fetch、inspect_pdf、render、build、check_html、finalize。CLI 失败退出码为 2，异常原因会写到终端；浏览器检查失败也会保存 JSON。

## 目录职责

```text
paper-reading-skill/
  skills/paper-deep-reading/
    SKILL.md
    agents/openai.yaml
    references/tooling.md
    references/writing.md
  src/paper_reading/
    __init__.py
    __main__.py
    cli.py
    core.py
    qa.py
    schemas/article.schema.json
    templates/reading.html
  examples/article.json
  scripts/install_skill.py
  scripts/smoke.py
  scripts/release.py
  tests/test_pipeline.py
  docs/GITHUB.md
  .github/workflows/tests.yml
  pyproject.toml
  README.md
  VALIDATION.md
  LICENSE
  .gitignore
```

源码发布不包含 `.venv`、`.test-deps`、`work`、缓存或第三方论文。源码包含 Skill 与安装代码；Python wheel 含运行库、HTML 模板、JSON Schema，不单独包含 Skill，分发 Skill 时使用源码包。

## 自行完整测试

```bash
python -m pytest -q
python scripts/smoke.py --out work/smoke --browser
python scripts/release.py
```

smoke 会生成合成 PDF，启动临时 localhost HTTP 服务验证网页→PDF 回退，再通过真实 CLI 执行解析、渲染、裁剪、HTML、静态与浏览器检查、finalize。带 `--browser` 时还会验证错误公式与缺失浏览器均被阻断；这两步预期退出码为 2，不代表测试失败。结束时关闭服务。结果与截图在指定输出目录，页面明确标识是工具测试而非真实论文总结。

release 验证 Python 语法、代码无注释/文档字符串、JSON 语法、配置无注释、模板无注释、Markdown 相对链接存在，并将允许的源文件打包至 `dist/paper-reading-skill-source.zip`。发布包排除缓存与运行产物。当前实测范围见 [验证记录](VALIDATION.md)。

## 已知边界与排错

- PDF 文本提取和元素定位是候选，不保证复杂双栏、公式顺序或扫描件自动正确。扫描 PDF 先外部 OCR，并对照原页；不能虚填核验字段。
- build 检查 JSON 结构、PDF/裁剪来源哈希、正文长度、局部图表与 HTML 约束，不能独立证明科学内容正确。finalize 的报告是流程记录，不是防伪签名。
- 图片和正文单文件离线可读；MathJax 3.2.2 使用 CDN，断网显示原始 LaTeX，不承诺离线公式排版。
- 浏览器报告检查数量、错误、非空 SVG、导航和页面溢出；数学语义、局部公式截断、表格数值仍要目视检查。
- doctor 失败：检查是否使用正确 Python、是否安装 `.[qa]` 与 Chromium。browser-check 失败：读取 JSON；CDN 失败则恢复网络后重新检查。
- 输出路径不能等于输入路径；文件写入使用原子替换。更换 PDF 版本必须重新 inspect 与 crop。
- 输入 HTML 只允许文章标签；不接受任意网页原样粘贴或脚本。资源链接只能使用 HTTP(S)。下载最多 12 个候选、每请求 30 秒、100 MiB 上限。
- 用户的代码与配置无注释要求由发布脚本检查；说明放在 Markdown。第三方依赖的源代码不属于本仓库原创代码范围。

## 上传 GitHub

请按 [完整上传教程](docs/GITHUB.md) 操作：新建空仓库 → 本地提交 → 设置 origin → push → 检查 Actions。不要上传 ZIP 代替源码，也不要把虚拟环境或测试论文加入 Git。

原创代码 MIT 授权。依赖与第三方论文保持各自许可；PyMuPDF 使用 AGPL/商业许可，本项目 MIT 不覆盖它。MathJax 从 CDN 获取，不打包第三方运行时。
