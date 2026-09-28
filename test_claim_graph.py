#!/usr/bin/env python3
"""test_claim_graph.py — claim_graph.py 단독 테스트. deck_toolkit 이 없는 프로젝트(저자·리뷰어)에서 그대로 돈다.

    python test_claim_graph.py      # 실패 0 이어야 함
test_toolkit.py(발표 프로젝트)는 이 파일을 import 해 같은 테스트를 함께 돌린다.
"""
import copy, io, os, subprocess, sys, traceback
sys.dont_write_bytecode = True   # /mnt/project 는 대화창 안에서 쓰기 가능 — __pycache__ 를 남기지 않는다 (v2.3.1)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import claim_graph as CGm


def _manifest_version(fname):
    """같은 폴더의 TOOLS_MANIFEST.md 에 적힌 판. 없으면 None (Z1 이후: EXPECT_VERSION 만 맞추고 manifest 를 안 올린 사고 방지)."""
    import os, re
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TOOLS_MANIFEST.md')
    if not os.path.exists(p):
        return None
    m = re.search(r'\| `%s` \| v([0-9.]+)' % re.escape(fname), open(p, encoding='utf8').read())
    return m.group(1) if m else None

EXPECT_VERSION = '15.8.2'

def t_version_matches_manifest():
    assert getattr(CGm, '__version__', None) == EXPECT_VERSION, (getattr(CGm, '__version__', None), EXPECT_VERSION)
    mv = _manifest_version('claim_graph.py')
    assert mv is None or mv == EXPECT_VERSION, ('TOOLS_MANIFEST.md 의 판', mv, '코드', EXPECT_VERSION)

GRAPH = [
    {'id': 'a', 'statement': 'A', 'evidence': 'e', 'sites': ['slide:7'], 'keys': ['title'],
     'status': 'accepted', 'depends_on': []},
    {'id': 'b', 'statement': 'B', 'evidence': 'e', 'sites': ['notes:7'], 'keys': ['note'],
     'depends_on': [{'id': 'a', 'type': 'premise', 'weight': 1.0}]},
    {'id': 'c', 'statement': 'C', 'evidence': 'e', 'sites': ['notes:8'], 'keys': [],
     'depends_on': [{'id': 'b', 'type': 'context', 'weight': 0.2}]},
]

MD = '/tmp/cg_doc.md'
open(MD, 'w', encoding='utf8').write('''# Results
FA decreased in the lesion group (0.36 vs 0.44, P = 0.014). Therefore marker A loss precedes marker B change.
However, the sample was small (n = 24).
# Discussion
Index X was higher in lesions (Kim et al. 2021).
''')

def _resolve_dict(d):
    return lambda site: d[site]

def t_mapgraph_clean():
    probs, order = CGm.mapgraph(copy.deepcopy(GRAPH), io.StringIO())
    assert not [p for p in probs if not p.startswith('[참고]')], probs
    assert order.index('a') < order.index('b') < order.index('c'), order

def t_mapgraph_unknown_id():
    g = copy.deepcopy(GRAPH); g[1]['depends_on'] = [{'id': 'zzz'}]
    probs, _ = CGm.mapgraph(g, io.StringIO())
    assert any('정의되지 않음' in p for p in probs), probs

def t_mapgraph_cycle_needs_anchor():
    g = copy.deepcopy(GRAPH); g[0]['depends_on'] = [{'id': 'c'}]
    probs, _ = CGm.mapgraph(g, io.StringIO())
    assert any('순환' in p and 'anchor' in p for p in probs), probs
    g[0]['anchor'] = True
    probs, order = CGm.mapgraph(g, io.StringIO())
    assert not any('순환' in p for p in probs), probs
    assert order[0] == 'a', order

def t_mapgraph_superseded_with_sites():
    g = copy.deepcopy(GRAPH); g[2]['status'] = 'superseded'
    probs, _ = CGm.mapgraph(g, io.StringIO())
    assert any('superseded' in p for p in probs), probs

def t_mapgraph_supersedes_needs_forbidden():
    g = copy.deepcopy(GRAPH); g[0]['supersedes'] = {'statement': 'the lesion is far denser than metastasis'}
    probs, _ = CGm.mapgraph(g, io.StringIO())
    hit = [p for p in probs if 'forbidden 이 비어' in p]
    assert hit and not hit[0].startswith('[참고]') and 'far denser' in hit[0], probs
    g[0]['forbidden'] = ['far denser']
    probs, _ = CGm.mapgraph(g, io.StringIO())
    assert not any('forbidden 이 비어' in p for p in probs), probs

def t_mapgraph_role_rules():
    g = copy.deepcopy(GRAPH)
    g[0]['role'] = 'evidence'; g[1]['role'] = 'main'; g[2]['role'] = 'claim'
    probs, _ = CGm.mapgraph(g, io.StringIO())
    assert any('a: evidence 인데 걸린 caveat' in p for p in probs), probs
    assert any('c: role=claim 인데 premise 간선이 없음' in p for p in probs), probs
    assert not any('b: role=main 인데' in p for p in probs), probs
    g[0]['depends_on'] = [{'id': 'c', 'type': 'caveat'}]; g[2]['role'] = 'caveat'
    probs, _ = CGm.mapgraph(g, io.StringIO())
    assert not any('걸린 caveat' in p for p in probs), probs

