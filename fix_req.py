with open('requirements.txt', 'r', encoding='utf-8-sig') as f:
    text = f.read()

# Replace any stray null bytes from previous bad encoding conversions
text = text.replace('\x00', '')

with open('requirements.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
