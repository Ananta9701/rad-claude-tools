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

EXPECT_VERSION = '16.8.1'

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

def t_v1583_selfcheck_unreadable_manifest_fails():
    # 코드 리뷰 09-28 [결함]: 판을 읽을 수 없는 manifest(판 없음 = 판 없음)로 '통과 — 작업 시작 가능' 이 나왔다
    import tempfile
    d = tempfile.mkdtemp()
    open(os.path.join(d, 'TOOLS_MANIFEST.md'), 'w', encoding='utf8').write('garbage\n')
    buf = io.StringIO(); r = CGm.selfcheck(d, stream=buf)
    assert not r['ok'] and any('판을 읽지 못했다' in p for p in r['problems']), (r, buf.getvalue())
    assert '통과 — 작업 시작 가능' not in buf.getvalue()


def t_v1584_unreadable_sites_not_unchanged():
    # 코드 리뷰 09-28 ⑦: 읽을 수 없는 자리(지운 슬라이드·바뀐 절 제목)가 freeze·stale 두 번 다 None 이면 '바뀐 것 없음'
    import copy
    texts = {'s:1': 'alpha text', 's:2': 'beta text'}
    def resolve(site):
        return texts[site]
    g = [{'id': 'x', 'statement': 'X', 'evidence': 'e', 'sites': ['s:1', 's:gone']}]
    try:                                                   # 실패 길: 읽을 수 없는 자리가 있으면 검증 기록을 하지 않는다
        CGm.mapfreeze(resolve, copy.deepcopy(g), at='2026-01-01'); assert False, '멈추지 않았다'
    except SystemExit as e:
        assert 's:gone' in str(e) and '읽지 못' in str(e), e
    old = copy.deepcopy(g)                                 # 구판 freeze 가 None 을 적어 둔 그래프 — 여전히 못 읽으면 알린다
    old[0]['verified'] = {'at': '2026-01-01', 'sites': {'s:1': CGm._fingerprint('alpha text'), 's:gone': None},
                          'evidence': CGm._fingerprint('e|X')}
    buf = io.StringIO(); r = CGm.mapstale(resolve, old, buf)
    assert r['changed'] == ['x'] and '읽을 수 없다' in buf.getvalue(), (r, buf.getvalue())
    ok = [{'id': 'y', 'statement': 'Y', 'evidence': 'e', 'sites': ['s:1', 's:2']}]   # 성공 길: 다 읽히면 전처럼
    CGm.mapfreeze(resolve, ok, at='2026-01-01')
    r = CGm.mapstale(resolve, ok, io.StringIO()); assert r['changed'] == [] and r['unverified'] == [], r


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
                 ['mapfreeze', MD, '--claims', '/tmp/cg_docg.json', '-o', '/tmp/cg_fz.json'],
                 ['mapstale', MD, '--claims', '/tmp/cg_fz.json']):
        if args[0] == 'mapfreeze':   # v15.8.4: 원고(md)에서 읽히는 자리로 — 덱 자리(slide:7) 그래프는 이제 멈춘다(아래)
            json.dump({'doc': 'cg_doc', 'claims': [{'id': 'a', 'statement': 'A', 'evidence': 'e', 'sites': ['doc:sec:Results']}]},
                      open('/tmp/cg_docg.json', 'w', encoding='utf8'))
        r = subprocess.run([sys.executable, os.path.join(here, 'claim_graph.py')] + args,
                           capture_output=True, text=True)
        assert r.returncode == 0, (args, r.stderr[-400:])
    r = subprocess.run([sys.executable, os.path.join(here, 'claim_graph.py'), 'mapfreeze', MD, '--claims', p, '-o', '/tmp/cg_fz2.json'],
                       capture_output=True, text=True)
    assert r.returncode != 0 and 'slide:7' in (r.stdout + r.stderr), (r.returncode, r.stderr[-300:])   # 읽지 못하는 자리 → 멈춤


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


# ---------------------------------------------------------------- v16 (5판: 근거 칸 · 반박 · 짝 저장 · 이력 · 관계도)
def _probs(g):
    return CGm.mapgraph(g, io.StringIO())[0]


def t_v16_sources_validation():
    g = copy.deepcopy(GRAPH)
    g[0]['sources'] = [{'kind': '문헌', 'what': '10.1000/abc', 'at': '[p.5 · PDF 5]', 'element': '방향', 'verdict': '부합'},
                       {'kind': '교과서', 'what': '시험책', 'at': 'p.56'}, {'kind': '덱', 'at': 'slide@260'}]
    assert not [p for p in _probs(g) if 'sources' in p], _probs(g)                 # 성공 길: 맞는 근거 칸은 조용
    g[0]['sources'] = [{'kind': '잡지', 'what': 'x', 'at': 'y'}, {'kind': '문헌', 'at': 'p.1'}, {'kind': '문헌', 'what': 'd', 'at': 'p.1', 'verdict': '맞음'},
                       {'kind': '덱', 'at': 'slide:7'}, {'kind': '문헌', 'what': 'd'}, 'x']
    ps = _probs(g)
    assert any('kind "잡지"' in p for p in ps) and any('what' in p and '비어' in p for p in ps) and any('verdict "맞음"' in p for p in ps), ps
    assert any(p.startswith('[참고]') and 'slide@sldId' in p for p in ps) and any(p.startswith('[참고]') and 'at(' in p for p in ps), ps
    assert any('sources[6]' in p for p in ps), ps
    g[0]['sources'] = 'x'
    assert any('목록이어야' in p for p in _probs(g))


