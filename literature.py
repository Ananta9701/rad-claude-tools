#!/usr/bin/env python3
"""literature.py — 논문 원문 받기·변환·찾기 (Cowork 「문헌」 역할). 규약은 LITERATURE.md.

리뷰어가 쓴 검증 지시(참고문헌 목록 + 확인할 주장 표)를 읽어, Cowork 가 받을 목록을 만들고, 받은 PDF 를 참고문헌에 짝지어
쪽 표지 붙은 md 로 바꿔 「문헌 보관소」에 DOI 별로 쌓고, 주장마다 원문 후보 문단을 찾아 둔다. **판정은 하지 않는다**(리뷰어 몫).
다운로드는 이 도구가 하지 않는다 — Cowork 가 브라우저로 한 편씩 받아 inbox 에 둔다(출판사 약관, LITERATURE.md §2).

    python3 literature.py plan   지시.md --out 작업폴더 [--store 보관소]     # 받을 목록(DOI·PubMed 링크·저장 이름·이미 있음)
    python3 literature.py ingest 지시.md --inbox 받은폴더 --store 보관소 --out 작업폴더
    python3 literature.py locate 지시.md --store 보관소 --out 작업폴더 [--top 3]
    python3 literature.py check  지시.md --inbox 받은폴더 [--store 보관소] [--out 작업폴더]   # 받은 파일 검사(%PDF·쪽 수·DOI·글자층·md 쪽 표지)
"""
import argparse
import datetime
import hashlib
import os
import re
import shutil
import sys
import unicodedata

__version__ = '0.3'   # LITERATURE.md 첫 줄·test_literature.EXPECT_VERSION 과 함께 올린다

DOI_RE = re.compile(r'\b(10\.\d{4,9}/[^\s"<>]+)', re.I)
PMID_RE = re.compile(r'\bPMID:?\s*(\d{5,9})\b', re.I)
PMC_RE = re.compile(r'\b(PMC\d{5,9})\b')
YEAR_RE = re.compile(r'\b(19[5-9]\d|20[0-4]\d)\b')
BAD_NAME = re.compile(r'[&/?\\:*"<>|→]')


def load_pypdf():
    try:
        import pypdf
        return pypdf
    except ImportError:
        if os.path.isdir('/tmp/pypdf/pypdf') or os.path.isdir(os.path.expanduser('~/pypdf/pypdf')):
            sys.path.insert(0, '/tmp/pypdf' if os.path.isdir('/tmp/pypdf/pypdf') else os.path.expanduser('~/pypdf'))
            import pypdf
            return pypdf
    raise SystemExit('[멈춤] pypdf 가 없다 — pip install --user pypdf, 또는 git clone -q --depth 1 https://github.com/py-pdf/pypdf ~/pypdf')


def _nfc(s):
    return unicodedata.normalize('NFC', s or '')


def _clean_doi(d):
    return d.rstrip('.,;)]').lower()


def doi_key(doi):
    return re.sub(r'[^0-9a-z._-]+', '_', _clean_doi(doi))


# ─────────────────────────── 지시 읽기 ───────────────────────────
def _section(text, head):
    m = re.search(r'^##\s*%s\s*$(.*?)(?=^##\s|\Z)' % re.escape(head), text, re.M | re.S)
    return m.group(1) if m else ''


def parse_refs(text):
    """'## 참고문헌' 아래 번호 붙은 줄 → [{n, raw, doi, pmid, pmc, year, author, title}]."""
    out = []
    cur = None
    for line in _section(text, '참고문헌').splitlines():
        m = re.match(r'^\s*\[?(\d{1,4})[\].)]\s+(.*\S)', line)
        if m:
            cur = {'n': int(m.group(1)), 'raw': m.group(2)}
            out.append(cur)
        elif cur and line.strip():
            cur['raw'] += ' ' + line.strip()
    for r in out:
        raw = r['raw']
        d = DOI_RE.search(raw); p = PMID_RE.search(raw); c = PMC_RE.search(raw)
        r['doi'] = _clean_doi(d.group(1)) if d else None
        r['pmid'] = p.group(1) if p else None
        r['pmc'] = c.group(1) if c else None
        ys = YEAR_RE.findall(raw)
        r['year'] = ys[0] if ys else ''
        parts = [q.strip() for q in re.split(r'\.\s+', raw) if q.strip()]
        r['author'] = re.split(r'[ ,]', parts[0])[0] if parts else ''
        r['title'] = parts[1] if len(parts) > 1 else ''
    return out


