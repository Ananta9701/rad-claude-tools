#!/usr/bin/env python3
"""handoff.py — 영상의학 넘김 문서(`{YYMMDD}_전평대본_{덱}_v{N}.md`)의 문법 검사와 미리보기 (apply-handoff 1단계).

문법은 HANDOFF_FORMAT.md. 원칙: **문법에 없는 줄을 만나면 추측하지 않고 멈춘다** — 전에 덱 스크립트들이 넘김 형식의
변형을 알아서 받아 주다 대본 첫 줄을 빠뜨렸다(D2). 미리보기는 기준 덱과 대조해 판 착오(D11)를 적용 전에 잡는다.

    python3 handoff.py check 넘김.md                         # 문법만
    python3 handoff.py check 넘김.md --deck 기준.pptx          # + 기준 덱 대조(화면 수·제목·문단 키·본문 수정)
    python3 handoff.py check 넘김.md --deck 기준.pptx --sha 1a2b3c4d5e6f7a8b   # 넘김 문서 sha256 앞 16자도 대조

    python3 handoff.py apply 넘김.md --deck 기준.pptx -o 결과.pptx [--sha 16자] [--import 덱이름=경로 …] [--report 보고.md]
                                                             # 2단계(v1.2): check 오류 0 일 때만 적용 + 적용 보고서
"""
import hashlib
import os
import re
import sys

__version__ = '1.6'   # HANDOFF_FORMAT.md 첫 줄·test_handoff.EXPECT_VERSION 과 함께 올린다

KEYS = ('작업:', '대본:', '참고:', '본문:', '제목:', '복제본(문제) 대본:')
PARA_OP = re.compile(r'^문단 (교체|추가|삭제)\b')
SCREEN_H = re.compile(r'^### 화면 (\d+) — (.*)$')
NEW_H = re.compile(r'^### 새 슬라이드\b(.*)$')
L_LINE = re.compile(r'^L([0-3]) (.*)$')
TICKS = re.compile(r'`([^`]*)`')

# 작업어 — 닫힌 집합. ' · ' 로 여럿, ' — ' 뒤와 괄호 속은 설명.
OPS = [
    ('없음', re.compile(r'^없음$')),
    ('삭제', re.compile(r'^삭제$')),
    ('숨김 해제', re.compile(r'^숨김 해제$')),
    ('숨김', re.compile(r'^숨김$')),
    ('배경', re.compile(r'^배경 단색 #([0-9A-Fa-f]{6})$')),
    ('앞에 복제', re.compile(r'^앞에 복제\(정답 표시 제거\)$')),
    ('이동', re.compile(r'^이동 → (?:원본 )?화면 (\d+) 뒤$')),
    ('가져옴', re.compile(r'^가져옴: (.+?) 화면 (\d+) → (.+)$')),
    ('새 슬라이드', re.compile(r'^새 슬라이드\((?:[^)]*?)화면 (\d+)[^)]*\) → (.+)$')),
    ('메모 복사', re.compile(r'^메모 복사$')),
    ('비교 문항', re.compile(r'^비교 문항으로 남김')),
    ('재게시', re.compile(r'^재게시')),
    ('본문 수정', re.compile(r'^본문 수정$')),
    ('문단 작업', re.compile(r'^문단 (?:교체|추가|삭제)(?: \d+곳)?$')),
    ('본문 N문단', re.compile(r'^본문 \d+문단$')),
    ('레이아웃', re.compile(r'^레이아웃 = 화면 (\d+) ?(?:과|와) 같게$')),   # v1.4 (발표 N3): 새 슬라이드·가져옴의 레이아웃을 넘김이 정한다
    ('제목·본문 전체 교체', re.compile(r'^제목·본문 전체 교체$')),
]


def _split0(s, sep):
    """괄호 밖(깊이 0)에서만 sep 로 나눈다."""
    out, depth, cur, i = [], 0, '', 0
    while i < len(s):
        if s.startswith(sep, i) and depth == 0:
            out.append(cur); cur = ''; i += len(sep); continue
        ch = s[i]
        depth += ch == '('
        depth -= ch == ')' and depth > 0
        cur += ch; i += 1
    out.append(cur)
    return out


OP_PARENS = ('앞에 복제', '새 슬라이드')   # 괄호가 작업어의 일부인 것 — 나머지 괄호는 모두 설명


def _strip_comment(s):
    """설명 괄호를 뺀다: '없음 (문단 교체 2곳)' → '없음', '배경 단색 #D2F6F6(규약 §1.1)' → '배경 단색 #D2F6F6'.
    '앞에 복제(정답 표시 제거)'·'새 슬라이드(… 화면 N …)' 의 괄호는 작업어의 일부라 남긴다."""
    out, depth, keep = '', 0, True
    for ch in s:
        if ch == '(' and depth == 0:
            keep = out.rstrip().endswith(OP_PARENS)
        if ch == '(':
            depth += 1
        if keep or depth == 0 and ch != ')':
            out += ch
        if ch == ')' and depth:
            depth -= 1
            if depth == 0 and not keep:
                keep = True
    return re.sub(r'\s+', ' ', out).strip()


def _match_op(p):
    for name, pat in OPS:
        m = pat.match(p)
        if m:
            return (name, m.groups())
    return None


def parse_ops(text):
    """'작업:' 줄 값 → ([(작업어, 인자들)], 설명, [오류]). ' · ' 로 여럿, ' — ' 뒤는 설명(괄호 밖에서만 나눈다)."""
    errs, ops = [], []
    parts = _split0(text, ' — ')
    main, note = parts[0], ' — '.join(parts[1:])
    for part in [p.strip() for p in _split0(main, ' · ') if p.strip()]:
        p = _strip_comment(part)
        hit = _match_op(p)
        if not hit and '·' in p:   # '본문 수정·문단 교체' 처럼 붙여 쓴 것 — 조각이 모두 작업어면 받는다
            subs = [_match_op(x.strip()) for x in p.split('·')]
            if all(subs):
                ops.extend(subs); continue
        if not hit:
            m = re.search(r'앞에 복제\(정답 표시 제거\)', part)
            if m and '본문 수정' in part:
                ops.append(('본문 수정', ())); ops.append(('앞에 복제', ()))
                errs.append(('경고', '작업어를 문장으로 썼다 — "본문 수정 · 앞에 복제(정답 표시 제거)" 로 (본문 수정은 언제나 복제 전에 적용된다)'))
                continue
            errs.append(('오류', '모르는 작업어 "%s"' % part))
            continue
        ops.append(hit)
    return ops, note.strip(), errs


def _boxes(note):
    """'— 해설 상자 "Less common…", "Smoking…" 도 뺌' / '해설 상자 없음' → 목록 / [] / None(안 적음)."""
    if re.search(r'해설 상자 없음', note):
        return []
    q = re.findall(r'해설 상자[^"“]*[“"]([^"”]+)[”"]', note)
    if q:
        return re.findall(r'[“"]([^"”]+)[”"]', note[note.find('해설 상자'):])
    return None