def t_mapgraph_main_role_count():
    g = copy.deepcopy(GRAPH); g[0]['role'] = 'evidence'
    probs, _ = CGm.mapgraph(g, io.StringIO())
    assert any('role=main' in p for p in probs), probs
    g[1]['role'] = 'main'
    probs, _ = CGm.mapgraph(g, io.StringIO())
    assert not any('role=main 인 주장이' in p for p in probs), probs

def t_impact_propagates_with_weight():
    rows = CGm.impact(copy.deepcopy(GRAPH), ['a'], io.StringIO())
    d = {cid: s for cid, s, _ in rows}
    assert d['b'] == 1.0 and abs(d['c'] - 0.2) < 1e-9, d

def t_impact_stops_on_cycle():
    g = copy.deepcopy(GRAPH); g[0]['depends_on'] = [{'id': 'c'}]; g[0]['anchor'] = True
    rows = CGm.impact(g, ['a'], io.StringIO())
    assert 'a' not in [r[0] for r in rows]

def t_freeze_stale_with_dict_resolver():
    d = {'slide:7': 'title x', 'notes:7': 'note y', 'notes:8': 'z'}
    g = CGm.mapfreeze(_resolve_dict(d), copy.deepcopy(GRAPH), at='2026-01-01')
    assert CGm.mapstale(_resolve_dict(d), g, io.StringIO())['changed'] == []
    d['notes:7'] = 'note y changed'
    r = CGm.mapstale(_resolve_dict(d), g, io.StringIO())
    assert r['changed'] == ['b'] and [x[0] for x in r['suspect']] == ['c'], r
    g[0]['statement'] = 'A changed'
    assert 'a' in CGm.mapstale(_resolve_dict(d), g, io.StringIO())['changed']
    g.append({'id': 'new', 'statement': '', 'sites': []})
    assert CGm.mapstale(_resolve_dict(d), g, io.StringIO())['unverified'] == ['new']

def t_save_load_claims_roundtrip():
    p = '/tmp/claims_rt.json'
    CGm.save_claims(p, copy.deepcopy(GRAPH), deck_name='X', note='n')
    dn, note, cl = CGm.load_claims_meta(p)
    assert dn == 'X' and [c['id'] for c in cl] == ['a', 'b', 'c']
    assert CGm.load_claims(p)[0]['id'] == 'a'

def t_docsource_resolve():
    src = CGm.DocSource(MD)
    assert src.resolve('doc:p:2').startswith('FA decreased')
    assert 'n = 24' in src.resolve('doc:find:sample was small')
    sec = src.resolve('doc:sec:Results')
    assert 'FA decreased' in sec and 'Index X' not in sec
    try:
        src.resolve('doc:find:the'); raise AssertionError('모호한 find 가 통과됨')
    except KeyError:
        pass

def t_extract_candidates_and_edges():
    src = CGm.DocSource(MD)
    c = CGm.extract(src.units(), stream=io.StringIO())
    fa = next(x for x in c if x['statement'].startswith('FA decreased'))
    assert fa['score'] >= 3 and fa['status'] == 'proposed' and fa['origin'] == 'extract'
    th = next(x for x in c if x['statement'].startswith('Therefore'))
    assert th['depends_on'][0]['id'] == fa['id'] and th['depends_on'][0]['type'] == 'premise'
    hw = next(x for x in c if x['statement'].startswith('However'))
    assert hw.get('role') == 'caveat'

def t_extract_skips_reference_lines():
    units = [('doc:p:1', 'Shin JI, et al. Korean J Radiol. 2024;25(1):62-73.'),
             ('doc:p:2', 'References) Gi T, et al.')]
    assert CGm.extract(units, stream=io.StringIO()) == []

def t_scaffold_orders_by_site():
    buf = io.StringIO()
    sites = CGm.scaffold(copy.deepcopy(GRAPH), buf)
    assert set(sites) == {'slide:7', 'notes:7', 'notes:8'} and '[a]' in buf.getvalue()

def t_docx_mapcheck_freeze_stale():
    src = CGm.DocSource(MD)
    cl = [{'id': 'fa', 'statement': 'FA down', 'evidence': 'e', 'sites': ['doc:find:FA decreased'],
           'keys': ['decreased'], 'forbidden': ['increased'], 'depends_on': []},
          {'id': 'cond', 'statement': 'cond up', 'evidence': 'e', 'sites': ['doc:sec:Discussion'],
           'keys': ['higher'], 'depends_on': [{'id': 'fa', 'type': 'premise'}]}]
    probs, _ = CGm.mapcheck(src.resolve, copy.deepcopy(cl), io.StringIO())
    assert not probs, probs
    g = CGm.mapfreeze(src.resolve, copy.deepcopy(cl), at='2026-01-01')
    assert CGm.mapstale(src.resolve, g, io.StringIO())['changed'] == []
    src.paras[1] = src.paras[1].replace('0.36', '0.37')
    r = CGm.mapstale(src.resolve, g, io.StringIO())
    assert r['changed'] == ['fa'] and [x[0] for x in r['suspect']] == ['cond'], r