def parse_claims(text):
    """'## 확인할 주장' 표 → [{id, refs:[n], sentence, terms:[…]}]."""
    out = []
    for line in _section(text, '확인할 주장').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 4 or not cells[0] or cells[0] in ('주장',) or set(cells[0]) <= set('-: '):
            continue
        refs = [int(v) for v in re.findall(r'\d+', cells[1])]
        terms = [t.strip() for t in re.split(r'[,，;]', cells[3]) if t.strip()]
        out.append({'id': cells[0], 'refs': refs, 'sentence': cells[2], 'terms': terms})
    return out


def manuscript_name(text, path):
    m = re.search(r'^>\s*원고:\s*(.+?)\s*$', text, re.M)
    name = (m.group(1) if m else os.path.splitext(os.path.basename(path))[0]).strip()
    return re.sub(r'[\s&/?\\:*"<>|→]+', '_', _nfc(name))[:60]


def save_name(r):
    a = re.sub(r'[^0-9A-Za-z가-힣]+', '', _nfc(r['author']))[:20] or 'ref'
    return '%03d_%s_%s.pdf' % (r['n'], a, r['year'] or 'na')


# ─────────────────────────── 보관소 ───────────────────────────
def store_index(store):
    """보관소의 {doi: 폴더}, {폴더: meta} — 폴더마다 meta.md 첫 줄 '<!-- lit: doi=… -->'."""
    by_doi, meta = {}, {}
    if not os.path.isdir(store):
        return by_doi, meta
    for d in sorted(os.listdir(store)):
        mp = os.path.join(store, d, 'meta.md')
        if os.path.exists(mp):
            head = open(mp, encoding='utf8').readline()
            m = re.search(r'doi=(\S*)', head)
            meta[d] = head
            if m and m.group(1) not in ('', '-'):
                by_doi[m.group(1)] = d
    return by_doi, meta


def plan(instr_path, out, store=None, stream=sys.stdout):
    text = _nfc(open(instr_path, encoding='utf8').read())
    refs, claims = parse_refs(text), parse_claims(text)
    if not refs:
        raise SystemExit('[멈춤] 지시에 "## 참고문헌" 번호 목록이 없다')
    name = manuscript_name(text, instr_path)
    by_doi, _ = store_index(store) if store else ({}, {})
    need = {n for c in claims for n in c['refs']}
    os.makedirs(out, exist_ok=True)
    L = ['# %s — 받을 목록' % name, '',
         '> literature.py v%s plan · 참고문헌 %d · 확인할 주장 %d(원문이 필요한 문헌 %d). **한 편씩, 사이를 두고** 받는다 — '
         '찾을 곳은 적힌 순서대로(doi.org 먼저). 쿠키 배너는 "필수만/거부" 로 먼저 닫고, PDF 가 안 뜨면 30–60 초 기다려 최대 3 번, '
         '로봇 확인·접속 제한이 뜨면 멈추고 주소·화면·배너 처리를 적어 알린다(LITERATURE.md §2).' % (
             __version__, len(refs), len(claims), len(need)),
         '> 받은 PDF 는 아래 **저장 이름**으로 inbox 에. 이름이 달라도 DOI·제목으로 짝짓지만, 이름이 가장 확실하다.', '',
         '| 번호 | 첫 저자·해 | 주장 | DOI | 찾을 곳 | 저장 이름 | 보관소 |', '|---|---|---|---|---|---|---|']
    n_have = 0
    for r in refs:
        links = []
        # v0.2 (리뷰어 09-28): doi.org(출판사)는 캡차 없이 열렸고 PubMed·PMC 는 캡차 — doi.org 먼저, PMC 는 그다음, PubMed 는 둘 다 없을 때만
        if r['doi']:
            links.append('https://doi.org/%s' % r['doi'])
        if r['pmc']:
            links.append('(안 되면) https://www.ncbi.nlm.nih.gov/pmc/articles/%s/' % r['pmc'])
        if r['pmid'] and not r['doi'] and not r['pmc']:
            links.append('https://pubmed.ncbi.nlm.nih.gov/%s/' % r['pmid'])
        if not links:
            links.append('PubMed 에서 제목으로: %s' % (r['title'][:60] or r['raw'][:60]))
        have = by_doi.get(r['doi']) if r['doi'] else None
        n_have += bool(have)
        L.append('| %d | %s %s | %s | %s | %s | `%s` | %s |' % (
            r['n'], r['author'], r['year'], '○' if r['n'] in need else '', r['doi'] or '—', ' · '.join(links), save_name(r),
            ('있음 `%s`' % have) if have else ''))
    L += ['', '받을 것: %d편(이미 보관소에 %d편). 원문이 필요한 문헌(주장 ○)을 먼저.' % (len(refs) - n_have, n_have), '']
    fp = os.path.join(out, '%s_받을목록.md' % name)
    open(fp, 'w', encoding='utf8').write('\n'.join(L))
    print('\n'.join(L), file=stream)
    return fp


