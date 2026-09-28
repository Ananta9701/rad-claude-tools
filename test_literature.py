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

EXPECT_VERSION = '0.1'
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
    assert 'https://doi.org/10.1000/abc123' in p and 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/' in p
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
    assert '문헌 4: **원문 없음**' in loc and re.search(r'문헌 3 `nodoi_[0-9a-f]+/paper.md`', loc), loc
    assert '판정은 리뷰어가' in loc


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
