import argparse
import shutil
from pathlib import Path


def install(target):
    source = Path(__file__).resolve().parents[1] / "skills/paper-deep-reading"
    destination = Path(target).expanduser().resolve() / source.name
    if destination.exists():
        raise ValueError(f"目标已存在，请先备份并自行迁移旧版本: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    print(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    args = parser.parse_args()
    try:
        install(args.target)
    except Exception as exc:
        parser.exit(2, str(exc) + "\n")
