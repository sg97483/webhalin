import re
import json
import shutil
import sys

filename = 'NiceNew.py'
filepath = f'C:/AndroidWork/WEBHALIN3/agency/{filename}'
shutil.copy(filepath, f'{filepath}.bak')

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# find first 'if park_id == '
match = re.search(r'\n\s*if park_id == \d+:', content)
if not match:
    print('Could not find start of if block')
    sys.exit(1)

start_idx = match.start()
block = content[start_idx:]

# find end of block (the end of the web_har_in function or a specific else)
last_else = block.rfind('else:\n            print(f"지원하지 않는 주차장 ID: {park_id}")')
if last_else == -1:
    last_else = block.rfind('return False\n')

block = block[:last_else]
park_blocks = re.split(r'\n\s*(?:elif|if) park_id == ', '\n' + block)

mappings = {}
for p_block in park_blocks:
    if not p_block.strip(): continue
    m_park = re.match(r'^(\d+):', p_block)
    if not m_park: continue
    park_id = int(m_park.group(1))
    
    mappings[park_id] = {}
    
    ticket_blocks = re.finditer(r'(?:if|elif)\s+ticket_name\s+(==|in)\s+(.*?):\s*return\s+select_discount_and_confirm\(\s*driver,\s*[\'"](.*?)[\'"]\s*\)', p_block, re.DOTALL)
    
    for tb in ticket_blocks:
        op = tb.group(1)
        names_str = tb.group(2).strip()
        xpath = tb.group(3).strip()
        
        if op == '==':
            name = names_str.strip('\"\'')
            mappings[park_id][name] = xpath
        elif op == 'in':
            names_list = eval(names_str)
            for name in names_list:
                mappings[park_id][name] = xpath

print(f'Extracted {len(mappings)} park mappings from NiceNew.py')
with open('C:/AndroidWork/WEBHALIN3/agency/nicenew_mappings.py', 'w', encoding='utf-8') as f:
    f.write('# -*- coding: utf-8 -*-\n')
    f.write('NICE_NEW_MAPPINGS = \\\n')
    json.dump(mappings, f, ensure_ascii=False, indent=4)
    f.write('\n')

