"""밖으로 보내는 스크립트의 경로 거부(스위치 아홉 줄 ⑥) — 거부할 자리는 저장소 밖 로컬 파일에서 읽음.

공개 저장소에도 넣을 수 있게 폴더 이름을 코드에 적지 않는다:
  거부 목록 = 환경 변수 RAD_DENY_PATHS_FILE(없으면 ~/.config/rad-guard/deny_paths.txt) — 한 줄에 하나:
    경로                 그 경로 아래면 거부
    name:<폴더 이름>     어느 깊이든 그 이름의 폴더 아래면 거부(심볼릭 링크는 실제 경로로 풀어 봄)
    sha:<sha16>          내용이 같은 파일(밖으로 복사한 같은 바이트 사본)이면 어디 있든 거부 — 읽기 도구가 읽을 때 더함
목록 파일이 없으면 막지 못한다 — 그때는 쓸 때마다 경고 한 줄(fail-open 을 조용히 두지 않음) · drive_watch 가 매일 status() 를 줄에 냄.

쓰는 법(스크립트 머리 · 파일을 여는 곳):
    from pass_a_guard import refuse, refuse_argv
    refuse_argv(sys.argv[1:])        # 인자 중 경로처럼 보이는 것 모두
    refuse(path)                     # 파일을 열기 직전
거부되면 SystemExit(3) · 경로 · 이름은 찍지 않고 '거부 자리 n 번째 규칙' 만.
"""
import hashlib
import os
import sys

DEFAULT = os.path.expanduser('~/.config/rad-guard/deny_paths.txt')
SHA_MAX = 512 * 1024 * 1024      # 이보다 큰 파일은 sha 를 세지 않음(경로 · 이름 규칙만)
_warned = False


def list_path(path=None):
    return path or os.environ.get('RAD_DENY_PATHS_FILE') or DEFAULT


def _warn():
    global _warned
    if not _warned:
        sys.stderr.write('경고 — 거부 목록 파일이 없음: 경로 거부가 꺼진 채 돎(스위치 켜진 동안은 사고 · 사용자에게 알림)\n')
        _warned = True


def rules(path=None, warn=True):
    p = list_path(path)
    if not os.path.exists(p):
        if warn:
            _warn()
        return []
    out = []
    with open(p, encoding='utf-8') as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            if ln.startswith('name:'):
                out.append(('name', ln[5:].strip()))
            elif ln.startswith('sha:'):
                out.append(('sha', ln[4:].strip().lower()))
            else:
                out.append(('path', os.path.realpath(os.path.expanduser(ln))))
    return out


def status(path=None):
    """('있음' | '없음', {'name': n, 'path': n, 'sha': n}) — drive_watch 매일 줄"""
    p = list_path(path)
    if not os.path.exists(p):
        return '없음', {}
    c = {'name': 0, 'path': 0, 'sha': 0}
    for k, _ in rules(p, warn=False):
        c[k] += 1
    return '있음', c


def sha16(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def add_sha(s16, path=None):
    """읽기 도구(read_a · Read 훅)가 읽은 파일의 sha16 을 거부 목록에 더함 — 목록 파일이 없으면 만들지 않고 경고(이름 규칙 없는 목록이 생기지 않게)"""
    p = list_path(path)
    if not os.path.exists(p):
        _warn(); return False
    line = 'sha:%s' % s16.lower()
    with open(p, encoding='utf-8') as fh:
        if any(ln.strip() == line for ln in fh):
            return True
    with open(p, 'a', encoding='utf-8') as fh:
        fh.write(line + '\n')
    return True


def hit(path, rs=None):
    """거부 규칙 번호(1부터) 또는 0"""
    rs = rules() if rs is None else rs
    if not rs:
        return 0
    real = os.path.realpath(os.path.expanduser(str(path)))
    parts = set(real.split(os.sep)) | set(os.path.abspath(os.path.expanduser(str(path))).split(os.sep))
    shas = None
    for i, (kind, v) in enumerate(rs, 1):
        if kind == 'name' and v in parts:
            return i
        if kind == 'path' and (real == v or real.startswith(v.rstrip(os.sep) + os.sep)):
            return i
        if kind == 'sha':
            if shas is None:
                shas = sha16(real) if os.path.isfile(real) and os.path.getsize(real) <= SHA_MAX else ''
            if shas and shas == v:
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
