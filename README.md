# Paper Deep Reading Skill

**把一篇论文，读成能够讲清楚、判断证据、着手复现并提出研究问题的知识。**

Paper Deep Reading Skill 是面向研究生和科研人员的单篇论文精读工作流。提供 PDF、链接或片段后，智能体可在对话中解释方法和实验、审视证据、构建先修知识与文献关系地图，并结合近期工作提出可验证的新角度；需要成品时可生成带原图证据的中文 HTML。

项目由 Skill 指令和可选的 Python 工具库组成，只有对话模式和工作模式。两种模式都完成单篇论文的学习、证据审视、近期文献检索、知识地图与可验证的改进建议；工作模式还可完成 PDF 解析、图表裁剪、HTML 生成和浏览器检查。运行时使用宿主提供的模型与工具，不固定模型版本或 API；对话模式只需安装 Skill。

## 一条命令安装 Skill

支持 Agent Skills 安装器的环境可以直接从 GitHub 安装：

```bash
npx skills add https://github.com/galaxyxora-cloud/paper-reading-skill --skill paper-deep-reading
```

默认安装到当前项目；若要在 Codex 的所有项目中使用，可在命令末尾加 `-g -a codex`。

也可以直接在 Codex 工作模式中提供项目地址，让 Codex 检查仓库并完成安装：

> 请检查并安装这个论文精读 Skill：https://github.com/galaxyxora-cloud/paper-reading-skill

安装时应读取仓库中的 `skills/paper-deep-reading/SKILL.md` 和安装说明，将完整 Skill 目录放入当前项目或个人技能目录；若要使用 HTML 工作流，再按下文安装 Python 工具库与 Chromium。需要写入个人技能目录或安装依赖时，按当前环境的权限提示操作。

安装后提供论文 PDF 或链接，直接说：

> 阅读并分析这篇论文：<PDF 或链接>

Skill 允许自然语言触发，无需写 Skill 名称或逐项指定分析内容。仅提供标题时会先定位原始论文；来源不明确或无法获取全文时才需要补充材料。

安装前可先检查 [`skills/paper-deep-reading/SKILL.md`](skills/paper-deep-reading/SKILL.md) 及其引用文件。

对话精读只需安装 Skill。生成 HTML 时还需按下方说明安装 Python 工具库。不使用 Node.js 安装器时，可用仓库自带脚本安装 Skill。

## 给一篇论文，能得到什么

默认使用对话模式完成论文的完整学习和审视；只问一个问题时聚焦回答，要求 HTML 或文件交付时使用工作模式。两种模式都覆盖方法、公式、实验、证据、复现、近期文献、知识地图和新方向；工作模式还可提供章节导航、关键图表、实验表格与浏览器验收。

无论使用哪种模式，读者都应逐步能够解释：作者为什么研究这个问题，方法从输入怎样得到输出，每个关键模块为什么存在，公式如何工作，实验究竟证明了什么，以及下一步应该验证什么。