def _mk_docx(path):
    from docx import Document
    d = Document()
    d.add_paragraph('Abstract').runs[0].bold = True
    d.add_paragraph('Objective: FA decreased (0.36 vs 0.44, P = 0.014).')
    d.add_paragraph('RESULTS')
    d.add_paragraph('Index X was higher in lesions.')
    t = d.add_table(rows=2, cols=2)
    t.cell(0, 0).text = 'Measure'; t.cell(0, 1).text = 'Value'
    t.cell(1, 0).text = 'IDX'; t.cell(1, 1).text = '0.612'
    d.add_paragraph('Limitations').runs[0].bold = True
    d.add_paragraph('The sample was small.')
    d.save(path)

def t_docx_heuristic_headings_and_table():
    p = '/tmp/cg_test.docx'; _mk_docx(p)
    src = CGm.DocSource(p)
    heads = [src.paras[i] for i in sorted(src.headings)]
    assert heads == ['Abstract', 'RESULTS', 'Limitations'], heads
    assert len(src.tables) == 1 and '0.612' in src.resolve('doc:tbl:1')
    assert 'higher in lesions' in src.resolve('doc:sec:RESULTS')
    assert 'Value' not in src.resolve('doc:sec:Limitations')

def t_mapdiff_pairs_by_sites_and_keys():
    a = copy.deepcopy(GRAPH)
    b = [{'id': 'x1', 'sites': ['slide:7'], 'keys': ['title'], 'depends_on': []},
         {'id': 'x2', 'sites': ['notes:7'], 'keys': [], 'depends_on': [{'id': 'x1', 'type': 'support', 'weight': 0.7}]},
         {'id': 'x9', 'sites': ['doc:find:zzz'], 'keys': ['reviewer only'], 'depends_on': []},
         {'id': 'lim', 'sites': ['doc:find:limit'], 'keys': [], 'depends_on': []}]
    b[0]['depends_on'] = [{'id': 'lim', 'type': 'caveat', 'weight': 0.5}]
    r = CGm.mapdiff(a, b, 'A', 'B', io.StringIO())
    assert ('a', 'x1') in r['both'] and ('b', 'x2') in r['both'], r['both']
    assert r['only_a'] == ['c'] and set(r['only_b']) == {'x9', 'lim'}, r
    assert any('premise' in d and 'support' in d for d in r['edge_diff']), r['edge_diff']
    assert any('a/x1' in d for d in r['caveat_diff']), r['caveat_diff']

def t_save_claims_preserves_meta_and_doc_wins():
    # v15.4 (#14): 상위 키 보존, doc 이 stale deck 을 이김
    import json
    p = '/tmp/cg_meta.json'
    json.dump({'deck': 'old_v44', 'doc': 'X_v45.docx', 'version': 'v5', 'protocol': 'v15', 'claims': copy.deepcopy(GRAPH)},
              open(p, 'w', encoding='utf8'))
    meta, cl = CGm.load_claims_full(p)
    assert meta == {'deck': 'old_v44', 'doc': 'X_v45.docx', 'version': 'v5', 'protocol': 'v15'}
    dn, _, _ = CGm.load_claims_meta(p)
    assert dn == 'X_v45.docx', dn   # v15.3 까지는 'old_v44' 가 나왔다
    buf, old = io.StringIO(), sys.stdout; sys.stdout = buf
    try:
        CGm.save_claims(p, cl, meta=meta, doc='/x/y/X_v46__3_.docx')
    finally:
        sys.stdout = old
    d = json.load(open(p, encoding='utf8'))
    assert d['doc'] == 'X_v46' and 'deck' not in d   # v15.4.1: 확장자 없음(규약 §3) and d['version'] == 'v5' and d['protocol'] == 'v15', d.keys()
    assert '[경고]' in buf.getvalue() and 'stale' in buf.getvalue()
    # 덱 경로는 그대로 deck 키
    CGm.save_claims(p, cl, deck_name='D.pptx', note='n')
    d = json.load(open(p, encoding='utf8')); assert d['deck'] == 'D.pptx' and d['note'] == 'n'

def t_norm_name_strips_suffix():
    assert CGm.doc_name('/x/DOC_v47_clean__2_.docx') == 'DOC_v47_clean' and CGm.doc_name('DOC_v47_clean') == 'DOC_v47_clean'
    assert CGm.norm_name('/a/b/claim_graph__8_.py') == 'claim_graph.py'
    assert CGm.norm_name('DOC_v45_clean__1_.docx') == 'DOC_v45_clean.docx'
    assert CGm.norm_name('plain.docx') == 'plain.docx' and CGm.norm_name(None) is None

