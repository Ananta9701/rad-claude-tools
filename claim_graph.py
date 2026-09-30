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
    doc:p:N                        (docx, N 번째 비어있지 않은 문단 — 1부터. 삽입에 약함)
    doc:find:<문구>                (docx, 그 문구가 들어 있는 문단. 삽입에 강함 — 권장)
    doc:sec:<제목>                 (docx, 그 제목 문단부터 다음 제목 전까지)
    doc:tbl:N                      (docx, N 번째 표 전체 — 1부터, 0 이나 표 수보다 크면 읽을 수 없음)

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
    sources: [{kind, what, at, element?, verdict?, via?, pdf?, date?, note?}]  (v16, 선택 — 근거 칸)
          kind 문헌|교과서|덱|원고|기타, what = DOI·책 폴더·파일, at = 쪽 표지 [p.인쇄 · PDF N]·절 표지 [§ …]·slide@sldId.
          verdict(요소별 판정) 부합|부분|근거 없음|반대 방향. mapfreeze/mapstale --sources 폴더 로 원문 바뀜을 본다
    supersedes: {statement, retracted} 또는 그 목록(v16 — 범위를 좁힌 이력, 마지막이 가장 최근)
    exploratory: true|false, exploratory_reason: 문장   (v16.17, 선택 — 탐색적 주장. main 의 premise 사슬에 있으면 사유 없이는 [필수])

원리는 소프트웨어에서 가져왔다: 빌드 시스템의 의존 DAG + 내용 해시(바뀐 것과 하류만
다시), 요구사항 추적의 suspect link(상류가 바뀌면 사람이 풀 때까지 의심), 스프레드시트의
위상 순서 재계산(순환은 기본 오류), ADR 의 superseded 상태.
"""

import html
import io
import os
import re
import sys
import unicodedata
import zipfile

__version__ = '16.21'   # TOOLS_MANIFEST 와 대조. 판이 오르면 여기와 test_claim_graph.EXPECT_VERSION 을 함께 올린다
# 코드 프로젝트 전용 파일(v15.8.2, 코드 v2.43) — 비공개 저장소에 있고 릴리스 사이에도 바뀐다. selfcheck ②′ RELEASE 대조에서 뺀다
CODE_ONLY = ('HISTORY.md', 'PRIVATE_TERMS.txt', 'CODE_PROJECT_README.md', 'release.py', 'GITHUB_README.md')

EDGE_TYPES = ('premise', 'support', 'context', 'caveat', 'rebuttal')
# v16 (저자·리뷰어 09-29): rebuttal = 반대 증거. caveat(한계)와 같은 방향 — 반박당하는 주장이 반박하는 쪽을 depends_on 에 적는다
EDGE_DEFAULT_WEIGHT = {'premise': 1.0, 'support': 0.7, 'context': 0.3, 'caveat': 0.5, 'rebuttal': 0.5}
SOURCE_KINDS = ('문헌', '교과서', '덱', '원고', '기타')
VERDICTS = ('부합', '부분', '근거 없음', '반대 방향')
IMPACT_CUTOFF = 0.25
CLAIM_STATUS = ('accepted', 'proposed', 'superseded', 'excluded')   # v16.6 (발표 K23): excluded = 배제된 감별 — 자리에 계속 실린다(superseded 와 다름)
CASE_KINDS = ('증례', 'case')
LIT_KINDS = ('문헌',)   # v16.19 (④ 1판): 논문 그래프 — 문헌 보관소/<DOI>/claims.json, 자리는 그 논문의 paper.md   # v16.6: 그래프 맨 위 kind — 논문용 [참고] 일부를 끈다
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

_PAPER_MARK = re.compile(r'^(\[p\.[^\]]*\]|\[§ [^\]]*\])\s*$', re.M)


def _fold(s):
    """v16.19: 찾기·해시용 — 글자마다 NFKC(합자 ﬂ→fl, 위첨자 ²→2, 전각→반각), literature._fold 와 같은 규칙."""
    return ''.join(unicodedata.normalize('NFKC', ch) if ord(ch) > 127 else ch for ch in unicodedata.normalize('NFC', s))


def _fold_re(term):
    core = re.sub(r'\s+', '', _fold(term))
    return re.compile(r'\s*'.join(map(re.escape, core)), re.I)


_HYPH_BREAK = re.compile(r'(?<=[A-Za-z]) ?[-­‐][ \t]*\n\s*(?=[a-z])')   # v16.20: 줄 끝 하이픈 + 소문자로 시작하는 다음 줄


def _norm_line(s):
    return re.sub(r'\s+', ' ', _fold(s)).strip()


def _running_res(pages):
    """v16.20 (④ 1판 실물 09-30): 쪽 머리·꼬리 — 쪽 표지 `[p.…]` 쪽이 3쪽 이상일 때, 쪽 위·아래 세 줄 안에서 쪽 절반 이상(3쪽 이상)에
    되풀이되는 줄 앞머리(숫자는 같게 본다, 12자 이상, 쪽 번호가 들었거나 그만큼의 쪽에서 줄 전체). 쪽 꼬리가 줄바꿈 없이 본문에 붙어 나오므로
    줄 전체가 아니라 앞머리로 본다.
    같은 쪽 수를 가진 앞머리 중 가장 긴 것 — 그보다 긴데 쪽 수가 줄면 본문으로 본다(쪽 첫 낱말이 우연히 같은 경우)."""
    pages = [t for mk, t in pages if mk.startswith('[p.')]
    if len(pages) < 3:
        return []
    need = max(3, (len(pages) + 1) // 2)
    cands = []
    for pi, t in enumerate(pages):
        ls = [l for l in t.split('\n') if l.strip()]
        for l in set(ls[:3] + ls[-3:]):
            cands.append((re.sub(r'\d+', '#', _norm_line(l)), pi))
    cands.sort()
    pre = {a[:next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))]
           for (a, pa), (b, pb) in zip(cands, cands[1:]) if pa != pb}
    count = {p: len({pi for c, pi in cands if c.startswith(p)}) for p in pre if len(p.strip()) >= 12}
    whole = {p: len({pi for c, pi in cands if c == p}) for p in count}
    ok = {p: n for p, n in count.items() if n >= need and ('#' in p or whole[p] >= need)}   # 쪽 번호가 들었거나 쪽 절반 이상에서 줄 전체 — 흔한 문장 첫머리('In addition, the')는 아니다
    keep = [p for p in ok if not any(q != p and q.startswith(p) and ok[q] == ok[p] for q in ok)          # 더 긴 같은 쪽 수가 있으면 짧은 것은 뺀다
            and not any(q != p and p.startswith(q) and ok[q] > ok[p] for q in ok)]                       # 짧은 쪽이 더 많이 나오면 긴 것은 본문
    return [re.compile(r'\d+'.join(r'\s*'.join(map(re.escape, piece.split(' '))) for piece in p.strip().split('#')))
            for p in sorted(keep, key=len, reverse=True)]


def _strip_running(t, res):
    """쪽 글 t 의 위·아래 세 줄에서 쪽 머리·꼬리 앞머리를 뺀다(남는 글이 없으면 그 줄을 지운다)."""
    if not res:
        return t
    ls = t.split('\n')
    nz = [i for i, l in enumerate(ls) if l.strip()]
    for i in set(nz[:3] + nz[-3:]):
        s = _norm_line(ls[i])
        for r in res:
            m = r.match(s)
            if m:
                s = s[m.end():].strip()
        ls[i] = s if s else None
    return '\n'.join(l for l in ls if l is not None)


def _paper_paras(txt):
    """v16.19 (④ 1판): 쪽·절 표지가 있는 md → (표지 목록, 문단 목록, 찾기 사본 목록). literature locate 와 같은 나눔 — 표지 줄로 쪽을 나누고,
    그 안에서 빈 줄이나 . : 로 끝난 줄 뒤에서 문단을 끊는다(PDF 글자층은 한 줄이 물리적 줄). 문단은 NFKC·띄어쓰기 하나로.
    v16.20: 쪽 머리·꼬리를 뺀다 · 찾기 사본은 줄 끝 하이픈 낱말을 붙인 꼴(문단 글 자체는 원문 그대로)."""
    marks, paras, joined = [], [], []
    parts = _PAPER_MARK.split(txt)
    pages = [(parts[k].strip(), parts[k + 1]) for k in range(1, len(parts) - 1, 2)]
    res = _running_res(pages)
    for mk, t in pages:
        if mk.startswith('[p.'):
            t = _strip_running(t, res)
        for para in re.split(r'\n\s*\n|(?<=[.:])\n', t):
            flat = re.sub(r'\s+', ' ', _fold(para)).strip()
            if flat:
                marks.append(mk); paras.append(flat)
                joined.append(re.sub(r'\s+', ' ', _fold(_HYPH_BREAK.sub('', para))).strip())
    return marks, paras, joined


def _mark_at(mark):
    """v16.20: 옛 쪽 표지 `[p.N]`(N = PDF 쪽 — literature 0.6 까지)는 `PDF N`, `[p.N · 인쇄]` 는 `[p.인쇄 · PDF N]` 으로 풀어 적는다.
    새 표지 `[p.인쇄 · PDF N]`·절 표지는 그대로(literature `_mark_label` 과 같은 판단 — 인쇄 쪽으로 읽히지 않게)."""
    m = re.match(r'^\[p\.\s*(\d+)(?:\s*·\s*([^\]]*?))?\s*\]$', mark.strip())
    if not m or 'PDF' in mark:
        return mark
    return ('[p.%s · PDF %s]' % (m.group(2).strip(), m.group(1))) if (m.group(2) or '').strip() else 'PDF %s' % m.group(1)


class DocSource:
    """docx 를 문단 목록으로 읽고 doc:* 자리를 해석한다."""

    def __init__(self, path):
        self.path = path
        self.marks = None                 # v16.19: 쪽·절 표지가 있는 md(literature paper.md·교과서 분할)면 문단마다 표지
        if not path.lower().endswith('.docx'):
            txt = open(path, encoding='utf8', errors='ignore').read()
            if _PAPER_MARK.search(txt):
                self.marks, self.paras, self.joined = _paper_paras(txt)
                self.headings, self.tables = set(), []
                return
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

    def mark_of(self, site):
        """v16.19: 자리가 든 문단의 쪽·절 표지(표지 있는 md 만 — 아니면 None). sources 의 at 을 적을 때."""
        if self.marks is None:
            return None
        t = self.resolve(site)
        return _mark_at(self.marks[self.paras.index(t)])     # v16.20: 옛 표지 [p.N] 은 PDF N 으로

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
        if sub in ('p', 'tbl'):     # v16.9 (리뷰어 09-29): 0 이 파이썬 음수 번호로 마지막 문단·표를 돌려주던 것
            seq = self.paras if sub == 'p' else self.tables
            n = int(arg)
            if not 1 <= n <= len(seq):
                raise KeyError('doc:%s:%d — 번호는 1부터 %d 까지(%s %d개)' % (sub, n, len(seq), '문단' if sub == 'p' else '표', len(seq)))
            return seq[n - 1] if sub == 'p' else ' '.join(seq[n - 1])
        if sub == 'find' and self.marks is not None:   # v16.19: literature locate 와 같게 — NFKC(합자)·띄어쓰기 무시
            pat = _fold_re(arg)
            hits = [p for p, j in zip(self.paras, self.joined) if pat.search(p) or pat.search(j)]   # v16.20: 줄 끝 하이픈 낱말을 붙인 사본으로도
            if not hits:
                raise KeyError('문구를 가진 문단 없음: %s' % arg)
            if len(hits) > 1:
                raise KeyError('문구가 %d개 문단에 있어 모호함: %s' % (len(hits), arg))
            return hits[0]
        if sub == 'sec' and self.marks is not None:    # v16.19: 절 = 표지(쪽 `PDF 2` · 절 `Methods`) — 처음 맞는 표지의 문단 전부
            want = _page_of(arg)                          # v16.20: 쪽이면 쪽 번호로(옛 표지 [p.N] 도 · PDF 1 이 PDF 10 을 집지 않게), 아니면 글자로
            if want != (None, None):
                m = next((mk for mk in self.marks if mk.startswith('[p.') and
                          (_page_of(_mark_at(mk))[1] == want[1] if want[1] is not None else _page_of(_mark_at(mk))[0] == want[0])), None)
            else:
                m = next((mk for mk in self.marks if arg.lower() in mk.lower()), None)
            if m is None:
                raise KeyError('표지 없음: %s' % arg)
            return ' '.join(p for p, mk in zip(self.paras, self.marks) if mk == m)
        if sub == 'find':
            hits = [p for p in self.paras if arg.lower() in p.lower()]
            if not hits:
                raise KeyError('문구를 가진 문단 없음: %s' % arg)
            if len(hits) > 1:
                raise KeyError('문구가 %d개 문단에 있어 모호함: %s' % (len(hits), arg))
            return hits[0]
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

def _supersedes(c):
    """v16 (저자 09-29 '다듬음'): supersedes 는 하나(dict) 또는 이력 목록. 늘 목록으로, 마지막이 가장 최근."""
    sp = c.get('supersedes') or []
    return [x for x in (sp if isinstance(sp, list) else [sp]) if isinstance(x, dict)]


def _source_problems(c, edges, root=None):
    """v16 근거 칸 검사 — kind·what 필수, at 권장, verdict 는 정해진 넷, 덱 자리는 sldId.
    v16.5 (사용자 09-29): root(문헌 보관소)를 주면 문헌 근거의 DOI 가 보관소에 없을 때 [필수], 판정(verdict)이 없으면 [참고]."""
    out, srcs = [], c.get('sources')
    if srcs is None:
        return out
    if not isinstance(srcs, list):
        return ['%s: sources 는 목록이어야 함' % c['id']]
    for k, x in enumerate(srcs, 1):
        tag = '%s: sources[%d]' % (c['id'], k)
        if not isinstance(x, dict):
            out.append('%s 는 {kind, what, at, …} 이어야 함' % tag); continue
        if x.get('kind') not in SOURCE_KINDS:
            out.append('%s: kind "%s" 는 %s 중 하나여야 함' % (tag, x.get('kind'), '/'.join(SOURCE_KINDS)))
        if not x.get('what') and x.get('kind') not in ('덱', '원고'):
            out.append('%s: what(DOI·책·파일)이 비어 있음' % tag)
        if not x.get('at'):
            out.append('[참고] %s: at(쪽·절·화면)이 없음 — 원문 전체로 본다' % tag)
        if x.get('verdict') and x['verdict'] not in VERDICTS:
            out.append('%s: verdict "%s" 는 %s 중 하나여야 함' % (tag, x['verdict'], '/'.join(VERDICTS)))
        if x.get('kind') == '덱' and re.match(r'^(slide|notes):\d+$', str(x.get('at', ''))):
            out.append('[참고] %s: 덱 자리 %s 는 파일 번호 — 화면이 밀리면 틀린다. slide@sldId 로(deck_toolkit mapcheck --to-sldid)' % (tag, x['at']))
        if x.get('verdict') == '반대 방향' and not any(t == 'rebuttal' for _, t, _ in edges.get(c['id'], [])):
            out.append('[참고] %s: 반대 방향 근거 — 반박 노드를 만들어 type rebuttal 로 걸지 확인' % tag)
        if root and x.get('kind') == '문헌' and x.get('what'):
            try:
                _source_file(root, x)
            except (KeyError, OSError):
                out.append('%s: 문헌 %s 가 보관소에 없다 — 원문을 받지 않은 근거는 sources 에 넣지 않는다(작업표에 둔다)' % (tag, x['what']))
            else:
                if not x.get('verdict'):
                    out.append('[참고] %s: 문헌 %s 판정(verdict)이 없다 — 리뷰어 판정 대기' % (tag, x['what']))
    return out


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


_DOI_SHAPE = re.compile(r'^10\.\d{4,9}/\S+$')
# v16.19: 사람 이름 꼴 — 논문 그래프는 DOI 로만(사용자 09-29). 다 잡지 못한다: et al · (이름, 연도) · 이름 연도 · 이름 and/& 이름
_NAME_LIKE = re.compile(r'\bet\s+al\b|\(\s*[A-Z][a-z]+,?\s+(?:19|20)\d\d[a-z]?\s*\)|\b[A-Z][a-z]{2,}\s+(?:19|20)\d\d\b|\b[A-Z][a-z]+\s+(?:and|&)\s+[A-Z][a-z]+\b')


def lit_graph_problems(meta, claims, path=None):
    """v16.19 (④ 1판): kind 문헌 그래프(문헌 보관소/<DOI>/claims.json)의 맨 위·이름 검사. [참고] 가 아니면 [필수].
    같은 폴더에 meta.md 가 있으면 doi(= [필수])·원 파일 sha(paper_sha — 다르면 [참고] 논문 판이 바뀜)를 대조한다."""
    out = []
    doi = str(meta.get('doi') or '').strip().lower().replace('https://doi.org/', '')
    if not doi:
        out.append('문헌 그래프에 doi 가 없다 — 맨 위 "doi": "10.xxxx/…"')
    elif not _DOI_SHAPE.match(doi):
        out.append('doi "%s" 가 DOI 모양(10.xxxx/…)이 아니다' % doi)
    if doi and str(meta.get('doc') or '').strip().lower() != doi:
        out.append('[참고] doc(%s) 이 doi 와 다르다 — 문헌 그래프는 doc 도 DOI 로' % meta.get('doc'))
    mp = os.path.join(os.path.dirname(os.path.abspath(path)), 'meta.md') if path else None
    if mp and os.path.exists(mp):
        head = open(mp, encoding='utf8').readline()
        m = re.search(r'doi=(\S+)', head); sha = re.search(r'sha=([0-9a-f]+)', head)
        if doi and m and m.group(1).lower() != doi:
            out.append('doi %s 가 같은 폴더 meta.md 의 doi %s 와 다르다 — 다른 논문 폴더에 둔 그래프' % (doi, m.group(1)))
        if sha and not meta.get('paper_sha'):
            out.append('[참고] paper_sha 가 없다 — meta.md 의 sha(%s) 를 적어 두면 논문 판이 바뀐 것을 알린다' % sha.group(1))
        elif sha and meta.get('paper_sha') != sha.group(1):
            out.append('[참고] paper_sha(%s) 가 meta.md 의 sha(%s) 와 다르다 — 논문 판이 바뀌었다(선공개 → 게재·정정). mapstale 로 자리를 다시 본다'
                       % (meta.get('paper_sha'), sha.group(1)))
    for c in claims:
        cid = str(c.get('id', ''))
        if re.search(r'[:#\s]', cid):
            out.append('%s: 문헌 그래프 id 에 : # 빈칸을 쓰지 않는다(우리 그래프에서 lit:<DOI>#<id> 로 부른다)' % cid)
        bad = [x for x in c.get('sites', []) if not str(x).startswith('doc:')]
        if bad:
            out.append('[참고] %s: 자리 %s — 문헌 그래프의 자리는 그 논문 paper.md 의 doc:find·doc:sec' % (cid, ', '.join(map(str, bad))))
        txt = ' '.join([c.get('statement', '') or '', c.get('evidence', '') or ''] + list(c.get('keys', [])) + list(map(str, c.get('sites', []))))
        hit = sorted({m.group(0) for m in _NAME_LIKE.finditer(txt)})
        if hit:
            out.append('[참고] %s: 사람 이름 꼴 %s — 문헌 그래프는 사람 이름 없이(DOI 로만). 인용 구절이면 이름 없는 구절로 바꾼다'
                       % (cid, ', '.join('"%s"' % h for h in hit)))
    pend = [c['id'] for c in claims if c.get('status') == 'proposed']
    if pend:
        out.append('[참고] 판정 대기(proposed) %d개%s — 리뷰어가 paper.md 를 읽고 accepted/고침/뺌'
                   % (len(pend), ' (AI 초안 %d)' % sum(1 for c in claims if c.get('status') == 'proposed' and c.get('origin') == 'ai')
                      if any(c.get('origin') == 'ai' for c in claims) else ''))
    return out


# v16.21 (④ 2판, 사용자 09-30 결정 1·2·5): 우리 주장 ↔ 논문 주장 짝 — 우리 그래프 맨 위 `lit_links`. rel(우리 쪽에서) → 합친 그래프의 간선 type
LIT_RELS = {'same': 'support', 'support': 'support', 'rebut': 'rebuttal', 'background': 'context'}


def lit_id(doi, theirs):
    """합친 그래프에서 논문 주장의 id — lit:<DOI>#<그 논문 그래프의 id>."""
    return 'lit:%s#%s' % (doi, theirs)