def parse(text):
    """넘김 문서 → dict. 문법 오류는 멈추지 않고 모두 모은다(줄 번호와 함께). 적용은 오류 0 일 때만."""
    lines = text.split('\n')
    doc = {'base': None, 'screens_n': None, 'base_sha': None, 'range': None, 'screens': {}, 'new': [], 'fixes': [],
           'problems': []}
    P = doc['problems']

    def prob(kind, ln, msg):
        P.append((kind, ln, msg))

    # 머리 — '> 기준: **이름**(N화면)' (옛 문서는 '> 날짜: … · 기준: **…**(N화면 …' 안에)
    for i, l in enumerate(lines[:12], 1):
        if l.startswith('>'):
            m = re.search(r'기준: \*\*`?([^*`]+?)`?\*\*\s*\((\d+)화면', l)
            if m and not doc['base']:
                doc['base'], doc['screens_n'] = m.group(1).strip(), int(m.group(2))
            m = re.search(r'기준 sha256: `?([0-9a-f]{16})', l)
            if m:
                doc['base_sha'] = m.group(1)
            if '범위:' in l:     # v1.5 (발표 M2): 병합 넘김 — 연도 규칙이 기준 덱 이름보다 이것을 먼저
                m = re.search(r'범위:\s*`?(20\d\d\s*[-–]\s*20\d\d)`?', l)
                if m and _range_years(m.group(1)):
                    doc['range'] = re.sub(r'\s*[-–]\s*', '-', m.group(1))
                else:
                    prob('오류', i, '범위를 읽을 수 없다 — "> 범위: 2023-2025" 꼴')
    if not doc['base']:
        prob('오류', 1, '기준 덱이 없다 — 머리에 "> 기준: **{기준 덱}**(N화면)" 가 있어야 화면 번호를 맞출 수 있다')

    cur, zone, coll = None, 'prose', None   # coll = (대상 목록, 이름)
    pending_para = None

    def close():
        nonlocal cur, coll, pending_para
        if pending_para:
            prob('오류', pending_para['ln'], '문단 %s 뒤에 "본문:" 과 L 줄이 없다' % pending_para['kind'])
        if cur is not None:
            if isinstance(cur['tips'], list) and [t.strip() for t in cur['tips']] in (['- 없음'], ['없음'], ['· 없음']):
                cur['tips'] = 'NONE'          # v1.3 (발표 3-4): '참고:' 다음 '- 없음' 한 줄은 없음
            for op in cur['para']:
                if op['kind'] == '교체' and len(op.get('lines') or []) != 1 and op is not pending_para:
                    prob('오류', op['ln'], '문단 교체는 L 줄 하나 — 여러 줄이면 교체 하나 + 문단 추가로')
            if cur['ops'] is None:
                prob('오류', cur['ln'], '"작업:" 줄이 없다')
            if any('**' in t for v in (cur['script'], cur['tips'], cur['dup_script']) if isinstance(v, list) for t in v):
                prob('경고', cur['ln'], '대본·참고에 ** — 노트는 서식 없는 글이라 적용 때 ** 를 지운다(v1.6, 발표 R2)')
            if cur['script'] is None and not any(o[0] == '삭제' for o in (cur['ops'] or [])):
                prob('오류', cur['ln'], '"대본:" 이 없다 — 대본을 바꾸지 않으면 "대본: 변경 없음"')
            if cur['kind'] == 'screen' and cur['tips'] is None and not any(o[0] == '삭제' for o in (cur['ops'] or [])):
                prob('오류', cur['ln'], '"참고:" 가 없다 — 없으면 "참고: 없음", 그대로면 "참고: 변경 없음"')
            if cur['kind'] == 'new':
                imp = any(o[0] == '가져옴' for o in (cur['ops'] or []))
                if imp and bool(cur['title']) != bool(cur['body']):
                    prob('오류', cur['ln'], '가져옴 — "제목:"·"본문:" 을 둘 다 적으면 틀로 쓰고, 둘 다 없으면 그대로 가져온다(v1.5). 하나만은 안 된다')
                if not imp:
                    if not cur['title']:
                        prob('오류', cur['ln'], '새 슬라이드에 "제목:" 이 없다')
                    if not cur['body']:
                        prob('오류', cur['ln'], '새 슬라이드에 "본문:" 이 없다')
                    if any(o[0] == '메모 복사' for o in (cur['ops'] or [])):
                        prob('오류', cur['ln'], '메모 복사는 가져옴에서만 — 새 슬라이드(틀)에는 원작자 메모가 없다')
            if any(o[0] == '앞에 복제' for o in (cur['ops'] or [])):
                if cur['dup_script'] is None:
                    prob('오류', cur['ln'], '앞에 복제인데 "복제본(문제) 대본:" 이 없다')
                if cur['boxes'] is None:
                    prob('경고', cur['ln'], '앞에 복제 — 해설 상자를 뺄지 적지 않았다("해설 상자 \\"…\\"" 또는 "해설 상자 없음")')
        cur, coll, pending_para = None, None, None

    for i, raw in enumerate(lines, 1):
        l = raw.rstrip('\r')
        s = l.strip()
        m_scr, m_new = SCREEN_H.match(l), NEW_H.match(l)
        if m_scr or m_new:
            close()
            zone = 'screen'
            cur = {'kind': 'screen' if m_scr else 'new', 'ln': i, 'no': int(m_scr.group(1)) if m_scr else None,
                   'title_h': (m_scr.group(2) if m_scr else re.sub(r'^\s*[—–-]\s*', '', m_new.group(1))).strip(), 'ops': None, 'note': '',
                   'script': None, 'tips': None, 'dup_script': None, 'title': None, 'body': None,
                   'para': [], 'boxes': None}
            if m_scr:
                if cur['no'] in doc['screens']:
                    prob('오류', i, '화면 %d 이 두 번 나온다' % cur['no'])
                doc['screens'][cur['no']] = cur
            else:
                doc['new'].append(cur)
            continue
        if l.startswith('## ') or l.startswith('# '):
            close()
            zone = 'fixes' if l.startswith('## 본문 수정') else 'prose'
            continue
        if s == '---':
            close(); zone = 'prose'; continue
        if zone == 'fixes':
            if s.startswith('|') and not re.match(r'^\|\s*(화면|-)', s):
                c = [x.strip() for x in s.strip('|').split('|')]
                if len(c) >= 3 and c[0].isdigit():
                    old, new = TICKS.findall(c[1]), TICKS.findall(c[2])
                    if not old or not new:
                        prob('오류', i, '본문 수정 표: 원문·수정문은 `…` 로 감싼다')
                    elif not old[0]:
                        prob('오류', i, '본문 수정 표: 원문이 비었다')
                    else:
                        doc['fixes'].append({'ln': i, 'screen': int(c[0]), 'old': old[0], 'new': new[0], 'why': c[3] if len(c) > 3 else ''})
            continue
        if zone != 'screen' or cur is None:
            continue
        # --- 화면 구역 안 ---
        if l.startswith('작업:'):
            coll = None
            ops, note, errs = parse_ops(l[3:].strip())
            cur['ops'], cur['note'] = ops, note
            cur['boxes'] = _boxes(note)
            for k, msg in errs:
                prob(k, i, msg)
            continue
        if l.startswith('제목:'):
            coll = None; cur['title'] = l[3:].strip(); continue
        if l.startswith('복제본(문제) 대본:'):
            cur['dup_script'] = []; coll = (cur['dup_script'], '복제본 대본')
            rest = l[len('복제본(문제) 대본:'):].strip()
            if rest:
                prob('경고', i, '"복제본(문제) 대본:" 같은 줄에 글이 있다 — 첫 줄로 받는다. 다음 줄부터 쓰기를 권한다')
                cur['dup_script'].append(rest)
            continue
        if l.startswith('대본:'):
            rest = l[3:].strip()
            if re.match(r'^변경 없음\b', rest):
                cur['script'] = 'KEEP'; coll = None
            elif rest == '(삭제 화면)':
                cur['script'] = 'DELETED'; coll = None
            else:
                cur['script'] = []; coll = (cur['script'], '대본')
                if rest:   # D2: 같은 줄에 쓴 첫 줄을 버리지 않는다 — 받고 경고
                    prob('경고', i, '"대본:" 같은 줄에 글이 있다 — 첫 줄로 받는다. 다음 줄부터 쓰기를 권한다')
                    cur['script'].append(rest)
            continue
        if l.startswith('참고:'):
            rest = l[3:].strip()
            if rest == '없음':
                cur['tips'] = 'NONE'; coll = None
            elif re.match(r'^변경 없음\b', rest):
                cur['tips'] = 'KEEP'; coll = None
            else:
                cur['tips'] = []; coll = (cur['tips'], '참고')
                if rest:
                    prob('경고', i, '"참고:" 같은 줄에 글이 있다 — 첫 줄로 받는다')
                    cur['tips'].append(rest)
            continue
        mp = PARA_OP.match(l)
        if mp:
            coll = None
            kind = mp.group(1)
            keys = TICKS.findall(l)
            if kind == '삭제':
                if not keys:
                    prob('오류', i, '문단 삭제: 지울 문단 글을 `…` 로')
                cur['para'].append({'ln': i, 'kind': '삭제', 'keys': keys})
                continue
            op = {'ln': i, 'kind': kind, 'keys': keys, 'lines': [], 'raw': l}
            if kind == '교체' and not keys:
                prob('오류', i, '문단 교체: 바꿀 문단 글을 `…` 로')
            if kind == '추가':
                op['at_end'] = '맨 끝' in l or '끝(' in l
                op['after'] = keys[0] if keys and ('뒤' in l) else None
                if not op['at_end'] and not op['after']:
                    prob('오류', i, '문단 추가: 자리가 없다 — "본문 맨 끝" 또는 "`…` 문단 바로 뒤"')
            cur['para'].append(op)
            pending_para = op
            continue
        if l.startswith('본문:'):
            if pending_para is not None:
                coll = (pending_para['lines'], '문단 %s 본문' % pending_para['kind'])
                pending_para = None
            elif cur['kind'] == 'screen':
                # v1.3 (발표 3-1): 화면 구역의 떠 있는 '본문:' — 전에는 새 슬라이드 본문으로 받아 두고 적용에서 조용히 버렸다
                prob('오류', i, '"본문:" 이 문단 교체/추가에 딸리지 않았다 — "문단 추가 — 본문 맨 끝:" 같은 줄이 앞에 있어야 한다')
                coll = ([], '본문')
            else:
                cur['body'] = []
                coll = (cur['body'], '본문')
            continue
        if not s:
            continue
        if coll is not None:
            tgt, name = coll
            if '본문' in name:
                m = L_LINE.match(l)
                if not m:
                    prob('오류', i, '%s: "L0 …"/"L1 …"/"L2 …" 줄이 아니다' % name)
                    continue
                body = m.group(2)
                if body.count('**') % 2:
                    prob('오류', i, '굵게 표시 ** 가 짝이 안 맞는다')
                if body.count('{r:') != body.count('}') and body.count('{r:') > body.count('}'):
                    prob('오류', i, '빨강 표시 {r:…} 가 닫히지 않았다')
            tgt.append(l)
            continue
        prob('오류', i, '화면 %s 구역에 문법에 없는 줄 — 작업:/대본:/참고:/문단 …/본문: 중 어디에도 속하지 않는다: %s'
             % (cur['no'] if cur['no'] else '(새 슬라이드)', s[:60]))
    close()
    return doc


