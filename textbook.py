#!/usr/bin/env python3
"""textbook.py — 교과서 PDF 분할·색인 (1단계 probe · 2단계 plan). 규약은 TEXTBOOK.md.

대화창의 Drive 연결은 큰 스캔 PDF 의 내용을 읽지 못한다(09-27 시험: 내용 빈칸). 그래서 분할 규칙을 정하기 전에
Cowork 가 Mac 동기화 폴더에서 책마다 구조를 조사해 md 로 남기고, 대화창이 그 md 를 읽어 규칙을 정한다.
원본 PDF 는 읽기만 한다 — 이 도구는 --out 폴더 밖에 아무것도 쓰지 않는다.

    python3 textbook.py probe 교과서폴더 --out 결과폴더 [--name 260927_회신_Cowork→코드_교과서probe_v1]
                              [--only 글자] [--front 40] [--samples 20]

    python3 textbook.py plan  교과서폴더 --out 결과폴더 [--name …교과서plan_v1] [--only 글자] [--skip 글자 …]
                              [--level N] [--budget 150]

결과: `{name}_요약.md`(책마다 한 줄 표) + `{name}_{NN}.md`(책마다). probe 는 구조(책갈피·글자층·차례 쪽·쪽 번호 차이),
plan 은 장 표(장·제목·PDF 쪽 범위·인쇄 쪽·근거·확인 필요) — 사용자가 확인한 장 표로 3단계 분할을 한다.
plan 은 --budget 초가 차면 멈추고, 같은 명령을 다시 돌리면 이미 쓴 책은 건너뛰고 이어서 한다(Cowork 셸 180초 제한).
공통: --recursive(하위 폴더), --skip(빼기, 여러 번). 시작 전에 모든 대상 PDF 의 앞·끝을 읽어 보고, 클라우드에만 있는
파일(Errno 35 등)이 있으면 아무것도 쓰지 않고 멈춘다. pypdf 가 필요하다 — 없으면 설치 방법을 알리고 멈춘다.
"""
import argparse
import os
import re
import signal
import subprocess
import sys
import time
import unicodedata
from collections import Counter

__version__ = '0.3'   # TEXTBOOK.md 첫 줄·test_textbook.EXPECT_VERSION 과 함께 올린다

TOC_WORDS = re.compile(r'차\s*[례려레]|목\s*차|c\s*o\s*n\s*t\s*e\s*n\s*t\s*s', re.I)   # v0.2: OCR '차려'·'C O N T E N T S'
NUM_LINE = re.compile(r'^\s*[-–—]?\s*(\d{1,4})\s*[-–—]?\s*$')
BAD_NAME = re.compile(r'[&/?\\:*"<>|]')


def load_pypdf():
    """pypdf 를 찾는다. 없으면 /tmp/pypdf (git clone 한 소스)도 본다. 끝내 없으면 방법을 알리고 멈춘다."""
    try:
        import pypdf
        return pypdf
    except ImportError:
        pass
    if os.path.isdir('/tmp/pypdf/pypdf'):
        sys.path.insert(0, '/tmp/pypdf')
        try:
            import pypdf
            return pypdf
        except ImportError:
            pass
    raise SystemExit('[멈춤] pypdf 가 없다. 둘 중 하나:\n'
                     '  pip install --user pypdf\n'
                     '  git clone -q --depth 1 https://github.com/py-pdf/pypdf /tmp/pypdf   (순수 Python — pip 가 막혔을 때)')


def _nfc(x):
    return unicodedata.normalize('NFC', x)     # Mac 파일 이름은 한글이 NFD 로 올 수 있다


def list_books(folder, only=None, skip=(), recursive=False, numbered=False):
    """PDF 목록(폴더 기준 상대 경로, NFC 순). numbered=True 면 (번호, 경로) — 번호는 --only 전 목록 기준이라 나눠 돌려도 같다."""
    if not os.path.isdir(folder):
        raise SystemExit('[멈춤] 폴더가 없다: %s — Cowork 에 동기화 폴더를 연결했는지 본다' % folder)
    found = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.')) if recursive else []
        rel = os.path.relpath(root, folder)
        for f in files:
            if f.lower().endswith('.pdf') and not f.startswith('.'):
                found.append(f if rel == '.' else os.path.join(rel, f))
    allb = sorted(found, key=_nfc)          # v0.3 (Cowork plan 3-1): 번호는 --skip·--only 전 목록 — 뺐다 넣어도 같은 책은 같은 번호
    sel = [(k, b) for k, b in enumerate(allb, 1) if (not only or _nfc(only) in _nfc(b))
           and not any(_nfc(x) in _nfc(b) for x in (skip or ()))]
    if not sel:
        raise SystemExit('[멈춤] %s 에 PDF 가 없다%s' % (folder, (' (--only %s)' % only) if only else ''))
    return sel if numbered else [b for _, b in sel]


def _read_ends(path):
    with open(path, 'rb') as f:
        head = f.read(8)
        f.seek(max(0, os.path.getsize(path) - 1024))
        f.read(1024)
    return head


