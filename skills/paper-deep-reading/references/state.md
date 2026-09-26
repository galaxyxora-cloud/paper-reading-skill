# 可恢复工作状态

不要把聊天上下文当作持久记忆。每篇论文使用独立任务目录，并把可恢复状态写入 `state.json`。首次处理时运行：

```bash
paper-read workspace <PDF 链接或本地路径> --out work/<paper-id>
paper-read state-check work/<paper-id>/state.json
```

若目录已有可信产物，不要重新初始化或覆盖；读取现有 `state.json`、核对产物后继续。恢复任务、上下文压缩后、切换智能体或准备交付前，都先运行 `state-check` 并阅读状态文件。

## 状态职责

`state.json` 只保存继续任务所需的稳定事实，不保存冗长思维过程。字段职责如下：

- `objective`：用户受众、重点与交付形式；用户改变要求时立即更新。
- `stage`：`initialized → acquired → inspected → evidence → writing → qa → finalized`；真正受阻时用 `blocked`。
- `completed` 与 `next_actions`：已完成的可验证步骤和接下来最多三项具体动作。
- `evidence`：原文证据账本。每项使用稳定 ID，记录种类、页码/章节/网址定位、核验状态、内容摘要及关联裁剪。
- `claims`：准备写入正文的主张，引用 evidence ID；证据不完整时保持 `open` 或 `partial`，不能升级为 `supported`。
- `symbols`：跨公式复用的符号、含义、形状/单位和作用域；同名异义分开记录。
- `artifacts`：PDF、解析报告、页面图、裁剪、article、草稿、QA 和最终 HTML 的相对路径、状态与可用时的 SHA256。
- `open_questions`：仍需查证的问题，不能把猜测移入结论。
- `decisions`：影响后续工作的选择及依据，例如采用哪个 PDF 版本或为何不复刻某张表。
- `last_error`：最近同类失败与次数；成功后清空。
- `handoff`：两三句话说明当前可信断点、下一动作和不能假定的事项。

## 更新纪律

完成一个产生新证据或新文件的步骤后再更新状态，使用 UTC ISO 8601 时间刷新 `updated_at`。不要预先把计划标成完成，也不要手工声称不存在的哈希或核验结果。

更换 PDF 后，将依赖旧版本的 inspection、裁剪、article、草稿和 QA 标为 `stale`，重新建立证据。修改 article 或 HTML 后同样使下游 QA/最终文件失效。产物标为 `ready` 或 `verified` 时必须确实存在；填写 SHA256 后，`state-check` 会核对文件身份。

工作笔记按“原文证据 → 可支持主张 → 文章表达”流动。不要把临时猜测、搜索片段或工具输出直接写进 article。长篇原文留在 PDF/inspection，状态文件只保留定位和摘要，避免它本身膨胀成第二篇文章。

同一错误最多重试两次。每次失败更新 `last_error` 和 `handoff`；达到停止条件后将阶段设为 `blocked`，说明恢复所需条件。最终发布前，`state-check` 必须通过，`finalized` 阶段必须登记一个状态为 `verified` 的 `final-html`，且 `next_actions` 为空。