# ----------------------------------------------------------------------------
# 미리보기 — 기준 덱 대조
# ----------------------------------------------------------------------------

def _norm(t):
    return re.sub(r'[\s\u00a0·,.:;!?()\[\]{}"\'“”‘’`~\-–—/]+', '', (t or '')).casefold()


def _title_text(D, sn):
    x = open(D._slide(sn), encoding='utf8').read()
    m = re.search(r'<p:sp>(?:(?!</p:sp>).)*?<p:ph\b[^>]*type="(?:title|ctrTitle)".*?</p:sp>', x, re.S)
    if not m:
        return ''
    import html as _h
    return _h.unescape(' '.join(''.join(re.findall(r'<a:t>([^<]*)</a:t>', p)) for p in re.findall(r'<a:p>.*?</a:p>', m.group(0), re.S))).strip()


def check(doc, deck=None, doc_bytes=None, expect_sha=None, stream=sys.stdout):
    """문법 문제 + (deck 가 있으면) 기준 덱 대조 → 보고서. 반환: (오류 수, 경고 수)."""
    probs = list(doc['problems'])
    w = lambda s='': print(s, file=stream)
    if doc_bytes is not None and expect_sha:
        got = hashlib.sha256(doc_bytes).hexdigest()[:16]
        if got != expect_sha:
            probs.append(('오류', 0, '넘김 문서 sha256 %s ≠ 보낸 쪽이 적은 %s — 다른 판이다(D11)' % (got, expect_sha)))
    order = []
    plan = []
    if deck is not None:
        order = [s for s, _, _ in deck.order() if s]
        n = len(order)
        if doc['screens_n'] and n != doc['screens_n']:
            probs.append(('오류', 0, '기준 덱 화면 수 %d ≠ 넘김 머리 %d화면 — 기준 판이 다르다' % (n, doc['screens_n'])))
        if doc['base_sha'] and deck_path_sha(deck) and deck_path_sha(deck) != doc['base_sha']:
            ch = content_hash(deck.src_path)
            if ch == doc['base_sha']:   # v1.6 (발표 K1): 파일 sha 는 zip 안 시각·압축이 달라도 바뀐다 — 내용이 같으면 경고만
                probs.append(('경고', 0, '기준 덱 파일 sha256 %s ≠ 넘김의 %s 이지만 **내용 해시가 같다** — 같은 판의 다른 사본(다시 압축됨)' % (deck_path_sha(deck), doc['base_sha'])))
            else:
                probs.append(('오류', 0, '기준 덱 sha256 %s(내용 해시 %s) ≠ 넘김 머리의 기준 sha256 %s — 기준 판과 파일이 다르다. 다른 판이거나, '
                              '사용자가 고쳐 저장했는지 확인(열어 저장만 해도 바뀐다)' % (deck_path_sha(deck), ch, doc['base_sha'])))
        bad_titles = []
        for no, sc in sorted(doc['screens'].items()):
            if no < 1 or no > n:
                probs.append(('오류', sc['ln'], '화면 %d 은 기준 덱(%d화면)에 없다' % (no, n))); continue
            want = sc['title_h']
            got = _title_text(deck, order[no - 1])
            if want in ('(제목 없음)', ''):
                ok = not got.strip()
            else:
                a, b = _norm(want), _norm(got)
                ok = bool(a) and (a == b or a in b or b in a)
            if not ok:
                bad_titles.append((no, want, got))
            # 문단 키
            for op in sc['para']:
                for k in (op['keys'] if op['kind'] in ('교체', '삭제') else ([op['after']] if op.get('after') else [])):
                    c = _para_count(deck, order[no - 1], k)
                    if c != 1:
                        probs.append(('오류', op['ln'], '화면 %d 문단 %s 키 `%s` — 본문에서 %d번 찾음(정확히 1번이어야)' % (no, op['kind'], k[:40], c)))
        if bad_titles:
            for no, want, got in bad_titles[:8]:
                probs.append(('오류', doc['screens'][no]['ln'], '화면 %d 제목 불일치 — 넘김 "%s" / 덱 "%s"' % (no, want[:40], got[:40])))
            if len(bad_titles) > 8:
                probs.append(('오류', 0, '제목 불일치 %d곳 더 — 기준 판이 다를 가능성이 크다' % (len(bad_titles) - 8)))
        for fx in doc['fixes']:
            if fx['screen'] < 1 or fx['screen'] > n:
                probs.append(('오류', fx['ln'], '본문 수정: 화면 %d 없음' % fx['screen'])); continue
            r = deck.settext(order[fx['screen'] - 1], fx['old'], fx['new'], dry_run=True)
            if not r['ok']:
                r2 = deck.settext(order[fx['screen'] - 1], fx['old'], fx['new'], dry_run=True, whole=True)
                if r2['ok']:
                    probs.append(('경고', fx['ln'], '본문 수정 화면 %d `%s` — 부분 일치로는 여러 번, 조각 전체로는 1번(whole 로 적용)' % (fx['screen'], fx['old'][:30])))
                else:
                    probs.append(('오류', fx['ln'], '본문 수정 화면 %d `%s` — %s' % (fx['screen'], fx['old'][:30], r['reason'])))
        for nw in doc['new']:
            for name, args in nw['ops'] or []:
                if name in ('새 슬라이드', '레이아웃') and args and int(args[0]) > n:
                    probs.append(('오류', nw['ln'], '%s 화면 %s 없음' % ('새 슬라이드 틀' if name == '새 슬라이드' else '레이아웃 기준', args[0])))
    # 계획
    kinds = {}
    for no, sc in sorted(doc['screens'].items()):
        names = [o[0] for o in (sc['ops'] or []) if o[0] not in ('없음', '문단 작업', '본문 N문단')]
        if sc['para']:
            names.append('문단 ' + '·'.join(sorted({p['kind'] for p in sc['para']})) + ' %d' % len(sc['para']))
        memo_req = [t for t in (sc['tips'] if isinstance(sc['tips'], list) else []) if '[메모 수정 요청]' in t]
        if memo_req:   # v1.1 (발표 실물점검): 원작자 메모 수정은 기본 멈춤(요청서 3-4) — 미리보기에 드러낸다
            names.append('메모 수정 요청 %d' % len(memo_req))
        if names:
            plan.append((no, sc['title_h'][:40], ', '.join(names), sc['boxes']))
        for nm in names:
            kinds[nm.split()[0]] = kinds.get(nm.split()[0], 0) + 1
    notes = sum(1 for sc in doc['screens'].values() if isinstance(sc['script'], list) or isinstance(sc['tips'], list))
    errs = [p for p in probs if p[0] == '오류']; warns = [p for p in probs if p[0] == '경고']
    w('## 넘김 미리보기 (handoff.py v%s)' % __version__)
    w()
    w('| 항목 | 값 |'); w('|---|---|')
    w('| 기준 | %s (%s화면)%s |' % (doc['base'], doc['screens_n'], (' · 덱 %d화면' % len(order)) if deck is not None else ''))
    if doc.get('range'):
        w('| 번호 연도 범위 | %s (넘김 머리 — 기준 덱 이름보다 먼저) |' % doc['range'])
    w('| 화면 구역 | %d (새 슬라이드 %d) · 노트 바뀌는 화면 %d · 본문 수정 %d줄 |' % (len(doc['screens']), len(doc['new']), notes, len(doc['fixes'])))
    w('| 판정 | %s |' % ('**적용 가능**' if not errs else '**멈춤 — 오류 %d**' % len(errs)) + (' · 경고 %d' % len(warns) if warns else ''))
    if probs:
        w(); w('| 종류 | 줄 | 내용 |'); w('|---|---|---|')
        for k, ln, msg in sorted(probs, key=lambda p: (p[0] != '오류', p[1])):
            w('| %s | %s | %s |' % (k, ln or '—', msg.replace('|', '/')))
    if plan:
        w(); w('**화면별 작업** (노트만 바뀌는 화면은 빼고)'); w()
        w('| 화면 | 제목 | 작업 | 해설 상자 |'); w('|---|---|---|---|')
        for no, t, ops, boxes in plan:
            w('| %d | %s | %s | %s |' % (no, t.replace('|', '/'), ops, '—' if boxes is None else ('없음' if boxes == [] else ', '.join(boxes))))
    if doc['new']:
        def _kind(n):
            ops = dict((a, b) for a, b in (n['ops'] or []))
            if '가져옴' not in ops:
                return ''
            t = ' (가져옴 %s 화면 %s, %s%s%s)' % (ops['가져옴'][0], ops['가져옴'][1], '틀' if n['title'] else '그대로',
                                           ' · 메모 복사' if '메모 복사' in ops else '', ' · 앞에 복제' if '앞에 복제' in ops else '')
            return t
        w(); w('**새 슬라이드 %d장**: %s' % (len(doc['new']), ' / '.join((n['title'] or n['title_h']) + _kind(n) for n in doc['new'])))
    w(); w('적용 순서(2단계): 본문 수정 → 문단 교체·추가·삭제 → 배경·숨김 → 새 슬라이드·가져옴 → 앞에 복제(정답 표시 제거·해설 상자) → '
           '이동·삭제 → **원작자 메모 수정**(요청이 있고 사용자가 허락한 것만 — 노트를 쓰기 전에, D8) → 노트(대본·참고, 기존 메모 보존) → '
           '매핑표·검증 보고서')
    if doc['base_sha'] is None:
        w('기준 sha256 이 머리에 없다 — 노트만 다른 판(예: 한 판 앞 덱)은 화면 수·제목·문단 키로 구별되지 않는다. '
          '발표 적용 회신의 결과 sha256 을 다음 넘김 머리 `기준 sha256` 에 적으면 잡힌다')
    return len(errs), len(warns)


