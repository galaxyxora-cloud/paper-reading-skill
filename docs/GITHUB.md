# 上传 GitHub

先解压发布包，进入包含 `pyproject.toml`、`README.md`、`skills`、`src` 的 `paper-reading-skill` 目录。不要把 ZIP 文件本身当作源代码上传。建议上传源码目录；其中 `.gitignore` 会排除虚拟环境、缓存、测试论文和生成物。

## 1. 准备工具和空仓库

安装 Git 并登录 GitHub。打开 GitHub 的 New repository 页面，仓库名可用 `paper-reading-skill`，选择 Public 或 Private。不要勾选自动添加 README、LICENSE 或 .gitignore，因为本地已提供。点击 Create repository 后复制 HTTPS 仓库地址。

## 2. 本地首次提交

在仓库目录打开终端。以下命令适用于新解压的目录；如果目录已有 `.git`，先检查现有远程和历史，不重新初始化到其他项目。

```bash
git init -b main
git add .
git status --short
git commit -m "Add paper reading skill and validated toolkit"
```

提交前查看 status：应包含源码、skills、docs、tests、scripts 和配置；不应包含 `.venv`、`.test-deps`、`work`、PDF 或浏览器缓存。若 Git 提示缺少身份，仅对当前仓库设置：

```bash
git config user.name "你的名字"
git config user.email "你的 GitHub 提交邮箱"
git commit -m "Add paper reading skill and validated toolkit"
```

## 3. 连接并推送

将下面的地址替换为第一步复制的真实地址，再执行：

```bash
git remote add origin https://github.com/你的用户名/paper-reading-skill.git
git remote -v
git push -u origin main
```

认证时使用 Git Credential Manager 的浏览器登录，或已配置的 SSH/个人访问令牌；不要将令牌写进文件或远程 URL。GitHub HTTPS 推送不使用账户密码。若已有 origin，先看 `git remote -v`，确认是否就是目标仓库；不要盲目重复添加或强推。

如果远程已经有 README 等提交，优先新建一个不初始化的空仓库，或者先克隆已有仓库再复制本项目文件并正常提交。不要用 force push 覆盖不熟悉的历史。

## 4. 上传后验证

刷新仓库页面，确认顶层直接显示 README、pyproject.toml、skills、src。进入 Actions → tests：等待 Windows/Linux 的单元与 CLI 测试、Linux 浏览器测试通过。浏览器测试会访问 MathJax CDN，网络失败时检查日志再重跑；不能把这种失败标成通过。

浏览器作业会上传 `browser-validation` artifact，其中有 HTML、截图和 JSON。下载并查看截图。远程 CI 的通过状态需要实际上传运行后确认，本地测试不能替代它。

## 5. 别人如何安装

```bash
git clone https://github.com/你的用户名/paper-reading-skill.git
cd paper-reading-skill
python -m venv .venv
```

然后按 [README](../README.md) 选择 Windows 或 macOS/Linux 安装步骤，再将 Skill 安装进自己的智能体目录。可选地在 GitHub 创建版本标签与 Release，并上传由 `python scripts/release.py` 生成的源码 ZIP，方便不使用 Git 的用户下载。

后续更新：

```bash
git add .
git commit -m "Improve paper reading workflow"
git push
```

流程依据：[GitHub 官方上传本地代码指南](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)。
