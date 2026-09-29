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

EXPECT_VERSION = '0.8.4'
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
    assert '[p.— · PDF 1]' in md and '[p.— · PDF 2]' in md and 'sensitivity of DWI' in md
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
    assert '[p.— · PDF 2] 맞은 말 2/2(sensitivity, 92%)' in loc, loc                # '92 %' 도 띄어쓰기 무시로
    assert '**원문 전체에서 0회: 없음' in loc and '"sensitivity" → [p.— · PDF 2]' in loc and '"92%" → 위와 같은 문단 [p.— · PDF 2]' in loc, loc
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
    open(mdp, 'w', encoding='utf8').write(t[:t.index('\n[p.— · PDF 2]')])                 # md 가 잘린 꼴
    rows = {f: (r, w) for f, r, w in LT.check(instr, os.path.join(d, 'inbox'), stream=io.StringIO(), store=store)}
    assert rows['download (3).pdf'][0] == '✗' and 'md 가 잘렸다' in rows['download (3).pdf'][1], rows
    make_pdf(os.path.join(d, 'inbox', '002_scan.pdf'), [[], [], ['x']])           # 3쪽 중 2쪽 글자층 없음
    rows = {f: (r, w) for f, r, w in LT.check(instr, os.path.join(d, 'inbox'), stream=io.StringIO())}
    assert rows['002_scan.pdf'][0] == '✗' and 'PDF 필요' in rows['002_scan.pdf'][1], rows


JATS = b"""<?xml version="1.0"?><article><front><article-meta><title-group><article-title>Contrast enhanced ultrasound in renal masses</article-title></title-group>
<abstract><p>We studied renal masses.</p></abstract></article-meta></front><body>
<sec><title>Results</title><p>Sensitivity was 88% for F<sub>ISF</sub> maps.</p>
<table-wrap><label>Table 1</label><caption><p>Accuracy</p></caption><table><tr><th>Group</th><th>AUC</th></tr><tr><td>A</td><td>&#8722;0.63</td></tr></table></table-wrap>
</sec></body></article>"""


def t_v04_oa_api_and_zero_loose_and_mathfont():
    import json
    d, instr = _fixture()
    store, out = os.path.join(d, 'store'), os.path.join(d, 'out')
    calls = []
    def fake_get(url, timeout=30):
        calls.append(url)
        if 'unpaywall' in url:
            return json.dumps({'best_oa_location': {'url_for_pdf': 'https://example.org/x.pdf'}} if 'xyz456' in url else {'best_oa_location': None}).encode()
        if 'search?query=DOI' in url:
            return json.dumps({'resultList': {'result': [{'pmcid': 'PMC7654321', 'isOpenAccess': 'Y', 'inEPMC': 'Y'}]}} if 'xyz456' in url else {'resultList': {'result': []}}).encode()
        if 'fullTextXML' in url:
            return JATS
        raise AssertionError(url)
    try:
        LT.oa(instr, None, store, out, getter=fake_get, sleep=0, stream=io.StringIO()); assert False
    except SystemExit as e:
        assert 'email' in str(e)
    res = dict(LT.oa(instr, 'me@example.invalid', store, out, fetch=True, getter=fake_get, sleep=0, stream=io.StringIO()))
    assert res == {1: 'none', 2: 'xml', 3: 'nodoi', 4: 'nodoi'}, res
    md = open(os.path.join(store, '10.1000_xyz456', 'paper.md'), encoding='utf8').read()
    assert '[§ Results]' in md and '| A | −0.63 |' in md and ('F ISF' in md or 'FISF' in md), md     # 표가 행 그대로, 음수 부호 그대로
    assert 'Europe PMC 전문 XML(PMC7654321)' in md and os.path.exists(os.path.join(store, '10.1000_xyz456', 'paper.xml'))
    assert all('email=me@example.invalid' in c for c in calls if 'unpaywall' in c)
    # 보관소에 있으면 다시 조회하지 않는다
    calls.clear(); res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=fake_get, sleep=0, stream=io.StringIO()))
    assert res[2] == 'have' and not any('xyz456' in c for c in calls)
    # 0회 거짓 양성: F_ISF 를 찾을 말로 — 원문에는 'F ISF'(첨자 분리) → 표기 차이 표시
    ins2 = _write(os.path.join(d, 'i3.md'), INSTR.replace('| C2 | 3, 4 | 예측 정확도 | accuracy, fracture healing |', '| C2 | 2 | 기호 | F_ISF, 88% |'))
    loc = open(LT.locate(ins2, store, out, stream=io.StringIO()), encoding='utf8').read()
    assert 'F_ISF(표기 차이로 0회일 수 있음 — 밑줄·하이픈·공백 무시하면 1회)' in loc, loc
    # 수식 글꼴 치환 표시
    assert LT.mathfont_count('a ¼ b þ c ðxÞ') == 4


