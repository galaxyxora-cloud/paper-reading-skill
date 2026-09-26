# 工具与数据契约

命令在仓库安装后跨目录可用，路径支持中文与空格。CLI 的失败退出码为 2；不替智能体写科学结论。

如果命令不在 PATH，用安装该库的 Python 运行 `python -m paper_reading` 替代 `paper-read`。`doctor` 检查版本与 Chromium 文件；实际能否启动浏览器由 browser-check 确认。

```bash
paper-read fetch https://arxiv.org/pdf/XXXX.XXXXX --out work/paper.pdf
paper-read inspect work/paper.pdf --out work/inspection.json
paper-read render-page work/paper.pdf --page 3 --out work/page3.png
paper-read crop work/paper.pdf --page 3 --box 40 70 555 350 --out work/figure1.png
paper-read build work/article.json --out work/reading.draft.html
paper-read check work/reading.draft.html
paper-read browser-check work/reading.draft.html --out work/browser-check.json
paper-read finalize work/reading.draft.html --qa work/browser-check.json --out work/reading.html
```

页码从 1 开始；裁剪坐标为 PDF 页面旋转后的可见坐标，左上原点、单位 point。候选元素检测不可靠时查阅逐页 blocks 与渲染图。全页裁剪默认拒绝。fetch 按给定 URL 优先，再解析页面 PDF 链接，再 arXiv 回退；最多 12 个候选、每请求 30 秒、100 MiB 上限，保留 attempts 日志。不自动绕过登录/付费墙。

`article.json` 是 UTF-8 JSON，示例见仓库 `examples/article.json`。相对路径相对于 JSON 文件目录。

- `title`, `authors`, `affiliations`, `contribution`: 文本。
- `pdf`, `inspection`: 本地 PDF 和 inspect 输出；build 会核对 SHA256 防止用错版本。
- `resources`: `{label,url}` 列表，仅真实 HTTP(S) 资源，来源/检索时间在正文说明。
- `sections`: `{id,title,html}` 列表。html 为智能体创作的可信文章片段，不可直接塞网页内容。支持 p/h3/ul/table 等常见标签，不允许脚本、iframe、外部图片。
- `figures`: `{id,path,label,caption,page}` 列表。正文用 `<figure data-asset="fig1"></figure>`，构建时替换内联图片与说明。每张裁剪须由 crop 创建相邻 `.crop.json` 来源凭证。
- `verification`: `title_authors_abstract_sections`、`element_locations_reviewed`、`crops_visually_reviewed` 均须 true；这是智能体声明，工具无法验证学术语义。`figure_exception` 只允许 `none_in_pdf` / `not_visible_in_pdf`，需 `exception_reason`；仅在论文确实无可见图表时使用，不是网络/解析失败的逃生口。
- `audit`: `{item,status,detail}` 列表，填写真实检查信息；浏览器检查后需回填状态并重新构建。

安装包中包含 `schemas/article.schema.json`，构建时自动检查必填字段、类型和非空内容。输出不得覆盖输入。正文标签采用白名单，外链自动补齐 target 与 rel，图片仅通过 data-asset 插入。输出使用临时文件和原子替换，减少半成品写入风险。

自动工具只能检查数据结构、文件身份、正文长度、来源裁剪、基本 HTML 约束。科学准确性、机构/摘要识别、表格数字、视觉质量仍由调用智能体负责。不要把人工布尔声明称为独立验证。不要手工修改 crop 凭证或 QA 的 passed/hash 字段；它们只应由工具产生。

浏览器 QA 会尝试等待 MathJax、统计错误与溢出，输出桌面/移动截图；随后阻断网络重载，核查正文与图片可用、LaTeX 源码保留。CDN 不可达时在线公式检查会失败，不能宣称通过。离线源码可读是默认契约，离线排版不是。

browser-check 会检查每个公式都生成非空 SVG，报告渲染错误、导航遮挡、视口溢出，并输出 HTML SHA256。finalize 要求报告通过且 hash 一致，之后原样复制草稿到最终文件；不重新渲染，避免验收后引入变化。报告不是签名，不用于防止恶意伪造。
