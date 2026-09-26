#!/usr/bin/env python3
"""
claim_graph.py — 문서(발표·원고·심사 회신)의 주장 의존 그래프. pptx/docx 에 독립.

발표·저자·리뷰어 세 프로젝트가 같은 규약을 쓴다. 문서 종류마다 다른 것은
"자리(site)를 어떻게 읽느냐"뿐이라, 그 부분만 resolver(site -> text) 로 넘겨받는다.

    from claim_graph import *
    resolve = DocSource('Manuscript_v37.docx').resolve      # docx
    resolve = deck_toolkit._resolver(deck)                  # pptx
    claims = load_claims('claims.json')
    mapgraph(claims); mapcheck(resolve, claims); mapfreeze(resolve, claims); mapstale(resolve, claims)

자리 표기
    slide:N  notes:N               (pptx, deck_toolkit 이 해석)
    doc:p:N                        (docx, N 번째 비어있지 않은 문단. 삽입에 약함)
    doc:find:<문구>                (docx, 그 문구가 들어 있는 문단. 삽입에 강함 — 권장)
    doc:sec:<제목>                 (docx, 그 제목 문단부터 다음 제목 전까지)
    doc:tbl:N                      (docx, N 번째 표 전체)

주장 하나의 항목
    id, statement, evidence, sites, keys, forbidden      (v11)
    depends_on[{id,type,weight}], status, supersedes, anchor, verified   (v12)
    role: main | claim | evidence | background | method | caveat | rebuttal   (v13, 선택)
          main 은 문서당 하나. IMRaD 로 읽을 때 evidence=Results, background=Introduction,
          method=Methods, caveat=Limitations, claim=Discussion 의 보조 주장
    section: 자유 문자열 (예: "Results/Within-group")                    (v13, 선택)
    confidence: high | mid | low  (기본 mid)                               (v15)
          weight 는 "의존 강도"(type 기본값으로 고정), confidence 는 "그 주장 자체의 근거 강도".
          둘을 한 숫자에 섞지 않는다. "weight 높은 간선의 상류가 low" = 약한 고리.
    origin: human | extract                                              (v13, extract 가 붙임)

원리는 소프트웨어에서 가져왔다: 빌드 시스템의 의존 DAG + 내용 해시(바뀐 것과 하류만
다시), 요구사항 추적의 suspect link(상류가 바뀌면 사람이 풀 때까지 의심), 스프레드시트의
위상 순서 재계산(순환은 기본 오류), ADR 의 superseded 상태.
"""

import html
import io
import os
import re
import sys
import zipfile

__version__ = '15.8'   # TOOLS_MANIFEST 와 대조. 판이 오르면 여기와 test_claim_graph.EXPECT_VERSION 을 함께 올린다

EDGE_TYPES = ('premise', 'support', 'context', 'caveat')
EDGE_DEFAULT_WEIGHT = {'premise': 1.0, 'support': 0.7, 'context': 0.3, 'caveat': 0.5}
IMPACT_CUTOFF = 0.25
CLAIM_STATUS = ('accepted', 'proposed', 'superseded')
CLAIM_ROLES = ('main', 'claim', 'evidence', 'background', 'method', 'caveat', 'rebuttal', 'premise')
CONFIDENCE = ('high', 'mid', 'low')   # high=이 자료로 재현됨 / mid=자료가 방향은 지지 / low=미검정·외부 근거·미해결


# ----------------------------------------------------------------------------
# 입출력
# ----------------------------------------------------------------------------

def load_claims(path):
    import json
    with open(path, encoding='utf8') as f:
        data = json.load(f)
    return data['claims'] if isinstance(data, dict) else data


def norm_name(name):
    """v15.4 (#7): 프로젝트 업로드가 붙이는 `__N_` 접미사를 벗긴 파일명. 판 비교는 이걸로 한다."""
    if not name:
        return name
    base = os.path.basename(name)
    return re.sub(r'__\d+_(?=\.[^.]+$)', '', base)


def doc_name(name):
    """v15.4.1: 규약 §3 의 `doc` 값 — 경로·`__N_`·확장자를 뺀 문서명. mapfreeze 가 기록하고 mapstale 이 비교한다."""
    if not name:
        return name
    return os.path.splitext(norm_name(name))[0]


def load_claims_full(path):
    """v15.4 (#14): (meta dict, claims). meta 는 claims 를 뺀 상위 키 전부 — 저장 시 그대로 보존한다."""
    import json
    with open(path, encoding='utf8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        meta = {k: v for k, v in data.items() if k != 'claims'}
        return meta, data['claims']
    return {}, data


def load_claims_meta(path):
    """(이름, note, claims). v15.4: `doc` 이 `deck` 보다 우선한다(v15.3 까지는 반대여서 stale `deck` 이 이겼다)."""
    meta, cl = load_claims_full(path)
    return meta.get('doc') or meta.get('deck'), meta.get('note'), cl


def save_claims(path, claims, deck_name=None, note=None, meta=None, doc=None):
    """v15.4 (#14): meta 의 상위 키를 전부 보존한다. deck_name 은 덱(pptx) 그래프용, doc 은 원고용 —
    둘 다 주면 doc 이 이기고 deck 은 제거하며 경고한다."""
    import json
    data = dict(meta or {})
    if doc:
        data['doc'] = doc_name(doc)
        if 'deck' in data:
            print('[경고] 원고 그래프에 stale `deck` 키(%s) — 제거. 덱과 원고 그래프는 키를 나눈다(doc/deck)' % data['deck'])
            del data['deck']
    elif deck_name:
        data['deck'] = deck_name
    if note is not None:
        data['note'] = note
    elif 'note' not in data and (doc or deck_name):
        data['note'] = ''
    data['claims'] = claims
    with open(path, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


# ----------------------------------------------------------------------------
# docx 자리 해석
# ----------------------------------------------------------------------------

class DocSource:
    """docx 를 문단 목록으로 읽고 doc:* 자리를 해석한다."""

    def __init__(self, path):
        self.path = path
        self.paras, self.headings, self.tables = self._read(path)

    @staticmethod
    def _read(path):
        """(문단 목록, 제목 인덱스 집합, 표 목록[[문단...]]).

        제목: pStyle Heading 이 있으면 그것. 없으면 휴리스틱 — 표 밖의 짧은 문단(60자 이하),
        마침표로 끝나지 않고, 숫자·기호로 시작하지 않으며, 전체 대문자이거나 굵게(w:b) 표시.
        """
        paras, heads, tables = [], set(), []
        if path.lower().endswith('.docx'):
            with zipfile.ZipFile(path) as z:
                x = z.read('word/document.xml').decode('utf8', 'ignore')
            styled = False
            # 표 블록을 먼저 떼어 낸다
            body = []
            pos = 0
            for tm in re.finditer(r'<w:tbl>.*?</w:tbl>', x, re.S):
                body.append(('p', x[pos:tm.start()])); body.append(('t', tm.group(0))); pos = tm.end()
            body.append(('p', x[pos:]))

            def ptexts(chunk):
                out = []
                for m in re.finditer(r'<w:p\b.*?</w:p>', chunk, re.S):
                    p = m.group(0)
                    t = html.unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)))
                    if t.strip():
                        out.append((t.strip(), p))
                return out
            for kind, chunk in body:
                if kind == 't':
                    cells = [t for t, _ in ptexts(chunk)]
                    tables.append(cells)
                    for t in cells:
                        paras.append(t)
                    continue
                for t, p in ptexts(chunk):
                    paras.append(t)
                    i = len(paras) - 1
                    if re.search(r'w:pStyle w:val="(Heading|heading|Title|제목)', p):
                        heads.add(i); styled = True
                    elif (len(t) <= 60 and not re.search(r'[.:;,]$', t) and not re.match(r'[\d\-(<>=χ]', t)
                          and re.search(r'[A-Za-z\uac00-\ud7a3]', t) and ' = ' not in t and '<' not in t
                          and (t.isupper() or re.search(r'<w:b\b', p))):
                        heads.add((i, 'heur'))
            if styled:
                heads = {h for h in heads if not isinstance(h, tuple)}
            else:
                heads = {h[0] if isinstance(h, tuple) else h for h in heads}
            return paras, heads, tables
        txt = open(path, encoding='utf8', errors='ignore').read()
        for ln in txt.splitlines():
            if ln.strip():
                if ln.startswith('#'):
                    heads.add(len(paras)); ln = ln.lstrip('#').strip()
                paras.append(ln.strip())
        return paras, heads, tables

    def units(self):
        """extract 용 (site, text) 목록. doc:find 는 문단 앞 6단어로 만든다."""
        out = []
        for i, p in enumerate(self.paras):
            out.append(('doc:p:%d' % (i + 1), p))
        return out

    def resolve(self, site):
        kind, rest = site.split(':', 1)
        if kind != 'doc':
            raise ValueError('docx resolver 는 doc:* 자리만 해석합니다: %s' % site)
        sub, arg = rest.split(':', 1)
        if sub == 'p':
            return self.paras[int(arg) - 1]
        if sub == 'find':
            hits = [p for p in self.paras if arg.lower() in p.lower()]
            if not hits:
                raise KeyError('문구를 가진 문단 없음: %s' % arg)
            if len(hits) > 1:
                raise KeyError('문구가 %d개 문단에 있어 모호함: %s' % (len(hits), arg))
            return hits[0]
        if sub == 'tbl':
            return ' '.join(self.tables[int(arg) - 1])
        if sub == 'sec':
            idx = [i for i in sorted(self.headings)
                   if self.paras[i].lower().startswith(arg.lower())]
            if not idx:
                idx = [i for i, p in enumerate(self.paras) if p.lower().startswith(arg.lower())]
            if not idx:
                raise KeyError('절 제목 없음: %s' % arg)
            s = idx[0]
            e = next((i for i in sorted(self.headings) if i > s), len(self.paras))
            return ' '.join(self.paras[s:e])
        raise ValueError('doc:p:N / doc:find:문구 / doc:sec:제목 / doc:tbl:N 중 하나: %s' % site)


