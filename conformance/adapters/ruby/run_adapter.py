#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def ruby_executable() -> str:
    candidates = [
        os.environ.get("MPP_RUBY"),
        os.environ.get("RUBY"),
        "/opt/homebrew/opt/ruby@3.3/bin/ruby",
        "/opt/homebrew/opt/ruby/bin/ruby",
        shutil.which("ruby"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.is_absolute() and not path.exists():
            continue
        check = subprocess.run(
            [
                candidate,
                "-e",
                'exit Gem::Version.new(RUBY_VERSION) >= Gem::Version.new("3.3") ? 0 : 1',
            ],
            capture_output=True,
            text=True,
        )
        if check.returncode == 0:
            return candidate
    return os.environ.get("MPP_RUBY") or os.environ.get("RUBY") or "ruby"


def bundle_executable(ruby: str) -> str:
    if os.environ.get("MPP_BUNDLE"):
        return os.environ["MPP_BUNDLE"]
    if os.environ.get("BUNDLE"):
        return os.environ["BUNDLE"]
    sibling = Path(ruby).with_name("bundle")
    if sibling.exists():
        return str(sibling)
    return "bundle"


def main() -> int:
    ruby = ruby_executable()
    bundle = bundle_executable(ruby)
    env = os.environ.copy()
    env.setdefault("BUNDLE_PATH", "vendor/bundle")

    if sys.argv[1:] == ["--build"]:
        return subprocess.run([bundle, "install", "--quiet"], cwd=Path(__file__).parent, env=env).returncode

    process = subprocess.run(
        [bundle, "exec", ruby, "adapter.rb", *sys.argv[1:]],
        input=sys.stdin.read(),
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
        env=env,
    )
    sys.stdout.write(process.stdout)
    sys.stderr.write(process.stderr)
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
