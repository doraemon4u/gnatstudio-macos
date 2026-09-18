#!/usr/bin/env python3
"""Patch GtkAda canvas_view.ads for GNAT 16.1 anonymous access limitation.

GNAT 16.1.0 does not support implicit or explicit conversion of anonymous
access parameters to named access types (an Ada 2022 feature requiring
GNAT >= 26). This script uses Unchecked_Conversion via System.Address
to bypass the limitation.
"""
import sys
import re


def patch(path):
    with open(path) as f:
        content = f.read()

    if 'To_Abstract_Item_Ptr' in content:
        print(f'Already patched: {path}')
        return

    # Add with System; before the first "with" or "private with" line
    if 'with System;' not in content:
        first_with = re.search(r'^(with |private with )', content, re.MULTILINE)
        if first_with:
            pos = first_with.start()
            content = content[:pos] + 'with System;\n' + content[pos:]
        else:
            print('WARNING: no with clause found, cannot inject with System;', file=sys.stderr)

    # Add with Ada.Unchecked_Conversion; before the first "with" or "private with" line
    if 'with Ada.Unchecked_Conversion;' not in content:
        first_with = re.search(r'^(with |private with )', content, re.MULTILINE)
        if first_with:
            pos = first_with.start()
            content = content[:pos] + 'with Ada.Unchecked_Conversion;\n' + content[pos:]
        else:
            print('WARNING: no with clause found, cannot inject with Ada.Unchecked_Conversion;', file=sys.stderr)

    # Add conversion function after the package declaration
    marker = 'package Gtkada.Canvas_View is\n'
    idx = content.find(marker)
    if idx < 0:
        print(f'ERROR: could not find package declaration in {path}', file=sys.stderr)
        sys.exit(1)

    conv_func = (
        '\n'
        '   function To_Abstract_Item_Ptr is new Ada.Unchecked_Conversion(\n'
        '      Source => System.Address,\n'
        '      Target => Abstract_Item);\n'
        '\n'
    )
    content = content[:idx + len(marker)] + conv_func + content[idx + len(marker):]

    # Replace the two expression functions
    old1 = '      return Abstract_Item is (Self);'
    new1 = "      return To_Abstract_Item_Ptr (Self'Address);"
    content = content.replace(old1, new1)

    with open(path, 'w') as f:
        f.write(content)
    print(f'Patched {path}')


if __name__ == '__main__':
    patch(sys.argv[1])