def preflight(folder, books):
    """쓰기 전에 모든 대상의 앞·끝을 읽는다. 클라우드에만 있는 파일은 여기서 OSError(맥 Errno 35 등) — 아무것도 쓰지 않고 멈춘다."""
    bad = []
    for b in books:
        try:
            _read_ends(os.path.join(folder, b))
        except OSError as e:
            bad.append('%s — %s' % (b, e))
    if bad:
        raise SystemExit('[멈춤] 읽을 수 없는 PDF %d권 — 아무것도 쓰지 않았다.\n  %s\n'
                         'Drive 에서 클라우드에만 있는 파일이면: Mac Finder 에서 교과서 폴더 → 오른쪽 단추 → '
                         '"오프라인으로 사용 가능" 으로 내려받은 뒤 다시 돌린다.' % (len(bad), '\n  '.join(bad)))


def _outline(reader):
    out = []

    def walk(items, depth):
        for it in items:
            if isinstance(it, list):
                walk(it, depth + 1)
                continue
            try:
                pg = reader.get_destination_page_number(it) + 1
            except Exception:
                pg = None
            out.append((depth, str(getattr(it, 'title', '') or '').strip(), pg))
    try:
        walk(reader.outline, 0)
    except Exception as e:
        out.append((0, '(책갈피 읽기 실패: %s)' % type(e).__name__, None))
    return out


def _page_text(page):
    try:
        return page.extract_text() or ''
    except Exception as e:
        return '\x00%s' % type(e).__name__


def _has_image(page):
    try:
        xo = page['/Resources'].get_object().get('/XObject')
        if not xo:
            return False
        xo = xo.get_object()
        return any(xo[k].get_object().get('/Subtype') == '/Image' for k in xo)
    except Exception:
        return False


def _printed_number(text):
    """쪽 위·아래 두 줄에서 숫자만 있는 줄 → 인쇄 쪽 번호 후보."""
    lines = [l for l in text.splitlines() if l.strip()]
    for l in lines[:2] + lines[-2:]:
        m = NUM_LINE.match(l)
        if m and 0 < int(m.group(1)) < 5000:
            return int(m.group(1))
    return None


def sample_pages(n, front, samples):
    """앞부분 front 쪽 + 뒤쪽 전체에서 고르게 samples 쪽 (0부터)."""
    head = list(range(min(n, front)))
    rest = n - len(head)
    if rest <= 0 or samples <= 0:
        return head, []
    step = rest / float(samples + 1)
    body = sorted({len(head) + int(step * (i + 1)) for i in range(samples)} - set(head))
    return head, [p for p in body if p < n]


