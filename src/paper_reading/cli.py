import argparse
import json
import sys
import importlib.metadata
from pathlib import Path
from .core import fetch, inspect_pdf, render, build, check_html, finalize, init_workspace, check_state


def main():
    parser = argparse.ArgumentParser(description="PDF 精读与离线 HTML 工具")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor")
    workspace = commands.add_parser("workspace")
    workspace.add_argument("source")
    workspace.add_argument("--out", required=True)
    state = commands.add_parser("state-check")
    state.add_argument("source")
    for name in ("fetch", "inspect", "render-page", "crop", "build", "check", "browser-check", "finalize"):
        cmd = commands.add_parser(name)
        cmd.add_argument("source")
        if name != "check":
            cmd.add_argument("--out", required=True)
        if name in ("crop", "render-page"):
            cmd.add_argument("--page", required=True, type=int)
            cmd.add_argument("--dpi", default=160, type=int)
        if name == "crop":
            cmd.add_argument("--box", required=True, nargs=4, type=float)
        if name == "finalize":
            cmd.add_argument("--qa", required=True)
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            versions = {"python": sys.version.split()[0]}
            for name in ("paper-reading-kit", "PyMuPDF", "beautifulsoup4", "Jinja2", "jsonschema", "playwright"):
                try:
                    versions[name] = importlib.metadata.version(name)
                except importlib.metadata.PackageNotFoundError:
                    versions[name] = "not installed"
            try:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    versions["chromium_installed"] = Path(p.chromium.executable_path).is_file()
            except ImportError:
                versions["chromium_installed"] = False
            print(json.dumps(versions, ensure_ascii=False, indent=2))
            return 0 if versions["chromium_installed"] else 2
        elif args.command == "fetch":
            fetch(args.source, args.out)
        elif args.command == "workspace":
            init_workspace(args.source, args.out)
        elif args.command == "state-check":
            result = check_state(args.source)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["passed"] else 2
        elif args.command == "inspect":
            inspect_pdf(args.source, args.out)
        elif args.command in ("crop", "render-page"):
            render(args.source, args.page, args.out, getattr(args, "box", None), args.dpi)
        elif args.command == "build":
            build(args.source, args.out)
        elif args.command == "finalize":
            finalize(args.source, args.qa, args.out)
        elif args.command == "check":
            errors = check_html(Path(args.source).read_text(encoding="utf-8"))
            print(json.dumps({"errors": errors, "scope": "static only"}, ensure_ascii=False))
            return 2 if errors else 0
        else:
            from .qa import browser_check
            return 0 if browser_check(args.source, args.out)["passed"] else 2
    except Exception as exc:
        parser.exit(2, f"失败: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