# ----------------------------------------------------------------------------
# 그래프
# ----------------------------------------------------------------------------

def _edges(claims):
    out = {}
    for c in claims:
        lst = []
        for e in c.get('depends_on', []):
            if isinstance(e, str):
                e = {'id': e}
            typ = e.get('type', 'support')
            w = float(e.get('weight', EDGE_DEFAULT_WEIGHT.get(typ, 0.5)))
            lst.append((e['id'], typ, w))
        out[c['id']] = lst
    return out


def _dependents(claims):
    rev = {c['id']: [] for c in claims}
    for cid, lst in _edges(claims).items():
        for up, typ, w in lst:
            rev.setdefault(up, []).append((cid, typ, w))
    return rev


def _sccs(claims):
    edges = _edges(claims)
    index, low, on, stack, out = {}, {}, set(), [], []
    counter = [0]

    def strong(v):
        index[v] = low[v] = counter[0]; counter[0] += 1
        stack.append(v); on.add(v)
        for up, _, _ in edges.get(v, []):
            if up not in index:
                if up in edges:
                    strong(up)
                    low[v] = min(low[v], low[up])
            elif up in on:
                low[v] = min(low[v], index[up])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop(); on.discard(w); comp.append(w)
                if w == v:
                    break
            selfloop = any(up == v for up, _, _ in edges.get(v, []))
            if len(comp) > 1 or selfloop:
                out.append(sorted(comp))
    for v in edges:
        if v not in index:
            strong(v)
    return out


def mapgraph(claims, stream=sys.stdout):
    """구조 검사 + 위상 순서. 반환 (문제목록, 순서)."""
    ids = {c['id'] for c in claims}
    problems = []
    edges = _edges(claims)
    by_id = {c['id']: c for c in claims}
    seen = set()
    for c in claims:
        if c['id'] in seen:
            problems.append('%s: id 중복' % c['id'])
        seen.add(c['id'])
        st = c.get('status', 'accepted')
        if st not in CLAIM_STATUS:
            problems.append('%s: status "%s" 는 %s 중 하나여야 함'
                            % (c['id'], st, '/'.join(CLAIM_STATUS)))
        if c.get('confidence', 'mid') not in CONFIDENCE:
            problems.append('%s: confidence "%s" 는 %s 중 하나여야 함'
                            % (c['id'], c['confidence'], '/'.join(CONFIDENCE)))
        for e in c.get('depends_on', []):
            if isinstance(e, dict) and 'weight' in e:
                typ = e.get('type', 'support')
                if abs(float(e['weight']) - EDGE_DEFAULT_WEIGHT.get(typ, 0.5)) > 1e-9:
                    problems.append('[참고] %s -> %s: weight %.2f 는 type 기본값(%.1f)이 아님 — 근거 강도는 confidence 로 적는다'
                                    % (c['id'], e.get('id'), float(e['weight']), EDGE_DEFAULT_WEIGHT.get(typ, 0.5)))
        if c.get('role') and c['role'] not in CLAIM_ROLES:
            problems.append('%s: role "%s" 는 %s 중 하나여야 함'
                            % (c['id'], c['role'], '/'.join(CLAIM_ROLES)))
        if st == 'superseded' and c.get('sites'):
            problems.append('%s: superseded 인데 sites 가 남아 있음 — 자리를 새 주장으로 옮기거나 비울 것'
                            % c['id'])
        if st == 'proposed' and c.get('origin') == 'extract':
            problems.append('[참고] %s: extract 가 뽑은 후보. 사람이 statement/근거/자리를 확정해야 함'
                            % c['id'])
        both = [k for k in c.get('keys', []) if k in c.get('forbidden', [])]
        if both:   # v15.5.2 (발표 T2): 찾을 표현과 금지 표현이 같으면 mapcheck 가 자리 통과·금지 실패를 동시에 낸다 — 주장 문장이 낡았다는 신호
            problems.append('%s: keys 와 forbidden 에 같은 표현 %s — statement 가 슬라이드/원고보다 낡았는지 확인' % (c['id'], both))
        if c.get('forbidden') and not c.get('supersedes'):
            problems.append('[참고] %s: forbidden 이 있는데 supersedes(철회한 옛 주장) 기록이 없음'
                            % c['id'])
        if c.get('supersedes') and not c.get('forbidden'):
            hint = _forbidden_hints(c['supersedes'].get('statement', ''))
            problems.append('%s: supersedes 가 있는데 forbidden 이 비어 있음 — 옛 문구를 넣지 않으면 '
                            'mapcheck 가 옛 주장을 통과시킨다. 후보: %s' % (c['id'], ' / '.join(hint) or '-'))
        if c.get('role') in ('main', 'claim') and not any(t == 'premise' for _, t, _ in edges[c['id']]):
            problems.append('[참고] %s: role=%s 인데 premise 간선이 없음 — 검정 없는 해석이 결론 자리에 있는지 확인'
                            % (c['id'], c['role']))
        for up, typ, w in edges[c['id']]:
            if up not in ids:
                problems.append('%s: depends_on 의 "%s" 가 정의되지 않음' % (c['id'], up))
            if typ not in EDGE_TYPES:
                problems.append('%s -> %s: type "%s" 는 %s 중 하나여야 함'
                                % (c['id'], up, typ, '/'.join(EDGE_TYPES)))
            if not (0.0 <= w <= 1.0):
                problems.append('%s -> %s: weight %.2f 는 0~1 이어야 함' % (c['id'], up, w))

    for c in claims:
        if c.get('role') == 'evidence' and not any(t == 'caveat' for _, t, _ in edges[c['id']]):
            problems.append('[참고] %s: evidence 인데 걸린 caveat 이 없음' % c['id'])
    weak = []
    for c in claims:
        for up, typ, w in edges[c['id']]:
            if typ in ('premise', 'support') and up in by_id and by_id[up].get('confidence', 'mid') == 'low':
                weak.append((w, c['id'], up, typ))
    for w, cid, up, typ in sorted(weak, reverse=True):
        problems.append('[참고] 약한 고리: %s 가 기대는 %s 는 confidence=low (%s %.1f)' % (cid, up, typ, w))
    mains = [c['id'] for c in claims if c.get('role') == 'main']
    if any(c.get('role') for c in claims) and len(mains) != 1:
        problems.append('[참고] role=main 인 주장이 %d개 (문서당 하나가 기본): %s'
                        % (len(mains), ', '.join(mains) or '-'))
    cycles = _sccs(claims)
    for comp in cycles:
        anchors = [x for x in comp if by_id[x].get('anchor')]
        if len(anchors) != 1:
            problems.append('순환 %s: anchor 가 정확히 하나여야 함 (지금 %d개). '
                            '순환 논증이 아니라면 한쪽 화살표를 지우고, 맞다면 시작점을 anchor 로 지정'
                            % (' <-> '.join(comp), len(anchors)))

    cut = set()
    for comp in cycles:
        for x in comp:
            if by_id[x].get('anchor'):
                cut.update((x, up) for up, _, _ in edges[x] if up in comp)
    order, done = [], set()

    def visit(v, path):
        if v in done or v not in edges or v in path:
            return
        for up, _, _ in edges[v]:
            if (v, up) in cut:
                continue
            visit(up, path | {v})
        done.add(v); order.append(v)
    starts = [x for comp in cycles for x in comp if by_id[x].get('anchor')]
    for v in starts + [c['id'] for c in claims]:
        visit(v, frozenset())

    print('=== 주장 의존 그래프 ===', file=stream)
    print('주장 %d개, 간선 %d개, 순환 %d개' % (
        len(claims), sum(len(v) for v in edges.values()), len(cycles)), file=stream)
    roots = [c['id'] for c in claims if not edges[c['id']]]
    rev = _dependents(claims)
    leaves = [c['id'] for c in claims if not rev.get(c['id'])]
    print('뿌리(전제 없음): %s' % ', '.join(roots), file=stream)
    print('잎(기대는 것 없음): %s' % ', '.join(leaves), file=stream)
    print('\n검토 순서 (상류 -> 하류):', file=stream)
    for i, v in enumerate(order, 1):
        ups = ', '.join('%s[%s %.1f]' % (u, t, w) for u, t, w in edges[v]) or '-'
        print('  %2d. %-24s <- %s' % (i, v, ups), file=stream)
    if problems:
        print('', file=stream)
        for p in problems:
            print('  [!] %s' % p, file=stream)
    return problems, order