def probe_book(path, front=40, samples=20):
    pypdf = load_pypdf()
    t0 = time.time()
    r = {'file': os.path.basename(path), 'bytes': os.path.getsize(path), 'error': None}
    try:
        reader = pypdf.PdfReader(path, strict=False)
        if reader.is_encrypted:
            try:
                reader.decrypt('')
            except Exception:
                pass
        r['encrypted'] = bool(reader.is_encrypted)
        n = len(reader.pages)
        r['pages'] = n
        meta = reader.metadata or {}
        r['producer'] = ' / '.join(str(meta.get(k, '')).strip() for k in ('/Creator', '/Producer') if meta.get(k))
        r['outline'] = _outline(reader)
        root = reader.trailer['/Root'].get_object()
        r['page_labels'] = '/PageLabels' in root
        if r['page_labels']:
            try:
                labs = reader.page_labels
                r['labels_sample'] = [(i + 1, labs[i]) for i in sorted({0, 1, 2, min(front, n - 1), n // 2, n - 1}) if i < n]
            except Exception as e:
                r['labels_sample'] = [('읽기 실패', type(e).__name__)]
        head, body = sample_pages(n, front, samples)
        r['front'], r['body'] = [], []
        for i in head + body:
            pg = reader.pages[i]
            tx = _page_text(pg)
            item = {'page': i + 1, 'chars': len(tx.strip()) if not tx.startswith('\x00') else -1,
                    'image': _has_image(pg), 'text': tx, 'num': _printed_number(tx)}
            (r['front'] if i in head else r['body']).append(item)
        allp = r['front'] + r['body']
        r['text_pages'] = sum(1 for p in allp if p['chars'] >= 50)
        r['sampled'] = len(allp)
        r['image_pages'] = sum(1 for p in allp if p['image'])
        r['toc_pages'] = [p['page'] for p in r['front'] if TOC_WORDS.search(p['text'][:400])]
        diffs = Counter(p['page'] - p['num'] for p in r['body'] if p['num'] is not None)
        r['offset'] = diffs.most_common(1)[0] if diffs else None
        r['offset_n'] = sum(diffs.values())
    except Exception as e:
        r['error'] = '%s: %s' % (type(e).__name__, str(e)[:200])
    r['seconds'] = round(time.time() - t0, 1)
    return r


def _cell(s):
    return str(s).replace('|', '\\|').replace('\n', ' ')


def summary_row(k, r):
    if r['error']:
        return '| %02d | %s | %.0f | — | — | — | — | — | — | 오류: %s |' % (k, _cell(r['file']), r['bytes'] / 1e6, _cell(r['error']))
    ol = r['outline']
    olc = '%d개 · 깊이 %d' % (len(ol), max(d for d, _, _ in ol) + 1) if ol else '없음'
    tx = '%d/%d' % (r['text_pages'], r['sampled'])
    off = ('%+d (%d/%d)' % (r['offset'][0], r['offset'][1], r['offset_n'])) if r['offset'] else '—'
    toc = ', '.join(map(str, r['toc_pages'][:8])) or '—'
    return '| %02d | %s | %.0f | %d | %s | %s | %s | %s | %s | %s |' % (
        k, _cell(r['file']), r['bytes'] / 1e6, r['pages'], olc, '있음' if r['page_labels'] else '없음', tx, toc, off,
        _cell(r['producer'] or '—')[:60])


def book_md(k, r, name):
    L = ['# %s_%02d — %s' % (name, k, r['file']), '',
         '> textbook.py v%s probe. 원본은 읽기만 했다. 쪽 번호는 PDF 쪽(1부터).' % __version__, '']
    if r['error']:
        return '\n'.join(L + ['**오류**: %s' % r['error'], ''])
    L += ['| 항목 | 값 |', '|---|---|',
          '| 크기 | %d 바이트 |' % r['bytes'], '| 쪽 | %d |' % r['pages'],
          '| 만든 프로그램 | %s |' % _cell(r['producer'] or '—'), '| 암호 | %s |' % ('있음' if r['encrypted'] else '없음'),
          '| 글자층(표본 쪽 중 50자 이상) | %d / %d |' % (r['text_pages'], r['sampled']),
          '| 그림 있는 표본 쪽 | %d / %d |' % (r['image_pages'], r['sampled']),
          '| 쪽 번호 표(PageLabels) | %s |' % (', '.join('%s→%s' % x for x in r.get('labels_sample', [])) if r['page_labels'] else '없음'),
          '| 인쇄 쪽 번호 차이(PDF 쪽 − 인쇄 쪽, 최빈) | %s |' % (('%+d — 표본 %d 중 %d' % (r['offset'][0], r['offset_n'], r['offset'][1])) if r['offset'] else '못 찾음'),
          '| 조사 시간 | %s 초 |' % r['seconds'], '']
    L += ['## 1. 책갈피 (%d개)' % len(r['outline']), '']
    if r['outline']:
        L += ['%s- %s — p.%s' % ('  ' * d, t or '(제목 없음)', p if p else '?') for d, t, p in r['outline'][:600]]
        if len(r['outline']) > 600:
            L.append('- … %d개 더' % (len(r['outline']) - 600))
    else:
        L.append('없음')
    L += ['', '## 2. 차례 후보 쪽 (글자 전부)', '']
    toc = [p for p in r['front'] if p['page'] in r['toc_pages']]
    if not toc:
        L.append('못 찾음 — "차례·목차·Contents" 가 앞 %d쪽의 머리에 없다. §3 의 쪽 머리로 판단한다.' % len(r['front']))
    for p in toc:
        L += ['### PDF p.%d (%d자)' % (p['page'], p['chars']), '', '```', p['text'].strip()[:6000], '```', '']
    L += ['', '## 3. 앞부분 쪽 머리 (쪽마다 120자)', '', '| PDF 쪽 | 글자 | 그림 | 인쇄 번호 | 머리 |', '|---|---|---|---|---|']
    for p in r['front']:
        L.append('| %d | %d | %s | %s | %s |' % (p['page'], p['chars'], '○' if p['image'] else '', p['num'] or '',
                                                _cell(re.sub(r'\s+', ' ', p['text'].strip())[:120])))
    L += ['', '## 4. 본문 표본 쪽', '', '| PDF 쪽 | 글자 | 그림 | 인쇄 번호 | 머리 |', '|---|---|---|---|---|']
    for p in r['body']:
        L.append('| %d | %d | %s | %s | %s |' % (p['page'], p['chars'], '○' if p['image'] else '', p['num'] or '',
                                                _cell(re.sub(r'\s+', ' ', p['text'].strip())[:120])))
    return '\n'.join(L) + '\n'


def probe(folder, out, name, only=None, front=40, samples=20, stream=sys.stdout, skip=(), recursive=False):
    if BAD_NAME.search(name):
        raise SystemExit('[멈춤] --name 에 & / ? 같은 기호를 쓰지 않는다(전달 규약 §3): %s' % name)
    if not os.path.isdir(folder):
        raise SystemExit('[멈춤] 폴더가 없다: %s — Cowork 에 동기화 폴더를 연결했는지 본다' % folder)
    load_pypdf()
    numbered = list_books(folder, only, skip, recursive, numbered=True)
    books = [b for _, b in numbered]
    preflight(folder, books)
    os.makedirs(out, exist_ok=True)
    if os.path.exists(os.path.join(out, '%s_요약.md' % name)):
        raise SystemExit('[멈춤] %s_요약.md 가 이미 있다 — 같은 이름을 다시 쓰지 않는다(규약 §3). --name 의 판을 올린다' % name)
    res = []
    for k, f in numbered:
        print('[%02d] %s' % (k, f), file=stream, flush=True)
        r = probe_book(os.path.join(folder, f), front, samples)
        r['file'] = f
        res.append(r)
        open(os.path.join(out, '%s_%02d.md' % (name, k)), 'w', encoding='utf8').write(book_md(k, r, name))
    S = ['# %s_요약' % name, '',
         '> textbook.py v%s probe · 폴더 `%s` · PDF %d권 · 앞 %d쪽 + 본문 표본 %d쪽. 책마다 `%s_{번호}.md`.' % (
             __version__, os.path.basename(os.path.normpath(folder)), len(books), front, samples, name),
         '> 글자층 = 표본 쪽 중 50자 이상 나온 쪽. 쪽 번호 차이 = PDF 쪽 − 인쇄 쪽(최빈값, 맞은 수/찾은 수).', '',
         '| # | 파일 | MB | 쪽 | 책갈피 | 쪽 번호 표 | 글자층 | 차례 후보 | 쪽 번호 차이 | 만든 프로그램 |',
         '|---|---|---|---|---|---|---|---|---|---|']
    S += [summary_row(k, r) for (k, _), r in zip(numbered, res)]
    S += ['', '오류 %d권 · 조사 %.0f 초' % (sum(1 for r in res if r['error']), sum(r['seconds'] for r in res)), '']
    open(os.path.join(out, '%s_요약.md' % name), 'w', encoding='utf8').write('\n'.join(S))
    print('\n'.join(S), file=stream)
    return res


# ───────────────────────── 2단계: plan (장 표 제안) ─────────────────────────
# 스캔 교과서는 책갈피가 없다. 홀수 쪽 머리의 "제 N 장 제목 쪽" 을 따라 장을 정한다. OCR 은 '제'→'저1'·'저|', '장'→'잠·징'
# 으로 읽는다(09-27 조사: '저15 징' = 5장, '저1 9 장' = 9장, '제 1 0 장' = 10장). 그래서 쪽마다 후보 번호를 여럿 두고,
# 장 번호가 쪽을 따라 c → c 또는 c+1(드물게 c+2) 로만 가며, 새 번호는 뒤 12쪽 안에서 한 번 더 나와야 받아들인다.
HEAD_KO = re.compile(r'(제|저)\s*([\]|lI!]?)\s*(\d(?:\s?\d){0,2})\s*[장잠징쟁]')
HEAD_EN = re.compile(r'\bchapter\s*(\d{1,3})\b', re.I)
OPENER = re.compile(r'(?:C\s*H\s*A\s*P\s*T\s*E\s*R|A\s*P\s*T?\s*E\s*R|T\s*E\s*R|(?<![A-Za-z])E\s*R)\s*(\d{1,2})(?!\d)')
LEAD_NUM = re.compile(r'^\s*(\d{1,4})\s')
CHUNK = 30
CH_TITLE = re.compile(r'^\s*(?:chapter|ch\.?)\s*\d+|^\s*\d{1,3}(?:[\s.:)]|$)|^\s*제\s*\d+\s*장', re.I)


def head_candidates(prefix, mark, digits):
    raw = digits
    d = raw.replace(' ', '')
    out = {int(d)}
    if len(d) >= 2 and d[0] == '1' and (prefix == '저' or raw.startswith('1 ')):
        out.add(int(d[1:]))
    return {x for x in out if 0 < x < 100}


def page_marks(text):
    """쪽 글자 → {'head': 장 번호 후보, 'opener': 여는 쪽 표지 번호, 'title': 쪽 머리 제목, 'num': 인쇄 쪽 후보}."""
    t = text or ''
    win = t[:200] + ' \n ' + t[-120:]
    heads, title, num = set(), None, None
    sets = [head_candidates(m.group(1), m.group(2), m.group(3)) for m in HEAD_KO.finditer(win)]
    sets += [{int(m.group(1))} for m in HEAD_EN.finditer(win)]
    if len(sets) >= 2 and not set.intersection(*sets):
        # 서로 다른 장 번호가 한 쪽에 여럿 — 차례·목록 쪽이다. 쪽 머리로 쓰지 않는다
        return {'head': set(), 'opener': set(), 'title': None, 'num': None, 'lead': re.sub(r'\s+', '', t[:80]), 'list': True}
    for m in HEAD_KO.finditer(win):
        heads |= head_candidates(m.group(1), m.group(2), m.group(3))
        if title is None:
            rest = win[m.end():m.end() + 60]
            mm = re.match(r'\s*(.*?)\s+(\d{1,4})(?=\s|$)', rest)
            title = (mm.group(1) if mm else rest.split('\n')[0])[:40].strip()
            if mm:
                num = int(mm.group(2))
    for m in HEAD_EN.finditer(win):
        heads.add(int(m.group(1)))
        if title is None:
            rest = win[m.end():m.end() + 60]
            mm = re.match(r'\s*(.*?)\s+(\d{1,4})(?=\s|$)', rest)
            title = (mm.group(1) if mm else rest.split('\n')[0])[:40].strip()
            if mm:
                num = int(mm.group(2))
    if num is None:
        m = LEAD_NUM.match(t[:12])
        if m:
            num = int(m.group(1))
    if num is None:
        num = _printed_number(t)
    opener = {int(m.group(1)) for m in OPENER.finditer(t[:150])}
    return {'head': {h for h in heads if 0 < h < 100}, 'opener': opener, 'title': title, 'num': num,
            'lead': re.sub(r'\s+', '', t[:80])}


def resolve_chapters(marks, lookahead=12):
    """marks: 쪽마다 page_marks 결과(0 = PDF p.1). → 장 목록 [{num, first, last, pages}] (쪽은 0부터)."""
    n, c, hits, skipped = len(marks), 0, {}, []
    for i in range(n):
        cand = marks[i]['head']
        if not cand:
            continue
        if c in cand:
            hits[c].append(i)
            continue
        if c == 0:
            # v0.3 (Cowork plan: 근골격영상의학 2 — 장 번호가 1이 아니라 이어진다): 첫 장은 어떤 번호든, 뒤 20쪽 안에서 두 번 이상 다시
            # 나오는 후보 중 가장 많이 나오는 것('저11 장' = {1, 11} 이면 뒤 쪽 머리가 가른다)
            sup = {k: sum(1 for j in range(i + 1, min(n, i + 21)) if k in marks[j]['head']) for k in cand}
            k = max(sorted(sup), key=lambda x: sup[x])
            if sup[k] >= 2:
                c = k
                hits[k] = [i]
            continue
        for k in (c + 1, c + 2):
            if k in cand and any(k in marks[j]['head'] for j in range(i + 1, min(n, i + 1 + lookahead))):
                if k == c + 2:
                    skipped.append(c + 1)
                c = k
                hits[k] = [i]
                break
    return [{'num': k, 'first': v[0], 'last': v[-1], 'pages': v} for k, v in sorted(hits.items())], skipped


def _clean_title(t):
    """v0.3: 쪽 머리 제목 앞의 구분선 OCR 조각('I '·'| '·'l ')과 끝의 부스러기를 뗀다."""
    t = re.sub(r'^\s*[I|l1!\]]\s+', '', t or '')
    return re.sub(r'[\s\W_]+$', '', t).strip()


BACK = re.compile(r'찾\s*아\s*보\s*기|색\s*인|index', re.I)


def _title_key(s):
    return re.sub(r'[\s\W\d_]+', '', s or '')


def chapters_from_heads(marks):
    chs, skipped = resolve_chapters(marks)
    checks = ['%d장: 쪽 머리를 찾지 못했다(건너뜀) — 앞뒤 장의 경계를 사람이 확인' % k for k in skipped]
    out, prev_last = [], -1
    for ch in chs:
        titles = Counter(_clean_title(marks[i]['title']) for i in ch['pages'] if marks[i]['title'])
        titles.pop('', None)
        title = titles.most_common(1)[0][0] if titles else ''
        key = _title_key(title)[:4]
        lo = prev_last + 1 if prev_last >= 0 else max(0, ch['first'] - 8)
        start, why = None, ''
        for i in range(lo, ch['first'] + 1):
            if marks[i].get('list'):
                continue                              # 차례·목록 쪽
            if ch['num'] in marks[i]['opener']:
                start, why = i, '여는 쪽 표지'
                break
            if key and len(key) >= 2 and key in _title_key(marks[i]['lead'])[:40] and not marks[i]['head']:
                start, why = i, '여는 쪽 제목'
                break
        if start is None:
            start, why = max(lo, ch['first'] - 1), '쪽 머리만'
            checks.append('%d장 시작 PDF p.%d 는 추정(첫 쪽 머리 p.%d 바로 앞) — 여는 쪽을 확인' % (ch['num'], start + 1, ch['first'] + 1))
        out.append(dict(num=ch['num'], title=title, start=start, why=why, heads=ch['pages']))
        prev_last = ch['last']
    for a, b in zip(out, out[1:]):
        a['end'] = b['start'] - 1
    if out:
        last = chs[-1]['last']
        back = next((i for i in range(last + 1, len(marks)) if BACK.search(marks[i]['lead'][:30]) and not marks[i]['head']), None)
        if back is not None:
            out[-1]['end'] = back - 1              # v0.3: 찾아보기·Index 쪽 앞까지(마지막 장의 참고문헌 포함)
        else:
            out[-1]['end'] = last
            if last < len(marks) - 1:
                checks.append('마지막 장의 끝을 마지막 쪽 머리 p.%d 로 두었다(찾아보기·Index 쪽을 못 찾음) — 뒤 경계를 확인' % (last + 1))
    return out, checks


def chapters_from_outline(outline, n, level=None):
    """책갈피 한 수준을 장으로. level 없으면 'Chapter N'·'N.' 제목이 가장 많은 수준, 그것도 없으면 5개 이상인 가장 얕은 수준."""
    ent = [(d, t, p) for d, t, p in outline if p]
    depths = Counter(d for d, _, _ in ent)
    by_title = False
    if level is None:
        # v0.3 (Cowork plan: Cardiac 330쪽에 131개 — 절 수준): 평균 4쪽 미만인 깊이는 장으로 보지 않는다
        fine = {d for d in depths if n / float(depths[d]) >= 4}
        score = {d: sum(1 for dd, t, _ in ent if dd == d and CH_TITLE.match(t)) for d in depths if d in fine}
        best = max(score, key=lambda d: (score[d], -d)) if score else None
        if best is not None and score[best] >= 5:
            level, by_title = best, True
        else:
            ok = [d for d in sorted(depths) if depths[d] >= 5 and d in fine]
            level = ok[0] if ok else None
    if level is None:
        return None, depths, None
    idxs = [i for i, (d, _, _) in enumerate(ent) if d == level]
    if by_title:                                     # 장 제목 앞뒤의 Cover·Contents·Index 는 앞붙이·뒤붙이로
        hit = [i for i in idxs if CH_TITLE.match(ent[i][1])]
        idxs = [i for i in idxs if hit[0] <= i <= hit[-1]]
    out = []
    for idx, (d, t, p) in enumerate(ent):
        if idx not in idxs or (out and out[-1]['start'] == p - 1):
            continue
        nxt = next((pp for dd, _, pp in ent[idx + 1:] if dd <= level and pp > p), None)
        out.append(dict(num=len(out) + 1, title=t, start=p - 1, end=(nxt - 2) if nxt else n - 1, why='책갈피 깊이 %d' % level))
    return out, depths, level


def _offsets(marks, lo, hi):
    """장 안에서 (PDF 쪽 − 인쇄 쪽) 최빈값. v0.3: 3표 이상·과반·|차이| ≤ 60·인쇄 시작 ≥ 1 이 아니면 None('—') — 복부영상의학에서
    본문 속 숫자를 쪽 번호로 읽어 '-144–35' 가 나왔다. 인쇄 0쪽(번호 없는 여는 쪽)까지는 둔다."""
    c = Counter(i - (marks[i]['num'] - 1) for i in range(lo, hi + 1) if marks[i].get('num'))
    if not c:
        return None
    off, v = c.most_common(1)[0]
    if v < 3 or v * 2 < sum(c.values()) or abs(off) > 60 or lo - off + 1 < 0:
        return None
    return off, v


def plan_book(path, level=None):
    pypdf = load_pypdf()
    t0 = time.time()
    r = {'bytes': os.path.getsize(path), 'error': None, 'checks': [], 'chapters': []}
    try:
        reader = pypdf.PdfReader(path, strict=False)
        if reader.is_encrypted:
            try:
                reader.decrypt('')
            except Exception:
                pass
        n = r['pages'] = len(reader.pages)
        ol = _outline(reader)
        chs, depths, lv = chapters_from_outline(ol, n, level)
        r['depths'] = depths
        r['outline_titles'] = {d: [t for dd, t, p in ol if dd == d and p][:8] for d in sorted(depths)}
        labels = None
        if '/PageLabels' in reader.trailer['/Root'].get_object():
            try:
                labels = reader.page_labels
            except Exception:
                labels = None
        if chs and len(chs) >= 3:
            r['method'] = '책갈피 (깊이 %d)' % lv
            r['chapters'] = chs
            marks = None
            if labels is None:
                r['checks'].append('쪽 번호 표(PageLabels)가 없어 인쇄 쪽을 적지 않았다')
        else:
            if ol and level is None:
                r['checks'].append('책갈피 %d개는 장으로 쓰기에 모자라 쪽 머리로 정했다' % len(ol))
            marks = [page_marks(_page_text(pg)) for pg in reader.pages]
            r['head_pages'] = sum(1 for m in marks if m['head'])
            chs, checks = chapters_from_heads(marks)
            r['method'] = '쪽 머리' if chs else '쪽 묶음 %d' % CHUNK
            if not chs:
                # v0.3: 장을 못 정한 책(쪽 머리가 없는 책)은 30쪽 묶음 — 제목 없이도 INDEX(쪽 범위)와 글자 md 로 찾을 수 있게
                chs = [dict(num=i // CHUNK + 1, title='p.%d–%d' % (i + 1, min(n, i + CHUNK)), start=i, end=min(n, i + CHUNK) - 1,
                            why='쪽 묶음') for i in range(0, n, CHUNK)]
                checks.append('쪽 머리("제 N 장"·"Chapter N")를 못 찾아 %d쪽 묶음으로 나눴다 — 장으로 나누려면 장 시작 쪽 목록을 사용자가 준다' % CHUNK)
            r['chapters'], r['checks'] = chs, r['checks'] + checks
        for ch in r['chapters']:
            ch['pages_n'] = ch['end'] - ch['start'] + 1
            if labels:
                ch['printed'] = '%s–%s' % (labels[ch['start']], labels[ch['end']])
            elif marks:
                off = _offsets(marks, ch['start'], ch['end'])
                ch['printed'] = ('%d–%d' % (ch['start'] - off[0] + 1, ch['end'] - off[0] + 1)) if off else '—'
                ch['offset'] = off
            else:
                ch['printed'] = '—'
        r['labels'] = bool(labels)
    except Exception as e:
        r['error'] = '%s: %s' % (type(e).__name__, str(e)[:200])
    r['seconds'] = round(time.time() - t0, 1)
    return r


def plan_md(k, f, r, name):
    ck = len(r['checks'])
    head = '<!-- plan: method=%s chapters=%d check=%d pages=%s seconds=%s error=%s -->' % (
        r.get('method', '—'), len(r['chapters']), ck, r.get('pages', '—'), r['seconds'], 'yes' if r['error'] else 'no')
    L = [head, '# %s_%02d — %s' % (name, k, f), '',
         '> textbook.py v%s plan. 원본은 읽기만 했다. PDF 쪽은 1부터. **사용자가 이 장 표를 확인·고친 뒤** 3단계 분할에 쓴다.' % __version__, '']
    if r['error']:
        return '\n'.join(L + ['**오류**: %s' % r['error'], ''])
    L += ['| 항목 | 값 |', '|---|---|', '| 쪽 | %d |' % r['pages'], '| 방법 | %s |' % r['method'],
          '| 책갈피 깊이별 개수 | %s |' % (', '.join('%d: %d' % kv for kv in sorted(r['depths'].items())) or '없음'),
          '| 쪽 머리가 잡힌 쪽 | %s |' % r.get('head_pages', '—'), '| 인쇄 쪽 | %s |' % ('쪽 번호 표' if r['labels'] else '장마다 PDF 쪽 − 최빈 차이'),
          '| 조사 시간 | %s 초 |' % r['seconds'], '']
    L += ['## 1. 장 표', '', '| 장 | 제목 | PDF 시작 | PDF 끝 | 쪽 수 | 인쇄 쪽 | 근거 |', '|---|---|---|---|---|---|---|']
    chs = r['chapters']
    if chs and chs[0]['start'] > 0:
        L.append('| 앞 | (앞붙이) | 1 | %d | %d | — | — |' % (chs[0]['start'], chs[0]['start']))
    for ch in chs:
        L.append('| %02d | %s | %d | %d | %d | %s | %s |' % (ch['num'], _cell(ch['title'])[:60], ch['start'] + 1, ch['end'] + 1,
                                                          ch['pages_n'], ch['printed'], ch['why']))
    if chs and chs[-1]['end'] < r['pages'] - 1:
        L.append('| 뒤 | (뒤붙이) | %d | %d | %d | — | — |' % (chs[-1]['end'] + 2, r['pages'], r['pages'] - chs[-1]['end'] - 1))
    L += ['', '## 2. 확인할 것 (%d)' % ck, '']
    L += ['- %s' % c for c in r['checks']] or ['없음']
    if 'heads' in (chs[0] if chs else {}):
        L += ['', '## 3. 근거 — 장마다 쪽 머리가 잡힌 PDF 쪽 (앞 12개)', '']
        L += ['- %02d장 (%d쪽): %s' % (ch['num'], len(ch['heads']), ', '.join(str(i + 1) for i in ch['heads'][:12])) for ch in chs]
    if r['depths']:
        L += ['', '## 4. 책갈피 깊이별 앞 8개 제목', '']
        L += ['- 깊이 %d (%d개): %s' % (d, r['depths'][d], ' · '.join(_cell(t)[:40] for t in ts)) for d, ts in r['outline_titles'].items()]
    return '\n'.join(L) + '\n'


def plan(folder, out, name, only=None, skip=(), recursive=False, level=None, budget=150, stream=sys.stdout):
    if BAD_NAME.search(name):
        raise SystemExit('[멈춤] --name 에 & / ? 같은 기호를 쓰지 않는다(전달 규약 §3): %s' % name)
    load_pypdf()
    sel = list_books(folder, only, skip, recursive, numbered=True)
    os.makedirs(out, exist_ok=True)
    todo = [(k, b) for k, b in sel if not os.path.exists(os.path.join(out, '%s_%02d.md' % (name, k)))]
    preflight(folder, [b for _, b in todo])
    t0, rate, done, left = time.time(), 0.08, 0, []
    for k, b in todo:
        path = os.path.join(folder, b)
        if done:
            try:
                est = len(load_pypdf().PdfReader(path, strict=False).pages) * rate
            except Exception:
                est = 0
            if time.time() - t0 + est > budget:
                left.append(b)
                continue
        print('[%02d] %s' % (k, b), file=stream, flush=True)
        # v0.3 (Cowork plan 3회 Killed): 책마다 하위 프로세스 — 메모리가 책마다 풀리고, 한 권이 죽어도 그 권만 오류로 남는다
        fp = os.path.join(out, '%s_%02d.md' % (name, k))
        t1 = time.time()
        cp = subprocess.run([sys.executable, os.path.abspath(__file__), '_plan_one', path, fp, str(k), b, name] +
                            (['--level', str(level)] if level is not None else []),
                            capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        if cp.returncode != 0 or not os.path.exists(fp):
            why = 'Killed(메모리 부족 추정)' if cp.returncode in (-9, 137) else 'rc=%d %s' % (
                cp.returncode, ((cp.stderr or '').strip().splitlines() or [''])[-1][:160])
            open(fp, 'w', encoding='utf8').write(plan_md(k, b, {'error': '하위 프로세스 실패 — %s. 다시 하려면 이 파일을 지우고 같은 명령' % why,
                                                               'seconds': round(time.time() - t1, 1), 'chapters': [], 'checks': []}, name))
        else:
            m = re.search(r'pages=(\d+)', open(fp, encoding='utf8').readline())
            if m and 'method=쪽' in open(fp, encoding='utf8').readline():
                rate = max(rate, (time.time() - t1) / float(m.group(1)))
        done += 1
    rows = []
    for k, b in sel:
        fp = os.path.join(out, '%s_%02d.md' % (name, k))
        if not os.path.exists(fp):
            rows.append('| %02d | %s | (남음) | | | | |' % (k, _cell(b)))
            continue
        m = re.match(r'<!-- plan: method=(.*?) chapters=(\d+) check=(\d+) pages=(\S+) seconds=(\S+) error=(\w+) -->',
                     open(fp, encoding='utf8').readline())
        if m:
            rows.append('| %02d | %s | %s | %s | %s | %s | %s |' % (k, _cell(b), '오류' if m.group(6) == 'yes' else m.group(1),
                                                                m.group(2), m.group(3), m.group(4), m.group(5)))
    S = ['# %s_요약' % name, '',
         '> textbook.py v%s plan · 폴더 `%s` · %d권. 책마다 `%s_{번호}.md` 의 장 표를 확인한다.' % (
             __version__, os.path.basename(os.path.normpath(folder)), len(sel), name),
         '> 남은 책이 있으면 **같은 명령을 다시** 돌린다 — 이미 쓴 책은 건너뛴다(Cowork 셸 180초 제한).', '',
         '| # | 파일 | 방법 | 장 | 확인 | 쪽 | 초 |', '|---|---|---|---|---|---|---|'] + rows
    S += ['', '이번 실행 %d권 · 남은 책 %d권 · %.0f 초' % (done, sum(1 for r in rows if '(남음)' in r), time.time() - t0), '']
    open(os.path.join(out, '%s_요약.md' % name), 'w', encoding='utf8').write('\n'.join(S))
    print('\n'.join(S), file=stream)
    return done, left


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    for cmd, word in (('probe', '교과서probe'), ('plan', '교과서plan')):
        p = sub.add_parser(cmd, help={'probe': '책마다 구조 조사 → md', 'plan': '책마다 장 표 제안 → md'}[cmd])
        p.add_argument('folder'); p.add_argument('--out', required=True)
        p.add_argument('--name', default=time.strftime('%y%m%d') + '_회신_Cowork→코드_%s_v1' % word)
        p.add_argument('--only', default=None, help='파일 이름에 이 글자가 든 PDF 만')
        p.add_argument('--skip', action='append', default=[], help='파일 이름에 이 글자가 든 PDF 는 뺀다(여러 번)')
        p.add_argument('--recursive', action='store_true', help='하위 폴더까지')
        if cmd == 'probe':
            p.add_argument('--front', type=int, default=40); p.add_argument('--samples', type=int, default=20)
        else:
            p.add_argument('--level', type=int, default=None, help='책갈피 깊이를 장으로 (--only 와 함께)')
            p.add_argument('--budget', type=float, default=150, help='이 초가 차면 멈춤 — 다시 돌리면 이어서')
    one = sub.add_parser('_plan_one', help=argparse.SUPPRESS)      # plan 이 책마다 부르는 하위 프로세스
    one.add_argument('path'); one.add_argument('md'); one.add_argument('k', type=int); one.add_argument('label'); one.add_argument('name')
    one.add_argument('--level', type=int, default=None)
    a = ap.parse_args()
    if a.cmd == '_plan_one':
        if os.environ.get('TEXTBOOK_TEST_KILL') and os.environ['TEXTBOOK_TEST_KILL'] in a.path:   # 시험용: 죽는 책 흉내
            os.kill(os.getpid(), signal.SIGKILL)
        open(a.md, 'w', encoding='utf8').write(plan_md(a.k, a.label, plan_book(a.path, a.level), a.name))
    elif a.cmd == 'probe':
        probe(a.folder, a.out, a.name, a.only, a.front, a.samples, skip=a.skip, recursive=a.recursive)
    else:
        plan(a.folder, a.out, a.name, a.only, a.skip, a.recursive, a.level, a.budget)
