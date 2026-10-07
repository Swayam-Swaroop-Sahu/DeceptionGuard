#!/usr/bin/env python3
"""Pre-push gate script for DeceptionGuard.

Runs on `git push`. Validates:
1. Tests pass.
2. Ruff / Lints pass.
3. No secrets in the repo.
4. No data leakage (large files, real emails).
5. README and CHANGELOG were modified.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

SECRET_PATTERNS = [
    r"nvapi-[a-zA-Z0-9\-_]{30,}",  # NVIDIA API key
    r"sk-[a-zA-Z0-9]{20,}",        # OpenAI API key format
    r"Bearer\s+[a-zA-Z0-9\-\._~+/]+=", # Bearer tokens
    r"-----BEGIN PRIVATE KEY-----", # Private keys
]

def run_tests():
    print("Running tests...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
    if result.returncode != 0:
        print("[FAIL] Tests failed!")
        return False
    print("[OK] Tests passed.")
    return True

def run_linter():
    print("Running linter (ruff)...")
    try:
        result = subprocess.run([sys.executable, "-m", "ruff", "check", "src/"], capture_output=True, text=True)
        if result.returncode != 0:
            print("[FAIL] Linter failed!")
            print(result.stdout)
            print(result.stderr)
            return False
        print("[OK] Linter passed.")
        return True
    except FileNotFoundError:
        print("[WARN] Ruff not found, skipping linter check.")
        return True

def check_secrets():
    print("Checking for secrets...")
    # Check .env is not tracked
    result = subprocess.run(["git", "ls-files", ".env"], capture_output=True, text=True)
    if result.stdout.strip():
        print("[FAIL] .env file is tracked in git!")
        return False

    # Check for secret patterns in all tracked files
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    tracked_files = result.stdout.splitlines()

    for file_path in tracked_files:
        if file_path.endswith("pre_push_check.py"):
            continue
        path = Path(file_path)
        if not path.is_file():
            continue
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
                for pattern in SECRET_PATTERNS:
                    if re.search(pattern, content):
                        print(f"[FAIL] Possible secret found in {file_path}")
                        return False
        except UnicodeDecodeError:
            pass # Skip binary files

    print("[OK] No secrets found.")
    return True

def check_data_leakage():
    print("Checking for data leakage...")
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    tracked_files = result.stdout.splitlines()

    for file_path in tracked_files:
        path = Path(file_path)
        if not path.is_file():
            continue

        # Check size
        if path.stat().st_size > MAX_FILE_SIZE_BYTES:
            print(f"[FAIL] File {file_path} is larger than {MAX_FILE_SIZE_MB}MB!")
            return False

        # Check restricted directories/extensions
        if path.suffix in [".eml", ".mbox"]:
            if "tests/fixtures" not in str(path).replace(os.sep, "/"):
                print(f"[FAIL] Real email file found outside fixtures: {file_path}")
                return False

        # Check data dirs
        if any(bad_dir in file_path for bad_dir in ["data/raw", "datasets/"]):
            print(f"[FAIL] File tracked in restricted directory: {file_path}")
            return False

    print("[OK] No data leakage found.")
    return True

def check_docs_updated():
    print("Checking if README and CHANGELOG were updated...")
    # Get current branch
    branch_cmd = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
    branch = branch_cmd.stdout.strip()

    # Get changed files against main
    # If we are on main, check last commit
    if branch == "main":
        diff_cmd = ["git", "diff", "--name-only", "HEAD~1"]
    else:
        diff_cmd = ["git", "diff", "--name-only", "main..."]

    result = subprocess.run(diff_cmd, capture_output=True, text=True)
    changed_files = result.stdout.splitlines()

    has_readme = "README.md" in changed_files
    has_changelog = "CHANGELOG.md" in changed_files

    if not has_readme:
        print("[FAIL] README.md was not modified in this phase!")
        return False
    if not has_changelog:
        print("[FAIL] CHANGELOG.md was not modified in this phase!")
        return False

    print("[OK] Documentation updated.")
    return True

def main():
    print("Starting pre-push checks...")
    checks = [
        run_tests(),
        run_linter(),
        check_secrets(),
        check_data_leakage(),
        check_docs_updated()
    ]

    if all(checks):
        print("[OK] All pre-push checks passed!")
        sys.exit(0)
    else:
        print("[FAIL] Pre-push checks failed. Fix the issues before pushing.")
        sys.exit(1)

if __name__ == "__main__":
    main()