def impact(claims, changed, stream=sys.stdout):
    """바뀐 주장의 하류와 다시 볼 자리. 반환 [(id, 강도, 경로)] 강도 내림차순."""
    rev = _dependents(claims)
    by_id = {c['id']: c for c in claims}
    best = {}
    frontier = [(cid, 1.0, [cid]) for cid in changed if cid in by_id]
    for cid in changed:
        if cid not in by_id:
            print('  [!] 정의되지 않은 주장: %s' % cid, file=stream)
    while frontier:
        v, s, path = frontier.pop(0)
        for down, typ, w in rev.get(v, []):
            ns = s * w
            if down in path or down in changed:
                continue
            if down not in best or ns > best[down][0]:
                best[down] = (ns, path + [down])
                frontier.append((down, ns, path + [down]))

    rows = sorted(best.items(), key=lambda kv: -kv[1][0])
    print('=== 영향 범위: %s ===' % ', '.join(changed), file=stream)
    sites_must, sites_ref = [], []
    for cid in changed:
        if cid in by_id:
            sites_must += [s for s in by_id[cid].get('sites', []) if s not in sites_must]
    for cid, (s, path) in rows:
        lvl = '필수' if s >= IMPACT_CUTOFF else '참고'
        print('  [%s] %-24s 강도 %.2f  conf=%-4s 경로 %s'
              % (lvl, cid, s, by_id[cid].get('confidence', 'mid'), ' -> '.join(path)), file=stream)
        tgt = sites_must if s >= IMPACT_CUTOFF else sites_ref
        tgt += [x for x in by_id[cid].get('sites', []) if x not in tgt]
    print('\n다시 봐야 할 자리 (필수): %s' % ', '.join(sites_must), file=stream)
    ref = [x for x in sites_ref if x not in sites_must]
    if ref:
        print('참고로 볼 자리           : %s' % ', '.join(ref), file=stream)
    if not rows:
        print('  하류 주장 없음 — 바뀐 주장의 자리만 고치면 됨', file=stream)
    return [(cid, s, path) for cid, (s, path) in rows]


# ----------------------------------------------------------------------------
# 자리 대조 / 해시
# ----------------------------------------------------------------------------

_NUMTOK = re.compile(r'(?<![\w.])[-−]?\d+(?:[.,]\d+)?(?:\s*%)?(?![\w])')


def _numtokens(text):
    """evidence 문자열의 수치 토큰.

    소수·백분율·4자리 이상 정수는 항상. 1~3자리 정수는 n=, ±, vs, /, : 같은 통계 문맥에 붙은 것만
    (참고문헌 번호·권·페이지를 걸러 내기 위해). 연도(19xx/20xx)는 뺀다.
    """
    out = []
    for m in _NUMTOK.finditer(text):
        t = m.group(0).replace('−', '-').replace(',', '.').strip()
        if re.fullmatch(r'(19|20)\d\d', t):
            continue
        if re.fullmatch(r'-?\d{1,3}', t):
            ctx = text[max(0, m.start() - 4):m.end() + 2]
            if not re.search(r'n\s*=\s*\d|±|vs\.?\s*\d|\d\s*±|\d/\d|\d\s*vs', ctx):
                continue
        out.append(t)
    return out


def _cited_numbers(txt):
    """자리 텍스트의 대괄호 인용을 전부 펼친 번호 집합. [24,26-28] → {24,26,27,28}"""
    out = set()
    for m in _CITE_BRACKET.finditer(txt):
        inner = re.search(r'\[(.*)\]', m.group(0)).group(1)
        try:
            out.update(_expand_range(inner))
        except ValueError:
            pass
    return out


def _key_hit(key, txt):
    """v15.4.2 (리뷰어 도구회신 refs키_mapcheck): key 가 `refs 26-28` / `refs 26,28` / `refs 26` 꼴이면
    리터럴이 아니라 인용번호로 본다 — 자리의 대괄호 인용을 펼쳐 그 번호가 전부 인용돼 있으면 적중.
    [24,26-28] 처럼 다른 번호와 섞인 인용도 잡는다. 그 외 key 는 종전대로 소문자 부분문자열."""
    m = _REFS_KEY.match(key.strip())
    if m:
        try:
            want = set(_expand_range(m.group(1)))
        except ValueError:
            return key in txt
        return bool(want) and want <= _cited_numbers(txt)
    return key in txt


def mapcheck(resolve, claims, stream=sys.stdout, nums=False, nums_sep=None):
    """nums=True 면 evidence 의 수치 토큰이 sites 자리 중 한 곳에는 있어야 한다 ([참고]).
    nums_sep (v15.5, 리뷰어 요청): 사용자가 명시한 구분자 **앞쪽**만 검사한다. evidence 를
    "원고 값 | 재현 값" 으로 쓰는 리뷰어 용법에서 `--nums-sep "|"` 로 재현값을 뺀다. 구분자는 도구가
    가정하지 않고 사용자가 선언하는 것이므로 서식 의존이 아니다. 지정하지 않으면 종전대로 전체."""
    problems, matrix = [], {}
    for c in claims:
        cid = c['id']
        keys = [k.lower() for k in c.get('keys', [])]
        forb = [k.lower() for k in c.get('forbidden', [])]
        for site in c.get('sites', []):
            try:
                txt = resolve(site).lower()
            except Exception as e:
                problems.append('%s: 자리 %s 를 읽을 수 없음 (%s)' % (cid, site, e))
                continue
            matrix.setdefault(site, []).append(cid)
            if keys and not any(_key_hit(k, txt) for k in keys):
                problems.append('%s: %s 에 주장이 반영되지 않음 (찾는 표현: %s)'
                                % (cid, site, ' / '.join(c['keys'])))
            for f, forig in zip(forb, c.get('forbidden', [])):
                if f in txt:
                    problems.append('%s: %s 에 철회된 표현이 남아 있음 ("%s")' % (cid, site, forig))
        if nums and c.get('evidence'):
            alltxt = ''
            for site in c.get('sites', []):
                try:
                    alltxt += ' ' + resolve(site)
                except Exception:
                    pass
            alltxt = alltxt.replace('−', '-').replace('\u2009', ' ')
            ev_txt = c['evidence'].split(nums_sep, 1)[0] if nums_sep else c['evidence']
            missing = [t for t in _numtokens(ev_txt) if t.rstrip('%').strip() not in alltxt]
            if missing:
                problems.append('[참고] %s: evidence 의 수치 %s 가 sites 어디에도 없음' % (cid, ', '.join(missing)))
    gp, _ = mapgraph(claims, stream=open(os.devnull, 'w'))
    problems.extend(p for p in gp if not p.startswith('[참고]'))
    print('=== 주장 관계도 대조 ===', file=stream)
    print('주장 %d개 / 자리 %d곳' % (len(claims), len(matrix)), file=stream)
    if problems:
        for p in problems:
            print('  [!] %s' % p, file=stream)
    else:
        print('  모든 주장이 선언된 자리에 반영됨', file=stream)
    return problems, matrix


def _site_key(s):
    m = re.search(r':(\d+)', s)
    return (int(m.group(1)) if m else 10 ** 9, s)


def mapreport(claims, stream=sys.stdout):
    sites = []
    for c in claims:
        for s in c.get('sites', []):
            if s not in sites:
                sites.append(s)
    sites.sort(key=_site_key)
    w = max([len(c['id']) for c in claims] + [10])
    print('%-*s  %s' % (w, 'claim', '  '.join('%-9s' % s[:9] for s in sites)), file=stream)
    for c in claims:
        row = ['  O      ' if s in c.get('sites', []) else '  .      ' for s in sites]
        print('%-*s  %s' % (w, c['id'], '  '.join(row)), file=stream)
    print('', file=stream)
    for c in claims:
        print('[%s] %s' % (c['id'], c.get('statement', '')), file=stream)
        if c.get('evidence'):
            print('      근거: %s' % c['evidence'], file=stream)
        if c.get('forbidden'):
            print('      철회: %s' % ' / '.join(c['forbidden']), file=stream)
    return sites


