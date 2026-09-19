#!/usr/bin/env python3
"""Patch GtkAda GPR files for GNAT 16 compatibility.

GNAT 16.1.0 and gprbuild 26 have compatibility issues when -gnatX is
injected into GtkAda's shared GPR. The "cannot generate code for file
(package spec)" error on spec-only packages like gtkada-intl.ads is caused
by -gnatX changing how gprbuild processes library sources.

This script now does nothing (no-op) — the -gnatX injection was removed
because it causes more problems than it solves with this toolchain
combination. The canvas_view.ads anonymous access issue is handled by
patch_gtkada_anon_access.py instead.
"""
import sys


def patch(path):
    print(f'No-op: skipping GPR patch for {path} (gnatX injection removed)')


if __name__ == '__main__':
    patch(sys.argv[1])
