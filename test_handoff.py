#!/usr/bin/env python3
"""handoff.py 테스트 — python3 test_handoff.py (pytest 불필요)."""
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import handoff as H          # noqa: E402
import deck_toolkit as T     # noqa: E402

EXPECT_VERSION = '1.3'
TMP = tempfile.mkdtemp(prefix='th_')


def _manifest_version(fname):
    p = os.path.join(HERE, 'TOOLS_MANIFEST.md')
    if not os.path.exists(p):
        return None
    m = re.search(r'\| `%s` \| v([0-9.]+)' % re.escape(fname), open(p, encoding='utf8').read())
    return m.group(1) if m else None


HEAD = '# 260924_전평대본_시험_v1\n\n> 발신: 영상의학 → 수신: 발표\n> 날짜: 2026-09-24 · 유형: 대본 넘김(v1) · 기준: **시험 v1 pptx**(%d화면) — 화면 번호는 v1 기준\n\n## 0. 요약\n| 항목 | 내용 |\n|---|---|\n| x | y |\n\n---\n\n'


def doc(body, n=10):
    return HEAD % n + body


def errs(d):
    return [p for p in d['problems'] if p[0] == '오류']


def warns(d):
    return [p for p in d['problems'] if p[0] == '경고']


def t_version():
    assert H.__version__ == EXPECT_VERSION
    mv = _manifest_version('handoff.py')
    assert mv is None or mv == H.__version__, ('TOOLS_MANIFEST.md 의 판', mv, '코드', H.__version__)
    first = open(os.path.join(HERE, 'HANDOFF_FORMAT.md'), encoding='utf8').readline()
    assert 'v%s' % H.__version__ in first, first


def t_minimal_ok():
    d = H.parse(doc('### 화면 1 — 표지\n작업: 없음\n대본:\n첫 문장.\n둘째 문장.\n참고: 없음\n\n### 화면 2 — Q. 진단은? (25-01)\n작업: 없음\n대본: 변경 없음 (v0 그대로)\n참고: 변경 없음\n'))
    assert not d['problems'], d['problems']
    assert d['base'] == '시험 v1 pptx' and d['screens_n'] == 10
    assert d['screens'][1]['script'] == ['첫 문장.', '둘째 문장.'] and d['screens'][1]['tips'] == 'NONE'
    assert d['screens'][2]['script'] == 'KEEP' and d['screens'][2]['tips'] == 'KEEP'


def t_required_blocks_and_unknown_lines():
    d = H.parse(doc('### 화면 1 — 표지\n대본:\n문장.\n\n### 화면 2 — x\n작업: 없음\n참고: 없음\n\n### 화면 3 — y\n작업: 없음\n아무 줄\n대본:\n문장\n참고: 없음\n'))
    msgs = ' / '.join(p[2] for p in errs(d))
    assert '"작업:" 줄이 없다' in msgs and '"참고:" 가 없다' in msgs and '"대본:" 이 없다' in msgs and '문법에 없는 줄' in msgs, msgs
    d = H.parse('# x\n\n### 화면 1 — a\n작업: 없음\n대본:\nx\n참고: 없음\n')
    assert any('기준 덱이 없다' in p[2] for p in errs(d))


def t_d2_same_line_script_kept():
    # D2: '대본: 첫 문장' 을 버리던 사고 — 받고 경고
    d = H.parse(doc('### 화면 1 — a\n작업: 없음\n대본: 첫 문장입니다.\n둘째.\n참고: 없음\n'))
    assert d['screens'][1]['script'] == ['첫 문장입니다.', '둘째.'] and warns(d) and not errs(d), d['problems']


def t_reserved_word_like_content_is_content():
    # 대본 안의 'CT: …', '영상: …' 같은 줄은 예약어가 아니다
    d = H.parse(doc('### 화면 1 — a\n작업: 없음\n대본:\nCT: wall thickening.\n영상: US 소견.\n참고:\n- [검증] 교과서\n'))
    assert not d['problems'] and d['screens'][1]['script'] == ['CT: wall thickening.', '영상: US 소견.']


