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

EXPECT_VERSION = '0.8.1'
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
    assert TB.list_books(d, skip=['b.pdf'], recursive=True, numbered=True) == [(1, 'a.pdf'), (3, os.path.join('sub', 'c.pdf'))]   # v0.3: 빼도 번호 그대로


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
    pages = [['Cover']] + [['Chapter %d' % (i // 6 + 1), FILL] for i in range(30)]
    ol = [('Cover', 0, None)] + [('Chapter %d Topic' % k, 1 + (k - 1) * 6, None) for k in range(1, 6)]
    make_pdf(os.path.join(d, 'o.pdf'), pages, ol, labels=[(0, 0, '/r', 1), (1, 30, '/D', 1)])
    out = os.path.join(TMP, 'plan2_out')
    TB.plan(d, out, 'p', stream=io.StringIO())
    b = open(os.path.join(out, 'p_01.md'), encoding='utf8').read()
    assert 'method=책갈피 (깊이 0)' in b and '| 01 | Chapter 1 Topic | 2 | 7 | 6 | 1–6 | 책갈피 깊이 0 |' in b, b
    assert '| 05 | Chapter 5 Topic | 26 | 31 | 6 | 25–30 |' in b, b


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


# ── v0.3 ──────────────────────────────────────────────────────────────
def t_first_chapter_not_one():
    # 분책 2권: 쪽 머리가 11장부터. '저11 장' 은 {1, 11} — 뒤 쪽 머리('제 11 장')가 가른다
    spec = {3: ({1, 11},) + ((), ''), 5: ({11},) + ((), ''), 7: ({1, 11},) + ((), ''), 9: ({11},) + ((), ''),
            12: ({12},) + ((), ''), 14: ({12, 2},) + ((), ''), 16: ({12},) + ((), '')}
    chs, skipped = TB.resolve_chapters(_marks(spec, 18))
    assert [(c['num'], c['first'] + 1) for c in chs] == [(11, 3), (12, 12)] and skipped == [], chs
    lone = TB.resolve_chapters(_marks({3: ({7},) + ((), '')}, 10))[0]
    assert lone == [], lone                                                  # 한 번만 나온 번호는 첫 장이 아니다


def t_offsets_and_titles():
    mk = lambda nums: [{'num': x} for x in nums]
    assert TB._offsets(mk([None, 1, 2, 3, 4]), 1, 4) == (1, 4)
    assert TB._offsets(mk([None, 1, 2, None, None]), 0, 4) is None            # 2표 — 모자람
    assert TB._offsets(mk([47, 88, 3, 150, 9]), 0, 4) is None                # 본문 숫자 — 과반 아님
    assert TB._offsets(mk([None, 200, 201, 202, 203]), 0, 4) is None         # 차이 −199
    assert TB._clean_title('I 흉부 병변의 위치 결정') == '흉부 병변의 위치 결정'
    assert TB._clean_title('| 무기폐 ·”:-') == '무기폐' and TB._clean_title('식도') == '식도'
    assert TB._clean_title('흉부결핵 I') == '흉부결핵' and TB._clean_title('CT 물리 I') == 'CT 물리' and TB._clean_title('Part I') == 'Part'


def t_back_matter_and_chunks():
    spec = {3: ({1},) + ((), ''), 5: ({1},) + ((), ''), 7: ({1},) + ((), '')}
    marks = _marks(spec, 12)
    marks[9]['lead'] = '찾아보기가나다'
    chs, checks = TB.chapters_from_heads(marks)
    assert chs[-1]['end'] == 8 and not any('마지막 장' in c for c in checks), (chs, checks)   # p.10 찾아보기 앞까지
    d = os.path.join(TMP, 'plain'); os.makedirs(d)
    make_pdf(os.path.join(d, 'p.pdf'), [['plain text page %d' % i, FILL] for i in range(65)])
    out = os.path.join(TMP, 'plain_out'); TB.plan(d, out, 'q', stream=io.StringIO())
    b = open(os.path.join(out, 'q_01.md'), encoding='utf8').read()
    assert 'method=쪽 묶음 30 chapters=3' in b and '| 03 | p.61–65 | 61 | 65 | 5 |' in b and '30쪽 묶음' in b, b


def t_plan_child_killed():
    d = os.path.join(TMP, 'kill'); os.makedirs(d); _heads_book(os.path.join(d, 'a.pdf')); _heads_book(os.path.join(d, 'zz_kill.pdf'))
    out = os.path.join(TMP, 'kill_out')
    os.environ['TEXTBOOK_TEST_KILL'] = 'zz_kill'
    try:
        done, left = TB.plan(d, out, 'k', stream=io.StringIO())
    finally:
        del os.environ['TEXTBOOK_TEST_KILL']
    assert done == 2 and left == []
    b = open(os.path.join(out, 'k_02.md'), encoding='utf8').read()
    assert 'error=yes' in b and 'Killed' in b, b
    s = open(os.path.join(out, 'k_요약.md'), encoding='utf8').read()
    assert '| 01 | a.pdf | 쪽 머리 | 2 |' in s and '| 02 | zz_kill.pdf | 오류 |' in s, s


# ── v0.4 (3단계) ───────────────────────────────────────────────────────
def t_short_name():
    assert TB.short_name('복부영상의학(4판)(양장본 HardCover) (대한복부영상의학회)_R+_OCR+.pdf') == '복부영상의학(4판)'
    assert TB.short_name('흉부영상진단 X선(3판)(양장본 HardCover) (대한흉부영상의학회)_R+_OCR+ (1).pdf') == '흉부영상진단 X선(3판)'
    assert TB.short_name('Practical+Textbook+of+Cardiac+CT+and+MRI.pdf') == 'Practical Textbook of Cardiac CT and MRI'
    assert TB.short_name('심장 혈관.pdf') == '심장 혈관' and TB.short_name('A→B & C.pdf') == 'A_B _ C'


def t_plan_resumes_empty_md():
    d = os.path.join(TMP, 'z0'); os.makedirs(d); _heads_book(os.path.join(d, 'a.pdf'))
    out = os.path.join(TMP, 'z0_out'); os.makedirs(out)
    open(os.path.join(out, 'z_01.md'), 'w').close()                                       # 0바이트 — 거짓 완료였던 것
    done, _ = TB.plan(d, out, 'z', stream=io.StringIO())
    assert done == 1 and TB._md_ok(os.path.join(out, 'z_01.md'), TB.PLAN_HEAD)
    assert '남은 책 0권' in open(os.path.join(out, 'z_요약.md'), encoding='utf8').read()


def _split_setup(tag):
    d = os.path.join(TMP, tag); os.makedirs(d); _heads_book(os.path.join(d, 'h book.pdf'))
    pdir = os.path.join(TMP, tag + '_plan'); TB.plan(d, pdir, 'pl', stream=io.StringIO())
    return d, pdir


def t_split_search_and_printed_map():
    d, pdir = _split_setup('sp')
    out = os.path.join(TMP, 'sp_out')
    done, left = TB.split(d, pdir, 'pl', out, stream=io.StringIO())
    assert done == 1 and left == []
    bd = os.path.join(out, '01_h book')
    assert sorted(os.listdir(bd)) == ['00_앞붙이.md', '01_Liver.md', '02_Kidney.md', '99_뒤붙이.md', 'INDEX.md'], os.listdir(bd)
    c1 = open(os.path.join(bd, '01_Liver.md'), encoding='utf8').read()
    assert '[p.— · PDF 1] (겹침 — 앞)' in c1 and '[p.1 · PDF 3]' in c1 and '[p.5 · PDF 7]' in c1 and '[p.7 · PDF 9] (겹침 — 뒤)' in c1, c1[:600]
    assert 'Lorem ipsum' in c1
    ix = open(os.path.join(bd, 'INDEX.md'), encoding='utf8').read()
    assert '| `01_Liver.md` | 1 | Liver | 1–5 | 3–7 | 5 |' in ix, ix
    assert TB.printed_to_pdf(os.path.join(bd, 'INDEX.md'), 4) == 6 and TB.printed_to_pdf(os.path.join(bd, 'INDEX.md'), 99) is None
    top = open(os.path.join(out, 'INDEX.md'), encoding='utf8').read()
    assert '| 01 | h book | `01_h book/INDEX.md` | 4 | 13 |' in top and '남은 책 0권' in top, top
    assert TB.split(d, pdir, 'pl', out, stream=io.StringIO())[0] == 0                       # 끝난 책은 건너뜀
    hits = TB.search(out, 'Loremipsum radiology', stream=io.StringIO())                   # 띄어쓰기 무시
    pdfs = [h[2] for h in hits]
    assert len(pdfs) == len(set(pdfs)) and len(hits) == 11, hits                            # 겹침 쪽은 한 번만(글 있는 11쪽)
    assert [h[1] for h in hits if h[2] == '[p.6 · PDF 8]'] == ['02_Kidney.md'], hits          # 겹침 쪽은 제 장 파일로
    assert sorted({h[1] for h in TB.search(out, 'Chapter 2 Kidney', stream=io.StringIO())}) == ['00_앞붙이.md', '02_Kidney.md']   # 차례 쪽도 찾힌다


def t_split_parts_long_chapter():
    rows = [('앞', '앞붙이', 1, 2, None), (1, 'Long chapter', 3, 70, 2), ('뒤', '뒤붙이', 71, 75, None)]
    u = TB.split_units(rows, 75, part=30, overlap=2)
    assert [x[0] for x in u] == ['00_앞붙이.md', '01_Long_chapter_1.md', '01_Long_chapter_2.md', '01_Long_chapter_3.md', '99_뒤붙이.md'], u
    assert [(x[3], x[4], x[5], x[6]) for x in u[1:4]] == [(3, 32, 1, 34), (33, 62, 31, 64), (63, 70, 61, 72)], u


def t_page_images():
    from PIL import Image, ImageDraw
    d = os.path.join(TMP, 'img'); os.makedirs(d)
    im = Image.new('RGB', (300, 400), 'white'); ImageDraw.Draw(im).rectangle([50, 50, 250, 350], outline='black', width=5)
    im.save(os.path.join(d, 'img book.pdf'), 'PDF'); _heads_book(os.path.join(d, 'other.pdf'))
    out = os.path.join(TMP, 'img_out')
    got = TB.page_images(d, 'img book', out, pdf_page=1, stream=io.StringIO())
    assert len(got) == 1 and got[0].endswith('img_book_PDF1.jpg') and Image.open(got[0]).size == (300, 400), got   # v0.5: 기본 JPEG
    got = TB.page_images(d, 'img book', out, pdf_page=1, fmt='png', stream=io.StringIO())
    assert got[0].endswith('img_book_PDF1.png'), got
    tiny = Image.new('RGB', (1, 1)); tiny.save(os.path.join(d, 'tiny.pdf'), 'PDF')
    buf = io.StringIO(); assert TB.page_images(d, 'tiny', out, pdf_page=1, stream=buf) == [] and '건너뛰었다' in buf.getvalue(), buf.getvalue()
    for bad in (dict(book='zzz', pdf_page=1), dict(book='img book', pdf_page=9)):
        try:
            TB.page_images(d, bad['book'], out, pdf_page=bad['pdf_page'], stream=io.StringIO()); assert False, bad
        except SystemExit:
            pass
    buf = io.StringIO(); assert TB.page_images(d, 'other', out, pdf_page=1, stream=buf) == [] and '이미지가 없다' in buf.getvalue()


def _cmyk_pdf(path, decode):
    """CMYK JPEG(Adobe 표지 — 뒤집힌 값) 한 장이 든 PDF. decode=True 면 출판 프로그램처럼 /Decode [1 0 …] 로 되돌린다."""
    from PIL import Image
    from pypdf import PdfWriter
    from pypdf.generic import NameObject, NumberObject, StreamObject, DictionaryObject, ArrayObject
    im = Image.new('CMYK', (200, 200), (0, 255, 255, 0)); im.paste((255, 255, 0, 0), (0, 100, 200, 200))   # 위 빨강 · 아래 파랑
    b = io.BytesIO(); im.save(b, 'JPEG', quality=95)
    w = PdfWriter(); pg = w.add_blank_page(200, 200)
    x = StreamObject(); x._data = b.getvalue()
    x.update({NameObject('/Type'): NameObject('/XObject'), NameObject('/Subtype'): NameObject('/Image'),
              NameObject('/Width'): NumberObject(200), NameObject('/Height'): NumberObject(200),
              NameObject('/ColorSpace'): NameObject('/DeviceCMYK'), NameObject('/BitsPerComponent'): NumberObject(8),
              NameObject('/Filter'): NameObject('/DCTDecode')})
    if decode:
        x[NameObject('/Decode')] = ArrayObject([NumberObject(v) for v in (1, 0, 1, 0, 1, 0, 1, 0)])
    c = StreamObject(); c._data = b'q 200 0 0 200 0 0 cm /Im0 Do Q'
    pg[NameObject('/Resources')] = DictionaryObject({NameObject('/XObject'): DictionaryObject({NameObject('/Im0'): w._add_object(x)})})
    pg[NameObject('/Contents')] = w._add_object(c)
    w.write(path)


def t_v051_page_cmyk_png_and_rc():
    # Cowork 09-28 [결함]: 전자책 PDF 74 의 CMYK JPEG 3장이 --png 에서 모두 OSError, 파일 0개인데 rc=0
    from PIL import Image
    d = os.path.join(TMP, 'cmyk'); os.makedirs(d)
    Image.new('CMYK', (200, 200), (0, 255, 255, 0)).save(os.path.join(d, 'pil cmyk.pdf'), 'PDF')
    _cmyk_pdf(os.path.join(d, 'adobe cmyk.pdf'), decode=True)
    _cmyk_pdf(os.path.join(d, 'raw cmyk.pdf'), decode=False)
    Image.new('RGB', (1, 1)).save(os.path.join(d, 'tiny.pdf'), 'PDF')
    out = os.path.join(TMP, 'cmyk_out')
    near = lambda px, want: all(abs(a - b) < 40 for a, b in zip(px, want))
    # 성공 길: PNG 도 RGB 로 바꿔 저장, 색은 뷰어(MuPDF 로 확인)와 같게 — 빨강·파랑
    for book, fmt in (('pil cmyk', 'png'), ('adobe cmyk', 'png'), ('adobe cmyk', 'jpg')):
        buf = io.StringIO(); got = TB.page_images(d, book, out, pdf_page=1, fmt=fmt, stream=buf)
        assert len(got) == 1 and got[0].endswith('.' + fmt) and '실패' not in buf.getvalue(), (book, fmt, got, buf.getvalue())
        im = Image.open(got[0]); assert im.mode == 'RGB', im.mode
        assert near(im.getpixel((10, 10)), (255, 0, 0)), (book, fmt, im.getpixel((10, 10)))
        if book == 'adobe cmyk':
            assert near(im.getpixel((10, 150)), (0, 0, 255)), (book, fmt, im.getpixel((10, 150)))
    # /Decode 없는 Adobe JPEG 는 뷰어도 뒤집어 그린다(MuPDF 로 확인) — 도구가 따로 되돌리지 않는다
    got = TB.page_images(d, 'raw cmyk', out, pdf_page=1, fmt='png', stream=io.StringIO())
    assert len(got) == 1 and not near(Image.open(got[0]).getpixel((10, 10)), (255, 0, 0)), got
    # 종료 코드: 저장했으면 0, 하나도 못 저장했으면 0 이 아니다
    cli = lambda book: subprocess.run([sys.executable, os.path.join(HERE, 'textbook.py'), 'page', d, '--book', book, '--pdf', '1', '--png', '--out', out],
                                      capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    r = cli('adobe cmyk'); assert r.returncode == 0 and r.stdout.strip().endswith('.png'), (r.returncode, r.stdout, r.stderr)
    r = cli('tiny'); assert r.returncode != 0 and '저장한 그림이 없다' in r.stderr, (r.returncode, r.stdout, r.stderr)


def t_v06_page_render_maxpx_name():
    # v0.6 (Cowork 09-28 제안, 사용자 결정): --render 쪽 전체(pdftoppm) · --max-px 긴 변 상한 · --name 이름 틀
    import shutil
    from PIL import Image
    d = os.path.join(TMP, 'render'); os.makedirs(d)
    im = Image.new('RGB', (300, 400), 'white'); im.paste((0, 0, 0), (50, 50, 250, 350)); im.save(os.path.join(d, 'pic book.pdf'), 'PDF')
    _heads_book(os.path.join(d, 'text book.pdf'))
    out = os.path.join(TMP, 'render_out')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    cli = lambda *a, **kw: subprocess.run([sys.executable, os.path.join(HERE, 'textbook.py'), 'page', d, '--out', out] + list(a),
                                          capture_output=True, text=True, env=kw.get('env', env))
    # --max-px · --name (그림 뽑기 길): 300×400 → 긴 변 100, 이름 틀 {pdf}
    got = TB.page_images(d, 'pic book', out, pdf_page=1, fmt='png', max_px=100, name='PB_q{pdf:03d}', stream=io.StringIO())
    assert [os.path.basename(g) for g in got] == ['PB_q001.png'] and Image.open(got[0]).size == (75, 100), (got, Image.open(got[0]).size)
    got = TB.page_images(d, 'pic book', out, pdf_page=1, fmt='png', max_px=1000, stream=io.StringIO())   # 상한보다 작으면 그대로
    assert Image.open(got[0]).size == (300, 400), Image.open(got[0]).size
    # 이름 틀 실패 길: 인쇄 쪽을 모르는데 {printed}, 모르는 칸, 폴더 포함, --max-px 너무 작음
    for kw in (dict(name='X_p{printed:03d}'), dict(name='X_{zzz}'), dict(name='a/b_{pdf}'), dict(max_px=4), dict(render=True, dpi=5)):
        try:
            TB.page_images(d, 'pic book', out, pdf_page=1, fmt='png', stream=io.StringIO(), **kw); assert False, kw
        except SystemExit as e:
            assert '[멈춤]' in str(e), (kw, e)
    # --render 실패 길: pdftoppm 이 없으면 멈춘다(종료 코드 0 아님)
    bare = os.path.join(TMP, 'bare_path'); os.makedirs(bare, exist_ok=True)
    r = cli('--book', 'text book', '--pdf', '3', '--render', '--png', env=dict(env, PATH=bare))
    assert r.returncode != 0 and 'pdftoppm 이 없다' in r.stderr, (r.returncode, r.stdout, r.stderr)
    if not shutil.which('pdftoppm'):
        return   # 성공 길은 pdftoppm 이 있는 곳(빌드·Cowork Mac)에서
    # --render 성공 길: 글만 있는 쪽 — 그림 뽑기는 0개로 멈추지만 쪽 전체 그림은 한 장, 글자가 찍힌다
    r = cli('--book', 'text book', '--pdf', '3', '--png')
    assert r.returncode != 0 and '저장한 그림이 없다' in r.stderr, (r.returncode, r.stderr)
    r = cli('--book', 'text book', '--pdf', '3', '--render', '--png', '--dpi', '100', '--max-px', '600', '--name', 'TB_{pdf:03d}')
    assert r.returncode == 0 and r.stdout.strip().endswith('TB_003.png') and '쪽 전체 100 dpi' in r.stdout, (r.returncode, r.stdout, r.stderr)
    pic = Image.open(os.path.join(out, 'TB_003.png'))
    assert pic.mode == 'RGB' and max(pic.size) <= 600 and pic.convert('L').getextrema()[0] < 128, (pic.mode, pic.size, pic.convert('L').getextrema())
    # 그림 쪽 render: 가운데 검정 · 가장자리 흰색 (쪽 300×400 pt, 72 dpi → 300×400 px)
    got = TB.page_images(d, 'pic book', out, pdf_page=1, fmt='jpg', render=True, dpi=72, stream=io.StringIO())
    pic = Image.open(got[0]); assert abs(pic.size[0] - 300) <= 2 and abs(pic.size[1] - 400) <= 2, pic.size
    assert sum(pic.getpixel((150, 200))) < 60 and sum(pic.getpixel((10, 10))) > 700, (pic.getpixel((150, 200)), pic.getpixel((10, 10)))


def t_v04_opener_first_tail_warning_units():
    # 여는 쪽 표지가 제목 일치보다 먼저 — 차례 쪽(p.4)이 장 제목을 담고 있어도 p.8 의 표지를 고른다
    spec = {10: ({1},) + ((), ''), 12: ({1},) + ((), ''), 14: ({1},) + ((), ''), 20: ({2},) + ((), ''), 22: ({2},) + ((), '')}
    marks = _marks(spec, 200)
    marks[3]['lead'] = '가짜1가짜2차례'; marks[7]['opener'] = {1}; marks[189]['lead'] = '찾아보기'
    chs, checks = TB.chapters_from_heads(marks)
    assert (chs[0]['start'] + 1, chs[0]['why']) == (8, '여는 쪽 표지'), chs[0]
    assert any('2장 끝' in c and '쪽 머리 없이' in c for c in checks), checks                 # 쪽 머리 없는 꼬리 167쪽
    # split: 앞·뒤 나눔, 수상하게 긴 장의 뒤쪽은 '미확인'
    rows = [('앞', '앞붙이', 1, 95, None)] + [(k, 'T%d' % k, 96 + (k - 1) * 20, 95 + k * 20, None) for k in range(1, 6)] + \
           [(6, 'Long', 196, 400, None), ('뒤', '뒤붙이', 401, 440, None)]
    u = TB.split_units(rows, 440)
    names = [x[0] for x in u]
    assert names[:4] == ['00_앞붙이_1.md', '00_앞붙이_2.md', '00_앞붙이_3.md', '00_앞붙이_4.md'] and '장 미확인일 수 있음' in u[0][2], u[:2]
    assert '06_Long_1.md' in names and '06_미확인_p226-255.md' in names and not any(n.startswith('06_Long_2') for n in names), names
    assert names[-2:] == ['99_뒤붙이_1.md', '99_뒤붙이_2.md'], names
    assert TB._fill_titles([(1, 'Chapter 1', 5, 9, None), (2, 'Intro', 10, 12, None)],
                           [(0, 'Chapter 1', 5), (1, '1 Imaging Contrast Agents', 5), (0, 'Chapter 2', 10)])[0][1] == '1 Imaging Contrast Agents'


def t_v04_split_page_labels():
    d = os.path.join(TMP, 'lab'); os.makedirs(d)
    pages = [['Cover']] + [['Chapter %d' % (i // 6 + 1), FILL] for i in range(30)]
    ol = [('Cover', 0, None)] + [('Chapter %d Topic' % k, 1 + (k - 1) * 6, None) for k in range(1, 6)]
    make_pdf(os.path.join(d, 'lab.pdf'), pages, ol, labels=[(0, 0, '/r', 1), (1, 30, '/D', 1)])
    pdir = os.path.join(TMP, 'lab_plan'); TB.plan(d, pdir, 'pl', stream=io.StringIO())
    out = os.path.join(TMP, 'lab_out'); TB.split(d, pdir, 'pl', out, stream=io.StringIO())
    c1 = open(os.path.join(out, '01_lab', '01_Chapter_1_Topic.md'), encoding='utf8').read()
    assert '[p.i · PDF 1] (겹침 — 앞)' in c1 and '[p.1 · PDF 2]' in c1 and '인쇄 1–6쪽' in c1, c1[:400]
    assert '| `01_Chapter_1_Topic.md` | 1 | Chapter 1 Topic | 1–6 | 2–7 | 6 |' in open(os.path.join(out, '01_lab', 'INDEX.md'), encoding='utf8').read()


def t_v05_split_part_option():
    d, pdir = _split_setup('pt')
    out = os.path.join(TMP, 'pt_out')
    TB.split(d, pdir, 'pl', out, part=2, stream=io.StringIO())
    names = sorted(os.listdir(os.path.join(out, '01_h book')))
    assert '01_Liver_1.md' in names and '01_Liver_3.md' in names and '02_Kidney_3.md' in names, names


def t_v072_split_failure_paths():
    """코드 리뷰 17: split 실패 길 — 하위 프로세스 실패는 '남음' 이 아니라 '실패'(까닭과 함께), 이번 실행 수에 넣지 않고 rc=1."""
    d, pdir = _split_setup('sf')
    pf = os.path.join(pdir, 'pl_01.md'); good = open(pf, encoding='utf8').read()
    open(pf, 'w', encoding='utf8').write(good.splitlines()[0] + '\n\n(장 표를 지웠다)\n')      # 첫 줄은 온전 → 장 표 빔 → 하위 프로세스 ValueError
    out = os.path.join(TMP, 'sf_out'); buf = io.StringIO()
    done, left = TB.split(d, pdir, 'pl', out, stream=buf)
    top = open(os.path.join(out, 'INDEX.md'), encoding='utf8').read()
    assert done == 0 and left == [], (done, left)                                            # 실패 길: 실패한 책을 '이번 실행' 에 세지 않는다
    assert '(실패 — ' in top and '장 표가 비었다' in top and '(남음)' not in top, top
    assert '이번 실행 0권 · 실패 1권 · 남은 책 0권' in top, top
    assert not os.path.exists(os.path.join(out, '01_h book', 'INDEX.md'))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    cli = [sys.executable, os.path.join(HERE, 'textbook.py'), 'split', d, '--plan-dir', pdir, '--plan-name', 'pl', '--out', out]
    r = subprocess.run(cli, capture_output=True, text=True, env=env)
    assert r.returncode == 1 and '실패 1권' in r.stdout, (r.returncode, r.stdout[-400:], r.stderr[-300:])
    open(pf, 'w', encoding='utf8').write(good)                                                   # 성공 길: 장 표를 고치고 같은 명령
    r = subprocess.run(cli, capture_output=True, text=True, env=env)
    assert r.returncode == 0 and '이번 실행 1권 · 실패 0권 · 남은 책 0권' in r.stdout, (r.returncode, r.stdout[-400:])
    assert '(실패' not in open(os.path.join(out, 'INDEX.md'), encoding='utf8').read()


def t_v072_split_noplan_and_budget():
    """장 표 없음(plan 오류)은 '장 표 없음' 으로, 예산을 넘긴 책은 '남음' 으로 — 실패와 섞지 않는다."""
    d, pdir = _split_setup('sb')
    import shutil
    shutil.copy(os.path.join(d, 'h book.pdf'), os.path.join(d, 'k book.pdf'))
    shutil.copy(os.path.join(pdir, 'pl_01.md'), os.path.join(pdir, 'pl_02.md'))
    out = os.path.join(TMP, 'sb_out')
    done, left = TB.split(d, pdir, 'pl', out, budget=0, stream=io.StringIO())                     # 첫 책은 늘 한다, 둘째는 예산 넘김
    top = open(os.path.join(out, 'INDEX.md'), encoding='utf8').read()
    assert done == 1 and left == ['k book.pdf'], (done, left)
    assert '| 02 | k book | (남음) |' in top and '실패 0권 · 남은 책 1권' in top, top
    pf2 = os.path.join(pdir, 'pl_02.md'); t = open(pf2, encoding='utf8').read()
    open(pf2, 'w', encoding='utf8').write(t.replace('error=no', 'error=yes', 1))
    done, left = TB.split(d, pdir, 'pl', out, stream=io.StringIO())
    top = open(os.path.join(out, 'INDEX.md'), encoding='utf8').read()
    assert done == 0 and '| 02 | k book | (장 표 없음) |' in top and '실패 0권 · 남은 책 0권' in top, top



def t_v08_three_digit_rows():
    # v0.8 (10-04 Gore 100–127장): 장 표의 세 자리 장 번호도 읽는다 — 전에는 정규식 \d\d 가 100장 이상 28줄을 조용히 버렸다
    fp = os.path.join(TMP, 'pl3.md')
    open(fp, 'w', encoding='utf8').write('\n'.join([
        '| 장 | 제목 | PDF 시작 | PDF 끝 | 쪽 수 | 인쇄 쪽 | 근거 |', '|---|---|---|---|---|---|---|',
        '| 99 | Ninety | 10 | 19 | 10 | 8–17 | 책갈피 |',
        '| 100 | Pancreas | 20 | 29 | 10 | 18–27 | 책갈피 |',
        '| 127 | Monitoring | 30 | 39 | 10 | 28–37 | 책갈피 |',
        '| 1000 | Noise | 40 | 41 | 2 | — | 잡음 |', '| 1 | Noise | 42 | 43 | 2 | — | 잡음 |', '']))
    rows = TB.read_plan_rows(fp)
    assert [r[0] for r in rows] == [99, 100, 127], rows                                     # 네 자리·한 자리는 여전히 안 읽음
    assert rows[1] == (100, 'Pancreas', 20, 29, 2), rows
    assert [x[0] for x in TB.split_units(rows, 50)] == ['99_Ninety.md', '100_Pancreas.md', '127_Monitoring.md']


def t_v08_named_long_chapter():
    # v0.8 (10-04 신경영상의학 11장 150쪽): 책갈피·사람이 만든 장 표는 긴 장도 장 이름으로 — 쪽 머리로 만든 장 표만 '미확인'
    rows = [(k, 'T%d' % k, 1 + (k - 1) * 10, k * 10, 0) for k in range(1, 6)] + [(6, 'Long', 51, 200, 0)]
    named = [x[0] for x in TB.split_units(rows, 200, named=True)]
    assert named[5:] == ['06_Long_1.md', '06_Long_2.md', '06_Long_3.md', '06_Long_4.md', '06_Long_5.md'], named
    auto = [x[0] for x in TB.split_units(rows, 200)]
    assert '06_Long_1.md' in auto and '06_미확인_p81-110.md' in auto and '06_Long_2.md' not in auto, auto
    for head, want in [('method=책갈피 (깊이 1) chapters=6', True), ('method=쪽 머리 chapters=6', False),
                       ('method=사람 확인 chapters=6', True)]:
        fp = os.path.join(TMP, 'pm.md')
        open(fp, 'w', encoding='utf8').write('<!-- plan: %s check=0 pages=200 seconds=1 error=no -->\n# x\n' % head)
        assert TB.plan_named(fp) is want, head


def t_v08_ocr_heads_and_lone_opener():
    # v0.8 (10-04 신경영상의학 — 10장부터 끝까지 못 찾음): '제'→'세' OCR · 쪽 머리가 한 번만 잡힌 짧은 장
    assert 11 in TB.page_marks('I세111 장 증강 I 295 ////')['head']
    assert TB.page_marks('저129 잠  동정맥루의혈관내치료')['head'] == {29}
    assert TB.page_marks('저12 8 장  동맥류의혈관내치료')['head'] == {28}
    assert TB.page_marks('세 장의 사진을 비교한다')['head'] == set()
    # 9장 쪽 머리 여럿 → 10장은 여는 쪽 한 번뿐(13쪽 장) → 11장 여는 쪽, 다음 쪽 머리는 44쪽 뒤 → 12장
    spec = {1: ({9},) + ((), ''), 3: ({9},) + ((), ''), 5: ({9},) + ((), ''), 10: ({10},) + ((), ''),
            23: ({11},) + ((), ''), 67: ({11},) + ((), ''), 100: ({12},) + ((), ''), 104: ({12},) + ((), '')}
    chs, _ = TB.resolve_chapters(_marks(spec, 120))
    assert [(c['num'], c['first'] + 1) for c in chs] == [(9, 1), (10, 10), (11, 23), (12, 100)], chs
    # 실패 쪽: 장 안의 잡음 한 번(c+1)은 다음 쪽 머리가 다시 c 면 받지 않는다
    spec = {1: ({3},) + ((), ''), 3: ({3},) + ((), ''), 5: ({3},) + ((), ''), 8: ({4},) + ((), ''), 30: ({3},) + ((), ''),
            40: ({4},) + ((), ''), 42: ({4},) + ((), '')}
    chs, _ = TB.resolve_chapters(_marks(spec, 60))
    assert [(c['num'], c['first'] + 1) for c in chs] == [(3, 1), (4, 40)], chs


def t_v081_dropped_plan_rows():
    # v0.8.1 (대기열 10-04 — Gore 100–127장이 조용히 사라진 일): 장 표 모양인데 읽지 못한 줄은 버리되 경고한다
    d, pdir = _split_setup('dr')
    pf = os.path.join(pdir, 'pl_01.md')
    s = open(pf, encoding='utf8').read()
    assert s.count('| 02 |') == 1, s
    open(pf, 'w', encoding='utf8').write(s.replace('| 02 |', '| 2 |'))                     # 사람이 손으로 고치다 한 자리로
    dr = TB.plan_dropped(pf)
    assert len(dr) == 1 and dr[0][1].startswith('| 2 | Kidney |'), dr
    buf = io.StringIO(); out = os.path.join(TMP, 'dr_out')
    TB.split(d, pdir, 'pl', out, stream=buf)
    assert '[경고] 장 표 줄 1개를 읽지 못해 버림' in buf.getvalue(), buf.getvalue()
    ix = open(os.path.join(out, '01_h book', 'INDEX.md'), encoding='utf8').read()
    assert '[경고] 장 표에서 읽지 못해 버린 줄 1개' in ix and '| 2 | Kidney |' in ix, ix
    assert '02_Kidney.md' not in os.listdir(os.path.join(out, '01_h book'))               # 버린 장은 여전히 안 나뉨(경고만)
    # 성공 쪽: 고치지 않은 장 표는 경고 없음 · 머리줄·구분줄·다른 표는 버린 줄로 세지 않음
    d2, pdir2 = _split_setup('dr2')
    assert TB.plan_dropped(os.path.join(pdir2, 'pl_01.md')) == []
    buf2 = io.StringIO(); out2 = os.path.join(TMP, 'dr2_out')
    TB.split(d2, pdir2, 'pl', out2, stream=buf2)
    assert '[경고]' not in buf2.getvalue()
    assert '[경고]' not in open(os.path.join(out2, '01_h book', 'INDEX.md'), encoding='utf8').read()
    assert TB.plan_dropped(os.path.join(TMP, '없는_파일.md')) == []


def t_v081_plan_empty_title_row():
    # v0.8.1 (10-04 인터벤션 11장): 쪽 머리 제목이 비면 plan 이 '| 11 |  | 143 |' 줄을 썼고 split 이 그 줄을 조용히 버렸다
    ch = lambda num, title, a, b: {'num': num, 'title': title, 'start': a - 1, 'end': b - 1, 'pages_n': b - a + 1, 'printed': '—', 'why': '쪽 머리만'}
    r = {'method': '쪽 머리', 'chapters': [ch(10, 'Balloon', 1, 14), ch(11, '', 15, 18), ch(12, '  ', 19, 30)], 'checks': [], 'pages': 30,
         'seconds': 1, 'error': None, 'depths': {}, 'labels': None}
    fp = os.path.join(TMP, 'empty_title.md')
    open(fp, 'w', encoding='utf8').write(TB.plan_md(1, 'x.pdf', r, 'pl'))
    rows = TB.read_plan_rows(fp)
    assert [x[0] for x in rows] == [10, 11, 12], rows                                       # 빈 제목 장도 읽힌다
    assert rows[1][1] == rows[2][1] == '(제목 못 읽음)' and rows[0][1] == 'Balloon', rows
    assert TB.plan_dropped(fp) == []

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