# ─────────────────────────── 받은 PDF → 보관소 ───────────────────────────
def _pdf_pages(path):
    pypdf = load_pypdf()
    rd = pypdf.PdfReader(path, strict=False)
    labels = None
    try:
        if '/PageLabels' in rd.trailer['/Root'].get_object():
            labels = rd.page_labels
    except Exception:
        labels = None
    pages = []
    for k, pg in enumerate(rd.pages):
        try:
            t = pg.extract_text() or ''
        except Exception:
            t = ''
        pages.append((k + 1, labels[k] if labels else None, t.strip()))
    return pages


BOILER = [re.compile(p_, re.I | re.M) for p_ in (
    r'^.*Downloaded from https?://\S+.*$',                       # Wiley 등 — 쪽마다 기관·날짜가 든 다운로드 안내
    r'^.*See the Terms and Conditions.*$',
    r'^.*Wiley Online Library for rules of use.*$',
    r'^.*OA articles are governed by the applicable Creative Commons License.*$')]


def _strip_boiler(t):
    """v0.2 (문헌 Cowork 시험 v2): 쪽마다 붙는 출판사 다운로드 안내 줄을 뺀다(위치 찾기의 잡음, 기관 이름). 반환 (글, 뺀 줄 수)."""
    n = 0
    for p_ in BOILER:
        t, k = p_.subn('', t)
        n += k
    return re.sub(r'\n{3,}', '\n\n', t).strip(), n


def _tokens(s):
    return {w for w in re.findall(r'[0-9a-z가-힣]{3,}', _nfc(s).lower())}


def match_pdf(fname, pages, refs):
    """받은 PDF 하나 → (참고문헌, 근거) — 파일 이름 번호 → 앞 두 쪽의 DOI → 제목 낱말 겹침 60% 이상."""
    m = re.match(r'^(\d{1,4})_', fname)
    if m:
        r = next((q for q in refs if q['n'] == int(m.group(1))), None)
        if r:
            return r, '파일 이름'
    head = ' '.join(t for _, _, t in pages[:2])
    for d in DOI_RE.findall(head):
        r = next((q for q in refs if q['doi'] and q['doi'] == _clean_doi(d)), None)
        if r:
            return r, 'DOI'
    ht = _tokens(head)
    best, score = None, 0.0
    for q in refs:
        tt = _tokens(q['title'])
        if len(tt) >= 3:
            s = len(tt & ht) / float(len(tt))
            if s > score:
                best, score = q, s
    if best and score >= 0.6:
        return best, '제목 %d%%' % int(score * 100)
    return None, ''


