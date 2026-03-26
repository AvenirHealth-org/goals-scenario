#!/usr/bin/env python3
"""
Update PJNZ import code from Spectrum Engine.

Reads the ref from scripts/spectrum_engine_ref, shallow-clones that ref from
GitHub, and copies the configured source paths into this repository.

Authentication (required for private repos — tried in order):
  1. GITHUB_TOKEN environment variable
  2. `gh auth token` (GitHub CLI)
  3. Unauthenticated (public repos only)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import git

# ---------------------------------------------------------------------------
# File map — edit this to change what gets copied.
#
# Each entry is:
#   ("source/glob/pattern", "dest/relative/to/repo/root")
#
# Source path is relative to the root of the cloned spectrum-engine repo.
# Destination path is relative to the root of this repository.
#
# Rules:
#   - A directory path copies the entire directory tree into dest.
#   - A glob pattern (e.g. "Dir/Sub/*.py") copies all matching files flat
#     into dest (files land directly in dest, no subdirectory structure).
#   - A plain file path copies that single file into dest.
# ---------------------------------------------------------------------------
FILE_MAP: list[tuple[str, str]] = [
    ("SpectrumCommon/Const/HV", "src/goals_sa/_const/HV"),
    ("SpectrumCommon/Const/RN", "src/goals_sa/_const/RN"),
    ("Tools/ImportExportPJNZ/DP/ImportDP.py", "src/goals_sa/_import/DP"),
    ("Tools/ImportExportPJNZ/RN", "src/goals_sa/_import/RN"),
    ("Tools/ImportExportPJNZ/HV", "src/goals_sa/_import/HV"),
    ("Calc/DP/LeapfrogDataMapping.py", "src/goals_sa/_leapfrog"),
]

GITHUB_REPO = "AvenirHealth-org/SpectrumEngine"
REF_FILE = "scripts/spectrum_engine_ref"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_project_root() -> Path:
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return Path(root)
    except subprocess.CalledProcessError:
        sys.exit("Error: not inside a Git repository.")


def read_ref(proj_root: Path) -> str:
    ref_path = proj_root / REF_FILE
    if not ref_path.exists():
        sys.exit(f"Error: ref file not found: {ref_path}")
    ref = ref_path.read_text().strip()
    if not ref:
        sys.exit(f"Error: ref file is empty: {ref_path}")
    return ref


def get_github_token() -> str | None:
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    # Fall back to the GitHub CLI token if available
    if shutil.which("gh"):
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            token = result.stdout.strip()
            if token:
                return token
    print(
        "Warning: no GitHub token found. The clone will fail if the repository is private.\n"
        "To fix, authenticate via one of:\n"
        "  - GitHub CLI:   gh auth login\n"
        "  - Environment:  export GITHUB_TOKEN=<your-token>",
        file=sys.stderr,
    )
    return None


def clone_repo(repo: str, ref: str, dest: Path, token: str | None) -> None:

    clone_url = f"https://oauth2:{token}@github.com/{repo}.git" if token else f"https://github.com/{repo}.git"

    print(f"Cloning {repo} at ref '{ref}' ...")
    try:
        git.Repo.clone_from(
            clone_url,
            dest,
            branch=ref,
            depth=1,
            single_branch=True,
        )
    except git.exc.GitCommandError as exc:
        msg = str(exc)
        # Strip the token from any error message before printing
        if token:
            msg = msg.replace(token, "***")
        if "not found" in msg.lower() or "repository" in msg.lower():
            hint = (
                (
                    "\nIf the repository is private, authenticate via one of:\n"
                    "  - Install the GitHub CLI and run: gh auth login\n"
                    "  - Set the GITHUB_TOKEN environment variable"
                )
                if not token
                else ""
            )
            sys.exit(f"Error: could not clone repository.{hint}\n{msg}")
        sys.exit(f"Error cloning repository: {msg}")


def is_glob_pattern(pattern: str) -> bool:
    return any(c in pattern for c in ("*", "?", "["))


def copy_entry(src_root: Path, src_pattern: str, dest_dir: Path) -> None:
    """Copy one FILE_MAP entry from src_root into dest_dir."""
    src_path = src_root / src_pattern

    # --- plain directory --------------------------------------------------
    if not is_glob_pattern(src_pattern) and src_path.is_dir():
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        shutil.copytree(src_path, dest_dir)
        print(f"  Copied directory  {src_pattern}  ->  {dest_dir}")
        return

    # --- plain file -------------------------------------------------------
    if not is_glob_pattern(src_pattern) and src_path.is_file():
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest_dir / src_path.name)
        print(f"  Copied file       {src_pattern}  ->  {dest_dir / src_path.name}")
        return

    # --- glob pattern -----------------------------------------------------
    if is_glob_pattern(src_pattern):
        parts = Path(src_pattern).parts
        glob_start = next(
            (i for i, p in enumerate(parts) if any(c in p for c in ("*", "?", "["))),
            len(parts) - 1,
        )
        base_dir = src_root / Path(*parts[:glob_start]) if glob_start > 0 else src_root
        glob_part = str(Path(*parts[glob_start:]))

        matches = list(base_dir.glob(glob_part))
        if not matches:
            print(f"  Warning: no files matched pattern  {src_pattern}", file=sys.stderr)
            return

        dest_dir.mkdir(parents=True, exist_ok=True)
        for match in matches:
            shutil.copy2(match, dest_dir / match.name)
            print(f"  Copied  {match.relative_to(src_root)}  ->  {dest_dir / match.name}")
        return

    sys.exit(f"Error: source path not found: {src_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update import code from Spectrum Engine.",
        epilog=(
            "Authentication for private repos: install the GitHub CLI and run "
            "`gh auth login`, or set the GITHUB_TOKEN environment variable."
        ),
    )
    parser.add_argument(
        "--ref",
        help="Override the ref from spectrum_engine_ref (branch, tag, or commit SHA).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be copied without making any changes.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    proj_root = get_project_root()
    ref = args.ref or read_ref(proj_root)
    print(f"Using ref: {ref}")

    if args.dry_run:
        print("\nDry run — file map:")
        for src, dest in FILE_MAP:
            print(f"  {src}  ->  {dest}")
        return

    token = get_github_token()

    with tempfile.TemporaryDirectory() as tmpdir:
        clone_dir = Path(tmpdir) / "repo"
        clone_repo(GITHUB_REPO, ref, clone_dir, token)

        print("\nCopying files...")
        for src_pattern, dest_rel in FILE_MAP:
            copy_entry(clone_dir, src_pattern, proj_root / dest_rel)

    print("\nDone.")


if __name__ == "__main__":
    main()