def t_v06_locate_section_markers():
    # 코드 리뷰 09-28 ⑪: oa 로 받은 paper.md(쪽 표지 없이 절 표지 [§ …])에서 locate 가 후보 문단을 하나도 내지 못했다
    import json
    d, instr = _fixture()
    store, out = os.path.join(d, 'store'), os.path.join(d, 'out')
    def fake_get(url, timeout=30):
        if 'unpaywall' in url:
            return json.dumps({'best_oa_location': None}).encode()
        if 'search?query=DOI' in url:
            return json.dumps({'resultList': {'result': [{'pmcid': 'PMC7654321', 'isOpenAccess': 'Y', 'inEPMC': 'Y'}]}} if 'xyz456' in url else {'resultList': {'result': []}}).encode()
        return JATS
    LT.oa(instr, 'me@example.invalid', store, out, fetch=True, getter=fake_get, sleep=0, stream=io.StringIO())
    ins = _write(os.path.join(d, 'i6.md'), INSTR.replace('| C2 | 3, 4 | 예측 정확도 | accuracy, fracture healing |', '| C2 | 2 | 민감도 | Sensitivity, 88% |'))
    loc = open(LT.locate(ins, store, out, stream=io.StringIO()), encoding='utf8').read()
    part = loc[loc.index('## C2'):]
    assert '[§ Results] 맞은 말 2/2' in part and '찾을 말이 든 문단 없음' not in part, part   # 성공 길: 절 표지로 나눈 후보
    ins2 = _write(os.path.join(d, 'i7.md'), INSTR.replace('| C2 | 3, 4 | 예측 정확도 | accuracy, fracture healing |', '| C2 | 2 | 없는 말 | zzqq |'))
    loc = open(LT.locate(ins2, store, out, stream=io.StringIO()), encoding='utf8').read()
    part = loc[loc.index('## C2'):]
    assert '찾을 말이 든 문단 없음' in part and '원문 전체에서 0회: zzqq' in part, part            # 실패 길: 없는 말은 전처럼


JATS_TABLE = (b'<article><front><article-meta><title-group><article-title>T</article-title></title-group></article-meta></front><body>'
              b'<sec><title>Results</title><table-wrap><label>Table 2</label><caption><p>c</p></caption><table>'
              b'<thead><tr><th rowspan="2">Region</th><th rowspan="2">Side</th><th colspan="2">Variables</th></tr>'
              b'<tr><th>Age</th><th>X</th></tr></thead><tbody>'
              b'<tr><td rowspan="2">Region A</td><td>Lt</td><td>b = 0.1</td><td>p = 0.076<break/>Adj p = 0.319</td></tr>'
              b'<tr><td>Rt</td><td>b = 0.2</td><td>p = 0.417<break/>Adj p = 0.683</td></tr>'
              b'<tr><td>Region B</td><td>Lt</td><td>b = &#x2212;0.3</td><td>p = 0.8</td></tr>'
              b'</tbody></table></table-wrap>'
              b'<table-wrap><label>Table 3</label><table><tr><td rowspan="9">Z</td><td>1</td></tr><tr><td>2</td></tr></table></table-wrap>'
              b'<table-wrap><label>Table 4</label><table><tr><td rowspan="x">Q</td><td>a</td></tr><tr><td>b</td><td>c</td></tr></table></table-wrap>'
              b'</sec></body></article>')