def _lit_doi(s):
    return str(s or '').strip().lower().replace('https://doi.org/', '')


def _lit_dir(store, doi):
    """보관소에서 meta.md 첫 줄의 doi= 가 같은 폴더(없으면 None) — sources 의 문헌 찾기(_source_file)와 같은 규칙."""
    for d in (sorted(os.listdir(store)) if os.path.isdir(store) else []):
        mp = os.path.join(store, d, 'meta.md')
        if os.path.exists(mp):
            m = re.search(r'doi=(\S+)', open(mp, encoding='utf8').readline())
            if m and m.group(1).lower() == doi:
                return os.path.join(store, d)
    return None


def _main_chain(claims):
    """{살아 있는 main: premise 만 따라 닿는 주장 집합(main 포함)} — 탐색적 표지의 전제 사슬과 같은 정의."""
    by = {c['id']: c for c in claims}
    edges = _edges(claims)
    out = {}
    for c in claims:
        if c.get('role') != 'main' or c.get('status') in ('superseded', 'excluded'):
            continue
        seen, st = set(), [c['id']]
        while st:
            v = st.pop()
            if v in seen or v not in by:
                continue
            seen.add(v)
            st += [u for u, t, _ in edges.get(v, []) if t == 'premise']
        out[c['id']] = seen
    return out


def lit_merge(meta, claims, store):
    """v16.21 (④ 2판): 우리 그래프 + `lit_links` 가 가리키는 논문 주장만 → (합친 claims, 문제 목록). 문제: [참고] 가 아니면 [필수].
    논문 주장은 id `lit:<DOI>#<id>`, `lit: true` — 자리·keys·간선·sources 없이(자리 검사는 그 논문 paper.md 에서 한다), 역할은 `lit_role` 로.
    우리 주장에 간선 하나(rel → type, weight 는 type 기본값). 합친 파일을 남기지 않는다(구연 덧붙임과 같은 방식). 우리 파일은 바꾸지 않는다.
    [필수]: 모양 · ours 없음 · rel·verdict 값 · 보관소에 없는 DOI · 논문 claims.json 없음/다른 논문 · theirs 없음 ·
            **판정 안 된(proposed) 논문 주장이 same·support 로 main 의 전제(premise) 사슬을 받침**(결정 5).
    [참고]: verdict 없음 · 우리 주장 sources 에 같은 DOI 없음 · 같은 짝 두 번 · 사람 이름 꼴 · 철회된(superseded) 논문 주장."""
    import copy as _copy
    links = meta.get('lit_links')
    if links is None:
        return claims, []
    if not isinstance(links, list):
        return claims, ['lit_links 는 목록이어야 함 — [{"ours", "doi", "theirs", "rel", "verdict", "by", "date"}, …]']
    probs, out = [], _copy.deepcopy(claims)
    by = {c['id']: c for c in out}
    papers, added, seen, backs = {}, {}, set(), []
    for k, l in enumerate(links, 1):
        if not isinstance(l, dict):
            probs.append('lit_links[%d] 는 {ours, doi, theirs, rel, …} 이어야 함' % k); continue
        ours, doi, theirs, rel = l.get('ours'), _lit_doi(l.get('doi')), str(l.get('theirs') or ''), l.get('rel')
        tag = 'lit_links[%d] %s → %s' % (k, ours, lit_id(doi, theirs))
        bad = False
        if ours not in by:
            probs.append('%s: ours "%s" 가 우리 그래프에 없다' % (tag, ours)); bad = True
        if rel not in LIT_RELS:
            probs.append('%s: rel "%s" 는 %s 중 하나여야 함' % (tag, rel, '/'.join(LIT_RELS))); bad = True
        if l.get('verdict') and l['verdict'] not in VERDICTS:
            probs.append('%s: verdict "%s" 는 %s 중 하나여야 함' % (tag, l['verdict'], '/'.join(VERDICTS))); bad = True
        if not _DOI_SHAPE.match(doi):
            probs.append('%s: doi "%s" 가 DOI 모양(10.xxxx/…)이 아니다' % (tag, l.get('doi'))); continue
        if doi not in papers:
            dd = _lit_dir(store, doi)
            if dd is None:
                papers[doi] = ('보관소에 없다 — 원문을 받은 논문만 짝을 맺는다', None)
            elif not os.path.exists(os.path.join(dd, 'claims.json')):
                papers[doi] = ('논문 그래프 %s/claims.json 이 없다 — 초안(문헌 Cowork)·판정(리뷰어) 뒤에 짝을 맺는다' % os.path.basename(dd), None)
            else:
                pm, pc = load_claims_full(os.path.join(dd, 'claims.json'))
                if pm.get('kind') not in LIT_KINDS or _lit_doi(pm.get('doi')) != doi:
                    papers[doi] = ('%s/claims.json 이 이 논문의 문헌 그래프가 아니다(kind %s · doi %s)'
                                   % (os.path.basename(dd), pm.get('kind'), pm.get('doi')), None)
                else:
                    papers[doi] = (None, {c.get('id'): c for c in pc})
            if papers[doi][0]:
                probs.append('문헌 %s: %s' % (doi, papers[doi][0]))
        err, pby = papers[doi]
        if err:
            continue
        if theirs not in pby:
            probs.append('%s: 논문 그래프에 주장 "%s" 가 없다' % (tag, theirs)); continue
        if bad:
            continue
        if (ours, doi, theirs) in seen:
            probs.append('[참고] %s: 같은 짝이 두 번 — 하나만 둔다' % tag); continue
        seen.add((ours, doi, theirs))
        lid = lit_id(doi, theirs)
        if lid not in added:
            p_ = pby[theirs]
            node = {'id': lid, 'lit': True, 'statement': p_.get('statement', ''), 'status': p_.get('status', 'accepted'),
                    'confidence': p_.get('confidence', 'mid'), 'sites': [], 'keys': [], 'depends_on': []}
            for f in ('role', 'origin'):
                if p_.get(f):
                    node['lit_role' if f == 'role' else f] = p_[f]
            added[lid] = node
            nm = sorted({m.group(0) for m in _NAME_LIKE.finditer(node['statement'])})
            if nm:
                probs.append('[참고] %s: 사람 이름 꼴 %s — 논문 주장도 사람 이름 없이' % (lid, ', '.join('"%s"' % h for h in nm)))
            if node['status'] == 'superseded':
                probs.append('[참고] %s: 논문 그래프에서 철회된(superseded) 주장과 짝 — 정정·철회 논문인지 본다' % lid)
        by[ours].setdefault('depends_on', []).append({'id': lid, 'type': LIT_RELS[rel]})
        if rel in ('same', 'support'):
            backs.append((ours, lid))
        if not l.get('verdict'):
            probs.append('[참고] %s: verdict 없음 — 리뷰어 판정 전%s' % (tag, ' (%s)' % l['by'] if l.get('by') else ''))
        if not any(isinstance(x, dict) and x.get('kind') == '문헌' and _lit_doi(x.get('what')) == doi for x in (by[ours].get('sources') or [])):
            probs.append('[참고] %s: 우리 주장 %s 의 sources 에 같은 DOI 가 없다 — 원문 자리(at)·판정은 sources 에' % (tag, ours))
    out += list(added.values())
    chain = _main_chain(out)
    for ours, lid in backs:
        ms = sorted(m for m, s in chain.items() if ours in s)
        if ms and added[lid]['status'] == 'proposed':
            probs.append('%s: 판정 전(proposed) 논문 주장 %s 이 main(%s) 의 전제 사슬에 있는 %s 을 받친다 — 리뷰어가 paper.md 로 판정(accepted)한 뒤에 쓴다'
                         % (ours, lid, ', '.join(ms), ours))
    return out, probs


def _exploratory_paths(claims):
    """v16.17 (사용자 09-30 ③): 탐색적 주장(exploratory true, 철회·배제 아님)마다 (단계, [main]).
    단계 chain = main 에서 premise 만 따라 닿음(main 자신 포함) · mixed = premise·support 로만 닿음 · off = 그 밖."""
    by = {c['id']: c for c in claims}
    edges = _edges(claims)
    live = lambda c: c.get('status') not in ('superseded', 'excluded')

    def up_from(m, types):
        seen, st = set(), [m]
        while st:
            v = st.pop()
            if v in seen or v not in by:
                continue
            seen.add(v)
            st += [u for u, t, _ in edges.get(v, []) if t in types]
        return seen
    mains = [c['id'] for c in claims if c.get('role') == 'main' and live(c)]
    chain = {m: up_from(m, ('premise',)) for m in mains}
    mixed = {m: up_from(m, ('premise', 'support')) for m in mains}
    out = {}
    for c in claims:
        if c.get('exploratory') is not True or not live(c):
            continue
        ms = [m for m in mains if c['id'] in chain[m]]
        if ms:
            out[c['id']] = ('chain', ms)
            continue
        ms = [m for m in mains if c['id'] in mixed[m]]
        out[c['id']] = ('mixed', ms) if ms else ('off', [])
    return out


def mapgraph(claims, stream=sys.stdout, sources=None, kind=None):
    """구조 검사 + 위상 순서. 반환 (문제목록, 순서). sources(v16.5) = 문헌 보관소 — 주면 문헌 근거가 보관소에 있는지·판정이 있는지도.
    kind(v16.6) = 그래프 맨 위 kind. '증례' 면 논문용 [참고](forbidden 인데 supersedes 없음 · evidence 인데 caveat 없음 · main 개수)를 끈다."""
    case = kind in CASE_KINDS
    lit = kind in LIT_KINDS           # v16.19: 논문 그래프는 짝이 될 주장만 뽑는다 — caveat 없는 evidence · forbidden 만 [참고] 는 끈다
    ids = {c['id'] for c in claims}
    problems = []
    edges = _edges(claims)
    by_id = {c['id']: c for c in claims}
    noedge = len(claims) > 1 and not any(edges.values())   # v16.3: 간선 0 그래프 — 주장별 간선 [참고] 는 요약 한 줄로 합친다
    folded = {'premise': 0, 'caveat': 0}
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
        if 'exploratory' in c and not isinstance(c['exploratory'], bool):   # v16.17
            problems.append('%s: exploratory 는 true/false 여야 함 (지금 %r)' % (c['id'], c['exploratory']))
        if c.get('exploratory_reason') and c.get('exploratory') is not True:
            problems.append('[참고] %s: exploratory_reason 이 있는데 exploratory 가 true 가 아님 — 표지를 빠뜨렸는지' % c['id'])
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
        if c.get('forbidden') and not c.get('supersedes') and not case and not lit:
            problems.append('[참고] %s: forbidden 이 있는데 supersedes(철회한 옛 주장) 기록이 없음'
                            % c['id'])
        if c.get('supersedes') and not c.get('forbidden'):
            hint = _forbidden_hints(_supersedes(c)[-1].get('statement', ''))
            problems.append('%s: supersedes 가 있는데 forbidden 이 비어 있음 — 옛 문구를 넣지 않으면 '
                            'mapcheck 가 옛 주장을 통과시킨다. 후보: %s' % (c['id'], ' / '.join(hint) or '-'))
        problems.extend(_source_problems(c, edges, sources))
        if st == 'excluded':          # v16.6 (발표 K23): 배제된 감별 — premise 가 없는 것이 정상, 대신 배제 근거(rebuttal)가 있어야 한다
            if not any(t == 'rebuttal' for _, t, _ in edges[c['id']]):
                problems.append('[참고] %s: 배제(excluded)인데 rebuttal 간선이 없음 — 배제 근거가 없는 배제' % c['id'])
        elif c.get('role') in ('main', 'claim') and not any(t == 'premise' for _, t, _ in edges[c['id']]) and noedge:
            folded['premise'] += 1
        elif c.get('role') in ('main', 'claim') and not any(t == 'premise' for _, t, _ in edges[c['id']]):
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
            if typ == 'caveat' and by_id.get(up, {}).get('role') == 'rebuttal':
                problems.append('[참고] %s -> %s: caveat 간선이 role=rebuttal 주장을 가리킴 — 한계가 아니라 반대 증거면 type rebuttal' % (c['id'], up))

    for c in claims:
        if c.get('role') == 'evidence' and (case or lit):
            pass
        elif c.get('role') == 'evidence' and noedge:
            folded['caveat'] += 1
        elif c.get('role') == 'evidence' and not any(t == 'caveat' for _, t, _ in edges[c['id']]):
            problems.append('[참고] %s: evidence 인데 걸린 caveat 이 없음' % c['id'])
    rev_any = {}
    for cid, lst in edges.items():
        for up, _, _ in lst:
            rev_any[up] = True
    weak = []
    for c in claims:
        for up, typ, w in edges[c['id']]:
            if typ in ('premise', 'support') and up in by_id and by_id[up].get('confidence', 'mid') == 'low':
                weak.append((w, c['id'], up, typ))
    for w, cid, up, typ in sorted(weak, reverse=True):
        problems.append('[참고] 약한 고리: %s 가 기대는 %s 는 confidence=low (%s %.1f)' % (cid, up, typ, w))
    # v16.17 (사용자 09-30 ③): 탐색적 주장이 main 의 전제(premise) 사슬에 있으면 [필수] — exploratory_reason 을 적으면 [참고] 로 내리고 사유를 보인다
    for cid, (lv, ms) in _exploratory_paths(claims).items():
        why = by_id[cid].get('exploratory_reason')
        if lv == 'chain' and not why:
            problems.append('%s: 탐색적 주장(exploratory)이 main(%s) 의 전제(premise) 사슬에 있다 — 결론을 받치게 두려면 exploratory_reason 에 '
                            '까닭을 적고, 아니면 사슬에서 뺀다(간선을 support 로 내리거나 끊는다)' % (cid, ', '.join(ms)))
        elif lv == 'chain':
            problems.append('[참고] %s: 탐색적 주장이 main(%s) 의 전제 사슬에 있음 — 사유: %s' % (cid, ', '.join(ms), why))
        elif lv == 'mixed':
            problems.append('[참고] %s: 탐색적 주장이 support 가 섞인 경로로 main(%s) 을 받친다%s'
                            % (cid, ', '.join(ms), (' — 사유: %s' % why) if why else ''))
    alone = [c['id'] for c in claims if not edges[c['id']] and not rev_any.get(c['id'])]
    if len(claims) > 1 and not any(edges.values()):   # v16.2 (사용자 09-29): 간선이 하나도 없는 그래프(발표 09-20 판 등)는 목록 대신 한 줄
        fo = ['premise 없음 %d' % folded['premise']] * bool(folded['premise']) + ['caveat 없음 %d' % folded['caveat']] * bool(folded['caveat'])
        problems.append('[참고] 간선이 하나도 없는 그래프(주장 %d개) — 관계(depends_on)를 아직 적지 않았다%s'
                        % (len(claims), ' (주장별 간선 [참고] %s 를 이 줄로 합침)' % ' · '.join(fo) if fo else ''))
    elif alone and len(claims) > 1:     # v16.1 (사용자 09-29): 간선이 하나도 없는 주장 — 관계도에서 떨어져 나온다. 한 줄로(간선 없는 옛 그래프가 줄로 쏟아지지 않게)
        problems.append('[참고] 간선이 하나도 없는 주장(외톨이) %d개: %s' % (len(alone), ', '.join(alone)))
    mains = [c['id'] for c in claims if c.get('role') == 'main']
    if any(c.get('role') for c in claims) and len(mains) != 1 and not case:   # 증례 덱은 증례마다 결론(main)이 하나 — 여럿이 정상
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
# 근거 공백 목록 (v16.5) — 문헌 찾기 작업표. 사용자 09-29: AI 가 제안한 논문은 DOI 확인 → 원문 입수 → 리뷰어 판정을
# 거친 것만 sources 에 들어간다. 이 도구는 작업표를 만들고(gaps) 채운 표를 literature 검증지시로 바꿀 뿐, sources 를 고치지 않는다.
# ----------------------------------------------------------------------------

GAP_CITED = '문헌 없음(인용 있음 — sources 미기입)'   # v16.7 (저자 09-29): 원고 인용 [n] 은 있는데 sources 칸만 빈 것 — 찾을 공백이 아니라 기입·판정할 것
LIT_ROLES = ('claim', 'main', 'background')      # 문헌 공백을 보는 역할 — evidence(우리 결과)는 뺀다(사용자 09-29)
_DOI = re.compile(r'\b(10\.\d{4,9}/[^\s|,;<>"]+)', re.I)


def _lit(c):
    return [x for x in (c.get('sources') or []) if isinstance(x, dict) and x.get('kind') in ('문헌', '교과서')]


def find_gaps(claims):
    """공백 목록 [(id, role, [공백 종류], 검색어)]. 종류: 문헌 없음 · 근거 하나(sources 1 또는 받침 간선 1) · 약한 고리 · 외톨이.
    철회(superseded)한 주장은 뺀다. 간선이 하나도 없는 그래프는 외톨이를 줄마다 내지 않는다(요약은 표 머리에)."""
    edges = _edges(claims)
    rev = _dependents(claims)
    noedge = len(claims) > 1 and not any(edges.values())
    by_id = {c['id']: c for c in claims}
    out = []
    for c in claims:
        if c.get('status') in ('superseded', 'excluded'):   # v16.6: 배제된 감별은 받칠 주장이 아니다
            continue
        cid, role, kinds = c['id'], c.get('role'), []
        lit = _lit(c)
        if role in LIT_ROLES and not lit:
            cited = any(_CITE_BRACKET.search(t or '') for t in [c.get('statement', '')] + list(c.get('sites', [])))
            kinds.append(GAP_CITED if cited else '문헌 없음')
        backing = [u for u, t, _ in edges[cid] if t in ('premise', 'support')]
        one = []
        if role in LIT_ROLES and len(lit) == 1:
            one.append('sources 1')
        if role in ('main', 'claim') and len(backing) == 1:
            one.append('받침 간선 1(%s)' % backing[0])
        if one:
            kinds.append('근거 하나 — ' + ' · '.join(one))
        leaning = [d for d, t, _ in rev.get(cid, []) if t in ('premise', 'support')]
        if c.get('confidence') == 'low' and leaning:
            kinds.append('약한 고리 — confidence low, 기대는 주장 %d(%s)' % (len(leaning), ', '.join(leaning[:3])))
        if not noedge and not edges[cid] and not rev.get(cid) and len(claims) > 1:
            kinds.append('외톨이')
        if kinds:     # v16.7 (사용자 09-29): 검색어는 keys(원고 추적용 앵커)에서 가져오지 않는다 — 역할 대화창이 공백을 읽고 만든다
            out.append((cid, role or '-', kinds, ''))
    return out, noedge


