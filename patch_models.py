import re

with open('app/models.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_historico_mode = False
for i, line in enumerate(lines):
    if line.startswith('class Historico'):
        in_historico_mode = True
    elif line.startswith('class '):
        in_historico_mode = False
        
    if in_historico_mode:
        # replace db.String(...) with db.Text
        lines[i] = re.sub(r'db\.String\(\d+\)', 'db.Text', line)

with open('app/models.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Updated models.py: db.String(...) inside Historico* classes has been changed to db.Text")
