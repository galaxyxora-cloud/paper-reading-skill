# Paper Deep Reading Skill

**把一篇论文，读成能够讲清楚、判断证据、着手复现并提出研究问题的知识。**

Paper Deep Reading Skill 是面向研究生和科研人员的论文精读工作流。安装后，将论文 PDF 或链接交给智能体，它会按照研究问题、方法机制、数学表达、实验论证和研究价值这条理解路径展开分析，生成图文结合、可追溯到原文证据的中文 HTML 精读页面。

项目由 Skill 阅读规范和 Python 工具库组成。前者指导智能体如何理解与讲解论文，后者负责 PDF 获取、正文解析、局部图表裁剪、页面生成和浏览器检查。它需要具备阅读、推理、执行 Python 和使用浏览器能力的智能体，不绑定特定模型 API，也不把工具运行成功等同于论文已被正确理解。

## 给一篇论文，能得到什么

默认交付适合反复阅读、组会准备和复现参考的单文件 HTML。页面包含固定章节导航、原文关键图表局部裁剪、可读的实验表格、嵌入方法讲解中的数学公式，以及区分事实与分析的结论说明。

读完后，读者应能用自己的话解释：作者为什么研究这个问题，方法从输入怎样得到输出，每个模块为什么存在，关键公式如何工作，实验究竟证明了什么，以及自己下一步应该验证什么。

| 理解维度 | 精读会回答的问题 | 具体产出 |
|---|---|---|
| 研究定位 | 研究对象、任务边界和应用场景是什么？ | 问题定义、输入输出、任务假设与一句话贡献 |
| 背景与先修知识 | 读懂本文需要哪些概念？现有路线如何工作？ | 就地解释术语、必要背景、常见 baseline 流程 |
| 研究动机 | 现有方法在哪个具体环节失效？为什么值得解决？ | 失败模式、动机图解和问题本质 |
| 创新与相关工作 | 作者改变了什么？哪些组件已有，哪些组合或证据是新增的？ | 贡献拆解与有来源的差异比较，避免仅复述作者的创新声明 |
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

给出最小可验证的复现路径，区分论文明确提供的设置与需要自行选择的设置。研究建议写成可检验假设：改变什么、保持什么不变、观察什么指标、什么结果会否定该想法。最后通过自测问答检验对机制、公式、实验和边界的理解。

## 如何交给智能体使用

完成下方安装后，提供 PDF 文件或链接即可开始。未提供学科基础时默认面向具有相关专业基础、但不熟悉该论文具体方法的研究生，首次出现的专业概念仍会解释；无需每次重新粘贴长提示词。

```text
使用 $paper-deep-reading 精读这篇论文：<PDF 链接或文件路径>。
按研究生精读深度解释问题、先修概念、创新、完整方法、关键公式、实验与消融、局限、复现路线和后续研究方向。
最后生成经过图表与公式检查的单文件 HTML，并加入自测问答和组会讲述主线。
```

也可以补充“我刚入门”“重点讲推导”“准备复现”“准备组会”或“评估能否作为课题”。这些偏好调整篇幅分配，不省略关键证据，也不要求用户必须先填写背景问卷。

## 阅读依据与交付边界

- 先获取和读取 PDF 正文，并定位关键图表与公式；不能仅凭摘要生成成品。
- 阅读与核心结论有关的附录和补充材料；引用外部背景或相关工作时核验来源，未能获得的材料明确标记。
- 原文结论、智能体的解释、独立推断和研究建议分别标识，不混写成作者已验证的结果。
- 保留图表编号、页码、坐标轴、图例和重要脚注；复刻表格逐格核对数值。
- 默认覆盖理解一篇论文的主要研究维度，但不承诺穷尽某个学科的所有知识；深度取决于论文可访问材料与调用智能体的能力。
- 自动校验保证文件与展示流程的基本可靠性，不能替代科学判断。信息不足时保留问题和证据缺口，而不是编造完整答案。

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
    references/graduate-reading.md
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