def ingest(instr_path, inbox, store, out, stream=sys.stdout):
    text = _nfc(open(instr_path, encoding='utf8').read())
    refs = parse_refs(text)
    name = manuscript_name(text, instr_path)
    if not os.path.isdir(inbox):
        raise SystemExit('[멈춤] inbox 폴더가 없다: %s' % inbox)
    os.makedirs(store, exist_ok=True); os.makedirs(out, exist_ok=True)
    by_doi, _ = store_index(store)
    got, unmatched = {}, []
    for f in sorted(os.listdir(inbox)):
        if not f.lower().endswith('.pdf') or f.startswith('.'):
            continue
        path = os.path.join(inbox, f)
        try:
            pages = _pdf_pages(path)
        except Exception as e:
            unmatched.append((f, '읽지 못함 %s' % type(e).__name__)); continue
        r, why = match_pdf(f, pages, refs)
        if not r:
            unmatched.append((f, '짝 없음')); continue
        doi = r['doi']
        if not doi:        # 참고문헌에 DOI 가 없으면 PDF 앞쪽에서
            d = DOI_RE.search(' '.join(t for _, _, t in pages[:2]))
            doi = _clean_doi(d.group(1)) if d else None
        key = by_doi.get(doi) if doi else None
        new = key is None
        if new:
            key = doi_key(doi) if doi else 'nodoi_%s' % hashlib.sha256(open(path, 'rb').read()).hexdigest()[:12]
            dd = os.path.join(store, key); os.makedirs(dd, exist_ok=True)
            shutil.copyfile(path, os.path.join(dd, 'paper.pdf'))
            L = ['# %s' % (r['title'] or r['raw'][:80]), '',
                 '> 원문 PDF 의 글자층(literature.py v%s). 쪽 표지 `[p.PDF쪽 · 인쇄쪽]`. 인용 문구는 이 md 로 찾고, 표·그림은 `paper.pdf` 로 확인한다.' % __version__, '']
            blank = boiler = 0
            for k, lab, t in pages:
                t, nb = _strip_boiler(t); boiler += nb
                L += ['[p.%d%s]' % (k, (' · %s' % lab) if lab and lab != str(k) else ''), '', t or '(글자층 없음 — 스캔 쪽)', '']
                blank += not t
            if boiler:
                L.insert(3, '> 출판사 다운로드 안내 줄 %d개를 뺐다(쪽마다 붙는 기관·날짜 줄).' % boiler)
            md = '\n'.join(L) + '\n'
            open(os.path.join(dd, 'paper.md'), 'w', encoding='utf8').write(md)
            open(os.path.join(dd, 'meta.md'), 'w', encoding='utf8').write(
                '<!-- lit: doi=%s pages=%d blank=%d sha=%s -->\n# %s\n\n- DOI: %s\n- 첫 저자·해: %s %s\n- 참고문헌: %s\n- 받은 날: %s\n- 원 파일 이름: `%s`\n'
                '- 원 PDF: sha256 앞 16자 `%s` · %d쪽 · 글자층 없는 쪽 %d · paper.md 쪽 표지 %d(= 쪽 수여야 한다)\n' % (
                    doi or '-', len(pages), blank, hashlib.sha256(open(path, 'rb').read()).hexdigest()[:16], r['title'] or r['raw'][:80],
                    doi or '—', r['author'], r['year'], r['raw'][:300], datetime.date.today().isoformat(), f,
                    hashlib.sha256(open(path, 'rb').read()).hexdigest()[:16], len(pages), blank, md.count('\n[p.')))
            if doi:
                by_doi[doi] = key
        _cite_note(store, key, name, r['n'])
        got[r['n']] = (key, why, new)
    rows = []
    for r in refs:
        g = got.get(r['n'])
        if not g and r['doi'] and r['doi'] in by_doi:        # 전에 받아 둔 것
            g = (by_doi[r['doi']], '보관소에 있음', False)
            _cite_note(store, g[0], name, r['n'])
        rows.append('| %d | %s %s | %s | %s |' % (r['n'], r['author'], r['year'], r['doi'] or '—',
                                                 ('`%s/paper.md` (%s%s)' % (g[0], g[1], ', 새로' if g[2] else '')) if g else '**못 받음**'))
    L = ['# %s — 문헌 목록' % name, '',
         '> literature.py v%s ingest · 보관소 `%s`. 못 받은 문헌은 리뷰어가 REVIEW_PROTOCOL 의 입수 불가 문헌으로 처리한다.' % (
             __version__, os.path.basename(os.path.normpath(store))), '',
         '| 번호 | 첫 저자·해 | DOI | 원문 |', '|---|---|---|---|'] + rows
    if unmatched:
        L += ['', '## 짝짓지 못한 PDF', ''] + ['- `%s` — %s' % u for u in unmatched]
    L += ['', '받음 %d / %d · 짝 없는 PDF %d' % (sum(1 for x in rows if '못 받음' not in x), len(refs), len(unmatched)), '']
    fp = os.path.join(out, '%s_문헌목록.md' % name)
    open(fp, 'w', encoding='utf8').write('\n'.join(L))
    _write_store_index(store)
    print('\n'.join(L), file=stream)
    return got, unmatched


