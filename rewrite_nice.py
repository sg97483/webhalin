import re
filepath = 'C:/AndroidWork/WEBHALIN3/agency/NiceNew.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

if 'from nicenew_mappings import NICE_NEW_MAPPINGS' not in content:
    # Let's insert after 'import WebInfo' or somewhere safe
    content = content.replace('import WebInfo', 'import WebInfo\nfrom nicenew_mappings import NICE_NEW_MAPPINGS')

match = re.search(r'        # park_id. ticket_name.\s*if park_id == \d+:', content)
if not match:
    match = re.search(r'\s*if park_id == \d+:\s*(?:if|elif) ticket_name', content)

if not match:
    print('Could not find start index')
    exit(1)

start_idx = match.start()

# find end index
end_str = '    return False\n'
idx_end = content.find(end_str, start_idx) + len(end_str)

new_logic = '''        park_str = str(park_id)
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
            try:
                driver.implicitly_wait(3)
                try:
                    driver.find_element("xpath", side_nav_xpath).click()
                except:
                    driver.find_element_by_xpath(side_nav_xpath).click()
                print(Colors.BLUE + "지원하지 않는 주차장 ID: " + str(park_id) + Colors.ENDC)
                return False
            except Exception as ex:
                print(f"Error during process: {ex}")
                return False

    return False
'''

content = content[:start_idx] + new_logic + content[idx_end:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Optimized NiceNew.py')
