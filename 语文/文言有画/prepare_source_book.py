"""Render source.json books into the existing shared reader. No third-party modules."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parent
NUM = {4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九', 10: '十'}

def prepare_source_book(directory):
    directory = Path(directory)
    data = json.loads((directory / 'source.json').read_text())
    front = data.pop('frontmatter')
    data.setdefault('contextLabels', {})
    for i, scene in enumerate(data['scenes'], 1):
        scene['id'] = f'{i:02}'
    count = len(data['scenes'])
    cover = data['scenes'][int(front['cover']) - 1]
    values = {**front, **{k:data[k] for k in ['title','author','slug','volume']},
              'countCN': NUM[count], 'count': count,
              'coverAlt': cover['alt'], 'last': f'{count:02}',
              'lastAlt': data['scenes'][-1]['alt']}
    values['comparisonsHTML'] = ''.join(
        f'<div><h3>{html.escape(t)}</h3><p>{p}</p></div>' for t,p in front['comparisons'])
    template = (ROOT / 'shared' / 'source-book.template.html').read_text()
    rich = {'titleBreak','line','afterLine','comparisonsHTML'}
    def replace(m):
        key = m[1]
        value = str(values[key])
        return value if key in rich else html.escape(value, quote=True)
    rendered = re.sub(r'\{\{(\w+)\}\}', replace, template)
    assert '{{' not in rendered
    (directory / 'index.html').write_text(rendered)
    (directory / 'book-data.js').write_text('const BOOK = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n')
    (directory / 'frontmatter.json').write_text(json.dumps(front, ensure_ascii=False, indent=2) + '\n')
    return data

if __name__ == '__main__':
    for source in ROOT.glob('*/source.json'):
        book = prepare_source_book(source.parent)
        print(book['title'], len(book['scenes']))
