import re

with open('C:/AndroidWork/WEBHALIN3/agency/AJpark.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_19004_logic = '''    if park_id == 19004:
        target_text = None
        if "당일권" in ticket_name or "1일권" in ticket_name:
            if "휴일" in ticket_name:
                target_text = "휴일당일권(공유서비스)"
            else:
                target_text = "평일당일권(공유서비스)"
        elif "12시간권" in ticket_name:
            target_text = "평일12시간권(공유서비스)"
        elif "야간권" in ticket_name or "심야권" in ticket_name:
            target_text = "야간권(공유서비스)"
        elif "3시간권" in ticket_name:
            target_text = "3시간(공유서비스)"
        elif "2시간권" in ticket_name:
            target_text = "2시간(공유서비스)"
        elif "1시간권" in ticket_name:
            target_text = "1시간(공유서비스)"

        if not target_text:
            print(f"ERROR: 19004에서 지원하지 않는 ticket_name: {ticket_name}")
            return False'''

content = re.sub(r'    if park_id == 19004:.*?        if ticket_name not in ticket_map:.*?            return False\n\n        target_text = ticket_map\[ticket_name\]', new_19004_logic, text, flags=re.DOTALL)

with open('C:/AndroidWork/WEBHALIN3/agency/AJpark.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
