with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

keywords = ['1,338', '1,860', '339', '1,494', '255', 'Wave 4 Calibrated', '772 / 1,000', '8000', '8,000']
for kw in keywords:
    pos = 0
    while True:
        pos = text.find(kw, pos)
        if pos == -1:
            break
        snippet = text[max(0, pos-80):min(len(text), pos+120)]
        print(f'Found "{kw}" at pos {pos}:')
        print(snippet.replace('\n', ' '))
        print('-'*50)
        pos += len(kw)
