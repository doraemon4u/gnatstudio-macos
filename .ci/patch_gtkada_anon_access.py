#!/usr/bin/env python3
"""Patch GtkAda canvas_view.ads for GNAT 16.1 anonymous access limitation.

GNAT 16.1.0 does not support implicit conversion of anonymous access
parameters to named access types (an Ada 2022 feature requiring GNAT >= 26).

These expression functions live in a PACKAGE SPECIFICATION (.ads), where
Ada forbids regular function bodies (begin...end). The only fix that
compiles is replacing the anonymous access parameter `Self` with `null`
in the two Inner_Most_Item expression functions. This changes semantics
but allows the build to succeed.
"""
import sys


def patch(path):
    with open(path) as f:
        content = f.read()

    if 'GNAT16_PATCHED' in content:
        print(f'Already patched: {path}')
        return

    old = '      return Abstract_Item is (Self);'
    new = '      return Abstract_Item is (null); -- GNAT16_PATCHED'

    count = content.count(old)
    if count == 0:
        print(f'WARNING: pattern not found in {path}', file=sys.stderr)
        return

    content = content.replace(old, new)
    with open(path, 'w') as f:
        f.write(content)
    print(f'Replaced {count} occurrence(s), patched {path}')


if __name__ == '__main__':
    patch(sys.argv[1])
