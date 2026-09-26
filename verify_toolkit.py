#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_toolkit.py — 논문 원고 기계적 검증 툴킷
================================================
이 프로젝트(논문 원고) 작업 중 반복적으로 발생했던 실수들을 재현하지 않기 위해
"매번 다시 추론하지 말고 기계적으로 돌려야 하는 검사"를 한 파일에 모았습니다.

사용법
------
프로젝트 지식(project knowledge)에 이 파일을 업로드해 두면, 이후 대화에서
Claude가 /mnt/project/verify_toolkit.py 를 view로 읽고, 그 내용을
/home/claude/에 복사한 뒤 bash_tool로 바로 실행할 수 있습니다.

    python3 verify_toolkit.py all <파일.docx>          # 전체 검사
    python3 verify_toolkit.py trackchanges <파일.docx>  # 추적변경만
    python3 verify_toolkit.py highlight <파일.docx>     # 형광/한글 잔존만
    python3 verify_toolkit.py citations <파일.docx>     # 인용 순서/개수
    python3 verify_toolkit.py wordcount <파일.docx>     # 섹션별 단어수
    python3 verify_toolkit.py fixzoom <파일.docx>       # zoom 버그 수정 (덮어씀)
    python3 verify_toolkit.py fixbookmarks <파일.docx>  # bookmark 중복 제거 (덮어씀)
    python3 verify_toolkit.py figure <이미지.jpg>       # Figure 규격(dpi/inch) 확인
    python3 verify_toolkit.py wordcount <docx> [--from INTRODUCTION --to 'AI Disclosure']   # 구간 지정 가능(v1.3.1)
    python3 verify_toolkit.py images <docx>            # v1.2 내장 이미지 rId·크기·캡션·고아 여부
    python3 verify_toolkit.py notation <docx>          # v1.2 음수 구간 모호 표기·minus/하이픈 혼용
    python3 verify_toolkit.py renumber <docx> --remove 13,26 [-o out] [--dry-run]   # v1.2 재번호(보수 모드). --remove 13 26 도 됨

자동 테스트: python3 test_verify_toolkit.py (fixture 는 python-docx 로 생성, 실물 불필요)

