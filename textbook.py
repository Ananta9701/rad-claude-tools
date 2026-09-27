#!/usr/bin/env python3
"""textbook.py — 교과서 PDF 분할·색인 (1단계: 구조 조사 probe). 규약은 TEXTBOOK.md.

대화창의 Drive 연결은 큰 스캔 PDF 의 내용을 읽지 못한다(09-27 시험: 내용 빈칸). 그래서 분할 규칙을 정하기 전에
Cowork 가 Mac 동기화 폴더에서 책마다 구조를 조사해 md 로 남기고, 대화창이 그 md 를 읽어 규칙을 정한다.
원본 PDF 는 읽기만 한다 — 이 도구는 --out 폴더 밖에 아무것도 쓰지 않는다.

    python3 textbook.py probe 교과서폴더 --out 결과폴더 [--name 260927_회신_Cowork→코드_교과서probe_v1]
                              [--only 글자] [--front 40] [--samples 20]

결과: `{name}_요약.md`(책마다 한 줄 표) + `{name}_{NN}.md`(책마다: 책갈피 전체, 차례 후보 쪽 글자 전부, 앞부분 쪽 머리,
표본 쪽 글자 수, 쪽 번호 차이). pypdf 가 필요하다 — 없으면 설치 방법을 알리고 멈춘다.
"""
import argparse
import os
import re
import sys
import time
import unicodedata
from collections import Counter

__version__ = '0.1'   # TEXTBOOK.md 첫 줄·test_textbook.EXPECT_VERSION 과 함께 올린다

TOC_WORDS = re.compile(r'차\s*례|목\s*차|contents', re.I)
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


def probe(folder, out, name, only=None, front=40, samples=20, stream=sys.stdout):
    if BAD_NAME.search(name):
        raise SystemExit('[멈춤] --name 에 & / ? 같은 기호를 쓰지 않는다(전달 규약 §3): %s' % name)
    if not os.path.isdir(folder):
        raise SystemExit('[멈춤] 폴더가 없다: %s — Cowork 에 동기화 폴더를 연결했는지 본다' % folder)
    load_pypdf()
    nfc = lambda x: unicodedata.normalize('NFC', x)     # Mac 파일 이름은 한글이 NFD 로 올 수 있다
    books = sorted((f for f in os.listdir(folder) if f.lower().endswith('.pdf') and not f.startswith('.')
                    and (not only or nfc(only) in nfc(f))), key=nfc)
    if not books:
        raise SystemExit('[멈춤] %s 에 PDF 가 없다%s' % (folder, (' (--only %s)' % only) if only else ''))
    os.makedirs(out, exist_ok=True)
    if os.path.exists(os.path.join(out, '%s_요약.md' % name)):
        raise SystemExit('[멈춤] %s_요약.md 가 이미 있다 — 같은 이름을 다시 쓰지 않는다(규약 §3). --name 의 판을 올린다' % name)
    res = []
    for k, f in enumerate(books, 1):
        print('[%d/%d] %s' % (k, len(books), f), file=stream, flush=True)
        r = probe_book(os.path.join(folder, f), front, samples)
        res.append(r)
        open(os.path.join(out, '%s_%02d.md' % (name, k)), 'w', encoding='utf8').write(book_md(k, r, name))
    S = ['# %s_요약' % name, '',
         '> textbook.py v%s probe · 폴더 `%s` · PDF %d권 · 앞 %d쪽 + 본문 표본 %d쪽. 책마다 `%s_{번호}.md`.' % (
             __version__, os.path.basename(os.path.normpath(folder)), len(books), front, samples, name),
         '> 글자층 = 표본 쪽 중 50자 이상 나온 쪽. 쪽 번호 차이 = PDF 쪽 − 인쇄 쪽(최빈값, 맞은 수/찾은 수).', '',
         '| # | 파일 | MB | 쪽 | 책갈피 | 쪽 번호 표 | 글자층 | 차례 후보 | 쪽 번호 차이 | 만든 프로그램 |',
         '|---|---|---|---|---|---|---|---|---|---|']
    S += [summary_row(k, r) for k, r in enumerate(res, 1)]
    S += ['', '오류 %d권 · 조사 %.0f 초' % (sum(1 for r in res if r['error']), sum(r['seconds'] for r in res)), '']
    open(os.path.join(out, '%s_요약.md' % name), 'w', encoding='utf8').write('\n'.join(S))
    print('\n'.join(S), file=stream)
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('probe', help='책마다 구조 조사 → md')
    p.add_argument('folder'); p.add_argument('--out', required=True)
    p.add_argument('--name', default=time.strftime('%y%m%d') + '_회신_Cowork→코드_교과서probe_v1')
    p.add_argument('--only', default=None, help='파일 이름에 이 글자가 든 PDF 만')
    p.add_argument('--front', type=int, default=40); p.add_argument('--samples', type=int, default=20)
    a = ap.parse_args()
    if a.cmd == 'probe':
        probe(a.folder, a.out, a.name, a.only, a.front, a.samples)