def t_mapdiff_role_mismatch_excluded_and_manual_pairs():
    # v15.4 (#9): 같은 자리라도 caveat↔evidence 는 짝짓지 않는다; --pairs 로 수동 확정
    a = [{'id': 'pv-5mm', 'role': 'caveat', 'sites': ['doc:find:5 mm'], 'keys': [], 'depends_on': []},
         {'id': 'idx-md', 'role': 'evidence', 'sites': ['doc:find:IDX'], 'keys': ['idx md'], 'depends_on': []}]
    b = [{'id': 'ev-null', 'role': 'evidence', 'sites': ['doc:find:5 mm'], 'keys': [], 'depends_on': []},
         {'id': 'ev-idx-md', 'role': 'evidence', 'sites': ['doc:find:idx'], 'keys': [], 'depends_on': []}]
    r = CGm.mapdiff(a, b, 'A', 'B', io.StringIO())
    assert ('pv-5mm', 'ev-null') not in r['both'] and ('idx-md', 'ev-idx-md') in r['both'], r['both']
    r = CGm.mapdiff(a, b, 'A', 'B', io.StringIO(), pairs={'pv-5mm': 'ev-null'})
    assert ('pv-5mm', 'ev-null') in r['both'] and r['only_a'] == [] and r['only_b'] == [], r
    # role 이 한쪽에만 있으면 종전대로 짝짓는다
    del a[0]['role']
    r = CGm.mapdiff(a, b, 'A', 'B', io.StringIO())
    assert ('pv-5mm', 'ev-null') in r['both']

def t_remap_refs():
    # v15.4 (#4): 매핑 {29:26,30:27,31:28,13:None,12:12}
    cl = [{'id': 'wb', 'statement': 'Prior work [29-31] and [13] agree.', 'evidence': 'refs 29-31',
           'sites': [], 'keys': ['29-31', 'refs 29-31', 'whole brain'], 'depends_on': []},
          {'id': 'n', 'statement': 'n = 200 [12]', 'evidence': '', 'sites': [], 'keys': ['42', '99'], 'depends_on': [],
           'verified': {'at': '2026-01-01'}}]
    refmap = {29: 26, 30: 27, 31: 28, 13: None, 12: 12}
    buf = io.StringIO()
    ch = CGm.remap_refs(copy.deepcopy(cl), refmap, stream=buf)
    c2 = copy.deepcopy(cl); CGm.remap_refs(c2, refmap, stream=io.StringIO())
    assert c2[0]['statement'] == 'Prior work [26-28] and agree.', c2[0]['statement']
    assert c2[0]['keys'] == ['29-31', 'refs 26-28', 'whole brain'], c2[0]['keys']   # 순수 숫자 key 는 절대 보존 (v15.4.1)
    assert c2[1]['statement'] == 'n = 200 [12]' and c2[1]['keys'] == ['42', '99']
    assert '삭제된 문헌' in buf.getvalue() and "순수 숫자 key" in buf.getvalue()
    c4 = copy.deepcopy(cl); buf = io.StringIO(); CGm.remap_refs(c4, {**refmap, 12: 11}, stream=buf)
    assert c4[1]['statement'] == 'n = 200 [11]' and 'mapfreeze' in buf.getvalue()

def t_mapcheck_refs_key_matches_bracket_citation():
    # v15.4.2: `refs 26-28` key 는 자리의 [26-28] / [26–28] / [24,26-28] 인용으로 적중, [26,27] 만 있으면 실패
    texts = {'doc:find:a': 'Prior work [26-28] showed.', 'doc:find:b': 'Prior work [24,26–28] showed.',
             'doc:find:c': 'Prior work [26,27] showed.', 'doc:find:d': 'no citation here'}
    def mk(site, key):
        return [{'id': 'x', 'statement': 's', 'evidence': 'e', 'sites': [site], 'keys': [key], 'depends_on': []}]
    ok = lambda site, key: not [p for p in CGm.mapcheck(_resolve_dict(texts), mk(site, key), io.StringIO())[0] if '반영되지 않음' in p]
    assert ok('doc:find:a', 'refs 26-28') and ok('doc:find:b', 'refs 26-28') and ok('doc:find:a', 'refs: 27')
    assert not ok('doc:find:c', 'refs 26-28') and not ok('doc:find:d', 'refs 26-28')
    assert ok('doc:find:a', 'prior work') and ok('doc:find:a', '26-28') and not ok('doc:find:a', '26-29')   # 리터럴 key 는 종전대로 부분문자열

def t_remap_refs_then_mapcheck_passes():
    # 리뷰어 요청 테스트: remap-refs 적용 후 mapcheck 통과
    texts = {'doc:find:p': 'Previous studies [26-28] reported.'}
    cl = [{'id': 'wb', 'statement': 'reported [29-31]', 'evidence': 'refs 29-31', 'sites': ['doc:find:p'],
           'keys': ['refs 29-31'], 'depends_on': []}]
    CGm.remap_refs(cl, {29: 26, 30: 27, 31: 28}, stream=io.StringIO())
    assert cl[0]['keys'] == ['refs 26-28']
    probs, _ = CGm.mapcheck(_resolve_dict(texts), cl, io.StringIO())
    assert not [p for p in probs if '반영되지 않음' in p], probs