def t_ops_closed_set_and_comments():
    ok = ['없음 (문단 교체 2곳 · 문단 추가 1곳)', '배경 단색 #D2F6F6(교육목표 통일, 규약 §1.1) · 본문 수정·문단 교체 — 아래',
          '앞에 복제(정답 표시 제거) — 복제본이 문제. 해설 상자 없음', '이동 → 원본 화면 12 뒤(순서 유지) · 배경 단색 #D2F6F6',
          '새 슬라이드(교육목표 형식, 화면 61과 같은 틀) → 바로 앞 새 슬라이드 뒤 · 배경 단색 #D2F6F6 · 본문 13문단',
          '가져옴: LGI 덱 화면 2 → T1 뒤 · 제목·본문 전체 교체', '숨김 해제', '삭제', '메모 복사 — 원본 43 의 메모']
    for t in ok:
        ops, _, e = H.parse_ops(t)
        assert ops and not [x for x in e if x[0] == '오류'], (t, ops, e)
    assert H.parse_ops('배경 단색 #D2F6F6 (설명 — 안의 대시)')[0] == [('배경', ('D2F6F6',))]
    ops, _, e = H.parse_ops('크기 줄이기')
    assert e and e[0][0] == '오류'
    assert H._boxes('복제본이 문제 — 해설 상자 "Less common features", "Smoking related" 도 뺌') == ['Less common features', 'Smoking related']
    assert H._boxes('해설 상자 없음') == [] and H._boxes('복제본이 문제') is None


def t_dup_requires_problem_script():
    d = H.parse(doc('### 화면 3 — Q\n작업: 앞에 복제(정답 표시 제거) — 해설 상자 없음\n대본:\n정답 ㉡.\n참고: 없음\n'))
    assert any('복제본(문제) 대본' in p[2] for p in errs(d))
    d = H.parse(doc('### 화면 3 — Q\n작업: 앞에 복제(정답 표시 제거)\n복제본(문제) 대본:\n먼저 골라 보세요.\n대본:\n정답 ㉡.\n참고: 없음\n'))
    assert not errs(d) and any('해설 상자' in p[2] for p in warns(d)) and d['screens'][3]['dup_script'] == ['먼저 골라 보세요.']


def t_paragraph_ops_and_notation():
    body = ('### 화면 2 — 학습목표\n작업: 없음 (문단 교체 1곳 · 문단 삭제 1곳 · 문단 추가 1곳)\n'
            '문단 교체 1 — `Genioglossus 24-15` 줄:\n본문:\nL1 **Floor of mouth muscles** {r:[짤]24-15}, 19-14\n'
            '문단 삭제: `Mylohyoid m. 19-14`, `Hyoglossus m. 16-12`\n'
            '문단 추가 — 본문 맨 끝(각주 서식):\n본문:\nL2 * 각주\n'
            '대본: 변경 없음\n참고: 변경 없음\n')
    d = H.parse(doc(body))
    assert not d['problems'], d['problems']
    p = d['screens'][2]['para']
    assert [x['kind'] for x in p] == ['교체', '삭제', '추가'] and p[1]['keys'] == ['Mylohyoid m. 19-14', 'Hyoglossus m. 16-12'] and p[2]['at_end']
    bad = H.parse(doc('### 화면 2 — x\n작업: 없음\n문단 교체 — `a` 줄:\n본문:\nL1 **굵게 안 닫음\n대본: 변경 없음\n참고: 없음\n'))
    assert any('**' in e[2] for e in errs(bad))
    bad = H.parse(doc('### 화면 2 — x\n작업: 없음\n문단 교체 — `a` 줄:\n대본: 변경 없음\n참고: 없음\n'))
    assert any('"본문:"' in e[2] for e in errs(bad)), bad['problems']


def t_new_slide_and_fixes_table():
    body = ('### 새 슬라이드 — Thyroid (1/2)\n작업: 새 슬라이드(교육목표 형식, 화면 3과 같은 틀) → 화면 4 앞 · 배경 단색 #D2F6F6\n'
            '제목: Thyroid (1/2)\n본문:\nL0 **1) 영상 해부학**\nL1 가) 정상 모양을 이해한다(B).\n대본:\n교육목표입니다.\n참고: 없음\n\n'
            '## 본문 수정\n\n| 화면 | 원문 | 수정문 | 근거 |\n|---|---|---|---|\n| 5 | `Parathyoid` | `Parathyroid` | 오기 |\n| 6 | `ㄴ` | `` | 입력 잔재 |\n')
    d = H.parse(doc(body))
    assert not d['problems'], d['problems']
    assert d['new'][0]['title'] == 'Thyroid (1/2)' and len(d['new'][0]['body']) == 2
    assert d['fixes'] == [{'ln': d['fixes'][0]['ln'], 'screen': 5, 'old': 'Parathyoid', 'new': 'Parathyroid', 'why': '오기'},
                          {'ln': d['fixes'][1]['ln'], 'screen': 6, 'old': 'ㄴ', 'new': '', 'why': '입력 잔재'}]