def _gap_kind(k):
    return k if k == GAP_CITED else k.split(' — ')[0]


def gaps_table(claims, name='원고'):
    """작업표 md. 1부 = 찾을 공백(공백마다 받침·반박 두 줄), 2부 = 인용은 있는데 sources 만 빈 주장(기입 한 줄).
    사람이 채울 칸: 검색어(역할 대화창이 만든다) · 후보 DOI · 출처(AI 제안/사람) · 입수 · 판정."""
    rows, noedge = find_gaps(claims)
    kinds = {}
    for _, _, ks, _ in rows:
        for k in ks:
            kinds[_gap_kind(k)] = kinds.get(_gap_kind(k), 0) + 1
    fill = [r for r in rows if r[2] == [GAP_CITED]]
    find = [r for r in rows if r[2] != [GAP_CITED]]
    L = ['# %s — 근거 공백 작업표' % name, '',
         '> claim_graph.py v%s gaps. 주장 %d개 중 공백 %d개(%s).%s' % (
             __version__, len(claims), len(rows), ' · '.join('%s %d' % kv for kv in kinds.items()) or '없음',
             ' 간선이 하나도 없는 그래프 — 외톨이·받침 간선 공백은 관계를 적은 뒤에 다시.' if noedge else ''),
         '> **규칙(사용자 09-29)**: 후보 논문은 이 표에만 적는다. **AI 가 제안한 논문(대화창 웹 검색·Gemini 조사)은 출처 칸에 "AI 제안"** — '
         'DOI 확인 → 원문 입수(literature) → 리뷰어 판정을 거친 것만 claims 의 sources 에 옮긴다. 받침만 찾지 말고 **반박 줄도 찾는다**(없으면 판정 칸에 "찾았으나 없음").',
         '> **검색어 칸은 비어 있다** — 역할 대화창이 공백(주장 문장)을 읽고 만든다(원고 추적용 keys 는 검색어로 쓰지 않는다).',
         '> 문헌 공백은 claim·main·background 만 본다(evidence = 우리 결과는 뺀다). 채운 표 → `claim_graph.py gaps --to-instr 이 표.md -o 검증지시.md` → literature(Cowork).', '',
         '## 1. 찾을 공백 %d개' % len(find), '',
         '| 번호 | 주장 | 역할 | 공백 | 방향 | 검색어 | 후보 DOI | 출처 | 입수 | 판정 |', '|---|---|---|---|---|---|---|---|---|---|']
    for k, (cid, role, ks, terms) in enumerate(find, 1):
        for d in ('받침', '반박'):
            L.append('| G%02d-%s | `%s` | %s | %s | %s | %s |  |  |  |  |' % (k, d, cid, role, ' / '.join(ks).replace('|', '/'), d, terms))
    if not find:
        L.append('| — | 없음 |  |  |  |  |  |  |  |  |')
    # v16.11 (다음 할 일 ③, 실물 v9): 인용 있음 + 다른 공백(약한 고리·외톨이 등)은 1부로 간다 — 머리 줄 수와 2부 제목 수가 달라 보이지 않게 적는다
    both = [(k, cid) for k, (cid, _, ks, _) in enumerate(find, 1) if GAP_CITED in ks]
    L += ['', '## 2. 인용 있음 — sources 미기입 %d개%s' % (len(fill), (' (+ 다른 공백과 겹쳐 1부에 간 %d개)' % len(both)) if both else ''), '']
    if both:
        L += ['> 인용 있음 %d개 중 %d개는 다른 공백과 겹쳐 1부에 있다 — %s. 그 주장도 인용 문헌 DOI 를 1부 받침 줄의 후보 DOI 칸에 적는다.'
              % (len(fill) + len(both), len(both), ' · '.join('G%02d `%s`' % kv for kv in both)), '']
    L += ['> 원고에 이미 인용 `[n]` 이 있다 — 새 논문을 찾는 공백이 아니라, 그 인용 문헌의 DOI 를 적어 받고 판정해 sources 에 기입할 것. 후보 DOI 칸에 인용 문헌 DOI.', '',
          '| 번호 | 주장 | 역할 | 공백 | 방향 | 검색어 | 후보 DOI | 출처 | 입수 | 판정 |', '|---|---|---|---|---|---|---|---|---|---|']
    for k, (cid, role, ks, terms) in enumerate(fill, len(find) + 1):
        L.append('| G%02d-기입 | `%s` | %s | %s | 기입 | %s |  |  |  |  |' % (k, cid, role, GAP_CITED, terms))
    if not fill:
        L.append('| — | 없음 |  |  |  |  |  |  |  |  |')
    return '\n'.join(L) + '\n'


def gaps_to_instr(table_md, name='원고'):
    """채운 작업표 → literature 검증지시 md(## 참고문헌 · ## 확인할 주장). 후보 DOI 가 있고 판정이 빈 줄만. 반환 (md, 알림 목록)."""
    refs, rows, notes, filled = {}, [], [], {}
    for line in table_md.splitlines():
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) < 10 or not re.match(r'^G\d+-(받침|반박|기입)$', c[0]):
            continue
        num, cid, direction, terms, cand, src, verdict = c[0], c[1].strip('`'), c[4], c[5], c[6], c[7], c[9]
        g = num.split('-')[0]
        filled.setdefault(g, {})[direction] = bool(cand or verdict)
        dois = [d.rstrip('.').lower() for d in _DOI.findall(cand)]
        if cand and not dois:
            notes.append('%s: 후보 칸에 DOI 가 없다("%s") — DOI 를 확인해 적는다' % (num, cand[:40]))
        if not dois or verdict:
            continue
        if not terms:
            notes.append('%s: 검색어 칸이 비었다 — locate 가 찾을 말이 없다(원문에서 찾을 말을 적는다)' % num)
        ns = []
        for d in dois:
            if d not in refs:
                refs[d] = (len(refs) + 1, num, src)
            ns.append(refs[d][0])
        rows.append('| %s | %s | %s %s(%s) | %s |' % (num, ', '.join(map(str, ns)), cid, direction, src or '출처 미기재', terms))
    for g, d in sorted(filled.items()):
        if d.get('받침') and not d.get('반박'):
            notes.append('%s: 받침 줄만 채웠다 — 반박 줄도 찾는다(없으면 판정 칸에 "찾았으나 없음")' % g)
    L = ['# 검증지시 — %s 근거 공백' % name, '', '> 원고: %s' % name,
         '> claim_graph.py v%s gaps --to-instr. 후보 %d편 — **AI 제안 후보는 아직 근거가 아니다**: 받아서 locate 한 뒤 리뷰어가 판정한다.' % (__version__, len(refs)), '',
         '## 참고문헌', '']
    for d, (n, num, src) in sorted(refs.items(), key=lambda kv: kv[1][0]):
        L.append('%d. 후보 %s (%s). doi:%s' % (n, num, src or '출처 미기재', d))
    L += ['', '## 확인할 주장', '', '| 주장 | 문헌 | 원고 문장(짧게) | 찾을 말 |', '|---|---|---|---|'] + rows + ['']
    return '\n'.join(L), notes


# ----------------------------------------------------------------------------
# 관계도 그림 (v16) — Mermaid 글. 그래프 전체 또는 impact 결과(바뀐 주장 → 하류 경로)
# ----------------------------------------------------------------------------

_ROLE_SHAPE = {'main': ('{{', '}}'), 'evidence': ('[', ']'), 'claim': ('(', ')'), 'caveat': ('[/', '/]'),
               'rebuttal': ('[\\', '\\]'), 'background': ('([', '])'), 'method': ('[[', ']]'), 'premise': ('[', ']')}
_EDGE_ARROW = {'premise': '==>', 'support': '-->', 'context': '-.->', 'caveat': '-. 한계 .->', 'rebuttal': '-- 반박 --x'}


SUGGEST_MIN_SHARED = 2
SUGGEST_MIN_CAVEAT = 3
SUGGEST_NO_MAIN_CAVEAT = 'main 에 직접 걸린 한계 0개 — 아래 공통 한계 중 main 에 걸 것을 고른다'


def suggest(claims, stream=sys.stdout, kind=None, min_shared=SUGGEST_MIN_SHARED, min_caveat=SUGGEST_MIN_CAVEAT):
    """v16.17 (사용자 09-30 ③): 새 주장 후보 — [참고]만, claims 는 바꾸지 않는다. 철회·배제한 주장은 뺀다.
    규칙 1 같은 근거(premise·support 로 기대는 주장, 또는 같은 문헌 DOI — 따로 센다)를 min_shared 개 이상 함께 쓰는데 어느 방향으로도
    이어지지 않은 주장(같은 근거 묶음이면 한 줄로). 증례 그래프(kind 증례)는 끈다 — 감별끼리 같은 소견을 나눠 쓰는 것이 정상.
    규칙 2 어디에도 안 쓰인 근거(role evidence 인데 기대는 주장이 없음 — rebuttal 로 쓰인 소견도 쓰임).
    규칙 3 min_caveat 개 이상 주장에 걸린 공통 한계. main 에 직접 걸린 한계가 0 이면 머리 한 줄을 먼저(사용자 09-30).
    덧줄: main 전제 사슬(premise 만, main 포함 — v16.18)의 절반 넘게 걸렸는데 main 에는 없는 한계.
    v16.18 (저자 09-30): 규칙 3 줄마다 한계 statement 앞 40자 · 이미 main 에 걸린 한계는 권고 대신 '(main 에 이미 걸림)'.
    반환 {'shared': [{ids, claims, dois}], 'unused': [{id, alone}], 'caveats': [{id, n, on}], 'half': [{id, main, on, of}], 'no_main_caveat': [main]}."""
    live = [c for c in claims if c.get('status') not in ('superseded', 'excluded')]
    lid = {c['id'] for c in live}
    edges = _edges(claims)
    rev = _dependents(claims)
    order = {c['id']: k for k, c in enumerate(claims)}

    def reach(a, b):
        seen, st = set(), [a]
        while st:
            v = st.pop()
            if v == b:
                return True
            if v in seen:
                continue
            seen.add(v)
            st += [u for u, _, _ in edges.get(v, [])]
        return False
    ups = {c['id']: {u for u, t, _ in edges[c['id']] if t in ('premise', 'support') and u in lid} for c in live}
    dois = {c['id']: {x['what'] for x in (c.get('sources') or []) if isinstance(x, dict) and x.get('kind') == '문헌' and x.get('what')} for c in live}
    case = kind in CASE_KINDS
    groups = {}
    if not case:
        for i, a in enumerate(live):
            for b in live[i + 1:]:
                sc = ups[a['id']] & ups[b['id']]; sd = dois[a['id']] & dois[b['id']]
                sc = sc if len(sc) >= min_shared else set(); sd = sd if len(sd) >= min_shared else set()
                if not (sc or sd) or reach(a['id'], b['id']) or reach(b['id'], a['id']):
                    continue
                groups.setdefault((frozenset(sc), frozenset(sd)), set()).update((a['id'], b['id']))
    shared = [{'ids': sorted(m, key=order.get), 'claims': sorted(k[0], key=order.get), 'dois': sorted(k[1])} for k, m in groups.items()]
    shared.sort(key=lambda x: order[x['ids'][0]])
    unused = [{'id': c['id'], 'alone': not edges[c['id']]} for c in live if c.get('role') == 'evidence' and not rev.get(c['id'])]
    cav = {}
    for c in live:
        for u, t, _ in edges[c['id']]:
            if t == 'caveat' and u in lid:
                cav.setdefault(u, []).append(c['id'])
    caveats = [{'id': k, 'n': len(v), 'on': v} for k, v in sorted(cav.items(), key=lambda kv: (-len(kv[1]), order[kv[0]])) if len(v) >= min_caveat]
    mains = [c['id'] for c in live if c.get('role') == 'main']
    direct = {m: {u for u, t, _ in edges[m] if t == 'caveat'} for m in mains}
    no_main = [m for m in mains if not direct[m]]
    half = []
    for m in mains:
        seen, st = set(), [m]
        while st:
            v = st.pop()
            if v in seen or v not in lid:
                continue
            seen.add(v)
            st += [u for u, t, _ in edges.get(v, []) if t == 'premise']
        # v16.18 (저자 09-30 [확인 필요]): 사슬은 설계대로 main 을 포함해 센다 — v16.17 은 main 을 빼고 세어 저자 v10 에서 3줄(설계 1줄)
        if len(seen) < 2:
            continue
        for k, on in cav.items():
            n = len(seen & set(on))
            if n * 2 > len(seen) and k not in direct[m]:
                half.append({'id': k, 'main': m, 'on': n, 'of': len(seen)})
    P = lambda t: print(t, file=stream)
    by = {c['id']: c for c in claims}

    def head(k):                                  # v16.18 (저자 09-30): 고르기 전에 한계 문장이 낡았는지 보이게 — statement 앞 40자
        st = re.sub(r'\s+', ' ', by.get(k, {}).get('statement', '') or '').strip()
        return (' "%s"' % (st if len(st) <= 40 else st[:40].rstrip() + '…')) if st else ''
    P('=== 새 주장 후보 (suggest) — [참고]만, claims 는 바꾸지 않는다 ===')
    if case:
        P('규칙 1 — 증례 그래프라 끔(감별끼리 같은 소견을 나눠 쓰는 것이 정상)')
    else:
        P('규칙 1 — 같은 근거를 %d개 이상 함께 쓰는데 안 이어진 주장: %d줄' % (min_shared, len(shared)))
    for x in shared:
        what = []
        if x['claims']:
            what.append('함께 기대는 주장 %s' % ', '.join(x['claims']))
        if x['dois']:
            what.append('함께 쓰는 문헌 %s' % ', '.join(x['dois']))
        P('  [참고] %s — %s → 같은 뜻이면 합침 · 한쪽이 다른 쪽에 기댐 · 둘을 묶는 상위 주장' % (', '.join(x['ids']), ' · '.join(what)))
    P('규칙 2 — 어디에도 안 쓰인 근거(evidence): %d개' % len(unused))
    for x in unused:
        P('  [참고] %s — 기대는 주장 없음%s → 새 주장 후보 또는 빼기' % (x['id'], '(외톨이 — mapgraph 에도 나옴)' if x['alone'] else ''))
    P('규칙 3 — %d개 이상 주장에 걸린 공통 한계: %d개' % (min_caveat, len(caveats)))
    if caveats and no_main:
        P('  [참고] ' + (SUGGEST_NO_MAIN_CAVEAT if len(mains) == 1 else '%s — %s' % (', '.join(no_main), SUGGEST_NO_MAIN_CAVEAT)))
    for x in caveats:
        onm = [m for m in mains if x['id'] in direct[m]]
        todo = ('(main 에 이미 걸림)' if len(mains) == 1 else '(main %s 에 이미 걸림)' % ', '.join(onm)) if onm else '→ main 에 직접 걸기(Limitations 첫 문단)'
        P('  [참고] %s%s — 걸린 주장 %d개(%s) %s'
          % (x['id'], head(x['id']), x['n'], ', '.join(x['on'][:6]) + (' …' if x['n'] > 6 else ''), todo))
    for x in half:
        P('  [참고] %s%s — main(%s) 전제 사슬 %d개 중 %d개에 걸렸는데 main 에는 없음' % (x['id'], head(x['id']), x['main'], x['of'], x['on']))
    return {'shared': shared, 'unused': unused, 'caveats': caveats, 'half': half, 'no_main_caveat': no_main}


def _mm(t):
    return (t or '').replace('"', '#quot;').replace('<', '#lt;').replace('>', '#gt;')


_ROLE_COLOR = {'main': 'fill:#ffd8a8,stroke:#c2410c,stroke-width:3px', 'evidence': 'fill:#d0e7ff,stroke:#1d4ed8',
               'premise': 'fill:#d0e7ff,stroke:#1d4ed8', 'claim': 'fill:#d3f2d3,stroke:#15803d',
               'background': 'fill:#ececec,stroke:#6b6b6b', 'method': 'fill:#e6dcff,stroke:#6d28d9',
               'rebuttal': 'fill:#ffd6d6,stroke:#b91c1c', 'caveat': 'fill:#fff3bf,stroke:#a16207'}
_ROLE_KO = {'main': '주 결론', 'evidence': '근거(결과)', 'premise': '근거(결과)', 'claim': '해석', 'background': '배경', 'method': '방법',
            'rebuttal': '반박', 'caveat': '한계'}