def t_nums_sep_checks_only_prefix():
    # v15.5 리뷰어 요청: evidence "원고 | 재현" 에서 구분자 앞쪽만 --nums
    texts = {'doc:find:p': 'IDX 0.612 vs 0.523 in Table 2.'}
    cl = [{'id': 'x', 'statement': 's', 'evidence': '원고 0.612 vs 0.523 | 재현 0.612 vs 0.523, r 0.843', 'sites': ['doc:find:p'],
           'keys': ['idx'], 'depends_on': []}]
    probs, _ = CGm.mapcheck(_resolve_dict(texts), cl, io.StringIO(), nums=True)
    assert any('0.843' in p for p in probs), probs
    probs, _ = CGm.mapcheck(_resolve_dict(texts), cl, io.StringIO(), nums=True, nums_sep='|')
    assert not [p for p in probs if '수치' in p or '0.843' in p], probs

def t_mapstale_detects_keys_change_only_when_hash_present():
    # v15.5 리뷰어 §2-2: keys_hash 별도 필드 — 구판 freeze 는 무영향
    texts = {'doc:find:p': 'Prior work [26-28] reported.'}
    cl = [{'id': 'wb', 'statement': 's', 'evidence': 'e', 'sites': ['doc:find:p'], 'keys': ['prior work'], 'depends_on': []}]
    CGm.mapfreeze(_resolve_dict(texts), cl)
    assert 'keys' in cl[0]['verified']
    r = CGm.mapstale(_resolve_dict(texts), cl, io.StringIO()); assert r['changed'] == []
    cl[0]['keys'] = ['refs 26-28']
    buf = io.StringIO(); r = CGm.mapstale(_resolve_dict(texts), cl, buf)
    assert r['changed'] == ['wb'] and 'keys 가 바뀜' in buf.getvalue()
    del cl[0]['verified']['keys']            # 구판 freeze 흉내
    r = CGm.mapstale(_resolve_dict(texts), cl, io.StringIO()); assert r['changed'] == []

def t_mapdiff_one_to_many_pairs():
    a = [{'id': 's10', 'role': 'evidence', 'sites': ['doc:find:S10'], 'keys': ['s10'], 'depends_on': []}]
    b = [{'id': 'nested', 'role': 'evidence', 'sites': ['doc:find:nested'], 'keys': [], 'depends_on': []},
         {'id': 'delta-r2', 'role': 'evidence', 'sites': ['doc:find:delta'], 'keys': [], 'depends_on': []}]
    r = CGm.mapdiff(a, b, 'A', 'B', io.StringIO(), pairs={'s10': ['nested', 'delta-r2']})
    assert r['only_a'] == [] and r['only_b'] == [] and r['both'][0][0] == 's10', r
    assert CGm.parse_pairs('s10=nested,s10=delta-r2') == {'s10': ['nested', 'delta-r2']}

def t_mapgraph_keys_forbidden_overlap():
    g = copy.deepcopy(GRAPH)
    g[0]['keys'] = list(g[0].get('keys', [])) + ['수리 권고']; g[0]['forbidden'] = ['수리 권고']; g[0]['supersedes'] = {'statement': 'old'}
    probs, _ = CGm.mapgraph(g, io.StringIO())
    assert any('keys 와 forbidden 에 같은 표현' in p for p in probs), probs

