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

EXPECT_VERSION = '0.2'
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


# ── v0.2 ──────────────────────────────────────────────────────────────
def t_toc_variants():
    for t in ('차려| CHAPTER 2', '차 례', '목차', 'C O N T E N T S', 'Contents'):
        assert TB.TOC_WORDS.search(t), t
    assert not TB.TOC_WORDS.search('차량 목록')


def t_page_marks_ko():
    # OCR 이 '제' 를 '저1'·'저|' 로, '장' 을 '잠·징' 으로 읽는 꼴 (제목은 가짜)
    cases = [('저| 1 장 가짜 제목 19 본문', {1}, 19), ('저1 2 장 가짜 둘 29 본문', {2, 12}, 29),
             ('제 6 잠 가짜 여섯 91 본문', {6}, 91), ('저15 징 가짜 다섯 81 본문', {5, 15}, 81),
             ('제 1 0 장 가짜 열 153 본문', {10}, 153), ('제 10 장 가짜 열 143 본문', {10}, 143),
             ('그림 1-7. 설명 글 저11 잠 가짜 룰 본문', {1, 11}, None), ('18 I 그림 1-21 설명', set(), 18),
             ('제3 판 머리말 6', set(), None)]
    for text, heads, num in cases:
        m = TB.page_marks(text)
        assert m['head'] == heads and m['num'] == num, (text, m)
    assert TB.page_marks('가짜 제목 AP ER 1 I 본문')['opener'] == {1}
    assert TB.page_marks('가짜 제목 ER 2 본문')['opener'] == {2}
    toc = TB.page_marks('제 1 장 가 3 제 2 장 나 17 제 3 장 다 40')
    assert toc['head'] == set() and toc.get('list')                       # 차례 쪽은 쪽 머리 아님


def _marks(spec, n):
    """spec: {쪽(1부터): (head 집합, opener 집합, lead)}"""
    out = []
    for i in range(1, n + 1):
        h, o, lead = spec.get(i, (set(), set(), ''))
        out.append({'head': set(h), 'opener': set(o), 'title': ('가짜%d' % min(h)) if h else None, 'num': None, 'lead': lead})
    return out


def t_resolve_chapters():
    spec = {5: ((), {1}, 'x'), 7: ({1},) + ((), ''), 9: ({1, 11}, (), ''), 11: ({1},) + ((), ''),
            12: ((), (), '가짜2장제목'), 14: ({2, 12}, (), ''), 16: ({2},) + ((), ''), 17: ({5},) + ((), ''),   # 17: 본문 속 "제5장" 잡음
            20: ({3},) + ((), ''), 22: ({3},) + ((), ''), 30: ({5},) + ((), ''), 32: ({5},) + ((), '')}
    marks = _marks(spec, 36)
    marks[11]['lead'] = '가짜2'                                       # p.12 는 2장 제목으로 여는 쪽
    chs, checks = TB.chapters_from_heads(marks)
    got = [(c['num'], c['start'] + 1, c['end'] + 1, c['why']) for c in chs]
    assert got == [(1, 5, 11, '여는 쪽 표지'), (2, 12, 18, '여는 쪽 제목'), (3, 19, 28, '쪽 머리만'), (5, 29, 32, '쪽 머리만')], got
    assert any('4장' in c for c in checks) and any('3장 시작' in c for c in checks) and any('마지막 장' in c for c in checks), checks


def t_chapters_from_outline():
    ol = [(0, 'Cover', 1), (0, 'Contents', 3), (0, 'Part I', 5)] + \
         [(1, 'Chapter %d Topic' % i, 5 + i * 10) for i in range(1, 7)] + [(2, 'sub', 17), (0, 'Index', 90)]
    chs, depths, lv = TB.chapters_from_outline(ol, 100)
    assert lv == 1 and len(chs) == 6 and (chs[0]['start'], chs[0]['end']) == (14, 23) and chs[-1]['end'] == 88, (lv, chs[:1], chs[-1])
    chs, _, lv = TB.chapters_from_outline(ol, 100, level=0)
    assert lv == 0 and [c['title'] for c in chs] == ['Cover', 'Contents', 'Part I', 'Index']
    assert TB.chapters_from_outline([(0, 'A', 1), (0, 'B', 2)], 10)[0] is None     # 모자라면 None → 쪽 머리로


def t_preflight_stops_before_writing():
    d = os.path.join(TMP, 'cloud'); os.makedirs(d); _book(os.path.join(d, 'a.pdf')); _book(os.path.join(d, 'b.pdf'))
    out = os.path.join(TMP, 'cloud_out')
    real = TB._read_ends

    def fake(path):
        if path.endswith('b.pdf'):
            raise OSError(35, 'Resource deadlock avoided')
        return real(path)
    TB._read_ends = fake
    try:
        for fn in (lambda: TB.probe(d, out, 'n', stream=io.StringIO()), lambda: TB.plan(d, out, 'n', stream=io.StringIO())):
            try:
                fn(); assert False, '멈추지 않음'
            except SystemExit as e:
                assert 'b.pdf' in str(e) and '오프라인' in str(e), str(e)
            assert not os.path.exists(out) or os.listdir(out) == [], os.listdir(out)
    finally:
        TB._read_ends = real