_CITE_BRACKET = re.compile(r'\s*\[\d{1,3}(?:\s*[,\u2013\u2014-]\s*\d{1,3})*\]')


def _fingerprint(text):
    """자리 텍스트 해시. v15.2: 대괄호 인용번호([12], [15,16], [29-31])를 빼고 잰다 —
    참고문헌 재번호는 주장을 바꾸지 않는데 v44→v45 에서 39자리 중 28자리가 [변경]으로 떴다."""
    import hashlib
    t = _CITE_BRACKET.sub('', text or '')
    return hashlib.sha1(re.sub(r'\s+', ' ', t).strip().encode('utf8')).hexdigest()[:12]


def mapfreeze(resolve, claims, at=None):
    """검증 완료 선언. 자리 텍스트와 statement/evidence 의 해시를 기록."""
    import datetime
    at = at or datetime.date.today().isoformat()
    for c in claims:
        fp = {}
        for site in c.get('sites', []):
            try:
                fp[site] = _fingerprint(resolve(site))
            except Exception:
                fp[site] = None
        c['verified'] = {'at': at, 'sites': fp,
                         'evidence': _fingerprint(c.get('evidence', '') + '|' + c.get('statement', '')),
                         # v15.5: keys 만 바꾼 그래프(mapstale 0 · mapcheck 실패)를 잡기 위한 별도 해시.
                         # 구판 freeze 에는 이 키가 없고, 없으면 mapstale 이 검사하지 않는다(기존 그래프 무영향)
                         'keys': _fingerprint('|'.join(c.get('keys', [])))}
    return claims


def mapstale(resolve, claims, stream=sys.stdout):
    changed, unverified, detail = [], [], []
    for c in claims:
        v = c.get('verified')
        if not v:
            unverified.append(c['id']); continue
        if v.get('evidence') != _fingerprint(c.get('evidence', '') + '|' + c.get('statement', '')):
            changed.append(c['id']); detail.append('%s: statement/evidence 가 바뀜' % c['id']); continue
        if 'keys' in v and v['keys'] != _fingerprint('|'.join(c.get('keys', []))):
            changed.append(c['id']); detail.append('%s: keys 가 바뀜 (freeze 뒤 편집)' % c['id']); continue
        for site in c.get('sites', []):
            try:
                now = _fingerprint(resolve(site))
            except Exception:
                now = None
            if v.get('sites', {}).get(site) != now:
                changed.append(c['id']); detail.append('%s: %s 텍스트가 바뀜' % (c['id'], site)); break
    print('=== 검증 이후 변경 ===', file=stream)
    if unverified:
        print('  [!] 아직 검증 기록 없음: %s' % ', '.join(unverified), file=stream)
    for d in detail:
        print('  [변경] %s' % d, file=stream)
    if not changed and not unverified:
        print('  검증 이후 바뀐 것 없음', file=stream)
        return {'changed': [], 'suspect': [], 'unverified': []}
    sus = impact(claims, changed, stream) if changed else []
    if changed:
        by_id = {c['id']: c for c in claims}
        direct = []
        for cid in changed:
            direct += [s for s in by_id.get(cid, {}).get('sites', []) if s not in direct]
        print('\n실제로 바뀐 주장의 자리(직접) : %s' % (', '.join(direct) or '(없음)'), file=stream)
        print('위 "다시 봐야 할 자리" 중 나머지는 하류 전파 — 내용이 바뀐 것이 아니라 근거가 흔들린 자리다.', file=stream)
    print('\n위 자리를 확인한 뒤 mapfreeze 로 다시 기록하십시오.', file=stream)
    return {'changed': changed, 'suspect': sus, 'unverified': unverified}


# ----------------------------------------------------------------------------
# extract — 문서에서 주장 후보를 뽑아 관계도 초안을 만든다
#
#  자동으로 "논리 구조"를 뽑는 것은 안 된다(argument mining 은 미해결 문제이고,
#  같은 뜻을 다른 말로 쓴 것을 코드가 알 수 없다). 되는 것은 **후보 표시**다:
#  수치·인용·방향어·한정어·대조어가 들어간 문장을 자리와 함께 뽑아 status=proposed 로
#  놓고, 인접 문장 사이의 접속어로 간선 후보(따라서→premise, 그러나/다만→caveat)를 단다.
#  사람이 이 초안을 지우고·합치고·확정한다. 초안이 빈 파일보다 빠르다는 것이 전부다.
# ----------------------------------------------------------------------------

_NUM = re.compile(r'\d+\.\d+|\d+\s*%|\bn\s*=\s*\d+|\bp\s*[<=]\s*0?\.\d+', re.I)
_CITE = re.compile(r'\bet al\b|\b(19|20)\d\d\b(?![-/.]\d)|\[\d+\]|\(\w+,? (19|20)\d\d\)', re.I)
# 참고문헌 조각(저자 목록, 권·페이지)은 주장이 아니다
_REFLINE = re.compile(r'^\W*(references?\)|[A-Z][a-z]+ [A-Z]{1,3},? et al|\d{4};\s*\d+|doi|PMID)', re.I)
_DIRECTION = ('increas', 'decreas', 'higher', 'lower', 'greater', 'reduc', 'improv', 'worsen',
              '증가', '감소', '높', '낮', '커', '작아', '상승', '하강', '소실', '보존')
_HEDGE = ('may ', 'might', 'suggest', 'likely', 'possibl', 'cannot', 'not ', 'no ',
          '시사', '가능', '할 수 없', '아니', '없', '못')
_CONSEQ = ('therefore', 'thus', 'hence', 'so that', 'accordingly', 'consequently',
           '따라서', '그러므로', '그래서', '이에 따라', '즉')
_CONTRAST = ('however', 'but ', 'although', 'whereas', 'nevertheless', 'in contrast', 'caveat',
             'limitation', '그러나', '하지만', '다만', '반면', '한계', '주의')
_SENT = re.compile(r'\n+|(?<=[.!?。])\s+|(?<=다\.)\s*|(?<=니다\.)\s*')


def _sentences(text):
    text = re.sub(r'\bet al\.', 'et al', text)          # 약어 마침표로 쪼개지지 않게
    out = []
    for s in _SENT.split(text):
        s = s.strip()
        if len(s) < 15 or _REFLINE.search(s):
            continue
        if _CITE.search(s) and not re.search(r'[a-z\uac00-\ud7a3]{4,}.*[a-z\uac00-\ud7a3]{4,}', s.lower()):
            continue                                       # 인용 표기만 있는 조각
        out.append(s)
    return out


def _score(s):
    low = s.lower()
    sc = 0
    if _NUM.search(s): sc += 2
    if _CITE.search(s): sc += 2
    if any(w in low for w in _DIRECTION): sc += 1
    if any(w in low for w in _HEDGE): sc += 1
    if any(w in low for w in _CONTRAST): sc += 1
    return sc


def _slug(s, n=3):
    words = re.findall(r'[A-Z]{2,}|[A-Za-z][A-Za-z\-]+|[\uac00-\ud7a3]{2,}', s)
    stop = {'the', 'and', 'with', 'for', 'that', 'this', 'from', 'are', 'was', 'not',
            '그래서', '따라서', '그러나', '다만', '만으로는', '없습니다', '있습니다', '입니다'}
    words = [w.lower() for w in words if (len(w) > 2 or w.isupper()) and w not in stop][:n]
    return '-'.join(words) or 'claim'