def t_selfcheck():
    import hashlib, shutil, tempfile, subprocess
    d = tempfile.mkdtemp()
    src = os.path.dirname(os.path.abspath(CGm.__file__))
    for f in ('claim_graph.py', 'test_claim_graph.py'):
        shutil.copy(os.path.join(src, f), d)
    h = lambda f: hashlib.sha256(open(os.path.join(d, f), 'rb').read()).hexdigest()[:12]
    man = ('# TOOLS_MANIFEST\n\n**manifest 판: v9 · 릴리스 v9.9 · 2026-01-01**\n\n## 1.\n\n'
           '| 파일 | 판 | 해시 | 테스트 | 크기 |\n|---|---|---|---|---|\n'
           '| `claim_graph.py` | v%s | `%s` | — | 1 |\n| `test_claim_graph.py` | v%s 동반 | `%s` | — | 1 |\n'
           '| `deck_toolkit.py` | v1 | `000000000000` | — | 1 |\n\n'
           '## 2. 배포표\n\n| 파일 | 저자 | 발표 |\n|---|:-:|:-:|\n'
           '| claim_graph.py · test_claim_graph.py | ○ | ○ |\n| deck_toolkit.py | × | ○ |\n'
           '| TOOLS_MANIFEST.md (이 파일) · RELEASE.md | ○ | ○ |\n\n## 3. 절차\n'
           % (CGm.__version__, h('claim_graph.py'), CGm.__version__, h('test_claim_graph.py')))
    open(os.path.join(d, 'TOOLS_MANIFEST.md'), 'w', encoding='utf8').write(man)
    mh = hashlib.sha256(open(os.path.join(d, 'TOOLS_MANIFEST.md'), 'rb').read()).hexdigest()[:12]
    rel_ok = ('# RELEASE v9.9 — manifest v9 — x\n\n<!-- sets:begin -->\n### 저자 (3)\n| 파일 | 판 | 해시 | 변경 |\n|---|---|---|---|\n'
              '| `claim_graph.py` | v%s | `%s` | — |\n| `TOOLS_MANIFEST.md` | v9 | `%s` | ○ |\n<!-- sets:end -->\n' % (CGm.__version__, h('claim_graph.py'), mh))
    open(os.path.join(d, 'RELEASE.md'), 'w', encoding='utf8').write(rel_ok)
    for junk in ('TOOLS_MANIFEST_v3.md', 'x__2_.py', '260910_manifest만_발표_v9.md', 'DOC_v47_claims.json'):
        open(os.path.join(d, junk), 'w').write('x')
    buf = io.StringIO(); r = CGm.selfcheck(d, stream=buf)
    assert r['ok'] and r['project'] == '저자', (r, buf.getvalue())
    assert set(r['delete']) == {'TOOLS_MANIFEST_v3.md', 'x__2_.py', '260910_manifest만_발표_v9.md'} and r['other'] == ['DOC_v47_claims.json'], r
    assert '②′ RELEASE §3 대조' in buf.getvalue()
    # v15.7: --role — 전체 세트(GitHub)처럼 다른 역할 도구가 같이 있어도 역할대로 보고, 안 쓰는 도구는 삭제 후보가 아니다
    open(os.path.join(d, 'deck_toolkit.py'), 'w').write("__version__ = '1'\n")
    buf = io.StringIO(); r = CGm.selfcheck(d, stream=buf, role='저자')
    assert r['project'] == '저자' and 'deck_toolkit.py' not in r['delete'] and '역할(지정)' in buf.getvalue(), (r, buf.getvalue())
    assert CGm.selfcheck(d, stream=io.StringIO(), role='없는역할')['ok'] is False
    # --compare: 예비 폴더와 대조
    d2 = tempfile.mkdtemp()
    for f in ('claim_graph.py', 'TOOLS_MANIFEST.md'):
        shutil.copy(os.path.join(d, f), d2)
    buf = io.StringIO(); CGm.selfcheck(d, stream=buf, role='저자', compare=d2)
    assert '예비 폴더' in buf.getvalue() and '없는 파일 2' in buf.getvalue() and '다름' in buf.getvalue(), buf.getvalue()
    os.remove(os.path.join(d, 'deck_toolkit.py'))
    # v15.8: git 저장소 폴더면 받은 커밋을 적고, .git 은 세트 밖 파일로 잡지 않는다
    r0 = subprocess.run(['git', 'init', '-q', d], capture_output=True)
    if r0.returncode == 0:
        subprocess.run(['git', '-C', d, '-c', 'user.email=t@t', '-c', 'user.name=t', 'add', '-A'], capture_output=True)
        subprocess.run(['git', '-C', d, '-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'x'], capture_output=True)
        buf = io.StringIO(); r = CGm.selfcheck(d, stream=buf, role='저자')
        assert '받은 커밋' in buf.getvalue() and '.git' not in r['other'], buf.getvalue()
    # ②′: manifest 를 바꿔치기하면(자기 기준으로는 ○) RELEASE 대조가 잡는다
    open(os.path.join(d, 'TOOLS_MANIFEST.md'), 'a', encoding='utf8').write('\n<!-- tampered -->\n')
    r = CGm.selfcheck(d, stream=io.StringIO()); assert any('②′ TOOLS_MANIFEST.md' in p for p in r['problems']), r['problems']
    open(os.path.join(d, 'TOOLS_MANIFEST.md'), 'w', encoding='utf8').write(man)
    open(os.path.join(d, 'RELEASE.md'), 'w', encoding='utf8').write('# RELEASE v9.8 — manifest v8 — x\n')
    r = CGm.selfcheck(d, stream=io.StringIO()); assert not r['ok'] and any('1단계' in p for p in r['problems'])
    s = open(os.path.join(d, 'claim_graph.py'), encoding='utf8').read().replace("__version__ = '%s'" % CGm.__version__, "__version__ = '0.0'")
    open(os.path.join(d, 'claim_graph.py'), 'w', encoding='utf8').write(s)
    r = CGm.selfcheck(d, stream=io.StringIO()); assert any('2단계' in p for p in r['problems']) and any('3단계' in p for p in r['problems'])

def t_selfcheck_tests_leave_no_pycache():
    # 리뷰어 v2.3 수령 [결함]: /mnt/project 는 대화창 안에서 쓰기 가능 — selfcheck --tests 가 __pycache__ 를 남겼다
    import hashlib, shutil, tempfile
    d = tempfile.mkdtemp()
    shutil.copy(CGm.__file__, d)
    open(os.path.join(d, 'test_x.py'), 'w').write("EXPECT_VERSION = '1'\nimport sys, os\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\nimport claim_graph\nprint('통과 1 / 실패 0  (전체 1)')\n")
    h = lambda f: hashlib.sha256(open(os.path.join(d, f), 'rb').read()).hexdigest()[:12]
    man = ('**manifest 판: v1 · 릴리스 v1 · x**\n\n| `claim_graph.py` | v%s | `%s` | — | 1 |\n| `test_x.py` | v1 동반 | `%s` | — | 1 |\n\n'
           '## 2.\n\n| 파일 | 저자 |\n|---|:-:|\n| claim_graph.py · test_x.py | ○ |\n| TOOLS_MANIFEST.md · RELEASE.md | ○ |\n\n## 3.\n' % (CGm.__version__, h('claim_graph.py'), h('test_x.py')))
    open(os.path.join(d, 'TOOLS_MANIFEST.md'), 'w', encoding='utf8').write(man)
    mh = h('TOOLS_MANIFEST.md')
    open(os.path.join(d, 'RELEASE.md'), 'w', encoding='utf8').write('# RELEASE v1 — manifest v1 — x\n\n### 저자 (3)\n| `TOOLS_MANIFEST.md` | v1 | `%s` | ○ |\n<!-- sets:end -->\n' % mh)
    r = CGm.selfcheck(d, run_tests=True, stream=io.StringIO())
    assert r['ok'], r['problems']
    assert not os.path.exists(os.path.join(d, '__pycache__')), os.listdir(d)

def t_selfcheck_code_only_release_hash():
    # v15.8.2 (코드 v2.43): 코드 전용 5개(HISTORY 등)는 비공개 저장소에서 릴리스 사이에도 바뀐다 — ②′ RELEASE 대조에서 뺀다.
    # 공개 파일(claim_graph.py)은 그대로 잡는다
    import hashlib, shutil, tempfile
    code_only = ('HISTORY.md', 'PRIVATE_TERMS.txt', 'CODE_PROJECT_README.md', 'release.py', 'GITHUB_README.md')
    d = tempfile.mkdtemp()
    shutil.copy(CGm.__file__, d)
    h = lambda f: hashlib.sha256(open(os.path.join(d, f), 'rb').read()).hexdigest()[:12]
    man = ('**manifest 판: v1 · 릴리스 v1 · x**\n\n| `claim_graph.py` | v%s | `%s` | — | 1 |\n\n'
           '## 2.\n\n| 파일 | 저자 |\n|---|:-:|\n| claim_graph.py | ○ |\n| TOOLS_MANIFEST.md · RELEASE.md | ○ |\n\n## 3.\n' % (CGm.__version__, h('claim_graph.py')))
    open(os.path.join(d, 'TOOLS_MANIFEST.md'), 'w', encoding='utf8').write(man)
    for f in code_only:
        open(os.path.join(d, f), 'w', encoding='utf8').write('릴리스 뒤에 고친 내용\n')
    rows = ''.join('| `%s` | — | `000000000000` | ○ |\n' % f for f in code_only)
    def rel(cg_hash):
        open(os.path.join(d, 'RELEASE.md'), 'w', encoding='utf8').write(
            '# RELEASE v1 — manifest v1 — x\n\n### 저자 (3)\n| `claim_graph.py` | v1 | `%s` | — |\n| `TOOLS_MANIFEST.md` | v1 | `%s` | ○ |\n%s<!-- sets:end -->\n'
            % (cg_hash, h('TOOLS_MANIFEST.md'), rows))
    rel(h('claim_graph.py'))          # 성공 길: 코드 전용 해시가 모두 달라도 통과
    buf = io.StringIO(); r = CGm.selfcheck(d, stream=buf)
    assert r['ok'] and not any('②′' in p for p in r['problems']), (r['problems'], buf.getvalue())
    rel('000000000000')               # 실패 길: 공개 파일 해시가 다르면 여전히 잡는다
    r = CGm.selfcheck(d, stream=io.StringIO())
    assert not r['ok'] and any('②′ claim_graph.py' in p for p in r['problems']), r['problems']
    assert not any(('②′ %s' % f) in p for f in code_only for p in r['problems']), r['problems']
    assert tuple(CGm.CODE_ONLY) == code_only, CGm.CODE_ONLY

def t_claim_graph_cli():
    p = '/tmp/cg_cli.json'
    CGm.save_claims(p, copy.deepcopy(GRAPH))
    import json
    json.dump({'map': {'1': 1}}, open('/tmp/cg_refmap.json', 'w'))
    r = subprocess.run([sys.executable, CGm.__file__, 'remap-refs', '--claims', p, '--map', '/tmp/cg_refmap.json', '-o', '/tmp/cg_cli2.json'], capture_output=True, text=True)
    assert r.returncode == 0 and os.path.exists('/tmp/cg_cli2.json'), r.stderr[-300:]
    r = subprocess.run([sys.executable, CGm.__file__, 'mapdiff', p, p, '--pairs', 'a=a'], capture_output=True, text=True)
    assert r.returncode == 0 and '(a) 양쪽이 잡은 주장 3개' in r.stdout, r.stdout[-300:] + r.stderr[-300:]
    r = subprocess.run([sys.executable, CGm.__file__, 'impact', '--claims', p, 'a', '--sites'], capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.strip() and '===' not in r.stdout, r.stdout
    # v15.4.1: 두 번 적용 중단, --force 로 통과
    r = subprocess.run([sys.executable, CGm.__file__, 'remap-refs', '--claims', '/tmp/cg_cli2.json', '--map', '/tmp/cg_refmap.json', '-o', '/tmp/cg_cli3.json'], capture_output=True, text=True)
    assert r.returncode == 2 and '이미 적용' in r.stdout, r.stdout
    r = subprocess.run([sys.executable, CGm.__file__, 'remap-refs', '--claims', '/tmp/cg_cli2.json', '--map', '/tmp/cg_refmap.json', '-o', '/tmp/cg_cli3.json', '--force'], capture_output=True, text=True)
    assert r.returncode == 0 and len(json.load(open('/tmp/cg_cli3.json'))['refs_maps_applied']) == 2
    # v15.4.1: --pairs 텍스트 파일·잘못된 형식
    open('/tmp/cg_pairs.txt', 'w').write('# 주석\na=a\nb=b\n')
    r = subprocess.run([sys.executable, CGm.__file__, 'mapdiff', p, p, '--pairs', '/tmp/cg_pairs.txt'], capture_output=True, text=True)
    assert r.returncode == 0 and '(a) 양쪽이 잡은 주장 3개' in r.stdout, r.stderr[-300:]
    open('/tmp/cg_pairs_bad.txt', 'w').write('nonsense\n')
    r = subprocess.run([sys.executable, CGm.__file__, 'mapdiff', p, p, '--pairs', '/tmp/cg_pairs_bad.txt'], capture_output=True, text=True)
    assert r.returncode != 0 and '--pairs 파일 형식' in (r.stderr + r.stdout), r.stderr
    here = os.path.dirname(os.path.abspath(__file__))
    for args in (['mapgraph', '--claims', p], ['scaffold', '--claims', p], ['mapreport', '--claims', p],
                 ['extract', MD, '-o', '/tmp/cg_ex.json'], ['mapdiff', p, p], ['mapcheck', MD, '--claims', p, '--nums'] if False else ['mapdiff', p, p],
                 ['mapcheck', MD, '--claims', p] if False else ['impact', '--claims', p, 'a'],
                 ['mapfreeze', MD, '--claims', p, '-o', '/tmp/cg_fz.json'],
                 ['mapstale', MD, '--claims', '/tmp/cg_fz.json']):
        r = subprocess.run([sys.executable, os.path.join(here, 'claim_graph.py')] + args,
                           capture_output=True, text=True)
        assert r.returncode == 0, (args, r.stderr[-400:])


def t_confidence_and_weight_rules():
    g = copy.deepcopy(GRAPH)
    g[0]['confidence'] = 'low'; g[1]['confidence'] = 'bogus'
    probs, _ = CGm.mapgraph(g, io.StringIO())
    assert any('약한 고리: b 가 기대는 a' in p for p in probs), probs
    assert any('confidence "bogus"' in p and not p.startswith('[참고]') for p in probs), probs
    g[1]['confidence'] = 'mid'; g[1]['depends_on'][0]['weight'] = 0.9
    probs, _ = CGm.mapgraph(g, io.StringIO())
    assert any('weight 0.90 는 type 기본값' in p and p.startswith('[참고]') for p in probs), probs
    assert not any('약한 고리: c' in p for p in probs), probs      # context 간선은 약한 고리 아님

def t_numtokens_and_mapcheck_nums():
    assert CGm._numtokens('Shin KJR 2024;25(1):62-73 (n=1079)') == ['1079']
    assert CGm._numtokens('Ulano AJR 2016;207(2):362-368') == []
    assert CGm._numtokens('0.72 vs 0.61, P = 0.004, 784±162 HU') == ['0.72', '0.61', '0.004', '784', '162']
    src = CGm.DocSource(MD)
    cl = [{'id': 'fa', 'statement': 'x', 'evidence': 'FA 0.36 vs 0.44, P = 0.014',
           'sites': ['doc:find:FA decreased'], 'keys': ['decreased'], 'depends_on': []}]
    probs, _ = CGm.mapcheck(src.resolve, copy.deepcopy(cl), io.StringIO(), nums=True)
    assert not probs, probs
    cl[0]['evidence'] = 'FA 0.39 vs 0.45'
    probs, _ = CGm.mapcheck(src.resolve, cl, io.StringIO(), nums=True)
    assert any('수치 0.39' in p and p.startswith('[참고]') for p in probs), probs
    probs, _ = CGm.mapcheck(src.resolve, cl, io.StringIO())
    assert not probs, probs                                        # nums 안 켜면 안 본다


def run():
    results = []
    for name, fn in sorted(globals().items()):
        if name.startswith('t_'):
            try:
                fn(); results.append(('PASS', name[2:], ''))
            except Exception as e:
                results.append(('FAIL', name[2:], '%s: %s' % (type(e).__name__, e)))
                traceback.print_exc()
    w = max(len(n) for _, n, _ in results)
    for st, n, msg in results:
        print('%-4s %-*s %s' % (st, w, n, msg))
    f = sum(1 for s, _, _ in results if s == 'FAIL')
    print('\n통과 %d / 건너뜀 0 / 실패 %d  (전체 %d)' % (len(results) - f, f, len(results)))   # v15.8: 건너뜀 칸을 모든 테스트에 같은 모양으로(발표 요청)
    return f


if __name__ == '__main__':
    sys.exit(1 if run() else 0)
