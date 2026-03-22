#!/usr/bin/env python3
import os

path = r'c:\Users\Jules\Desktop\GPS0\minijeux\niveau5.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Unique anchor: last line of the STOP label branch (no emoji in this line)
# This appears only in _drawPhaseLabel, not in old code
anchor = "    ctx.fillText('STOP !', W / 2, H - 14); ctx.restore();\n  } else {"
pos = content.find(anchor)
if pos == -1:
    print("ERROR: STOP anchor not found in file")
else:
    # Also find the closing } of _drawPhaseLabel (after the else block)
    # After anchor: find the next "}\n}" that closes the function
    rest = content[pos:]
    end_marker = "  }\n}"
    end_pos = rest.find(end_marker)
    if end_pos == -1:
        print("ERROR: closing } not found")
    else:
        cut = pos + end_pos + len(end_marker)
        new_content = content[:cut] + "\n</script>\n</body>\n</html>"
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        lines_count = new_content.count('\n') + 1
        print(f"SUCCESS: file is now {lines_count} lines, {len(new_content)} chars")
        # verify end
        print("Last 100 chars:", repr(new_content[-100:]))

