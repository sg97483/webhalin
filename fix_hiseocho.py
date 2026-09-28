filepath = 'C:/AndroidWork/WEBHALIN3/agency/HiSeoCho.py'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if '        elif park_id == 19456:' in line:
        start_idx = i
    if start_idx != -1 and '        print(f"DEBUG: ' in line and 'target_btn_text' in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_block = [
        '        elif park_id == 19456:\n',
        '            if ticket_name == "평일 당일권":\n',
        '                target_btn_text = "당일권"\n',
        '            else:\n',
        '                target_btn_text = ticket_name\n',
        '        elif park_id == 19273:\n',
        '            if "당일권" in ticket_name:\n',
        '                target_btn_text = "전일권"\n',
        '            elif "심야권" in ticket_name:\n',
        '                target_btn_text = "야간 12시간권"\n',
        '            else:\n',
        '                target_btn_text = ticket_name\n',
        '        else:\n',
        '            target_btn_text = ticket_name\n',
        '\n'
    ]
    lines = lines[:start_idx] + new_block + lines[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Fixed formatting!")
