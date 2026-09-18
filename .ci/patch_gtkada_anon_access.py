#!/usr/bin/env python3
"""Patch GtkAda canvas_view.ads to work around GNAT 16 limitation.

GNAT 16.1.0 does not support implicit or explicit conversion of anonymous
access parameters to named access types (an Ada 2022 feature). This script
patches the two affected expression functions to use Unchecked_Conversion
via System.Address instead.
"""
import sys

def patch(path):
    with open(path) as f:
        content = f.read()

    if 'To_Abstract_Item_Ptr' in content:
        print(f'Already patched: {path}')
        return

    # Add with clauses if not present
    if 'with System;' not in content:
        content = content.replace(
            'with Ada.Unchecked_Deallocation;',
            'with System;\nwith Ada.Unchecked_Deallocation;',
            1
        )

    if 'with Ada.Unchecked_Conversion;' not in content:
        content = content.replace(
            'private with Ada.Unchecked_Deallocation;',
            'with Ada.Unchecked_Conversion;\nprivate with Ada.Unchecked_Deallocation;',
            1
        )

    # Add conversion function before the first package declaration body
    # Find the first "package Gtkada.Canvas_View is" and add after it
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
    new1 = '      return To_Abstract_Item_Ptr (Self\'Address);'
    content = content.replace(old1, new1)

    with open(path, 'w') as f:
        f.write(content)
    print(f'Patched {path}')

if __name__ == '__main__':
    patch(sys.argv[1])
