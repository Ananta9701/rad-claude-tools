#!/usr/bin/env python3
"""handoff.py 테스트 — python3 test_handoff.py (pytest 불필요)."""
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

EXPECT_VERSION = '1.0'
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
    print('\n통과 %d / 실패 %d  (전체 %d)' % (ok, fail, ok + fail))
    sys.exit(1 if fail else 0)