def _mapdraw_compact(claims, text=False):
    """v16.1 전체 그림 기본(사용자 09-29 — 저자 51주장·간선 83 이 6614×1033 px 로 화면 폭에서 못 읽힘):
    왼쪽(근거) → 오른쪽(main), caveat 상자·간선은 접어 걸린 상자에 '한계 N', 역할별 색, 간선 없는 상자는 그림 밖 목록."""
    by_id = {c['id']: c for c in claims}
    edges = _edges(claims)
    ncav = {cid: sum(1 for _, t, _ in lst if t == 'caveat') for cid, lst in edges.items()}
    def cav_node(cid):                   # 접을 caveat 상자: role=caveat 이고 caveat 이 아닌 간선에 끼지 않은 것
        if by_id[cid].get('role') != 'caveat':
            return False
        if any(t != 'caveat' for _, t, _ in edges[cid]):
            return False
        return not any(up == cid and t != 'caveat' for lst in edges.values() for up, t, _ in lst)
    if len(by_id) > 1 and not any(edges.values()):     # v16.2: 간선 0 — 빈 그림·주장 목록 대신 한 줄
        return ('# 관계도 — 그래프 전체\n\n> claim_graph.py v%s mapdraw. 간선이 하나도 없는 그래프(주장 %d개) — 그릴 관계가 없다. '
                'depends_on 을 적은 뒤 다시 그린다(상자만 보려면 `--all-edges`).\n' % (__version__, len(by_id)))
    folded = {cid for cid in by_id if cav_node(cid)}
    drawn = [(up, typ, cid) for cid in by_id if cid not in folded for up, typ, _ in edges[cid]
             if typ != 'caveat' and up in by_id and up not in folded]
    linked = {x for up, _, cid in drawn for x in (up, cid)}
    nid = {cid: 'n%d' % k for k, cid in enumerate(by_id, 1)}
    L = ['# 관계도 — 그래프 전체', '',
         '> claim_graph.py v%s mapdraw. 왼쪽 근거 → 오른쪽 주 결론. 굵은 선 premise · 실선 support · 점선 context · "반박"(x) rebuttal. '
         '색: 주황 주 결론(main) · 파랑 근거(evidence) · 초록 해석(claim) · 회색 배경(background) · 보라 방법(method) · 빨강 반박(rebuttal). '
         '상자: id · 역할·confidence(- = 역할 없음, high/mid/low) · **한계 N** = 걸린 caveat 수(caveat 상자·선은 접었다 — 다 보려면 `--all-edges`).' % __version__,
         '', '```mermaid', 'flowchart LR']
    groups = {}                         # v16.6 (사용자 09-29): group 칸 → Mermaid subgraph — 증례마다 묶어 선이 다른 증례 상자를 가로질러 읽히지 않게
    for cid, c in by_id.items():
        if cid in linked and c.get('group'):
            groups.setdefault(str(c['group']), []).append(cid)
    gid = {g: 'g%d' % k for k, g in enumerate(groups, 1)}
    node_lines = {}
    for cid, c in by_id.items():
        if cid not in linked:
            continue
        a, b = _ROLE_SHAPE.get(c.get('role'), ('[', ']'))
        lab = [cid, '%s·%s' % (c.get('role') or '-', c.get('confidence', 'mid'))]
        if ncav.get(cid):
            lab.append('한계 %d' % ncav[cid])
        if text and c.get('statement'):
            st = c['statement']
            lab.append(st[:40] + ('…' if len(st) > 40 else ''))
        if c.get('status') == 'superseded':
            lab.append('(철회)')
        if c.get('status') == 'excluded':
            lab.append('배제')
        if c.get('exploratory') is True:            # v16.17: 탐색적 주장 — 글자만(색은 더하지 않는다)
            lab.append('탐색')
        node_lines[cid] = '%s%s"%s"%s' % (nid[cid], a, '<br/>'.join(_mm(x) for x in lab), b)
    for g, members in groups.items():
        L.append('  subgraph %s["%s"]' % (gid[g], _mm(g)))
        if len(groups) > 1:
            L.append('    direction LR')
        L += ['    ' + node_lines[cid] for cid in members]
        L.append('  end')
    L += ['  ' + line for cid, line in node_lines.items() if not by_id[cid].get('group')]
    for up, typ, cid in drawn:
        L.append('  %s %s %s' % (nid[up], _EDGE_ARROW.get(typ, '-->'), nid[cid]))
    if len(groups) > 1:                 # v16.8 (사용자 09-29): 보이지 않는 연결로 묶음을 처음 나온 순서대로 위→아래(계단) — 순서가 뒤집히고
        L.append('  ' + ' ~~~ '.join(gid[g] for g in groups))   # 결론 선이 다른 묶음을 가로지르던 것(가짜 증례 3개로 재 봄: 가로지름 2 → 0)
    for role, style in _ROLE_COLOR.items():
        ids = [nid[cid] for cid in by_id if cid in linked and by_id[cid].get('role') == role and by_id[cid].get('status') not in ('superseded', 'excluded')]
        if ids:
            L += ['  classDef r_%s %s' % (role, style), '  class %s r_%s' % (','.join(ids), role)]
    sup = [nid[cid] for cid in by_id if cid in linked and by_id[cid].get('status') == 'superseded']
    if sup:
        L += ['  classDef old fill:#eeeeee,color:#777777', '  class %s old' % ','.join(sup)]
    exc = [nid[cid] for cid in by_id if cid in linked and by_id[cid].get('status') == 'excluded']
    if exc:                             # v16.6 (발표 K23 + 사용자): 흰 채움 + 점선 테두리 — 회색은 background 색이라 겹친다
        L += ['  classDef excluded fill:#ffffff,stroke:#555555,stroke-width:2px,stroke-dasharray:6 4', '  class %s excluded' % ','.join(exc)]
    off = [nid[cid] for cid in by_id if cid in linked and by_id[cid].get('offstage')]
    if off:                             # v16.12: 구연의 무대 밖 상류 — 흐린 글·가는 점선(화면에는 없고 받침으로만)
        L += ['  classDef offstage fill:#fafafa,color:#888888,stroke:#aaaaaa,stroke-dasharray:2 3', '  class %s offstage' % ','.join(off)]
    L += ['```', '']
    if exc:
        L.append('흰 상자 + 점선 테두리 + "배제" = 배제된 감별(status excluded) — 배제 근거에서 "반박"(x) 선이 들어온다.')
    if any(by_id[cid].get('exploratory') is True for cid in linked):
        L.append('"탐색" = 탐색적 주장(exploratory) — main 의 전제(premise) 사슬에 있으면 사유 없이는 mapgraph [필수].')
    alone = [cid for cid in by_id if cid not in linked and cid not in folded]
    if folded:
        L.append('접은 caveat %d개(상자에 "한계 N" 으로): %s' % (len(folded), ', '.join(sorted(folded))))
    if alone:
        L += ['', '그림에 없는 주장 — 그릴 간선이 없다 %d개:' % len(alone)]
        for cid in alone:
            c = by_id[cid]
            L.append('- `%s` (%s%s%s)%s' % (cid, _ROLE_KO.get(c.get('role'), c.get('role') or '역할 없음'),
                                          ', 한계 %d' % ncav[cid] if ncav.get(cid) else '', ', 탐색' if c.get('exploratory') is True else '',
                                          (' — ' + c['statement'][:60]) if text and c.get('statement') else ''))
    return '\n'.join(L) + '\n'


def mapdraw(claims, changed=None, text=False, stream=sys.stdout, all_edges=False):
    """Mermaid flowchart 글(```mermaid 블록이 든 md)을 돌려준다.
    전체 그림(v16.1 기본)은 _mapdraw_compact — 왼쪽→오른쪽, caveat 접기, 역할별 색, 외톨이는 목록.
    all_edges=True 면 v16.0 모양(아래→위, caveat 상자·간선까지 모두). changed 가 있으면 impact 와 같은 계산으로
    그 경로의 주장만 그리고, 바뀐 것·필수·참고를 색으로 나눈다(v16.0 그대로).
    GitHub·claude.ai 대화창에서 그림으로 보인다. Drive 미리보기는 글로만 보인다."""
    if not changed and not all_edges:
        return _mapdraw_compact(claims, text=text)
    by_id = {c['id']: c for c in claims}
    edges = _edges(claims)
    keep, lvl = set(by_id), {}
    title = '그래프 전체'
    if changed:
        rows = impact(claims, changed, stream=io.StringIO())
        keep = {x for x in changed if x in by_id} | {cid for cid, _, _ in rows}
        for cid, sc, _ in rows:
            lvl[cid] = 'must' if sc >= IMPACT_CUTOFF else 'ref'
        for x in changed:
            lvl[x] = 'changed'
        title = 'impact: %s' % ', '.join(changed)
    nid = {cid: 'n%d' % k for k, cid in enumerate(by_id, 1)}
    L = ['# 관계도 — %s' % title, '',
         '> claim_graph.py v%s mapdraw. 화살표: 근거 → 그것에 기대는 주장. 굵은 선 premise · 실선 support · 점선 context · '
         '"한계" caveat · "반박"(x) rebuttal. 모양: 육각 main · 네모 evidence · 둥근 claim · 기울임 caveat.' % __version__, '',
         '```mermaid', 'flowchart BT']
    for cid, c in by_id.items():
        if cid not in keep:
            continue
        a, b = _ROLE_SHAPE.get(c.get('role'), ('[', ']'))
        lab = [cid, '%s·%s' % (c.get('role') or '-', c.get('confidence', 'mid'))]
        if text and c.get('statement'):
            st = c['statement']
            lab.append(st[:40] + ('…' if len(st) > 40 else ''))
        if c.get('status') == 'superseded':
            lab.append('(철회)')
        if c.get('status') == 'excluded':
            lab.append('배제')
        if c.get('exploratory') is True:            # v16.17: 탐색적 주장 — 글자만(색은 더하지 않는다)
            lab.append('탐색')
        L.append('  %s%s"%s"%s' % (nid[cid], a, '<br/>'.join(_mm(x) for x in lab), b))   # 줄바꿈 <br/> 은 두고 글만 이스케이프
    for cid in by_id:
        if cid not in keep:
            continue
        for up, typ, w in edges[cid]:
            if up in keep and up in nid:
                L.append('  %s %s %s' % (nid[up], _EDGE_ARROW.get(typ, '-->'), nid[cid]))
    if lvl:
        L += ['  classDef changed fill:#f8d7da,stroke:#b02a37,stroke-width:3px',
              '  classDef must fill:#fff3cd,stroke:#b58105', '  classDef ref fill:#e7f1ff,stroke:#6c8ebf']
        for k in ('changed', 'must', 'ref'):
            ids = [nid[x] for x, v in lvl.items() if v == k and x in nid]
            if ids:
                L.append('  class %s %s' % (','.join(ids), k))
    sup = [nid[c['id']] for c in claims if c.get('status') == 'superseded' and c['id'] in keep]
    if sup:
        L += ['  classDef old fill:#eeeeee,color:#777777', '  class %s old' % ','.join(sup)]
    off = [nid[c['id']] for c in claims if c.get('offstage') and c['id'] in keep and c['id'] in nid]
    if off:
        L += ['  classDef offstage fill:#fafafa,color:#888888,stroke:#aaaaaa,stroke-dasharray:2 3', '  class %s offstage' % ','.join(off)]
    L += ['```', '']
    if lvl:
        L.append('빨강 = 바뀐 주장 · 노랑 = 다시 볼 것(필수, 강도 ≥ %.2f) · 파랑 = 참고.' % IMPACT_CUTOFF)
    out = '\n'.join(L) + '\n'
    return out


# ----------------------------------------------------------------------------
# 자리 대조 / 해시
# ----------------------------------------------------------------------------

_NUMTOK = re.compile(r'(?<![\w.])[-−]?\d+(?:[.,]\d+)?(?:\s*%)?(?![\w])')


_SUPPL_TAG = re.compile(r'\bSuppl(?:ementary)?\.?\s+(?:(?:Table|Fig(?:ure)?\.?|Tab\.?)\s+)?S\d+', re.I)
_SUPPL_NUMS = re.compile(r'(\bSuppl(?:ementary)?\.?\s+(?:(?:Table|Fig(?:ure)?\.?|Tab\.?)\s+)?)(S\d+(?:(?:\s*,\s*|\s*[\-\u2013]\s*|\s+and\s+)S\d+)*)', re.I)


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
    notes = {c['id']: c['oral_note'] for c in claims if c.get('oral_note')}   # v16.14 (발표 O2)
    problems, matrix, suppl = [], {}, []
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
            if missing and _SUPPL_TAG.search(ev_txt):   # v16.9 (저자 3a): 보충자료 수치 — sites 는 본문만 본다
                suppl.append((cid, len(missing)))
            elif missing:
                problems.append('[참고] %s: evidence 의 수치 %s 가 sites 어디에도 없음' % (cid, ', '.join(missing)))
    if suppl:
        problems.append('[참고] 보충자료 표지(Suppl S…)가 든 evidence %d개(%s)의 수치 %d개가 sites 에 없음 — sites 는 본문만 보므로 따로 적지 않는다'
                        % (len(suppl), ', '.join(c for c, _ in suppl), sum(n for _, n in suppl)))
    gp, _ = mapgraph(claims, stream=open(os.devnull, 'w'))
    problems.extend(p for p in gp if not p.startswith('[참고]'))
    print('=== 주장 관계도 대조 ===', file=stream)
    print('주장 %d개 / 자리 %d곳' % (len(claims), len(matrix)), file=stream)
    if problems:
        for p in problems:
            nt = notes.get(p.split(':', 1)[0])        # 구연 덧붙임의 note — 왜 [!] 인지 바로 보이게
            print('  [!] %s%s' % (p, (' — note: %s' % nt) if nt else ''), file=stream)
    else:
        print('  모든 주장의 자리에 찾는 표현이 있음 — 주장·evidence 가 최신인지는 보지 않는다(mapstale·판 올림 때 evidence 갱신)', file=stream)   # v16.9 (저자 4)
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
        for x in c.get('sources') or []:         # v16 근거 칸
            if isinstance(x, dict):
                print('      원문: %s %s %s%s%s' % (x.get('kind', ''), x.get('what', ''), x.get('at', ''),
                                                 (' · ' + x['element']) if x.get('element') else '',
                                                 (' → ' + x['verdict']) if x.get('verdict') else ''), file=stream)
    ex = _exploratory_paths(claims)
    if ex:                                        # v16.17 (사용자 09-30 ③): 리뷰어 보고 — 탐색적 주장과 사유
        by = {c['id']: c for c in claims}
        print('\n탐색적 주장 (exploratory) %d개:' % len(ex), file=stream)
        for cid, (lv, ms) in ex.items():
            why = by[cid].get('exploratory_reason')
            where = {'chain': 'main(%s) 의 전제 사슬(premise)' % ', '.join(ms), 'mixed': 'support 가 섞인 경로로 main(%s) 을 받침' % ', '.join(ms),
                     'off': 'main 과 이어지지 않음'}[lv]
            print('  [%s] %s · %s' % (cid, where, ('사유: ' + why) if why else ('사유 없음 — mapgraph [필수]' if lv == 'chain' else '사유 없음')), file=stream)
    return sites


_CITE_BRACKET = re.compile(r'\s*\[\d{1,3}(?:\s*[,\u2013\u2014-]\s*\d{1,3})*\]')


def _fingerprint(text):
    """자리 텍스트 해시. v15.2: 대괄호 인용번호([12], [15,16], [29-31])를 빼고 잰다 —
    참고문헌 재번호는 주장을 바꾸지 않는데 v44→v45 에서 39자리 중 28자리가 [변경]으로 떴다."""
    import hashlib
    t = _CITE_BRACKET.sub('', text or '')
    return hashlib.sha1(re.sub(r'\s+', ' ', t).strip().encode('utf8')).hexdigest()[:12]


# ----------------------------------------------------------------------------
# 근거 원문 (v16) — 문헌 보관소 paper.md · 교과서 분할 md 에서 at 자리의 글
# ----------------------------------------------------------------------------

_MARK_LINE = re.compile(r'^(\[p\.[^\]]*\]|\[§ [^\]]*\])\s*$', re.M)


def _page_of(mark):
    """쪽 표지·자리 → (인쇄 쪽 문자열 또는 None, PDF 쪽 int 또는 None).
    `[p.인쇄 · PDF N]`(새 표지) · `[p.N]`(대괄호 — 옛 문헌 md, N = PDF 쪽) · `PDF N` · `p.56`(대괄호 없음 = 인쇄 쪽)."""
    t = mark.strip()
    m = re.match(r'^\[?p\.\s*([^\]·]*?)\s*·\s*PDF\s*(\d+)\]?$', t)
    if m:
        pr = m.group(1).strip()
        return (None if pr in ('', '—', '-') else pr), int(m.group(2))
    m = re.match(r'^\[p\.\s*(\d+)\]$', t)
    if m:
        return None, int(m.group(1))
    m = re.match(r'^PDF\s*(\d+)$', t)
    if m:
        return None, int(m.group(1))
    m = re.match(r'^p\.\s*(\S+)$', t)
    return (m.group(1), None) if m else (None, None)


def _norm_body(t):
    """비교용 본문 — 쪽·절 표지 줄과 '> ' 머리말 줄을 빼고 NFKC·띄어쓰기를 맞춘다(형식만 바뀐 것은 같게)."""
    import unicodedata
    t = _MARK_LINE.sub('', t or '')
    t = '\n'.join(l for l in t.splitlines() if not l.startswith('> '))
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', t)).strip()


def _at_text(md, at):
    """md 에서 at 자리의 글. at 없음/'전체' → 머리말 뒤 전부. [§ 절] → 그 표지가 붙은 덩이 모두(상자 뒤 다시 붙은 것 포함)."""
    parts = _MARK_LINE.split(md)          # [앞, 표지, 글, 표지, 글, …]
    at = (at or '').strip()
    if not at or at == '전체':
        return md
    if at.startswith('[§'):
        want = re.sub(r'\s+', ' ', at)
        got = [parts[k + 1] for k in range(1, len(parts) - 1, 2) if re.sub(r'\s+', ' ', parts[k].strip()) == want]
        if not got:
            raise KeyError('절 표지 %s 없음' % at)
        return '\n'.join(got)
    pr, pdf = _page_of(at)
    if pr is None and pdf is None:
        raise KeyError('자리 %s 를 쪽 표지로 읽지 못함' % at)
    for k in range(1, len(parts) - 1, 2):
        mpr, mpdf = _page_of(parts[k].strip())
        if (pdf is not None and mpdf == pdf) or (pdf is None and pr is not None and mpr == pr):
            return parts[k + 1]
    raise KeyError('쪽 %s 없음' % at)


def _source_file(root, src):
    """(md 경로 목록, 원 파일 sha 또는 None). 문헌: 보관소에서 meta.md 의 doi= 로. 교과서: 분할 폴더 안 책 폴더(이름에 what 이 든 것)의 md."""
    kind, what = src.get('kind'), str(src.get('what', '')).strip()
    if kind == '문헌':
        want = what.lower().replace('https://doi.org/', '')
        for d in sorted(os.listdir(root)):
            mp = os.path.join(root, d, 'meta.md')
            if os.path.exists(mp):
                head = open(mp, encoding='utf8').readline()
                m = re.search(r'doi=(\S+)', head)
                if (m and m.group(1).lower() == want) or d == what:
                    sha = re.search(r'sha=([0-9a-f]+)', head)
                    return [os.path.join(root, d, 'paper.md')], (sha.group(1) if sha else None)
        raise KeyError('보관소에 %s 없음' % what)
    if kind == '교과서':
        books = [d for d in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, d)) and what and what in d]
        if len(books) != 1:
            raise KeyError('교과서 폴더 "%s" %s' % (what, '없음' if not books else '여럿: ' + ', '.join(books)))
        bd = os.path.join(root, books[0])
        return [os.path.join(bd, f) for f in sorted(os.listdir(bd)) if f.endswith('.md') and f != 'INDEX.md'], None
    raise KeyError('kind %s 는 원문 폴더로 읽지 않는다' % kind)


def _source_read(src, root, resolve=None):
    """근거 하나 → {'text': 그 자리 본문 해시, 'raw': 파일 전체 해시, 'orig': 원 파일 sha}. 덱·원고는 문서 resolver 로."""
    import hashlib
    h = lambda t: hashlib.sha1(t.encode('utf8')).hexdigest()[:12]
    if src.get('kind') in ('덱', '원고'):
        if resolve is None:
            raise KeyError('문서가 없다')
        t = resolve(src.get('at', ''))
        return {'text': h(_norm_body(t)), 'raw': h(t), 'orig': None}
    if not root:
        raise KeyError('원문 폴더(--sources)가 없다')
    files, orig = _source_file(root, src)
    last = None
    for fp in files:
        md = open(fp, encoding='utf8').read()
        try:
            t = _at_text(md, src.get('at'))
        except KeyError as e:
            last = e; continue
        return {'text': h(_norm_body(t)), 'raw': h(md), 'orig': orig}
    raise last or KeyError('md 없음')


def _src_key(x):
    return '%s|%s|%s|%s' % (x.get('kind', ''), x.get('what', ''), x.get('at', ''), x.get('element', ''))