def t_v16_rebuttal_edge():
    g = copy.deepcopy(GRAPH)
    g.append({'id': 'r', 'statement': 'R', 'role': 'rebuttal', 'depends_on': []})
    g[1]['depends_on'].append({'id': 'r', 'type': 'rebuttal'})
    assert not [p for p in _probs(g) if not p.startswith('[참고]')], _probs(g)   # 성공 길: 새 type 을 받는다
    rows = dict((cid, s) for cid, s, _ in CGm.impact(g, ['r'], io.StringIO()))
    assert abs(rows['b'] - 0.5) < 1e-9 and 'c' in rows, rows                          # caveat 과 같은 무게로 하류까지
    g[1]['depends_on'][-1]['type'] = 'caveat'
    assert any('type rebuttal' in p and p.startswith('[참고]') for p in _probs(g))      # 한계로 적은 반박 노드는 알린다
    g[1]['depends_on'][-1]['type'] = 'rebut'
    assert any('type "rebut"' in p for p in _probs(g))                                  # 실패 길: 모르는 type
    g[1]['depends_on'][-1]['type'] = 'rebuttal'
    g[0]['sources'] = [{'kind': '문헌', 'what': 'd', 'at': 'p.1', 'verdict': '반대 방향'}]
    assert any('반박 노드' in p for p in _probs(g))                                      # a 에는 rebuttal 간선이 없다
    g[1]['sources'] = [{'kind': '문헌', 'what': 'd', 'at': 'p.1', 'verdict': '반대 방향'}]
    assert not any(p.startswith('[참고] b:') and '반박 노드' in p for p in _probs(g))


def t_v16_supersedes_history():
    g = copy.deepcopy(GRAPH)
    g[0]['supersedes'] = [{'statement': 'whole sample alpha beta', 'retracted': '2026-08-01'},
                          {'statement': 'subgroup gamma delta', 'retracted': '2026-09-01'}]
    ps = _probs(g)
    assert any('supersedes 가 있는데 forbidden' in p and 'gamma' in p for p in ps), ps  # 가장 최근 것에서 후보
    assert CGm._supersedes({'supersedes': {'statement': 's'}}) == [{'statement': 's'}] and CGm._supersedes({}) == []


def _store(root, doi='10.1000/abc', sha='aaaa', md=None):
    d = os.path.join(root, doi.replace('/', '_')); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'meta.md'), 'w', encoding='utf8').write('<!-- lit: doi=%s pages=2 blank=0 sha=%s -->\n# t\n' % (doi, sha))
    open(os.path.join(d, 'paper.md'), 'w', encoding='utf8').write(md)
    return d


OLD_PDF_MD = '# t\n\n> 원문 PDF 의 글자층(literature.py v0.6). 쪽 표지 [p.N].\n\n[p.1]\n\nIntro words here.\n\n[p.2]\n\nThe sensitivity was 92 percent in lesions.\n'
NEW_PDF_MD = '# t\n\n> 원문 PDF 의 글자층(literature.py v0.8.1). 쪽 표지 [p.인쇄 · PDF N].\n\n[p.e11 · PDF 1]\n\nIntro words here.\n\n[p.e12 · PDF 2]\n\nThe sensitivity was 92 percent in lesions.\n'


def t_v16_mapstale_sources():
    import tempfile
    root = tempfile.mkdtemp(prefix='cgsrc_')
    d = _store(root, md=OLD_PDF_MD)
    cl = [{'id': 's', 'statement': 'S', 'evidence': 'e', 'sites': [], 'keys': [], 'depends_on': [],
           'sources': [{'kind': '문헌', 'what': '10.1000/abc', 'at': '[p.2]', 'verdict': '부합'},
                       {'kind': '문헌', 'what': '10.1000/abc', 'at': '[p.1]', 'element': 'x', 'verdict': '근거 없음'}]},
          {'id': 't', 'statement': 'T', 'sites': [], 'keys': [], 'depends_on': [{'id': 's', 'type': 'premise'}]}]
    CGm.mapfreeze(lambda s: '', cl, sources=root)
    assert len(cl[0]['verified']['sources']) == 2, cl[0]['verified']
    # 1. 쪽 표지 형식·머리말만 바뀐 새 ingest(v0.7+) — 알림 없음, '형식만' 한 줄
    open(os.path.join(d, 'paper.md'), 'w', encoding='utf8').write(NEW_PDF_MD)
    out = io.StringIO(); r = CGm.mapstale(lambda s: '', cl, out, sources=root)
    assert not r['changed'] and len(r['format_only']) == 2 and '검증 이후 바뀐 것 없음' in out.getvalue(), out.getvalue()
    # 2. 원 파일 같음(sha)인데 1쪽 글이 늘었다(변환 개선) — '변환', 하류로 안 번짐, '근거 없음' 판정만 다시 볼 것
    open(os.path.join(d, 'paper.md'), 'w', encoding='utf8').write(NEW_PDF_MD.replace('Intro words here.', 'Intro words here. - listed item now visible'))
    out = io.StringIO(); r = CGm.mapstale(lambda s: '', cl, out, sources=root)
    assert not r['changed'] and r['converted'] and len(r['recheck']) == 1 and '근거 없음' in r['recheck'][0], out.getvalue()
    # 2-1. 원 파일 같음인데 새 변환에 그 자리 표지가 없다 — [변경] 이 아니라 '변환' + at 을 고치라는 줄
    open(os.path.join(d, 'paper.md'), 'w', encoding='utf8').write('# t\n\n[§ Whole]\n\nIntro words here. The sensitivity was 92 percent in lesions.\n')
    out = io.StringIO(); r = CGm.mapstale(lambda s: '', cl, out, sources=root)
    assert not r['changed'] and any('at 을 새 표지로' in x for x in r['recheck']), out.getvalue()
    # 3. 원 파일이 바뀌고(다른 PDF) 2쪽 글도 다름 — [변경], 하류 t 까지
    _store(root, sha='bbbb', md=NEW_PDF_MD.replace('92 percent', '90 percent'))
    out = io.StringIO(); r = CGm.mapstale(lambda s: '', cl, out, sources=root)
    assert r['changed'] == ['s'] and any(x[0] == 't' for x in r['suspect']) and '원 파일도 다름' in out.getvalue(), out.getvalue()
    # 4. 폴더를 주지 않으면 근거 원문은 보지 않는다(전처럼)
    r = CGm.mapstale(lambda s: '', cl, io.StringIO())
    assert not r['changed'], r
    # 5. 보관소에서 그 DOI 가 없어졌다 — [변경](조용히 '같음' 이 되지 않는다)
    import shutil; shutil.rmtree(d)
    out = io.StringIO(); r = CGm.mapstale(lambda s: '', cl, out, sources=root)
    assert r['changed'] == ['s'] and '찾을 수 없음' in out.getvalue(), out.getvalue()
    # 6. 폴더 없이 다시 freeze 하면 전 근거 기록을 그대로 둔다
    CGm.mapfreeze(lambda s: '', cl)
    assert len(cl[0]['verified']['sources']) == 2