def t_skip_recursive():
    d = os.path.join(TMP, 'rec'); os.makedirs(os.path.join(d, 'sub')); os.makedirs(os.path.join(d, '.hidden'))
    for f in ('a.pdf', 'b.pdf', os.path.join('sub', 'c.pdf'), os.path.join('.hidden', 'x.pdf')):
        open(os.path.join(d, f), 'wb').write(b'%PDF-1.4\n')
    assert TB.list_books(d) == ['a.pdf', 'b.pdf']
    assert TB.list_books(d, recursive=True) == ['a.pdf', 'b.pdf', os.path.join('sub', 'c.pdf')]
    assert TB.list_books(d, skip=['b.pdf'], recursive=True) == ['a.pdf', os.path.join('sub', 'c.pdf')]
    assert TB.list_books(d, only='c', recursive=True, numbered=True) == [(3, os.path.join('sub', 'c.pdf'))]


def _heads_book(path):
    F = FILL
    pages = [['Title Page'], ['Contents', 'Chapter 1 Liver 1 Chapter 2 Kidney 6'],
             ['CHAPTER 1', 'Liver', F], ['2', F], ['Chapter 1 Liver 3', F], ['4', F], ['Chapter 1 Liver 5', F],
             ['CHAPTER 2', 'Kidney', F], ['7', F], ['Chapter 2 Kidney 8', F], ['9', F], ['Chapter 2 Kidney 10', F],
             ['Index', F]]
    make_pdf(path, pages)


def t_plan_heads_pdf():
    d = os.path.join(TMP, 'plan1'); os.makedirs(d); _heads_book(os.path.join(d, 'h.pdf'))
    out = os.path.join(TMP, 'plan1_out')
    done, left = TB.plan(d, out, '260927_시험plan', stream=io.StringIO())
    assert done == 1 and left == []
    b = open(os.path.join(out, '260927_시험plan_01.md'), encoding='utf8').read()
    assert b.startswith('<!-- plan: method=쪽 머리 chapters=2 ')
    assert '| 앞 | (앞붙이) | 1 | 2 | 2 |' in b, b
    assert '| 01 | Liver | 3 | 7 | 5 | 1–5 | 여는 쪽 표지 |' in b, b
    assert '| 02 | Kidney | 8 | 12 | 5 | 6–10 | 여는 쪽 표지 |' in b, b
    assert '| 뒤 | (뒤붙이) | 13 | 13 | 1 |' in b
    s = open(os.path.join(out, '260927_시험plan_요약.md'), encoding='utf8').read()
    assert '| 01 | h.pdf | 쪽 머리 | 2 |' in s and '남은 책 0권' in s, s


def t_plan_outline_pdf():
    d = os.path.join(TMP, 'plan2'); os.makedirs(d)
    pages = [['Cover']] + [['Chapter %d' % (i // 3 + 1), FILL] for i in range(15)]
    ol = [('Cover', 0, None)] + [('Chapter %d Topic' % k, 1 + (k - 1) * 3, None) for k in range(1, 6)]
    make_pdf(os.path.join(d, 'o.pdf'), pages, ol, labels=[(0, 0, '/r', 1), (1, 15, '/D', 1)])
    out = os.path.join(TMP, 'plan2_out')
    TB.plan(d, out, 'p', stream=io.StringIO())
    b = open(os.path.join(out, 'p_01.md'), encoding='utf8').read()
    assert 'method=책갈피 (깊이 0)' in b and '| 01 | Chapter 1 Topic | 2 | 4 | 3 | 1–3 | 책갈피 깊이 0 |' in b, b
    assert '| 05 | Chapter 5 Topic | 14 | 16 | 3 | 13–15 |' in b, b


def t_plan_budget_resume():
    d = os.path.join(TMP, 'plan3'); os.makedirs(d)
    _heads_book(os.path.join(d, 'a.pdf')); _heads_book(os.path.join(d, 'b.pdf'))
    open(os.path.join(d, 'c.pdf'), 'wb').write(b'%PDF-1.4\nbroken')
    out = os.path.join(TMP, 'plan3_out')
    done, left = TB.plan(d, out, 'r', budget=0, stream=io.StringIO())        # 첫 책은 늘 한다
    assert done == 1 and left == ['b.pdf', 'c.pdf'], (done, left)
    s = open(os.path.join(out, 'r_요약.md'), encoding='utf8').read()
    assert '| 02 | b.pdf | (남음) |' in s and '남은 책 2권' in s, s
    m1 = os.path.getmtime(os.path.join(out, 'r_01.md'))
    done, left = TB.plan(d, out, 'r', stream=io.StringIO())
    assert done == 2 and left == [] and os.path.getmtime(os.path.join(out, 'r_01.md')) == m1
    s = open(os.path.join(out, 'r_요약.md'), encoding='utf8').read()
    assert '| 03 | c.pdf | 오류 |' in s and '남은 책 0권' in s, s


def t_cli_plan():
    d = os.path.join(TMP, 'cli2'); os.makedirs(d); _heads_book(os.path.join(d, 'k.pdf'))
    out = os.path.join(TMP, 'cli2_out')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'textbook.py'), 'plan', d, '--out', out, '--name', 'c2', '--skip', 'zzz'],
                       capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode == 0 and '| 01 | k.pdf | 쪽 머리 | 2 |' in r.stdout, (r.stdout[-400:], r.stderr[-400:])


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
