#!/usr/bin/env python3
"""textbook.py 테스트 — python3 test_textbook.py (pytest 불필요). fixture PDF 는 pypdf 로 만든다(가짜 글, 영어)."""
import io
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import textbook as TB          # noqa: E402

EXPECT_VERSION = '0.1'
TMP = tempfile.mkdtemp(prefix='ttb_')


def _manifest_version(fname):
    p = os.path.join(HERE, 'TOOLS_MANIFEST.md')
    if not os.path.exists(p):
        return None
    m = re.search(r'\| `%s` \| v([0-9.]+)' % re.escape(fname), open(p, encoding='utf8').read())
    return m.group(1) if m else None


def make_pdf(path, pages, outline=(), labels=None):
    """pages: 쪽마다 줄 목록(None = 글자 없는 쪽). outline: (제목, 쪽 0부터, 부모 제목 or None)."""
    pypdf = TB.load_pypdf()
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
    w = pypdf.PdfWriter()
    font = w._add_object(DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'),
                                           NameObject('/BaseFont'): NameObject('/Helvetica')}))
    for lines in pages:
        pg = w.add_blank_page(612, 792)
        if lines is None:
            continue
        body = ['BT', '/F1 11 Tf', '14 TL', '72 740 Td']
        for ln in lines:
            body.append('(%s) Tj T*' % ln.replace('(', r'\(').replace(')', r'\)'))
        body.append('ET')
        s = DecodedStreamObject(); s.set_data('\n'.join(body).encode('latin-1'))
        pg[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): font})})
        pg[NameObject('/Contents')] = w._add_object(s)
    made = {}
    for title, pno, parent in outline:
        made[title] = w.add_outline_item(title, pno, parent=made.get(parent))
    if labels:
        for a, b, style, start in labels:
            w.set_page_label(a, b, style=style, start=start)
    with open(path, 'wb') as f:
        w.write(f)


FILL = 'Lorem ipsum radiology text line for the sample page, long enough to count as text.'


def _book(path, with_outline=True):
    pages = [['Title Page'], None, ['Contents', 'Chapter 1 Liver ..... 1', 'Chapter 2 Kidney ..... 3']]
    for i in range(1, 7):
        pages.append(['Chapter %d' % (1 if i <= 2 else 2), FILL, FILL, str(i)])   # 인쇄 쪽 번호 1..6, PDF 쪽 4..9
    ol = [('Chapter 1 Liver', 3, None), ('1.1 Anatomy', 3, 'Chapter 1 Liver'), ('Chapter 2 Kidney', 5, None)] if with_outline else ()
    make_pdf(path, pages, ol, labels=[(0, 2, '/r', 1), (3, 8, '/D', 1)])


def t_version():
    assert TB.__version__ == EXPECT_VERSION
    mv = _manifest_version('textbook.py')
    assert mv is None or mv == TB.__version__, ('TOOLS_MANIFEST.md 의 판', mv, '코드', TB.__version__)
    first = open(os.path.join(HERE, 'TEXTBOOK.md'), encoding='utf8').readline()
    assert 'v%s' % TB.__version__ in first, first


def t_sample_pages():
    h, b = TB.sample_pages(1000, 40, 20)
    assert h == list(range(40)) and len(b) == 20 and min(b) >= 40 and max(b) < 1000
    h, b = TB.sample_pages(10, 40, 20)
    assert h == list(range(10)) and b == []


def t_probe_book():
    p = os.path.join(TMP, 'a.pdf'); _book(p)
    r = TB.probe_book(p, front=3, samples=6)
    assert r['error'] is None and r['pages'] == 9
    assert [(d, t, pg) for d, t, pg in r['outline']] == [(0, 'Chapter 1 Liver', 4), (1, '1.1 Anatomy', 4), (0, 'Chapter 2 Kidney', 6)], r['outline']
    assert r['page_labels'] and ('1', 'i') in [(str(a), b) for a, b in r['labels_sample']], r['labels_sample']
    assert r['toc_pages'] == [3], r['toc_pages']
    assert r['text_pages'] == 7 and r['sampled'] == 9                      # 빈 쪽 + 짧은 표지
    assert r['offset'] and r['offset'][0] == 3, r['offset']                # PDF 쪽 − 인쇄 쪽 = 3


