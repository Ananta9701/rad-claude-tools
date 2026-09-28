#!/usr/bin/env python3
"""literature.py 테스트 — python3 test_literature.py. fixture PDF 는 pypdf 로 만든다(가짜 논문, 영어)."""
import io
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import literature as LT          # noqa: E402

EXPECT_VERSION = '0.3'
TMP = tempfile.mkdtemp(prefix='tlt_')


def _manifest_version(fname):
    p = os.path.join(HERE, 'TOOLS_MANIFEST.md')
    if not os.path.exists(p):
        return None
    m = re.search(r'\| `%s` \| v([0-9.]+)' % re.escape(fname), open(p, encoding='utf8').read())
    return m.group(1) if m else None


def make_pdf(path, pages):
    pypdf = LT.load_pypdf()
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
    w = pypdf.PdfWriter()
    font = w._add_object(DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'),
                                           NameObject('/BaseFont'): NameObject('/Helvetica')}))
    for lines in pages:
        pg = w.add_blank_page(612, 792)
        body = ['BT', '/F1 10 Tf', '12 TL', '72 740 Td'] + ['(%s) Tj T*' % l.replace('(', r'\(').replace(')', r'\)') for l in lines] + ['ET']
        s = DecodedStreamObject(); s.set_data('\n'.join(body).encode('latin-1'))
        pg[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): font})})
        pg[NameObject('/Contents')] = w._add_object(s)
    with open(path, 'wb') as f:
        w.write(f)


INSTR = """# 검증지시 — 시험 원고 v1

> 원고: 시험 원고 v1

## 참고문헌

1. Smith J, Lee K. Diffusion weighted imaging of liver lesions. Radiology. 2020;295:100-110. doi:10.1000/abc123.
2. Park S, Kim H. Contrast enhanced ultrasound in renal masses. AJR. 2019;212:50-60. https://doi.org/10.1000/XYZ456 PMID: 31234567
3. Chen L, Wang Y. Machine learning prediction of fracture healing outcomes. Eur Radiol. 2021;31:1-9.
4. Jones A. Unavailable old paper about something. J Old. 1998;1:1-2. PMC1234567

## 확인할 주장

| 주장 | 문헌 | 원고 문장(짧게) | 찾을 말 |
|---|---|---|---|
| C1 | 1 | DWI 민감도 92% | sensitivity, 92% |
| C2 | 3, 4 | 예측 정확도 | accuracy, fracture healing |
"""


def _write(path, text):
    open(path, 'w', encoding='utf8').write(text)
    return path


def _fixture():
    d = os.path.join(TMP, 'fx_%d' % len(os.listdir(TMP))); os.makedirs(os.path.join(d, 'inbox'))
    instr = _write(os.path.join(d, 'instr.md'), INSTR)
    make_pdf(os.path.join(d, 'inbox', '001_Smith_2020.pdf'), [
        ['Diffusion weighted imaging of liver lesions', 'Abstract. We studied 120 patients.'],
        ['Results. The sensitivity of DWI was 92 % for malignant lesions.', '', 'Specificity was 85%.']])
    make_pdf(os.path.join(d, 'inbox', 'download (3).pdf'), [['Contrast enhanced ultrasound in renal masses', 'doi: 10.1000/xyz456'], ['body text']])
    make_pdf(os.path.join(d, 'inbox', 'article.pdf'), [
        ['Machine learning prediction of fracture healing outcomes'], ['The model accuracy for fracture healing was 0.87 in the test set.']])
    make_pdf(os.path.join(d, 'inbox', 'unrelated.pdf'), [['Completely different topic about cardiac valves'], ['nothing']])
    return d, instr


def t_version():
    assert LT.__version__ == EXPECT_VERSION
    mv = _manifest_version('literature.py')
    assert mv is None or mv == LT.__version__, ('manifest', mv)
    assert 'v%s' % LT.__version__ in open(os.path.join(HERE, 'LITERATURE.md'), encoding='utf8').readline()


def t_parse():
    refs = LT.parse_refs(INSTR)
    assert [r['n'] for r in refs] == [1, 2, 3, 4]
    assert refs[0]['doi'] == '10.1000/abc123' and refs[1]['doi'] == '10.1000/xyz456' and refs[1]['pmid'] == '31234567'
    assert refs[2]['doi'] is None and refs[3]['pmc'] == 'PMC1234567' and refs[0]['author'] == 'Smith' and refs[0]['year'] == '2020'
    assert refs[2]['title'].startswith('Machine learning prediction')
    cl = LT.parse_claims(INSTR)
    assert [(c['id'], c['refs']) for c in cl] == [('C1', [1]), ('C2', [3, 4])] and cl[0]['terms'] == ['sensitivity', '92%']
    assert LT.save_name(refs[0]) == '001_Smith_2020.pdf' and LT.manuscript_name(INSTR, 'x.md') == '시험_원고_v1'