def t_v05_jats_table_spans_and_breaks():
    # v0.5 (코드 09-28 oa 첫 실시험): 세로 병합 칸 뒤 행이 한 칸씩 밀림 · 칸 안 줄바꿈(<break/>)이 붙어 버림(p = 0.076Adj p)
    md = LT.jats_to_md(JATS_TABLE)
    rows = [l for l in md.splitlines() if l.startswith('| ')]
    cells = lambda l: [c.strip() for c in l.strip().strip('|').split('|')]
    t2 = rows[:5]
    # 성공 길: 세로 병합은 행마다 값을 채우고, 가로 병합은 빈 칸으로 열 수를 맞춘다 — 모든 행이 4칸
    assert [len(cells(l)) for l in t2] == [4, 4, 4, 4, 4], t2
    assert cells(t2[0]) == ['Region', 'Side', 'Variables', ''], t2[0]
    assert cells(t2[1]) == ['Region', 'Side', 'Age', 'X'], t2[1]
    assert cells(t2[2]) == ['Region A', 'Lt', 'b = 0.1', 'p = 0.076 / Adj p = 0.319'], t2[2]
    assert cells(t2[3]) == ['Region A', 'Rt', 'b = 0.2', 'p = 0.417 / Adj p = 0.683'], t2[3]
    assert cells(t2[4]) == ['Region B', 'Lt', 'b = \u22120.3', 'p = 0.8'], t2[4]
    assert '0.076Adj' not in md
    # 실패 길: 표보다 긴 rowspan 은 그 표 안에서 끝나고 다음 표로 새지 않는다, 숫자가 아닌 rowspan 은 1 로 본다
    assert cells(rows[5]) == ['Z', '1'] and cells(rows[6]) == ['Z', '2'], rows[5:7]
    assert cells(rows[7]) == ['Q', 'a'] and cells(rows[8]) == ['b', 'c'], rows[7:9]
    assert len(rows) == 9, rows


def t_v07_page_marker_printed_first():
    # 사용자 09-29 (코드 리뷰 ⑩ (가)): 교과서와 같은 [p.인쇄 · PDF N] — 인쇄 쪽을 모르면 —, 같아도 늘 둘 다. 옛 [p.N] md 도 계속 읽는다
    from pypdf import PdfReader, PdfWriter
    d, instr = _fixture()
    src = os.path.join(d, 'inbox', '001_Smith_2020.pdf')
    w = PdfWriter(); w.append(PdfReader(src)); w.set_page_label(0, 1, style='/D', prefix='e', start=11); w.write(src)   # e11, e12 (e-번호 학술지)
    store, out = os.path.join(d, 'store'), os.path.join(d, 'out')
    LT.ingest(instr, os.path.join(d, 'inbox'), store, out, stream=io.StringIO())
    md = open(os.path.join(store, '10.1000_abc123', 'paper.md'), encoding='utf8').read()
    assert '[p.e11 · PDF 1]' in md and '[p.e12 · PDF 2]' in md, md[:600]                      # 성공 길: 쪽 번호 표가 있으면 그 값
    md3 = open(os.path.join(store, [k for k in os.listdir(store) if 'nodoi' in k][0], 'paper.md'), encoding='utf8').read()
    assert '[p.— · PDF 1]' in md3 and not re.search(r'^\[p\.\d+\]$', md3, re.M), md3[:400]        # 표가 없으면 — (줄이지 않음)
    # 옛 형식 호환: 보관소에 이미 있는 [p.N] md(v0.6 까지)도 locate·check 가 그대로 읽는다
    old = re.sub(r'\[p\.[^\]]* · PDF (\d+)\]', r'[p.\1]', md)
    open(os.path.join(store, '10.1000_abc123', 'paper.md'), 'w', encoding='utf8').write(old)
    loc = open(LT.locate(instr, store, out, stream=io.StringIO()), encoding='utf8').read()
    assert '[p.2] 맞은 말 2/2' in loc, loc
    rows = LT.check(instr, os.path.join(d, 'inbox'), store=store, stream=io.StringIO())
    assert not any('잘렸다' in str(r) for r in (rows or [])), rows