def t_v16_sources_textbook_and_section():
    import tempfile
    root = tempfile.mkdtemp(prefix='cgtb_')
    bd = os.path.join(root, '01_시험책'); os.makedirs(bd)
    open(os.path.join(bd, '03_장.md'), 'w', encoding='utf8').write('[p.55 · PDF 69]\n\nalpha\n\n[p.56 · PDF 70]\n\nbeta finding.\n')
    cl = [{'id': 'q', 'statement': 'Q', 'sites': [], 'keys': [], 'depends_on': [],
           'sources': [{'kind': '교과서', 'what': '시험책', 'at': 'p.56'}, {'kind': '교과서', 'what': '없는책', 'at': 'p.1'}]}]
    out = io.StringIO(); CGm.mapfreeze(lambda s: '', cl, sources=root, stream=out)
    assert list(cl[0]['verified']['sources']) == ['교과서|시험책|p.56|'] and '없는책' in out.getvalue(), out.getvalue()   # 못 찾은 근거는 알리고 기록 안 함
    open(os.path.join(bd, '03_장.md'), 'w', encoding='utf8').write('[p.55 · PDF 69]\n\nalpha changed\n\n[p.56 · PDF 70]\n\nbeta finding.\n')
    assert not CGm.mapstale(lambda s: '', cl, io.StringIO(), sources=root)['changed']      # 다른 쪽이 바뀐 것은 무관
    open(os.path.join(bd, '03_장.md'), 'w', encoding='utf8').write('[p.55 · PDF 69]\n\nalpha\n\n[p.56 · PDF 70]\n\nbeta finding revised.\n')
    assert CGm.mapstale(lambda s: '', cl, io.StringIO(), sources=root)['changed'] == ['q']  # 원 sha 가 없는 교과서는 글이 바뀌면 [변경]
    # 절 표지(oa XML md): 상자 뒤 다시 붙은 같은 절 표지도 한 절로
    md = '# t\n\n> Europe PMC 전문 XML(PMC1)에서(변환 v0.8.1)\n\n[§ Methods]\n\nfirst part.\n\n[§ 상자 · K]\n\nbox.\n\n[§ Methods]\n\nsecond part.\n'
    assert 'first part' in CGm._at_text(md, '[§ Methods]') and 'second part' in CGm._at_text(md, '[§ Methods]') and 'box' not in CGm._at_text(md, '[§ Methods]')
    try:
        CGm._at_text(md, '[§ Results]'); assert False
    except KeyError:
        pass
    assert CGm._page_of('[p.e12 · PDF 2]') == ('e12', 2) and CGm._page_of('[p.— · PDF 3]') == (None, 3) and CGm._page_of('[p.7]') == (None, 7) and CGm._page_of('p.7') == ('7', None)


def t_v16_mapdraw():
    g = copy.deepcopy(GRAPH)
    g[0]['role'] = 'evidence'; g[1]['role'] = 'main'; g[1]['statement'] = 'He said "yes" <b>'
    g.append({'id': 'r', 'statement': 'R', 'role': 'rebuttal', 'depends_on': []})
    g.append({'id': 'z', 'statement': 'Z', 'depends_on': []})
    g[1]['depends_on'].append({'id': 'r', 'type': 'rebuttal'})
    md = CGm.mapdraw(g, text=True, all_edges=True)                                          # v16.0 모양은 --all-edges 로 남는다
    assert md.count('```mermaid') == 1 and 'flowchart BT' in md, md
    assert 'n1 ==> n2' in md and 'n2 -.-> n3' in md and 'n4 -- 반박 --x n2' in md, md       # 근거 → 주장 방향, 종류별 선
    assert '#quot;yes#quot;' in md and '<b>' not in md and '#lt;b#gt;' in md, md             # 따옴표·꺾쇠는 Mermaid 가 깨지지 않게
    assert 'n1["a<br/>evidence·mid' in md and '#lt;br' not in md, md                          # 줄바꿈 <br/> 은 그대로(v16 첫 빌드 결함)
    assert 'n5' in md                                                                       # --all-edges 는 외톨이도 그린다
    md = CGm.mapdraw(g, changed=['a'])
    assert 'n5' not in md and 'n4' not in md and 'class n1 changed' in md and 'class n2 must' in md, md   # impact: 경로만, 색
    md = CGm.mapdraw(g, changed=['nope'])                                                   # 실패 길: 없는 id — 멈추지 않고 빈 그림
    assert 'flowchart BT' in md and 'n1' not in md, md