def extract(units, min_score=2, stream=sys.stdout):
    """units: [(site, text)] -> 주장 후보 목록 (status=proposed, origin=extract).

    같은 문장이 여러 자리에 있으면(슬라이드 본문과 노트) 하나로 합쳐 sites 를 늘린다.
    간선 후보: 앞 문장이 후보이고 이 문장이 접속어로 시작하면 (문단 경계를 넘어도 본다)
      따라서/thus  -> 앞 문장을 premise 로
      그러나/다만  -> 앞 문장에 caveat 로
    """
    cands, by_norm = [], {}
    prev = None                      # 자리(문단)를 넘어서도 앞 문장을 기억한다
    for site, text in units:
        for s in _sentences(text):
            sc = _score(s)
            low = s.lower()
            is_conseq = any(low.startswith(w) or (' ' + w) in low[:25] for w in _CONSEQ)
            is_contrast = any(low.startswith(w) for w in _CONTRAST)
            if sc < min_score and not (prev and (is_conseq or is_contrast)):
                continue
            norm = re.sub(r'[^0-9a-z\uac00-\ud7a3]+', '', low)[:80]
            if norm in by_norm:
                c = by_norm[norm]
                if site not in c['sites']:
                    c['sites'].append(site)
                prev = c
                continue
            cid = _slug(s)
            k = 2
            while any(x['id'] == cid for x in cands):
                cid = '%s-%d' % (_slug(s), k); k += 1
            c = {'id': cid, 'statement': s[:160], 'evidence': '', 'status': 'proposed',
                 'origin': 'extract', 'score': sc, 'sites': [site], 'keys': [], 'forbidden': [],
                 'depends_on': []}
            m = _CITE.search(s)
            if m:
                c['evidence'] = '(문장 안 인용) ' + s[max(0, m.start() - 30):m.end() + 10]
            if prev is not None:
                if is_conseq:
                    c['depends_on'].append({'id': prev['id'], 'type': 'premise', 'weight': 1.0})
                elif is_contrast:
                    c['role'] = 'caveat'
                    c['depends_on'].append({'id': prev['id'], 'type': 'caveat', 'weight': 0.5})
            cands.append(c); by_norm[norm] = c
            prev = c
    cands.sort(key=lambda c: -c['score'])
    print('=== 주장 후보 %d개 (점수 높은 순) ===' % len(cands), file=stream)
    for c in cands:
        print('  [%d] %-28s %s' % (c['score'], c['id'], ', '.join(c['sites'])), file=stream)
        print('       %s' % c['statement'][:110], file=stream)
        for e in c['depends_on']:
            print('       <- %s [%s]' % (e['id'], e['type']), file=stream)
    print('\n* 후보입니다. 사람이 지우고 합치고 statement 를 한 문장 주장으로 고쳐 확정하십시오.',
          file=stream)
    print('* keys 는 비어 있습니다. 확정하면서 3~4개를 넣어야 mapcheck 가 작동합니다.', file=stream)
    return cands


# ----------------------------------------------------------------------------
# scaffold — 관계도에서 문서 뼈대를 낸다 (그래프가 원본, 문서는 그 표현)
# ----------------------------------------------------------------------------

def scaffold(claims, stream=sys.stdout):
    """위상 순서대로 '자리 -> 거기에 실릴 주장' 목록을 낸다. 문서를 이 순서로 쓴다."""
    _, order = mapgraph(claims, stream=open(os.devnull, 'w'))
    by_id = {c['id']: c for c in claims}
    sites = {}
    for cid in order:
        for s in by_id[cid].get('sites', []):
            sites.setdefault(s, []).append(cid)
    print('=== 문서 뼈대 (자리 순) ===', file=stream)
    for s in sorted(sites, key=_site_key):
        print('%s' % s, file=stream)
        for cid in sites[s]:
            c = by_id[cid]
            tag = '' if c.get('status', 'accepted') == 'accepted' else ' (%s)' % c['status']
            print('    - [%s]%s %s' % (cid, tag, c.get('statement', '')), file=stream)
            if c.get('evidence'):
                print('        근거: %s' % c['evidence'], file=stream)
    unplaced = [cid for cid in order if not by_id[cid].get('sites')]
    if unplaced:
        print('\n자리가 없는 주장: %s' % ', '.join(unplaced), file=stream)
    return sites


def _forbidden_hints(statement, n=3):
    """철회한 옛 주장 문장에서 forbidden 후보 어구를 뽑는다 (3~4 단어 구절)."""
    words = re.findall(r"[A-Za-z][A-Za-z\-']+|[\uac00-\ud7a3]+", statement)
    out = []
    for i in range(0, max(0, len(words) - 2), 3):
        out.append(' '.join(words[i:i + 3]))
        if len(out) >= n:
            break
    return out


# ----------------------------------------------------------------------------
# mapdiff — 두 그래프(저자 vs 리뷰어)를 짝지어 차이를 낸다
#
#  id 는 각자 붙인 것이라 쓸 수 없다. sites 겹침(같은 문구·같은 표)과 keys 겹침으로 짝짓는다.
#  출력: 한쪽에만 있는 주장 / 짝지은 주장의 간선 유무·type·weight 차이 / caveat 부착 차이.
#  리뷰 규약의 (a) 양쪽이 잡은 것 (b) 심사만 (c) 저자만 표가 이것이다.
# ----------------------------------------------------------------------------

def _norm_site(s):
    return re.sub(r'\s+', ' ', s.strip().lower())


_ROLE_GROUP = {'main': 'claim', 'claim': 'claim', 'evidence': 'evidence', 'premise': 'evidence',
               'caveat': 'caveat', 'rebuttal': 'caveat', 'background': 'background', 'method': 'method'}


def _pair_claims(a, b, manual=None):
    """a 의 주장마다 b 에서 가장 겹치는 주장. (점수, a_id, b_id) — 점수 0 은 짝 없음.
    v15.4 (#9): role 이 둘 다 있고 계열(_ROLE_GROUP)이 다르면 후보에서 뺀다(caveat↔evidence 오매칭).
    manual {a_id: b_id} 는 점수와 무관하게 먼저 확정한다(--pairs)."""
    def sig(c):
        return ({_norm_site(x) for x in c.get('sites', [])},
                {k.lower() for k in c.get('keys', [])})
    sa = {c['id']: sig(c) for c in a}
    sb = {c['id']: sig(c) for c in b}
    ra = {c['id']: _ROLE_GROUP.get(c.get('role')) for c in a}
    rb = {c['id']: _ROLE_GROUP.get(c.get('role')) for c in b}
    pairs, used = {}, set()
    for ia, ib in (manual or {}).items():
        ibs = ib if isinstance(ib, list) else [ib]
        if ia in sa and all(x in sb for x in ibs):
            pairs[ia] = (ibs[0] if len(ibs) == 1 else ibs, 99); used.update(ibs)
    cand = []
    for ia, (s1, k1) in sa.items():
        for ib, (s2, k2) in sb.items():
            if ra[ia] and rb[ib] and ra[ia] != rb[ib]:
                continue
            score = 2 * len(s1 & s2) + len(k1 & k2)
            if score:
                cand.append((score, ia, ib))
    for score, ia, ib in sorted(cand, reverse=True):
        if ia in pairs or ib in used:
            continue
        pairs[ia] = (ib, score); used.add(ib)
    return pairs


def mapdiff(a, b, label_a='A', label_b='B', stream=sys.stdout, pairs=None):
    """반환 {'both': [(a_id, b_id)], 'only_a': [...], 'only_b': [...], 'edge_diff': [...], 'caveat_diff': [...]}
    pairs: 수동 짝 {a_id: b_id} (v15.4). 자동 짝은 sites·keys 겹침뿐이라 명명만 다른 주장은 못 잡는다 —
    (b)(c) 가 크게 나오면 사람이 짝을 만들어 --pairs 로 넘긴다."""
    pairs = _pair_claims(a, b, manual=pairs)
    by_a = {c['id']: c for c in a}; by_b = {c['id']: c for c in b}
    a2b = {ia: ib for ia, (ib, _) in pairs.items()}
    def _bs(ib):
        return ib if isinstance(ib, list) else [ib]
    both = [(ia, ib) for ia, ib in a2b.items()]
    matched_b = {x for ib in a2b.values() for x in _bs(ib)}
    only_a = [c['id'] for c in a if c['id'] not in a2b]
    only_b = [c['id'] for c in b if c['id'] not in matched_b]
    ea, eb = _edges(a), _edges(b)
    def _lab(ib):
        return '+'.join(_bs(ib))   # 1:N 짝은 b1+b2 로 표기 (v15.5)
    edge_diff, caveat_diff = [], []
    for ia, ib in both:
        da = {_lab(a2b[up]) if up in a2b else '?' + up: (t, w) for up, t, w in ea[ia]}
        db = {}
        for x in _bs(ib):
            db.update({up: (t, w) for up, t, w in eb[x]})
        ib = _lab(ib)
        for up in sorted(set(da) | set(db)):
            if up not in db:
                edge_diff.append('%s/%s: %s 에만 간선 -> %s [%s %.1f]' % (ia, ib, label_a, up, *da[up]))
            elif up not in da:
                edge_diff.append('%s/%s: %s 에만 간선 -> %s [%s %.1f]' % (ia, ib, label_b, up, *db[up]))
            elif da[up] != db[up]:
                edge_diff.append('%s/%s -> %s: %s [%s %.1f] vs %s [%s %.1f]'
                                 % (ia, ib, up, label_a, *da[up], label_b, *db[up]))
    for ia, ib in both:
        ca = {_lab(a2b[d]) if d in a2b else '?' + d for d, t, _ in ea[ia] if t == 'caveat'}
        cb = {d for x in _bs(ib) for d, t, _ in eb[x] if t == 'caveat'}
        if ca != cb:
            caveat_diff.append('%s/%s: caveat %s=%s vs %s=%s'
                               % (ia, _lab(ib), label_a, sorted(ca) or '-', label_b, sorted(cb) or '-'))
    print('=== 그래프 대조: %s(%d) vs %s(%d) ===' % (label_a, len(a), label_b, len(b)), file=stream)
    print('(a) 양쪽이 잡은 주장 %d개' % len(both), file=stream)
    for ia, ib in both:
        print('    %-28s ~ %s' % (ia, _lab(ib)), file=stream)
    print('(b) %s 에만 있는 주장 %d개: %s' % (label_a, len(only_a), ', '.join(only_a) or '-'), file=stream)
    print('(c) %s 에만 있는 주장 %d개: %s' % (label_b, len(only_b), ', '.join(only_b) or '-'), file=stream)
    if edge_diff:
        print('간선 차이:', file=stream)
        for d in edge_diff:
            print('    ' + d, file=stream)
    if caveat_diff:
        print('caveat 부착 차이:', file=stream)
        for d in caveat_diff:
            print('    ' + d, file=stream)
    return {'both': both, 'only_a': only_a, 'only_b': only_b, 'edge_diff': edge_diff, 'caveat_diff': caveat_diff}


