#!/usr/bin/env python3
"""Inject -gnatX into Ada Switches clauses in a GPR project file.

Handles both single-line and multi-line 'for Switches ("Ada") use' constructs.
"""
import re
import sys

def patch(path):
    with open(path) as f:
        lines = f.readlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Multi-line: 'for [Default_]Switches ("Ada") use' alone on line
        if re.search(r'for\s+(Default_)?Switches\s+\("Ada"\)\s+use\s*$', line.rstrip()):
            out.append(line)
            i += 1
            if i < len(lines):
                nxt = lines[i]
                nxt = re.sub(r'^(\s*)\(', r'\1("-gnatX", ', nxt, count=1)
                out.append(nxt)
        # Single-line: 'for [Default_]Switches ("Ada") use (...)' on one line
        elif re.search(r'for\s+(Default_)?Switches\s+\("Ada"\)\s+use\s+\(', line):
            line = re.sub(r'(use\s+)\(', r'\1("-gnatX", ', line, count=1)
            out.append(line)
        else:
            out.append(line)
        i += 1
    with open(path, 'w') as f:
        f.writelines(out)
    print('Patched', path)

if __name__ == '__main__':
    patch(sys.argv[1])