def content_hash(path):
    """v1.6 (발표 K1): pptx(zip) 안 파일 이름·내용만으로 낸 해시 앞 16자 — zip 항목 시각·압축 방식과 무관. 같은 판이면 같다."""
    import zipfile
    h = hashlib.sha256()
    with zipfile.ZipFile(path) as z:
        for n in sorted(z.namelist()):
            h.update(n.encode('utf8') + b'\0' + hashlib.sha256(z.read(n)).digest())
    return h.hexdigest()[:16]


def _normalize_zip(src, dst):
    """v1.6 (발표 K1): 항목 시각을 1980-01-01 로, 속성을 고정해 다시 쓴다 — 같은 입력·같은 기계면 같은 파일 sha."""
    import zipfile
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            zinfo = zipfile.ZipInfo(it.filename, date_time=(1980, 1, 1, 0, 0, 0))
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            zinfo.external_attr = 0o644 << 16
            zinfo.create_system = 3
            zo.writestr(zinfo, zi.read(it.filename))


VALIDATE_PY = '/mnt/skills/public/pptx/scripts/office/validate.py'   # deck_toolkit.validate 가 쓰는 것 — 없으면 건너뛴다


def _plain_note(lines):
    """v1.6 (발표 R2): 노트는 서식 없는 글 — 대본·참고의 ** 를 지운다."""
    return [l.replace('**', '') for l in lines] if isinstance(lines, list) else lines


def deck_path_sha(deck):
    p = getattr(deck, 'src_path', None)
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if p and os.path.exists(p) else None


