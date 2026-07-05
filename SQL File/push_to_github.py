"""
push_to_github.py

Simple helper to add, commit, and push files to a GitHub repo
using your local git configuration and credentials.

IMPORTANT:
- This script assumes you already have:
    1. A local git repo initialized (or cloned) on your machine
    2. A remote named 'origin' pointing to your GitHub repo
    3. Git credentials already configured (SSH key or a
       credential helper for HTTPS + PAT)
- This script does NOT store, request, or transmit any
  passwords/tokens. It simply calls your local `git` CLI,
  which handles authentication using whatever you've already
  set up on your machine.

Usage:
    python push_to_github.py "your commit message"

Optional:
    python push_to_github.py "your commit message" --branch main
"""

import subprocess
import sys
import argparse


def run(cmd):
    """Run a shell command, print output, and stop on failure."""
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr.strip())
        sys.exit(f"Command failed: {' '.join(cmd)}")
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Add, commit, and push to GitHub.")
    parser.add_argument("message", help="Commit message")
    parser.add_argument("--branch", default=None, help="Branch to push to (default: current branch)")
    args = parser.parse_args()

    # Confirm we're inside a git repo
    run(["git", "rev-parse", "--is-inside-work-tree"])

    # Stage all changes
    run(["git", "add", "."])

    # Show what will be committed
    status = run(["git", "status", "--short"])
    if not status:
        print("\nNothing to commit — working tree is clean.")
        return

    # Commit
    run(["git", "commit", "-m", args.message])

    # Determine branch
    branch = args.branch or run(["git", "rev-parse", "--abbrev-ref", "HEAD"])

    # Push
    run(["git", "push", "origin", branch])

    print(f"\n✅ Pushed to origin/{branch} successfully.")


if __name__ == "__main__":
    main()