JATS_BLOCKS = (b'<article><front><article-meta><title-group><article-title>T</article-title></title-group>'
               b'<abstract><title>Abstract</title><sec><title>Purpose</title><p>Abstract purpose words.</p></sec><sec><p>Untitled psi part.</p></sec></abstract>'
               b'<abstract abstract-type="highlights"><title>Key tau points</title><list><list-item><p>Highlight chi.</p></list-item></list></abstract></article-meta></front><body>'
               b'<p>Body lead paragraph before sections.</p>'
               b'<sec><title>Methods</title>'
               b'<p>Inclusion criteria were:</p>'
               b'<list list-type="bullet"><list-item><p>age alpha over 18</p></list-item>'
               b'<list-item><p>proven beta lesion<list><list-item><p>nested gamma item</p></list-item></list></p></list-item></list>'
               b'<boxed-text><caption><title>Key points</title><p>Box caption rho words.</p></caption><p>Box delta sentence.</p></boxed-text>'
               b'<sec><title>Sub [a] part</title><p>Sub section sigma words here.</p></sec>'
               b'<p>After the box epsilon sentence.</p>'
               b'<p>We measured <disp-formula><mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML"><mml:mi>x</mml:mi></mml:math></disp-formula> and then zeta tail words follow.</p>'
               b'<p>Values are in the table <table-wrap><label>Table 5</label><caption><p>Inline</p></caption><table>'
               b'<tr><td>eta</td><td>0.63</td></tr><tr><td>theta</td><td>12</td></tr></table>'
               b'<table-wrap-foot><fn><p>AUC, area under iota curve.</p></fn></table-wrap-foot></table-wrap> shown here.</p>'
               b'<disp-formula><mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML"><mml:mi>y</mml:mi><mml:mo>=</mml:mo><mml:mtext>kappa</mml:mtext></mml:math></disp-formula>'
               b'<disp-formula><tex-math>\\documentclass{minimal}\\begin{document}upsilon2\\end{document}</tex-math></disp-formula>'
               b'<def-list><def-item><term>ADC</term><def><p>apparent lambda coefficient</p></def></def-item></def-list>'
               b'<custom-block>unknown omega text</custom-block>'
               b'<notes><title>Consent to upsilon</title><p>Not applicable.</p><fn><p>Phi note</p><p>Chi remains</p></fn></notes>'
               b'</sec></body>'
               b'<back><ack><p>We thank mu people.</p></ack>'
               b'<app-group><app><title>Appendix A</title><p>Appendix nu text.</p></app></app-group>'
               b'<ref-list><ref><mixed-citation>Reference xi title words.</mixed-citation></ref></ref-list></back>'
               b'<floats-group><table-wrap><label>Table 6</label><table><tr><td>omicron</td><td>7</td></tr></table></table-wrap>'
               b'<fig><label>Figure 2</label><caption><p>Figure pi caption.</p></caption></fig></floats-group></article>')


def t_v08_jats_blocks_not_dropped():
    # 코드 리뷰 ⑨: 목록·상자 글·부록·문단 안 표·본문 밖 표(floats-group)·수식 뒤 글이 paper.md 에서 빠져 locate 가 거짓 "0회"
    md = LT.jats_to_md(JATS_BLOCKS)
    for w in ('Abstract purpose words', 'Body lead paragraph', 'age alpha over 18', 'proven beta lesion', 'nested gamma item',
              'Box delta sentence', 'After the box epsilon', 'zeta tail words', 'Values are in the table', 'shown here',
              'area under iota curve', 'kappa', 'apparent lambda coefficient', 'unknown omega text', 'We thank mu people',
              'Appendix nu text', 'Figure pi caption', 'Box caption rho words', 'Sub section sigma words'):
        assert w in md, (w, md)                                                            # 성공 길: 글이 모두 남는다
    rows = [l for l in md.splitlines() if l.startswith('| ')]
    assert '| eta | 0.63 |' in rows and '| theta | 12 |' in rows and '| omicron | 7 |' in rows, rows   # 문단 안·본문 밖 표도 행 그대로
    assert '0.6312' not in md and 'eta0.63' not in md, md
    assert '[§ Sub (a) part]' in md, md                                                     # 제목 안 ] 는 ) 로 — locate 가 표지로 나눈다
    assert '[§ Abstract · Key tau points]' in md and '- Highlight chi.' in md, md
    assert 'Abstract · Abstract' not in md and '· 절]' not in md and 'Untitled psi part' in md, md     # v0.8.2 (실제 XML): 초록 제목이 겹치지 않는다
    assert '[§ Abstract · Purpose]' in md and '[§ 부록 · Appendix A]' in md and '[§ 상자 · Key points]' in md, md
    # 상자 뒤 문단은 다시 원래 절 표지 아래에 — 상자 표지가 뒤 문단까지 가져가지 않는다
    before = md[:md.index('After the box epsilon')]
    assert re.findall(r'^\[§ [^\]]*\]$', before, re.M)[-1] == '[§ Methods]', before[-300:]
    # 실패 길: 참고문헌 목록은 넣지 않는다(찾을 말이 참고문헌 제목에만 있으면 거짓 "있음")
    assert 'Reference xi' not in md, md
    assert '[수식: y=kappa]' in md and '[수식: x]' in md and 'documentclass' not in md and 'upsilon2' not in md, md   # 수식은 MathML 글만
    assert 'upsilonNot' not in md and 'noteChi' not in md and 'Phi note Chi remains' in md, md     # 이웃 문단이 띄어쓰기 없이 붙지 않는다(실제 XML)
    assert 'F<sub>' not in md and ('FISF' in LT.jats_to_md(JATS) or 'F ISF' in LT.jats_to_md(JATS))
    # locate 도 새 표지로 나눈 문단을 찾는다
    assert md.count('[§ Methods]') >= 2