def _fixture_deck():
    p = os.path.join(TMP, 'base.pptx')
    T.make_fixture(p)
    return p


def t_check_against_deck():
    base = _fixture_deck()
    D = T.Deck.open(base, os.path.join(TMP, 'd1')); D.src_path = base
    order = [s for s, _, _ in D.order() if s]
    n = len(order)
    titles = {k: H._title_text(D, order[k - 1]) for k in range(1, n + 1)}
    k = next(i for i in range(1, n + 1) if titles[i])
    # 본문 문단 하나를 키로
    import html as _h
    x = open(D._slide(order[k - 1]), encoding='utf8').read()
    paras = [re.sub(r'\s+', ' ', _h.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>', p)))).strip() for p in re.findall(r'<a:p>.*?</a:p>', x, re.S)]
    key = next((p for p in paras if p and paras.count(p) == 1 and p != titles[k]), None)
    body = '### 화면 %d — %s\n작업: 없음\n' % (k, titles[k])
    if key:
        body += '문단 교체 — `%s` 줄:\n본문:\nL1 새 글\n' % key
    body += '대본:\n문장.\n참고: 없음\n'
    good = H.parse(doc(body, n))
    buf = io.StringIO(); e, _ = H.check(good, D, stream=buf)
    assert e == 0 and '적용 가능' in buf.getvalue(), buf.getvalue()
    # 화면 수가 다르면(다른 판) 오류
    buf = io.StringIO(); e, _ = H.check(H.parse(doc(body, n + 3)), D, stream=buf)
    assert e and '기준 판이 다르다' in buf.getvalue(), buf.getvalue()
    # 제목이 다르면 오류
    wrong = body.replace('— %s' % titles[k], '— 전혀 다른 제목 XYZ', 1)
    buf = io.StringIO(); e, _ = H.check(H.parse(doc(wrong, n)), D, stream=buf)
    assert e and '제목 불일치' in buf.getvalue(), buf.getvalue()
    # 없는 문단 키
    miss = doc('### 화면 %d — %s\n작업: 없음\n문단 삭제: `없는 문단 글 QQQ`\n대본: 변경 없음\n참고: 없음\n' % (k, titles[k]), n)
    buf = io.StringIO(); e, _ = H.check(H.parse(miss), D, stream=buf)
    assert e and '0번 찾음' in buf.getvalue(), buf.getvalue()
    # 본문 수정: 없는 원문은 오류
    fx = doc('## 본문 수정\n\n| 화면 | 원문 | 수정문 | 근거 |\n|---|---|---|---|\n| %d | `없는원문QQQ` | `x` | t |\n' % k, n)
    buf = io.StringIO(); e, _ = H.check(H.parse(fx), D, stream=buf)
    assert e and '본문 수정' in buf.getvalue()
    # 넘김 sha 대조
    b = doc(body, n).encode('utf8')
    buf = io.StringIO(); e, _ = H.check(H.parse(b.decode('utf8')), D, b, '0000000000000000', stream=buf)
    assert e and 'D11' in buf.getvalue()


def t_ellipsis_key():
    base = _fixture_deck()
    D = T.Deck.open(base, os.path.join(TMP, 'd2'))
    sn = [s for s, _, _ in D.order() if s][6]
    D.set_body(sn, T.Body().line('Thyroid nodule: K-TIRADS 24-01, 22-13, 21-02, 18-14').line('other'))
    assert H._para_count(D, sn, 'Thyroid nodule: K-TIRADS 24-01, …, 18-14') == 1
    assert H._para_count(D, sn, 'Thyroid nodule: K-TIRADS 99-01, …, 18-14') == 0


def t_v11_memo_request_and_base_sha():
    base = _fixture_deck()
    D = T.Deck.open(base, os.path.join(TMP, 'd4')); D.src_path = base
    order = [s for s, _, _ in D.order() if s]
    t1 = H._title_text(D, order[0]) or '(제목 없음)'
    body = '### 화면 1 — %s\n작업: 없음\n대본: 변경 없음\n참고:\n- [메모 수정 요청] 원작자 메모 A → B\n' % t1
    buf = io.StringIO(); e, _ = H.check(H.parse(doc(body, len(order))), D, stream=buf)
    assert e == 0 and '메모 수정 요청 1' in buf.getvalue() and '원작자 메모 수정' in buf.getvalue() and '기준 sha256 이 머리에 없다' in buf.getvalue(), buf.getvalue()
    # 기준 sha256 이 있고 다르면 오류(노트만 다른 판도 잡는다)
    head_sha = doc(body, len(order)).replace('— 화면 번호는 v1 기준\n', '— 화면 번호는 v1 기준\n> 기준 sha256: `0000000000000000`\n', 1)
    d = H.parse(head_sha); assert d['base_sha'] == '0000000000000000'
    buf = io.StringIO(); e, _ = H.check(d, D, stream=buf)
    assert e and '고쳐 저장했는지' in buf.getvalue(), buf.getvalue()
    real = hashlib.sha256(open(base, 'rb').read()).hexdigest()[:16]
    buf = io.StringIO(); e, _ = H.check(H.parse(head_sha.replace('0000000000000000', real)), D, stream=buf)
    assert e == 0, buf.getvalue()

def _body_paras(D, sn):
    import html as _h
    x = open(D._slide(sn), encoding='utf8').read()
    m = re.search(r'<p:sp>(?:(?!</p:sp>).)*?<p:ph\b(?![^>]*type="(?:title|ctrTitle)")[^>]*/?>.*?</p:sp>', x, re.S)
    if not m:
        return []
    return [_h.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>', p))) for p in re.findall(r'<a:p>.*?</a:p>', m.group(0), re.S)]

def t_v12_apply_end_to_end():
    base0 = _fixture_deck()
    D0 = T.Deck.open(base0, os.path.join(TMP, 'ap00'))
    F0 = [s for s, _, _ in D0.order() if s]
    k = 7
    D0.set_body(F0[k - 1], T.Body().line('Alpha item 22-01').line('Beta item 23-02').line('Gamma item 24-03'))
    D0.set_notes(F0[1], ['원작자 메모 한 줄 CT 비교'])
    D0.protect_memo(F0[1])                                   # 화면 2 에 원작자 메모 — 적용 뒤에도 그대로여야
    base = os.path.join(TMP, 'base_ap.pptx'); D0.save(base)
    D = T.Deck.open(base, os.path.join(TMP, 'ap0'))
    F = [s for s, _, _ in D.order() if s]; n = len(F)
    title = lambda k: H._title_text(D, F[k - 1]) or '(제목 없음)'
    bp = [t for t in _body_paras(D, F[k - 1]) if t.strip()]
    fix_old = bp[0].split()[0]
    md = doc(
        '### 화면 2 — %s\n작업: 없음\n대본:\n새 대본 한 줄.\n참고: 없음\n\n' % title(2) +
        '### 화면 3 — %s\n작업: 배경 단색 #D2F6F6 · 숨김\n대본: 변경 없음\n참고: 변경 없음\n\n' % title(3) +
        '### 화면 5 — %s\n작업: 앞에 복제(정답 표시 제거) — 해설 상자 없음\n복제본(문제) 대본:\n먼저 골라 보세요.\n대본: 변경 없음\n참고:\n- [메모 수정 요청] 원작자 메모 A → B\n\n' % title(5) +
        '### 화면 6 — %s\n작업: 삭제\n대본: (삭제 화면)\n\n' % title(6) +
        '### 화면 %d — %s\n작업: 없음 (문단 교체 1곳 · 문단 추가 1곳)\n문단 교체 — `%s` 줄:\n본문:\nL1 **교체된 줄** 25-01\n문단 추가 — 본문 맨 끝:\n본문:\nL2 * 각주\n대본: 변경 없음\n참고:\n- [검증] 교과서\n\n' % (k, title(k), bp[1]) +
        '### 새 슬라이드 — 교육목표 (1/1)\n작업: 새 슬라이드(교육목표 형식, 화면 %d과 같은 틀) → 화면 %d 앞 · 배경 단색 #D2F6F6\n제목: 교육목표 (1/1)\n본문:\nL0 **1) 영상 해부학**\nL1 가) 정상 모양을 이해한다(B).\n대본:\n교육목표입니다.\n참고: 없음\n\n' % (k, k) +
        '## 본문 수정\n\n| 화면 | 원문 | 수정문 | 근거 |\n|---|---|---|---|\n| %d | `%s` | `%sX` | 시험 |\n' % (k, fix_old, fix_old), n)
    d = H.parse(md)
    D.src_path = base
    e, _ = H.check(d, D, stream=io.StringIO())
    assert e == 0, d['problems']
    out = os.path.join(TMP, 'applied.pptx')
    rep = H.apply(d, base, out, workdir=os.path.join(TMP, 'apw'))
    assert rep['valid'] and not rep['memo_bad'], rep
    assert rep['screens'] == n + 1 + 1 - 1, rep['screens']
    R = T.Deck.open(out, os.path.join(TMP, 'apr'))
    ro = [s for s, _, _ in R.order() if s]
    # 새 슬라이드: 화면 k 바로 앞, 제목·본문·배경·노트
    new_sn = rep['new'][0][1]
    assert ro.index(new_sn) + 1 == ro.index(F[k - 1])
    assert H._title_text(R, new_sn) == '교육목표 (1/1)'
    assert [t for t in _body_paras(R, new_sn) if t.strip()] == ['1) 영상 해부학', '가) 정상 모양을 이해한다(B).']
    assert 'D2F6F6' in open(R._slide(new_sn), encoding='utf8').read() and R.notes_sections(new_sn)[0] == ['교육목표입니다.']
    # 화면 k: 본문 수정·교체·추가
    kb = [t for t in _body_paras(R, F[k - 1]) if t.strip()]
    assert kb[0].startswith(fix_old + 'X') and '교체된 줄 25-01' in kb and kb[-1] == '* 각주', kb
    assert R.notes_sections(F[k - 1])[1] == ['· [검증] 교과서']          # 결정 1: 글머리 ·
    # 화면 3: 배경·숨김 / 화면 2: 노트 / 화면 6 삭제 / 화면 5 앞 복제
    assert 'D2F6F6' in open(R._slide(F[2]), encoding='utf8').read() and R.is_hidden(F[2])
    assert R.notes_sections(F[1])[0] == ['새 대본 한 줄.'] and R.notes_sections(F[1])[1] == []
    assert R.notes_sections(F[1])[2] == ['원작자 메모 한 줄 CT 비교'], R.notes_sections(F[1])   # 메모 보존
    assert F[5] not in ro and rep['deleted'] == [6]
    dup = rep['dup'][0][1]
    assert ro.index(dup) + 1 == ro.index(F[4]) and R.notes_sections(dup)[0] == ['먼저 골라 보세요.']
    assert rep['memo_req'] and rep['memo_req'][0][0] == 5
    buf = io.StringIO(); H.report(rep, buf)
    assert 'sha256' in buf.getvalue() and '메모 수정 요청' in buf.getvalue()
    # compare: 같은 파일은 0, 기준과 결과는 다르다
    assert H.compare(out, out, io.StringIO(), os.path.join(TMP, 'cmp1')) == 0
    buf = io.StringIO(); assert H.compare(base, out, buf, os.path.join(TMP, 'cmp2')) > 0 and '화면 수가 다르다' in buf.getvalue()

def t_v12_apply_refuses_on_check_errors():
    base = _fixture_deck()
    D = T.Deck.open(base, os.path.join(TMP, 'ap1'))
    n = len([s for s, _, _ in D.order() if s])
    md = os.path.join(TMP, 'bad.md')
    open(md, 'w', encoding='utf8').write(doc('### 화면 1 — 전혀 다른 제목 QQQ\n작업: 없음\n대본:\nx\n참고: 없음\n', n))
    r = subprocess.run([sys.executable, os.path.join(HERE, 'handoff.py'), 'apply', md, '--deck', base, '-o', os.path.join(TMP, 'x.pptx')],
                       capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode == 1 and '적용하지 않았다' in r.stdout and not os.path.exists(os.path.join(TMP, 'x.pptx')), r.stdout[-500:]

def t_v13_fixes_from_real_test():
    # 3-1: 떠 있는 '본문:' 은 오류
    d = H.parse(doc('### 화면 2 — x\n작업: 없음 (문단 추가 2곳 — 본문 맨 끝)\n본문:\nL1 **기타**\n대본: 변경 없음\n참고: 없음\n'))
    assert any('딸리지 않았다' in p[2] for p in errs(d)), d['problems']
    # 3-4: '- 없음' 한 줄은 없음
    d = H.parse(doc('### 화면 2 — x\n작업: 없음\n대본: 변경 없음\n참고:\n- 없음\n'))
    assert d['screens'][2]['tips'] == 'NONE' and not d['problems']
    # 결정 2: 연도 규칙
    assert H._range_years('2026_전평_4_흉부1__2023-2025__x.pptx') == {'23', '24', '25'}
    assert H._apply_year_rule('L1 AEP [짤]22-11, 24-02, {r:25-01}', {'23', '24', '25'}, (True, True)) == 'L1 AEP [짤]22-11, **{r:24-02}**, {r:25-01}'
    assert H._apply_year_rule('L1 x 24-02', {'23', '24', '25'}, (False, True)) == 'L1 x {r:24-02}'
    # 3-2: 본문 수정이 문단 키를 바꿔도 문단 추가가 같은 문단을 찾는다
    base0 = _fixture_deck()
    D0 = T.Deck.open(base0, os.path.join(TMP, 'v13a')); F0 = [s for s, _, _ in D0.order() if s]
    D0.set_body(F0[6], T.Body().line('Chest AP 23-23, 19-30').line('Other 11-11'))
    base = os.path.join(TMP, 'v13_2023-2025_base.pptx'); D0.save(base)
    D = T.Deck.open(base, os.path.join(TMP, 'v13b')); D.src_path = base
    n = len(F0); t7 = H._title_text(D, F0[6])
    md = doc('### 화면 7 — %s\n작업: 없음\n문단 추가 — `Chest AP 23-23, 19-30` 줄 바로 뒤:\n본문:\nL1 Added 24-01\n대본: 변경 없음\n참고: 없음\n\n'
             '## 본문 수정\n\n| 화면 | 원문 | 수정문 | 근거 |\n|---|---|---|---|\n| 7 | `23-23` | `[짤]23-23` | t |\n' % t7, n)
    d = H.parse(md); assert H.check(d, D, stream=io.StringIO())[0] == 0
    rep = H.apply(d, base, os.path.join(TMP, 'v13o.pptx'))
    R = T.Deck.open(os.path.join(TMP, 'v13o.pptx'), os.path.join(TMP, 'v13r'))
    body = [t for t in _body_paras(R, F0[6]) if t.strip()]
    assert body[:3] == ['Chest AP [짤]23-23, 19-30', 'Added 24-01', 'Other 11-11'], body
    assert not os.path.exists(os.path.join(os.path.dirname(rep.get('_wd', '/nonexistent')), 'x'))

def t_cli():
    base = _fixture_deck()
    D = T.Deck.open(base, os.path.join(TMP, 'd3'))
    order = [s for s, _, _ in D.order() if s]
    t1 = H._title_text(D, order[0]) or '(제목 없음)'
    md = os.path.join(TMP, 'h.md')
    open(md, 'w', encoding='utf8').write(doc('### 화면 1 — %s\n작업: 없음\n대본:\n문장.\n참고: 없음\n' % t1, len(order)))
    r = subprocess.run([sys.executable, os.path.join(HERE, 'handoff.py'), 'check', md, '--deck', base], capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode == 0 and '적용 가능' in r.stdout, (r.stdout, r.stderr[-400:])
    open(md, 'w', encoding='utf8').write(doc('### 화면 1 — x\n대본:\n문장.\n', len(order)))
    r = subprocess.run([sys.executable, os.path.join(HERE, 'handoff.py'), 'check', md], capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode == 1 and '멈춤' in r.stdout


if __name__ == '__main__':
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith('t_') and callable(v)]
    ok = fail = 0
    for name, fn in tests:
        try:
            fn(); ok += 1; print('PASS %s' % name[2:])
        except Exception as e:
            fail += 1; print('FAIL %-40s %s: %s' % (name[2:], type(e).__name__, str(e)[:300]))
    print('\n통과 %d / 건너뜀 0 / 실패 %d  (전체 %d)' % (ok, fail, ok + fail))
    sys.exit(1 if fail else 0)
