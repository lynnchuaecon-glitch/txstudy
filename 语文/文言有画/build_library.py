"""Build the offline shelf, self-contained books, and a clean reading ZIP.
Run with Python 3. The catalog is the only registry; no server is required.
"""
from pathlib import Path
from urllib.parse import quote
import base64
import json
import re
import zipfile
from prepare_source_book import prepare_source_book

ROOT = Path(__file__).resolve().parent

def data_url(path):
    return 'data:image/jpeg;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')

def build_book(book):
    directory = ROOT / book['directory']
    if (directory / 'source.json').exists():
        prepared = prepare_source_book(directory)
        assert prepared['slug'] == book['id'], 'Source and catalog IDs differ'
        assert len(prepared['scenes']) == book['sceneCount'], 'Source and catalog scene counts differ'
    html = (directory / 'index.html').read_text()
    html = re.sub(r'<link rel="stylesheet" href="([^"]+)">',
                  lambda m: '<style>\n' + (directory / m[1]).resolve().read_text() + '\n</style>', html)
    scripts = []
    def collect_script(match):
        scripts.append((directory / match[1]).resolve().read_text())
        return ''
    html = re.sub(r'<script defer src="([^"]+)"></script>', collect_script, html)
    images = {f'{i:02}': data_url(directory / 'assets' / f'{i:02}.jpg')
              for i in range(1, book['sceneCount'] + 1)}
    html = re.sub(r'src="assets/(\d\d)\.jpg"', r'data-art="\1"', html)
    code = 'window.BOOK_IMAGES=' + json.dumps(images) + ';\n'
    code += 'document.querySelectorAll("img[data-art]").forEach(el=>el.src=window.BOOK_IMAGES[el.dataset.art]);\n'
    code += '\n'.join(scripts)
    html = html.replace('</body>', '<script>\n' + code + '\n</script>\n</body>')
    target = directory / book['file']
    target.write_text(html)
    assert '<script defer src=' not in html
    assert 'src="assets/' not in html
    print(f'{book["title"]}: {target.stat().st_size / 1024 / 1024:.2f} MiB, {len(images)} images')
    return target

def main():
    catalog = sorted(json.loads((ROOT / 'catalog.json').read_text()), key=lambda item: item['order'])
    assert len({b['id'] for b in catalog}) == len(catalog), 'Duplicate catalog IDs'
    assert len({b['directory'] for b in catalog}) == len(catalog), 'Duplicate book directories'
    (ROOT / 'catalog.js').write_text('window.WENYAN_LIBRARY=' + json.dumps(catalog, ensure_ascii=False) + ';\n')
    artifacts = [build_book(book) for book in catalog]
    shelf_books = [{**book, 'href': quote(book['directory']) + '/' + quote(book['file']),
                    'thumbnail': data_url(ROOT / book['directory'] / 'assets' / 'shelf-cover.jpg')}
                   for book in catalog]
    shelf = (ROOT / 'shared' / 'shelf.template.html').read_text()
    shelf = shelf.replace('/* SHELF_CSS */', (ROOT / 'shared' / 'shelf.css').read_text())
    shelf = shelf.replace('/* SHELF_DATA */', 'window.SHELF_BOOKS=' + json.dumps(shelf_books, ensure_ascii=False) + ';')
    shelf = shelf.replace('/* SHELF_JS */', (ROOT / 'shared' / 'shelf.js').read_text())
    entry = ROOT / '打开书架.html'
    entry.write_text(shelf)
    archive = ROOT / '文言有画·离线阅读包.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as package:
        package.write(entry, '文言有画/打开书架.html')
        for path in artifacts:
            package.write(path, '文言有画/' + str(path.relative_to(ROOT)))
        package.writestr('文言有画/从这里开始.txt',
            '请先解压整个文件夹，再打开“打开书架.html”。\n'
            '每册都是独立 HTML，内含插画，可单独阅读。\n'
            '返回书架和篇目切换需要保留文件夹结构。\n'
            '孩子填写的读后记录保存在浏览器中，不包含在此压缩包内；请在对应绘本中导出重要记录。\n')
    with zipfile.ZipFile(archive) as package:
        archive_files = package.namelist()
    report = {'books': len(catalog), 'shelf_bytes': entry.stat().st_size,
              'reading_zip_bytes': archive.stat().st_size,
              'book_bytes': {b['title']: p.stat().st_size for b,p in zip(catalog,artifacts)},
              'reading_archive_files': archive_files}
    (ROOT / 'qa').mkdir(exist_ok=True)
    (ROOT / 'qa' / 'build-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f'Shelf: {entry.stat().st_size / 1024:.0f} KiB; ZIP: {archive.stat().st_size / 1024 / 1024:.2f} MiB')

if __name__ == '__main__':
    main()
