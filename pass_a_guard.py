"""밖으로 보내는 스크립트의 경로 거부(스위치 아홉 줄 ⑥) — 거부할 자리는 저장소 밖 로컬 파일에서 읽음.

공개 저장소에도 넣을 수 있게 폴더 이름을 코드에 적지 않는다:
  거부 목록 = 환경 변수 RAD_DENY_PATHS_FILE(없으면 ~/.config/rad-guard/deny_paths.txt) — 한 줄에 경로 하나 또는 'name:<폴더 이름>'
  (name: 규칙 = 어느 깊이든 그 이름의 폴더 아래면 거부 · 심볼릭 링크는 실제 경로로 풀어 봄)
목록 파일이 없으면 아무것도 막지 않음(켜기 = 목록 파일을 두는 것 — '해' 뒤).

쓰는 법(스크립트 머리 · 파일을 여는 곳):
    from pass_a_guard import refuse, refuse_argv
    refuse_argv(sys.argv[1:])        # 인자 중 경로처럼 보이는 것 모두
    refuse(path)                     # 파일을 열기 직전
거부되면 SystemExit(3) · 경로 · 이름은 찍지 않고 '거부 자리 n 번째 규칙' 만.
"""
import os
import sys

DEFAULT = os.path.expanduser('~/.config/rad-guard/deny_paths.txt')


def rules(path=None):
    p = path or os.environ.get('RAD_DENY_PATHS_FILE') or DEFAULT
    if not os.path.exists(p):
        return []
    out = []
    with open(p, encoding='utf-8') as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            if ln.startswith('name:'):
                out.append(('name', ln[5:].strip()))
            else:
                out.append(('path', os.path.realpath(os.path.expanduser(ln))))
    return out


def hit(path, rs=None):
    """거부 규칙 번호(1부터) 또는 0"""
    rs = rules() if rs is None else rs
    if not rs:
        return 0
    real = os.path.realpath(os.path.expanduser(str(path)))
    parts = set(real.split(os.sep)) | set(os.path.abspath(os.path.expanduser(str(path))).split(os.sep))
    for i, (kind, v) in enumerate(rs, 1):
        if kind == 'name' and v in parts:
            return i
        if kind == 'path' and (real == v or real.startswith(v.rstrip(os.sep) + os.sep)):
            return i
    return 0


def refuse(path, rs=None):
    i = hit(path, rs)
    if i:
        sys.stderr.write('거부 — 밖으로 보내는 도구가 막힌 자리를 읽으려 함(거부 규칙 %d) · 멈춤\n' % i)
        raise SystemExit(3)


def refuse_argv(argv, rs=None):
    rs = rules() if rs is None else rs
    if not rs:
        return
    for a in argv:
        s = str(a)
        for piece in ([s.split('=', 1)[1]] if s.startswith('--') and '=' in s else [s]):
            if os.sep in piece or os.path.exists(piece):
                refuse(piece, rs)