| 理解维度 | 精读会回答的问题 | 具体产出 |
|---|---|---|
| 研究定位 | 研究对象、任务边界和应用场景是什么？ | 问题定义、输入输出、任务假设与一句话贡献 |
| 背景与先修知识 | 读懂本文需要哪些概念？现有路线如何工作？ | 就地解释术语、必要背景、常见 baseline 流程 |
| 研究动机 | 现有方法在哪个具体环节失效？为什么值得解决？ | 失败模式、动机图解和问题本质 |
| 创新与相关工作 | 作者改变了什么？哪些组件已有，哪些组合或证据是新增的？ | 贡献拆解与有来源的差异比较，避免仅复述作者的创新声明 |
| 最新研究进展 | 后续工作如何扩展、竞争、复现或修正本文？ | 带检索日期和原始来源的定向文献比较 |
| 知识地图 | 哪些知识是读懂本文的前提？文献之间有哪些可靠关系？ | 按学习顺序排列的先修概念、带来源的文献关系与研究机会 |
| 方法全貌 | 训练与推理分别经过哪些步骤？ | 输入→中间表示→模块→输出的完整数据流 |
| 模块机制 | 模块为何这样设计？替代选择是什么？ | 设计动机、机制、接口、作用、证据与风险 |
| 数学理解 | 每个符号、维度、运算和假设是什么意思？ | 关键公式逐项解释、必要推导、边界情形与直觉 |
| 优化与理论 | loss 如何驱动目标行为？理论结论依赖什么条件？ | 目标与模块的对应关系；适用时解释定理、证明思路与适用边界 |
| 算法与实现 | 怎样从论文描述写出可执行步骤？ | 算法流程、张量或数据结构、更新顺序和实现易错点 |
| 实验设置 | 数据如何划分？指标测量什么？比较是否公平？ | benchmark、设置、指标方向、混杂因素和可比性解释 |
| 主结果与消融 | 提升来自哪里？哪些结论被支持，哪些仍未被证明？ | 按研究问题组织的结果、数值差异和替代解释 |
| 可靠性与局限 | 统计波动、数据泄漏、分布变化或失败案例影响多大？ | 有依据的可信度分析与适用范围 |
| 复现与工程 | 最小复现需要什么？算力与延迟瓶颈在哪？ | 复现路线、已知配置、缺失信息、排错顺序与监控指标 |
| 后续研究 | 哪个问题最值得继续验证？如何设计低成本实验？ | 假设、变量、对照、评价标准与可能反证 |
| 优化方向 | 哪些具体改动最值得尝试，近期工作是否已经覆盖？ | 依据、改动、最小实验、成败判据、风险与优先级 |
| 学习与表达 | 我是否真的理解，而不只是记住术语？ | 常见误解、带解释的自测问答，以及组会讲述主线 |

这些维度按论文实际内容展开。理论论文侧重假设和证明，方法论文侧重机制与实验，数据集论文侧重采样、标注与评测，系统论文侧重成本与部署。没有训练、定理或消融的论文不会被强行补上这些内容。

## 分析深度如何保证

### 先建立全局，再解释细节

精读先把问题、现有方法和完整 pipeline 讲清，再进入模块。每个模块沿“为什么需要 → 怎么做 → 公式与实现 → 证据 → 局限”展开。公式和图表出现在它们参与论证的位置，不单独堆成公式仓库或图片目录。

### 从符号走到可执行理解

对关键公式解释输入输出、变量含义、形状或单位、运算方向、参数来源，以及训练或推理中的作用。需要补充中间推导或简单例子时明确标成读者理解辅助；不会给自行推导的表达编造论文 Equation 编号。对于论文跳过或无法确认的步骤，指出缺口。

### 从“结果更好”走到证据判断

不仅呈现分数，还解释数据、模型规模、训练预算、评测协议是否一致，绝对提升和相对提升分别是多少，消融真正控制了哪个变量。没有重复实验、置信区间或关键对照时如实说明；不把单个最优结果当成稳健性证据。

### 从“读懂”走到复现与研究

给出最小可验证的复现路径，区分论文明确提供的设置与需要自行选择的设置。研究建议写成可检验假设：改变什么、保持什么不变、观察什么指标、什么结果会否定该想法。需要准备组会或检验理解时，再补充针对本文的自测问答。

### 把概念与文献串成知识地图

以目标论文为中心，标出读懂方法所需的概念、关键方法与实验证据、前序和后续论文之间有来源的关系。知识缺口按默认读者背景建议学习顺序；新角度附最小验证实验，并标明当前检索范围内是否已有相近工作。关系少时用短列表，复杂时再用表格或图示。

### 按问题分配上下文

完整分析先定位论文主张和关键证据，再定向阅读相关章节、图表与少量高相关文献。后续追问复用已核验的来源定位；只问一个公式或实验时仅展开对应部分，不重复整篇分析。

## 如何交给智能体使用

完成下方安装后，提供 PDF、链接、截图、公式或论文片段即可开始。未提供学科基础时默认面向具有相关专业基础、但不熟悉该论文具体方法的研究生。

对话模式：

```text
阅读并分析这篇论文：<PDF 或链接>
```

连续追问可以直接说“把这个公式再推一步”“这个消融能证明什么”或“如果我要复现，先做哪部分”。Skill 会沿用完整分析中已核验的上下文，只补充当前问题需要的新层次。