def mapfreeze(resolve, claims, at=None, sources=None, stream=None):
    """검증 완료 선언. 자리 텍스트와 statement/evidence 의 해시를 기록."""
    import datetime
    at = at or datetime.date.today().isoformat()
    # v15.8.4 (코드 리뷰 09-28): 읽을 수 없는 자리를 None 으로 적으면, 나중에도 못 읽을 때 '바뀐 것 없음' 이 된다 — 먼저 다 읽고, 하나라도
    # 못 읽으면 아무것도 기록하지 않고 멈춘다
    fps, bad = {}, []
    for c in claims:
        for site in c.get('sites', []):
            try:
                fps[(c['id'], site)] = _fingerprint(resolve(site))
            except Exception as e:
                bad.append('%s: %s (%s)' % (c['id'], site, type(e).__name__))
    if bad:
        raise SystemExit('[멈춤] 자리를 읽지 못해 검증 기록(mapfreeze)을 하지 않았다 — 지운 화면·바뀐 절 제목이면 sites 를 먼저 고친다:\n  '
                         + '\n  '.join(bad[:20]))
    # v16.10 (사용자 09-29): --sources(문헌 보관소)를 주었는데 문헌 근거의 DOI 가 보관소에 없으면 mapgraph --sources 처럼 [필수] — 아무것도
    # 기록하지 않고 멈춘다. 전에는 [참고] 로만 알리고 나머지를 기록해, 원문 없는 근거가 검증된 그래프에 남았다
    if sources is not None:
        nodoi = []
        for c in claims:
            for k, x in enumerate(c.get('sources') or [], 1):
                if isinstance(x, dict) and x.get('kind') == '문헌' and x.get('what'):
                    try:
                        _source_file(sources, x)
                    except (KeyError, OSError):
                        nodoi.append('%s: sources[%d]: 문헌 %s' % (c['id'], k, x['what']))
        if nodoi:
            raise SystemExit('[멈춤] [필수] 근거 문헌 %d곳이 보관소(%s)에 없어 검증 기록(mapfreeze)을 하지 않았다 — 원문을 받지 않은 근거는 '
                             'sources 에서 빼 작업표에 두거나, 보관소에 받은 뒤 다시 한다(mapgraph --sources 와 같은 규칙):\n  %s'
                             % (len(nodoi), sources, '\n  '.join(nodoi[:20]) + ('\n  … 외 %d곳' % (len(nodoi) - 20) if len(nodoi) > 20 else '')))
    src_rec, src_skip = {}, []
    for c in claims:                      # v16: 근거 원문 — 폴더를 준 때만. 못 읽는 근거는 기록하지 않고 알린다(근거 칸은 선택)
        old = (c.get('verified') or {}).get('sources', {})
        rec = {}
        for x in c.get('sources') or []:
            if not isinstance(x, dict):
                continue
            k = _src_key(x)
            if sources is None and x.get('kind') not in ('덱', '원고'):
                if k in old:
                    rec[k] = old[k]        # 폴더 없이 다시 freeze — 전 기록을 그대로 둔다
                continue
            try:
                rec[k] = _source_read(x, sources, resolve)
            except (KeyError, OSError) as e:
                src_skip.append('%s: %s %s %s (%s)' % (c['id'], x.get('kind'), x.get('what', ''), x.get('at', ''), e))
        src_rec[c['id']] = rec
    for c in claims:
        fp = {site: fps[(c['id'], site)] for site in c.get('sites', [])}
        c['verified'] = {'at': at, 'sites': fp,
                         'evidence': _fingerprint(c.get('evidence', '') + '|' + c.get('statement', '')),
                         # v15.5: keys 만 바꾼 그래프(mapstale 0 · mapcheck 실패)를 잡기 위한 별도 해시.
                         # 구판 freeze 에는 이 키가 없고, 없으면 mapstale 이 검사하지 않는다(기존 그래프 무영향)
                         'keys': _fingerprint('|'.join(c.get('keys', []))),
                         # v16.17 (사용자 09-30): 탐색적 표지 — 지우면(true→false·칸 삭제) mapstale [변경]. 없는 옛 기록은 보지 않는다
                         'exploratory': c.get('exploratory') is True}
        if src_rec.get(c['id']):
            c['verified']['sources'] = src_rec[c['id']]
    if src_skip and stream is not None:
        print('[참고] 근거 원문 %d곳은 기록하지 않음(원문 폴더·자리를 못 찾음 — mapstale 이 보지 않는다):\n  %s'
              % (len(src_skip), '\n  '.join(src_skip[:20])), file=stream)
    return claims


def mapstale(resolve, claims, stream=sys.stdout, sources=None):
    """sources(v16): 근거 원문 폴더(문헌 보관소·교과서 분할). 주면 freeze 때 적은 근거 원문과 비교한다 —
    본문이 같으면 쪽 표지·머리말이 바뀌어도 알리지 않고(형식만), 원 파일(PDF·XML sha)이 같은데 본문이 다르면 '변환 바뀜' 으로 따로
    (하류 전파 없음, '근거 없음'·'부분' 판정만 다시 볼 것), 원 파일이 다르거나 sha 가 없는데 본문이 다르면 [변경]."""
    changed, unverified, detail = [], [], []
    fmt_only, converted, conv_recheck = [], [], []
    ex_added = []
    for c in claims:
        v = c.get('verified')
        if not v:
            unverified.append(c['id']); continue
        if v.get('evidence') != _fingerprint(c.get('evidence', '') + '|' + c.get('statement', '')):
            changed.append(c['id']); detail.append('%s: statement/evidence 가 바뀜' % c['id']); continue
        if 'keys' in v and v['keys'] != _fingerprint('|'.join(c.get('keys', []))):
            changed.append(c['id']); detail.append('%s: keys 가 바뀜 (freeze 뒤 편집)' % c['id']); continue
        if 'exploratory' in v and v['exploratory'] and c.get('exploratory') is not True:
            # v16.17 (사용자 09-30): 표지를 지우는 것은 전제 사슬 [필수] 를 사유 없이 넘는 가장 쉬운 길 — confidence 와 달리 [변경]
            changed.append(c['id']); detail.append('%s: 탐색적 표지(exploratory)가 지워짐 (true → %s) — 까닭을 확인하고 다시 freeze'
                                                   % (c['id'], '칸 삭제' if 'exploratory' not in c else repr(c['exploratory']).lower())); continue
        if 'exploratory' in v and not v['exploratory'] and c.get('exploratory') is True:
            ex_added.append(c['id'])
        for site in c.get('sites', []):
            try:
                now = _fingerprint(resolve(site))
            except Exception:
                changed.append(c['id']); detail.append('%s: %s 자리를 읽을 수 없다(지운 화면·바뀐 절 제목?)' % (c['id'], site)); break   # v15.8.4
            if v.get('sites', {}).get(site) != now:
                changed.append(c['id']); detail.append('%s: %s 텍스트가 바뀜' % (c['id'], site)); break
        if c['id'] in changed or not v.get('sources'):
            continue
        for x in c.get('sources') or []:
            k = _src_key(x) if isinstance(x, dict) else None
            was = v['sources'].get(k)
            if not was or (sources is None and x.get('kind') not in ('덱', '원고')):
                continue
            label = '%s %s %s' % (x.get('kind'), x.get('what', ''), x.get('at', ''))
            try:
                now = _source_read(x, sources, resolve)
            except (KeyError, OSError) as e:
                try:                      # 원 파일(XML·PDF)은 같은데 새 변환에 그 표지가 없다 — 내용 변경이 아니라 at 을 고칠 일
                    same = bool(was.get('orig')) and _source_file(sources, x)[1] == was['orig']
                except (KeyError, OSError):
                    same = False
                if same:
                    converted.append('%s: %s' % (c['id'], label))
                    conv_recheck.append('%s: %s — 새 변환에 이 자리 표지가 없다, at 을 새 표지로 고칠 것' % (c['id'], label)); continue
                changed.append(c['id']); detail.append('%s: 근거 원문 %s 를 찾을 수 없음 (%s)' % (c['id'], label, e)); break
            if now['text'] == was['text']:
                if now['raw'] != was['raw']:
                    fmt_only.append('%s: %s' % (c['id'], label))
                continue
            if was.get('orig') and now.get('orig') == was['orig']:
                converted.append('%s: %s' % (c['id'], label))
                if x.get('verdict') in ('근거 없음', '부분'):
                    conv_recheck.append('%s: %s — 판정 "%s"' % (c['id'], label, x['verdict']))
                continue
            changed.append(c['id']); detail.append('%s: 근거 원문 %s 의 글이 바뀜%s' % (
                c['id'], label, ' (원 파일도 다름)' if was.get('orig') and now.get('orig') else '')); break
    print('=== 검증 이후 변경 ===', file=stream)
    if unverified:
        print('  [!] 아직 검증 기록 없음: %s' % ', '.join(unverified), file=stream)
    for d in detail:
        print('  [변경] %s' % d, file=stream)
    for cid in ex_added:
        print('  [참고] %s: 탐색적 표지가 새로 붙음(false → true) — 하류로 번지지 않는다, mapfreeze 로 다시 기록' % cid, file=stream)
    if fmt_only:
        print('  [같음] 근거 원문 %d곳은 파일은 바뀌었으나 그 자리 본문은 그대로(쪽 표지·머리말·다른 쪽) — 할 일 없음' % len(fmt_only), file=stream)
    if converted:
        print('  [변환] 근거 원문 %d곳은 원 파일(PDF·XML)이 같고 md 변환만 바뀜 — 하류로 번지지 않는다' % len(converted), file=stream)
        for r in conv_recheck:
            print('    다시 볼 것(전에 없던 글이 생겼을 수 있음): %s' % r, file=stream)
    extra = {'format_only': fmt_only, 'converted': converted, 'recheck': conv_recheck, 'exploratory_added': ex_added}
    if not changed and not unverified:
        print('  검증 이후 바뀐 것 없음', file=stream)
        return dict({'changed': [], 'suspect': [], 'unverified': []}, **extra)
    sus = impact(claims, changed, stream) if changed else []
    if changed:
        by_id = {c['id']: c for c in claims}
        direct = []
        for cid in changed:
            direct += [s for s in by_id.get(cid, {}).get('sites', []) if s not in direct]
        print('\n실제로 바뀐 주장의 자리(직접) : %s' % (', '.join(direct) or '(없음)'), file=stream)
        print('위 "다시 봐야 할 자리" 중 나머지는 하류 전파 — 내용이 바뀐 것이 아니라 근거가 흔들린 자리다.', file=stream)
    print('\n위 자리를 확인한 뒤 mapfreeze 로 다시 기록하십시오.', file=stream)
    return dict({'changed': changed, 'suspect': sus, 'unverified': unverified}, **extra)


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

def _edge(to, typ):
    return {'id': to, 'type': typ, 'weight': EDGE_DEFAULT_WEIGHT[typ]}


def _reaches(claims, start, goal):
    """start 에서 depends_on 을 따라 goal 에 닿는가(순환 검사)."""
    by = {c['id']: c for c in claims}
    seen, todo = set(), [start]
    while todo:
        x = todo.pop()
        if x == goal:
            return True
        if x in seen or x not in by:
            continue
        seen.add(x)
        todo += [e['id'] for e in by[x].get('depends_on', []) if isinstance(e, dict)]
    return False


def link_claims(claims, frm, to, typ='premise'):
    """v16.9 (저자 3c): frm 이 to 에 기댄다 — frm.depends_on 에 {to, type, weight=type 기본값}. 없는 id·같은 간선·순환은 ValueError."""
    by = {c['id']: c for c in claims}
    for x in (frm, to):
        if x not in by:
            raise ValueError('없는 주장: %s' % x)
    if frm == to or _reaches(claims, to, frm):
        raise ValueError('%s -> %s 는 순환을 만든다(%s 가 이미 %s 에 기댐)' % (frm, to, to, frm))
    deps = by[frm].setdefault('depends_on', [])
    if any(isinstance(e, dict) and e.get('id') == to for e in deps):
        raise ValueError('%s -> %s 간선이 이미 있다 — 종류를 바꾸려면 파일에서 고친다' % (frm, to))
    deps.append(_edge(to, typ))


def add_claim(claims, cid, statement, role=None, evidence=None, sites=(), keys=(), deps=(), exploratory=False):
    """v16.9 (저자 3c): 주장 하나를 더한다. deps = [(id, type)] — weight 는 type 기본값."""
    if any(c['id'] == cid for c in claims):
        raise ValueError('주장 %s 가 이미 있다' % cid)
    ids = {c['id'] for c in claims}
    for d, typ in deps:
        if d not in ids:
            raise ValueError('없는 주장: %s' % d)
    c = {'id': cid, 'statement': statement}
    if role:
        c['role'] = role
    if evidence:
        c['evidence'] = evidence
    c.update({'sites': list(sites), 'keys': list(keys), 'depends_on': [_edge(d, typ) for d, typ in deps]})
    if exploratory:                               # v16.17: suggest 후보를 주장으로 적을 때 — 사유(exploratory_reason)는 사람이 파일에
        c['exploratory'] = True
    claims.append(c)
    return c


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


def remap_refs(claims, refmap, stream=sys.stdout, suppl=None):
    """claims 를 제자리에서 갱신하고 변경 목록 [(id, 필드, 이전, 이후)] 을 반환.
    매핑에 없는 번호는 그대로 두고 [경고] 로 알린다. 삭제(null)된 번호는 인용에서 빠지고, 인용이 비면 [경고].
    v15.4.1: keys 의 순수 숫자는 어떤 옵션으로도 건드리지 않는다(`--keys-are-refs` 폐기 — 실물에서 참여자 수 42 가 39 로 바뀜).
    인용번호 key 는 `refs 29-31` 로 쓴다. 순수 숫자 key 가 대괄호 인용과 겹치면 [참고] 로만 알린다.
    v16.9 (저자 3b): suppl={옛: 새} 면 statement·evidence 의 `Suppl S{n}`(`Supplementary Table S4 and S2` 처럼 이어진 것도)을 바꾼다.
    매핑에 없거나 삭제(None)된 보충 번호는 그대로 두고 [경고] — 글에서 지우는 것은 사람이 한다."""
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
    def sub_suppl(text, where):
        def one(m):
            n = int(m.group(1))
            if suppl.get(n) is None:
                warns.append('%s: 보충 S%d %s — 그대로 둠' % (where, n, '매핑에 없음' if n not in suppl else '삭제된 보충 표·그림'))
                return m.group(0)
            return 'S%d' % suppl[n]
        return _SUPPL_NUMS.sub(lambda m: m.group(1) + re.sub(r'S(\d+)', one, m.group(2)), text or '')
    for c in claims:
        for fld in ('statement', 'evidence'):
            old = c.get(fld, '')
            new = sub_text(old, '%s.%s' % (c['id'], fld)) if refmap else old
            if suppl and new:
                new = sub_suppl(new, '%s.%s' % (c['id'], fld))
            if new != old:
                c[fld] = new; changes.append((c['id'], fld, old, new))
        newkeys = []
        for k in c.get('keys', []):
            m = _REFS_KEY.match(k) if refmap else None      # v16.9: --suppl 만 줄 때는 인용 key 를 보지 않는다
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


def _hash12(path):
    """파일 sha256 앞 12자리 — manifest·RELEASE 표의 해시. release.py(비공개)도 이것을 쓴다(v16.8.1 — 같은 계산을 두 곳에 두지 않게)."""
    import hashlib
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:12]


def _run_test(folder, t, python=None, env=None):
    """테스트 파일 하나를 folder 에서 돌린다 → (종료 코드, 마지막 줄, stdout). 판정은 부르는 쪽이 한다. release.py 도 쓴다(v16.8.1)."""
    import subprocess
    r = subprocess.run([python or sys.executable, t], capture_output=True, text=True, cwd=folder, env=dict(os.environ, **(env or {})))
    return r.returncode, (r.stdout.strip().splitlines() or [''])[-1], r.stdout


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


_ENV_LIBS = {'pypdf': 'pypdf', 'pillow': 'Pillow', 'python-pptx': 'python-pptx', 'python-docx': 'python-docx'}


def _lib_versions(libs=None):
    """'Python 3.11.15 · pypdf 5.9.0 · Pillow 12.1.1 · …' — 설치 정보만 읽고 불러오지는 않는다. 없으면 '이름 없음'."""
    import platform
    from importlib import metadata
    out = [] if libs else ['Python %s' % platform.python_version()]
    for dist, name in (libs or _ENV_LIBS).items():
        try:
            out.append('%s %s' % (name, metadata.version(dist)))
        except Exception:
            out.append('%s 없음' % name)
    return ' · '.join(out)


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
    s1 = rv == mver and mver is not None
    if mver is None:   # v15.8.3 (코드 리뷰 09-28): 판 없음 = 판 없음 으로 '통과' 하던 것
        problems.append('1단계: TOOLS_MANIFEST.md 의 manifest 판을 읽지 못했다 — 깨졌거나 다른 파일')
    elif not s1:
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
    # v16.9 (발표 4): '통과' 는 이 환경에서의 판정 — 판을 표에 남긴다(3.12 에서만 통과하던 사고 ⑨)
    lines.append('| 환경 | %s | — |' % _lib_versions())
    # 2·3단계
    for f in sorted(need & set(rows)):
        p = os.path.join(folder, f)
        if not os.path.exists(p):
            problems.append('받을 파일 없음: %s' % f); lines.append('| `%s` | 없음 | ✗ |' % f); continue
        want_v, want_h = rows[f]
        got_v = _file_version(p); got_h = _hash12(p)
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
                if f in CODE_ONLY:          # v15.8.2: 비공개 저장소에서 릴리스 사이에도 바뀐다
                    continue
                fp = os.path.join(folder, f)
                if os.path.exists(fp) and _hash12(fp) != h:
                    bad.append(f)
            mh = _hash12(mp)
            lines.append('| ②′ RELEASE §3 대조 | TOOLS_MANIFEST `%s` 외 세트 파일 | %s |' % (mh, '○' if not bad else '✗ ' + ', '.join(bad)))
            for f in bad:
                problems.append('②′ %s 해시가 RELEASE §3 표와 다르다' % f)
    # 테스트
    tests = []
    if run_tests:
        for t in sorted(f for f in present if f.startswith('test_') and f.endswith('.py') and f in need):
            rc, last, _ = _run_test(folder, t, env={'PYTHONDONTWRITEBYTECODE': '1'})   # v15.6.1: __pycache__ 부산물 방지
            last = last or '(출력 없음)'
            tests.append('| `%s` | %s |' % (t, last))
            if rc != 0 or '실패 0' not in last or ('건너뜀' in last and '건너뜀 0' not in last):
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


# ----------------------------------------------------------------------------
# 구연 덧붙임 (v16.12, 사용자 09-30) — 저자 claims(원고용, 읽기 전용)를 판째로 읽고, 발표는 따로 둔 덧붙임 파일에
# 화면 자리(sites)·화면 keys 만 적는다. 두 파일은 읽는 순간 합친다(합친 파일을 남기지 않는다 — 손으로 고칠 세 번째 파일이 없게).
#   덧붙임: {"kind": "구연", "deck": 덱 이름, "source": {file, doc, sha, n, snap}, "use": {저자 id: {sites, keys}}, "claims": [p-…]}
#   snap = 저자 주장마다 role · 글 지문 · 원고 자리·keys 해시 — 원고 문장을 옮기지 않는다(판이 바뀌면 v2.71 sync 가 짝짓는 데 쓴다)
# ----------------------------------------------------------------------------

ORAL_KIND = '구연'
_DECK_SITE = re.compile(r'^(slide|notes)[@:]\d+$')


def _oral_h(s):
    import hashlib
    return hashlib.sha1((s or '').encode('utf8')).hexdigest()[:12]


def _file_sha(path):
    import hashlib
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:16]


def oral_snapshot(claims):
    """{id: {role, text, sites, keys}} — text 는 mapfreeze 와 같은 글 지문, sites·keys 는 mapdiff 짝짓기와 같은 정규화 뒤 해시.
    짝짓기는 정확히 같은 것만 세므로 해시로도 점수가 같다."""
    return {c['id']: {'role': c.get('role'), 'text': _fingerprint(c.get('evidence', '') + '|' + c.get('statement', '')),
                      'sites': sorted({_oral_h(_norm_site(x)) for x in c.get('sites', [])}),
                      'keys': sorted({_oral_h(k.lower()) for k in c.get('keys', [])}),
                      # v16.19 (발표 S1): 간선(대상 id:종류) — 저자 판이 간선만 바꿔도 oral sync 가 알린다. id 는 이미 덧붙임에 있는 이름이라 해시하지 않는다
                      'deps': sorted('%s:%s' % (u, t) for u, t, _ in _edges([c])[c['id']])} for c in claims}


