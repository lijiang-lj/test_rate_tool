#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_mcp.py
A minimal, dependency-free scaffold to verify repo context and provide a placeholder
for future MCP-related tests.
"""

import os
import sys
import subprocess
from pathlib import Path


def run(cmd: str) -> str:
    """
    Run a shell command and return its stdout (utf-8). On failure, return the error text.
    """
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return out.decode("utf-8", errors="ignore").strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.output.decode('utf-8', errors='ignore').strip()}"


def git_info() -> dict:
    """
    Collect basic git repository information.
    """
    info = {}
    info["top_level"] = run("git rev-parse --show-toplevel")
    info["branch"] = run("git branch --show-current")
    info["origin"] = run("git remote get-url origin")
    info["head_sha"] = run("git rev-parse HEAD")
    return info


def check_mcp_setup() -> tuple[bool, str]:
    """
    Check if scripts/setup_github_mcp.ps1 exists in the repo.
    """
    top = run("git rev-parse --show-toplevel")
    repo_root = Path(top) if top and not top.startswith("ERROR") else Path(os.getcwd())
    ps1 = repo_root / "scripts" / "setup_github_mcp.ps1"
    return ps1.exists(), str(ps1)


def placeholder_mcp_probe() -> None:
    """
    Placeholder for future MCP probing logic.
    Implement actual MCP server checks or client interactions here.
    """
    print("[MCP] Placeholder probe: no MCP logic implemented yet.")


def main() -> None:
    print("== MCP Test Scaffold ==")
    print(f"Python: {sys.version.split()[0]}")
    print(f"CWD: {os.getcwd()}")

    print("\n-- Git Info --")
    info = git_info()
    for k, v in info.items():
        print(f"{k}: {v}")

    print("\n-- MCP Setup Check --")
    exists, path = check_mcp_setup()
    print(f"scripts/setup_github_mcp.ps1 exists: {exists} ({path})")

    print("\n-- MCP Probe --")
    placeholder_mcp_probe()

    print("\nDone.")


if __name__ == "__main__":
    main()