def _para_count(deck, sn, key):
    """key 를 포함하는 본문 문단 수. 공백·탭은 하나로 본다. key 안의 '…' 는 '무엇이든'(긴 줄을 줄여 적은 것)."""
    import html as _h
    x = open(deck._slide(sn), encoding='utf8').read()
    k = re.sub(r'\s+', ' ', key.replace('⇥', ' ')).strip()
    if not k:
        return 0
    pat = re.compile('.*?'.join(re.escape(part.strip()) for part in k.split('…')))
    n = 0
    for p in re.findall(r'<a:p>.*?</a:p>', x, re.S):
        t = re.sub(r'\s+', ' ', _h.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>', p)))).strip()
        if pat.search(t):
            n += 1
    return n


# ----------------------------------------------------------------------------
# 2단계 — 적용 (v1.2)
# ----------------------------------------------------------------------------

def _resolve_key(deck, sn, key):
    """넘김의 문단 키(… 줄임 허용) → 그 문단의 실제 글(도구 함수에 넘길 정확한 키). 정확히 한 문단이어야."""
    import html as _h
    x = open(deck._slide(sn), encoding='utf8').read()
    k = re.sub(r'\s+', ' ', key.replace('⇥', ' ')).strip()
    pat = re.compile('.*?'.join(re.escape(part.strip()) for part in k.split('…')))
    hits = []
    for p in re.findall(r'<a:p>.*?</a:p>', x, re.S):
        raw = _h.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>', p)))
        if pat.search(re.sub(r'\s+', ' ', raw).strip()):
            hits.append(raw)
    if len(hits) != 1:
        raise ValueError('문단 키 `%s` — %d번 찾음' % (key[:40], len(hits)))
    return hits[0]


def _set_title_text(deck, sn, text):
    """제목 placeholder 의 글만 바꾼다 — 첫 문단의 pPr·첫 run 서식을 그대로 쓰고 나머지 문단은 뺀다."""
    p = deck._slide(sn); x = open(p, encoding='utf8').read()
    m = re.search(r'<p:sp>(?:(?!</p:sp>).)*?<p:ph\b[^>]*type="(?:title|ctrTitle)".*?</p:sp>', x, re.S)
    if not m:
        raise ValueError('제목 placeholder 없음: slide%d' % sn)
    sp = m.group(0)
    tb = re.search(r'(<p:txBody>.*?)(<a:p>.*</a:p>)(\s*</p:txBody>)', sp, re.S)
    first = re.search(r'<a:p>.*?</a:p>', tb.group(2), re.S).group(0)
    ppr = (re.search(r'<a:pPr\b[^>]*/>|<a:pPr\b[^>]*>.*?</a:pPr>', first, re.S) or [''])[0] if re.search(r'<a:pPr', first) else ''
    rpr = re.search(r'<a:rPr\b[^>]*/>|<a:rPr\b[^>]*>.*?</a:rPr>', first, re.S)
    endp = re.search(r'<a:endParaRPr\b[^>]*/>|<a:endParaRPr\b[^>]*>.*?</a:endParaRPr>', first, re.S)
    import html as _h
    para = '<a:p>%s<a:r>%s<a:t>%s</a:t></a:r>%s</a:p>' % (ppr, rpr.group(0) if rpr else '<a:rPr lang="ko-KR"/>',
                                                         _h.escape(text, quote=False), endp.group(0) if endp else '')
    new_sp = sp[:tb.start(2)] + para + sp[tb.end(2):]
    open(p, 'w', encoding='utf8').write(x[:m.start()] + new_sp + x[m.end():])


def _delete_box(deck, sn, words):
    """복제본에서 해설 상자 — 글이 words 로 시작(또는 포함)하는 도형 하나를 이름으로 지운다."""
    import html as _h
    x = open(deck._slide(sn), encoding='utf8').read()
    cands = []
    for m in re.finditer(r'<p:sp>(?:(?!<p:sp>).)*?</p:sp>', x, re.S):
        if '<p:ph ' in m.group(0) and 'type="title"' in m.group(0):
            continue
        t = re.sub(r'\s+', ' ', _h.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>', m.group(0))))).strip()
        w = re.sub(r'\s+', ' ', words.rstrip('…').strip())
        if w and w in t:
            nm = re.search(r'<p:cNvPr\b[^>]*\bname="([^"]*)"', m.group(0))
            cands.append(_h.unescape(nm.group(1)) if nm else None)
    if len(cands) != 1 or not cands[0]:
        raise ValueError('해설 상자 "%s" — 후보 %d개' % (words[:30], len(cands)))
    return deck.delete_shape(sn, cands[0], must_contain=re.sub(r'\s+', ' ', words.rstrip('…').strip()).split(' ')[0])


def _pos_after(deck, text, F, last_new):
    """'화면 M 앞' / '화면 M 뒤' / '바로 앞 새 슬라이드 뒤' / 'T1 뒤' → after(파일 번호)."""
    if '바로 앞 새 슬라이드 뒤' in text or re.search(r'\bT\d+ 뒤', text):
        if last_new is None:
            raise ValueError('"%s" — 앞 새 슬라이드가 없다' % text)
        return last_new
    m = re.search(r'화면 (\d+) (앞|뒤)', text)
    if not m:
        raise ValueError('자리를 읽을 수 없다: "%s"' % text)
    n = int(m.group(1))
    if m.group(2) == '뒤':
        return F[n - 1]
    order = [s for s, _, _ in deck.order() if s]
    i = order.index(F[n - 1])
    if i == 0:
        raise ValueError('화면 1 앞에는 넣을 수 없다(표지)')
    return order[i - 1]


_NUM = re.compile(r'(\[짤\])?\b(\d\d)-(\d\d|\?)\b\*?†?')


def _range_years(*names):
    """덱 이름의 '2023-2025' → {'23','24','25'}. 못 읽으면 None."""
    for nm in names:
        m = re.search(r'(20\d\d)\s*[-–_]+\s*(20\d\d)', nm or '')
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if 0 <= b - a <= 20:
                return {'%02d' % (y % 100) for y in range(a, b + 1)}
    return None


def _dominant_num_style(deck, years):
    """덱에서 이번 범위 번호가 가장 많이 쓰는 서식 (굵게, 빨강) — 결정 2(사용자 09-27).
    v1.6 (발표 Y1): **출제줄(⇥ 로 시작하는 문단)** 만 센다 — 덱 전체를 세면 문제 화면 제목 'Q. … (25-11)' 의 보통 글자가 다수라
    교육목표 출제줄의 빨강이 지워졌다. 출제줄 표본이 3개 미만이면 덱 전체로. 반환: (서식 또는 None, 표본 수, '출제줄'|'덱 전체')."""
    import html as _h
    from collections import Counter
    tab, alls = Counter(), Counter()
    for sn in deck.slide_numbers():
        x = open(deck._slide(sn), encoding='utf8').read()
        for pm in re.finditer(r'<a:p>.*?</a:p>', x, re.S):
            is_tab = _ptext(pm.group(0)).startswith('\t')
            for rm in re.finditer(r'<a:r>(.*?)</a:r>', pm.group(0), re.S):
                t = _h.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>', rm.group(1))))
                if any(m.group(2) in years for m in _NUM.finditer(t)):
                    rp = re.search(r'<a:rPr\b[^>]*/>|<a:rPr\b[^>]*>.*?</a:rPr>', rm.group(1), re.S)
                    rp = rp.group(0) if rp else ''
                    k = (bool(re.search(r'\bb="1"', rp)), bool(re.search(r'srgbClr val="(?:FF0000|C00000|E00000|FF3333|EE0000)"', rp)))
                    alls[k] += 1
                    if is_tab:
                        tab[k] += 1
    c, scope = (tab, '출제줄') if sum(tab.values()) >= 3 else (alls, '덱 전체')
    return (c.most_common(1)[0][0] if c else None), sum(c.values()), scope


def _apply_year_rule(line, years, style):
    """표기의 보통 조각에 있는 기출 번호: 범위 안 → 덱의 강조 서식, 범위 밖 → 그대로(보통). {r:}·** 안은 표기 우선."""
    if not years or style is None:
        return line
    lv, body = line[:3], line[3:]
    out = []
    for tok in re.split(r'(\*\*.+?\*\*|\{r:.+?\})', body):
        if not tok or tok.startswith('**') or tok.startswith('{r:'):
            out.append(tok); continue
        def wrap(m):
            if m.group(2) not in years:
                return m.group(0)
            t = m.group(0); b, r = style
            if r:
                t = '{r:%s}' % t
            if b:
                t = '**%s**' % t
            return t
        out.append(_NUM.sub(wrap, tok))
    return lv + ''.join(out)


def _years_for(doc, base_path):
    """v1.5 (발표 M2): 넘김 머리 '범위:' → 기준 덱 파일 이름 → 머리 '기준:' 이름. 반환 (연도 집합, 'head'|'name'|None)."""
    if doc.get('range'):
        return _range_years(doc['range']), 'head'
    y = _range_years(os.path.basename(base_path or ''), doc.get('base'))
    return y, ('name' if y else None)


def _adopt_layout_sizes(T, D, s):
    """v1.5 (발표 M1): 슬라이드 s 의 자리 표시자(제목·본문) run 에서 명시 글자 크기(sz)를 지워 레이아웃 크기를 따르게.
    반환: ['본문 16pt → 20pt', …] — 보고서가 넘침 점검 대상을 고르게."""
    x = open(D._slide(s), encoding='utf8').read()
    t_sz, b_sz = T._layout_default_sizes(D, D.layout_of(s))
    found = {'제목': set(), '본문': set()}

    def fix(m):
        seg = m.group(0)
        ph = re.search(r'<p:ph\b([^>]*)/?>', seg)
        if not ph or re.search(r'type="(?:dt|ftr|sldNum|pic|chart|tbl|media|clipArt|sldImg)"', ph.group(1)):
            return seg
        kind = '제목' if re.search(r'type="(?:title|ctrTitle)"', ph.group(1)) else '본문'
        tx = re.search(r'<p:txBody>.*?</p:txBody>', seg, re.S)
        if not tx:
            return seg
        found[kind] |= {int(v) for v in re.findall(r'<a:(?:rPr|endParaRPr)\b[^>]*?\bsz="(\d+)"', tx.group(0))}
        body = re.sub(r'(<a:(?:rPr|endParaRPr)\b[^>]*?)\s+sz="\d+"', r'\1', tx.group(0))
        return seg[:tx.start()] + body + seg[tx.end():]
    open(D._slide(s), 'w', encoding='utf8').write(re.sub(r'<p:sp>(?:(?!</p:sp>).)*</p:sp>', fix, x, flags=re.S))
    return ['%s %s → %s' % (k, '·'.join('%gpt' % (v / 100.0) for v in sorted(found[k])), ('%gpt' % (now / 100.0)) if now else '레이아웃 기본값')
            for k, now in (('제목', t_sz), ('본문', b_sz)) if found[k]]


def _slide_paras(deck, sn):
    x = open(deck._slide(sn), encoding='utf8').read()
    return x, [(m.start(), m.end()) for m in re.finditer(r'<a:p>.*?</a:p>', x, re.S)]


def _ptext(xml):
    import html as _h
    return _h.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>', xml)))


def _key_index(deck, sn, key):
    """문단 키 → 슬라이드 안 문단 번호(0부터). 정확히 한 문단이어야."""
    x, spans = _slide_paras(deck, sn)
    k = re.sub(r'\s+', ' ', key.replace('⇥', ' ')).strip()
    pat = re.compile('.*?'.join(re.escape(part.strip()) for part in k.split('…')))
    hits = [i for i, (a, b) in enumerate(spans) if pat.search(re.sub(r'\s+', ' ', _ptext(x[a:b])).strip())]
    if len(hits) != 1:
        raise ValueError('문단 키 `%s` — %d번 찾음' % (key[:40], len(hits)))
    return hits[0]


def _body_levels(deck, sn):
    """본문 placeholder 의 (수준, 탭 여부) 집합."""
    try:
        _, d, a, e = deck._body_span(sn)
    except Exception:
        return set()
    out = set()
    for p in re.findall(r'<a:p>.*?</a:p>', d[a:e], re.S):
        if _ptext(p).strip():
            out.add((int((re.search(r'<a:pPr\b[^>]*\blvl="(\d)"', p) or [0, 0])[1]), _ptext(p).startswith('\t')))
    return out


def _tips_bullets(tips):
    """결정 1(사용자 09-27): 참고 줄 글머리 '- ' → '· '."""
    return [('· ' + t[2:]) if t.startswith('- ') else t for t in tips]


def apply(doc, base_path, out_path, imports=None, stream=sys.stdout, workdir=None):
    """check 오류 0 인 넘김을 기준 덱에 적용해 out_path 에 저장. 반환: 보고 dict. 순서는 check 의 '적용 순서'.
    원작자 메모 수정 요청은 적용하지 않고 보고서에 남긴다(요청서 3-4 — 사용자 허락 뒤 settext(notes=True, zone='memo'))."""
    import tempfile, shutil
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import deck_toolkit as T
    imports = imports or {}
    wd = workdir or tempfile.mkdtemp(prefix='ho_')
    D = T.Deck.open(base_path, os.path.join(wd, 'd'))
    F = [s for s, _, _ in D.order() if s]           # 기준 화면 → 파일 번호(넣고 빼도 변하지 않는다)
    rep = {'warn': [], 'done': [], 'memo_req': [], 'new': [], 'dup': [], 'deleted': [], 'imports': [], 'dup_new': []}
    W = rep['warn'].append; DONE = rep['done'].append
    # 0. 문단 키를 먼저 문단 번호로 풀어 둔다 — 본문 수정이 키 글을 바꿔도(물리 v1 '23-23' → '[짤]23-23') 같은 문단을 찾는다(v1.3, 발표 3-2)
    plan = {}
    for no, sc in sorted(doc['screens'].items()):
        sn = F[no - 1]
        for op in sc['para']:
            if op['kind'] == '교체':
                plan.setdefault(sn, []).append(('교체', _key_index(D, sn, op['keys'][0]), op['lines'][0], no))
            elif op['kind'] == '삭제':
                for k in op['keys']:
                    plan.setdefault(sn, []).append(('삭제', _key_index(D, sn, k), None, no))
            elif op['kind'] == '추가':
                i = _key_index(D, sn, op['after']) if op.get('after') else None
                for j, line in enumerate(op['lines']):
                    plan.setdefault(sn, []).append(('추가', i, line, no, j))
    years, ysrc = _years_for(doc, base_path)
    style, ns, scope = _dominant_num_style(D, years) if years else (None, 0, '')
    if plan and years and (style is None or (scope == '덱 전체' and style == (False, False))):
        W('번호 연도 규칙 — 범위 안 번호의 강조를 정하지 못했다(출제줄 표본 부족 · %s %d개 · 결과 %s) — 강조가 필요한 번호는 넘김에 {r:}·** 로 적는다'
          % (scope, ns, '없음' if style is None else '보통'))
    if plan and not years:
        W('번호 연도 규칙 — 기준 덱 이름에서 범위 연도를 읽지 못해 쓰지 않았다(넘김 표기대로). 병합 넘김이면 머리에 "> 범위: 2023-2025"')
    elif plan and ysrc == 'head':
        DONE('연도 범위 %s(넘김 머리)' % doc['range'])
    # 1. 본문 수정 (문단 수는 바뀌지 않는다)
    for fx in doc['fixes']:
        sn = F[fx['screen'] - 1]
        r = D.settext(sn, fx['old'], fx['new'])
        if not r['ok']:
            D.settext(sn, fx['old'], fx['new'], whole=True, strict=True)
            W('본문 수정 화면 %d `%s` — 조각 전체로 적용' % (fx['screen'], fx['old'][:30]))
    if doc['fixes']:
        DONE('본문 수정 %d' % len(doc['fixes']))
    # 2. 문단 교체·삭제·추가 — 슬라이드마다 뒤 문단부터(앞 문단 번호가 밀리지 않게)
    npara = 0
    for sn, ops in plan.items():
        def _ok(o):
            j = o[4] if len(o) > 4 else 0
            return (-(o[1] if o[1] is not None else 10 ** 6), {'추가': 0, '교체': 1, '삭제': 2}[o[0]], j if o[1] is None else -j)
        for op in sorted(ops, key=_ok):
            x, spans = _slide_paras(D, sn)
            kind, idx, line, no = op[0], op[1], op[2], op[3]
            if kind == '교체':
                a, b = spans[idx]; para = x[a:b]
                cur = D._para_notation(para)
                only_nums = lambda seg: bool(years) and bool(_NUM.search(seg)) and not _NUM.sub('', seg).strip(' ,')
                merged = T._merge_format(cur, line, skip_bold=only_nums)
                ruled = _apply_year_rule(merged, years, style)
                if merged != line:
                    W('화면 %d 문단 교체 — 넘김 줄에 빠진 서식(탭·앞 공백·굵게)을 원래 문단에서 살림: `%s`' % (no, line[:50]))
                was_bold = set(m.group(0) for m in re.finditer(r'\*\*(.+?)\*\*', cur) for m in _NUM.finditer(m.group(1)))
                now_bold = set(m.group(0) for m in re.finditer(r'\*\*(.+?)\*\*', ruled) for m in _NUM.finditer(m.group(1)))
                lost = sorted(was_bold - now_bold)
                if lost or ruled != merged:
                    W('화면 %d 번호 서식을 연도 규칙으로 정함%s' % (no, (' — 원래 굵게였음(%s)' % ', '.join(lost)) if lost else ''))
                open(D._slide(sn), 'w', encoding='utf8').write(x[:a] + T._para_like(para, ruled) + x[b:])
            elif kind == '삭제':
                a, b = spans[idx]
                open(D._slide(sn), 'w', encoding='utf8').write(x[:a] + x[b:])
            else:   # 추가 — 틀: 같은 탭 여부·같은 수준의 가장 가까운 문단(앞쪽 우선), 자리: idx 문단 뒤 또는 본문 끝
                _, bd, ba, be = D._body_span(sn)
                in_body = [k for k, (a, b) in enumerate(spans) if ba <= a and b <= be]
                pos_k = idx if idx is not None else (in_body[-1] if in_body else len(spans) - 1)
                want = T.parse_body_notation([line])[0]
                cand = in_body or list(range(len(spans)))
                order_k = sorted(cand, key=lambda k: (k > pos_k, abs(k - pos_k)))
                tab = lambda k: _ptext(x[spans[k][0]:spans[k][1]]).startswith('\t')
                lv = lambda k: int((re.search(r'<a:pPr\b[^>]*\blvl="(\d)"', x[spans[k][0]:spans[k][1]]) or [0, 0])[1])
                pick = [k for k in order_k if _ptext(x[spans[k][0]:spans[k][1]]).strip() and tab(k) == want['tab'] and lv(k) == want['lvl']] or \
                       [k for k in order_k if _ptext(x[spans[k][0]:spans[k][1]]).strip() and tab(k) == want['tab']] or order_k
                tpl = x[spans[pick[0]][0]:spans[pick[0]][1]]
                at = spans[pos_k][1]
                open(D._slide(sn), 'w', encoding='utf8').write(x[:at] + T._para_like(tpl, line) + x[at:])
            npara += 1
    if npara:
        DONE('문단 작업 %d' % npara)
    # 3. 배경·숨김
    for no, sc in sorted(doc['screens'].items()):
        for name, args in sc['ops'] or []:
            if name == '배경':
                D.set_background(F[no - 1], rgb=args[0].upper())
            elif name == '숨김':
                D.set_hidden(F[no - 1], True)
            elif name == '숨김 해제':
                D.set_hidden(F[no - 1], False)
            elif name in ('메모 복사',):
                W('화면 %d 메모 복사 — 자동 적용 안 함(copy_note_paragraphs 로 손으로)' % no)
            elif name == '재게시':
                raise ValueError('화면 %d 재게시 — 2단계에서 지원하지 않는다' % no)
    # 복제·새 슬라이드의 원천: 본문 수정·문단 작업이 끝난 덱(D10)
    mid = os.path.join(wd, 'mid.pptx'); D.save(mid)
    S = T.Deck.open(mid, os.path.join(wd, 's'))
    SF = [s for s, _, _ in S.order() if s]
    # 4. 새 슬라이드 · 가져옴
    last_new = None
    anchor_last = {}     # v1.5 (발표 M4): 같은 자리 뒤로 여러 장 — 적은 순서대로(하나씩 같은 자리에 넣으면 거꾸로 된다)
    for nw in doc['new']:
        ops = dict((n, a) for n, a in (nw['ops'] or []))
        imp, as_is, src_label = '가져옴' in ops, False, None
        if '새 슬라이드' in ops:
            tpl, where = int(ops['새 슬라이드'][0]), ops['새 슬라이드'][1]
            src, src_sn = S, SF[tpl - 1]
        elif imp:
            name, k, where = ops['가져옴']
            if name not in imports:
                raise ValueError('가져옴 "%s" — --import "%s=경로" 가 필요하다' % (name, name))
            src = T.Deck.open(imports[name], os.path.join(wd, 'imp_%d' % len(rep['new'])))
            src_sn = [s for s, _, _ in src.order() if s][int(k) - 1]
            as_is = not nw['title'] and not nw['body']       # v1.5: 제목·본문이 없으면 그대로(그림·글상자·글) 가져온다
            src_label = '%s 화면 %s' % (name, k)
        else:
            raise ValueError('새 슬라이드 "%s" — 틀(새 슬라이드(…화면 N…) 또는 가져옴)이 없다' % (nw['title'] or nw['title_h']))
        label = nw['title'] or re.sub(r'^[—–-]\s*', '', nw['title_h'] or '').strip() or src_label
        base_after = _pos_after(D, where, F, last_new)
        chained = '바로 앞 새 슬라이드 뒤' in where or re.search(r'\bT\d+ 뒤', where)
        after = base_after if chained else anchor_last.get(base_after, base_after)
        lay = None
        if '레이아웃' in ops:
            lay = D.layout_of(F[int(ops['레이아웃'][0]) - 1])
        elif '배경' in ops:   # v1.3 (발표 3-6): 같은 배경(교육목표 #D2F6F6 등) 슬라이드가 이미 있으면 그 레이아웃으로 — D4 재발 방지
            from collections import Counter
            same_bg = Counter(D.layout_of(x) for x in D.slide_numbers()
                              if re.search(r'<p:bg>.*?%s.*?</p:bg>' % ops['배경'][0], open(D._slide(x), encoding='utf8').read(), re.S | re.I))
            lay = same_bg.most_common(1)[0][0] if same_bg else None
        memo_copy = imp and '메모 복사' in ops
        s = D.import_slide(src, src_sn, after=after, pictures=as_is, layout=lay, copy_notes=memo_copy)
        anchor_last[base_after] = s
        if lay:
            DONE('새 슬라이드 레이아웃 %s(%s)' % (lay, '넘김 지정' if '레이아웃' in ops else '같은 배경 슬라이드를 따름')) if not any('레이아웃' in d for d in rep['done']) else None
        elif imp:   # v1.4 (발표 N3): 첫 가져옴은 근거 없이 마스터를 고르게 된다 — 알리고 넘김이 정하게
            W('"%s" 을 다른 덱에서 가져와 레이아웃 %s 에 붙였다 — 같은 배경 슬라이드가 없어 도구가 골랐다. 원하는 레이아웃이 있으면 넘김 작업에 '
              '"레이아웃 = 화면 N 과 같게"' % (label, D.layout_of(s)))
        sizes = []
        if imp and '레이아웃' in ops:
            # v1.5 (발표 M1 = N4): 가져온 슬라이드는 기준 덱 모양으로 — 자리 표시자(제목·본문) 글자 크기는 목적지 레이아웃을 따른다.
            # 그림·화살표·따로 그린 글상자는 원래 위치·크기 그대로. 제목은 기준 화면 제목 규격(titles --like)으로
            sizes = _adopt_layout_sizes(T, D, s)
            ref = int(ops['레이아웃'][0])
            try:
                prof = T.title_profile(D, like=[x for x, _, _ in D.order() if x].index(F[ref - 1]) + 1)
            except Exception:
                prof = None
            for c in (T.conform_title(D, s, prof) if prof else []):
                (W if c.startswith('[!]') else sizes.append)(('가져옴 "%s" 제목 규격: %s' % (label, c)) if c.startswith('[!]') else '제목 규격: ' + c)
        if not as_is:
            # v1.4 (발표 N1): 본문 틀 — 틀 슬라이드에 없는 수준(예: L2)이 있으면 같은 레이아웃·같은 배경의 다른 슬라이드 중 모든 수준을 가진 것을
            need = {(q['lvl'], q['tab']) for q in T.parse_body_notation(nw['body'])}
            tsrc = (D, s)
            if not need <= _body_levels(D, s):
                bgc = ops['배경'][0] if '배경' in ops else None
                cands = [x for x in D.slide_numbers() if x != s and D.layout_of(x) == D.layout_of(s) and
                         (not bgc or re.search(r'<p:bg>.*?%s.*?</p:bg>' % bgc, open(D._slide(x), encoding='utf8').read(), re.S | re.I))]
                full = [x for x in cands if need <= _body_levels(D, x)]
                if full:
                    tsrc = (D, full[0])
                else:
                    miss = sorted(need - _body_levels(D, s))
                    W('새 슬라이드 "%s" — 틀에 없는 수준 %s 은 가장 가까운 수준의 서식을 썼다(같은 틀 묶음에도 없음) — 들여쓰기·글자 크기를 확인' % (nw['title'], ', '.join('L%d%s' % (l, '탭' if t else '') for l, t in miss)))
            _set_title_text(D, s, nw['title'])
            D.set_body_like(s, nw['body'], template=None if tsrc == (D, s) else tsrc)
        if '배경' in ops:
            D.set_background(s, rgb=ops['배경'][0].upper())
        # 노트 — v1.5 (발표 M3): 가져옴의 '메모 복사' 는 원천 노트를 결과 노트의 '기존 메모' 구역으로. 원천 노트가 표지 없는 노트(원작자
        # 노트 그대로)면 전체가 메모, 이미 3부 구조면 그 메모 구역만. 메모 복사가 없으면 원작자 노트는 들어오지 않는다(새 노트)
        memo_n = 0
        if imp:
            raw = src.notes(src_sn)
            sectioned = any(T._is_memo_sep(l) or T._is_cutoff_line(l) for l in raw)
            ss, st, sm = src.notes_sections(src_sn)
            script = _plain_note(nw['script']) if isinstance(nw['script'], list) else (ss if sectioned else [])
            if nw['script'] == 'KEEP' and not sectioned and any(l.strip() for l in raw):
                W('가져옴 "%s" — 원천 노트에 대본 구역이 없어 대본을 비웠다(원천 노트는 %s)' % (label, '기존 메모로 옮겼다' if memo_copy else '가져오지 않았다 — 필요하면 "메모 복사"'))
            tips = _tips_bullets(_plain_note(nw['tips'])) if isinstance(nw['tips'], list) else (st if (nw['tips'] == 'KEEP' and sectioned) else None)
            if memo_copy:
                if not sectioned:
                    D.protect_memo(s)
                    memo_n = sum(1 for l in raw if l.strip())
                else:
                    memo_n = len(sm)
                    if not sm:
                        W('가져옴 "%s" — 메모 복사: 원천 노트에 기존 메모 구역이 없다(원천이 이미 대본 노트) — 복사한 메모 없음' % label)
            D.set_notes(s, script, tips or None)
        else:
            D.set_notes(s, _plain_note(nw['script']) if isinstance(nw['script'], list) else [], _tips_bullets(_plain_note(nw['tips'])) if isinstance(nw['tips'], list) else None)
        rep['new'].append((label, s)); last_new = s
        if imp:
            rep['imports'].append((label, src_label, s, '그대로' if as_is else '틀', memo_n, sizes))
        # v1.5 (발표 M3-③): 새 슬라이드·가져옴에도 '앞에 복제' — 원천은 방금 만든 슬라이드, 메모는 같이 복제된다
        if any(n == '앞에 복제' for n, _ in (nw['ops'] or [])):
            order = [x for x, _, _ in D.order() if x]
            d2 = D.import_slide(D, s, after=order[order.index(s) - 1], pictures=True, copy_notes=True)
            k2 = D.strip_color(d2, 'FF0000')
            for box in nw['boxes'] or []:
                _delete_box(D, d2, box)
            D.set_notes(d2, _plain_note(nw['dup_script'] or []), None)
            rep['dup_new'].append((label, d2, k2, len(nw['boxes'] or [])))
    if rep['new']:
        DONE('새 슬라이드 %d%s' % (len(rep['new']), (' (가져옴 %d)' % len(rep['imports'])) if rep['imports'] else ''))
    # 5. 앞에 복제(정답 표시 제거)
    for no, sc in sorted(doc['screens'].items()):
        if not any(n == '앞에 복제' for n, _ in (sc['ops'] or [])):
            continue
        order = [s for s, _, _ in D.order() if s]
        i = order.index(F[no - 1])
        s = D.import_slide(S, SF[no - 1], after=order[i - 1] if i else F[no - 1], pictures=True, copy_notes=True)
        if i == 0:
            D.move_slide(s, after_pos=0)
        k = D.strip_color(s, 'FF0000')
        for box in sc['boxes'] or []:
            _delete_box(D, s, box)
        D.set_notes(s, _plain_note(sc['dup_script'] or []), None)
        rep['dup'].append((no, s, k, len(sc['boxes'] or [])))
    if rep['dup']:
        DONE('앞에 복제 %d' % len(rep['dup']))
    # 6. 이동 — 같은 자리 뒤로 가는 화면들은 원래 순서를 지킨다(v1.4, 발표 N2: 하나씩 같은 자리에 넣어 거꾸로 됐다)
    moves = {}
    for no, sc in sorted(doc['screens'].items()):
        for name, args in sc['ops'] or []:
            if name == '이동':
                moves.setdefault(int(args[0]), []).append(no)
    for tgt, nos in moves.items():
        after = F[tgt - 1]
        for no in sorted(nos):
            D.move_slide(F[no - 1], after=after)
            after = F[no - 1]
        DONE('이동 화면 %s → 화면 %d 뒤' % (','.join(map(str, sorted(nos))), tgt))
    # 7. 원작자 메모 수정 요청 — 적용하지 않고 남긴다
    for no, sc in sorted(doc['screens'].items()):
        for t in (sc['tips'] if isinstance(sc['tips'], list) else []):
            if '[메모 수정 요청]' in t:
                rep['memo_req'].append((no, t.strip()))
    # 8. 노트
    nn, plain_notes = 0, []
    for no, sc in sorted(doc['screens'].items()):
        if any(n == '삭제' for n, _ in (sc['ops'] or [])):
            continue
        if not (isinstance(sc['script'], list) or isinstance(sc['tips'], list) or sc['tips'] == 'NONE'):
            continue
        sn = F[no - 1]
        cur_s, cur_t, _ = D.notes_sections(sn)
        if isinstance(sc['script'], list) and cur_s and not cur_t and not D.notes_sections(sn)[2] and \
                not any(T._is_memo_sep(l) or T._is_cutoff_line(l) for l in D.notes(sn)):
            plain_notes.append(no)
        script = _plain_note(sc['script']) if isinstance(sc['script'], list) else cur_s
        tips = _tips_bullets(_plain_note(sc['tips'])) if isinstance(sc['tips'], list) else (None if sc['tips'] == 'NONE' else (cur_t or None))
        D.set_notes(sn, script, tips); nn += 1
    if nn:
        DONE('노트 %d화면' % nn)
    if plain_notes:   # v1.3 (발표 3-7): 화면마다가 아니라 한 줄로
        W('표지 없는 노트(대본만 있던 노트) %d화면을 대본으로 보고 바꿨다 — 기준 덱이 restore-memo·normalize-notes 된 판이면 정상: 화면 %s'
          % (len(plain_notes), ', '.join(map(str, plain_notes[:12])) + (' …' if len(plain_notes) > 12 else '')))
    # 9. 삭제
    for no, sc in sorted(doc['screens'].items()):
        if any(n == '삭제' for n, _ in (sc['ops'] or [])):
            D.remove_slide(F[no - 1]); rep['deleted'].append(no)
    if rep['deleted']:
        D.purge_orphans(); DONE('삭제 %d' % len(rep['deleted']))
    # v1.6 (발표 K2): 동기화 폴더에서 zip 임시 파일 이름 바꾸기가 막혔다 — 임시 폴더에 만들고 마지막에 한 번 복사.
    # (K1) zip 항목 시각을 고정해 같은 입력이면 같은 파일 sha
    raw = os.path.join(wd, 'out_raw.pptx'); fixed = os.path.join(wd, 'out_fixed.pptx')
    D.save(raw); _normalize_zip(raw, fixed); shutil.copyfile(fixed, out_path)
    # 보고: 매핑·메모 보존·검증
    R = T.Deck.open(out_path, os.path.join(wd, 'r'))
    ro = [s for s, _, _ in R.order() if s]
    B = T.Deck.open(base_path, os.path.join(wd, 'b'))
    mapping, memo_ok, memo_bad = {}, 0, []
    for no, sn in enumerate(F, 1):
        if sn in ro:
            mapping[no] = ro.index(sn) + 1
            if B.notes_sections(sn)[2] == R.notes_sections(sn)[2]:
                memo_ok += 1
            else:
                memo_bad.append(no)
    rep.update({'mapping': mapping, 'memo_ok': memo_ok, 'memo_bad': memo_bad, 'screens': len(ro),
                'valid': (bool(T.validate(out_path, base_path)) if os.path.exists(VALIDATE_PY) else None),   # v1.6 (발표 K4): 없으면 '건너뜀'
                'sha': hashlib.sha256(open(out_path, 'rb').read()).hexdigest()[:16], 'content': content_hash(out_path)})
    if workdir is None:   # v1.3 (발표 3-7): 임시 폴더(덱마다 수백 MB)를 지운다 — 대화창 디스크가 찼다
        shutil.rmtree(wd, ignore_errors=True)
    return rep


def report(rep, stream=sys.stdout):
    w = lambda s='': print(s, file=stream)
    w('## 넘김 적용 보고 (handoff.py v%s)' % __version__); w()
    w('| 항목 | 값 |'); w('|---|---|')
    w('| 결과 | %d화면 · validate %s · **sha256 앞 16자 `%s`** · 내용 해시 `%s` (둘 다 적용 회신에 — 다음 넘김의 `기준 sha256` 은 어느 쪽이어도 된다) |' % (
        rep['screens'], {True: '통과', False: '**실패**', None: '건너뜀(validate.py 없음 — 통과 아님)'}[rep['valid']], rep['sha'], rep.get('content', '—')))
    w('| 한 일 | %s |' % (' · '.join(rep['done']) or '없음'))
    w('| 원작자 메모 | 기준 화면 %d곳 그대로%s |' % (rep['memo_ok'], (' · **달라진 화면 %s**' % rep['memo_bad']) if rep['memo_bad'] else ''))
    if rep['dup']:
        w('| 앞에 복제 | %s |' % ', '.join('화면 %d → slide%d(빨강 %d 제거, 해설 상자 %d 삭제)' % d for d in rep['dup']))
    if rep.get('dup_new'):
        w('| 앞에 복제(새·가져옴) | %s |' % ', '.join('"%s" → slide%d(빨강 %d 제거, 해설 상자 %d 삭제)' % d for d in rep['dup_new']))
    for lb, src, sn, mode, memo_n, sizes in rep.get('imports', []):
        w('| 가져옴 | "%s" ← %s → slide%d · %s · 원작자 메모 %s%s |' % (lb.replace('|', '/'), src, sn, mode, ('%d줄' % memo_n) if memo_n else '없음',
                                                         (' · ' + '; '.join(sizes)) if sizes else ''))
    if rep['deleted']:
        w('| 삭제 | 기준 화면 %s |' % rep['deleted'])
    if rep['memo_req']:
        w(); w('**원작자 메모 수정 요청 — 적용하지 않았다(사용자 허락 뒤 `settext(..., notes=True, zone=\'memo\')`)**'); w()
        for no, t in rep['memo_req']:
            w('- 기준 화면 %d: %s' % (no, t))
    if rep['warn']:
        w(); w('**경고**'); w()
        for t in rep['warn']:
            w('- %s' % t)
    # 매핑은 같은 차이가 이어지는 구간으로 줄여 적는다: '3–13 → +1, 14–260 → +2'
    segs, cur = [], None
    for b, r in sorted(rep['mapping'].items()):
        off = r - b
        if cur and cur[2] == off and b == cur[1] + 1:
            cur[1] = b
        else:
            cur = [b, b, off]; segs.append(cur)
    txt = ', '.join(('%d' % s if s == e else '%d–%d' % (s, e)) + ' → %+d' % o for s, e, o in segs if o) or '없음'
    w(); w('**매핑 (기준 화면 → 결과 화면, 밀린 칸 수)**: %s' % txt)


def _screen_texts(deck, sn):
    import html as _h
    x = open(deck._slide(sn), encoding='utf8').read()
    paras = [_h.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>', p))) for p in re.findall(r'<a:p>.*?</a:p>', x, re.S)]
    bg = re.search(r'<p:bg>.*?</p:bg>', x, re.S)
    norm = lambda p: re.sub(r'\s(?:dirty|err|smtClean|noProof|lang|altLang)="[^"]*"', '', p)
    return {'title': _title_text(deck, sn), 'text': [t for t in paras if t.strip()], 'notes': deck.notes_sections(sn),
            'hidden': deck.is_hidden(sn), 'bg': re.sub(r'\s+', '', bg.group(0)) if bg else '',
            'fmt': [norm(p) for p in re.findall(r'<a:p>.*?</a:p>', x, re.S) if _h.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>', p))).strip()],
            'layout': _layout_name_of(deck, sn)}


def _layout_name_of(deck, sn):
    lp = os.path.join(deck.dir, 'ppt/slideLayouts', deck.layout_of(sn))
    m = re.search(r'<p:cSld name="([^"]*)"', open(lp, encoding='utf8').read()) if os.path.exists(lp) else None
    return m.group(1) if m else deck.layout_of(sn)


def compare(a_path, b_path, stream=sys.stdout, workdir=None):
    """두 덱을 화면 순서대로 비교 — 제목·슬라이드 글·노트(대본·참고·메모)·숨김·배경. 도구 적용본과 손 적용본 대조용.
    반환: 다른 화면 수. (서식·위치는 보지 않는다 — 글과 구조만)"""
    import tempfile
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import deck_toolkit as T
    import shutil
    wd = workdir or tempfile.mkdtemp(prefix='hc_')
    A, B = T.Deck.open(a_path, os.path.join(wd, 'a')), T.Deck.open(b_path, os.path.join(wd, 'b'))
    ao, bo = [s for s, _, _ in A.order() if s], [s for s, _, _ in B.order() if s]
    w = lambda s='': print(s, file=stream)
    w('## 덱 비교 (handoff.py v%s) — `%s` ↔ `%s`' % (__version__, os.path.basename(a_path), os.path.basename(b_path))); w()
    if len(ao) != len(bo):
        w('- **화면 수가 다르다: %d ↔ %d** — 앞에서부터 짝지어 본다' % (len(ao), len(bo)))
    diff, lines_out = 0, []
    names = [('title', '제목'), ('text', '슬라이드 글'), ('hidden', '숨김'), ('bg', '배경')]
    for i, (sa, sb) in enumerate(zip(ao, bo), 1):
        ta, tb = _screen_texts(A, sa), _screen_texts(B, sb)
        what = [lab for k, lab in names if ta[k] != tb[k]]
        for j, lab in enumerate(('대본', '참고', '메모')):
            if ta['notes'][j] != tb['notes'][j]:
                what.append(lab)
        # v1.3 (발표 3-7): 글이 같아도 서식(문단 XML — 굵게·강조·색)·레이아웃 이름이 다르면 적는다
        if 'text' not in [k for k, _ in names if ta[k] != tb[k]] and ta['fmt'] != tb['fmt']:
            what.append('서식')
        if ta['layout'] != tb['layout']:
            what.append('레이아웃(%s ↔ %s)' % (ta['layout'], tb['layout']))
        if what:
            diff += 1
            lines_out.append('- 화면 %d: %s' % (i, ', '.join(what)))
    for l in lines_out[:60]:
        w(l)
    if len(lines_out) > 60:
        w('- … 외 %d화면' % (len(lines_out) - 60))
    w(); w('**다른 화면 %d / %d**' % (diff, min(len(ao), len(bo))) + ('' if len(ao) == len(bo) else ' (화면 수 다름)'))
    if workdir is None:
        shutil.rmtree(wd, ignore_errors=True)
    return diff + abs(len(ao) - len(bo))


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('check', help='문법 검사 + (--deck) 기준 덱 대조 미리보기')
    c.add_argument('md'); c.add_argument('--deck', default=None); c.add_argument('--sha', default=None, help='보낸 쪽이 적은 넘김 문서 sha256 앞 16자')
    ap_ = sub.add_parser('apply', help='check 오류 0 일 때만 적용 + 보고서 (v1.2)')
    ap_.add_argument('md'); ap_.add_argument('--deck', required=True); ap_.add_argument('-o', '--out', required=True)
    ap_.add_argument('--sha', default=None); ap_.add_argument('--import', dest='imports', action='append', default=[], help='덱이름=경로 (가져옴)')
    ap_.add_argument('--report', default=None, help='보고서 md 도 파일로')
    cp = sub.add_parser('compare', help='두 덱을 화면별로 비교(글·노트·숨김·배경) — 도구 적용본과 손 적용본 대조 (v1.2)')
    cp.add_argument('a'); cp.add_argument('b')
    a = ap.parse_args()
    if a.cmd == 'compare':
        sys.exit(1 if compare(a.a, a.b) else 0)
    if a.cmd == 'apply':
        b = open(a.md, 'rb').read()
        doc = parse(b.decode('utf8'))
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import deck_toolkit as T
        D = T.Deck.open(a.deck); D.src_path = a.deck
        e, _ = check(doc, D, b, a.sha)
        if e:
            print('\n**적용하지 않았다 — 위 오류를 넘긴 쪽에 돌려보낸다**')
            sys.exit(1)
        imports = dict(x.split('=', 1) for x in a.imports)
        try:
            rep = apply(doc, a.deck, a.out, imports)
        except Exception as ex:   # v1.3 (발표 3-2): Traceback 이 아니라 멈춤·보고 — 결과 파일은 만들지 않는다
            if os.path.exists(a.out):
                os.remove(a.out)
            print('\n**멈춤 — 적용 중 문제: %s**\n결과 파일을 만들지 않았다. 넘긴 쪽과 확인하거나 코드에 도구회신.' % ex)
            sys.exit(1)
        print()
        report(rep)
        if a.report:
            import io as _io
            buf = _io.StringIO(); report(rep, buf); open(a.report, 'w', encoding='utf8').write(buf.getvalue())
        sys.exit(0 if rep['valid'] is not False and not rep['memo_bad'] else 1)
    b = open(a.md, 'rb').read()
    doc = parse(b.decode('utf8'))
    D = None
    if a.deck:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import deck_toolkit as T
        D = T.Deck.open(a.deck)
        D.src_path = a.deck
    e, _ = check(doc, D, b, a.sha)
    sys.exit(1 if e else 0)


if __name__ == '__main__':
    main()
