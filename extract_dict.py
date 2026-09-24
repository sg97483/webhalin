with open('C:/AndroidWork/WEBHALIN3/agency/HighCity.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(400, 420):
    print(lines[i].rstrip())

for i in range(1200, 1220):
    try:
        print(lines[i].rstrip())
    except:
        pass
