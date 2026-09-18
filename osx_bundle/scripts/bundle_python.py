#!/usr/bin/env python3
"""Copy the active Homebrew Python runtime into a GNAT Studio bundle."""

from __future__ import annotations

import shutil
import site
import sys
import sysconfig
from pathlib import Path


def copytree(src: Path, dst: Path) -> None:
    if not src.exists():
        raise RuntimeError(f"Python runtime path does not exist: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, symlinks=False, dirs_exist_ok=True)


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} <bundle-lib-dir> <python-executable>")

    bundle_lib = Path(sys.argv[1]).resolve()
    python_exe = Path(sys.argv[2])

    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    py_lib = bundle_lib / f"python{version}"
    py_lib.mkdir(parents=True, exist_ok=True)

    paths = sysconfig.get_paths(vars={"base": sys.prefix, "platbase": sys.exec_prefix})
    stdlib = Path(paths["stdlib"])
    platstdlib = Path(paths.get("platstdlib", paths["stdlib"]))

    # Copy the standard library and the platform lib-dynload directory.
    copytree(stdlib, py_lib)
    if platstdlib != stdlib and platstdlib.exists():
        copytree(platstdlib, py_lib)

    # PyGObject / Pycairo are installed as normal Python site packages by
    # Homebrew. Copy both pure-Python and platform-specific package trees.
    purelib = Path(sysconfig.get_path("purelib"))
    platlib = Path(sysconfig.get_path("platlib"))
    site_dst = py_lib / "site-packages"
    copytree(purelib, site_dst)
    if platlib != purelib and platlib.exists():
        copytree(platlib, site_dst)

    # Avoid importing Homebrew's external-prefix customization in the bundle.
    for pth in site_dst.glob("*.pth"):
        pth.unlink()
    sitecustomize = py_lib / "sitecustomize.py"
    if sitecustomize.exists():
        sitecustomize.unlink()

    # GNAT Studio's source tree convention expects a Python home at
    # share/gnatstudio/python. Point that location at lib/pythonX.Y.
    gpy = bundle_lib.parent / "share" / "gnatstudio" / "python"
    gpy_lib = gpy / "lib"
    gpy_lib.mkdir(parents=True, exist_ok=True)
    link = gpy_lib / f"python{version}"
    if link.exists() or link.is_symlink():
        if link.is_dir() and not link.is_symlink():
            shutil.rmtree(link)
        else:
            link.unlink()
    link.symlink_to(Path("../../../../lib") / f"python{version}")

    # Keep the executable reference visible for diagnostics without creating
    # a symlink into Homebrew's prefix.
    print(f"Python executable: {python_exe.resolve()}")
    print(f"Python version:    {sys.version.split()[0]}")
    print(f"stdlib:            {stdlib}")
    print(f"site-packages:     {purelib}")
    print(f"bundle runtime:    {py_lib}")
    print(f"python home link:  {gpy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