# ----------------------------------------------------------------------------
# 참고문헌 재번호 매핑 반영 (v15.4, 도구회신 #4)
#  verify_toolkit.renumber_references 가 낸 refmap json {"map": {"29": 26, "13": null, ...}} 을
#  statement · evidence 의 대괄호 인용 [n], [n-m], [n,m] 과 keys 의 "refs n-m" 에 적용한다.
#  keys 의 순수 숫자("42", "29-31")는 참여자 수 같은 값일 수 있어 기본은 손대지 않는다(--keys-are-refs).
# ----------------------------------------------------------------------------

def _refmap_load(path):
    import json
    with open(path, encoding='utf8') as f:
        d = json.load(f)
    m = d.get('map', d) if isinstance(d, dict) else d
    return {int(k): (None if v is None else int(v)) for k, v in m.items()}


def _expand_range(txt):
    out = []
    for part in re.split(r'\s*,\s*', txt.strip()):
        if re.search(r'[\-\u2013]', part):
            a, b = re.split(r'\s*[\-\u2013]\s*', part)
            out += list(range(int(a), int(b) + 1))
        elif part.isdigit():
            out.append(int(part))
    return out


def _compress_range(nums):
    nums = sorted(set(nums)); parts = []; i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        parts.append(str(nums[i]) if j == i else (f'{nums[i]},{nums[j]}' if j == i + 1 else f'{nums[i]}-{nums[j]}'))
        i = j + 1
    return ','.join(parts)


_REFS_KEY = re.compile(r'^refs?[:\s]+(\d{1,3}(?:\s*[,\-\u2013]\s*\d{1,3})*)$', re.I)
_BARE_RANGE = re.compile(r'^\d{1,3}(?:\s*[\-\u2013]\s*\d{1,3})?$')


def remap_refs(claims, refmap, stream=sys.stdout):
    """claims 를 제자리에서 갱신하고 변경 목록 [(id, 필드, 이전, 이후)] 을 반환.
    매핑에 없는 번호는 그대로 두고 [경고] 로 알린다. 삭제(null)된 번호는 인용에서 빠지고, 인용이 비면 [경고].
    v15.4.1: keys 의 순수 숫자는 어떤 옵션으로도 건드리지 않는다(`--keys-are-refs` 폐기 — 실물에서 참여자 수 42 가 39 로 바뀜).
    인용번호 key 는 `refs 29-31` 로 쓴다. 순수 숫자 key 가 대괄호 인용과 겹치면 [참고] 로만 알린다."""
    changes, warns = [], []
    def map_nums(nums, where):
        out = []
        for n in nums:
            if n not in refmap:
                warns.append('%s: [%d] 매핑에 없음 — 그대로 둠' % (where, n)); out.append(n)
            elif refmap[n] is None:
                warns.append('%s: [%d] 삭제된 문헌 — 인용에서 제거' % (where, n))
            else:
                out.append(refmap[n])
        return out
    def sub_text(text, where):
        def f(m):
            nums = map_nums(_expand_range(m.group(1)), where)
            return '[' + _compress_range(nums) + ']' if nums else ''
        def g(m):
            r = f(re.match(r'\s*\[(.*)\]', m.group(0)))
            return ((' ' if m.group(0).startswith(' ') else '') + r) if r else ''
        return _CITE_BRACKET.sub(g, text or '')
    for c in claims:
        for fld in ('statement', 'evidence'):
            old = c.get(fld, '')
            new = sub_text(old, '%s.%s' % (c['id'], fld))
            if new != old:
                c[fld] = new; changes.append((c['id'], fld, old, new))
        newkeys = []
        for k in c.get('keys', []):
            m = _REFS_KEY.match(k)
            if m:
                nums = map_nums(_expand_range(m.group(1)), '%s.keys' % c['id'])
                nk = re.sub(r'\d.*$', _compress_range(nums), k, count=1) if nums else None
            elif _BARE_RANGE.match(k):
                nk = k
                if all(n in refmap for n in _expand_range(k)):
                    warns.append('%s.keys %r: 순수 숫자 key — 매핑 범위 안이지만 건드리지 않음. 인용번호면 `refs %s` 로 바꿀 것' % (c['id'], k, k))
            else:
                nk = k
            if nk != k:
                changes.append((c['id'], 'keys', k, nk))
            if nk is not None:
                newkeys.append(nk)
        if newkeys != c.get('keys', []):
            c['keys'] = newkeys
        if 'verified' in c and any(ch[0] == c['id'] for ch in changes):
            warns.append('%s: verified 기록이 있는 주장 — statement/evidence 가 바뀌었으니 mapfreeze 를 다시 할 것' % c['id'])
    print('=== remap-refs: 변경 %d건, 경고 %d건 ===' % (len(changes), len(warns)), file=stream)
    for cid, fld, o, n in changes:
        print('    %s.%s: %r -> %r' % (cid, fld, o[:60], n[:60]), file=stream)
    for w in warns:
        print('    [경고] ' + w, file=stream)
    return changes


def _pairs_multi(kv):
    """v15.5: 같은 a_id 가 여러 번 나오면 1:N 짝 — 값을 리스트로."""
    out = {}
    for k, v in kv:
        k, v = k.strip(), v.strip()
        if k in out:
            out[k] = (out[k] if isinstance(out[k], list) else [out[k]]) + [v]
        else:
            out[k] = v
    return out


def parse_pairs(spec):
    """v15.4.1: --pairs 입력 파싱. 문자열 "a=b,c=d" / json 파일 {"a": "b"} / 텍스트 파일(한 줄에 a=b, # 주석 허용)."""
    import json
    if os.path.exists(spec):
        txt = open(spec, encoding='utf8').read()
        try:
            d = json.loads(txt)
            if not isinstance(d, dict):
                raise ValueError
            return {str(k): str(v) for k, v in d.items()}
        except ValueError:
            pass
        lines = [l.strip() for l in txt.splitlines() if l.strip() and not l.strip().startswith('#')]
        if lines and all('=' in l for l in lines):
            return _pairs_multi(l.split('=', 1) for l in lines)
        sys.exit('[오류] --pairs 파일 형식: json {"a_id": "b_id"} 이거나 한 줄에 a_id=b_id. 파일: %s' % spec)
    pairs = _pairs_multi(x.strip().split('=', 1) for x in spec.split(',') if '=' in x)
    if not pairs:
        sys.exit('[오류] --pairs 형식: "a1=b1,a2=b2" 또는 파일 경로')
    return pairs


# ----------------------------------------------------------------------------
# CLI (docx / md / txt 용. pptx 는 deck_toolkit 이 같은 명령을 제공한다)
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# 세트 자가 점검 (v15.6) — 세 프로젝트 모두에 있는 파일이 claim_graph.py 라서 여기에 둔다.
# 세션 시작 3단계(manifest 판 → 파일별 판 → 해시)와 프로젝트 파일 분류 (a)(b)(c) 를 한 명령으로,
# 결과는 도구회신 §1 에 그대로 붙일 수 있는 표로 낸다. 손으로 하던 대조에서 판·해시를 잘못 읽은 적은 없지만,
# 구판 잔존(manifest v5, CLAIM_GRAPH v15.4.2)·삭제 누락(manifest만_v9)·판 문자열 불일치(deck 16.7.3)는 전부
# 사람이 "이미 맞겠지" 하고 넘긴 곳에서 났다.
# ----------------------------------------------------------------------------

_C_PATTERNS = [
    (r'^TOOLS_MANIFEST_v\d+\.md$', '판 붙은 구 manifest'),
    (r'_릴리스_v[\d.]+\.md$', '구 릴리스 노트'),
    (r'_배포안내_', '구 배포안내'),
    (r'_manifest만_', '폐지된 manifest 만 세트'),
    (r'__\d+_\.[^.]+$', '__N_ 접미사 (업로드 중복)'),
    (r'^code_slimming_', '경량화 의견 (처리 완료)'),
    (r'\.diff$', 'fork diff'),
    (r'도구회신', '도구회신 사본 — 코드 프로젝트에 보냈으면 삭제'),
]