def t_plan_ingest_locate():
    d, instr = _fixture()
    store, out = os.path.join(d, 'store'), os.path.join(d, 'out')
    fp = LT.plan(instr, out, store, stream=io.StringIO())
    p = open(fp, encoding='utf8').read()
    assert 'https://doi.org/10.1000/abc123' in p and '(안 되면) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/' in p
    assert 'pubmed.ncbi.nlm.nih.gov/31234567' not in p                   # v0.2: DOI 가 있으면 PubMed 로 보내지 않는다(캡차)
    assert '`001_Smith_2020.pdf`' in p and 'PubMed 에서 제목으로: Machine learning' in p and '받을 것: 4편' in p
    got, unmatched = LT.ingest(instr, os.path.join(d, 'inbox'), store, out, stream=io.StringIO())
    assert got[1][1] == '파일 이름' and got[2][1] == 'DOI' and got[3][1].startswith('제목') and 4 not in got, got
    assert unmatched == [('unrelated.pdf', '짝 없음')], unmatched
    k1 = got[1][0]
    assert k1 == '10.1000_abc123' and got[3][0].startswith('nodoi_')
    md = open(os.path.join(store, k1, 'paper.md'), encoding='utf8').read()
    assert '[p.1]' in md and '[p.2]' in md and 'sensitivity of DWI' in md
    lst = open(os.path.join(out, '시험_원고_v1_문헌목록.md'), encoding='utf8').read()
    assert '| 4 | Jones 1998 | — | **못 받음** |' in lst and '받음 3 / 4' in lst, lst
    assert 'INDEX' in open(os.path.join(store, 'INDEX.md'), encoding='utf8').read()
    # 다른 원고가 같은 문헌을 인용 — 다시 받지 않고 보관소 것을 쓴다
    other = _write(os.path.join(d, 'instr2.md'), INSTR.replace('시험 원고 v1', '다른 원고'))
    empty = os.path.join(d, 'inbox2'); os.makedirs(empty)
    assert '있음 `10.1000_abc123`' in open(LT.plan(other, out, store, stream=io.StringIO()), encoding='utf8').read()
    got2, _ = LT.ingest(other, empty, store, out, stream=io.StringIO())
    meta = open(os.path.join(store, k1, 'meta.md'), encoding='utf8').read()
    assert '- 인용: 시험_원고_v1 참고문헌 1' in meta and '- 인용: 다른_원고 참고문헌 1' in meta, meta
    # 주장별 후보 — 판정은 하지 않는다
    fp = LT.locate(instr, store, out, stream=io.StringIO())
    loc = open(fp, encoding='utf8').read()
    assert '[p.2] 맞은 말 2/2(sensitivity, 92%)' in loc, loc                # '92 %' 도 띄어쓰기 무시로
    assert '**원문 전체에서 0회: 없음' in loc and '"sensitivity" → [p.2]' in loc and '"92%" → 위와 같은 문단 [p.2]' in loc, loc
    assert re.search(r'문헌 3 `nodoi_[0-9a-f]+/paper.md`:\n  - \*\*원문 전체에서 0회: 없음', loc), loc
    assert '문헌 4: **원문 없음**' in loc and re.search(r'문헌 3 `nodoi_[0-9a-f]+/paper.md`', loc), loc
    assert '판정은 리뷰어가' in loc


def t_v02_zero_terms_and_check():
    d, instr = _fixture()
    store, out = os.path.join(d, 'store'), os.path.join(d, 'out')
    LT.ingest(instr, os.path.join(d, 'inbox'), store, out, stream=io.StringIO())
    ins2 = _write(os.path.join(d, 'i2.md'), INSTR.replace('| C1 | 1 | DWI 민감도 92% | sensitivity, 92% |', '| C1 | 1 | DWI 민감도 97% | sensitivity, 97%, PPV |'))
    loc = open(LT.locate(ins2, store, out, stream=io.StringIO()), encoding='utf8').read()
    assert '**원문 전체에서 0회: 97%, PPV**' in loc, loc                      # 원고의 말이 원문에 없다 — 가장 강한 신호
    ib = os.path.join(d, 'inbox'); open(os.path.join(ib, '004_Jones_1998.pdf'), 'w').write('<html>viewer</html>')
    make_pdf(os.path.join(ib, '002_Park_2019.pdf'), [['Other paper', 'doi: 10.9999/other'], ['x']])
    make_pdf(os.path.join(ib, '003_Chen_2021.pdf'), [['single page only']])
    rows = {f: (r, why) for f, r, why in LT.check(instr, ib, out, stream=io.StringIO())}
    assert rows['004_Jones_1998.pdf'][0] == '✗' and 'PDF 가 아니다' in rows['004_Jones_1998.pdf'][1]
    assert rows['003_Chen_2021.pdf'][0] == '✗' and '쪽 수 1' in rows['003_Chen_2021.pdf'][1]
    assert rows['002_Park_2019.pdf'][0] == '△' and '다른 논문' in rows['002_Park_2019.pdf'][1]
    assert rows['001_Smith_2020.pdf'][0] == '△' and 'DOI 가 없다' in rows['001_Smith_2020.pdf'][1], rows   # 앞쪽에 DOI 없는 논문
    assert rows['download (3).pdf'][0] == '○' and '참고문헌 2(DOI)' in rows['download (3).pdf'][1], rows        # 사용자가 받은 이름도 DOI 로
    assert rows['unrelated.pdf'][0] == '△' and '짝짓지 못함' in rows['unrelated.pdf'][1]
    assert os.path.exists(os.path.join(out, '시험_원고_v1_받은파일검사.md'))