다른 논문/다른 프로젝트에서 재사용하려면
----------------------------------------
아래 "PAPER-SPECIFIC CONFIG" 구간만 그 논문에 맞게 고치면 됩니다.
그 아래 함수들은 범용이라 손댈 필요가 없습니다.
"""

import re
import sys
import zipfile
import os
import shutil

__version__ = '1.3.3'   # TOOLS_MANIFEST 와 대조. 판이 오르면 test_verify_toolkit.EXPECT_VERSION 도 함께

# ══════════════════════════════════════════════════════════════
# PAPER-SPECIFIC CONFIG — 논문·학술지가 바뀌면 여기만 수정
# ══════════════════════════════════════════════════════════════
JOURNAL = "KJR"
BODY_WORD_LIMIT = 3000          # 본문 단어 한도
ABSTRACT_WORD_LIMIT = 300       # 초록 단어 한도
BODY_START_MARKER = "INTRODUCTION"
BODY_END_MARKER = "AI Disclosure"      # 이 마커 전까지가 "본문"
REFERENCES_MARKER = "REFERENCES"
FIGURE_MIN_DPI = 300
FIGURE_MIN_INCH = 3.0
FIGURE_MAX_INCH = 7.0
CITATION_PATTERN = r'\[[\d,\s\-]+\]'   # Vancouver 스타일 [1], [1,2], [1-3]
PVALUE_DECIMALS = 3
# ══════════════════════════════════════════════════════════════


# ---------- 1. 추적 변경(Track Changes) 감지 ----------
def scan_track_changes(path):
    """python-docx가 못 읽는 <w:ins>/<w:del>을 XML 레벨로 직접 찾는다.
    저자가 Word 추적변경으로 편집한 파일을 받았을 때 반드시 먼저 실행."""
    z = zipfile.ZipFile(path)
    doc = z.read('word/document.xml').decode('utf-8')
    ins_blocks = re.findall(r'<w:ins [^>]*>(.*?)</w:ins>', doc, re.S)
    del_blocks = re.findall(r'<w:del [^>]*>(.*?)</w:del>', doc, re.S)

    def texts(blocks, tag='w:t'):
        out = []
        for b in blocks:
            t = "".join(re.findall(rf'<{tag}[^>]*>([^<]*)</{tag}>', b))
            if t.strip():
                out.append(t)
        return out

    ins_texts = texts(ins_blocks, 'w:t')
    del_texts = texts(del_blocks, 'w:delText')
    kor_ins = [t for t in ins_texts if re.search(r'[가-힣]', t)]

    print(f"=== 추적 변경 스캔: {path} ===")
    print(f"  <w:ins> 삽입 블록: {len(ins_blocks)}개 (텍스트 있는 것 {len(ins_texts)}개)")
    print(f"  <w:del> 삭제 블록: {len(del_blocks)}개 (텍스트 있는 것 {len(del_texts)}개)")
    print(f"  한글 포함 삽입(=저자 지시문 가능성): {len(kor_ins)}개")
    for t in kor_ins[:10]:
        print(f"    • {t[:100]}")
    if ins_blocks or del_blocks:
        print("  ⚠ 이 파일은 추적 변경 상태입니다. p.text만 읽으면 이 내용을 놓칩니다.")
        print("    저자의 실제 수정(ins)과 지시문을 구분해서 처리하세요.")
    return {'ins': len(ins_blocks), 'del': len(del_blocks), 'korean_ins': kor_ins}


def accept_or_reject_changes(src, out, keep_korean_as_note=True):
    """추적변경 일괄 정리: 삭제(del)는 제거, 삽입(ins)은 한글이면 제거(지시문으로 간주)
    아니면 텍스트로 수용. 저장 전 반드시 결과를 재확인할 것 — 자동 판단이 항상 옳지는 않음."""
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.namelist():
        data = zin.read(item)
        if item == 'word/document.xml':
            s = data.decode('utf-8')
            s = re.sub(r'<w:del [^>]*>.*?</w:del>', '', s, flags=re.S)

            def handle_ins(m):
                inner = m.group(1)
                txt = "".join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', inner))
                if keep_korean_as_note and re.search(r'[가-힣]', txt):
                    return ''  # 한글 지시문 → 제거
                return inner  # 저자의 실제 수정 → 수용
            s = re.sub(r'<w:ins [^>]*>(.*?)</w:ins>', handle_ins, s, flags=re.S)
            s = s.replace('<w:delText', '<w:t').replace('</w:delText>', '</w:t>')
            data = s.encode('utf-8')
        zout.writestr(item, data)
    zin.close()
    zout.close()
    print(f"추적변경 정리 완료: {out}")
    print("⚠ 자동 처리 결과이니 diff로 실제 반영 여부를 다시 확인하세요.")


# ---------- 2. 형광·한글 잔존 스캔 (clean 버전 검증용) ----------
def scan_highlight_and_korean(path):
    """clean(제출용) 파일에 형광이나 한글이 남아있지 않은지 XML 레벨로 확인.
    python-docx는 중첩 표 안을 못 읽는 경우가 있어 반드시 XML로 검사."""
    z = zipfile.ZipFile(path)
    doc = z.read('word/document.xml').decode('utf-8')
    hl_count = len(re.findall(r'<w:highlight[^/]*/>', doc))
    texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', doc)
    kor = [t for t in texts if re.search(r'[가-힣]', t)]
    print(f"=== 형광/한글 스캔: {path} ===")
    print(f"  형광(<w:highlight>) run: {hl_count}개")
    print(f"  한글 포함 <w:t>: {len(kor)}개")
    for t in kor[:10]:
        print(f"    • {t[:80]}")
    ok = hl_count == 0 and len(kor) == 0
    print(f"  {'✓ 제출용으로 깨끗함' if ok else '⚠ 잔존물 있음 — clean 버전이면 문제'}")
    return {'highlight': hl_count, 'korean': len(kor)}


def strip_all_highlight(src, out):
    """모든 형광을 XML 레벨에서 제거 (표 안까지 포함)."""
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.namelist():
        data = zin.read(item)
        if item == 'word/document.xml':
            s = data.decode('utf-8')
            n = len(re.findall(r'<w:highlight[^/]*/>', s))
            s = re.sub(r'<w:highlight[^/]*/>', '', s)
            print(f"형광 {n}건 제거")
            data = s.encode('utf-8')
        zout.writestr(item, data)
    zin.close()
    zout.close()
    print(f"저장: {out}")


# ---------- 3. 인용 순서/개수 검증 (Vancouver) ----------
def check_citations(path, body_start=BODY_START_MARKER, refs_marker=REFERENCES_MARKER,
                     pattern=CITATION_PATTERN):
    """본문 인용이 [1]부터 순차로 이어지는지, 목록 수와 일치하는지 확인.
    주의: 한글 메모(〔수정〕 등)에 인용번호 예시가 들어가면 오탐하니
    본문 구간만 자르는 body_start/refs_marker 지정이 중요.

    **표는 읽지 않는다(의도).** KJR §4 는 인용 순서를 "본문에 나타나는 순서"로 규정하고 §5 는 표 각주에
    인용번호 규정을 두지 않으므로, 표 각주의 인용은 본문 등장순 검사 대상이 아니다(저자 260910 v2 §2 확인).
    표까지 넓히면 규정상 위반이 아닌 것을 위반으로 잡게 된다."""
    from docx import Document
    d = Document(path)
    paras = [p.text for p in d.paragraphs]
    try:
        i0 = next(i for i, t in enumerate(paras) if t.strip() == body_start)
        i1 = next(i for i, t in enumerate(paras) if t.strip() == refs_marker)
    except StopIteration:
        print("  ⚠ body_start 또는 refs_marker를 찾지 못했습니다. CONFIG 확인.")
        return None
    body_paras = [t for t in paras[i0:i1] if not re.search(r'[가-힣]', t)]  # 한글 메모 제외
    body = " ".join(body_paras)

    seq = []
    for c in re.findall(pattern, body):
        for part in c.strip('[]').split(','):
            part = part.strip()
            if '-' in part:
                a, b = part.split('-')
                seq += list(range(int(a), int(b) + 1))
            elif part.isdigit():
                seq.append(int(part))
    first = {}
    for n in seq:
        if n not in first:
            first[n] = len(first)
    order = sorted(first, key=lambda k: first[k])
    bad = [x for i, x in enumerate(order) if x != i + 1]

    # v1.2 (#1): 첫 위반 지점 — 연쇄 위반은 접고 원인 문단만
    first_bad = None
    if bad:
        pos = next(i for i, x in enumerate(order) if x != i + 1)
        n = order[pos]
        para = next((t for t in body_paras if re.search(r'\[[^\]]*\b%d\b[^\]]*\]' % n, t)), '')
        first_bad = {'nth': pos + 1, 'found': n, 'expected': pos + 1, 'para': para[:120]}

    refs = [t.strip() for t in paras[i1:] if re.match(r'^\d+\.\s+[A-Z]', t.strip())]  # v1.1: REFERENCES 이후만 센다

    print(f"=== 인용 검증: {path} ===")
    print(f"  본문 사용 문헌 수: {len(order)}")
    print(f"  REFERENCES 목록 수: {len(refs)}")
    print(f"  일치 여부: {'✓' if len(order) == len(refs) else '⚠ 불일치'}")
    print(f"  순서 위반: {len(bad)}건 {bad[:10] if bad else '(없음)'}")
    if first_bad:
        print(f"  첫 위반: 본문 {first_bad['nth']}번째 등장 [{first_bad['found']}] (기대 [{first_bad['expected']}]) — 문단 '{first_bad['para']}'")
        print(f"          그 뒤 {len(bad) - 1}건은 연쇄일 가능성이 큼. 이 지점부터 고치고 재실행.")
    missing = sorted(set(range(1, max(order) + 1)) - set(order)) if order else []
    print(f"  중간 결번: {missing if missing else '없음'}")
    return {'used': len(order), 'listed': len(refs), 'order_violations': bad, 'gaps': missing,
            'first_violation': first_bad}


class _PvalueResult(list):
    """위반 목록(list) + lowercase_p·thresholds 부가 정보. v1.3 이전 호출부와 호환."""
    def __new__(cls, bad, lower, thresholds):
        o = super().__new__(cls, bad); return o

    def __init__(self, bad, lower, thresholds):
        super().__init__(bad)
        self.violations = list(bad)
        self.lowercase_p = lower
        self.thresholds = thresholds


def _all_texts(path):
    """문단 + 표 셀 문단의 텍스트. v1.3 — 표 안 표기를 놓치던 결함(저자 260910 #4) 때문에 추가.
    중첩 표도 재귀로 읽는다."""
    from docx import Document
    d = Document(path)
    out = [p.text for p in d.paragraphs]

    def walk(tables):
        for t in tables:
            for row in t.rows:
                for c in row.cells:
                    out.extend(p.text for p in c.paragraphs)
                    if c.tables:
                        walk(c.tables)
    walk(d.tables)
    return out


# ---------- 4. 섹션별 단어수 ----------
def check_word_count(path, body_start=BODY_START_MARKER, body_end=BODY_END_MARKER,
                      body_limit=BODY_WORD_LIMIT, abstract_limit=ABSTRACT_WORD_LIMIT):
    """본문·초록 단어수. **표는 세지 않는다** — KJR Manuscript Types 각주가 title/abstract/keywords/
    references/tables/figure legends 를 제외하도록 규정(저자 260910 v2 §3 확인). `Document.paragraphs`
    만 읽는 현행이 규정과 맞으므로 v1.3 의 표 확장을 여기에는 적용하지 않는다.

    범위는 body_start ~ body_end 문단 사이다. 그 앞의 blinded title page·abstract·keywords 와
    그 뒤의 references·tables·figure legends 는 자연히 빠진다 — 다만 **body_end 마커가 본문 끝에
    있어야 한다.** 마커를 못 찾으면 body 는 None 이고 세지 않는다(추정하지 않는다).
    v1.3.1: body_start/body_end 를 CLI 에서 `--from`/`--to` 로 지정할 수 있다(감량 작업용).
    Word 공식 카운트와는 다를 수 있다 — 여기 수치는 상대 비교·감량 추적용이다."""
    from docx import Document
    d = Document(path)
    paras = [p.text for p in d.paragraphs]
    full = " ".join(paras)
    try:
        i0 = paras.index(body_start)
        i1 = paras.index(body_end)
        body_wc = sum(len(t.split()) for t in paras[i0:i1] if t.strip()
                       and not re.search(r'[가-힣]', t) and not re.match(r'^\d+\.\s+[A-Z]', t.strip()))
    except ValueError:
        body_wc = None
        print(f"  ⚠ 구간 마커를 찾지 못했습니다 (from={body_start!r} to={body_end!r}) — 본문 수를 세지 않았습니다")
    ab0, ab1 = full.find('Objective:'), full.find('Key Words:')
    ab_wc = len(full[ab0:ab1].split()) if ab0 > 0 and ab1 > 0 else None

    print(f"=== 단어수 검증 (표·참고문헌·figure legend 제외, KJR 규정): {path} ===")
    if body_wc is not None:
        print(f"  구간: {body_start!r} ~ {body_end!r}")
        flag = '✓' if body_wc <= body_limit else '⚠ 초과'
        print(f"  본문: {body_wc} / {body_limit}  {flag}")
    if ab_wc is not None:
        flag = '✓' if ab_wc <= abstract_limit else '⚠ 초과'
        print(f"  초록: {ab_wc} / {abstract_limit}  {flag}")
    return {'body': body_wc, 'abstract': ab_wc}


# ---------- 5. P값 소수점 자리수 ----------
def check_pvalue_format(path, decimals=PVALUE_DECIMALS):
    """실제 계산된 P값(P = 0.023 등)만 검사한다. P < 0.05 / P < 0.01 같은
    통상적 임계값 표기는 관례이므로 위반으로 잡지 않는다(이전 오탐 수정).
    v1.2 (#8): `<` 뒤 값은 전부 임계값(Bonferroni `P < 0.0045` 등)으로 보고 자릿수 검사에서 뺀다.
    v1.3 (저자 260910 #4): **표 안 문단도 읽는다.** v1.2.1 까지 `Document.paragraphs` 만 봐서 표에 든
    `P = 0.xxx` 를 통째로 놓쳤다(v47_clean 기준 22곳). 또 소문자 p 를 **라벨**로 세어 별도 키로 돌려준다 —
    실물 위반은 값(`p = 0.023`)이 아니라 열 머리 `(r/p)`·각주 `p-values` 였다.

    반환 {'violations': [...], 'lowercase_p': [(표기, 횟수)], 'thresholds': {...}}.
    호환: 반환값을 리스트처럼 순회·비교하던 호출부를 위해 list 를 상속한 자료형으로 돌려주며,
    그 리스트 내용은 종전과 같은 위반 목록이다.
    검사 범위: 값 검사는 대문자 P 와 `=` 만. `P > 0.05`·`P ≥ 0.05` 는 임계값 표기로 집계(v1.3.2), `P = 0.5` 처럼 자릿수 검사가 무의미한 표기는 제외.
    소문자 p 는 세기만 하고 위반으로 올리지 않는다(자동 수정 없음 — 표 헤더는 사람이 고친다)."""
    full = " ".join(_all_texts(path))
    bad, thresholds = [], {}
    for m in re.findall(r'P\s*[=<>≥≤]\s*0\.\d+', full):
        val = m.split('.')[-1]
        if '<' in m or '>' in m or '≥' in m or '≤' in m:   # v1.3.2: `>`·≥·≤ 도 임계값 표기로 집계(미검사 항목 해소)
            thresholds[re.sub(r'\s+', ' ', m)] = thresholds.get(re.sub(r'\s+', ' ', m), 0) + 1
            continue  # 임계값 표기는 통과 (v1.2: 목록 고정 없음)
        if len(val) != decimals:
            bad.append(m)
    lower = {}
    for pat in (r'\bp[-\s]?values?\b', r'\(\s*r\s*/\s*p\s*\)', r'\bp\s*[=<]\s*0?\.\d+'):
        for m in re.findall(pat, full, re.I):
            key = re.sub(r'\s+', ' ', m if isinstance(m, str) else m[0]).strip()
            if re.search(r'[A-Z]', key) and not re.search(r'\bp', key):
                continue
            if re.match(r'^P', key):      # 대문자 표기는 라벨 위반이 아니다
                continue
            lower[key] = lower.get(key, 0) + 1
    print(f"=== P값 형식 검증 (소수 {decimals}자리, `<` 임계값 표기 제외, 표 포함): {path} ===")
    print(f"  위반: {bad if bad else '없음'}")
    print(f"  `<` 임계값 표기 종류(눈검사): {thresholds if thresholds else '없음'}")
    print(f"  소문자 p 라벨(자동 수정 안 함): {sorted(lower.items()) if lower else '없음'}")
    return _PvalueResult(bad, sorted(lower.items()), thresholds)


# ---------- 6. docx 구조 버그 수정 ----------
def fix_zoom_bug(src, out=None):
    """python-docx로 새로 만든 docx가 <w:zoom w:val="bestFit"/>로 저장되어
    validate.py에서 percent 속성 누락 오류가 나는 문제를 고친다."""
    out = out or src
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(out + '.tmp', 'w', zipfile.ZIP_DEFLATED)
    fixed = False
    for item in zin.namelist():
        data = zin.read(item)
        if item == 'word/settings.xml':
            s = data.decode('utf-8')
            if 'w:zoom w:val="bestFit"' in s:
                s = s.replace('<w:zoom w:val="bestFit"/>', '<w:zoom w:percent="100"/>')
                fixed = True
            data = s.encode('utf-8')
        zout.writestr(item, data)
    zin.close()
    zout.close()
    shutil.move(out + '.tmp', out)
    print(f"zoom 버그 {'수정함' if fixed else '해당 없음(이미 정상)'}: {out}")


def dedupe_bookmarks(src, out=None):
    """copy.deepcopy로 문단을 복제할 때 bookmarkStart/End의 w:id가
    중복되어 validate.py가 실패하는 문제를 고친다. bookmark 자체를 제거."""
    out = out or src
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(out + '.tmp', 'w', zipfile.ZIP_DEFLATED)
    for item in zin.namelist():
        data = zin.read(item)
        if item == 'word/document.xml':
            s = data.decode('utf-8')
            s = re.sub(r'<w:bookmarkStart[^>]*/>', '', s)
            s = re.sub(r'<w:bookmarkEnd[^>]*/>', '', s)
            data = s.encode('utf-8')
        zout.writestr(item, data)
    zin.close()
    zout.close()
    shutil.move(out + '.tmp', out)
    print(f"bookmark 중복 제거 완료: {out}")


# ---------- 7. Figure 규격 (KJR: 300dpi, 3-7인치) ----------
def check_figure_spec(path, min_dpi=FIGURE_MIN_DPI, min_inch=FIGURE_MIN_INCH, max_inch=FIGURE_MAX_INCH):
    from PIL import Image
    im = Image.open(path)
    dpi = im.info.get('dpi', (72, 72))
    w_in, h_in = im.size[0] / dpi[0], im.size[1] / dpi[1]
    print(f"=== Figure 규격 검증: {path} ===")
    print(f"  픽셀: {im.size} | DPI: {dpi} | 인치: {w_in:.2f} x {h_in:.2f}")
    ok_dpi = dpi[0] >= min_dpi
    ok_size = (min_inch <= w_in <= max_inch) and (min_inch <= h_in <= max_inch)
    print(f"  DPI≥{min_dpi}: {'✓' if ok_dpi else '⚠'}  |  {min_inch}-{max_inch}인치 범위: {'✓' if ok_size else '⚠'}")
    return {'dpi': dpi, 'inch': (w_in, h_in), 'ok': ok_dpi and ok_size}


# ---------- 8. raw 데이터 대조 (범용 프레임) ----------
def verify_number_in_text(docx_path, csv_path, stated_value, region, indicator,
                           group=None, stat='median', tol=0.01):
    """원고에 적힌 수치가 raw CSV에서 재계산한 값과 일치하는지 확인.
    CSV 컬럼명 규칙이 '{region}_{indicator}' 형태라고 가정(이 프로젝트 스키마).
    다른 스키마의 논문이면 이 함수만 고치면 됨."""
    import csv
    import statistics as st
    rows = list(csv.DictReader(open(csv_path)))
    col = f'{region}_{indicator}'
    vals = [float(r[col]) for r in rows if group is None or int(float(r.get('Group', -1))) == group]
    calc = st.median(vals) if stat == 'median' else st.mean(vals)
    ok = abs(calc - stated_value) < tol
    print(f"  {'✓' if ok else '⚠'} {region} {indicator}: 원고={stated_value} raw({stat})={calc:.3f}")
    return ok


# ---------- 8. 내장 이미지 실체 확인 (v1.2, 도구회신 #3·#13) ----------
def list_images(path):
    """docx 안의 이미지마다 rId·미디어 파일명·픽셀 크기·본문 참조 여부·직전 문단(캡션 후보)을 나열한다.
    rId 순서 ≠ Figure 번호. document.xml 에서 참조되지 않는 미디어는 '고아'로 표시한다.
    반환: [{'rId','target','pixels','referenced','para_index','caption_before','caption_after'}]"""
    import io
    z = zipfile.ZipFile(path)
    rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
    doc = z.read('word/document.xml').decode('utf-8')
    rel_map = {}
    for m in re.finditer(r'<Relationship [^>]*?/>', rels):
        tag = m.group(0)
        rid = re.search(r'Id="([^"]+)"', tag); tgt = re.search(r'Target="([^"]+)"', tag)
        typ = re.search(r'Type="[^"]*/(\w+)"', tag)
        if rid and tgt and typ and typ.group(1) == 'image':
            rel_map[rid.group(1)] = tgt.group(1)
    paras = re.findall(r'<w:p\b.*?</w:p>', doc, re.S)
    ptext = [html_unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', pp))) for pp in paras]
    out = []
    for rid, tgt in sorted(rel_map.items(), key=lambda kv: int(re.sub(r'\D', '', kv[0]) or 0)):
        media = 'word/' + tgt if not tgt.startswith('/') else tgt.lstrip('/')
        pixels = None
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(z.read(media)))
            pixels = im.size
        except Exception:
            pass
        idx = next((i for i, pp in enumerate(paras) if 'r:embed="%s"' % rid in pp or "r:embed='%s'" % rid in pp), None)
        rec = {'rId': rid, 'target': tgt, 'pixels': pixels, 'referenced': idx is not None,
               'para_index': None if idx is None else idx + 1,
               'caption_before': None, 'caption_after': None}
        if idx is not None:
            before = next((ptext[j] for j in range(idx - 1, -1, -1) if ptext[j].strip()), '')
            after = next((ptext[j] for j in range(idx + 1, len(ptext)) if ptext[j].strip()), '')
            rec['caption_before'], rec['caption_after'] = before[:100], after[:100]
        out.append(rec)
    print(f"=== 내장 이미지: {path} ===")
    for r in out:
        flag = '' if r['referenced'] else '  ⚠ 고아(rels 에만 있고 본문 참조 없음)'
        print(f"  {r['rId']:6s} {r['target']:28s} {str(r['pixels']):14s} 문단 {r['para_index']}{flag}")
        if r['referenced']:
            print(f"         직전: {r['caption_before']!r}")
            print(f"         직후: {r['caption_after']!r}")
    orphans = [r['rId'] for r in out if not r['referenced']]
    print(f"  고아 이미지: {orphans if orphans else '없음'}")
    return out


def html_unescape(t):
    import html
    return html.unescape(t)


# ---------- 9. 표·본문 표기 검사 (v1.2, 도구회신 #11·#12) ----------
_MINUS = '\u2212'
_RANGE_AMBIG = re.compile(r'\(\s*(-?\d[\d.]*)\s*(--|-)\s*(-?\d[\d.]*)\s*\)')


def check_table_notation(path):
    """(a-b) 형 구간에 음수가 끼어 하이픈이 겹치는 모호 표기(`(-22.9--3.5)`, `(-16.3-2.1)`)와
    minus 기호(U+2212) vs 하이픈 혼용을 본문/표로 나눠 집계한다.
    반환 {'ambiguous': [(위치, 텍스트)], 'minus_body','hyphen_neg_body','minus_table','hyphen_neg_table'}"""
    from docx import Document
    d = Document(path)
    body = [p.text for p in d.paragraphs]
    cells = []
    for t in d.tables:
        for row in t.rows:
            for c in row.cells:
                cells.append(c.text)
    amb = []
    for where, texts in (('본문', body), ('표', cells)):
        for i, t in enumerate(texts):
            for m in _RANGE_AMBIG.finditer(t):
                a, sep, b = m.group(1), m.group(2), m.group(3)
                if sep == '--' or a.startswith('-') or b.startswith('-'):
                    amb.append((f'{where}#{i + 1}', m.group(0)))
    def counts(texts):
        s = ' '.join(texts)
        return len(re.findall(_MINUS + r'\d', s)), len(re.findall(r'(?<![\w.])-\d', s))
    mb, hb = counts(body); mt, ht = counts(cells)
    print(f"=== 표기 검사: {path} ===")
    print(f"  음수 구간 모호 표기: {len(amb)}건")
    for w, t in amb[:10]:
        print(f"    • {w}: {t}")
    print(f"  minus(U+2212) vs 하이픈-숫자: 본문 {mb}/{hb}, 표 {mt}/{ht}")
    if (mb and hb) or (mt and ht) or (mb and ht) or (hb and mt):
        print("  ⚠ 혼용 — 저널 규정에 맞춰 한 가지로 통일")
    return {'ambiguous': amb, 'minus_body': mb, 'hyphen_neg_body': hb, 'minus_table': mt, 'hyphen_neg_table': ht}


# ---------- 10. 참고문헌 재번호 — 보수 모드 (v1.2, 도구회신 #2) ----------
_CITE_RE = re.compile(r'\[(\d{1,3}(?:\s*[,\-\u2013]\s*\d{1,3})*)\]')


def _expand(cite):
    out = []
    for part in re.split(r'\s*,\s*', cite.strip()):
        if re.search(r'[\-\u2013]', part):
            a, b = re.split(r'\s*[\-\u2013]\s*', part)
            out += list(range(int(a), int(b) + 1))
        elif part.strip().isdigit():
            out.append(int(part))
    return out


def _compress(nums):
    nums = sorted(set(nums)); parts = []
    i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        parts.append(str(nums[i]) if j == i else (f'{nums[i]},{nums[j]}' if j == i + 1 else f'{nums[i]}-{nums[j]}'))
        i = j + 1
    return ','.join(parts)


def renumber_references(src, remove=(), out=None, body_start=BODY_START_MARKER, refs_marker=REFERENCES_MARKER,
                        body_end=BODY_END_MARKER, map_json=None, dry_run=False):
    """참고문헌 삭제 + 본문 첫 등장 순서로 재번호 + 인용 치환 + 목록 재배열을 한 번에.
    보수 모드: 다음 중 하나라도 걸리면 파일을 쓰지 않고 실패 사유·위치를 반환한다.
      (a) 인용 `[..]` 가 한 <w:t> 안에 온전히 있지 않음 (run 경계로 쪼개짐)
      (b) REFERENCES 목록 항목이 문단 하나가 아니거나, 항목 번호가 첫 <w:t> 에 온전히 없음
      (c) 본문에 삭제 대상 번호가 남아 있음 (사람이 먼저 인용을 지워야 함)
      (d) 본문 인용 번호가 목록 범위를 벗어남
    처리 범위: body_start ~ refs_marker 사이 문단 + 그 구간의 표. Supplementary 는 건드리지 않는다(독립 목록 가정).
    매핑 json: {"old": new 또는 null(삭제)} — 원본 번호 기준 한 단계.
    실행 후 check_citations 를 다시 돌려 0건인지 보고한다."""
    import json
    z = zipfile.ZipFile(src)
    doc = z.read('word/document.xml').decode('utf-8')
    remove = set(int(x) for x in remove)
    # 문단 블록 (표 안 문단 포함) — 순서 보존
    blocks = [(m.start(), m.end(), m.group(0)) for m in re.finditer(r'<w:p\b.*?</w:p>', doc, re.S)]
    texts = [html_unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', b[2]))) for b in blocks]
    def idx_of(marker):
        return next((i for i, t in enumerate(texts) if t.strip() == marker), None)
    i0, i1 = idx_of(body_start), idx_of(refs_marker)
    if i0 is None or i1 is None:
        return {'ok': False, 'reason': 'body_start/refs_marker 문단을 찾지 못함 — CONFIG 확인', 'where': []}
    i_end = idx_of(body_end)
    ref_end = i_end if (i_end is not None and i_end > i1) else len(blocks)
    problems = []

    # (a) 본문 인용이 <w:t> 안에 온전한가
    wt_re = re.compile(r'(<w:t(?:\s[^>]*)?>)([^<]*)(</w:t>)')
    body_cites_seq = []
    for i in range(i0, i1):
        t = texts[i]
        if re.search(r'[가-힣]', t):
            continue
        in_wt = ''.join(m.group(2) for m in wt_re.finditer(blocks[i][2]))
        whole = _CITE_RE.findall(html_unescape(t))
        inside = []
        for m in wt_re.finditer(blocks[i][2]):
            inside += _CITE_RE.findall(html_unescape(m.group(2)))
        if whole != inside:
            problems.append(('a', i + 1, t[:80]))
        for c in whole:
            body_cites_seq += _expand(c)

    # (b) 목록 항목
    ref_items = []  # (block_index, number)
    for i in range(i1 + 1, ref_end):
        t = texts[i].strip()
        m = re.match(r'^(\d+)\.\s+\S', t)
        if not m:
            continue
        first_wt = next((html_unescape(x.group(2)) for x in wt_re.finditer(blocks[i][2]) if x.group(2).strip()), '')
        if not re.match(r'^\s*%s\.' % m.group(1), first_wt):
            problems.append(('b', i + 1, t[:80]))
        ref_items.append((i, int(m.group(1))))
    listed = [n for _, n in ref_items]
    if listed != list(range(1, len(listed) + 1)):
        problems.append(('b', None, f'목록 번호가 1..N 연속이 아님: {listed[:12]}'))

    used = []
    for n in body_cites_seq:
        if n not in used:
            used.append(n)
    # (c)(d)
    still = sorted(remove & set(used))
    if still:
        problems.append(('c', None, f'삭제 대상 번호가 본문에 남아 있음: {still}'))
    beyond = sorted(set(used) - set(listed))
    if beyond:
        problems.append(('d', None, f'본문 인용이 목록에 없음: {beyond}'))
    if problems:
        print("⚠ 보수 모드 중단 — 파일을 쓰지 않았습니다.")
        for code, where, txt in problems:
            print(f"  ({code}) 문단 {where}: {txt}")
        return {'ok': False, 'reason': '전제 위반', 'where': problems}

    # 매핑: 본문 등장순 → 1..; 본문에 안 쓰인 목록 항목은 뒤에 원래 순서로
    keep_listed = [n for n in listed if n not in remove]
    unused = [n for n in keep_listed if n not in used]
    new_order = used + unused
    mapping = {n: (None if n in remove else new_order.index(n) + 1) for n in listed}

    def repl_cite(m):
        nums = [mapping[n] for n in _expand(m.group(1)) if n in mapping and mapping[n] is not None]
        return '[' + _compress(nums) + ']' if nums else ''
    def rewrite_wt(block):
        return wt_re.sub(lambda m: m.group(1) + _CITE_RE.sub(lambda c: repl_cite(c), m.group(2)) + m.group(3), block)

    new_blocks = list(blocks)
    for i in range(i0, i1):
        if re.search(r'[가-힣]', texts[i]):
            continue
        new_blocks[i] = (blocks[i][0], blocks[i][1], rewrite_wt(blocks[i][2]))
    # 목록 재배열: 항목 블록들을 새 순서로, 번호 텍스트 갱신
    item_blocks = {n: blocks[i][2] for i, n in ref_items}
    item_slots = [i for i, _ in ref_items]
    def renum_block(block, old, new):
        done = [False]
        def f(m):
            if done[0] or not m.group(2).strip():
                return m.group(0)
            done[0] = True
            return m.group(1) + re.sub(r'^(\s*)%d\.' % old, lambda mm: mm.group(1) + '%d.' % new, m.group(2), count=1) + m.group(3)
        return wt_re.sub(f, block)
    ordered = [(n, mapping[n]) for n in new_order]
    for slot, (old, new) in zip(item_slots, ordered):
        new_blocks[slot] = (blocks[slot][0], blocks[slot][1], renum_block(item_blocks[old], old, new))
    for slot in item_slots[len(ordered):]:
        new_blocks[slot] = (blocks[slot][0], blocks[slot][1], '')  # 삭제된 항목 자리 비움

    pieces, pos = [], 0
    for (s0, e0, _), (_, _, nb) in zip(blocks, new_blocks):
        pieces.append(doc[pos:s0]); pieces.append(nb); pos = e0
    pieces.append(doc[pos:])
    new_doc = ''.join(pieces)

    print(f"=== 재번호: {src} ===")
    print(f"  삭제 {sorted(remove)} / 목록 {len(listed)} → {len(new_order)} / 본문 사용 {len(used)} / 미사용 목록 {unused if unused else '없음'}")
    moved = {o: n for o, n in mapping.items() if n is not None and n != o}
    print(f"  번호 이동 {len(moved)}건: {dict(list(moved.items())[:12])}{' …' if len(moved) > 12 else ''}")
    if dry_run:
        return {'ok': True, 'dry_run': True, 'mapping': mapping, 'unused': unused}
    out = out or src.replace('.docx', '_renum.docx')
    zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    for item in z.namelist():
        zout.writestr(item, new_doc.encode('utf-8') if item == 'word/document.xml' else z.read(item))
    zout.close()
    map_json = map_json or out.replace('.docx', '_refmap.json')
    with open(map_json, 'w', encoding='utf8') as f:
        json.dump({'source': os.path.basename(src), 'removed': sorted(remove),
                   'map': {str(k): v for k, v in mapping.items()}}, f, ensure_ascii=False, indent=1)
    print(f"  저장: {out}\n  매핑: {map_json} (원본 번호 → 새 번호, null=삭제)")
    print("  재검사:")
    chk = check_citations(out, body_start=body_start, refs_marker=refs_marker)
    return {'ok': True, 'out': out, 'map_json': map_json, 'mapping': mapping, 'unused': unused, 'recheck': chk}


# ---------- 통합 실행 ----------
def run_all(path):
    print(f"\n{'='*60}\n전체 검증: {path}\n{'='*60}\n")
    scan_track_changes(path)
    print()
    scan_highlight_and_korean(path)
    print()
    check_citations(path)
    print()
    check_word_count(path)
    print()
    check_pvalue_format(path)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd, target = sys.argv[1], sys.argv[2]
    if cmd == 'all':
        run_all(target)
    elif cmd == 'trackchanges':
        scan_track_changes(target)
    elif cmd == 'highlight':
        scan_highlight_and_korean(target)
    elif cmd == 'citations':
        check_citations(target)
    elif cmd == 'wordcount':
        kw = {}
        if '--from' in sys.argv:
            kw['body_start'] = sys.argv[sys.argv.index('--from') + 1]
        if '--to' in sys.argv:
            kw['body_end'] = sys.argv[sys.argv.index('--to') + 1]
        check_word_count(target, **kw)
    elif cmd == 'pvalue':
        check_pvalue_format(target)
    elif cmd == 'fixzoom':
        fix_zoom_bug(target)
    elif cmd == 'fixbookmarks':
        dedupe_bookmarks(target)
    elif cmd == 'figure':
        check_figure_spec(target)
    elif cmd == 'images':
        list_images(target)
    elif cmd == 'notation':
        check_table_notation(target)
    elif cmd == 'renumber':
        # python3 verify_toolkit.py renumber <docx> --remove 13,26 [-o out.docx] [--dry-run]
        rm = []; o = None; dry = '--dry-run' in sys.argv
        if '--remove' in sys.argv:
            # v1.2.1: "--remove 13,26" 와 "--remove 13 26" 둘 다. (v1.2 는 콤마만 받아 두 번째 값을 버렸다 — 저자 실물검증 #2)
            for tok in sys.argv[sys.argv.index('--remove') + 1:]:
                if tok.startswith('-') and not tok.lstrip('-').isdigit():
                    break
                rm += [int(x) for x in tok.split(',') if x.strip().isdigit()]
        if '-o' in sys.argv:
            o = sys.argv[sys.argv.index('-o') + 1]
        r = renumber_references(target, remove=rm, out=o, dry_run=dry)
        sys.exit(0 if r.get('ok') else 1)
    else:
        print(f"알 수 없는 명령: {cmd}")
        print(__doc__)