def _file_version(path):
    """코드 __version__ / 테스트 EXPECT_VERSION / 문서 첫 줄(또는 manifest 판 줄)의 vX.Y."""
    name = os.path.basename(path)
    txt = open(path, encoding='utf8', errors='replace').read(20000)
    if name.endswith('.py'):
        m = re.search(r"^(?:__version__|EXPECT_VERSION) = '([^']+)'", txt, re.M)
        return m.group(1) if m else None
    if name == 'TOOLS_MANIFEST.md':
        m = re.search(r'manifest 판: v([\d.]+)', txt)
        return m.group(1) if m else None
    first = txt.splitlines()[0] if txt else ''
    vs = re.findall(r'v(\d+(?:\.\d+)*)', first)
    return vs[-1] if vs else None


def _manifest_parse(text):
    """TOOLS_MANIFEST.md → (manifest 판, {파일: (판, 해시)}, {프로젝트: [파일...]})."""
    mv = re.search(r'manifest 판: v([\d.]+)', text)
    rows = {}
    for m in re.finditer(r'^\| `([^`]+)` \| v?([\d.]+)[^|]*\| `([0-9a-f]{12})` \|', text, re.M):
        rows[m.group(1)] = (m.group(2), m.group(3))
    sets, cols = {}, []
    sec = text[text.find('## 2.'):text.find('## 3.')] if '## 2.' in text else ''
    for line in sec.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if cells and cells[0] == '파일':
            cols = cells[1:]; sets = {c: [] for c in cols}; continue
        if not cols or len(cells) != len(cols) + 1 or cells[0].startswith('**') or set(cells[0]) <= set('-: '):
            continue
        names = [re.sub(r'\s*\(.*?\)', '', n).strip().strip('`') for n in cells[0].split('·')]
        for c, mark in zip(cols, cells[1:]):
            if mark in ('○', '진본'):
                sets[c] += names
    return (mv.group(1) if mv else None), rows, sets


def selfcheck(folder, run_tests=False, stream=sys.stdout, role=None, compare=None):
    """세트 자가 점검. 반환 {'ok': bool, 'project': str, 'problems': [...], 'delete': [...], 'other': [...]}
    v15.7 (GitHub 배포): role='발표' 등을 주면 프로젝트를 추정하지 않고 그 역할로 본다 — GitHub 에서 받은 폴더에는 모든 도구가
    다 있으므로(한 저장소, 역할별로 나누지 않음) 추정이 늘 '코드' 가 된다. 역할이 안 쓰는 도구는 삭제 후보가 아니라 '안 쓰는 도구'.
    compare='/mnt/project' 를 주면 그 폴더(예비로 둔 프로젝트 파일)와 판·해시를 대조한다."""
    import hashlib, subprocess
    mp = os.path.join(folder, 'TOOLS_MANIFEST.md')
    if not os.path.exists(mp):
        print('[중단] %s 에 TOOLS_MANIFEST.md 가 없다' % folder, file=stream)
        return {'ok': False, 'problems': ['manifest 없음'], 'project': None, 'delete': [], 'other': []}
    mver, rows, sets = _manifest_parse(open(mp, encoding='utf8').read())
    present = sorted(f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
    # 프로젝트 추정: 그 프로젝트가 받는 파일이 가장 많이 있고, 안 받는 도구 파일이 가장 적은 열
    tool_files = set(rows) | {'RELEASE.md', 'TOOLS_MANIFEST.md'}
    def score(c):
        need = set(sets[c]); have = need & set(present)
        extra = (tool_files & set(present)) - need
        return (len(have) - len(extra), -len(need - have))
    if role:
        if role not in sets:
            print('[중단] 역할 %r 이 manifest §2 에 없다 (%s)' % (role, ', '.join(sets)), file=stream)
            return {'ok': False, 'problems': ['역할 없음'], 'project': None, 'delete': [], 'other': []}
        project = role
    else:
        project = max(sets, key=score) if sets else None
    need = set(sets.get(project, []))
    problems, lines = [], []
    # 1단계
    rel = os.path.join(folder, 'RELEASE.md')
    rv = None
    if os.path.exists(rel):
        m = re.search(r'manifest v([\d.]+)', open(rel, encoding='utf8').readline())
        rv = m.group(1) if m else None
    s1 = rv == mver
    if not s1:
        problems.append('1단계: manifest 판 v%s ≠ RELEASE 첫 줄 v%s' % (mver, rv))
    lines.append('| ① manifest 판 | v%s / RELEASE v%s | %s |' % (mver, rv, '○' if s1 else '✗'))
    # v15.8: git clone 으로 받은 세트면 커밋 해시 — 받은 판을 회신에서 확정한다(tarball 은 판 식별자가 없다)
    if os.path.isdir(os.path.join(folder, '.git')):
        try:
            head = subprocess.run(['git', '-C', folder, 'log', '-1', '--format=%H %cd', '--date=format:%Y-%m-%d %H:%M'],
                                  capture_output=True, text=True, timeout=20).stdout.strip()
        except Exception:
            head = ''
        lines.append('| 받은 커밋 | `%s` | %s |' % (head[:12] + head[40:] if head else '(읽지 못함)', '○' if head else '—'))
    # 2·3단계
    for f in sorted(need & set(rows)):
        p = os.path.join(folder, f)
        if not os.path.exists(p):
            problems.append('받을 파일 없음: %s' % f); lines.append('| `%s` | 없음 | ✗ |' % f); continue
        want_v, want_h = rows[f]
        got_v = _file_version(p); got_h = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:12]
        ok = got_v == want_v and got_h == want_h
        if got_v != want_v:
            problems.append('2단계: %s 판 %s ≠ manifest %s' % (f, got_v, want_v))
        if got_h != want_h:
            problems.append('3단계: %s 해시 %s ≠ manifest %s' % (f, got_h, want_h))
        lines.append('| `%s` | %s `%s` | %s |' % (f, got_v, got_h, '○' if ok else '✗'))
    # ②′ RELEASE §3 교차 대조 (v15.6.1, 발표 요청): manifest 가 통째로 틀리면 manifest 기준으로는 전부 ○ 가 나온다.
    # release.py 가 두 문서를 같은 빌드에서 만들므로, 세트 파일(manifest 자신 포함) 해시를 RELEASE 표와도 맞춘다
    if os.path.exists(rel):
        rt = open(rel, encoding='utf8').read()
        sec = re.search(r'### %s \(\d+\)\n(.*?)(?=\n### |<!-- sets:end|\Z)' % re.escape(project or ''), rt, re.S)
        if not sec:
            problems.append('②′ RELEASE §3 에 %s 프로젝트 표가 없다' % project)
        else:
            bad = []
            for f, h in re.findall(r'\| `([^`]+)` \| [^|]+ \| `([0-9a-f]{12})` \|', sec.group(1)):
                fp = os.path.join(folder, f)
                if os.path.exists(fp) and hashlib.sha256(open(fp, 'rb').read()).hexdigest()[:12] != h:
                    bad.append(f)
            mh = hashlib.sha256(open(mp, 'rb').read()).hexdigest()[:12]
            lines.append('| ②′ RELEASE §3 대조 | TOOLS_MANIFEST `%s` 외 세트 파일 | %s |' % (mh, '○' if not bad else '✗ ' + ', '.join(bad)))
            for f in bad:
                problems.append('②′ %s 해시가 RELEASE §3 표와 다르다' % f)
    # 테스트
    tests = []
    if run_tests:
        for t in sorted(f for f in present if f.startswith('test_') and f.endswith('.py') and f in need):
            r = subprocess.run([sys.executable, os.path.join(folder, t)], capture_output=True, text=True, cwd=folder,
                               env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))   # v15.6.1: __pycache__ 부산물 방지
            last = (r.stdout.strip().splitlines() or ['(출력 없음)'])[-1]
            tests.append('| `%s` | %s |' % (t, last))
            if r.returncode != 0 or '실패 0' not in last or ('건너뜀' in last and '건너뜀 0' not in last):
                problems.append('테스트: %s — %s' % (t, last))
    # 분류
    delete, other = [], []
    for f in present:
        if f in need:
            continue
        why = next((w for pat, w in _C_PATTERNS if re.search(pat, f)), None)
        if f in tool_files or f == 'README.md' and role:
            if role:
                continue          # 전체 세트(GitHub)에서 이 역할이 안 쓰는 도구 — 정상
            why = '다른 프로젝트 소속 도구'
        (delete if why else other).append((f, why))
    # v15.7: 예비 폴더(프로젝트 파일)와 대조
    cmp_lines = []
    if compare and os.path.isdir(compare):
        cm = os.path.join(compare, 'TOOLS_MANIFEST.md')
        cv = _manifest_parse(open(cm, encoding='utf8').read())[0] if os.path.exists(cm) else None
        diff = [f for f in sorted(need) if os.path.exists(os.path.join(folder, f)) and os.path.exists(os.path.join(compare, f))
                and hashlib.sha256(open(os.path.join(folder, f), 'rb').read()).digest() != hashlib.sha256(open(os.path.join(compare, f), 'rb').read()).digest()]
        miss = [f for f in sorted(need) if not os.path.exists(os.path.join(compare, f))]
        cmp_lines.append('| 예비 폴더 `%s` | manifest v%s (받은 것 v%s) · 다른 파일 %d · 없는 파일 %d | %s |'
                         % (compare, cv, mver, len(diff), len(miss), '같음' if cv == mver and not diff and not miss else '다름 — 받은 것을 쓴다'))
    ok = not problems
    w = lambda s: print(s, file=stream)
    w('## 세트 자가 점검 (claim_graph selfcheck v%s) — %s %s' % (__version__, project, '역할(지정)' if role else '프로젝트로 추정'))
    w(''); w('| 항목 | 값 | 판정 |'); w('|---|---|---|')
    for l in lines + cmp_lines:
        w(l)
    if tests:
        w(''); w('| 테스트 | 결과 |'); w('|---|---|')
        for t in tests:
            w(t)
    w(''); w('**결과: %s**' % ('통과 — 작업 시작 가능' if ok else '불일치 %d건 — 작업 전에 사용자에게 알릴 것' % len(problems)))
    for p in problems:
        w('- %s' % p)
    w(''); w('**(c) 삭제 후보** — 사용자에게 목록으로 보고, 삭제는 사용자가 한다')
    for f, why in delete or [('(없음)', '')]:
        w('- `%s`%s' % (f, ' — ' + why if why else ''))
    w(''); w('**(b) 세트 밖 파일** — 고유 산출물로 추정. 판단이 서지 않으면 사용자에게 묻는다')
    for f, _ in other or [('(없음)', '')]:
        w('- `%s`' % f)
    return {'ok': ok, 'project': project, 'problems': problems, 'delete': [f for f, _ in delete], 'other': [f for f, _ in other]}