def oral_init(author_path, deck=None, out=None):
    """저자 claims 에서 빈 덧붙임을 만든다. out 을 주면 저장하되 이미 있으면 멈춘다(발표가 적은 자리를 덮지 않게)."""
    import json
    if out and os.path.exists(out):
        raise SystemExit('[멈춤] 덧붙임 %s 이 이미 있다 — 저자 판이 바뀌었으면 oral sync(v2.71), 새로 시작하려면 다른 이름으로' % out)
    meta, cl = load_claims_full(author_path)
    ov = {'kind': ORAL_KIND, 'deck': deck or '', 'note': '',
          'source': {'file': os.path.basename(author_path), 'doc': meta.get('doc') or meta.get('deck') or '',
                     'sha': _file_sha(author_path), 'n': len(cl), 'snap': oral_snapshot(cl)},
          'use': {}, 'claims': []}
    if out:
        with open(out, 'w', encoding='utf8') as f:
            json.dump(ov, f, ensure_ascii=False, indent=2)
    return ov


def oral_merge(author_meta, author, overlay, author_sha=None):
    """(meta, 합친 claims, 문제 목록). 문제: [참고] 가 아니면 [필수].
    합친 그래프 = 쓴 저자 주장(자리·keys·verified 는 덧붙임 것, 글·간선·forbidden·status 는 저자 것) + 그 상류 전부(무대 밖 —
    offstage, 자리 없음) + 발표 주장 p-…(저자 id 에만 기댄다). 하류·쓰지 않은 주장은 넣지 않는다."""
    import copy as _copy
    probs = []
    src = overlay.get('source') or {}
    if overlay.get('kind') != ORAL_KIND:
        probs.append('덧붙임의 kind 가 "%s" 가 아니다(%s)' % (ORAL_KIND, overlay.get('kind')))
    if author_sha and src.get('sha') and src['sha'] != author_sha:
        probs.append('저자 파일이 덧붙임을 만든 판이 다르다(덧붙임 %s %s · 지금 %s) — 저자 판을 따라가려면 oral sync(v2.71)'
                     % (src.get('file', '?'), src['sha'], author_sha))
    by_id = {c['id']: c for c in author}
    use = overlay.get('use') or {}
    for cid, u in use.items():
        if cid not in by_id:
            probs.append('구연이 쓴 저자 주장 %s 이 저자 파일에 없다(화면 %s) — 저자 판이 바뀌었으면 oral sync(v2.71)'
                         % (cid, ', '.join((u or {}).get('sites', [])) or '-'))
            continue
        if by_id[cid].get('status') == 'superseded':
            probs.append('저자가 철회한 주장 %s 이 화면 %s 에 걸려 있다 — 화면에서 빼거나 저자 새 주장으로' % (cid, ', '.join(u.get('sites', [])) or '-'))
        bad = [s_ for s_ in (u or {}).get('sites', []) if not _DECK_SITE.match(str(s_))]
        if bad:
            probs.append('use[%s].sites 는 화면 자리(slide@ID·notes@ID)만 — %s' % (cid, ', '.join(map(str, bad))))
    pcl = overlay.get('claims') or []
    pids = {c.get('id') for c in pcl}
    for c in pcl:
        pid = c.get('id', '')
        if not str(pid).startswith('p-'):
            probs.append('발표 주장 id "%s" 는 p- 로 시작해야 한다(저자 id 와 섞이지 않게)' % pid)
        if pid in by_id:
            probs.append('발표 주장 %s 이 저자 id 와 겹친다' % pid)
        for up, _, _ in _edges([c]).get(pid, []):
            if up not in by_id:
                probs.append('%s: 발표 주장은 저자 id 에만 기댈 수 있다(%s%s)' % (pid, up, ' — 발표 주장' if up in pids else ' — 없는 id'))
    edges = _edges(author)
    todo = [cid for cid in use if cid in by_id] + [up for c in pcl for up, _, _ in _edges([c]).get(c.get('id'), []) if up in by_id]
    keep = set()
    while todo:
        v = todo.pop()
        if v in keep:
            continue
        keep.add(v)
        todo += [up for up, _, _ in edges.get(v, []) if up in by_id]
    out, nokeys, off = [], [], 0
    for c in author:
        if c['id'] not in keep:
            continue
        d = _copy.deepcopy(c)
        d.pop('verified', None)                   # 원고 자리의 확인 기록 — 화면 확인과 섞지 않는다
        if c['id'] in use:
            u = use[c['id']] or {}
            d['sites'] = list(u.get('sites', [])); d['keys'] = list(u.get('keys', []))
            if u.get('verified'):
                d['verified'] = u['verified']
            if u.get('note'):                     # v16.14 (발표 O2): 공식 칸 — 왜 그 화면이 [!] 인지 적는다
                d['oral_note'] = u['note']
            if u.get('keys_missing'):
                d['keys_missing'] = True
            if d['sites'] and not d['keys']:
                nokeys.append(c['id'])
        else:
            d['sites'], d['keys'], d['offstage'] = [], [], True
            ov_ = (overlay.get('offstage_verified') or {}).get(c['id'])
            if ov_:                                   # v16.13: 무대 밖 상류의 글 지문 — 저자가 받침을 고치면 mapstale 이 잡는다
                d['verified'] = ov_
            off += 1
        out.append(d)
    for c in pcl:
        d = _copy.deepcopy(c)
        if d.get('note'):
            d['oral_note'] = d['note']
        if d.get('sites') and not d.get('keys'):
            nokeys.append(d.get('id'))
        out.append(d)
    if nokeys:                                    # 사용자 09-30: 조용히 건너뛰지 않는다
        probs.append('[참고] 화면 keys 없는 주장 %d개(%s) — 그 주장은 keys 검사를 하지 않는다(화면 표현을 use.keys 에)'
                     % (len(nokeys), ', '.join(nokeys[:10]) + (' …' if len(nokeys) > 10 else '')))
    meta = {'deck': overlay.get('deck') or '', 'oral': {'author': src.get('file'), 'used': len([u for u in use if u in by_id]),
                                                        'offstage': off, 'own': len(pcl)}}
    if author_meta.get('kind'):
        meta['kind'] = author_meta['kind']
    return meta, out, probs


def oral_keys_missing(resolve, merged):
    """v16.14 (발표 O1): 화면 keys 가 그 자리에 없는 주장 {id: [자리]} — mapcheck 의 "반영되지 않음" 과 같은 판정(무대 밖·keys 없는 주장은 뺀다)."""
    out = {}
    for c in merged:
        keys = [k.lower() for k in c.get('keys', [])]
        if c.get('offstage') or not keys:
            continue
        for site in c.get('sites', []):
            try:
                txt = resolve(site).lower()
            except Exception:
                continue                          # 못 읽는 자리는 mapfreeze 가 따로 멈춘다
            if not any(_key_hit(k, txt) for k in keys):
                out.setdefault(c['id'], []).append(site)
    return out


def oral_store_verified(overlay, merged, keys_missing=None):
    """v16.13: mapfreeze 가 합친 그래프에 적은 확인 기록을 덧붙임으로 — 쓴 주장은 use[id].verified, 발표 주장은 그 칸,
    무대 밖 상류는 offstage_verified[id](글 지문 — 받침이 바뀌면 mapstale 이 하류 화면까지). 저자 파일에는 쓰지 않는다."""
    use = overlay.setdefault('use', {})
    own = {c.get('id'): c for c in overlay.get('claims') or []}
    km = keys_missing or {}
    for cid, u in use.items():                    # v16.14 (발표 O1): 화면에 keys 가 없던 채로 기록한 주장 — 표시(다시 확인해 keys 가 있으면 빠진다)
        if cid in km:
            u['keys_missing'] = True
        else:
            u.pop('keys_missing', None)
    for pid, c in own.items():
        if pid in km:
            c['keys_missing'] = True
        else:
            c.pop('keys_missing', None)
    offv = {}
    for c in merged:
        v = c.get('verified')
        if not v:
            continue
        if c.get('offstage'):
            offv[c['id']] = v
        elif c['id'] in own:
            own[c['id']]['verified'] = v
        elif c['id'] in use:
            use[c['id']]['verified'] = v
    overlay['offstage_verified'] = offv
    return overlay


def oral_sync(overlay, new_meta, new_claims, new_sha, new_file, pairs=None, drop=()):
    """v16.13 (사용자 09-30 결정 4): 저자 새 판을 따라간다. 반환 (새 덧붙임 또는 None, 알림 줄, [필수] 목록).
    [필수] 가 하나라도 있으면 None — 아무것도 쓰지 않는다. 쓴 id 가 새 판에 없으면 스냅숏 해시로 후보를 찾아 보여 주고
    --pairs 옛=새(1:N 은 리스트)·--drop 옛 전까지 멈춘다. 옮긴 주장은 확인 기록 없이(새 주장이다) — 글이 바뀐 같은 id 는 기록을 두어
    mapstale 이 [변경] 으로 잡게 한다."""
    import copy as _copy, datetime
    ov = _copy.deepcopy(overlay)
    src = ov.get('source') or {}
    if src.get('sha') == new_sha:
        return None, ['같은 판(sha %s) — 할 일 없음' % new_sha], []
    old_snap = src.get('snap') or {}
    new_snap = oral_snapshot(new_claims)
    by_new = {c['id']: c for c in new_claims}
    pairs = dict(pairs or {}); drop = set(drop or ())
    use = ov.setdefault('use', {})
    own = ov.get('claims') or []
    refs = list(use) + [up for c in own for up, _, _ in _edges([c]).get(c.get('id'), []) if not str(up).startswith('p-')]
    hard, lines, moved, dropped = [], [], {}, []

    def where(cid):
        return ', '.join((use.get(cid) or {}).get('sites', [])) or ('발표 주장 ' + ', '.join(c['id'] for c in own if any(u == cid for u, _, _ in _edges([c]).get(c['id'], []))))

    def cands(cid):
        o = old_snap.get(cid) or {}
        s1, k1, g1 = set(o.get('sites', [])), set(o.get('keys', [])), _ROLE_GROUP.get(o.get('role'))
        out = []
        for nid, n in new_snap.items():
            if nid in old_snap and nid != cid:
                continue                          # 옛 판에도 있던 id 는 후보가 아니다(제 자리가 있다)
            g2 = _ROLE_GROUP.get(n.get('role'))
            if g1 and g2 and g1 != g2:
                continue
            sc = 2 * len(s1 & set(n['sites'])) + len(k1 & set(n['keys']))
            if sc:
                out.append((sc, nid))
        return sorted(out, reverse=True)[:3]
    for cid in dict.fromkeys(refs):
        if cid in drop:
            continue
        if cid in pairs:
            tg = pairs[cid] if isinstance(pairs[cid], list) else [pairs[cid]]
            bad = [t for t in tg if t not in by_new]
            if bad:
                hard.append('--pairs %s=%s — 새 판에 %s 이 없다' % (cid, ','.join(tg), ', '.join(bad)))
            elif any(by_new[t].get('status') == 'superseded' for t in tg):
                hard.append('--pairs %s=%s — 새 판에서 철회된 주장으로는 옮기지 않는다' % (cid, ','.join(tg)))
            else:
                moved[cid] = tg
            continue
        if cid not in by_new:
            cs = cands(cid)
            hint = ('후보: %s → --pairs %s=%s' % (', '.join('%s(점수 %d)' % (n, sc) for sc, n in cs), cid, cs[0][1])) if cs \
                else '원고 자리·keys 로 찾은 후보 없음 → --pairs %s=<새 id>' % cid
            hard.append('쓴 주장 %s 이 새 판에 없다(%s) — %s 또는 --drop %s' % (cid, where(cid), hint, cid))
            continue
        if by_new[cid].get('status') == 'superseded' and cid in use:
            hard.append('저자가 새 판에서 철회한 주장 %s 이 화면 %s 에 걸려 있다 → --pairs %s=<새 id> 또는 --drop %s' % (cid, where(cid), cid, cid))
            continue
        if (old_snap.get(cid) or {}).get('text') and old_snap[cid]['text'] != new_snap[cid]['text']:
            lines.append('[변경] 쓴 주장 %s 의 글이 바뀜 — 화면 %s 를 다시 본다(mapstale 이 [변경] 으로 잡는다)' % (cid, where(cid)))
    if hard:
        return None, lines, hard
    for cid, tg in moved.items():
        u = use.pop(cid, None)
        for t in tg:
            if u is not None:
                if t in use:
                    use[t]['sites'] = list(dict.fromkeys(use[t].get('sites', []) + u.get('sites', [])))
                    use[t]['keys'] = list(dict.fromkeys(use[t].get('keys', []) + u.get('keys', [])))
                    use[t].pop('verified', None)
                else:
                    use[t] = {'sites': list(u.get('sites', [])), 'keys': list(u.get('keys', []))}
        lines.append('[옮김] %s → %s%s' % (cid, ', '.join(tg), (' (화면 %s)' % ', '.join(u.get('sites', []))) if u else ''))
    for cid in sorted(drop):
        u = use.pop(cid, None)
        dropped.append(cid)
        lines.append('[뺌] %s%s' % (cid, (' (화면 %s — 그 화면의 글은 사람이 고친다)' % ', '.join(u.get('sites', []))) if u else ''))
    for c in own:                                 # 발표 주장의 기댐도 따라간다
        deps = []
        for e in c.get('depends_on', []):
            e = {'id': e} if isinstance(e, str) else dict(e)
            if e['id'] in moved:
                deps += [dict(e, id=t) for t in moved[e['id']]]
            elif e['id'] in drop:
                lines.append('[참고] 발표 주장 %s 이 기대던 %s 을 뺐다 — 새로 기댈 주장을 적는다' % (c['id'], e['id']))
            else:
                deps.append(e)
        c['depends_on'] = deps
    # v16.19 (발표 S1): 쓴 주장·그 무대 밖 상류의 간선이 늘거나 줄면 [참고] — 새로 걸린 쪽이 화면에 있는지도(결론 화면의 한계가 Limitation 화면에 다 있나)
    ne = _edges(new_claims)
    keep, todo = set(), [x for x in list(use) + [up for c in own for up, _, _ in _edges([c]).get(c.get('id'), [])] if x in by_new]
    while todo:
        v = todo.pop()
        if v not in keep:
            keep.add(v); todo += [u for u, _, _ in ne.get(v, []) if u in by_new]
    olds = [i for i in keep if i in old_snap]
    if olds and not any('deps' in old_snap[i] for i in olds):
        lines.append('[참고] 옛 스냅숏(claim_graph 16.19 전)이라 간선 변화는 보지 않았다 — 이번 sync 부터 적는다')
    for cid in [i for i in new_snap if i in keep and i in old_snap and 'deps' in old_snap[i]]:
        was, now = set(old_snap[cid]['deps']), set(new_snap[cid]['deps'])
        who = ('쓴 주장 %s' if cid in use else '무대 밖 상류 %s') % cid
        for d_ in sorted(now - was):
            up, typ = d_.rsplit(':', 1)
            scr = ', '.join((use.get(up) or {}).get('sites', []))
            lines.append('[참고] %s 에 %s %s 가 새로 걸림 — %s' % (who, typ, up, ('화면 ' + scr) if scr else '화면에 없음'))
        for d_ in sorted(was - now):
            up, typ = d_.rsplit(':', 1)
            lines.append('[참고] %s 에서 %s %s 가 빠짐' % (who, typ, up))
    newids = [i for i in new_snap if i not in old_snap and not any(i in tg for tg in moved.values())]
    gone = [i for i in old_snap if i not in new_snap and i not in use and i not in moved and i not in drop]
    offch = [i for i in (ov.get('offstage_verified') or {}) if i in old_snap and i in new_snap and old_snap[i]['text'] != new_snap[i]['text']]
    if offch:
        lines.append('[참고] 무대 밖 상류 %d개(%s)의 글이 바뀜 — 기대는 화면은 mapstale 이 흔들림으로 잡는다' % (len(offch), ', '.join(offch[:10])))
    if newids:
        lines.append('[참고] 새 저자 주장 %d개(%s) — 구연에 쓸지' % (len(newids), ', '.join(newids[:10]) + (' …' if len(newids) > 10 else '')))
    if gone:
        lines.append('[참고] 저자가 뺀 주장 %d개(%s) — 구연에서 쓰지 않던 것' % (len(gone), ', '.join(gone[:10])))
    ov['offstage_verified'] = {k: v for k, v in (ov.get('offstage_verified') or {}).items() if k in new_snap}
    ov.setdefault('synced', []).append({'from': src.get('sha'), 'to': new_sha, 'date': datetime.date.today().isoformat(),
                                        'moved': moved, 'dropped': dropped})
    ov['source'] = {'file': new_file, 'doc': new_meta.get('doc') or new_meta.get('deck') or src.get('doc', ''),
                    'sha': new_sha, 'n': len(new_claims), 'snap': new_snap}
    return ov, lines, []


def load_oral(overlay_path, author_path):
    """덧붙임 + 저자 파일 → (meta, 합친 claims, 문제). 저자 파일은 읽기만 한다."""
    import json
    with open(overlay_path, encoding='utf8') as f:
        ov = json.load(f)
    am, ac = load_claims_full(author_path)
    return oral_merge(am, ac, ov, author_sha=_file_sha(author_path))


def _claims_arg(a):
    """--claims 하나, 또는 --oral 덧붙임 + --author 저자 파일(v16.12). (meta, claims, 구연 문제). 잘못 주면 종료 코드 2."""
    if getattr(a, 'oral', None) or getattr(a, 'author', None):
        if not (a.oral and a.author) or getattr(a, 'claims', None):
            print('[중단] 구연은 --oral 덧붙임.json --author 저자claims.json 둘 다(--claims 없이)'); sys.exit(2)
        meta, cl, probs = load_oral(a.oral, a.author)
        for p_ in probs:
            print(p_ if p_.startswith('[참고]') else '[필수] ' + p_)
        if any(not p_.startswith('[참고]') for p_ in probs):
            print('[멈춤] 구연 덧붙임에 [필수] 문제 — 고친 뒤 다시'); sys.exit(1)
        return meta, cl, probs
    if not getattr(a, 'claims', None):
        print('[중단] --claims 또는 --oral·--author 가 필요하다'); sys.exit(2)
    meta, cl = load_claims_full(a.claims)
    return meta, cl, []


# ----------------------------------------------------------------------------
# 초점 그림 (v16.15, 사용자 09-30 큰 방향 ②) — 선택한 주장을 가운데, 받침(상류 2단계·한계·반박)과 영향(하류)을 한 그림에.
# 교신저자 이메일용: 쉬운 말 범례, 상자는 문장(선택한 주장은 전문). --png 는 로컬 브라우저(Chrome·Chromium) headless 로 찍는다.
# ----------------------------------------------------------------------------

FOCUS_UP = 2
FOCUS_CDN = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js'
_FOCUS_STYLE = {'focus': 'fill:#ffd8a8,stroke:#c2410c,stroke-width:3px,color:#111',
                'base': 'fill:#d0e7ff,stroke:#1d4ed8,color:#111',
                'context': 'fill:#e5e7eb,stroke:#6b7280,color:#111',
                'limit': 'fill:#fff3cd,stroke:#b58105,stroke-dasharray:4 3,color:#111',
                'rebut': 'fill:#fde2e2,stroke:#b91c1c,color:#111',
                'impact': 'fill:#e9d8fd,stroke:#6b46c1,color:#111',
                'offstage': 'fill:#fafafa,stroke:#aaaaaa,stroke-dasharray:2 3,color:#777'}
_FOCUS_WORD = [('focus', '선택한 주장'), ('base', '핵심 근거'), ('context', '배경'), ('limit', '한계'), ('rebut', '반박'), ('impact', '영향받는 결론')]


