import re
filepath = 'C:/AndroidWork/WEBHALIN3/agency/NiceNew.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add import
if 'from nicenew_mappings import NICE_NEW_MAPPINGS' not in content:
    content = content.replace('import pymysql\n', 'import pymysql\nfrom nicenew_mappings import NICE_NEW_MAPPINGS\n')

# Find start and end
match = re.search(r'\n\s*if park_id == \d+:', content)
start_idx = match.start()

# find the last return False of web_har_in
idx4 = content.rfind('return False', start_idx)
# Let's find exactly the else block at the end of web_har_in
idx_end = content.find('def ', start_idx)
if idx_end == -1: idx_end = len(content)
block = content[start_idx:idx_end]
# The end of the if-elif chain is likely near the end of the block.
# I'll just replace everything from start_idx to the end of the function.

new_logic = '''
        park_str = str(park_id)
        if park_str in NICE_NEW_MAPPINGS:
            mapping = NICE_NEW_MAPPINGS[park_str]
            if ticket_name in mapping:
                return select_discount_and_confirm(
                    driver,
                    mapping[ticket_name]
                )
            else:
                return handle_invalid_ticket(driver)
        else:
            print(f"지원하지 않는 주차장 ID: {park_id}")
            return handle_invalid_ticket(driver)

    return False
'''

# Wait, NiceNew.py might have an outer exception block or something at the end of web_har_in?
# Let's verify by just printing the end of the file.