def t_v08_locate_ligature_nfkc():
    # 리뷰어 09-29(문헌 Cowork): PDF 글자층의 합자(ﬂ U+FB02, ﬁ U+FB01) 때문에 찾을 말이 "원문 전체 0회" 로 나온 거짓 음성
    d, instr = _fixture()
    store, out = os.path.join(d, 'store'), os.path.join(d, 'out')
    LT.ingest(instr, os.path.join(d, 'inbox'), store, out, stream=io.StringIO())
    mdp = os.path.join(store, '10.1000_abc123', 'paper.md')
    md = open(mdp, encoding='utf8').read()
    lig = md + '\n[p.— · PDF 3]\n\nThe ﬂip angle of the sequence was ﬁxed at baseline in every patient.\n'
    open(mdp, 'w', encoding='utf8').write(lig)
    ins = _write(os.path.join(d, 'i8.md'), INSTR.replace('| C1 | 1 | DWI 민감도 92% | sensitivity, 92% |',
                                                         '| C1 | 1 | 숙임각 | flip angle, fixed, zzqq |'))
    loc = open(LT.locate(ins, store, out, stream=io.StringIO()), encoding='utf8').read()
    part = loc[loc.index('## C1'):loc.index('## C2')]
    assert '원문 전체에서 0회: zzqq' in part, part                                          # 성공 길: 합자로 적힌 말은 0회가 아니다
    assert '[p.— · PDF 3] 맞은 말 2/3' in part, part                                          # 후보 문단으로도 나온다
    assert 'ﬂip angle of the sequence' in part, part                                      # 인용은 원문 글자 그대로(찾기용 사본만 바꿈)
    assert '"flip angle" → [p.— · PDF 3] …The ﬂip angle of the sequence' in part, part   # 찾을 말별 첫 자리도 원문 위치로
    assert open(mdp, encoding='utf8').read() == lig                                            # paper.md 는 그대로
    # 실패 길: 합자 풀기가 없는 말을 만들지 않는다
    assert 'fixed(' not in part and 'zzqq(' not in part, part
    # 제목 짝짓기도 합자를 푼다(ﬁ 가 빠져 'brosis' 로 쪼개지지 않게)
    assert 'fibrosis' in LT._tokens('Liver ﬁbrosis staging')