def t_v02_strip_publisher_boiler():
    d = os.path.join(TMP, 'bp'); os.makedirs(os.path.join(d, 'inbox'))
    instr = _write(os.path.join(d, 'i.md'), INSTR)
    notice = 'Downloaded from https://onlinelibrary.wiley.com/doi/10.1000/xyz456 by Some Institution, Wiley Online Library on [01/01/2026].'
    make_pdf(os.path.join(d, 'inbox', 'NMR - 2019 - Park - Contrast enhanced ultrasound.pdf'), [
        ['Contrast enhanced ultrasound in renal masses', notice, 'See the Terms and Conditions (https://example) on Wiley Online Library for rules of use'],
        ['Results were good.', notice]])
    got, _ = LT.ingest(instr, os.path.join(d, 'inbox'), os.path.join(d, 's'), os.path.join(d, 'o'), stream=io.StringIO())
    assert got[2][1] == 'DOI', got                                             # 이름이 달라도 안내 줄의 DOI 로
    md = open(os.path.join(d, 's', got[2][0], 'paper.md'), encoding='utf8').read()
    assert 'Downloaded from' not in md and 'Some Institution' not in md and 'Results were good.' in md and '안내 줄 3개를 뺐다' in md, md


def t_v03_check_text_layer_and_md_pages():
    d, instr = _fixture()
    store, out = os.path.join(d, 'store'), os.path.join(d, 'out')
    got, _ = LT.ingest(instr, os.path.join(d, 'inbox'), store, out, stream=io.StringIO())
    meta = open(os.path.join(store, got[1][0], 'meta.md'), encoding='utf8').read()
    assert '- 원 PDF: sha256 앞 16자' in meta and '2쪽 · 글자층 없는 쪽 0 · paper.md 쪽 표지 2' in meta, meta
    rows = {f: (r, w) for f, r, w in LT.check(instr, os.path.join(d, 'inbox'), stream=io.StringIO(), store=store)}
    assert rows['download (3).pdf'][0] == '○' and 'paper.md 쪽 표지 2 = 쪽 수' in rows['download (3).pdf'][1], rows
    mdp = os.path.join(store, got[2][0], 'paper.md'); t = open(mdp, encoding='utf8').read()
    open(mdp, 'w', encoding='utf8').write(t[:t.index('\n[p.2]')])                 # md 가 잘린 꼴
    rows = {f: (r, w) for f, r, w in LT.check(instr, os.path.join(d, 'inbox'), stream=io.StringIO(), store=store)}
    assert rows['download (3).pdf'][0] == '✗' and 'md 가 잘렸다' in rows['download (3).pdf'][1], rows
    make_pdf(os.path.join(d, 'inbox', '002_scan.pdf'), [[], [], ['x']])           # 3쪽 중 2쪽 글자층 없음
    rows = {f: (r, w) for f, r, w in LT.check(instr, os.path.join(d, 'inbox'), stream=io.StringIO())}
    assert rows['002_scan.pdf'][0] == '✗' and 'PDF 필요' in rows['002_scan.pdf'][1], rows


def t_cli():
    d, instr = _fixture()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'literature.py'), 'plan', instr, '--out', os.path.join(d, 'o')],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0 and '받을 목록' in r.stdout, r.stderr[-300:]
    r = subprocess.run([sys.executable, os.path.join(HERE, 'literature.py'), 'ingest', instr, '--inbox', os.path.join(d, 'nope'),
                        '--store', os.path.join(d, 's'), '--out', os.path.join(d, 'o')], capture_output=True, text=True, env=env)
    assert r.returncode != 0 and 'inbox' in (r.stdout + r.stderr)


if __name__ == '__main__':
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith('t_') and callable(v)]
    try:
        LT.load_pypdf()
    except SystemExit as e:
        print(str(e)); print('\n통과 0 / 건너뜀 0 / 실패 %d  (전체 %d)' % (len(tests), len(tests))); sys.exit(1)
    ok = fail = 0
    for name, fn in tests:
        try:
            fn(); ok += 1; print('PASS %s' % name[2:])
        except Exception as e:
            fail += 1; print('FAIL %-40s %s: %s' % (name[2:], type(e).__name__, str(e)[:300]))
    print('\n통과 %d / 건너뜀 0 / 실패 %d  (전체 %d)' % (ok, fail, ok + fail))
    sys.exit(1 if fail else 0)