def main():
    import argparse
    ap = argparse.ArgumentParser(description='주장 의존 그래프 (문서 독립)')
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('mapgraph'); g.add_argument('--claims', required=True)
    i = sub.add_parser('impact'); i.add_argument('--claims', required=True); i.add_argument('ids', nargs='+')
    i.add_argument('--sites', action='store_true', help='자리 목록만 한 줄에 하나씩 (v15.5, 저자 v48 목록 검증용)')
    for name in ('mapcheck', 'mapfreeze', 'mapstale'):
        p = sub.add_parser(name); p.add_argument('doc'); p.add_argument('--claims', required=True)
        if name == 'mapfreeze':
            p.add_argument('-o', required=True)
        if name == 'mapcheck':
            p.add_argument('--nums', action='store_true', help='evidence 수치가 자리에 있는지도 본다')
            p.add_argument('--nums-sep', default=None, help='evidence 에서 이 구분자 앞쪽만 --nums 검사 (예 "|", v15.5)')
    r = sub.add_parser('mapreport'); r.add_argument('--claims', required=True)
    e = sub.add_parser('extract'); e.add_argument('doc'); e.add_argument('-o', required=True)
    e.add_argument('--min-score', type=int, default=2)
    s = sub.add_parser('scaffold'); s.add_argument('--claims', required=True)
    d = sub.add_parser('mapdiff'); d.add_argument('a'); d.add_argument('b')
    d.add_argument('--labels', nargs=2, default=['A', 'B'])
    d.add_argument('--pairs', help='수동 짝. 문자열 "a1=b1,a2=b2" 또는 파일 경로 — json {"a_id": "b_id"} 이거나 한 줄에 a_id=b_id 인 텍스트')
    rr = sub.add_parser('remap-refs', help='참고문헌 재번호 매핑으로 claims 의 인용번호 갱신 (v15.4, #4)')
    rr.add_argument('--claims', required=True); rr.add_argument('--map', required=True, dest='refmap')
    rr.add_argument('-o', required=True)
    rr.add_argument('--force', action='store_true', help='같은 매핑이 이미 적용된 그래프에도 다시 적용 (기본은 중단 — 두 번 적용하면 번호가 두 단계 밀린다)')
    sc = sub.add_parser('selfcheck', help='세트 자가 점검: 3단계 확인 + 파일 분류 + 회신용 표 (v15.6)')
    sc.add_argument('--dir', default=os.path.dirname(os.path.abspath(__file__)), help='세트가 있는 폴더 (기본: 이 파일의 폴더, 프로젝트에서는 /mnt/project)')
    sc.add_argument('--tests', action='store_true', help='그 프로젝트의 test_*.py 도 돌린다')
    sc.add_argument('--role', default=None, help='저자 / 발표 / 리뷰어 / 코드 — GitHub 에서 받은 전체 세트에서 쓸 역할 (v15.7)')
    sc.add_argument('--compare', default=None, help='예비 폴더(예: /mnt/project)와 판·해시 대조 (v15.7)')
    a = ap.parse_args()
    if a.cmd == 'selfcheck':
        r = selfcheck(a.dir, run_tests=a.tests, role=a.role, compare=a.compare)
        sys.exit(0 if r['ok'] else 1)
    if a.cmd == 'mapgraph':
        probs, _ = mapgraph(load_claims(a.claims))
        sys.exit(1 if any(not p.startswith('[참고]') for p in probs) else 0)
    elif a.cmd == 'impact':
        if a.sites:
            cl = load_claims(a.claims)
            rows = impact(cl, a.ids, stream=io.StringIO())
            by_id = {c['id']: c for c in cl}
            seen = []
            for cid in a.ids + [r[0] for r in rows if r[1] >= IMPACT_CUTOFF]:
                for s in by_id.get(cid, {}).get('sites', []):
                    if s not in seen:
                        seen.append(s); print(s)
        else:
            impact(load_claims(a.claims), a.ids)
    elif a.cmd == 'mapreport':
        mapreport(load_claims(a.claims))
    elif a.cmd == 'scaffold':
        scaffold(load_claims(a.claims))
    elif a.cmd == 'mapdiff':
        pairs = parse_pairs(a.pairs) if a.pairs else None
        mapdiff(load_claims(a.a), load_claims(a.b), a.labels[0], a.labels[1], pairs=pairs)
    elif a.cmd == 'remap-refs':
        import hashlib, json
        meta, cl = load_claims_full(a.claims)
        tag = {'map': norm_name(a.refmap), 'sha': hashlib.sha256(open(a.refmap, 'rb').read()).hexdigest()[:12]}
        applied = meta.get('refs_maps_applied', [])
        if any(x.get('sha') == tag['sha'] for x in applied) and not a.force:
            print('[중단] 이 매핑(%s, sha %s)은 이미 적용된 그래프입니다 — 두 번 적용하면 번호가 두 단계 밀립니다. 확실하면 --force' % (tag['map'], tag['sha']))
            sys.exit(2)
        remap_refs(cl, _refmap_load(a.refmap))
        meta['refs_maps_applied'] = applied + [tag]
        print('저장: %s' % save_claims(a.o, cl, meta=meta))
    elif a.cmd == 'extract':
        src = DocSource(a.doc)
        cands = extract(src.units(), a.min_score)
        save_claims(a.o, cands, os.path.basename(a.doc), 'extract 초안 — 사람이 확정해야 함')
        print('저장: %s' % a.o)
    else:
        src = DocSource(a.doc)
        if a.cmd == 'mapcheck':
            probs, _ = mapcheck(src.resolve, load_claims(a.claims), nums=a.nums, nums_sep=a.nums_sep)
            sys.exit(1 if any(not p.startswith('[참고]') for p in probs) else 0)
        elif a.cmd == 'mapfreeze':
            meta, cl = load_claims_full(a.claims)
            mapfreeze(src.resolve, cl)
            print('기록 완료: %s' % save_claims(a.o, cl, meta=meta, doc=a.doc))
        elif a.cmd == 'mapstale':
            meta, cl = load_claims_full(a.claims)
            stale_doc = meta.get('doc') or meta.get('deck')
            if stale_doc and doc_name(stale_doc) != doc_name(a.doc):
                print('[경고] 그래프의 doc=%s 와 대상 %s 가 다름 — 다른 판에 대한 freeze 일 수 있음' % (doc_name(stale_doc), doc_name(a.doc)))
            r = mapstale(src.resolve, cl)
            sys.exit(1 if (r['changed'] or r['unverified']) else 0)


if __name__ == '__main__':
    main()
