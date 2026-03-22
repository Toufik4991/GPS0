#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix niveau2.html encoding (triple-encoded UTF-8 -> correct UTF-8)"""
import sys
import re
import io

FILEPATH = r'c:\Users\Jules\Desktop\GPS0\minijeux\niveau2.html'
OUTPATH = r'c:\Users\Jules\Desktop\GPS0\fix_n2_test.txt'

log = io.open(OUTPATH, 'w', encoding='utf-8')

with open(FILEPATH, 'rb') as f:
    raw = f.read()

log.write('raw len: ' + str(len(raw)) + '\n')
log.write('first bytes around lives span: ' + str(raw[1081:1105]) + '\n')

# Bytes are triple-encoded: original UTF-8 bytes read as latin-1, chars re-encoded as UTF-8
# Fix: read as raw bytes, decode latin-1 (treat each byte as codepoint), re-encode latin-1 (gets back original bytes), decode UTF-8
try:
    latin_str = raw.decode('latin-1')
    utf8_bytes = latin_str.encode('latin-1')
    text_once = utf8_bytes.decode('utf-8', errors='replace')
    # Try second pass
    try:
        utf8_bytes2 = text_once.encode('latin-1', errors='replace')
        text = utf8_bytes2.decode('utf-8', errors='replace')
        log.write('Double bridge OK\n')
    except Exception as e2:
        log.write('Second bridge: ' + str(e2) + '\n')
        text = text_once
    log.write('Decoded via latin-1 bridge OK\n')
    # Verify
    i = text.find('\u2764')
    log.write('hearts char U+2764 found at: ' + str(i) + '\n')
except Exception as e:
    log.write('bridge failed: ' + str(e) + '\n')
    text = raw.decode('utf-8', errors='replace')

# Fix TUTO_TEXT name
text = text.replace('Lune de Cendre', 'Lune Phobos')

# Count replacements remaining issues
bad_check = '\u00e2\u00a4'  # starts of remaining mojibake
i2 = text.find(bad_check)
log.write('bad_check pos: ' + str(i2) + '\n')

# Sample around lives
li = text.find('id="lives">')
if li < 0:
    li = text.find("id='lives'")
log.write('lives at: ' + str(li) + ' -> ' + repr(text[li:li+30] if li>=0 else 'not found') + '\n')
log.write('TUTO: ' + repr(text[text.find('TUTO_TEXT'):text.find('TUTO_TEXT')+150]) + '\n')
log.close()

# Verify
# Verify and write
log2 = io.open(OUTPATH, 'a', encoding='utf-8')
log2.write('Done script - file not yet written (debug mode)\n')
log2.close()
