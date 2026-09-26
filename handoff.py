#!/usr/bin/env python3
"""handoff.py — 영상의학 넘김 문서(`{YYMMDD}_전평대본_{덱}_v{N}.md`)의 문법 검사와 미리보기 (apply-handoff 1단계).

문법은 HANDOFF_FORMAT.md. 원칙: **문법에 없는 줄을 만나면 추측하지 않고 멈춘다** — 전에 덱 스크립트들이 넘김 형식의
변형을 알아서 받아 주다 대본 첫 줄을 빠뜨렸다(D2). 미리보기는 기준 덱과 대조해 판 착오(D11)를 적용 전에 잡는다.

    python3 handoff.py check 넘김.md                         # 문법만
    python3 handoff.py check 넘김.md --deck 기준.pptx          # + 기준 덱 대조(화면 수·제목·문단 키·본문 수정)
    python3 handoff.py check 넘김.md --deck 기준.pptx --sha 1a2b3c4d5e6f7a8b   # 넘김 문서 sha256 앞 16자도 대조

적용(2단계)·검증 보고서(3단계)는 다음 판.
"""
import hashlib
import os
import re
import sys

__version__ = '1.1'   # HANDOFF_FORMAT.md 첫 줄·test_handoff.EXPECT_VERSION 과 함께 올린다

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
    doc = {'base': None, 'screens_n': None, 'base_sha': None, 'screens': {}, 'new': [], 'fixes': [],
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
    if not doc['base']:
        prob('오류', 1, '기준 덱이 없다 — 머리에 "> 기준: **{기준 덱}**(N화면)" 가 있어야 화면 번호를 맞출 수 있다')

    cur, zone, coll = None, 'prose', None   # coll = (대상 목록, 이름)
    pending_para = None

    def close():
        nonlocal cur, coll, pending_para
        if pending_para:
            prob('오류', pending_para['ln'], '문단 %s 뒤에 "본문:" 과 L 줄이 없다' % pending_para['kind'])
        if cur is not None:
            if cur['ops'] is None:
                prob('오류', cur['ln'], '"작업:" 줄이 없다')
            if cur['script'] is None and not any(o[0] == '삭제' for o in (cur['ops'] or [])):
                prob('오류', cur['ln'], '"대본:" 이 없다 — 대본을 바꾸지 않으면 "대본: 변경 없음"')
            if cur['kind'] == 'screen' and cur['tips'] is None and not any(o[0] == '삭제' for o in (cur['ops'] or [])):
                prob('오류', cur['ln'], '"참고:" 가 없다 — 없으면 "참고: 없음", 그대로면 "참고: 변경 없음"')
            if cur['kind'] == 'new':
                if not cur['title']:
                    prob('오류', cur['ln'], '새 슬라이드에 "제목:" 이 없다')
                if not cur['body']:
                    prob('오류', cur['ln'], '새 슬라이드에 "본문:" 이 없다')
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
                   'title_h': (m_scr.group(2) if m_scr else m_new.group(1)).strip(), 'ops': None, 'note': '',
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
            probs.append(('오류', 0, '기준 덱 sha256 %s ≠ 넘김 머리의 기준 sha256 %s — 기준 판과 파일이 다르다. 다른 판이거나, '
                          '사용자가 고쳐 저장했는지 확인(열어 저장만 해도 바뀐다)' % (deck_path_sha(deck), doc['base_sha'])))
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
                if name == '새 슬라이드' and args and int(args[0]) > n:
                    probs.append(('오류', nw['ln'], '새 슬라이드 틀 화면 %s 없음' % args[0]))
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
        w(); w('**새 슬라이드 %d장**: %s' % (len(doc['new']), ' / '.join(n['title'] or n['title_h'] for n in doc['new'])))
    w(); w('적용 순서(2단계): 본문 수정 → 문단 교체·추가·삭제 → 배경·숨김 → 새 슬라이드·가져옴 → 앞에 복제(정답 표시 제거·해설 상자) → '
           '이동·삭제 → **원작자 메모 수정**(요청이 있고 사용자가 허락한 것만 — 노트를 쓰기 전에, D8) → 노트(대본·참고, 기존 메모 보존) → '
           '매핑표·검증 보고서')
    if doc['base_sha'] is None:
        w('기준 sha256 이 머리에 없다 — 노트만 다른 판(예: 한 판 앞 덱)은 화면 수·제목·문단 키로 구별되지 않는다. '
          '발표 적용 회신의 결과 sha256 을 다음 넘김 머리 `기준 sha256` 에 적으면 잡힌다')
    return len(errs), len(warns)


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


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('check', help='문법 검사 + (--deck) 기준 덱 대조 미리보기')
    c.add_argument('md'); c.add_argument('--deck', default=None); c.add_argument('--sha', default=None, help='보낸 쪽이 적은 넘김 문서 sha256 앞 16자')
    a = ap.parse_args()
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
