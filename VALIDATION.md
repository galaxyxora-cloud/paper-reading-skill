# 0.2.0 验证记录

测试日期：2026-09-26。执行环境：Windows、Python 3.12.14、Chromium 153.0.8010.12（Playwright 1.63.0）。本次测试覆盖工具链实际执行，不声称任意论文、任意网络或任意操作系统都不会出错。

## 已通过

| 项目 | 实际结果 |
|---|---|
| 新环境安装 | 从独立虚拟环境安装项目、依赖与 Chromium，doctor 成功 |
| 回归测试 | 30 passed，最后一轮 1.12 秒 |
| 标准 CLI 全流程 | fetch → inspect → render-page → crop → build → check → browser-check → finalize，全通过 |
| 网页回退 | localhost 页面 citation_pdf_url 链接下载真实 PDF 字节成功 |
| arXiv 失败回退 | 模拟首个 PDF 503，验证 abs 页面和其 PDF 链接依次被访问 |
| 网络失败 | 验证明确失败、错误日志存在、不会生成新 PDF |
| 图表门槛 | 缺图、未核验、版本不一致、裁剪被篡改、整页/越界裁剪、输入覆盖均被阻断 |
| 数据/HTML | Schema 错误、空 sections、不允许的主动内容、外部图片、公式结构错误均有检查 |
| 正常公式 | 合成页预期 4 个、实际渲染 4 个、错误 0、空公式 0 |
| 视口 | 1440、1024、390 像素：无页面横向溢出、无导航遮挡；桌面和手机截图已目视检查 |
| 离线 | 全新断网浏览器上下文中正文与内联图像可读，LaTeX 源码保留，未依赖浏览器缓存 |
| 反向浏览器测试 | 不完整 frac 公式产生错误并退出 2；缺失 Chromium 保存失败报告并退出 2 |
| 最终发布 | QA 通过且 HTML SHA256 相同可 finalize；修改 HTML 或失败报告被拒绝 |
| 真实论文 | arXiv 1706.03762，15 页，44,609 文本字符；Figure 1 局部裁剪及 Equation 1 原页核对 |
| 真实论文浏览器 | 预期/实际公式 1/1；错误 0；三种视口与断网检查通过，finalize 成功 |
| wheel 分发 | 实际构建 wheel，装进第二个全新虚拟环境；从非源码目录完整运行，确认导入来自 site-packages |
| Skill 安装 | 完整复制 agents/references；重复安装明确拒绝且保留已有目录 |
| Skill 格式 | Skill Creator quick_validate 通过 |
| 发布检查 | Python 语法、JSON、Markdown 相对链接、代码无注释/文档字符串、模板/配置无注释通过 |

## 测试依赖版本

PyMuPDF 1.28.2、BeautifulSoup 4.15.0、Jinja2 3.1.6、jsonschema 4.26.0、Playwright 1.63.0、pytest 9.1.1。代码已使用 `pymupdf` 导入方式，避免旧 `fitz` 导入的弃用警告。

## 可复现命令

```bash
python -m pytest -q
python scripts/smoke.py --out work/smoke --browser
python scripts/release.py
```

单元测试和合成 smoke 不需要真实论文。浏览器步骤需要已安装 Chromium、联网访问 MathJax CDN；反向测试预期退出 2，脚本会确认这是预期错误。

## 未覆盖与边界

- GitHub Actions 已配置 Windows/Linux、Python 3.10/3.12，以及 Linux 浏览器任务；远程 CI 要在上传后实际运行，本次本地没有 Linux/macOS 系统测试。
- 真实论文测试验证下载、正文、裁剪、公式和页面生成，未制作其完整 13 节精读文章，也未评估其他智能体的学术判断质量。
- 图表/公式定位是启发式候选；复杂版式、扫描件、加密 PDF 和特定数学宏需要另行处理。不能用本次通过替代每篇论文的核验。
- 离线测试通过的是正文、图片和 LaTeX 源码可读；默认 MathJax 排版仍依赖 CDN。
- 未将论文 PDF、裁剪或任何机器特定路径放入源码发布包；真实与合成测试产物保留在本地被忽略的 work 目录。
