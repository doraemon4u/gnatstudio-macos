#!/usr/bin/env python3
"""Patch GtkAda canvas_view.ads for GNAT 16.1 anonymous access limitation.

GNAT 16.1.0 does not support implicit or explicit conversion of anonymous
access parameters to named access types (an Ada 2022 feature requiring
GNAT >= 26). This script converts the two expression functions that return
`Abstract_Item is (Self)` into regular function bodies that use
Unchecked_Conversion via System.Address to bypass the limitation.

The original expression functions:
   return Abstract_Item is (Self);

Are converted to regular function bodies:
   return Abstract_Item is
   begin
      return To_Abstract_Item_Ptr (Self'Address);
   end;

In a regular function body, `return To_abstract_Item_Ptr(Self'Address)` is
unambiguously parsed as a function call (not a type conversion), avoiding
the GNAT 16 parser ambiguity that occurs in expression function context.
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
            print('WARNING: no with clause found, cannot inject with System;',
                  file=sys.stderr)

    # Add with Ada.Unchecked_Conversion; before the first "with" or "private with" line
    if 'with Ada.Unchecked_Conversion;' not in content:
        first_with = re.search(r'^(with |private with )', content, re.MULTILINE)
        if first_with:
            pos = first_with.start()
            content = content[:pos] + 'with Ada.Unchecked_Conversion;\n' + content[pos:]
        else:
            print('WARNING: no with clause found, cannot inject with Ada.Unchecked_Conversion;',
                  file=sys.stderr)

    # Add conversion function after Abstract_Item type declaration
    marker = "type Abstract_Item is access all Abstract_Item_Record'Class;\n"
    idx = content.find(marker)
    if idx < 0:
        print(f'ERROR: could not find Abstract_Item type in {path}',
              file=sys.stderr)
        sys.exit(1)

    conv_func = (
        '\n'
        '   function To_Abstract_Item_Ptr is new Ada.Unchecked_Conversion(\n'
        '      Source => System.Address,\n'
        '      Target => Abstract_Item);\n'
    )
    content = content[:idx + len(marker)] + conv_func + content[idx + len(marker):]

    # Replace expression function `return Abstract_Item is (Self);`
    # with a regular function body that uses Unchecked_Conversion.
    #
    # The original is an expression function:
    #   function Inner_Most_Item (...) return Abstract_Item is (Self);
    # where `return Abstract_Item is` is the function spec and `(Self)` is
    # the expression body.
    #
    # We convert it to a regular function body:
    #   function Inner_Most_Item (...) return Abstract_Item is
    #   begin
    #      return To_Abstract_Item_Ptr (Self'Address);
    #   end;
    old_pattern = '      return Abstract_Item is (Self);'
    new_body = (
        '      return Abstract_Item is\n'
        '   begin\n'
        '      return To_Abstract_Item_Ptr (Self\'Address);\n'
        '   end;'
    )
    count = content.count(old_pattern)
    if count == 0:
        print(f'WARNING: pattern "return Abstract_Item is (Self);" not found in {path}',
              file=sys.stderr)
    else:
        content = content.replace(old_pattern, new_body)
        print(f'Replaced {count} expression function(s) with Unchecked_Conversion bodies')

    with open(path, 'w') as f:
        f.write(content)
    print(f'Patched {path}')


if __name__ == '__main__':
    patch(sys.argv[1])
