import re

with open('C://__TESTAUTOMATION//SCRIPTS//PYTHON//myapps_github_cline//www_centrumzdravenia_sk_chatbot//chatbot.html', 'r', encoding='utf-8') as f:
    content = f.read()

print('File size:', len(content))

# Find lines containing "border"
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'border' in line.lower() and 'base64' not in line:
        print(f'Line {i+1}: {line.strip()[:120]}')
