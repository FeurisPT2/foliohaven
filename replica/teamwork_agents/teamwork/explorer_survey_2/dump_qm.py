import struct, io
from collections import defaultdict

with open(r'C:\Program Files (x86)\Icecream Ebook Reader\translations\ebookreader_en.qm', 'rb') as f:
    buf = f.read()

bio = io.BytesIO(buf)
magic = bio.read(16)

sections = {}
while bio.tell() < len(buf):
    tag = bio.read(1)
    if not tag:
        break
    tag = tag[0]
    length = int.from_bytes(bio.read(4), 'big')
    offset = bio.tell()
    sections[tag] = (offset, length)
    bio.seek(offset + length)

msg_off, msg_len = sections[105]
data = buf[msg_off:msg_off+msg_len]

ptr = 0
items = []
curr = {}
while ptr < len(data):
    tag = data[ptr]
    ptr += 1
    if tag == 1:
        if curr:
            items.append(curr)
            curr = {}
    elif tag in (2, 3, 4, 6, 7, 8):
        tlen = int.from_bytes(data[ptr:ptr+4], 'big')
        ptr += 4
        if tlen == 0xffffffff:
            val = ''
        else:
            raw = data[ptr:ptr+tlen]
            ptr += tlen
            if tag in (2, 3, 4):
                val = raw.decode('utf-16be', 'ignore')
            else:
                val = raw.decode('utf-8', 'ignore')
        
        name = {2: 'source16', 3: 'trans', 4: 'context16', 6: 'source', 7: 'context', 8: 'comment'}[tag]
        curr[name] = val
    else:
        break

if curr:
    items.append(curr)

by_ctx = defaultdict(list)
for it in items:
    ctx = it.get('context', it.get('context16', 'NO_CTX'))
    by_ctx[ctx].append(it)

output_lines = []
output_lines.append(f"TOTAL PARSED STRINGS: {len(items)}")
output_lines.append(f"TOTAL CONTEXTS: {len(by_ctx)}\n")

for ctx in sorted(by_ctx.keys()):
    output_lines.append(f"==================================================")
    output_lines.append(f"CONTEXT: {ctx} ({len(by_ctx[ctx])} strings)")
    output_lines.append(f"==================================================")
    for it in by_ctx[ctx]:
        src = it.get('source', it.get('source16', ''))
        tr = it.get('trans', '')
        comment = it.get('comment', '')
        if comment:
            output_lines.append(f"  [{comment}]")
        output_lines.append(f"  SOURCE:      {src}")
        output_lines.append(f"  TRANSLATION: {tr}")
        output_lines.append(f"  ---")
    output_lines.append("")

out_path = r'c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\explorer_survey_2\extracted_strings.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    out.write('\n'.join(output_lines))

print(f"Successfully exported {len(items)} strings to {out_path}")