工作模式：

```text
阅读并分析这篇论文，生成 HTML：<PDF 或链接>
```

也可以补充“我刚入门”“重点讲推导”“准备复现”“准备组会”或“评估能否作为课题”。这些偏好调整内容选择和解释深度，不要求用户先填写背景问卷。

## 可恢复任务状态

工作模式下，每篇论文任务可用 `workspace` 创建结构化 `state.json`，集中记录阅读目标、当前阶段、证据与主张关系、公式符号、产物身份、未决问题、失败次数和下一步。通过 `state-check` 可在中断、上下文压缩、换会话或交付前核对可信断点，从文件继续工作，不依赖对话中的隐含记忆。对话模式复用简短的来源定位与已核验结论，不反复输入全文。

## 阅读依据与交付边界

- 两种模式的完整分析都应读取可获得的全文、关键图表和相关附录；只有摘要、截图或片段时只能给暂定分析，并明确完成全文审视所缺的材料。
- 工作模式的最终 HTML 必须获取和读取 PDF 正文，定位关键图表与公式，并追踪支撑核心结论的附录和补充材料；不能仅凭摘要生成。
- 原文结论、智能体的解释、独立推断和研究建议分别标识，不混写成作者已验证的结果。
- 两种模式默认检索最新高度相关文献，注明检索日期和覆盖范围；引用外部背景或相关工作时使用原始来源，资源状态和接收信息按当前来源确认。
- 成品中的图表保留编号、页码、坐标轴、图例和重要脚注；复刻表格逐格核对数值。
- 自动校验保证文件与展示流程的基本可靠性，不能替代科学判断。信息不足时保留问题和证据缺口，而不是编造完整答案。

当前版本：0.5.0。工作模式需要 Python 3.10+（建议 3.12）、独立虚拟环境、`.[qa]` 中的 PyMuPDF、Beautiful Soup、Jinja2、jsonschema、Playwright 等包，以及 Chromium。对话模式无需这些本地依赖。

## 工作模式：安装 Python 工具库

先获取完整源码并进入仓库根目录：

```bash
git clone https://github.com/galaxyxora-cloud/paper-reading-skill.git
cd paper-reading-skill
```

已有源码时直接进入包含 `pyproject.toml` 的目录。安装需要网络；后续读取本地 PDF 和生成 HTML 不需要网络，公式在线排版检查需要访问 MathJax CDN。

Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install ".[qa]"
.\.venv\Scripts\python.exe -m playwright install chromium
```

若没有 `py` 命令，用已安装 Python 的完整路径替换。直接调用虚拟环境中的解释器，无需激活脚本或修改 PowerShell 执行策略。

macOS/Linux：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install ".[qa]"
.venv/bin/python -m playwright install chromium
```

Linux 缺少浏览器系统依赖时，按 Playwright 提示运行 `python -m playwright install --with-deps chromium`，可能需要管理员权限。下面统一以 `python` 表示这个虚拟环境的解释器；没有激活环境时用其完整路径替换，所有命令必须使用同一解释器。

## 安装 Skill

将 Skill 放到目标智能体的技能根目录。脚本参数是根目录，脚本会自动添加 `paper-deep-reading` 子目录；不会覆盖已有 Skill。

```bash
python scripts/install_skill.py --target "你的技能根目录"
```

Codex 常见位置是 `~/.codex/skills`。其他智能体使用各自配置的目录。脚本会完整复制 SKILL.md、agents 和 references。Python 工具库另外安装在虚拟环境中，单独复制 Skill 不会自动安装库。给智能体明确的 Python 解释器路径，或将虚拟环境激活后启动智能体。

调用示例：

> 阅读并分析这篇论文：<PDF 或链接>

## 工作模式标准流程