def focus_graph(claims, ids, up=FOCUS_UP):
    """{'claims', 'ids', 'kind': {id: focus|base|limit|rebut|impact}, 'edges': [(위, 종류, 아래)]}.
    받침 = premise·support·context 로 up 단계까지, 한계(caveat)·반박(rebuttal) = 선택한 주장과 받침 1단계에 직접 달린 것,
    영향 = impact 의 하류(강도 IMPACT_CUTOFF 이상)."""
    by = {c['id']: c for c in claims}
    bad = [i for i in ids if i not in by]
    if bad:
        raise ValueError('없는 주장 id: %s' % ', '.join(bad))
    edges = _edges(claims)
    kind = {i: 'focus' for i in ids}
    level = {i: 0 for i in ids}
    frontier = list(ids)
    for depth in range(1, up + 1):
        nxt = []
        for v in frontier:
            for u, typ, _ in edges.get(v, []):
                if u not in by or typ not in ('premise', 'support', 'context'):
                    continue
                # v16.16 (사용자 09-30): 배경 — role background 이거나 context 로만 닿은 받침은 핵심 근거와 나눈다
                k_ = 'context' if (typ == 'context' or by[u].get('role') == 'background') else 'base'
                if u not in kind:
                    kind[u] = k_; level[u] = depth; nxt.append(u)
                elif kind[u] == 'context' and k_ == 'base':
                    kind[u] = 'base'
        frontier = nxt
    for v in [x for x, lv in level.items() if lv <= 1]:
        for u, typ, _ in edges.get(v, []):
            if u in by and u not in kind and typ in ('caveat', 'rebuttal'):
                kind[u] = 'limit' if typ == 'caveat' else 'rebut'
    for cid, strength, _ in impact(claims, list(ids), stream=io.StringIO()):
        if strength >= IMPACT_CUTOFF and cid not in kind:
            kind[cid] = 'impact'
    drawn = [(u, typ, v) for v in kind for u, typ, _ in edges.get(v, []) if u in kind]
    return {'claims': [by[i] for i in by if i in kind], 'ids': list(ids), 'kind': kind, 'edges': drawn}


def _focus_text(c, full, ids, screen):
    if ids:
        t = c['id']
    else:
        st = re.sub(r'\s+', ' ', c.get('statement', '') or c['id']).strip()
        if full:
            words, lines, cur = st.split(' '), [], ''
            for w in words:
                if cur and len(cur) + 1 + len(w) > 34:
                    lines.append(cur); cur = w
                else:
                    cur = (cur + ' ' + w).strip()
            lines.append(cur)
            t = '<br/>'.join(lines)
        else:
            t = st if len(st) <= 40 else st[:40].rstrip() + '…'
    if c.get('exploratory') is True:              # v16.17: 탐색적 주장 — 글자만
        t += '<br/>(탐색)'
    if c.get('offstage'):
        t += '<br/>(화면에 없음)'
    elif c.get('sites') and screen is not False:
        scr = [(screen(x) if screen else x) for x in c['sites'] if _DECK_SITE.match(str(x))]
        if scr:
            t += '<br/>' + ', '.join(dict.fromkeys(scr))
    return t.replace('"', '#quot;')


def focus_mermaid(fg, ids=False, screen=None):
    """mermaid 글 — 받침 | 선택한 주장 | 영향 세 칸(LR). screen(자리) → '화면 N' 을 주면 화면 번호로."""
    kind = fg['kind']; nid = {c['id']: 'n%d' % k for k, c in enumerate(fg['claims'], 1)}
    L = ['flowchart LR']
    cols = [('s_up', '받침', ('base', 'context', 'limit', 'rebut')), ('s_focus', '선택한 주장', ('focus',)), ('s_down', '영향', ('impact',))]
    for sid, title, ks in cols:
        mem = [c for c in fg['claims'] if kind[c['id']] in ks]
        if not mem:
            continue
        L.append('  subgraph %s["%s"]' % (sid, title))
        for c in mem:
            L.append('    %s["%s"]' % (nid[c['id']], _focus_text(c, kind[c['id']] == 'focus' and not ids, ids, screen)))
        L.append('  end')
    for u, typ, v in fg['edges']:
        L.append('  %s %s %s' % (nid[u], _EDGE_ARROW.get(typ, '-->'), nid[v]))
    for k_, style in _FOCUS_STYLE.items():
        if k_ == 'offstage':
            continue
        mem = [nid[c['id']] for c in fg['claims'] if kind[c['id']] == k_ and not c.get('offstage')]
        if mem:
            L += ['  classDef %s %s' % (k_, style), '  class %s %s' % (','.join(mem), k_)]
        off = [nid[c['id']] for c in fg['claims'] if kind[c['id']] == k_ and c.get('offstage')]
        if off:                                    # v16.16 (사용자 09-30): 무대 밖도 종류 색을 흐리게 — 범례와 맞게
            L += ['  classDef %s_off %s' % (k_, _faded(style)), '  class %s %s_off' % (','.join(off), k_)]
    return '\n'.join(L) + '\n'


