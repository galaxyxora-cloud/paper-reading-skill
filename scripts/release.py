import ast
import io
import json
import re
import tokenize
import zipfile
from pathlib import Path


def collect(root):
    folders = ("src", "skills", "examples", "tests", "scripts", "docs", ".github")
    files = [p for folder in folders for p in (root / folder).rglob("*")
             if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
             and not any(part.endswith(".egg-info") for part in p.parts)]
    files += [root / name for name in ("pyproject.toml", ".gitignore", "README.md", "LICENSE", "VALIDATION.md")]
    return sorted(files)


def validate(files):
    for path in files:
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            tree = ast.parse(text)
            if any(t.type == tokenize.COMMENT for t in tokenize.generate_tokens(io.StringIO(text).readline)):
                raise ValueError("代码含注释: " + str(path))
            if any(ast.get_docstring(n) for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))):
                raise ValueError("代码含文档字符串: " + str(path))
        if path.suffix == ".html" and re.search(r"<!--|/\*|\{#", text):
            raise ValueError("模板含注释: " + str(path))
        if path.suffix in (".toml", ".yml", ".yaml") and re.search(r"(?m)^\s*#", text):
            raise ValueError("配置含注释: " + str(path))
        if path.suffix == ".json":
            json.loads(text)
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" not in target and not target.startswith("#"):
                    if not (path.parent / target.split("#")[0]).exists():
                        raise ValueError("文档引用不存在: " + str(path) + " -> " + target)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    files = collect(root)
    validate(files)
    output = root / "dist/paper-reading-skill-source.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, "paper-reading-skill/" + path.relative_to(root).as_posix())
    print(f"Validated and packaged {len(files)} files: {output}")