def _cite_note(store, key, name, n):
    mp = os.path.join(store, key, 'meta.md')
    line = '- 인용: %s 참고문헌 %d' % (name, n)
    t = open(mp, encoding='utf8').read()
    if line not in t:
        open(mp, 'a', encoding='utf8').write(line + '\n')


def _write_store_index(store):
    rows = []
    for d in sorted(os.listdir(store)):
        mp = os.path.join(store, d, 'meta.md')
        if not os.path.exists(mp):
            continue
        t = open(mp, encoding='utf8').read()
        head = re.search(r'doi=(\S+) pages=(\d+) blank=(\d+)', t)
        title = (re.search(r'^# (.+)$', t, re.M) or [None, ''])[1]
        cites = re.findall(r'^- 인용: (.+)$', t, re.M)
        rows.append('| `%s` | %s | %s | %s | %s |' % (d, head.group(1) if head else '—', title[:70].replace('|', '/'),
                                                     head.group(2) if head else '', '; '.join(cites)[:120]))
    L = ['# 문헌 보관소 — INDEX', '', '> literature.py v%s. 폴더마다 `paper.pdf`(원문)·`paper.md`(글자층, 쪽 표지)·`meta.md`. 대화창은 이 INDEX → paper.md.' % __version__,
         '> **공유하지 않는다·GitHub 에 올리지 않는다**(출판사 원문).', '',
         '| 폴더 | DOI | 제목 | 쪽 | 인용한 원고 |', '|---|---|---|---|---|'] + rows
    open(os.path.join(store, 'INDEX.md'), 'w', encoding='utf8').write('\n'.join(L) + '\n')


# ─────────────────────────── 주장 → 원문 후보 문단 ───────────────────────────
def _term_re(term):
    core = re.sub(r'\s+', '', _nfc(term))
    return re.compile(r'\s*'.join(map(re.escape, core)), re.I)