def t_v16_mapdraw_and_saved_pairs_cli():
    import json, tempfile
    d = tempfile.mkdtemp(prefix='cgcli_')
    cg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'claim_graph.py')
    A = os.path.join(d, 'a.json'); B = os.path.join(d, 'b.json')
    json.dump({'doc': 'x.docx', 'claims': [{'id': 'a1', 'statement': 's', 'sites': ['doc:p:1'], 'keys': ['k1'], 'depends_on': []}]}, open(A, 'w'))
    json.dump({'claims': [{'id': 'b9', 'statement': 's', 'sites': ['doc:p:9'], 'keys': ['k9'], 'depends_on': []}]}, open(B, 'w'))
    run = lambda *a: subprocess.run([sys.executable, cg] + list(a), capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    r = run('mapdiff', A, B, '--labels', '저자', '리뷰어')
    assert '양쪽이 잡은 주장 0개' in r.stdout, r.stdout                                      # 자리·keys 가 달라 자동으로는 못 짝짓는다
    r = run('mapdiff', A, B, '--labels', '저자', '리뷰어', '--save-pairs')
    assert r.returncode == 2 and '--pairs 와 함께' in r.stdout, r.stdout                     # 실패 길: 짝 없이 저장하지 않는다
    r = run('mapdiff', A, B, '--labels', '저자', '리뷰어', '--pairs', 'a1=b9', '--save-pairs')
    assert json.load(open(A))['pairs_with'] == {'리뷰어': {'a1': 'b9'}} and json.load(open(A))['doc'] == 'x.docx', open(A).read()
    r = run('mapdiff', A, B, '--labels', '저자', '리뷰어')
    assert '양쪽이 잡은 주장 1개' in r.stdout and 'pairs_with' in r.stdout, r.stdout           # 다음부터 --pairs 없이
    r = run('mapdiff', B, A, '--labels', '리뷰어', '저자')
    assert '양쪽이 잡은 주장 1개' in r.stdout, r.stdout                                      # 반대쪽에서 불러도 뒤집어 쓴다
    out = os.path.join(d, '관계도.md')
    r = run('mapdraw', '--claims', A, '-o', out)
    t = open(out, encoding='utf8').read()
    assert r.returncode == 0 and 'flowchart LR' in t and '`a1`' in t, (r.stderr, t)          # 간선 없는 한 주장 — 그림 밖 목록으로
    r = run('mapdraw', '--claims', A, '-o', out, '--all-edges')
    assert r.returncode == 0 and 'flowchart BT' in open(out, encoding='utf8').read(), r.stderr
    r = run('mapdraw', '--claims', A, '-o', out, '--impact', 'a1', '--text')
    assert r.returncode == 0 and 'class n1 changed' in open(out, encoding='utf8').read()



def t_v161_mapdraw_compact_default():
    # 사용자 09-29: 저자 51주장·간선 83(caveat 46) 전체 그림이 6614×1033 px — 왼쪽→오른쪽, caveat 접기, 역할별 색, 외톨이는 목록
    g = [{'id': 'm', 'role': 'main', 'depends_on': [{'id': 'e', 'type': 'premise'}, {'id': 'cv', 'type': 'caveat'}]},
         {'id': 'e', 'role': 'evidence', 'depends_on': [{'id': 'cv', 'type': 'caveat'}, {'id': 'cv2', 'type': 'caveat'}, {'id': 'bg', 'type': 'context'}]},
         {'id': 'bg', 'role': 'background', 'depends_on': []},
         {'id': 'cv', 'role': 'caveat', 'depends_on': []},
         {'id': 'cv2', 'role': 'caveat', 'depends_on': []},
         {'id': 'cvk', 'role': 'caveat', 'depends_on': []},                                   # caveat 이지만 context 간선으로 끼어 있다 — 접지 않는다
         {'id': 'k', 'role': 'claim', 'depends_on': [{'id': 'cvk', 'type': 'context'}, {'id': 'm', 'type': 'support'}]},
         {'id': 'lone', 'role': 'method', 'statement': 'lonely', 'depends_on': []},
         {'id': 'onlycav', 'role': 'claim', 'depends_on': [{'id': 'cv', 'type': 'caveat'}]}]
    md = CGm.mapdraw(g)
    block = md.split('```mermaid')[1].split('```')[0]
    assert 'flowchart LR' in block and 'flowchart BT' not in block, md                       # 근거 왼쪽 → main 오른쪽
    assert '"e<br/>evidence·mid<br/>한계 2"' in block and '"m<br/>main·mid<br/>한계 1"' in block, block   # 걸린 caveat 수
    assert '"cv<br/>' not in block and '"cv2<br/>' not in block and '한계 .->' not in block, block       # caveat 상자·선은 접힘
    assert '"cvk<br/>caveat·mid"' in block, block                                             # 다른 간선에 낀 caveat 은 남긴다
    assert 'classDef r_main' in block and 'classDef r_evidence' in block and 'classDef r_claim' in block and 'classDef r_background' in block, block
    assert '"lone' not in block and '"onlycav' not in block, block                           # 외톨이는 그림에 없고
    after = md.split('```')[-1]
    assert '`lone` (방법)' in after and '`onlycav` (해석, 한계 1)' in after and '접은 caveat 2개' in after, after   # 그림 밖 목록에
    assert '역할·confidence' in md                                                            # 범례에 상자 글 뜻(발표 09-29)
    # --impact 는 v16.0 그대로(저자 확인 끝남): 아래→위, caveat 도 경로에 있으면 그린다
    mi = CGm.mapdraw(g, changed=['cv'])
    assert 'flowchart BT' in mi and 'class n4 changed' in mi and 'classDef r_' not in mi, mi
    # 실패 길: 간선이 하나도 없는 그래프(발표 09-20 판 모양) — 빈 그림·목록 대신 한 줄(v16.2)
    none = [{'id': 'x%02d' % k, 'depends_on': []} for k in range(21)]
    md = CGm.mapdraw(none)
    assert '```mermaid' not in md and '간선이 하나도 없는 그래프(주장 21개)' in md and 'x05' not in md, md
    assert 'flowchart BT' in CGm.mapdraw(none, all_edges=True) and '"x05' in CGm.mapdraw(none, all_edges=True)   # 상자는 --all-edges 로
    one = CGm.mapdraw([{'id': 'solo', 'depends_on': []}])                                     # 주장 하나는 그래프 모양 그대로(목록 한 줄)
    assert '`solo`' in one, one


def t_v161_mapgraph_isolated_note():
    g = copy.deepcopy(GRAPH) + [{'id': 'z1', 'depends_on': []}, {'id': 'z2', 'depends_on': []}]
    ps = [p for p in CGm.mapgraph(g, io.StringIO())[0] if '외톨이' in p]
    assert ps == ['[참고] 간선이 하나도 없는 주장(외톨이) 2개: z1, z2'], ps                    # 한 줄로, 이름과 함께
    assert not [p for p in CGm.mapgraph(copy.deepcopy(GRAPH), io.StringIO())[0] if '외톨이' in p]   # 다 이어졌으면 없음
    assert not [p for p in CGm.mapgraph([{'id': 'solo'}], io.StringIO())[0] if '외톨이' in p]        # 주장 하나뿐이면 알리지 않음
    ps = [p for p in CGm.mapgraph([{'id': 'x%02d' % k} for k in range(21)], io.StringIO())[0] if '간선이 하나도' in p]
    assert ps == ['[참고] 간선이 하나도 없는 그래프(주장 21개) — 관계(depends_on)를 아직 적지 않았다'], ps   # v16.2: 21개 이름을 늘어놓지 않는다
    # v16.3 (사용자 09-29, 부관리자 재현): role=claim 21개·간선 0 — "premise 간선이 없음" 이 21줄 나오던 것도 요약 한 줄로
    g21 = [{'id': 'x%02d' % k, 'role': 'claim'} for k in range(20)] + [{'id': 'ev', 'role': 'evidence'}]
    ps = [p for p in CGm.mapgraph(g21, io.StringIO())[0] if p.startswith('[참고]')]
    assert '[참고] 간선이 하나도 없는 그래프(주장 21개) — 관계(depends_on)를 아직 적지 않았다 (주장별 간선 [참고] premise 없음 20 · caveat 없음 1 를 이 줄로 합침)' in ps, ps
    assert len(ps) == 2 and any('role=main 인 주장이 0개' in p for p in ps), ps               # 그래프 전체 한 줄(main 개수)은 그대로
    # 실패 길: 간선이 하나라도 있으면 주장별 [참고] 는 전처럼 줄마다
    g21[0]['depends_on'] = [{'id': 'ev', 'type': 'premise'}]
    ps = CGm.mapgraph(g21, io.StringIO())[0]
    assert sum('premise 간선이 없음' in p for p in ps) == 19 and any('ev: evidence 인데 걸린 caveat 이 없음' in p for p in ps), ps



def t_v164_case_example_in_doc_is_valid():
    # v16.4·v16.6: CLAIM_GRAPH.md §3-2-1 증례 예시가 규약대로 돈다 — 문서가 도구와 어긋나지 않게
    import json, re as _re
    doc = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CLAIM_GRAPH.md')
    if not os.path.exists(doc):
        return
    t = open(doc, encoding='utf8').read()
    g = json.loads(_re.search(r'## 3-2-1.*?```json\n(.*?)```', t, _re.S).group(1))
    cl = g['claims']
    assert CGm.mapgraph(copy.deepcopy(cl), io.StringIO(), kind=g['kind'])[0] == []               # kind 증례 — 알림 없음
    assert [r[0] for r in CGm.impact(cl, ['f-calc'], io.StringIO())] == ['ddx-gran', 'dx', 'ddx-malig']
    md = CGm.mapdraw(cl)
    assert '-- 반박 --x' in md and 'class ' in md and 'excluded' in md and 'subgraph g1["증례1"]' in md, md



GAPG = [
    {'id': 'm', 'role': 'main', 'sources': [{'kind': '문헌', 'what': '10.1000/a', 'at': 'p.1'}, {'kind': '문헌', 'what': '10.1000/b', 'at': 'p.2'}],
     'depends_on': [{'id': 'e', 'type': 'premise'}, {'id': 'lowc', 'type': 'support'}, {'id': 'k', 'type': 'premise'}]},
    {'id': 'k', 'role': 'claim', 'keys': ['alpha term', 'beta term'], 'depends_on': [{'id': 'e', 'type': 'premise'}, {'id': 'b', 'type': 'support'}]},
    {'id': 'k2', 'role': 'claim', 'sources': [{'kind': '문헌', 'what': '10.1000/c'}, {'kind': '교과서', 'what': '책', 'at': 'p.5'}],
     'depends_on': [{'id': 'e', 'type': 'support'}]},
    {'id': 'b', 'role': 'background', 'sources': [{'kind': '문헌', 'what': '10.1000/d', 'at': 'p.3'}], 'depends_on': []},
    {'id': 'e', 'role': 'evidence', 'depends_on': []},
    {'id': 'lowc', 'role': 'claim', 'confidence': 'low', 'sources': [{'kind': '문헌', 'what': '10.1000/e'}, {'kind': '문헌', 'what': '10.1000/f'}],
     'depends_on': [{'id': 'e', 'type': 'premise'}, {'id': 'b', 'type': 'premise'}]},
    {'id': 'x', 'role': 'method', 'depends_on': []},
    {'id': 'old', 'role': 'claim', 'status': 'superseded', 'depends_on': []},
]


def t_v165_find_gaps():
    # 사용자 09-29 (가): 문헌 없음(claim·main·background 만) · 근거 하나(sources 1 또는 받침 간선 1) · 약한 고리 · 외톨이
    rows, noedge = CGm.find_gaps(copy.deepcopy(GAPG))
    got = {cid: ks for cid, _, ks, _ in rows}
    assert not noedge and set(got) == {'k', 'k2', 'b', 'lowc', 'x'}, got                    # m 은 sources 2·받침 3 — 공백 없음
    assert got['k'] == ['문헌 없음'], got                                                     # 받침 간선 2 라 '근거 하나' 는 아님
    assert got['k2'] == ['근거 하나 — 받침 간선 1(e)'], got                                    # 교과서도 원문 근거로 센다(sources 2)
    assert got['b'] == ['근거 하나 — sources 1'], got
    assert got['lowc'][0].startswith('약한 고리 — confidence low, 기대는 주장 1(m)'), got
    assert got['x'] == ['외톨이'], got
    assert 'e' not in got and 'old' not in got                                               # evidence 는 문헌 공백에서 빼고, 철회는 뺀다
    assert all(t_ == '' for _, _, _, t_ in rows), rows                                        # v16.7: 검색어는 keys 에서 가져오지 않는다(비움)
    rows, noedge = CGm.find_gaps([{'id': 'p', 'role': 'claim'}, {'id': 'q', 'role': 'claim'}])   # 간선 0 그래프: 외톨이를 줄마다 내지 않는다
    assert noedge and all('외톨이' not in ks for _, _, ks, _ in rows) and len(rows) == 2, rows


def t_v165_gaps_table_and_to_instr():
    md = CGm.gaps_table(copy.deepcopy(GAPG), '시험원고')
    rows = [l for l in md.splitlines() if l.startswith('| G')]
    assert len(rows) == 10 and rows[0].startswith('| G01-받침 | `k`') and rows[1].startswith('| G01-반박 | `k`'), rows[:2]   # 공백마다 받침·반박
    assert 'AI 제안' in md and '반박 줄도' in md and 'evidence' in md, md[:600]
    # 채운 표: G01 받침은 AI 제안 DOI, 반박은 비움 · G02 받침은 DOI 없이 글만 · G03 받침은 이미 판정 · G04 받침·반박이 같은 DOI
    fill = {'G01-받침': ('https://doi.org/10.1234/ABC.5', 'AI 제안', '', 'alpha term; beta term'), 'G02-받침': ('Kim 2020 어딘가', 'AI 제안', '', 'x'),
            'G03-받침': ('10.9/zz', '사람', '부합', 'x'), 'G04-받침': ('10.1234/abc.5', '사람', '', 'y'), 'G04-반박': ('10.5555/r1', 'AI 제안', '', 'z')}
    out = []
    for l in md.splitlines():
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        if c and c[0] in fill:
            cand, src, ver, terms = fill[c[0]]; c[6], c[7], c[9], c[5] = cand, src, ver, terms
            l = '| ' + ' | '.join(c) + ' |'
        out.append(l)
    instr, notes = CGm.gaps_to_instr('\n'.join(out), '시험원고')
    assert '1. 후보 G01-받침 (AI 제안). doi:10.1234/abc.5' in instr and '2. 후보 G04-반박 (AI 제안). doi:10.5555/r1' in instr, instr
    assert '10.9/zz' not in instr and instr.count('doi:10.1234/abc.5') == 1, instr           # 판정 있는 줄은 빼고, 같은 DOI 는 한 번
    assert '| G04-받침 | 1 |' in instr and '| G04-반박 | 2 |' in instr, instr
    assert any('G01: 받침 줄만' in n for n in notes) and any('G02-받침: 후보 칸에 DOI 가 없다' in n for n in notes), notes   # 실패 길: 알림
    assert not any('G04' in n for n in notes), notes
    try:                                                                                        # literature 가 있는 세트면 그 파서로 읽힌다
        import literature as LT
    except ImportError:
        return
    refs, cl = LT.parse_refs(instr), LT.parse_claims(instr)
    assert [r['doi'] for r in refs] == ['10.1234/abc.5', '10.5555/r1'] and [c['refs'] for c in cl] == [[1], [1], [2]], (refs, cl)
    assert cl[0]['terms'] == ['alpha term', 'beta term'], cl


def t_v165_mapgraph_sources_store():
    import tempfile
    root = tempfile.mkdtemp(prefix='cggs_')
    d = os.path.join(root, '10.1000_a'); os.makedirs(d)
    open(os.path.join(d, 'meta.md'), 'w', encoding='utf8').write('<!-- lit: doi=10.1000/a pages=1 blank=0 sha=aa -->\n')
    g = [{'id': 'k', 'role': 'claim', 'depends_on': [], 'sources': [
        {'kind': '문헌', 'what': '10.1000/a', 'at': 'p.1', 'verdict': '부합'},
        {'kind': '문헌', 'what': '10.1000/a', 'at': 'p.2'},
        {'kind': '문헌', 'what': '10.1000/zzz', 'at': 'p.1', 'verdict': '부합'}]}]
    ps = CGm.mapgraph(copy.deepcopy(g), io.StringIO(), sources=root)[0]
    hard = [p for p in ps if not p.startswith('[참고]')]
    assert hard == ['k: sources[3]: 문헌 10.1000/zzz 가 보관소에 없다 — 원문을 받지 않은 근거는 sources 에 넣지 않는다(작업표에 둔다)'], ps   # [필수]
    assert any(p.startswith('[참고] k: sources[2]: 문헌 10.1000/a 판정') for p in ps) and not any('sources[1]' in p for p in ps), ps
    assert not [p for p in CGm.mapgraph(copy.deepcopy(g), io.StringIO())[0] if '보관소' in p or '판정' in p]   # 보관소를 안 주면 전처럼


def t_v165_gaps_cli():
    import json, tempfile
    d = tempfile.mkdtemp(prefix='cggc_')
    cg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'claim_graph.py')
    A = os.path.join(d, 'a.json'); json.dump({'doc': 'Doc_v1.docx', 'claims': GAPG}, open(A, 'w'), ensure_ascii=False)
    run = lambda *a: subprocess.run([sys.executable, cg] + list(a), capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    r = run('gaps', '--claims', A, '-o', os.path.join(d, 't.md'))
    assert r.returncode == 0 and '공백 5' in r.stdout and '# Doc_v1 — 근거 공백 작업표' in open(os.path.join(d, 't.md'), encoding='utf8').read(), (r.stdout, r.stderr)
    r = run('gaps', '--to-instr', os.path.join(d, 't.md'), '-o', os.path.join(d, 'i.md'), '--name', 'Doc_v1')
    assert r.returncode == 0 and '> 원고: Doc_v1' in open(os.path.join(d, 'i.md'), encoding='utf8').read(), r.stdout
    r = run('gaps', '-o', os.path.join(d, 'x.md'))
    assert r.returncode == 2 and '--claims' in r.stdout, r.stdout                           # 실패 길: 입력 없음
    r = run('mapgraph', '--claims', A, '--sources', d)
    assert r.returncode == 1 and '보관소에 없다' in r.stdout, r.stdout                          # 보관소에 없는 문헌 근거 = [필수] → 1



def t_v166_excluded_ddx_and_case_kind():
    # 발표 K23 (09-29): 배제된 감별이 확정 진단과 같은 상자로 그려짐 · premise 없음 [참고] 가 매번 · 논문용 [참고] 16줄
    g = [{'id': 'f1', 'group': 'c1', 'role': 'evidence', 'forbidden': ['old'], 'depends_on': []},
         {'id': 'ok', 'group': 'c1', 'role': 'claim', 'depends_on': [{'id': 'f1', 'type': 'premise'}]},
         {'id': 'ex', 'group': 'c1', 'role': 'claim', 'status': 'excluded', 'sites': ['slide@9'], 'depends_on': [{'id': 'f1', 'type': 'rebuttal'}]},
         {'id': 'ex2', 'group': 'c1', 'role': 'claim', 'status': 'excluded', 'depends_on': []},
         {'id': 'dx', 'group': 'c1', 'role': 'main', 'depends_on': [{'id': 'ok', 'type': 'premise'}]},
         {'id': 'f9', 'group': 'c2', 'role': 'evidence', 'depends_on': []},
         {'id': 'dx9', 'group': 'c2', 'role': 'main', 'depends_on': [{'id': 'f9', 'type': 'premise'}]}]
    ps = CGm.mapgraph(copy.deepcopy(g), io.StringIO())[0]
    assert not [p for p in ps if not p.startswith('[참고]')], ps                                # excluded 는 맞는 status(sites 가 있어도 됨)
    assert not any('ex:' in p and 'premise' in p for p in ps), ps                             # 배제 감별은 premise 없음 [참고] 를 내지 않고
    assert any(p.startswith('[참고] ex2: 배제(excluded)인데 rebuttal 간선이 없음') for p in ps), ps   # 배제 근거가 없으면 알린다
    assert any('forbidden 이 있는데' in p for p in ps) and any('caveat 이 없음' in p for p in ps) and any('role=main 인 주장이 2개' in p for p in ps), ps
    ps = CGm.mapgraph(copy.deepcopy(g), io.StringIO(), kind='증례')[0]                          # 증례 모드: 논문용 [참고] 셋을 끈다
    assert not any('forbidden 이 있는데' in p or 'caveat 이 없음' in p or 'role=main 인' in p for p in ps), ps
    assert any('ex2: 배제' in p for p in ps), ps                                                # 배제 근거 [참고] 는 증례에서도
    bad = copy.deepcopy(g); bad[2]['status'] = 'excludd'
    assert any('status "excludd"' in p for p in CGm.mapgraph(bad, io.StringIO())[0])           # 실패 길: 모르는 status
    md = CGm.mapdraw(copy.deepcopy(g))
    blk = md.split('```mermaid')[1].split('```')[0]
    assert 'subgraph g1["c1"]' in blk and 'subgraph g2["c2"]' in blk and blk.count('  end') == 2, blk   # 증례마다 묶음
    assert '  g1 ~~~ g2' in blk and blk.count('direction LR') == 2, blk                          # v16.8: 처음 나온 순서로 위→아래(보이지 않는 연결)
    rev = CGm.mapdraw([x for x in g if x['group'] == 'c2'] + [x for x in g if x['group'] == 'c1'])
    assert 'subgraph g1["c2"]' in rev and '  g1 ~~~ g2' in rev, rev                             # 처음 나온 순서 = 파일 순서
    one = CGm.mapdraw([x for x in g if x['group'] == 'c1'])
    assert '~~~' not in one and 'direction LR' not in one, one                                  # 실패 길: 묶음 하나면 연결·방향을 넣지 않는다
    assert '"ex<br/>claim·mid<br/>배제"' in blk and 'stroke-dasharray' in blk and 'fill:#ffffff' in blk, blk
    rc = [l for l in blk.splitlines() if l.strip().startswith('class ') and l.strip().endswith(' r_claim')][0]
    ex_nid = 'n3'
    assert ex_nid not in rc.split()[1].split(','), rc                                         # 배제 상자는 초록(claim) 색을 받지 않는다
    assert '배제된 감별' in md.split('```')[-1], md                                            # 범례 한 줄
    md = CGm.mapdraw([dict(x, group=None) for x in g])                                        # group 이 없으면 묶지 않는다
    assert 'subgraph' not in md
    rows, _ = CGm.find_gaps(copy.deepcopy(g))
    assert not any(cid in ('ex', 'ex2') for cid, _, _, _ in rows), rows                       # 배제 감별은 근거 공백에서 뺀다


def t_v166_cli_kind():
    import json, tempfile
    d = tempfile.mkdtemp(prefix='cgk_')
    cg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'claim_graph.py')
    A = os.path.join(d, 'a.json')
    cl = [{'id': 'f', 'role': 'evidence', 'forbidden': ['x'], 'depends_on': []}, {'id': 'm', 'role': 'main', 'depends_on': [{'id': 'f', 'type': 'premise'}]}]
    json.dump({'kind': '증례', 'claims': cl}, open(A, 'w'), ensure_ascii=False)
    r = subprocess.run([sys.executable, cg, 'mapgraph', '--claims', A], capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode == 0 and 'forbidden 이 있는데' not in r.stdout and 'caveat 이 없음' not in r.stdout, r.stdout
    json.dump({'claims': cl}, open(A, 'w'), ensure_ascii=False)
    r = subprocess.run([sys.executable, cg, 'mapgraph', '--claims', A], capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    assert 'forbidden 이 있는데' in r.stdout, r.stdout                                          # kind 가 없으면 전처럼



def t_v167_gaps_cited_split_and_blank_terms():
    # 저자 09-29(claims v10): "문헌 없음" 14개 중 6개는 원고 인용 [n] 이 이미 있는데 sources 만 빈 것 — 따로. 검색어는 keys 가 아니라 비움
    g = [{'id': 'c1', 'role': 'claim', 'statement': 'X is higher [12,14].', 'keys': ['argue', 'refs 12-14'], 'depends_on': []},
         {'id': 'c2', 'role': 'claim', 'statement': 'Y is linked', 'sites': ['doc:find:Y was linked [7\u20139]'], 'depends_on': []},
         {'id': 'c3', 'role': 'claim', 'statement': 'Z plausibly follows', 'keys': ['pooling'], 'depends_on': []},
         {'id': 'c4', 'role': 'background', 'statement': 'W [3]', 'confidence': 'low', 'depends_on': []},
         {'id': 'd', 'role': 'main', 'sources': [{'kind': '문헌', 'what': '10.1/a'}, {'kind': '문헌', 'what': '10.1/b'}],
          'depends_on': [{'id': 'c1', 'type': 'premise'}, {'id': 'c2', 'type': 'premise'}, {'id': 'c3', 'type': 'context'}, {'id': 'c4', 'type': 'support'}]}]
    got = {cid: ks for cid, _, ks, _ in CGm.find_gaps(copy.deepcopy(g))[0]}
    assert got['c1'] == [CGm.GAP_CITED] and got['c2'] == [CGm.GAP_CITED], got               # 문장 또는 자리에 [n]
    assert got['c3'] == ['문헌 없음'], got                                                     # 실패 길: 인용이 없으면 그대로 공백
    assert got['c4'][0] == CGm.GAP_CITED and got['c4'][1].startswith('약한 고리'), got
    md = CGm.gaps_table(copy.deepcopy(g), 'T')
    p1, p2 = md.split('## 2. 인용 있음')
    assert '## 1. 찾을 공백 2개' in p1 and '`c3`' in p1 and '`c4`' in p1 and '`c1`' not in p1, p1   # 인용 + 다른 공백(c4)은 1부에
    assert '— sources 미기입 2개' in p2 and '| G03-기입 | `c1`' in p2 and '| G04-기입 | `c2`' in p2 and 'G03-받침' not in md, p2
    assert 'argue' not in md and 'pooling' not in md and 'refs 12-14' not in md, md            # keys 가 검색어로 들어가지 않는다
    assert '문헌 없음(인용 있음 — sources 미기입) 3' in md and '문헌 없음 1' in md, md.splitlines()[2]   # 머리 요약도 두 부류를 나눠 센다
    rows = []
    for l in md.splitlines():
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        if c and c[0] == 'G03-기입':
            c[6], c[7] = '10.7777/cited', '사람'
            l = '| ' + ' | '.join(c) + ' |'
        rows.append(l)
    instr, notes = CGm.gaps_to_instr('\n'.join(rows), 'T')
    assert 'doi:10.7777/cited' in instr and '| G03-기입 | 1 |' in instr, instr                     # 기입 줄도 검증지시로
    assert any('G03-기입: 검색어 칸이 비었다' in n for n in notes), notes                       # 검색어가 비면 알린다


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