def t_v08_old_xml_md_reconverted():
    # v0.8: 보관소에 이미 있는 옛 XML 변환 md(목록 등이 빠진 것)는 locate 가 알리고, oa 를 다시 돌리면 paper.xml 에서 네트워크 없이 다시 만든다
    import json
    d, instr = _fixture()
    store, out = os.path.join(d, 'store'), os.path.join(d, 'out')
    def fake_get(url, timeout=30):
        if 'fullTextXML' in url:
            return JATS_BLOCKS
        if 'unpaywall' in url:
            return json.dumps({'best_oa_location': None}).encode()
        return json.dumps({'resultList': {'result': [{'pmcid': 'PMC7654321', 'isOpenAccess': 'Y', 'inEPMC': 'Y'}]}} if 'xyz456' in url else {'resultList': {'result': []}}).encode()
    LT.oa(instr, 'me@example.invalid', store, out, fetch=True, getter=fake_get, sleep=0, stream=io.StringIO())
    dd = os.path.join(store, '10.1000_xyz456'); mdp = os.path.join(dd, 'paper.md')
    assert LT.JATS_MD in open(mdp, encoding='utf8').read() and not LT._xml_md_old(dd)
    old = '# T\n\n> Europe PMC 전문 XML(PMC7654321)에서 — 쪽 표지 대신 절 표지 `[§ …]`.\n\n[§ Methods]\n\nInclusion criteria were:\n'   # v0.7 까지의 모양
    open(mdp, 'w', encoding='utf8').write(old)
    ins = _write(os.path.join(d, 'i9.md'), INSTR.replace('| C2 | 3, 4 | 예측 정확도 | accuracy, fracture healing |', '| C2 | 2 | 목록 | age alpha |'))
    loc = open(LT.locate(ins, store, out, stream=io.StringIO()), encoding='utf8').read()
    assert '옛 XML 변환' in loc and '원문 전체에서 0회: age alpha' in loc, loc                    # 실패 길: 옛 md 는 0회를 믿지 말라고 알린다
    def no_net(url, timeout=30):
        if 'xyz456' in url or 'fullTextXML' in url:
            raise AssertionError('보관소에 있는 문헌을 다시 조회했다: ' + url)
        return fake_get(url)
    res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=no_net, sleep=0, stream=io.StringIO()))
    assert res[2] == 'redo' and 'age alpha over 18' in open(mdp, encoding='utf8').read(), res   # 성공 길: paper.xml 에서 다시 만듦
    loc = open(LT.locate(ins, store, out, stream=io.StringIO()), encoding='utf8').read()
    assert '옛 XML 변환' not in loc and '원문 전체에서 0회: 없음' in loc, loc
    res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=no_net, sleep=0, stream=io.StringIO()))
    assert res[2] == 'have', res                                                                    # 한 번 다시 만든 뒤에는 그대로
    # PDF 로 받은 문헌(paper.xml 없음)은 옛 변환으로 보지 않는다
    LT.ingest(instr, os.path.join(d, 'inbox'), store, out, stream=io.StringIO())
    assert not LT._xml_md_old(os.path.join(store, '10.1000_abc123'))


def t_cli():
    d, instr = _fixture()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'literature.py'), 'plan', instr, '--out', os.path.join(d, 'o')],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0 and '받을 목록' in r.stdout, r.stderr[-300:]
    r = subprocess.run([sys.executable, os.path.join(HERE, 'literature.py'), 'ingest', instr, '--inbox', os.path.join(d, 'nope'),
                        '--store', os.path.join(d, 's'), '--out', os.path.join(d, 'o')], capture_output=True, text=True, env=env)
    assert r.returncode != 0 and 'inbox' in (r.stdout + r.stderr)