def locate(instr_path, store, out, top=3, stream=sys.stdout):
    """주장마다 그 문헌 paper.md 에서 '찾을 말' 이 가장 많이 든 문단 top 개(쪽 표지와 함께). 판정은 하지 않는다."""
    text = _nfc(open(instr_path, encoding='utf8').read())
    refs, claims = parse_refs(text), parse_claims(text)
    name = manuscript_name(text, instr_path)
    by_doi, _ = store_index(store)
    ref_key = {}
    for r in refs:
        if r['doi'] and r['doi'] in by_doi:
            ref_key[r['n']] = by_doi[r['doi']]
    for d in (os.listdir(store) if os.path.isdir(store) else []):       # DOI 없는 문헌: meta 의 '인용' 줄로
        mp = os.path.join(store, d, 'meta.md')
        if os.path.exists(mp):
            for m in re.finditer(r'^- 인용: %s 참고문헌 (\d+)$' % re.escape(name), open(mp, encoding='utf8').read(), re.M):
                ref_key.setdefault(int(m.group(1)), d)
    L = ['# %s — 주장별 원문 후보' % name, '',
         '> literature.py v%s locate. 주장마다 그 문헌 원문에서 "찾을 말" 이 가장 많이 든 문단(띄어쓰기·대소문자 무시). '
         '**맞는지 판정은 리뷰어가 한다** — 후보가 없거나 낱말만 겹칠 수 있다.' % __version__, '']
    for c in claims:
        L += ['## %s — 문헌 %s' % (c['id'], ', '.join(map(str, c['refs'])) or '?'), '', '원고: %s' % c['sentence'],
              '찾을 말: %s' % ', '.join(c['terms']), '']
        pats = [(t, _term_re(t)) for t in c['terms']]
        for n in c['refs'] or []:
            key = ref_key.get(n)
            if not key or not os.path.exists(os.path.join(store, key, 'paper.md')):
                L += ['- 문헌 %d: **원문 없음**(못 받음 — 입수 불가 문헌으로)' % n, '']; continue
            md = open(os.path.join(store, key, 'paper.md'), encoding='utf8').read()
            parts = re.split(r'^(\[p\.[^\]]*\])$', md, flags=re.M)
            cands = []
            for k in range(1, len(parts) - 1, 2):
                mark = parts[k]
                for para in re.split(r'\n\s*\n|(?<=[.:])\n', parts[k + 1]):
                    flat = re.sub(r'\s+', ' ', para).strip()
                    if len(flat) < 20:
                        continue
                    hit = [t for t, p in pats if p.search(flat)]
                    if hit:
                        cands.append((len(hit), mark, hit, flat))
            # v0.2 (리뷰어 09-28): 원문 전체에서 한 번도 안 나온 말 — 원문 검증에서 가장 강한 신호
            whole = re.sub(r'\s+', ' ', md)
            zero = [t for t, p in pats if not p.search(whole)]
            order = list(cands)
            cands.sort(key=lambda z: -z[0])
            L.append('- 문헌 %d `%s/paper.md`:' % (n, key))
            L.append('  - **원문 전체에서 0회: %s**' % (', '.join(zero) if zero else '없음(찾을 말이 모두 한 번 이상 나온다)'))
            if not cands:
                L += ['  - 찾을 말이 든 문단 없음 — 원문을 직접 본다', '']; continue
            for sc, mark, hit, flat in cands[:top]:
                L.append('  - %s 맞은 말 %d/%d(%s): %s' % (mark, sc, len(pats), ', '.join(hit), flat[:400] + ('…' if len(flat) > 400 else '')))
            # v0.2: 찾을 말마다 따로 — 여러 요소를 한 주장에 담으면 초록·결론만 위로 올라와 요소별 근거 자리가 밀린다
            if len(pats) > 1:
                L.append('  - 찾을 말별 첫 자리(요약 문단 편향을 피해 — 같은 문단이 여러 말에 걸리면 한 번만):')
                shown = set()
                for t, p in pats:
                    first = next(((mark, flat) for _, mark, hit, flat in order if t in hit), None)
                    if not first:
                        continue
                    if first[1] in shown:
                        L.append('    - "%s" → 위와 같은 문단 %s' % (t, first[0])); continue
                    shown.add(first[1])
                    m_ = p.search(first[1]); a_ = max(0, m_.start() - 120)
                    L.append('    - "%s" → %s …%s…' % (t, first[0], first[1][a_:m_.end() + 160]))
            L.append('')
    os.makedirs(out, exist_ok=True)
    fp = os.path.join(out, '%s_주장위치.md' % name)
    open(fp, 'w', encoding='utf8').write('\n'.join(L) + '\n')
    print('\n'.join(L), file=stream)
    return fp