1. **环境与输入**：运行 doctor，用 workspace 为每篇论文建立独立任务目录和可恢复 state.json；继续任务先运行 state-check。
2. **获取与解析**：优先提供的 URL，必要时网页 PDF 链接/arXiv 回退；保存下载日志与逐页解析报告。
3. **核验与裁剪**：智能体阅读正文、定位元素、渲染原页后裁剪；核验裁剪、公式与表格数值，不能只读摘要。
4. **写作**：按 Skill 的理解路径填 article.json，核查资源、接收信息；人工核验字段只能在真实检查后设为 true。
5. **草稿与检查**：build → check → browser-check，查看三种视口截图，修复问题后重跑。
6. **最终交付**：finalize 核对通过的 QA 报告与 HTML 哈希后复制成品，交付单文件和准确自检。

```bash
python -m paper_reading workspace https://arxiv.org/pdf/论文编号 --out work/paper-id
python -m paper_reading state-check work/paper-id/state.json
python -m paper_reading fetch https://arxiv.org/pdf/论文编号 --out work/paper-id/paper.pdf
python -m paper_reading inspect work/paper-id/paper.pdf --out work/paper-id/inspection.json
python -m paper_reading render-page work/paper-id/paper.pdf --page 3 --out work/paper-id/page3.png
python -m paper_reading crop work/paper-id/paper.pdf --page 3 --box 40 70 550 400 --out work/paper-id/figure1.png
python -m paper_reading build work/paper-id/article.json --out work/paper-id/reading.draft.html
python -m paper_reading check work/paper-id/reading.draft.html
python -m paper_reading browser-check work/paper-id/reading.draft.html --out work/paper-id/browser-check.json
python -m paper_reading finalize work/paper-id/reading.draft.html --qa work/paper-id/browser-check.json --out work/paper-id/reading.html
```

论文编号和裁剪坐标必须根据实际输入替换。article.json 由智能体从 [输入模板](examples/article.json) 创建，模板默认不通过核验。字段规范见 [数据契约](skills/paper-deep-reading/references/tooling.md)，写作要求见 [文章规范](skills/paper-deep-reading/references/writing.md)。`paper-read` 与 `python -m paper_reading` 等价，后者不依赖脚本 PATH。

任何正文/附录修改都要重建并重验；finalize 会拒绝旧报告。API 位于 `paper_reading.core`，提供 fetch、inspect_pdf、render、build、check_html、finalize。CLI 失败退出码为 2，异常原因会写到终端；浏览器检查失败也会保存 JSON。

## 目录职责

```text
paper-reading-skill/
  skills/paper-deep-reading/
    SKILL.md
    agents/openai.yaml
    references/conversation.md
    references/literature.md
    references/tooling.md
    references/state.md
    references/writing.md
    references/graduate-reading.md
  src/paper_reading/
    __init__.py
    __main__.py
    cli.py
    core.py
    qa.py
    schemas/article.schema.json
    schemas/workspace.schema.json
    templates/reading.html
  examples/article.json
  scripts/install_skill.py
  scripts/smoke.py
  scripts/release.py
  tests/test_pipeline.py
  .github/workflows/tests.yml
  pyproject.toml
  README.md
  VALIDATION.md
  LICENSE
  .gitignore
```

## 已知边界与排错

- PDF 文本提取和元素定位是候选，不保证复杂双栏、公式顺序或扫描件自动正确。扫描 PDF 先外部 OCR，并对照原页；不能虚填核验字段。
- build 检查 JSON 结构、PDF/裁剪来源哈希、正文长度、局部图表与 HTML 约束，不能独立证明科学内容正确。finalize 的报告是流程记录，不是防伪签名。
- 图片和正文单文件离线可读；MathJax 3.2.2 使用 CDN，断网显示原始 LaTeX，不承诺离线公式排版。
- 浏览器报告检查数量、错误、非空 SVG、导航和页面溢出；数学语义、局部公式截断、表格数值仍要目视检查。
- doctor 失败：检查是否使用正确 Python、是否安装 `.[qa]` 与 Chromium。browser-check 失败：读取 JSON；CDN 失败则恢复网络后重新检查。
- 输出路径不能等于输入路径；文件写入使用原子替换。更换 PDF 版本必须重新 inspect 与 crop。
- 输入 HTML 只允许文章标签；不接受任意网页原样粘贴或脚本。资源链接只能使用 HTTP(S)。下载最多 12 个候选、每请求 30 秒、100 MiB 上限。