def t_v083_oa_lookup_failure_not_none():
    """리뷰어 09-29 2번: 조회 실패(네트워크·차단·이메일 오류)를 'OA 없음' 과 나눈다 — 실패면 다시 조회, 없음이면 브라우저·사용자."""
    import json, urllib.error
    d, instr = _fixture()
    store, out = os.path.join(d, 'store'), os.path.join(d, 'out')
    def down(url, timeout=30):
        raise urllib.error.URLError('connect_rejected')
    buf = io.StringIO()
    res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=down, sleep=0, stream=buf))
    assert res == {1: 'err', 2: 'err', 3: 'nodoi', 4: 'nodoi'}, res                                # 실패 길: 둘 다 막힘
    t = buf.getvalue()
    assert 'OA 없음' not in t and t.count('조회 못 함 — 다시 조회') == 2 and 'URLError' in t, t
    assert '조회 못 함 2편' in t, t
    def up422(url, timeout=30):                                                                    # 한쪽만 실패 + 다른 쪽 '없음' → 아직 모른다
        if 'unpaywall' in url:
            raise urllib.error.HTTPError(url, 422, 'Unprocessable', {}, None)
        if 'search?query=DOI' in url:
            return json.dumps({'resultList': {'result': []}}).encode()
        raise AssertionError(url)
    buf = io.StringIO()
    res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=up422, sleep=0, stream=buf))
    t = buf.getvalue()
    assert res[1] == 'err' and res[2] == 'err', res
    assert 'Unpaywall HTTPError 422' in t and 'OA 없음' not in t, t
    def up_down_ep_ok(url, timeout=30):                                                            # 한쪽 실패여도 찾았으면 찾은 것
        if 'unpaywall' in url:
            raise urllib.error.URLError('x')
        if 'search?query=DOI' in url:
            return json.dumps({'resultList': {'result': [{'pmcid': 'PMC7654321', 'isOpenAccess': 'Y', 'inEPMC': 'Y'}]}} if 'xyz456' in url else {'resultList': {'result': []}}).encode()
        raise AssertionError(url)
    buf = io.StringIO()
    res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=up_down_ep_ok, sleep=0, stream=buf))
    t = buf.getvalue()
    assert res[1] == 'err' and res[2] == 'xml', res
    assert 'Europe PMC 전문 XML(PMC7654321) · (Unpaywall 조회 못 함 URLError — OA PDF 는 모름)' in t, t
    assert '조회 못 함 1편' in t, t
    def ok_none(url, timeout=30):                                                                  # 성공 길: 둘 다 답했고 없음 → OA 없음
        if 'unpaywall' in url:
            return json.dumps({'best_oa_location': None}).encode()
        return json.dumps({'resultList': {'result': []}}).encode()
    buf = io.StringIO()
    res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=ok_none, sleep=0, stream=buf))
    t = buf.getvalue()
    assert res[1] == 'none' and res[2] == 'none', res
    assert t.count('OA 없음 — 브라우저') == 2 and '조회 못 함' not in t, t
    def html200(url, timeout=30):                                                                  # 프록시가 200 으로 HTML 을 주면 조회 실패
        return b'<html>blocked</html>'
    res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=html200, sleep=0, stream=io.StringIO()))
    assert res[1] == 'err', res


def t_v084_oa_unpaywall_404_is_not_lookup_failure():
    """사용자 09-29: Unpaywall 404 = Crossref 에 없는 DOI(다시 조회해도 같음) — '조회 못 함' 에 세지 않고 'DOI 확인 필요' 로 따로."""
    import json, urllib.error
    d, instr = _fixture()
    store, out = os.path.join(d, 'store'), os.path.join(d, 'out')
    def g(code, ep_hit=None, ep_err=False):
        def get(url, timeout=30):
            if 'unpaywall' in url:
                if code == 200:
                    return json.dumps({'best_oa_location': None}).encode()
                raise urllib.error.HTTPError(url, code, 'x', {}, None)
            if ep_err:
                raise urllib.error.URLError('down')
            return json.dumps({'resultList': {'result': [ep_hit] if ep_hit and 'xyz456' in url else []}}).encode()
        return get
    buf = io.StringIO()
    res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=g(404), sleep=0, stream=buf)); t = buf.getvalue()
    assert res[1] == 'baddoi' and res[2] == 'baddoi', res                                        # 404 + Europe PMC 없음
    assert t.count(LT.NOT_IN_UNPAYWALL) == 2 and '조회 못 함' not in t and 'OA 없음' not in t, t
    assert 'Unpaywall 에 없는 DOI 2편' in t and 'AI 가 제안한 DOI' in t, t
    buf = io.StringIO()
    res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=g(404, ep_err=True), sleep=0, stream=buf)); t = buf.getvalue()
    assert res[1] == 'baddoi' and '(Europe PMC 조회 못 함 URLError)' in t and '조회 못 함 2편' not in t, (res, t)   # 404 가 먼저 — DOI 부터 확인
    buf = io.StringIO()
    hit = {'pmcid': 'PMC7654321', 'isOpenAccess': 'Y', 'inEPMC': 'Y'}
    res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=g(404, ep_hit=hit), sleep=0, stream=buf)); t = buf.getvalue()
    assert res[2] == 'xml' and 'Europe PMC 전문 XML(PMC7654321) · (Unpaywall 에 없는 DOI — Crossref 밖일 수 있음)' in t, t
    for code in (422, 500, 503):                                                                   # 404 밖의 HTTP 오류는 그대로 조회 못 함
        buf = io.StringIO()
        res = dict(LT.oa(instr, 'me@example.invalid', store, out, getter=g(code), sleep=0, stream=buf)); t = buf.getvalue()
        assert res[1] == 'err' and 'Unpaywall HTTPError %d' % code in t and '조회 못 함 2편' in t and LT.NOT_IN_UNPAYWALL not in t, (code, t)


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