def _faded(style):
    """종류 색을 흰색 쪽으로 60% 섞고 테두리는 점선·글은 흐리게(무대 밖)."""
    def mix(m):
        h = m.group(1)
        if len(h) == 3:
            h = ''.join(ch * 2 for ch in h)
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        return '#%02x%02x%02x' % tuple(int(v + (255 - v) * 0.6) for v in (r, g, b))
    fill = re.sub(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', mix, re.search(r'fill:(#\w+)', style).group(0))
    stroke = re.search(r'stroke:(#\w+)', style)
    return '%s,stroke:%s,stroke-dasharray:3 3,color:#666' % (fill, stroke.group(1) if stroke else '#999')


def focus_legend(fg):
    """[(말, 스타일)] — 그림에 있는 것만. 반박 선이 없으면 반박도 뺀다(사용자 09-30)."""
    have = set(fg['kind'].values())
    if not any(t == 'rebuttal' for _, t, _ in fg['edges']):
        have.discard('rebut')
    out = [(w, _FOCUS_STYLE[k]) for k, w in _FOCUS_WORD if k in have]
    if any(c.get('offstage') for c in fg['claims']):
        out.append(('화면에 없음', _FOCUS_STYLE['offstage']))
    if any(c.get('exploratory') is True for c in fg['claims']):
        out.append(('(탐색) = 탐색적 주장', 'fill:#ffffff,stroke:#999999'))
    return out


def focus_md(fg, ids=False, screen=None):
    L = ['# 초점 그림 — %s' % ', '.join(fg['ids']), '', '```mermaid', focus_mermaid(fg, ids, screen).rstrip(), '```', '', '범례: ' + ' · '.join(w for w, _ in focus_legend(fg)), '']
    return '\n'.join(L)


def find_mermaid_js(given=None, cwd=None, env=None):
    """(src, 어디서) — ① --mermaid-js ② 환경변수 CLAIM_GRAPH_MERMAID_JS ③ npm 으로 받은 node_modules/mermaid/dist/mermaid.min.js
    (지금 폴더·이 파일 옆·홈) ④ CDN(마지막 — claude.ai 컨테이너는 jsdelivr 가 막혀 있다, 사용자 09-30)."""
    env = os.environ if env is None else env
    if given:
        if not os.path.exists(given):
            raise ValueError('--mermaid-js %s 가 없다' % given)
        return os.path.abspath(given), '--mermaid-js'
    e = env.get('CLAIM_GRAPH_MERMAID_JS')
    if e:
        if not os.path.exists(e):
            raise ValueError('환경변수 CLAIM_GRAPH_MERMAID_JS=%s 가 없다' % e)
        return os.path.abspath(e), '환경변수'
    for base in (cwd or os.getcwd(), os.path.dirname(os.path.abspath(__file__)), os.path.expanduser('~')):
        p = os.path.join(base, 'node_modules', 'mermaid', 'dist', 'mermaid.min.js')
        if os.path.exists(p):
            return os.path.abspath(p), 'npm node_modules'
    return FOCUS_CDN, 'CDN'


def focus_html(fg, mermaid_src, ids=False, screen=None, title=''):
    import html as _h
    src = ('file://' + mermaid_src) if mermaid_src.startswith('/') else mermaid_src
    leg = ''.join('<span class="k"><i style="%s"></i>%s</span>' % (_h.escape(st.replace(',', ';').replace('fill:', 'background:').replace('stroke-dasharray:4 3', '').replace('stroke-dasharray:2 3', '')), _h.escape(w))
                  for w, st in focus_legend(fg))
    return ('<!doctype html><html><head><meta charset="utf-8"><title>%s</title><style>'
            'body{margin:24px;background:#fff;font-family:-apple-system,"Apple SD Gothic Neo","Noto Sans CJK KR","Noto Sans KR",sans-serif;color:#111}'
            '.leg{margin-top:14px;font-size:15px}.k{margin-right:18px;white-space:nowrap}.k i{display:inline-block;width:14px;height:14px;border:1px solid #666;'
            'vertical-align:-2px;margin-right:6px}</style></head><body><pre class="mermaid">%s</pre><div class="leg">%s</div>'
            '<script src="%s" onerror="document.title=\'mermaid-load-failed\'"></script><script>'
            'if(!window.mermaid){document.title="mermaid-load-failed"}else{'
            'mermaid.initialize({startOnLoad:false,flowchart:{htmlLabels:true,wrappingWidth:520},'
            'fontFamily:\'-apple-system,"Apple SD Gothic Neo","Noto Sans CJK KR",sans-serif\'});'
            'mermaid.run().then(function(){document.title=document.querySelector("pre.mermaid svg")?"done":"mermaid-error: svg 없음"})'
            '.catch(function(e){document.title="mermaid-error: "+((e&&e.message)||e)})}</script></body></html>'
            % (_h.escape(title or ', '.join(fg['ids'])), _h.escape(focus_mermaid(fg, ids, screen)), leg, _h.escape(src)))


def find_browser(env=None):
    """headless 로 찍을 브라우저. 환경변수 CLAIM_GRAPH_BROWSER(= none 이면 끔) → macOS Chrome·Chromium → Linux /opt/pw-browsers/chromium-*/chrome-linux/chrome
    (claude.ai 컨테이너) → PATH 의 chromium·google-chrome. 없으면 None."""
    import glob, shutil
    env = os.environ if env is None else env
    e = env.get('CLAIM_GRAPH_BROWSER')
    if e:
        return None if e.lower() == 'none' else e
    for p in ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium'):
        if os.path.exists(p):
            return p
    pw = sorted(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome'), key=lambda q: [int(x) for x in re.findall(r'\d+', q)], reverse=True)
    if pw:
        return pw[0]
    for n in ('chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable'):
        w = shutil.which(n)
        if w:
            return w
    return None


def _mermaid_status(dom):
    """--dump-dom 결과로 mermaid 가 실제로 그렸는지. (됨, 까닭). v16.16 (부관리자 09-30 [결함]): 못 그렸는데 글자만 찍힌 PNG 를 저장했다."""
    t = re.search(r'<title>([^<]*)</title>', dom or '')
    t = t.group(1).strip() if t else ''
    pre = re.search(r'<pre class="mermaid"[^>]*>(.*?)</pre>', dom or '', re.S)
    svg = bool(pre and '<svg' in pre.group(1)) or (not pre and '<svg' in (dom or ''))
    if t == 'done' and svg:
        return True, ''
    if t.startswith('mermaid-load-failed'):
        return False, 'mermaid 파일을 받지 못함(파일·주소를 읽지 못했거나 mermaid 가 아님)'
    if t.startswith('mermaid-error'):
        return False, 'mermaid 오류: %s' % t.split(':', 1)[-1].strip()
    return False, '제한 시간 안에 그리지 못함(mermaid 를 받지 못했을 수 있다)'


def _browser_pass(browser, extra, html_path, done, timeout):
    """브라우저를 한 번 돌린다 — done() 이 참이 되거나 끝나거나 제한 시간이면 그 임시 프로필의 브라우저만 끈다(찍은 뒤 끝나지 않는 Chrome, 09-30).
    반환 표준출력 글."""
    import subprocess, tempfile, time, shutil, signal
    prof = tempfile.mkdtemp(prefix='cg_chrome_')
    outf = os.path.join(prof, '_stdout.txt')
    cmd = [browser, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--hide-scrollbars',
           '--user-data-dir=%s' % prof] + extra + ['file://' + os.path.abspath(html_path)]
    if hasattr(os, 'geteuid') and os.geteuid() == 0:
        cmd.insert(1, '--no-sandbox')              # 컨테이너(root)
    with open(outf, 'w') as fo:
        p = subprocess.Popen(cmd, stdout=fo, stderr=subprocess.DEVNULL, start_new_session=True)
        t0 = time.time()
        try:
            while time.time() - t0 < timeout:
                if done(outf) or p.poll() is not None:
                    break
                time.sleep(0.3)
        finally:
            if p.poll() is None:
                try:
                    os.killpg(p.pid, signal.SIGTERM)
                except Exception:
                    p.terminate()
                try:
                    p.wait(5)
                except Exception:
                    p.kill()
    out = open(outf, encoding='utf8', errors='replace').read()
    shutil.rmtree(prof, ignore_errors=True)
    return out


def render_png(html_path, png_path, browser, size=(1800, 1400), timeout=90):
    """① --dump-dom 으로 mermaid SVG 가 실제로 생겼는지 본다 — 없으면 PNG 를 저장하지 않는다(v16.16) ② headless 로 찍고 여백을 자른다(2배).
    반환 (성공, 알림)."""
    if os.path.exists(png_path):
        os.remove(png_path)
    dom = _browser_pass(browser, ['--virtual-time-budget=15000', '--dump-dom'], html_path,
                        lambda f: '</html>' in open(f, encoding='utf8', errors='replace').read(), timeout)
    ok, why = _mermaid_status(dom)
    if not ok:
        return False, 'mermaid 가 그리지 못했다(%s) — npm install mermaid@11 또는 --mermaid-js 로 mermaid.min.js 를 준다. PNG 는 만들지 않았다' % why
    last = [-1]

    def shot_done(_f):
        if os.path.exists(png_path):
            sz = os.path.getsize(png_path)
            if sz and sz == last[0]:
                return True
            last[0] = sz
        return False
    _browser_pass(browser, ['--force-device-scale-factor=2', '--window-size=%d,%d' % size, '--virtual-time-budget=15000',
                            '--screenshot=%s' % png_path], html_path, shot_done, timeout)
    if not os.path.exists(png_path) or not os.path.getsize(png_path):
        return False, 'PNG 를 만들지 못했다(%d초) — %s 를 브라우저로 열어 저장한다' % (timeout, html_path)
    note = ''
    try:
        from PIL import Image, ImageChops
        im = Image.open(png_path).convert('RGB')
        box = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).getbbox()
        if box:
            m = 40
            if box[3] >= im.size[1] - 2 or box[2] >= im.size[0] - 2:
                note = '[참고] 그림이 창(%dx%d)보다 커서 잘렸을 수 있다 — --size 를 키운다' % size
            im.crop((max(0, box[0] - m), max(0, box[1] - m), min(im.size[0], box[2] + m), min(im.size[1], box[3] + m))).save(png_path)
    except Exception as e:
        note = '[참고] 여백을 자르지 못했다(%s)' % type(e).__name__
    return True, note

_CLAIMS_ONLY = ('mapgraph', 'gaps', 'impact', 'mapdraw', 'mapreport', 'scaffold', 'add', 'link', 'suggest', 'litcheck')


def main():
    import argparse
    ap = argparse.ArgumentParser(description='주장 의존 그래프 (문서 독립)')
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('mapgraph'); g.add_argument('--claims', default=None)
    g.add_argument('--sources', default=None, help='문헌 보관소 — 문헌 근거가 보관소에 없으면 [필수], 판정이 없으면 [참고] (v16.5)')
    gp = sub.add_parser('gaps', help='근거 공백 작업표 · 채운 표 → literature 검증지시 (v16.5)')
    gp.add_argument('--claims', default=None); gp.add_argument('-o', required=True)
    gp.add_argument('--to-instr', default=None, metavar='작업표.md', help='채운 작업표를 literature 검증지시로')
    gp.add_argument('--name', default=None, help='원고 이름(검증지시의 "> 원고:" 줄) — 없으면 claims 의 doc')
    sg = sub.add_parser('suggest', help='새 주장 후보 — [참고]만, claims 는 바꾸지 않는다 (v16.17)')
    sg.add_argument('--claims', required=True); sg.add_argument('-o', default=None, help='같은 내용을 md 로도')
    sg.add_argument('--min-shared', type=int, default=SUGGEST_MIN_SHARED, help='규칙 1 — 함께 쓰는 근거 수(기본 %d)' % SUGGEST_MIN_SHARED)
    sg.add_argument('--min-caveat', type=int, default=SUGGEST_MIN_CAVEAT, help='규칙 3 — 한계가 걸린 주장 수(기본 %d)' % SUGGEST_MIN_CAVEAT)
    i = sub.add_parser('impact'); i.add_argument('--claims', default=None); i.add_argument('ids', nargs='+')
    i.add_argument('--sites', action='store_true', help='자리 목록만 한 줄에 하나씩 (v15.5, 저자 v48 목록 검증용)')
    dr = sub.add_parser('mapdraw', help='관계도 Mermaid 글(md) — 전체 또는 --impact 주장 경로 (v16)')
    dr.add_argument('--claims', default=None); dr.add_argument('-o', required=True, help='쓸 md 파일')
    dr.add_argument('--impact', nargs='+', default=None, metavar='ID', help='이 주장들이 바뀌었을 때의 하류만')
    dr.add_argument('--text', action='store_true', help='상자에 statement 앞 40자도')
    dr.add_argument('--all-edges', action='store_true', help='전체 그림을 v16.0 모양으로 — 아래→위, caveat 상자·간선까지 모두 (v16.1)')
    for p_ in (g, i, dr):                 # v16.12: 구연 — 저자 파일(읽기 전용) + 덧붙임을 읽는 순간 합쳐서
        p_.add_argument('--oral', default=None, metavar='덧붙임.json'); p_.add_argument('--author', default=None, metavar='저자claims.json')
    for p_ in (g, i):                     # v16.21 (④ 2판): lit_links 가 가리키는 논문 주장을 읽는 순간 합쳐서(파일은 남기지 않는다)
        p_.add_argument('--lit', default=None, metavar='문헌보관소', help='lit_links 의 논문 주장을 lit:<DOI>#<id> 로 합쳐서 (v16.21)')
    lc = sub.add_parser('litcheck', help='우리 그래프의 lit_links(논문 주장 짝) 검사 — 보관소의 논문 그래프와 대조 (v16.21)')
    lc.add_argument('--claims', required=True); lc.add_argument('--store', required=True, metavar='문헌보관소')
    fo = sub.add_parser('focus', help='초점 그림 — 선택한 주장의 받침(상류 2단계·한계·반박)과 영향(하류), 이메일용 (v16.15)')
    fo.add_argument('ids', nargs='+'); fo.add_argument('--claims', default=None); fo.add_argument('-o', required=True, help='쓸 md')
    fo.add_argument('--oral', default=None); fo.add_argument('--author', default=None)
    fo.add_argument('--up', type=int, default=FOCUS_UP, help='받침 단계(기본 2)'); fo.add_argument('--ids', dest='ids_flag', action='store_true', help='상자에 id 만')
    fo.add_argument('--pptx', default=None, help='구연: 화면 자리를 화면 번호로(덱)')
    fo.add_argument('--png', default=None, help='PNG 도 — 로컬 브라우저 headless'); fo.add_argument('--mermaid-js', default=None, help='mermaid.min.js 파일(없으면 환경변수·npm·CDN 순)')
    fo.add_argument('--size', default='1800x1400', help='찍을 창 크기(2배로 찍힌다)')
    orl = sub.add_parser('oral', help='구연 덧붙임 — 저자 claims 는 읽기만, 화면 자리·keys 는 덧붙임에 (v16.12)')
    orl.add_argument('what', choices=('init', 'check', 'sync')); orl.add_argument('--author', required=True, metavar='저자claims.json')
    orl.add_argument('--oral', default=None, metavar='덧붙임.json', help='check 에서 읽을 덧붙임'); orl.add_argument('-o', default=None, help='init 이 쓸 덧붙임')
    orl.add_argument('--deck', default=None, help='init: 덧붙임의 덱 이름')
    orl.add_argument('--pairs', default=None, help='sync: 사라진 쓴 id 의 새 id — 옛=새, 1:N 은 같은 옛을 반복(mapdiff 와 같은 문법) (v16.13)')
    orl.add_argument('--drop', default=None, help='sync: 구연에서 뺄 옛 id, 쉼표로 (v16.13)')
    for name in ('mapcheck', 'mapfreeze', 'mapstale'):
        p = sub.add_parser(name); p.add_argument('doc'); p.add_argument('--claims', required=True)
        if name in ('mapfreeze', 'mapstale'):
            p.add_argument('--sources', default=None, help='근거 원문 폴더(문헌 보관소·교과서 분할) — 주면 근거 원문 바뀜도 본다 (v16)')
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
    d.add_argument('--save-pairs', action='store_true', help='--pairs 를 a 그래프의 맨 위 칸 pairs_with[b 라벨] 에 적어 둔다 — 다음부터 --pairs 없이 (v16)')
    rr = sub.add_parser('remap-refs', help='참고문헌 재번호 매핑으로 claims 의 인용번호 갱신 (v15.4, #4)')
    rr.add_argument('--claims', required=True); rr.add_argument('--map', default=None, dest='refmap', help='본문 인용 [n] 매핑 json')
    rr.add_argument('--suppl', default=None, help='보충 표·그림 `Suppl S{n}` 매핑 json — 형식은 --map 과 같다 (v16.9)')
    rr.add_argument('-o', required=True)
    rr.add_argument('--force', action='store_true', help='같은 매핑이 이미 적용된 그래프에도 다시 적용 (기본은 중단 — 두 번 적용하면 번호가 두 단계 밀린다)')
    ad = sub.add_parser('add', help='주장 하나 더하기 — 간선 weight 는 type 기본값 (v16.9)')
    ad.add_argument('--claims', required=True); ad.add_argument('--id', required=True); ad.add_argument('--statement', required=True)
    ad.add_argument('--role', choices=CLAIM_ROLES, default=None); ad.add_argument('--evidence', default=None)
    ad.add_argument('--site', action='append', default=[]); ad.add_argument('--key', action='append', default=[])
    ad.add_argument('--dep', action='append', default=[], metavar='ID[:type]', help='이 주장이 기대는 주장(type 기본 premise). 여러 번')
    ad.add_argument('--exploratory', action='store_true', help='탐색적 주장 표지 — 사유(exploratory_reason)는 파일에 (v16.17)')
    ad.add_argument('-o', required=True)
    lk = sub.add_parser('link', help='간선 하나 — FROM 이 TO 에 기댄다, weight 는 type 기본값 (v16.9)')
    lk.add_argument('--claims', required=True); lk.add_argument('frm', metavar='FROM'); lk.add_argument('to', metavar='TO')
    lk.add_argument('--type', choices=EDGE_TYPES, default='premise'); lk.add_argument('-o', required=True)
    sc = sub.add_parser('selfcheck', help='세트 자가 점검: 3단계 확인 + 파일 분류 + 회신용 표 (v15.6)')
    sc.add_argument('--dir', default=os.path.dirname(os.path.abspath(__file__)), help='세트가 있는 폴더 (기본: 이 파일의 폴더, 프로젝트에서는 /mnt/project)')
    sc.add_argument('--tests', action='store_true', help='그 프로젝트의 test_*.py 도 돌린다')
    sc.add_argument('--role', default=None, help='저자 / 발표 / 리뷰어 / 코드 — GitHub 에서 받은 전체 세트에서 쓸 역할 (v15.7)')
    sc.add_argument('--compare', default=None, help='예비 폴더(예: /mnt/project)와 판·해시 대조 (v15.7)')
    # v16.9 (발표 3): `mapgraph claims.json` 처럼 파일 이름만 주면 argparse 의 '--claims 필수' 대신 고칠 명령을 보여 준다
    argv = sys.argv[1:]
    if len(argv) >= 2 and argv[0] in _CLAIMS_ONLY and '--claims' not in argv and argv[1].endswith('.json'):
        print('[중단] 파일은 --claims 로 준다: %s --claims %s %s' % (argv[0], argv[1], ' '.join(argv[2:])))
        sys.exit(2)
    a = ap.parse_args()
    if a.cmd in ('add', 'link'):
        meta, cl = load_claims_full(a.claims)
        try:
            if a.cmd == 'add':
                deps = [(d.split(':', 1)[0], d.split(':', 1)[1] if ':' in d else 'premise') for d in a.dep]
                bad = [t for _, t in deps if t not in EDGE_TYPES]
                if bad:
                    raise ValueError('간선 종류 %s — %s 중 하나' % (', '.join(bad), '/'.join(EDGE_TYPES)))
                add_claim(cl, a.id, a.statement, a.role, a.evidence, a.site, a.key, deps, exploratory=a.exploratory)
            else:
                link_claims(cl, a.frm, a.to, a.type)
        except ValueError as e:
            print('[중단] %s' % e); sys.exit(2)
        print('저장: %s' % save_claims(a.o, cl, meta=meta)); sys.exit(0)
    if a.cmd == 'selfcheck':
        r = selfcheck(a.dir, run_tests=a.tests, role=a.role, compare=a.compare)
        sys.exit(0 if r['ok'] else 1)
    if a.cmd == 'gaps':
        if a.to_instr:
            md, notes = gaps_to_instr(open(a.to_instr, encoding='utf8').read(), a.name or '원고')
            open(a.o, 'w', encoding='utf8').write(md)
            for n_ in notes:
                print('[참고] %s' % n_)
            print('저장: %s' % a.o); sys.exit(0)
        if not a.claims:
            print('[중단] gaps 는 --claims(작업표 만들기) 또는 --to-instr(검증지시로) 가 필요하다'); sys.exit(2)
        name, _, cl = load_claims_meta(a.claims)
        open(a.o, 'w', encoding='utf8').write(gaps_table(cl, a.name or doc_name(name or '원고')))
        print('저장: %s (공백 %d)' % (a.o, len(find_gaps(cl)[0]))); sys.exit(0)
    if a.cmd == 'focus':
        meta_, cl_, _ = _claims_arg(a)
        try:
            fg_ = focus_graph(cl_, a.ids, up=a.up)
        except ValueError as e:
            print('[중단] %s' % e); sys.exit(2)
        scr_ = None
        if a.pptx:
            import deck_toolkit as _T
            dk_ = _T.Deck.open(a.pptx)
            def scr_(site_, _dk=dk_):
                m_ = re.search(r'\(화면 (\d+)\)', _T._relabel_sldid(_dk, site_))
                return '화면 %s' % m_.group(1) if m_ else site_
        with open(a.o, 'w', encoding='utf8') as f_:
            f_.write(focus_md(fg_, ids=a.ids_flag, screen=scr_))
        print('저장: %s (선택 %d · 받침 %d · 한계·반박 %d · 영향 %d)' % (a.o, *[sum(1 for v in fg_['kind'].values() if v in ks) for ks in (('focus',), ('base',), ('limit', 'rebut'), ('impact',))]))
        if not a.png:
            sys.exit(0)
        try:
            js_, how_ = find_mermaid_js(a.mermaid_js)
        except ValueError as e:
            print('[중단] %s' % e); sys.exit(2)
        hp_ = os.path.splitext(a.png)[0] + '.html'
        with open(hp_, 'w', encoding='utf8') as f_:
            f_.write(focus_html(fg_, js_, ids=a.ids_flag, screen=scr_))
        br_ = find_browser()
        if not br_:
            print('[!] 브라우저(Chrome·Chromium)를 찾지 못해 PNG 를 만들지 못했다 — %s 를 브라우저로 열어 저장하거나 CLAIM_GRAPH_BROWSER 로 경로를 준다' % hp_)
            sys.exit(1)
        w_, h_ = (int(x) for x in a.size.lower().split('x'))
        ok_, note_ = render_png(hp_, a.png, br_, size=(w_, h_))
        print('mermaid: %s (%s) · 브라우저: %s' % (js_ if how_ != 'CDN' else FOCUS_CDN, how_, br_))
        if not ok_:
            print('[!] ' + note_); sys.exit(1)
        if note_:
            print(note_)
        print('PNG: %s' % a.png)
        sys.exit(0)
    if a.cmd == 'oral':
        if a.what == 'init':
            if not a.o:
                print('[중단] oral init 은 -o 덧붙임.json'); sys.exit(2)
            ov = oral_init(a.author, deck=a.deck, out=a.o)
            print('덧붙임 저장: %s (저자 %s · 주장 %d · sha %s) — use 에 화면 자리·keys 를 적는다' % (a.o, ov['source']['file'], ov['source']['n'], ov['source']['sha']))
            sys.exit(0)
        if not a.oral:
            print('[중단] oral %s 는 --oral 덧붙임.json' % a.what); sys.exit(2)
        if a.what == 'sync':
            import json as _json
            if not a.o:
                print('[중단] oral sync 는 -o 새 덧붙임.json(같은 이름이면 덮는다)'); sys.exit(2)
            ov_ = _json.load(open(a.oral, encoding='utf8'))
            nm_, nc_ = load_claims_full(a.author)
            new_, lines_, hard_ = oral_sync(ov_, nm_, nc_, _file_sha(a.author), os.path.basename(a.author),
                                            pairs=parse_pairs(a.pairs) if a.pairs else None,
                                            drop=[x.strip() for x in (a.drop or '').split(',') if x.strip()])
            for l_ in lines_:
                print(l_)
            for h_ in hard_:
                print('[필수] ' + h_)
            if hard_:
                print('[멈춤] 덧붙임을 쓰지 않았다 — 위 [필수] 를 --pairs·--drop 으로 정한 뒤 다시'); sys.exit(1)
            if new_ is None:
                sys.exit(0)
            with open(a.o, 'w', encoding='utf8') as f_:
                _json.dump(new_, f_, ensure_ascii=False, indent=2)
            print('덧붙임 저장: %s (저자 %s · sha %s) — 이어서 oral check 와 mapstale' % (a.o, new_['source']['file'], new_['source']['sha']))
            sys.exit(0)
        meta_, cl_, probs = load_oral(a.oral, a.author)
        for p_ in probs:
            print(p_ if p_.startswith('[참고]') else '[필수] ' + p_)
        o_ = meta_.get('oral', {})
        print('구연: 쓴 저자 주장 %d · 무대 밖 상류 %d개 · 발표 주장 %d' % (o_.get('used', 0), o_.get('offstage', 0), o_.get('own', 0)))
        gp_, _ = mapgraph(cl_, kind=meta_.get('kind'))
        sys.exit(1 if any(not p_.startswith('[참고]') for p_ in probs + gp_) else 0)
    if a.cmd == 'litcheck':
        meta_, cl_ = load_claims_full(a.claims)
        n = len(meta_.get('lit_links') or []) if isinstance(meta_.get('lit_links'), list) else 0
        if meta_.get('lit_links') is None:
            print('lit_links 없음 — 짝을 맺은 논문 주장이 없다'); sys.exit(0)
        merged, lp = lit_merge(meta_, cl_, a.store)
        lits = [c for c in merged if c.get('lit')]
        print('=== 문헌 짝 (lit_links) ===')
        print('짝 %d · 논문 주장 %d(판정 대기 %d) · 논문 %d편' % (n, len(lits), sum(c.get('status') == 'proposed' for c in lits),
                                                         len({c['id'].split('#')[0] for c in lits})))
        for p_ in lp:
            print(p_ if p_.startswith('[참고]') else '[필수] ' + p_)
        if not lp:
            print('문제 없음')
        sys.exit(1 if any(not p_.startswith('[참고]') for p_ in lp) else 0)
    if getattr(a, 'lit', None) and getattr(a, 'oral', None):
        print('[중단] --lit 과 --oral 은 아직 같이 쓰지 않는다(④ 2판) — 저자 claims 에 --claims 로'); sys.exit(2)
    if a.cmd == 'mapgraph':
        meta_, cl_, _ = _claims_arg(a)
        lp_ = []
        if a.lit:
            cl_, lp_ = lit_merge(meta_, cl_, a.lit)
            print('문헌: 논문 주장 %d개를 lit:<DOI>#<id> 로 합침(보관소 %s)' % (sum(1 for c in cl_ if c.get('lit')), a.lit))
        elif isinstance(meta_.get('lit_links'), list) and meta_['lit_links']:
            print('[참고] lit_links %d개 — 논문 주장까지 보려면 --lit <문헌 보관소>, 짝 검사는 litcheck' % len(meta_['lit_links']))
        probs, _ = mapgraph(cl_, sources=a.sources, kind=meta_.get('kind'))
        for p_ in lp_:
            print('  [!] %s' % (p_ if p_.startswith('[참고]') else '[필수] ' + p_))
        probs = probs + lp_
        if meta_.get('kind') in LIT_KINDS:          # v16.19 (④ 1판): 문헌 그래프 — doi·meta.md·id·사람 이름 꼴·판정 대기
            lp = lit_graph_problems(meta_, cl_, a.claims)
            for p_ in lp:
                print('  [!] %s' % p_)
            probs = probs + lp
        sys.exit(1 if any(not p.startswith('[참고]') for p in probs) else 0)
    elif a.cmd == 'impact':
        meta_, cl, _ = _claims_arg(a)
        if a.lit:                                   # v16.21: 논문 주장이 바뀌거나 철회되면 우리 하류 — impact lit:<DOI>#<id> --lit 보관소
            cl, lp_ = lit_merge(meta_, cl, a.lit)
            for p_ in lp_:
                if not p_.startswith('[참고]'):
                    print('  [!] [필수] %s' % p_)
        if a.sites:
            rows = impact(cl, a.ids, stream=io.StringIO())
            by_id = {c['id']: c for c in cl}
            seen = []
            for cid in a.ids + [r[0] for r in rows if r[1] >= IMPACT_CUTOFF]:
                for s in by_id.get(cid, {}).get('sites', []):
                    if s not in seen:
                        seen.append(s); print(s)
        else:
            impact(cl, a.ids)
    elif a.cmd == 'mapdraw':
        out = mapdraw(_claims_arg(a)[1], changed=a.impact, text=a.text, all_edges=a.all_edges)
        with open(a.o, 'w', encoding='utf8') as f:
            f.write(out)
        print('저장: %s' % a.o)
    elif a.cmd == 'mapreport':
        mapreport(load_claims(a.claims))
    elif a.cmd == 'suggest':
        meta_, cl_ = load_claims_full(a.claims)
        buf = io.StringIO()
        suggest(cl_, stream=buf, kind=meta_.get('kind'), min_shared=a.min_shared, min_caveat=a.min_caveat)
        print(buf.getvalue(), end='')
        if a.o:
            with open(a.o, 'w', encoding='utf8') as f:
                f.write('# 새 주장 후보 — %s\n\n> claim_graph.py v%s suggest. [참고]만 — 주장으로 적을 때는 `add --exploratory`(CLAIM_GRAPH §3-7). '
                        '주장 문장이 든 내용 회신이다.\n\n```\n%s```\n' % (meta_.get('doc') or meta_.get('deck') or os.path.basename(a.claims), __version__, buf.getvalue()))
            print('저장: %s' % a.o)
        sys.exit(0)
    elif a.cmd == 'scaffold':
        scaffold(load_claims(a.claims))
    elif a.cmd == 'mapdiff':
        ma, ca = load_claims_full(a.a)
        mb, cb = load_claims_full(a.b)
        pairs = parse_pairs(a.pairs) if a.pairs else None
        if pairs is None:                 # v16 (리뷰어 09-29 '같은 뜻'): 그래프에 적어 둔 짝 — a 쪽 먼저, 없으면 b 쪽을 뒤집어
            pairs = (ma.get('pairs_with') or {}).get(a.labels[1])
            if not pairs and (mb.get('pairs_with') or {}).get(a.labels[0]):
                pairs = {}
                for ib, ia in mb['pairs_with'][a.labels[0]].items():
                    for x in (ia if isinstance(ia, list) else [ia]):
                        pairs.setdefault(x, []).append(ib)
                pairs = {k: (v[0] if len(v) == 1 else v) for k, v in pairs.items()}
            if pairs:
                print('(그래프에 적힌 짝 %d개를 씀 — pairs_with)' % len(pairs))
        mapdiff(ca, cb, a.labels[0], a.labels[1], pairs=pairs)
        if a.save_pairs:
            if not a.pairs:
                print('[중단] --save-pairs 는 --pairs 와 함께'); sys.exit(2)
            ma.setdefault('pairs_with', {})[a.labels[1]] = parse_pairs(a.pairs)
            print('짝 저장: %s (pairs_with.%s)' % (save_claims(a.a, ca, meta=ma), a.labels[1]))
    elif a.cmd == 'remap-refs':
        import json
        if not a.refmap and not a.suppl:
            print('[중단] remap-refs 는 --map(본문 인용 [n]) 이나 --suppl(보충 S{n}) 중 하나 이상이 필요하다'); sys.exit(2)
        meta, cl = load_claims_full(a.claims)
        applied, tags = meta.get('refs_maps_applied', []), []
        for path, kind in ((a.refmap, None), (a.suppl, 'suppl')):   # v16.9: 보충 매핑은 kind='suppl' 로 따로 기록
            if not path:
                continue
            tag = {'map': norm_name(path), 'sha': _hash12(path)}
            if kind:
                tag['kind'] = kind
            if any(x.get('sha') == tag['sha'] and x.get('kind') == kind for x in applied) and not a.force:
                print('[중단] 이 매핑(%s, sha %s)은 이미 적용된 그래프입니다 — 두 번 적용하면 번호가 두 단계 밀립니다. 확실하면 --force' % (tag['map'], tag['sha']))
                sys.exit(2)
            tags.append(tag)
        remap_refs(cl, _refmap_load(a.refmap) if a.refmap else {}, suppl=_refmap_load(a.suppl) if a.suppl else None)
        meta['refs_maps_applied'] = applied + tags
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
            mapfreeze(src.resolve, cl, sources=a.sources, stream=sys.stdout)
            lit_ = meta.get('kind') in LIT_KINDS           # v16.19: 문헌 그래프의 doc 은 DOI — paper.md 이름으로 바꾸지 않는다
            print('기록 완료: %s' % save_claims(a.o, cl, meta=meta, doc=None if lit_ else a.doc))
        elif a.cmd == 'mapstale':
            meta, cl = load_claims_full(a.claims)
            stale_doc = meta.get('doc') or meta.get('deck')
            if stale_doc and doc_name(stale_doc) != doc_name(a.doc) and meta.get('kind') not in LIT_KINDS:
                print('[경고] 그래프의 doc=%s 와 대상 %s 가 다름 — 다른 판에 대한 freeze 일 수 있음' % (doc_name(stale_doc), doc_name(a.doc)))
            r = mapstale(src.resolve, cl, sources=a.sources)
            sys.exit(1 if (r['changed'] or r['unverified']) else 0)


if __name__ == '__main__':
    main()