def t_probe_outputs_and_errors():
    d = os.path.join(TMP, 'books'); os.makedirs(d)
    _book(os.path.join(d, 'B one.pdf')); _book(os.path.join(d, 'A two.pdf'), with_outline=False)
    open(os.path.join(d, 'C broken.pdf'), 'wb').write(b'%PDF-1.4\nnot really')
    open(os.path.join(d, 'notes.txt'), 'w').write('x')
    out = os.path.join(TMP, 'out')
    res = TB.probe(d, out, '260927_시험probe', front=3, samples=6, stream=io.StringIO())
    assert [r['file'] for r in res] == ['A two.pdf', 'B one.pdf', 'C broken.pdf']
    assert res[2]['error'] and not res[0]['error']
    names = sorted(os.listdir(out))
    assert names == ['260927_시험probe_01.md', '260927_시험probe_02.md', '260927_시험probe_03.md', '260927_시험probe_요약.md'], names
    s = open(os.path.join(out, '260927_시험probe_요약.md'), encoding='utf8').read()
    assert '| 01 | A two.pdf |' in s and '| 없음 |' in s and '3개 · 깊이 2' in s and '오류:' in s and '오류 1권' in s
    b = open(os.path.join(out, '260927_시험probe_02.md'), encoding='utf8').read()
    assert '  - 1.1 Anatomy — p.4' in b and 'Chapter 2 Kidney ..... 3' in b and '+3 — 표본' in b
    assert sorted(os.listdir(d)) == ['A two.pdf', 'B one.pdf', 'C broken.pdf', 'notes.txt']   # 원본 폴더에 쓰지 않음
    try:
        TB.probe(d, out, '260927_시험probe', front=3, samples=6, stream=io.StringIO()); assert False, '덮어씀'
    except SystemExit as e:
        assert '이미 있다' in str(e)


def t_only_and_name_guard():
    d = os.path.join(TMP, 'only'); os.makedirs(d)
    _book(os.path.join(d, 'x1.pdf')); _book(os.path.join(d, 'y2.pdf'))
    res = TB.probe(d, os.path.join(TMP, 'o2'), 'n', only='y', front=3, samples=2, stream=io.StringIO())
    assert [r['file'] for r in res] == ['y2.pdf']
    import unicodedata
    nfd = unicodedata.normalize('NFD', '산과영상 책.pdf'); _book(os.path.join(d, nfd))
    res = TB.probe(d, os.path.join(TMP, 'o4'), 'n', only='산과영상', front=3, samples=2, stream=io.StringIO())
    assert len(res) == 1 and not res[0]['error'], res   # NFD 파일 이름도 NFC 로 찾는다
    for bad in ('a&b', 'a/b', 'a?b'):
        try:
            TB.probe(d, os.path.join(TMP, 'o3'), bad, stream=io.StringIO()); assert False, bad
        except SystemExit as e:
            assert '기호' in str(e)


def t_cli():
    d = os.path.join(TMP, 'cli'); os.makedirs(d); _book(os.path.join(d, 'k.pdf'))
    out = os.path.join(TMP, 'cli_out')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'textbook.py'), 'probe', d, '--out', out, '--name', 'c', '--front', '3'],
                       capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode == 0 and '| 01 | k.pdf |' in r.stdout, (r.stdout[-400:], r.stderr[-400:])
    r = subprocess.run([sys.executable, os.path.join(HERE, 'textbook.py'), 'probe', os.path.join(TMP, 'empty_none'), '--out', out],
                       capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode != 0


if __name__ == '__main__':
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith('t_') and callable(v)]
    try:
        TB.load_pypdf()
    except SystemExit as e:          # pypdf 없음 — 건너뛰지 않고 실패로 (SKIP 은 통과가 아니다)
        print(str(e)); print('\n통과 0 / 건너뜀 0 / 실패 %d  (전체 %d)' % (len(tests), len(tests))); sys.exit(1)
    ok = fail = 0
    for name, fn in tests:
        try:
            fn(); ok += 1; print('PASS %s' % name[2:])
        except Exception as e:
            fail += 1; print('FAIL %-40s %s: %s' % (name[2:], type(e).__name__, str(e)[:300]))
    print('\n통과 %d / 건너뜀 0 / 실패 %d  (전체 %d)' % (ok, fail, ok + fail))
    sys.exit(1 if fail else 0)