def check(instr_path, inbox, out=None, stream=sys.stdout, store=None):
    """v0.2 (리뷰어 09-28 받기 규칙 5): 받은 파일 검사 — 첫 바이트 %PDF(HTML 을 PDF 이름으로 저장한 것 거르기), 쪽 수 > 1,
    앞 두 쪽의 DOI 가 그 참고문헌(파일 이름 번호)의 DOI 와 같은지. 반환 [(파일, 결과, 까닭)]."""
    text = _nfc(open(instr_path, encoding='utf8').read())
    refs = parse_refs(text); name = manuscript_name(text, instr_path)
    rows = []
    for f in sorted(os.listdir(inbox)) if os.path.isdir(inbox) else []:
        if f.startswith('.') or not f.lower().endswith('.pdf'):
            continue
        path = os.path.join(inbox, f)
        head = open(path, 'rb').read(5)
        if not head.startswith(b'%PDF'):
            rows.append((f, '✗', 'PDF 가 아니다(첫 바이트 %r) — 뷰어·로그인 화면을 저장했을 수 있다' % head)); continue
        try:
            pages = _pdf_pages(path)
        except Exception as e:
            rows.append((f, '✗', '읽지 못함 %s' % type(e).__name__)); continue
        if len(pages) <= 1:
            rows.append((f, '✗', '쪽 수 %d — 초록·첫 쪽만 받았을 수 있다' % len(pages))); continue
        blank = sum(1 for _, _, t in pages if not t)
        if blank * 2 >= len(pages):     # v0.3 (리뷰어 09-28): 스캔본 — md 로 판정할 수 없다
            rows.append((f, '✗', '%d쪽 중 %d쪽 글자층 없음(스캔) — **PDF 필요**' % (len(pages), blank))); continue
        r, how = match_pdf(f, pages, refs)          # v0.2: 사용자가 받은 이름(저장 이름이 아닌 것)도 DOI·제목으로
        dois = {_clean_doi(d) for d in DOI_RE.findall(' '.join(t for _, _, t in pages[:2]))}
        if not r:
            rows.append((f, '△', '%d쪽 · 참고문헌과 짝짓지 못함(이름·DOI·제목) — 무슨 논문인지 확인' % len(pages))); continue
        if r and r['doi'] and dois and r['doi'] not in dois:
            rows.append((f, '△', '%d쪽 · 앞쪽 DOI %s ≠ 참고문헌 %d 의 %s — 다른 논문일 수 있다' % (len(pages), ', '.join(sorted(dois))[:60], r['n'], r['doi'])))
        elif r and r['doi'] and not dois:
            rows.append((f, '△', '%d쪽 · 앞쪽에 DOI 가 없다 — 제목으로 확인' % len(pages)))
        else:
            note = (' · 글자층 없는 쪽 %d' % blank) if blank else ''
            # v0.3 (리뷰어 09-28): 보관소 paper.md 의 쪽 표지 수 = PDF 쪽 수 — md 가 잘리면 '0회' 판정이 거짓이 된다
            if store and r['doi']:
                by_doi, _ = store_index(store)
                key = by_doi.get(r['doi'])
                mdp = os.path.join(store, key, 'paper.md') if key else None
                if mdp and os.path.exists(mdp):
                    nm = open(mdp, encoding='utf8').read().count('\n[p.')
                    if nm != len(pages):
                        rows.append((f, '✗', '%d쪽인데 보관소 paper.md 쪽 표지 %d — md 가 잘렸다(다시 ingest)' % (len(pages), nm))); continue
                    note += ' · paper.md 쪽 표지 %d = 쪽 수' % nm
            rows.append((f, '○', '%d쪽 · 참고문헌 %d(%s)%s%s' % (len(pages), r['n'], how, ' · DOI 맞음' if r['doi'] in dois else '', note)))
    L = ['# %s — 받은 파일 검사' % name, '', '| 파일 | 결과 | 까닭 |', '|---|---|---|'] + ['| `%s` | %s | %s |' % r_ for r_ in rows]
    L += ['', '○ %d · △ %d · ✗ %d' % tuple(sum(1 for r_ in rows if r_[1] == k) for k in '○△✗'), '']
    if out:
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, '%s_받은파일검사.md' % name), 'w', encoding='utf8').write('\n'.join(L))
    print('\n'.join(L), file=stream)
    return rows


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('plan'); p.add_argument('instr'); p.add_argument('--out', required=True); p.add_argument('--store', default=None)
    g = sub.add_parser('ingest'); g.add_argument('instr'); g.add_argument('--inbox', required=True); g.add_argument('--store', required=True)
    g.add_argument('--out', required=True)
    l_ = sub.add_parser('locate'); l_.add_argument('instr'); l_.add_argument('--store', required=True); l_.add_argument('--out', required=True)
    l_.add_argument('--top', type=int, default=3)
    c_ = sub.add_parser('check'); c_.add_argument('instr'); c_.add_argument('--inbox', required=True); c_.add_argument('--out', default=None)
    c_.add_argument('--store', default=None, help='보관소 — 있으면 paper.md 쪽 표지 수를 PDF 쪽 수와 대조(v0.3)')
    a = ap.parse_args()
    if a.cmd == 'plan':
        plan(a.instr, a.out, a.store)
    elif a.cmd == 'ingest':
        ingest(a.instr, a.inbox, a.store, a.out)
    elif a.cmd == 'check':
        rows = check(a.instr, a.inbox, a.out, store=a.store)
        sys.exit(1 if any(r[1] == '✗' for r in rows) else 0)
    else:
        locate(a.instr, a.store, a.out, a.top)
