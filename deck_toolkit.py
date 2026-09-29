#!/usr/bin/env python3
"""
deck_toolkit.py — 영상의학 quiz / case review / journal review PPTX 작업용 툴킷

목적
    매번 새로 코드를 짜지 않고 기계적인 작업(언팩·감사·본문 교체·노트 삽입·
    슬라이드 추가·재압축·QA 렌더)을 명령 하나로 끝낸다.
    남는 토큰은 영상 판독과 문헌 검증에 쓴다.

사용법 (CLI)
    python deck_toolkit.py audit    deck.pptx                 # 구조 감사 + 텍스트/노트 전수 덤프
    python deck_toolkit.py unpack   deck.pptx -o work/        # XML 언팩
    python deck_toolkit.py media    deck.pptx -o work/media/  # 이미지 추출 + 확대본 생성
    python deck_toolkit.py render   deck.pptx -o work/png/    # 슬라이드 PNG 렌더 (QA용)
    python deck_toolkit.py pack     work/ -o out.pptx         # 재압축 + 검증
    python deck_toolkit.py verify   out.pptx --original deck.pptx

사용법 (라이브러리)
    from deck_toolkit import Deck, Body, C
    d = Deck.open('deck.pptx')
    d.audit()                                   # 구조 리포트
    d.set_body(5, Body()
        .header('Chest PA')
        .line('Bulging contour of the ', ('left mediastinal border', C.CTX), ' ...')
        .gap()
        .header('Pitfall')
        .line(('A negative radiograph does not answer the question.', C.FLAG)))
    d.set_notes(5, ['[Slide 5 — ...]', '', '본문...'])
    d.add_slide(after=6, title='Radiologic findings', body=..., notes=[...])
    d.save('out.pptx')
"""

import argparse
import html
import io
import os
import re
import shutil
import subprocess
import sys
import zipfile

__version__ = '16.45'   # TOOLS_MANIFEST 와 대조. 판이 오르면 여기와 test_toolkit.EXPECT_VERSION 을 함께 올린다

# ----------------------------------------------------------------------------
# 색 규칙 — 프로젝트 전체 공통. 의미가 정해져 있으므로 임의로 늘리지 않는다.
# ----------------------------------------------------------------------------

class C:
    HEAD = 'HEAD'    # 섹션 제목. 구조를 잡는 용도이며 내용이 아니다
    KEY = 'KEY'      # 진단을 결정하는 핵심 소견 — 구(phrase) 단위로만
    CTX = 'CTX'      # 위치·분포·시간 등 감별을 가르는 맥락
    FLAG = 'FLAG'    # 함정, 음성 소견, 기술적 한계, 행동을 바꾸는 포인트
    PLAIN = 'PLAIN'  # 나머지 서술


# ----------------------------------------------------------------------------
# 팔레트 설계 근거 (DECK_SPEC.md §2 참조)
#
#  * 적록 대비로 부정/긍정을 표시하지 않는다. 북유럽계 남성의 약 8%, 한국인
#    남성도 수 % 수준이 적록색각이상이며, 영상의학과 청중은 남성 비율이 높다.
#    빨강과 초록을 의미의 반대쌍으로 쓰면 그 사람들에게는 구분이 사라진다.
#  * 색상(hue) 뿐 아니라 명도(luminance)가 다르도록 고른다. 색각이상에서도
#    명도 차이는 보존된다. 흑백 인쇄와 저가 빔프로젝터에서도 살아남는다.
#  * 어두운 배경에서 순수 빨강(FF0000)은 명도 대비가 낮고 chromostereopsis
#    (적·청의 초점 심도 차)로 글자가 떠 보인다. 본문 텍스트에 쓰지 않는다.
#  * 기본색은 Okabe-Ito Color Universal Design 8색에서 가져오되, 어두운 배경용
#    으로 명도를 올린 변형을 쓴다.
#  * 빨강 계열은 본문이 아니라 **영상 위 주석(화살표·ROI)** 에만 쓴다.
#    영상은 회색조라 경쟁하는 색이 없고, 이때는 단독 사용이므로 문제되지 않는다.
# ----------------------------------------------------------------------------

# 영상 주석 전용 (본문 텍스트에 쓰지 말 것)
ANNOT = {
    'primary':   'FF4136',   # 주 병변 화살표
    'secondary': '39CCCC',   # 비교·대조 구조물
    'tertiary':  'FFDC00',   # 계측선·ROI
}

THEMES = {
    # 권장 기본값. 어두운 배경(#262626 계열) 기준, 적록 의존 없음.
    #   sky blue(헤더) / yellow(핵심) / orange(맥락) / mint(함정)
    #   네 색의 상대 명도: 노랑 > 하늘 > 주황 > 민트 로 벌려 두었다.
    'cud': {C.HEAD: '56B4E9', C.KEY: 'F0E442', C.CTX: 'E69F00',
            C.FLAG: '5CD6AC', C.PLAIN: None},

    # 기존 덱 호환용 — 이미 만들어 둔 덱의 서식을 유지해야 할 때만 쓴다.
    # HEAD 와 CTX 가 같은 주황이라 충돌한다. 신규 덱에는 쓰지 않는다.
    'amber': {C.HEAD: 'FFC000', C.KEY: 'FFFF00', C.CTX: 'FFC000',
              C.FLAG: '00B050', C.PLAIN: None},
    'cyan':  {C.HEAD: '00B0F0', C.KEY: 'FFFF00', C.CTX: 'FFC000',
              C.FLAG: '00B050', C.PLAIN: None},
    # 흰 배경 시험 풀이 템플릿. PLAIN 은 상속(검정). KEY 는 템플릿 관례(정답 빨강)를 따름 (전평 대화창 흡수, v16.6)
    'exam':  {C.HEAD: '1F4E79', C.KEY: 'C00000', C.CTX: '7F6000',
              C.FLAG: '385723', C.PLAIN: 'INHERIT'},
}

DEFAULT_THEME = 'cud'

# ----------------------------------------------------------------------------
# 폰트 — 별도 설치 없이 어느 발표 PC에서도 뜨는 조합만 쓴다.
#
#   Arial        : 모든 Windows / macOS 기본 탑재. Office 없어도 있다
#   Calibri      : MS Office 설치 시 탑재 (Win/Mac 공통). Office 없으면 없다
#   맑은 고딕     : Windows Vista 이상 기본 탑재. 한글 발표의 사실상 표준
#   나눔고딕/Pretendard 등은 설치가 필요하므로 쓰지 않는다
#   Aptos(2024~ Office 기본)는 구형 PC에 없으므로 쓰지 않는다
#
# 투사 환경에서는 굵기가 얇은 서체가 뭉개진다. 본문은 bold 를 기본으로 둔다.
# ----------------------------------------------------------------------------

FONT_PROFILES = {
    # 최대 호환. Office 가 없는 PC(뷰어·구글슬라이드 변환)에서도 안전
    'safe':   {'latin': 'Arial',   'ea': '맑은 고딕'},
    # Office 가 있는 환경. Arial 보다 자간이 부드럽다
    'office': {'latin': 'Calibri', 'ea': '맑은 고딕'},
}
DEFAULT_FONT = 'safe'


def esc(t):
    return html.escape(str(t), quote=False)


# ----------------------------------------------------------------------------
# 본문 빌더
# ----------------------------------------------------------------------------

def parse_body_notation(lines):
    """영상의학 넘김 `본문:` 표기 → 문단 목록. `L0`/`L1`/`L2` 수준(없으면 0), `**굵게**`, `{r:빨강}`, `⇥` 탭(→ 탭 문자).
    예: 'L1 **Salivary gland** ⇥ {r:[짤]25-11}, 22-14' (v16.10)"""
    out = []
    for raw in lines:
        line = raw.rstrip('\n')
        if not line.strip():
            continue
        # v16.15 (발표 R1): 수준 표시 뒤 **첫 공백 하나만** 구분자 — 나머지 앞 공백은 글이다(들여쓰기 대신 쓴 공백 4칸이 지워졌다)
        m = re.match(r'^\s*L(\d)[ \t](.*)$', line)
        lvl, body = (int(m.group(1)), m.group(2)) if m else (0, line.strip())
        tab = '⇥' in body
        body = body.replace('⇥', '\t').replace(' \t ', '\t').replace(' \t', '\t').replace('\t ', '\t')
        runs = []
        for tok in re.split(r'(\*\*.+?\*\*|\{r:.+?\})', body):
            if not tok:
                continue
            if tok.startswith('**') and tok.endswith('**'):
                inner = tok[2:-2]
                for t2 in re.split(r'(\{r:.+?\})', inner):
                    if t2:
                        runs.append((t2[3:-1], True, True) if t2.startswith('{r:') else (t2, True, False))
            elif tok.startswith('{r:'):
                runs.append((tok[3:-1], False, True))
            else:
                runs.append((tok, False, False))
        out.append({'lvl': lvl, 'runs': runs, 'tab': tab})
    return out


def _para_templates(region):
    """본문 문단들에서 {(수준, 탭 여부): (pPr, 첫 rPr, 빨강 채움 또는 None)} 을 모은다."""
    tpl = {}
    red = None
    for pm in re.findall(r'<a:p>.*?</a:p>', region, re.S):
        ppr = re.search(r'<a:pPr\b[^>]*/>|<a:pPr\b[^>]*>.*?</a:pPr>', pm, re.S)
        ppr = ppr.group(0) if ppr else ''
        lvl = int((re.search(r'\blvl="(\d)"', ppr) or [0, 0])[1])
        rprs = re.findall(r'<a:rPr\b[^>]*/>|<a:rPr\b[^>]*>.*?</a:rPr>', pm, re.S)
        for r in rprs:
            f = re.search(r'<a:solidFill><a:srgbClr val="(FF0000|C00000|E00000|FF3333|EE0000)"/></a:solidFill>', r)
            if f and red is None:
                red = f.group(0)
        tab = '\t' in ''.join(_AT.findall(pm))
        key = (lvl, tab)
        plain = [r for r in rprs if not _RED_FILL.search(r)]
        if key not in tpl:
            tpl[key] = (ppr, (plain or rprs or ['<a:rPr lang="ko-KR"/>'])[0])
    return {k: (v[0], v[1], red) for k, v in tpl.items()} or {(0, False): ('', '<a:rPr lang="ko-KR"/>', red)}


def _pick_para_template(tpl, lvl, tab):
    for key in ((lvl, tab), (lvl, not tab)):
        if key in tpl:
            return tpl[key]
    near = min(tpl, key=lambda k: (abs(k[0] - lvl), k[1] != tab))
    ppr, rpr, red = tpl[near]
    ppr = re.sub(r'\s+lvl="\d"', '', ppr)
    if lvl:
        ppr = re.sub(r'^<a:pPr\b', '<a:pPr lvl="%d"' % lvl, ppr) if ppr else '<a:pPr lvl="%d"/>' % lvl
    return ppr, rpr, red


_RED_FILL = re.compile(r'<a:solidFill><a:srgbClr val="(?:FF0000|C00000|E00000|FF3333|EE0000)"/></a:solidFill>')


def _notation_of_paras(paras, keep_empty=False):
    """문단 XML 목록 → 표기 줄 (body_notation 의 핵심, v16.17 에서 떼어 냄)."""
    out = []
    for pm in paras:
        lvl = int((re.search(r'<a:pPr\b[^>]*\blvl="(\d)"', pm) or [0, 0])[1])
        runs = []
        for rm in re.finditer(r'<a:r>(.*?)</a:r>', pm, re.S):
            t = html.unescape(''.join(_AT.findall(rm.group(0))))
            if not t:
                continue
            rp = (re.search(r'<a:rPr\b[^>]*/>|<a:rPr\b[^>]*>.*?</a:rPr>', rm.group(1), re.S) or [None])[0] or ''
            bold = bool(re.search(r'<a:rPr\b[^>]*\bb="1"', rp)); red = bool(_RED_FILL.search(rp))
            if runs and re.fullmatch(r' +', t):
                runs[-1][0] += t; continue          # 굵은 단어 사이 공백 run 은 앞 조각에 붙인다(실물: '**Mandibular** **n.**' 로 쪼개짐)
            if not re.search(r'[^\s,\t]', t):
                bold = red = False
            if runs and runs[-1][1] == bold and runs[-1][2] == red:
                runs[-1][0] += t
            else:
                runs.append([t, bold, red])
        if not runs:
            if keep_empty:
                out.append('')
            continue
        s = ''
        for t, bold, red in runs:
            parts = re.split(r'(\t)', t)
            for part in parts:
                if part == '\t':
                    s += '⇥ '
                    continue
                if not part:
                    continue
                lead = part[:len(part) - len(part.lstrip())]; trail = part[len(part.rstrip()):]
                core = part.strip()
                if not core or not (bold or red):
                    s += part
                elif red:
                    s += lead + '{r:%s}' % core + trail
                else:
                    s += lead + '**%s**' % core + trail
        out.append('L%d %s' % (lvl, s))
    return out


def _merge_format(cur, new, skip_bold=None):
    """새 표기 줄에 원래 문단(cur, 표기)의 앞 탭·탭 뒤 공백·굵은 조각을 되살린다. 수준은 new 를 따른다 (v16.17, 발표 apply_HBP_v2 merge_format).
    v16.25 (발표 3-3·사용자 09-27): 줄 앞 탭·공백의 **수**도 원래 문단을 따른다(구분 공백 규칙 전 넘김이 한 칸 모자라던 D9).
    skip_bold(글) 이 참인 굵은 조각은 되살리지 않는다(기출 번호는 연도 규칙으로 — handoff)."""
    lv, body = new[:3], new[3:]
    cbody = cur[3:]
    if cbody.startswith('⇥') and not body.startswith('⇥'):
        lead = re.match(r'⇥ (\s*)', cbody)
        spaces = lead.group(1) if lead else ''
        body = '⇥ ' + (spaces if not body.startswith(spaces) else '') + body
    elif cbody.startswith('⇥') and body.startswith('⇥'):
        a, b = re.match(r'⇥ ?(\s*)', cbody).group(1), re.match(r'⇥ ?(\s*)', body).group(1)
        if a != b:
            body = '⇥ ' + a + body[len(re.match(r'⇥ ?\s*', body).group(0)):]
    else:
        a, b = re.match(r'(\s*)', cbody).group(1), re.match(r'(\s*)', body).group(1)
        if a != b and cbody.strip():
            body = a + body.lstrip()
    for seg in re.findall(r'\*\*(.+?)\*\*', cur):
        if '**%s**' % seg in body:
            continue
        if skip_bold and skip_bold(seg):
            continue
        i = body.find(seg)
        if i >= 0 and '{r:' not in body[max(0, i - 3):i] and '**' not in body[max(0, i - 2):i]:
            body = body[:i] + '**%s**' % seg + body[i + len(seg):]
    return lv + body


def _para_like(para, line):
    """문단 XML 하나를 틀로(pPr·굵은/보통/빨간 run 서식·endParaRPr) 표기 한 줄을 새 문단 XML 로 (v16.14 — replace/insert 공용)."""
    q = parse_body_notation([line])[0]
    ppr = re.search(r'<a:pPr\b[^>]*/>|<a:pPr\b[^>]*>.*?</a:pPr>', para, re.S)
    ppr = ppr.group(0) if ppr else ''
    cur_lvl = int((re.search(r'\blvl="(\d)"', ppr) or [0, 0])[1])
    if q['lvl'] != cur_lvl:
        ppr = re.sub(r'\s+lvl="\d"', '', ppr)
        if q['lvl']:
            ppr = re.sub(r'^<a:pPr\b', '<a:pPr lvl="%d"' % q['lvl'], ppr) if ppr else '<a:pPr lvl="%d"/>' % q['lvl']
    kinds = {}
    for rm in re.finditer(r'<a:r>(.*?)</a:r>', para, re.S):
        rp = re.search(r'<a:rPr\b[^>]*/>|<a:rPr\b[^>]*>.*?</a:rPr>', rm.group(1), re.S)
        if not rp or not re.search(r'[^\s,]', html.unescape(''.join(_AT.findall(rm.group(0))))):
            continue
        rp = rp.group(0)
        red = bool(_RED_FILL.search(rp)); bold = bool(re.search(r'<a:rPr\b[^>]*\bb="1"', rp))
        kinds.setdefault('red' if red else 'bold' if bold else 'plain', rp)
    base = kinds.get('plain') or kinds.get('bold') or kinds.get('red') or '<a:rPr lang="ko-KR"/>'
    redfill = _RED_FILL.search(kinds['red']).group(0) if 'red' in kinds else '<a:solidFill><a:srgbClr val="FF0000"/></a:solidFill>'
    def rpr_for(bold, red):
        if red:
            return kinds.get('red') or _rpr_set(base, bold, redfill)
        if bold:
            return kinds.get('bold') or _rpr_set(base, True, None)
        return kinds.get('plain') or _rpr_set(base, False, None)
    runs = ''.join('<a:r>%s<a:t>%s</a:t></a:r>' % (rpr_for(bd, rd), esc(t)) for t, bd, rd in q['runs'] if t)
    endp = re.search(r'<a:endParaRPr\b[^>]*/>|<a:endParaRPr\b[^>]*>.*?</a:endParaRPr>', para, re.S)
    return '<a:p>%s%s%s</a:p>' % (ppr, runs, endp.group(0) if endp else '')


_PPR_ORDER = ('lnSpc', 'spcBef', 'spcAft', 'buClrTx', 'buClr', 'buSzTx', 'buSzPct', 'buSzPts', 'buFontTx', 'buFont',
              'buNone', 'buAutoNum', 'buChar', 'buBlip', 'tabLst', 'defRPr', 'extLst')


def _ppr_set_child(ppr, tag, xml):
    """pPr 안의 tag 자식을 xml 로 바꾸거나, 스키마 순서에 맞는 자리에 넣는다."""
    if ppr.endswith('/>'):
        ppr = ppr[:-2] + '></a:pPr>'
    ppr = re.sub(r'<a:%s\b[^>]*/>|<a:%s\b[^>]*>.*?</a:%s>' % (tag, tag, tag), '', ppr, flags=re.S)
    later = _PPR_ORDER[_PPR_ORDER.index(tag) + 1:]
    m = re.search(r'<a:(%s)\b' % '|'.join(later), ppr)
    k = m.start() if m else ppr.rindex('</a:pPr>')
    return ppr[:k] + xml + ppr[k:]


def _rpr_set(rpr, bold, fill):
    """_rpr_with 와 같되 굵게를 끌 때 원래 b 속성이 있었으면 b="0" 을 남긴다(마스터 기본이 굵게인 덱에서 모양이 바뀌지 않게)."""
    had_b = bool(re.search(r'<a:rPr\b[^>]*\bb="', rpr))
    r = _rpr_with(rpr, bold, fill)
    if not bold and had_b:
        r = re.sub(r'^<a:rPr\b', '<a:rPr b="0"', r)
    return r


def _rpr_with(rpr, bold, fill):
    """틀 rPr 에서 굵게·채움만 바꾼다. 채움은 자식 순서(ln 뒤, 글꼴 앞)를 지킨다."""
    m = re.match(r'<a:rPr\b([^>]*?)(/?)>(.*?)(?:</a:rPr>)?$', rpr, re.S)
    attrs, selfclose, inner = m.group(1), m.group(2), m.group(3) if not m.group(2) else ''
    attrs = re.sub(r'\s+b="[^"]*"', '', attrs) + (' b="1"' if bold else '')
    # v16.12: 채움 요소는 닫는 태그까지 지운다. 전에는 첫 '/>' 에서 멈춰 `<a:solidFill><a:schemeClr val="tx1"><a:lumMod …/>` 류
    # (Pretendard 덱의 run 서식)에서 `</a:solidFill>` 가 남아 XML 이 깨졌다 — 실물 덱으로 높이 모델을 맞춰 보다 발견
    if fill:
        inner = re.sub(r'<a:(solidFill|gradFill|pattFill|blipFill)\b[^>]*/>|<a:(solidFill|gradFill|pattFill|blipFill)\b[^>]*>.*?</a:\2>|<a:noFill\s*/>', '', inner, flags=re.S)
    else:
        inner = _RED_FILL.sub('', inner)      # 빨강이 아닌 글: 틀의 빨강만 빼고 원래 글자색(scheme·lumMod 등)은 둔다
    if fill:
        ln = re.match(r'<a:ln\b.*?(?:</a:ln>|/>)', inner, re.S)
        inner = (inner[:ln.end()] + fill + inner[ln.end():]) if ln else fill + inner
    return '<a:rPr%s>%s</a:rPr>' % (attrs, inner) if inner else '<a:rPr%s/>' % attrs


class Body:
    """슬라이드 본문 문단을 조립한다.

    line()에 넘기는 조각은 str 이거나 (text, color) 튜플이다.
    색은 C.* 상수를 쓰고, 실제 hex 는 xml(deck=...) 시점에 테마로 해석된다.
    """

    def __init__(self, size=1600, header_size=1800):
        self._items = []
        self.size = size
        self.header_size = header_size

    def header(self, text, size=None):
        self._items.append(('header', text, size or self.header_size))
        return self

    def line(self, *chunks, size=None):
        self._items.append(('line', chunks, size or self.size))
        return self

    def gap(self, size=800):
        self._items.append(('gap', None, size))
        return self

    def ref(self, text, size=1000):
        """참고문헌 줄. 항상 마지막에, 작은 글씨, 흰색."""
        self._items.append(('line', ((text, C.PLAIN),), size))
        return self

    # ---- 렌더 ----
    def xml(self, theme=DEFAULT_THEME, white='bg1'):
        """theme: THEMES 키. white: 흰 글씨에 쓸 scheme 색 이름.

        덱마다 clrMap 이 달라 bg1 이 검정인 덱이 있다(§14). Deck.set_body 가
        deck.white() 를 넘겨 주므로 직접 호출할 때만 신경 쓰면 된다.
        """
        pal = THEMES[theme]
        out = []
        for kind, payload, size in self._items:
            if kind == 'gap':
                out.append(
                    '<a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr>'
                    '<a:endParaRPr lang="en-US" sz="%d" b="1"/></a:p>' % size)
            elif kind == 'header':
                out.append(_para([_run(payload, pal[C.HEAD], size, white=white)]))
            else:
                runs = []
                for ch in payload:
                    if isinstance(ch, tuple):
                        # ('text',) 도 허용 — 색 없는 튜플은 PLAIN 으로
                        text = ch[0]
                        color = ch[1] if len(ch) > 1 else C.PLAIN
                    else:
                        text, color = ch, C.PLAIN
                    runs.append(_run(text, pal.get(color, None), size, white=white))
                out.append(_para(runs))
        return ''.join(out)


def _font_tags(profile=None):
    f = FONT_PROFILES[profile or DEFAULT_FONT]
    return ('<a:latin typeface="%s"/><a:ea typeface="%s"/><a:cs typeface="%s"/>'
            % (f['latin'], f['ea'], f['latin']))


def _run(text, hexcolor, size, font=None, white='bg1', bold=True):
    if hexcolor == 'INHERIT':          # 테마 색 상속 (흰 배경 템플릿용)
        fill = ''
    elif not hexcolor:
        fill = '<a:solidFill><a:schemeClr val="%s"/></a:solidFill>' % white
    else:
        fill = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % hexcolor
    return ('<a:r><a:rPr lang="en-US" altLang="ko-KR" sz="%d"%s dirty="0">%s%s'
            '</a:rPr><a:t>%s</a:t></a:r>'
            % (size, ' b="1"' if bold else '', fill, _font_tags(font), esc(text)))



def _para(runs):
    return ('<a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr>'
            + ''.join(runs) + '</a:p>')


def notes_xml(lines, size=1200):
    """대본 문단. '**로 감싼 줄'은 굵게."""
    out = []
    for ln in lines:
        bold = ln.startswith('**') and ln.endswith('**')
        t = ln.strip('*')
        rpr = ('<a:rPr lang="ko-KR" altLang="en-US" sz="%d"%s dirty="0">'
               '<a:solidFill><a:srgbClr val="000000"/></a:solidFill>%s</a:rPr>'
               % (size, ' b="1"' if bold else '', _font_tags()))
        body = ('<a:r>' + rpr + '<a:t>%s</a:t></a:r>' % esc(t)) if t \
            else '<a:endParaRPr lang="ko-KR" altLang="en-US" sz="%d"/>' % size
        out.append('<a:p><a:pPr marL="0" indent="0">'
                   '<a:lnSpc><a:spcPct val="120000"/></a:lnSpc>'
                   '<a:buNone/></a:pPr>' + body + '</a:p>')
    return ''.join(out)


# ----------------------------------------------------------------------------
# 템플릿 (새 슬라이드 추가용)
# ----------------------------------------------------------------------------

SLIDE_TMPL = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:bg><p:bgPr><a:solidFill><a:schemeClr val="__DARK__"><a:lumMod val="85000"/><a:lumOff val="15000"/></a:schemeClr></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr><p:sp><p:nvSpPr><p:cNvPr id="2" name="TitlePH"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="__W__" cy="902677"/></a:xfrm></p:spPr><p:txBody><a:bodyPr><a:normAutofit/></a:bodyPr><a:lstStyle/><a:p><a:r><a:rPr lang="en-US" altLang="ko-KR" sz="3200" b="1" dirty="0"><a:solidFill><a:schemeClr val="__WHITE__"/></a:solidFill></a:rPr><a:t>__TITLE__</a:t></a:r></a:p></p:txBody></p:sp><p:sp><p:nvSpPr><p:cNvPr id="3" name="BodyPH"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph idx="1"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="164123" y="934670"/><a:ext cx="__BW__" cy="__BH__"/></a:xfrm></p:spPr><p:txBody><a:bodyPr vert="horz" lIns="91440" tIns="45720" rIns="91440" bIns="45720" rtlCol="0" anchor="t"><a:normAutofit/></a:bodyPr><a:lstStyle/>__BODY__</p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'''

SLIDE_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide__N__.xml"/><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/__LAYOUT__"/></Relationships>'''

NOTES_TMPL = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr><p:sp><p:nvSpPr><p:cNvPr id="2" name="SlideImagePH"/><p:cNvSpPr><a:spLocks noGrp="1" noRot="1" noChangeAspect="1"/></p:cNvSpPr><p:nvPr><p:ph type="sldImg"/></p:nvPr></p:nvSpPr><p:spPr/></p:sp><p:sp><p:nvSpPr><p:cNvPr id="3" name="NotesPH"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>__PARAS__</p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>'''

def _notes_tmpl(deck):
    """새 노트 슬라이드 틀. v16.15 (발표 R3): 노트 마스터에 슬라이드 번호 자리(sldNum)가 있으면 같은 ph 로 넣는다 — 새로 만든 노트에
    번호 자리가 없어 인쇄한 노트 쪽에 번호가 안 나오고, diff 가 원본 대비 'sldNum 소실' 로 냈다."""
    t = NOTES_TMPL
    mp = os.path.join(deck.dir, 'ppt/notesMasters/notesMaster1.xml')
    if os.path.exists(mp):
        ph = re.search(r'<p:ph\b[^>]*type="sldNum"[^>]*/>', open(mp, encoding='utf8').read())
        if ph:
            sp = ('<p:sp><p:nvSpPr><p:cNvPr id="4" name="Slide Number Placeholder 3"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
                  '<p:nvPr>%s</p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:fld id="{8A3C1D55-6E0B-4F4E-9B1D-5C2E7A9F0B31}" '
                  'type="slidenum"><a:rPr lang="en-US"/><a:t>‹#›</a:t></a:fld><a:endParaRPr lang="en-US"/></a:p></p:txBody></p:sp>' % ph.group(0))
            t = t.replace('</p:spTree>', sp + '</p:spTree>', 1)
    return t


NOTES_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="../slides/slide__S__.xml"/><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/></Relationships>'''


# ----------------------------------------------------------------------------
# Deck
# ----------------------------------------------------------------------------

class Deck:
    def __init__(self, workdir, theme=DEFAULT_THEME):
        self.dir = workdir
        self.theme = theme
        self.import_warnings = []   # v16.9: import_slide 의 테마·레이아웃 불일치 알림

    # ---- open / save ----
    @classmethod
    def open(cls, pptx, workdir=None, theme=DEFAULT_THEME):
        # v16.10 (발표 X1): 기본 풀기 자리를 현재 폴더(읽기 전용 /mnt/user-data/uploads 에서 실패)가 아니라 임시 폴더로.
        # tempfile_dir 로 만든 폴더는 프로세스 끝에 지운다
        workdir = workdir or tempfile_dir(re.sub(r'\W+', '_', os.path.splitext(os.path.basename(pptx))[0])[:20])
        if os.path.exists(workdir):
            shutil.rmtree(workdir)
        with zipfile.ZipFile(pptx) as z:
            z.extractall(workdir)
        return cls(workdir, theme)

    def save(self, out):
        if os.path.isdir(out):
            raise IsADirectoryError('출력 경로가 디렉터리입니다: %s' % out)
        if not out.lower().endswith(('.pptx', '.potx')):
            raise ValueError('출력 파일명은 .pptx 여야 합니다: %s' % out)
        if os.path.exists(out):
            os.remove(out)
        out_abs = os.path.abspath(out)
        subprocess.run(['zip', '-XrqD', out_abs, '.'], cwd=self.dir, check=True)
        return out

    # ---- paths ----
    def _slide(self, n):
        return os.path.join(self.dir, 'ppt/slides/slide%d.xml' % n)

    def _slide_rels(self, n):
        return os.path.join(self.dir, 'ppt/slides/_rels/slide%d.xml.rels' % n)

    def slide_numbers(self):
        ns = []
        for f in os.listdir(os.path.join(self.dir, 'ppt/slides')):
            m = re.fullmatch(r'slide(\d+)\.xml', f)
            if m:
                ns.append(int(m.group(1)))
        return sorted(ns)

    def is_hidden(self, slide_no):
        """v16.17 (발표 H1): 슬라이드 쇼에서 숨긴 슬라이드인지(<p:sld show="0">)."""
        return bool(re.search(r'<p:sld\b[^>]*\bshow="0"', open(self._slide(slide_no), encoding='utf8').read(2000)))

    def set_hidden(self, slide_no, hidden=True):
        """v16.17 (발표 H1): 숨김/숨김 해제. 반환: 이전 상태."""
        p = self._slide(slide_no); x = open(p, encoding='utf8').read()
        head = re.search(r'<p:sld\b[^>]*>', x).group(0)
        was = ' show="0"' in head
        new = re.sub(r'\s+show="[01]"', '', head)
        if hidden:
            new = new[:-1] + ' show="0">' if not new.endswith('/>') else new
        open(p, 'w', encoding='utf8').write(x.replace(head, new, 1))
        return was

    def hidden_slides(self):
        """숨긴 슬라이드의 화면 번호 목록."""
        return [pos for pos, (sn, _, _) in enumerate(self.order(), 1) if sn and self.is_hidden(sn)]

    def order(self):
        """presentation.xml 의 sldIdLst 순서 -> [(slide_no, sldId, rId), ...]"""
        d = open(os.path.join(self.dir, 'ppt/presentation.xml'), encoding='utf8').read()
        lst = re.search(r'<p:sldIdLst>(.*?)</p:sldIdLst>', d, re.S).group(1)
        rels = open(os.path.join(self.dir, 'ppt/_rels/presentation.xml.rels'),
                    encoding='utf8').read()
        rid2slide = {m.group(1): int(m.group(2)) for m in
                     re.finditer(r'Id="(rId\d+)"[^>]*Target="slides/slide(\d+)\.xml"', rels)}
        out = []
        tags = re.findall(r'<p:sldId\b[^>]*>', lst)
        for tag in tags:   # v16.38 (코드 리뷰 09-28): 속성 순서·공백과 무관하게 — 전에는 `" />"` 하나로 0장이 되고 오류도 없었다
            i, r = re.search(r'\bid="(\d+)"', tag), re.search(r'\br:id="(rId\d+)"', tag)
            if not (i and r):
                raise ValueError('presentation.xml 의 sldId 를 읽지 못했다: %s — 슬라이드 순서를 믿을 수 없어 멈춘다' % tag[:120])
            out.append((rid2slide.get(r.group(1)), i.group(1), r.group(1)))
        return out

    def notes_no(self, slide_no):
        p = self._slide_rels(slide_no)
        if not os.path.exists(p):
            return None
        m = re.search(r'notesSlides/notesSlide(\d+)\.xml', open(p, encoding='utf8').read())
        return int(m.group(1)) if m else None

    def layout_of(self, slide_no):
        m = re.search(r'slideLayouts/(slideLayout\d+\.xml)',
                      open(self._slide_rels(slide_no), encoding='utf8').read())
        return m.group(1) if m else 'slideLayout2.xml'

    # ---- clrMap ----
    def clrmap(self, slide_no=None):
        """slideMaster 의 clrMap 을 dict 로. bg1/tx1 이 어느 테마색에 붙는지."""
        mdir = os.path.join(self.dir, 'ppt/slideMasters')
        master = None
        if slide_no is not None:
            try:
                lay = self.layout_of(slide_no)
                lr = os.path.join(self.dir, 'ppt/slideLayouts/_rels', lay + '.rels')
                m = re.search(r'slideMasters/(slideMaster\d+\.xml)',
                              open(lr, encoding='utf8').read())
                if m:
                    master = os.path.join(mdir, m.group(1))
            except (OSError, ValueError):
                master = None
        if master is None or not os.path.exists(master):
            cands = sorted(f for f in os.listdir(mdir) if f.endswith('.xml')) \
                if os.path.isdir(mdir) else []
            if not cands:
                return {}
            master = os.path.join(mdir, cands[0])
        x = open(master, encoding='utf8').read()
        m = re.search(r'<p:clrMap([^>]*)/?>', x)
        if not m:
            return {}
        return dict(re.findall(r'(\w+)="(\w+)"', m.group(1)))

    def white(self, slide_no=None):
        """흰 글씨를 얻는 scheme 색 이름. 보통 bg1 이지만 clrMap 이 반전된
        덱(bg1=dk1, tx1=lt1)에서는 tx1 이다. §14 참조 — 실제 사고에서 나왔다."""
        cm = self.clrmap(slide_no)
        if cm.get('bg1') == 'lt1':
            return 'bg1'
        if cm.get('tx1') == 'lt1':
            return 'tx1'
        return 'bg1'

    def dark(self, slide_no=None):
        return 'tx1' if self.white(slide_no) == 'bg1' else 'bg1'

    def slide_size(self):
        d = open(os.path.join(self.dir, 'ppt/presentation.xml'), encoding='utf8').read()
        m = re.search(r'<p:sldSz cx="(\d+)" cy="(\d+)"', d)
        return int(m.group(1)), int(m.group(2))

    # ---- read ----
    def texts(self, slide_no):
        """run 단위 텍스트. v16.9: XML escape 를 풀어 돌려준다(전에는 '&gt;' 그대로)."""
        return [html.unescape(t) for t in _AT.findall(open(self._slide(slide_no), encoding='utf8').read())]

    def para_texts(self, slide_no, tables=True):
        """문단(<a:p>) 단위로 run 을 합친 텍스트 (v16.6.1). 색 강조로 run 이 'A '·'.' 처럼 쪼개진 것을 잔재로
        오인하지 않기 위해 audit 이 이것을 쓴다. tables=False (v16.7.1) 면 표(<a:tbl>) 안 문단은 뺀다."""
        x = open(self._slide(slide_no), encoding='utf8').read()
        if not tables:
            x = re.sub(r'<a:tbl>.*?</a:tbl>', '', x, flags=re.S)
        return [html.unescape(''.join(_AT.findall(pm))) for pm in re.findall(r'<a:p>(.*?)</a:p>', x, re.S)]

    def notes(self, slide_no):
        """노트 본문(body placeholder) 의 **문단** 텍스트, 빈 문단 제외, escape 해제 (v16.9).
        v16.8 까지는 노트 XML 전체의 <a:t> 를 run 단위로 escape 그대로 돌려줘서 (1) 여러 run 문단이 여러 줄로 쪼개지고
        (2) '-&gt;' 가 set_notes 에서 '-&amp;gt;' 로 이중 escape 되고 (3) sldNum 자리 글('61')까지 본문으로 섞였다 —
        set_notes(n, notes(n)) 왕복이 원작자 메모를 바꿨다 (전평 H&N 회신 N1). 문단 XML 이 필요하면 notes_paragraphs."""
        return [p['text'] for p in self.notes_paragraphs(slide_no) if p['text'].strip()]

    def _notes_path(self, slide_no):
        n = self.notes_no(slide_no)
        if not n:
            return None
        p = os.path.join(self.dir, 'ppt/notesSlides/notesSlide%d.xml' % n)
        return p if os.path.exists(p) else None

    def _notes_body(self, slide_no):
        """(경로, xml, 문단영역 시작, 끝). body placeholder 의 txBody 안, bodyPr·lstStyle 뒤부터 </p:txBody> 앞까지."""
        p = self._notes_path(slide_no)
        if not p:
            return None
        x = open(p, encoding='utf8').read()
        m = re.search(r'<p:sp>(?:(?!</p:sp>).)*?<p:ph\b[^>]*type="body".*?</p:sp>', x, re.S)
        if not m:
            return None
        ts = x.find('<p:txBody>', m.start())
        if ts == -1 or ts > m.end():
            return None
        te = x.find('</p:txBody>', ts)
        k = ts + len('<p:txBody>')
        for pat in (r'<a:bodyPr\b[^>]*/>|<a:bodyPr\b.*?</a:bodyPr>', r'<a:lstStyle\s*/>|<a:lstStyle>.*?</a:lstStyle>'):
            mm = re.compile(pat, re.S).match(x, k)
            if mm:
                k = mm.end()
        return p, x, k, te

    def notes_paragraphs(self, slide_no):
        """노트 본문 문단 [{'text', 'xml', 'start', 'end'}] — 빈 문단 포함, 순서 보존 (v16.9)."""
        b = self._notes_body(slide_no)
        if not b:
            return []
        _, x, a, e = b
        out = []
        for m in re.finditer(r'<a:p>.*?</a:p>|<a:p/>', x[a:e], re.S):
            seg = m.group(0)
            t = html.unescape(''.join(_AT.findall(seg)).replace('\n', ' '))
            if '<a:br' in seg:
                t = html.unescape(re.sub(r'<a:br\b[^>]*/>', '\n', seg)); t = ''.join(re.findall(r'>([^<]*)<', t))
            out.append({'text': t, 'xml': seg, 'start': a + m.start(), 'end': a + m.end()})
        return out

    def images(self, slide_no, placed_only=True):
        """슬라이드가 쓰는 미디어 파일명. v16.6 (학회 덱 회신 결함 4): 기본은 본문 `r:embed` 로 실제 배치된 것만.
        rels 에만 남은 고아 rel 은 `orphan_images()` 로 따로 본다."""
        p = self._slide_rels(slide_no)
        if not os.path.exists(p):
            return []
        rels = open(p, encoding='utf8').read()
        rid2media = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="\.\./media/([\w.]+)"', rels))
        if not placed_only:
            return list(rid2media.values())
        used = set(re.findall(r'r:embed="(rId\d+)"', open(self._slide(slide_no), encoding='utf8').read()))
        return [m for r, m in rid2media.items() if r in used]

    def orphan_images(self, slide_no):
        """rels 에는 있으나 본문에 배치되지 않은 미디어 (v16.6)."""
        return [m for m in self.images(slide_no, placed_only=False) if m not in self.images(slide_no)]

    def screen_no(self, slide_no):
        """xml 번호 → 화면 순서(1-based). sldIdLst 에 없으면 None."""
        for pos, (sn, _, _) in enumerate(self.order(), 1):
            if sn == slide_no:
                return pos
        return None

    def label(self, slide_no):
        """v16.6 (학회 덱 회신 결함 1): 사람이 보는 화면 번호와 xml 번호를 함께. '화면 11 (slide13.xml)'."""
        pos = self.screen_no(slide_no)
        return ('화면 %d (slide%d.xml)' % (pos, slide_no)) if pos else ('(순서 밖) slide%d.xml' % slide_no)

    def relabel(self, text):
        """출력 문자열의 'slideN' 표기를 label() 형식으로 바꾼다. 파일 경로(slideN.xml)는 건드리지 않는다."""
        return re.sub(r'\bslide(\d+)\b(?!\.xml)', lambda m: self.label(int(m.group(1))), text)

    def shapes(self, slide_no):
        d = open(self._slide(slide_no), encoding='utf8').read()
        out = []
        for m in re.finditer(r'<p:(sp|pic)>.*?</p:\1>', d, re.S):
            s = m.group(0)
            name = re.search(r'name="([^"]*)"', s)
            ph = re.search(r'<p:ph([^/]*)/>', s)
            off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>'
                            r'<a:ext cx="(\d+)" cy="(\d+)"', s)
            out.append({'kind': m.group(1),
                        'name': name.group(1) if name else '',
                        'ph': (ph.group(1).strip() if ph else ''),
                        'xy': off.groups() if off else None})
        return out

    # ---- write ----
    def _body_span(self, slide_no, shape=None):
        """(경로, xml, 문단영역 시작, 끝) — 이름이 shape 인 도형, 없으면 제목이 아닌 첫 txBody 도형."""
        p = self._slide(slide_no)
        d = open(p, encoding='utf8').read()
        i = d.find('name="%s"' % shape) if shape else -1
        if i == -1:
            for m in re.finditer(r'<p:sp>.*?</p:sp>', d, re.S):
                if re.search(r'type="(?:title|ctrTitle)"', m.group(0)):
                    continue
                if '<p:txBody>' in m.group(0):
                    i = m.start()
                    break
        if i == -1:
            raise ValueError('본문 placeholder 를 찾지 못함: slide%d' % slide_no)
        ts = d.find('<p:txBody>', i)
        te = d.find('</p:txBody>', ts)
        k = ts + len('<p:txBody>')
        for pat in (r'<a:bodyPr\b[^>]*/>|<a:bodyPr\b.*?</a:bodyPr>', r'<a:lstStyle\s*/>|<a:lstStyle>.*?</a:lstStyle>'):
            mm = re.compile(pat, re.S).match(d, k)
            if mm:
                k = mm.end()
        return p, d, k, te

    def set_body(self, slide_no, body, shape=None):
        """body 는 Body 인스턴스 또는 이미 만들어진 XML 문자열.
        v16.10: 문단 영역을 bodyPr·lstStyle 뒤에서 찾는다(`<a:lstStyle/>` 가 없는 도형에서 자리를 잘못 잡던 결함)."""
        inner = (body.xml(self.theme, white=self.white(slide_no))
                 if isinstance(body, Body) else body)
        p, d, a, e = self._body_span(slide_no, shape)
        open(p, 'w', encoding='utf8').write(d[:a] + inner + d[e:])

    def set_body_like(self, slide_no, paras, template=None, shape=None, red='FF0000'):
        """v16.10 (발표 Z1): 원천 슬라이드의 **수준별 문단 서식을 틀로** 본문을 새로 쓴다 — 전평 교육목표 슬라이드(절 제목 L0 굵게,
        항목 L1, 세부 L2, 탭 출제줄, 빨간 번호) 형식을 지키려고 덱 스크립트가 문단 XML 을 정규식으로 자르다 깨뜨린 일을 대신한다.
        paras: parse_body_notation() 결과 [{'lvl', 'runs': [(글, 굵게, 빨강)], 'tab'}] 또는 영상의학 표기 줄 목록(문자열이면 파싱).
        template: (덱, slide) — 수준별 pPr·rPr 를 가져올 슬라이드. 없으면 이 슬라이드의 지금 본문. 빨강은 틀에 빨간 run 이 있으면
        그 색, 없으면 red. 반환: 쓴 문단 수."""
        if paras and isinstance(paras[0], str):
            paras = parse_body_notation(paras)
        tdeck, tsn = template or (self, slide_no)
        _, td, ta, te_ = tdeck._body_span(tsn, shape if template is None else None)
        tpl = _para_templates(td[ta:te_])
        out = []
        for q in paras:
            ppr, rpr, redfill = _pick_para_template(tpl, q['lvl'], q['tab'])
            runs = ''.join('<a:r>%s<a:t>%s</a:t></a:r>' % (_rpr_with(rpr, bold, (redfill or '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % red) if isred else None), esc(t))
                           for t, bold, isred in q['runs'] if t)
            out.append('<a:p>%s%s%s</a:p>' % (ppr, runs, _rpr_with(rpr, False, None).replace('<a:rPr', '<a:endParaRPr').replace('</a:rPr>', '</a:endParaRPr>')))
        p, d, a, e = self._body_span(slide_no, shape)
        open(p, 'w', encoding='utf8').write(d[:a] + ''.join(out) + d[e:])
        return len(out)

    def set_title(self, slide_no, lines, size=3200, color='auto', bold=True):
        """color: 'auto'(배경에 맞춰 흰/검) / None(상속) / 'RRGGBB'"""
        p = self._slide(slide_no)
        d = open(p, encoding='utf8').read()
        i = d.find('type="title"')
        if i == -1:
            raise ValueError('title placeholder 없음: slide%d' % slide_no)
        ts = d.find('<p:txBody>', i)
        te = d.find('</p:txBody>', ts)
        ls = d.find('<a:lstStyle/>', ts) + len('<a:lstStyle/>')
        if color is None:
            fill = ''
        elif color == 'auto':
            fill = '<a:solidFill><a:schemeClr val="%s"/></a:solidFill>' % self.white(slide_no)
        else:
            fill = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % color
        rpr = ('<a:rPr lang="en-US" altLang="ko-KR" sz="%d"%s dirty="0">%s</a:rPr>'
               % (size, ' b="1"' if bold else '', fill))
        brk = '<a:br>%s</a:br>' % rpr
        parts = []
        if isinstance(lines, str):
            lines = [lines]
        for k, ln in enumerate(lines):
            if k:
                parts.append(brk)
            parts.append('<a:r>' + rpr + '<a:t>%s</a:t></a:r>' % esc(ln))
        open(p, 'w', encoding='utf8').write(
            d[:ls] + '<a:p>' + ''.join(parts) + '</a:p>' + d[te:])

    def set_notes(self, slide_no, lines, tips=None):
        """노트 전체를 lines 로. tips 를 주면(v16.7, F4·S1) 낭독분 뒤에 공식 표지 NOTES_SEP 와 참고 줄을 붙인다 —
        표지를 손으로 적다가 표지어 위치가 어긋나 lint 가 참고 블록을 낭독으로 센 사고(N1) 를 원천 차단."""
        if tips:     # v16.12: 참고가 비었으면 빈 참고 구역(표지만)을 만들지 않는다 — split_notes 왕복이 노트를 바꾸지 않게
            lines = list(lines) + ['', NOTES_SEP, ''] + list(tips)
        n = self.notes_no(slide_no)
        if n is None:
            n = self._create_notes(slide_no)
        if n is None:
            raise ValueError('notesSlide 가 없음: slide%d' % slide_no)
        b = self._notes_body(slide_no)
        if not b:
            raise ValueError('노트 body placeholder 없음: slide%d' % slide_no)
        p, d, a, e = b
        # v16.9: 원작자 메모 구역(NOTES_SEP_MEMO 부터 끝까지)은 바이트 그대로 뒤에 남긴다 — 순서: 대본 → 참고 → 기존 메모.
        # 메모 표지가 없는 남의 노트는 먼저 protect_memo() 로 표지를 세워야 보존된다(없으면 종전대로 전체 교체).
        memo = ''
        for para in self.notes_paragraphs(slide_no):
            if _is_memo_sep(para['text']):
                memo = d[para['start']:e]
                break
        head = notes_xml(lines) if (lines or not memo) else ''   # 대본·참고가 없고 메모만 있으면 앞에 빈 문단을 만들지 않는다
        open(p, 'w', encoding='utf8').write(d[:a] + head + memo + d[e:])

    def protect_memo(self, slide_no):
        """v16.9: 남이 쓴 노트가 있으면 맨 앞에 NOTES_SEP_MEMO 문단 하나만 끼워 넣어 전체를 '기존 메모' 구역으로 만든다.
        다른 바이트는 건드리지 않는다. 이후 set_notes(n, script, tips) 가 메모를 뒤에 그대로 남긴다. 반환: 표지를 넣었는지."""
        paras = self.notes_paragraphs(slide_no)
        if not any(p['text'].strip() for p in paras) or any(_is_memo_sep(p['text']) for p in paras):
            return False
        # v16.9.2 (발표 Y2): 이미 3부 구조(참고 표지가 있는) 노트는 우리가 쓴 노트다 — 옛 대본을 '기존 메모' 로 감싸지 않는다
        if any(p['text'].strip() == NOTES_SEP or _is_cutoff_line(p['text']) for p in paras):
            return False
        p, d, a, e = self._notes_body(slide_no)
        open(p, 'w', encoding='utf8').write(d[:a] + notes_xml([NOTES_SEP_MEMO]) + d[a:])
        return True

    def _note_para_index(self, slide_no, key, allow_memo=False):
        paras = self.notes_paragraphs(slide_no)
        memo_at = next((i for i, p in enumerate(paras) if _is_memo_sep(p['text'])), len(paras))
        hits = [i for i, p in enumerate(paras) if key in p['text']]
        if len(hits) != 1:
            raise ValueError('노트 key %r 매치 %d회 — 정확히 1회여야 함' % (key, len(hits)))
        if hits[0] >= memo_at and not allow_memo:
            raise ValueError('key %r 는 기존 메모 구역 — 원작자 메모는 고치지 않는다(allow_memo=True 로만)' % key)
        return paras, hits[0]

    def replace_note_paragraph(self, slide_no, key, text, allow_memo=False):
        """v16.9: key 를 포함한 노트 문단 하나만 text 로 바꾼다. 나머지 문단은 바이트 그대로."""
        paras, i = self._note_para_index(slide_no, key, allow_memo)
        p, d, a, e = self._notes_body(slide_no)
        open(p, 'w', encoding='utf8').write(d[:paras[i]['start']] + notes_xml([text]) + d[paras[i]['end']:])
        return paras[i]['text']

    def insert_note_after(self, slide_no, key, lines, allow_memo=False):
        paras, i = self._note_para_index(slide_no, key, allow_memo)
        p, d, a, e = self._notes_body(slide_no)
        open(p, 'w', encoding='utf8').write(d[:paras[i]['end']] + notes_xml(list(lines)) + d[paras[i]['end']:])
        return True

    def delete_note_paragraph(self, slide_no, key, allow_memo=False):
        paras, i = self._note_para_index(slide_no, key, allow_memo)
        p, d, a, e = self._notes_body(slide_no)
        open(p, 'w', encoding='utf8').write(d[:paras[i]['start']] + d[paras[i]['end']:])
        return True

    def copy_note_paragraphs(self, src, src_slide_no, dst_slide_no, start_key=None, end_key=None):
        """v16.9 (H&N 보충): src 덱 노트 본문의 문단을 XML 그대로 dst 노트 본문 끝에 붙인다. start_key 가 든 문단부터
        end_key 가 든 문단 앞까지(없으면 처음부터 끝까지). 문단 안 r:id(하이퍼링크 등)는 dst 노트 rels 에 새 rId 로 옮긴다.
        원본 덱에서 원작자 메모를 복구할 때 쓴다 — 텍스트로 다시 쓰면 굵게·색·링크가 사라진다(75화면 실측).
        반환: 붙인 문단 수."""
        sp = src.notes_paragraphs(src_slide_no)
        si = next((i for i, q in enumerate(sp) if start_key in q['text']), None) if start_key else 0
        if si is None:
            raise ValueError('start_key %r 없음' % start_key)
        ei = next((i for i, q in enumerate(sp) if i > si and end_key in q['text']), len(sp)) if end_key else len(sp)
        chunk = [q['xml'] for q in sp[si:ei]]
        if not chunk:
            return 0
        n_src = src.notes_no(src_slide_no); n_dst = self.notes_no(dst_slide_no)
        if n_dst is None:
            self.set_notes(dst_slide_no, ['']); n_dst = self.notes_no(dst_slide_no)
        srp = os.path.join(src.dir, 'ppt/notesSlides/_rels/notesSlide%d.xml.rels' % n_src)
        drp = os.path.join(self.dir, 'ppt/notesSlides/_rels/notesSlide%d.xml.rels' % n_dst)
        srels = open(srp, encoding='utf8').read() if os.path.exists(srp) else ''
        drels = open(drp, encoding='utf8').read()
        used = [int(v) for v in re.findall(r'Id="rId(\d+)"', drels)]
        nxt = [max(used) + 1 if used else 1]
        remap = {}
        def rid(m):
            old = m.group(2)
            if old not in remap:
                rel = re.search(r'<Relationship [^>]*Id="%s"[^>]*/>' % old, srels)
                if not rel:
                    return m.group(0)
                new = 'rId%d' % nxt[0]; nxt[0] += 1
                remap[old] = new
                nonlocal_rels.append(re.sub(r'Id="%s"' % old, 'Id="%s"' % new, rel.group(0)))
            return '%s="%s"' % (m.group(1), remap[old])
        nonlocal_rels = []
        chunk = [re.sub(r'(r:id|r:embed|r:link)="(rId\d+)"', rid, c) for c in chunk]
        if nonlocal_rels:
            open(drp, 'w', encoding='utf8').write(drels.replace('</Relationships>', ''.join(nonlocal_rels) + '</Relationships>'))
        p, d, a, e = self._notes_body(dst_slide_no)
        open(p, 'w', encoding='utf8').write(d[:e] + ''.join(chunk) + d[e:])
        return len(chunk)


    def _ensure_notes_master(self):
        """v16.9: 노트가 하나도 없던 덱(notesMaster 없음)에 노트를 만들면 notesSlide rels 가 없는 notesMaster1.xml 을 가리켜
        파일이 깨졌다(제목 규격 테스트가 발견). 최소 notesMaster 를 만들어 등록한다. 이미 있으면 아무것도 안 한다."""
        nm = os.path.join(self.dir, 'ppt/notesMasters/notesMaster1.xml')
        if os.path.exists(nm):
            return False
        os.makedirs(os.path.join(self.dir, 'ppt/notesMasters/_rels'), exist_ok=True)
        tdir = os.path.join(self.dir, 'ppt/theme')
        used = [int(m.group(1)) for f in os.listdir(tdir) for m in [re.fullmatch(r'theme(\d+)\.xml', f)] if m]
        tn = max(used) + 1
        shutil.copy(os.path.join(tdir, 'theme%d.xml' % min(used)), os.path.join(tdir, 'theme%d.xml' % tn))
        ns = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
              'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
              'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
        open(nm, 'w', encoding='utf8').write(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:notesMaster %s><p:cSld><p:spTree><p:nvGrpSpPr>'
            '<p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>'
            '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" '
            'accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/></p:notesMaster>' % ns)
        open(os.path.join(self.dir, 'ppt/notesMasters/_rels/notesMaster1.xml.rels'), 'w', encoding='utf8').write(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" '
            'Target="../theme/theme%d.xml"/></Relationships>' % tn)
        ctp = os.path.join(self.dir, '[Content_Types].xml'); ct = open(ctp, encoding='utf8').read()
        ct = ct.replace('</Types>', '<Override PartName="/ppt/notesMasters/notesMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesMaster+xml"/>'
                        '<Override PartName="/ppt/theme/theme%d.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>' % tn)
        open(ctp, 'w', encoding='utf8').write(ct)
        prp = os.path.join(self.dir, 'ppt/_rels/presentation.xml.rels'); pr = open(prp, encoding='utf8').read()
        rid = 'rId%d' % (max(int(v) for v in re.findall(r'Id="rId(\d+)"', pr)) + 1)
        pr = pr.replace('</Relationships>', '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="notesMasters/notesMaster1.xml"/></Relationships>' % rid)
        open(prp, 'w', encoding='utf8').write(pr)
        pxp = os.path.join(self.dir, 'ppt/presentation.xml'); px = open(pxp, encoding='utf8').read()
        px = re.sub(r'(</p:sldMasterIdLst>)', r'\1<p:notesMasterIdLst><p:notesMasterId r:id="%s"/></p:notesMasterIdLst>' % rid, px, 1)
        open(pxp, 'w', encoding='utf8').write(px)
        return True

    def _create_notes(self, slide_no):
        """notesSlide 가 없는 슬라이드에 새로 만들어 붙인다."""
        self._ensure_notes_master()
        base = os.path.join(self.dir, 'ppt/notesSlides')
        os.makedirs(os.path.join(base, '_rels'), exist_ok=True)
        used = [int(m.group(1)) for f in os.listdir(base)
                for m in [re.fullmatch(r'notesSlide(\d+)\.xml', f)] if m]
        n = (max(used) if used else 0) + 1
        open(os.path.join(base, 'notesSlide%d.xml' % n), 'w',
             encoding='utf8').write(_notes_tmpl(self).replace('__PARAS__', notes_xml([''])))
        open(os.path.join(base, '_rels/notesSlide%d.xml.rels' % n), 'w',
             encoding='utf8').write(NOTES_RELS.replace('__S__', str(slide_no)))

        rp = self._slide_rels(slide_no)
        d = open(rp, encoding='utf8').read()
        ids = [int(x) for x in re.findall(r'Id="rId(\d+)"', d)]
        rid = 'rId%d' % ((max(ids) if ids else 0) + 1)
        open(rp, 'w', encoding='utf8').write(d.replace(
            '</Relationships>',
            '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/notesSlide" '
            'Target="../notesSlides/notesSlide%d.xml"/></Relationships>' % (rid, n)))

        ct = os.path.join(self.dir, '[Content_Types].xml')
        c = open(ct, encoding='utf8').read()
        open(ct, 'w', encoding='utf8').write(c.replace(
            '</Types>',
            '<Override PartName="/ppt/notesSlides/notesSlide%d.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'presentationml.notesSlide+xml"/></Types>' % n))
        return n

    def replace_text(self, slide_no, old, new):
        p = self._slide(slide_no)
        d = open(p, encoding='utf8').read()
        if old not in d:
            return False
        open(p, 'w', encoding='utf8').write(d.replace(old, new))
        return True

    # ---- add slide ----
    def add_slide(self, after, title, body, notes=None, layout=None):
        """`after` 번 슬라이드 바로 뒤에 새 슬라이드를 끼워 넣는다.
        파일 번호는 새로 부여하므로 기존 슬라이드 번호는 바뀌지 않는다."""
        slide_no = max(self.slide_numbers()) + 1
        notes_files = [int(m.group(1)) for f in
                       os.listdir(os.path.join(self.dir, 'ppt/notesSlides'))
                       for m in [re.fullmatch(r'notesSlide(\d+)\.xml', f)] if m]
        notes_no = (max(notes_files) if notes_files else 0) + 1
        w, h = self.slide_size()
        white, dark = self.white(after), self.dark(after)
        inner = body.xml(self.theme, white=white) if isinstance(body, Body) else body

        open(self._slide(slide_no), 'w', encoding='utf8').write(
            SLIDE_TMPL.replace('__TITLE__', esc(title))
                      .replace('__BODY__', inner)
                      .replace('__WHITE__', white)
                      .replace('__DARK__', dark)
                      .replace('__W__', str(w))
                      .replace('__BW__', str(w - 328246))
                      .replace('__BH__', str(h - 1110517)))
        open(self._slide_rels(slide_no), 'w', encoding='utf8').write(
            SLIDE_RELS.replace('__N__', str(notes_no))
                      .replace('__LAYOUT__', layout or self.layout_of(after)))
        open(os.path.join(self.dir, 'ppt/notesSlides/notesSlide%d.xml' % notes_no),
             'w', encoding='utf8').write(
            _notes_tmpl(self).replace('__PARAS__', notes_xml(notes or [''])))
        open(os.path.join(self.dir, 'ppt/notesSlides/_rels/notesSlide%d.xml.rels' % notes_no),
             'w', encoding='utf8').write(NOTES_RELS.replace('__S__', str(slide_no)))

        ct = os.path.join(self.dir, '[Content_Types].xml')
        d = open(ct, encoding='utf8').read().replace(
            '</Types>',
            '<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
            '<Override PartName="/ppt/notesSlides/notesSlide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>'
            '</Types>' % (slide_no, notes_no))
        open(ct, 'w', encoding='utf8').write(d)

        prp = os.path.join(self.dir, 'ppt/_rels/presentation.xml.rels')
        d = open(prp, encoding='utf8').read()
        used = [int(x) for x in re.findall(r'Id="rId(\d+)"', d)]
        rid = 'rId%d' % (max(used) + 1)
        open(prp, 'w', encoding='utf8').write(d.replace(
            '</Relationships>',
            '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide%d.xml"/></Relationships>'
            % (rid, slide_no)))

        pxp = os.path.join(self.dir, 'ppt/presentation.xml')
        d = open(pxp, encoding='utf8').read()
        anchor = None
        for sn, sid, arid in self.order():
            if sn == after:
                anchor = '<p:sldId id="%s" r:id="%s"/>' % (sid, arid)
                break
        if anchor is None or anchor not in d:
            raise ValueError('삽입 위치를 찾지 못함: after=%s' % after)
        new_ids = [int(x) for x in re.findall(r'<p:sldId id="(\d+)"', d)]
        open(pxp, 'w', encoding='utf8').write(
            d.replace(anchor, anchor + '<p:sldId id="%d" r:id="%s"/>'
                      % (max(new_ids) + 1, rid)))
        return slide_no

    # ---- audit ----
    # ---- v12: 외부 제작 지침에서 들여온 점검 (DECK_SPEC §17) ----

    # ---- 덱 간 복사 / 삭제 ----
    def import_slide(self, src, src_slide_no, after, copy_notes=False, pictures=True, labels=True, margin=0.15, title_profile=None, keep_bg=False, layout=None):
        """다른 Deck(src)의 슬라이드를 이 덱의 `after` 뒤에 복사한다.

        - 레이아웃 (v16.14 docstring 정정): layout= 을 주면 그것. 아니면 이름·테마·글꼴이 원천과 같은 레이아웃(같은 덱 복제·같은
          템플릿) → title_profile 의 마스터 → after 슬라이드의 마스터에서 표시 이름이 같은 것 → 기준 레이아웃(_pick_layout).
          다르게 붙으면 import_warnings·[참고] 로 알린다 — 빌드 출력에서 걸러 버리지 말 것(H&N v9)
        - 이미지: 새 이름으로 복사 (충돌 방지). pictures=False (v16.7, MSK 회신 F2) 면 <p:pic> 과 그 rels·media 를
          복사하지 않는다 — base 슬라이드를 틀로만 쓸 때. 스크립트가 rels·media 를 직접 지우던 경계 위반(V2)을 대신한다.
          labels=True 는 그림 bbox 안(+margin 인치)의 라벨·화살표를 함께 지운다. **그림 옆에 붙은 sequence 라벨은 bbox 밖이라
          기본 margin(0.15) 로는 안 지워진다** — margin=2.3 처럼 키우거나, 가져온 뒤 clear_pictures(n, labels=True, margin=…)
        - 노트: 기본은 빈 노트로 새로 만든다 (copy_notes=True 면 원본 노트 복사)
        반환: 새 슬라이드 번호
        """
        import shutil as _sh
        sx = open(src._slide(src_slide_no), encoding='utf8').read()
        # v16.9 (실물 전평 덱 검증): 위치를 레이아웃에서 상속하는 placeholder 는 레이아웃이 바뀌면 자리도 바뀐다 — 본문 글이
        # 그림 위로 올라간 사고를 재현했다. 원천 레이아웃·마스터의 위치를 슬라이드에 적어 넣어 자리를 고정한다
        sx = _materialize_ph_geometry(src, src_slide_no, sx)
        dropped_rids = set()
        if not pictures:
            sx, dropped_rids = _strip_pictures_xml(sx, labels=labels, margin=margin)   # 그림 옆 라벨까지 지우려면 margin 을 키운다 (v16.7.2)
        srels_p = src._slide_rels(src_slide_no)
        srels = open(srels_p, encoding='utf8').read() if os.path.exists(srels_p) else ''

        new_no = max(self.slide_numbers()) + 1
        media_dir = os.path.join(self.dir, 'ppt/media')
        os.makedirs(media_dir, exist_ok=True)
        existing = set(os.listdir(media_dir))

        rel_lines = []
        notes_src = None
        for m in re.finditer(r'<Relationship\b[^>]*/>', srels):
            r = m.group(0)
            rid = re.search(r'Id="([^"]+)"', r).group(1)
            typ = re.search(r'Type="([^"]+)"', r).group(1).split('/')[-1]
            tgt = re.search(r'Target="([^"]+)"', r).group(1)
            if typ == 'slideLayout':
                # v16.9: 레이아웃 파일 **이름**(slideLayout2.xml)은 덱마다 뜻이 다르다 — 마스터가 7개인 실물 덱에서
                # 엉뚱한 테마의 레이아웃이 붙었다. 레이아웃 **표시 이름**(예: '제목 및 내용')으로, 기준 마스터 안에서 찾는다.
                # 기준 마스터 = title_profile 의 레이아웃 마스터, 없으면 after 슬라이드의 마스터
                lay = _pick_layout(self, src, tgt.split('/')[-1], title_profile, after, layout)
                # v16.9 (작업규약 §4.7 확인): 레이아웃은 파일 이름으로만 맞추고 원천의 마스터·테마는 가져오지 않는다.
                # 두 덱의 테마가 다르면 가져온 슬라이드가 목적지 모양(글꼴·색·제목 위치)을 입는다 — 알린다
                si, di = _layout_identity(src, tgt.split('/')[-1]), _layout_identity(self, lay)
                # v16.9 (영상의학 회신): 제목·본문 기본 글자 크기 차이도 알린다 — 크기는 원천대로 적어 넣어 고정했지만,
                # 받는 덱에서 다시 편집하면 템플릿 크기로 돌아갈 수 있다
                s_sz = (_title_default_sz(src, src_slide_no), _body_level_sizes(src, src_slide_no, 'idx="1"').get(0))
                d_sz = (_layout_default_sizes(self, lay))
                # v16.10 (발표 Z2): 테마가 다르면 슬라이드 자체 배경(<p:bg>)의 scheme 색이 목적지 테마로 해석돼 어느 쪽 모양도
                # 아닌 색이 된다(LGI accent4 → H&N 에서 분홍). 기본은 배경을 빼서 목적지 배경을 따른다. keep_bg=True 면 둔다
                if si and di and si[1:] != di[1:] and '<p:bg>' in sx and not keep_bg:
                    sx = re.sub(r'<p:bg>.*?</p:bg>', '', sx, count=1, flags=re.S)
                    self.import_warnings.append('import_slide: 원천 slide%d 의 슬라이드 배경을 뺐다(테마가 달라 색이 바뀜) — 필요하면 set_background' % src_slide_no)
                if si != di or s_sz != d_sz:
                    w = ('import_slide: 원천 slide%d 의 레이아웃·테마·글꼴 %s·제목/본문 크기 %s ≠ 목적지 %s·%s — 위치·제목 여백·제목/본문 글자 크기는 '
                         '원천대로 적어 넣어 고정했다. 글꼴·색은 목적지 테마를 따른다. 원래 모양을 온전히 지켜야 하면 PowerPoint 의 "원본 서식 유지" 로 (DECK_SPEC §21)'
                         % (src_slide_no, si, s_sz, di, d_sz))
                    self.import_warnings.append(w); print('[참고] ' + w, file=sys.stderr)
                rel_lines.append(r.replace('Target="%s"' % tgt,
                                           'Target="../slideLayouts/%s"' % lay))
            elif typ == 'notesSlide':
                notes_src = tgt
            elif typ == 'image' or tgt.startswith('../media/'):
                if rid in dropped_rids:
                    continue
                fname = tgt.split('/')[-1]
                srcp = os.path.join(src.dir, 'ppt/media', fname)
                base, ext = os.path.splitext(fname)
                newname = fname
                k = 0
                while newname in existing or os.path.exists(os.path.join(media_dir, newname)):
                    k += 1
                    newname = '%s_i%d%s' % (base, k, ext)
                if os.path.exists(srcp):
                    _sh.copy(srcp, os.path.join(media_dir, newname))
                    existing.add(newname)
                    self._ensure_default_ct(ext.lstrip('.'))
                rel_lines.append(r.replace('Target="%s"' % tgt,
                                           'Target="../media/%s"' % newname))
            else:
                rel_lines.append(r)

        # 새 노트
        self._ensure_notes_master()   # v16.9: 노트 없던 덱이면 notesMaster 부터
        notes_no = self._next_notes_no()
        if copy_notes and notes_src:
            np_src = os.path.join(src.dir, 'ppt/notesSlides', notes_src.split('/')[-1])
            nx = open(np_src, encoding='utf8').read() if os.path.exists(np_src) else \
                _notes_tmpl(self).replace('__PARAS__', notes_xml(['']))
        else:
            nx = _notes_tmpl(self).replace('__PARAS__', notes_xml(['']))
        open(os.path.join(self.dir, 'ppt/notesSlides/notesSlide%d.xml' % notes_no),
             'w', encoding='utf8').write(nx)
        open(os.path.join(self.dir, 'ppt/notesSlides/_rels/notesSlide%d.xml.rels' % notes_no),
             'w', encoding='utf8').write(NOTES_RELS.replace('__S__', str(new_no)))
        rel_lines.append(
            '<Relationship Id="rIdNotesX" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/notesSlide" '
            'Target="../notesSlides/notesSlide%d.xml"/>' % notes_no)

        open(self._slide(new_no), 'w', encoding='utf8').write(sx)
        open(self._slide_rels(new_no), 'w', encoding='utf8').write(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
            'relationships">' + ''.join(rel_lines) + '</Relationships>')

        self._register_slide(new_no, notes_no, after)
        if title_profile:   # v16.9: 베이스 제목 규격으로 맞춘다 (전평 새 연도 덱)
            conform_title(self, new_no, title_profile)
        return new_no

    def notes_sections(self, slide_no):
        """v16.12 (발표 U1): 노트를 (낭독, 참고, 기존 메모) 셋으로. 메모는 표지 뒤 문단 글(표지 제외)."""
        c = self.notes(slide_no)
        mi = next((i for i, t in enumerate(c) if _is_memo_sep(t)), len(c))
        head, memo = c[:mi], c[mi + 1:]
        ti = next((i for i, t in enumerate(head) if _is_cutoff_line(t) or _looks_like_cutoff(t)), None)
        if ti is None:
            return [l for l in head if l.strip()], [], [l for l in memo if l.strip()]
        return [l for l in head[:ti] if l.strip()], [l for l in head[ti + 1:] if l.strip()], [l for l in memo if l.strip()]

    def split_notes(self, slide_no):
        """v16.7 (F4): 노트를 (낭독분, 참고분) 으로 나눈다.
        v16.12 (발표 U1): **기존 메모 구역은 참고에 넣지 않는다** — 전에는 메모 표지도 절단 표지로 보고 그 뒤 전부를 참고로 돌려줘서
        `set_notes(n, *split_notes(n))` 가 원작자 메모를 참고 구역과 메모 구역에 두 번 넣었다. 메모까지 필요하면 notes_sections."""
        s, t, _ = self.notes_sections(slide_no)
        return s, t

    # ---- v16.7 (F5): 기존 슬라이드 본문 문단 편집 ----
    def _find_para(self, slide_no, key, shape=None):
        x = open(self._slide(slide_no), encoding='utf8').read()
        lo, hi = 0, len(x)
        if shape:
            m = re.search(r'<p:sp>(?:(?!</p:sp>).)*?name="%s"(?:(?!</p:sp>).)*</p:sp>' % re.escape(shape), x, re.S)
            if not m:
                raise ValueError('도형 "%s" 없음' % shape)
            lo, hi = m.start(), m.end()
        hits = [pm for pm in re.finditer(r'<a:p>.*?</a:p>', x[lo:hi], re.S) if key in html.unescape(''.join(_AT.findall(pm.group(0))))]
        if len(hits) != 1:
            raise ValueError('key %r 매치 %d회 — 정확히 1회여야 함' % (key, len(hits)))
        return x, lo + hits[0].start(), lo + hits[0].end()

    @staticmethod
    def runs_xml(runs, size=1800, lvl=0, theme='cud', spc=None):
        """[(text, role|hexcolor|None), ...] → <a:p>. role 은 C.HEAD 등, None 은 상속색·비굵게."""
        out = []
        for r in runs:
            t, col = (r, None) if isinstance(r, str) else r
            if col in THEMES.get(theme, {}):
                col = THEMES[theme][col]
            if col and col != 'INHERIT':
                out.append('<a:r><a:rPr lang="en-US" altLang="ko-KR" sz="%d" b="1" dirty="0"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:rPr><a:t>%s</a:t></a:r>' % (size, col, esc(t)))
            else:
                out.append('<a:r><a:rPr lang="en-US" altLang="ko-KR" sz="%d" dirty="0"/><a:t>%s</a:t></a:r>' % (size, esc(t)))
        ppr = '<a:pPr%s>%s</a:pPr>' % (' lvl="%d"' % lvl if lvl else '', '<a:lnSpc><a:spcPct val="%d"/></a:lnSpc>' % spc if spc else '')
        return '<a:p>%s%s</a:p>' % (ppr, ''.join(out))

    def replace_paragraph(self, slide_no, key, runs, shape=None, **kw):
        """key 를 포함한 문단(정확히 1개)을 runs 로 다시 쓴다. 반환: 이전 문단 텍스트."""
        x, a, b = self._find_para(slide_no, key, shape)
        old = ''.join(re.findall(r'<a:t>([^<]*)</a:t>', x[a:b]))
        open(self._slide(slide_no), 'w', encoding='utf8').write(x[:a] + self.runs_xml(runs, **kw) + x[b:])
        return old

    def set_layout(self, slide_no, layout, keep_positions=True):
        """v16.14 (발표 S1-3): 이미 있는 슬라이드의 레이아웃을 바꾼다. keep_positions=True 면 바꾸기 전에 지금 레이아웃에서 물려받던
        placeholder 위치·제목 여백·글자 크기를 적어 넣어 자리를 고정한다(import_slide 와 같은 방식). 반환: 이전 레이아웃 파일 이름."""
        if not os.path.exists(os.path.join(self.dir, 'ppt/slideLayouts', layout)):
            raise ValueError('레이아웃 %s 없음' % layout)
        old = self.layout_of(slide_no)
        if keep_positions:
            p = self._slide(slide_no)
            fixed = _materialize_ph_geometry(self, slide_no, open(p, encoding='utf8').read())   # 먼저 읽고 나서 쓴다
            open(p, 'w', encoding='utf8').write(fixed)
        rp = self._slide_rels(slide_no); r = open(rp, encoding='utf8').read()
        r = re.sub(r'(Type="[^"]*/slideLayout"[^>]*Target=")\.\./slideLayouts/[^"]+"', r'\1../slideLayouts/%s"' % layout, r)
        r = re.sub(r'(Target=")\.\./slideLayouts/[^"]+("[^>]*Type="[^"]*/slideLayout")', r'\1../slideLayouts/%s\2' % layout, r)
        open(rp, 'w', encoding='utf8').write(r)
        return old

    def set_paragraph_spacing(self, slide_no, before=None, after=None, line=None, shape=None, key=None):
        """v16.14 (발표 T2): 본문 문단의 앞 간격·뒤 간격(pt)·줄 간격(%)을 정한다. key 를 주면 그 글이 든 문단만. pPr 자식 순서를
        지킨다(lnSpc → spcBef → spcAft → 글머리표…). 반환: 바꾼 문단 수."""
        p, d, a, e = self._body_span(slide_no, shape)
        n = 0
        def para(m):
            nonlocal n
            q = m.group(0)
            if key and key not in html.unescape(''.join(_AT.findall(q))):
                return q
            ppr_m = re.search(r'<a:pPr\b[^>]*/>|<a:pPr\b[^>]*>.*?</a:pPr>', q, re.S)
            ppr = ppr_m.group(0) if ppr_m else '<a:pPr/>'
            for tag, val in (('lnSpc', line), ('spcBef', before), ('spcAft', after)):
                if val is None:
                    continue
                inner = '<a:spcPct val="%d"/>' % int(val * 1000) if tag == 'lnSpc' else '<a:spcPts val="%d"/>' % int(round(val * 100))
                ppr = _ppr_set_child(ppr, tag, '<a:%s>%s</a:%s>' % (tag, inner, tag))
            n += 1
            if ppr_m:
                return q[:ppr_m.start()] + ppr + q[ppr_m.end():]
            return q.replace('<a:p>', '<a:p>' + ppr, 1)
        body = re.sub(r'<a:p>.*?</a:p>', para, d[a:e], flags=re.S)
        open(p, 'w', encoding='utf8').write(d[:a] + body + d[e:])
        return n

    def insert_paragraph_like(self, slide_no, line, after_key=None, like_key=None, shape=None):
        """v16.14 (발표 T1): 표기 한 줄을 **이웃 문단과 같은 서식**으로 넣는다. after_key 문단 뒤(없으면 본문 끝)에. 틀은 like_key 문단,
        없으면 같은 수준의 문단 중 넣는 자리에서 가장 가까운 것(앞쪽 우선). 다른 문단은 바이트 그대로. 반환: 틀로 쓴 문단 글."""
        p, d, a, e = self._body_span(slide_no, shape)
        paras = [(m.start() + a, m.end() + a, m.group(0)) for m in re.finditer(r'<a:p>.*?</a:p>', d[a:e], re.S)]
        text = lambda q: html.unescape(''.join(_AT.findall(q)))
        if after_key:
            hits = [k for k, (_, _, q) in enumerate(paras) if after_key in text(q)]
            if len(hits) != 1:
                raise ValueError('after_key %r 매치 %d회 — 정확히 1회여야 함' % (after_key, len(hits)))
            at = hits[0]
        else:
            at = max((k for k, (_, _, q) in enumerate(paras) if text(q).strip()), default=len(paras) - 1)
        lvl = parse_body_notation([line])[0]['lvl']
        if like_key:
            cand = [q for _, _, q in paras if like_key in text(q)]
            if len(cand) != 1:
                raise ValueError('like_key %r 매치 %d회' % (like_key, len(cand)))
            tpl = cand[0]
        else:
            lv = lambda q: int((re.search(r'<a:pPr\b[^>]*\blvl="(\d)"', q) or [0, 0])[1])
            order = list(range(at, -1, -1)) + list(range(at + 1, len(paras)))
            # v16.25 (발표 3-5): 탭으로 시작하는 줄(출제줄)은 탭 문단을, 아닌 줄은 탭 아닌 문단을 틀로 — 앞 문단을 그대로 쓰다
            # 출제줄의 강조가 빠지고 각주에 강조가 붙었다(LGI v2 화면 3)
            want_tab = parse_body_notation([line])[0]['tab']
            is_tab = lambda q: text(q).startswith('\t')
            same = [paras[k][2] for k in order if text(paras[k][2]).strip() and is_tab(paras[k][2]) == want_tab and lv(paras[k][2]) == lvl]
            same = same or [paras[k][2] for k in order if text(paras[k][2]).strip() and is_tab(paras[k][2]) == want_tab]
            same = same or [paras[k][2] for k in order if lv(paras[k][2]) == lvl and text(paras[k][2]).strip()]
            tpl = same[0] if same else paras[at][2]
        new = _para_like(tpl, line)
        pos = paras[at][1] if paras else a
        open(p, 'w', encoding='utf8').write(d[:pos] + new + d[pos:])
        return text(tpl)

    def replace_paragraph_like(self, slide_no, key, line, shape=None, keep_format=False):
        """v16.11 (발표 V1): key 를 포함한 문단 **하나만** 표기 한 줄(`L1 **굵게** {r:빨강} ⇥ …`)로 다시 쓴다. 그 문단의 pPr 와 run 서식
        (굵은 run·보통 run·빨간 run 각각)을 틀로 쓰고, **다른 문단은 바이트 그대로** 둔다. 반환: 이전 문단 글.
        keep_format=True (v16.17, 발표 H4): 새 줄에 서식 표시가 빠졌으면 원래 문단의 앞 탭(⇥)·탭 뒤 공백과, 글이 그대로 남은 굵은
        조각을 되살린다 — 넘김 줄이 `⇥`·`**` 를 빠뜨려 들여쓰기·굵게가 사라지던 것(HBP 52줄 중 대부분)."""
        x, a, b = self._find_para(slide_no, key, shape)
        para = x[a:b]
        if keep_format:
            cur = self._para_notation(para)
            line = _merge_format(cur, line)
        old = html.unescape(''.join(_AT.findall(para)))
        open(self._slide(slide_no), 'w', encoding='utf8').write(x[:a] + _para_like(para, line) + x[b:])
        return old

    def _para_notation(self, para):
        """문단 XML 하나 → 표기 한 줄 (body_notation 과 같은 규칙)."""
        return _notation_of_paras([para])[0] if _notation_of_paras([para]) else 'L0 '

    def body_notation(self, slide_no, shape=None, keep_empty=False):
        """v16.11 (발표 V2): 본문 → 영상의학 표기 줄(parse_body_notation 의 역). 같은 서식의 이웃 run 은 합치고, 공백·쉼표뿐인 조각은
        서식 없이 쓴다(굵은 공백 run 을 `****` 로 적어 글에 별표가 들어간 결함 이후). 탭은 `⇥`. 빈 문단은 keep_empty 일 때만 빈 줄."""
        p, d, a, e = self._body_span(slide_no, shape)
        return _notation_of_paras(re.findall(r'<a:p>.*?</a:p>|<a:p/>', d[a:e], re.S), keep_empty)

    def insert_after(self, slide_no, key, runs, shape=None, **kw):
        """key 를 포함한 문단 바로 뒤에 새 문단을 넣는다."""
        x, a, b = self._find_para(slide_no, key, shape)
        open(self._slide(slide_no), 'w', encoding='utf8').write(x[:b] + self.runs_xml(runs, **kw) + x[b:])
        return True

    def box_to_memo(self, slide_no, match, dry_run=False):
        """v16.37 (발표 K21): 글에 match 가 든 글상자(자리 표시자 아님) **하나** 의 글을 노트 '기존 메모' 구역 끝에 한 줄로 더하고(구역이
        없으면 표지부터 — 대본·참고는 그대로) 상자를 지운다(delete_shape 규칙: 정확히 하나일 때만). 슬라이드에서 그림을 가리던 출처
        메모를 정보는 남기고 치우는 용도. 반환 (상자 이름, 옮긴 글, 메모 줄 수 전, 후)."""
        x = open(self._slide(slide_no), encoding='utf8').read()
        hits = []
        for m in re.finditer(r'<p:sp>(?:(?!<p:sp>).)*?</p:sp>', x, re.S):
            seg = m.group(0)
            if '<p:ph' in seg:
                continue
            parts = [html.unescape(''.join(_AT.findall(q))).strip() for q in re.findall(r'<a:p>(.*?)</a:p>', seg, re.S)]
            t = ' / '.join(q for q in parts if q)
            if match in t:
                nm = re.search(r'<p:cNvPr\b[^>]*\bname="([^"]*)"', seg)
                hits.append((html.unescape(nm.group(1)) if nm else '', t))
        if len(hits) != 1:
            raise ValueError('box-to-memo: "%s" 가 든 글상자 %d개 — 정확히 하나여야 한다%s' % (
                match, len(hits), (': ' + ', '.join('"%s"' % h[0] for h in hits[:5])) if hits else ''))
        nm, t = hits[0]
        before = len(self.notes_sections(slide_no)[2])
        if dry_run:
            return nm, t, before, before + 1
        if self.notes_no(slide_no) is None:
            self._create_notes(slide_no)
        p, d, a, e = self._notes_body(slide_no)
        has = any(_is_memo_sep(l) for l in self.notes(slide_no))
        open(p, 'w', encoding='utf8').write(d[:e] + notes_xml(([NOTES_SEP_MEMO] if not has else []) + [t]) + d[e:])
        self.delete_shape(slide_no, nm, must_contain=match)
        return nm, t, before, len(self.notes_sections(slide_no)[2])

    def fit_corner_boxes(self, slide_no, tol_in=0.02, pad=0.15, dry_run=False, font_path=None):
        """v16.27 (발표 K7): 슬라이드 가장자리(위·아래·왼쪽·오른쪽, 허용 tol_in 인치)에 붙은 채우기·테두리 없는 글상자를, 붙은 가장자리를
        고정한 채 반대쪽으로 글(추정 폭 × (1+pad), 줄 수 × 1.2 줄 높이 + 안쪽 여백)에 맞게 키운다. Google Slides 가 wrap="none"·spAutoFit
        을 따르지 않아 구석 인용 상자가 두 줄로 꺾여 화면 밖으로 나간 일(근골격). 글·크기·색·정렬·wrap 은 그대로. 반대쪽으로 키울 자리가
        없으면 건너뛰고, 키운 자리가 다른 글상자·그림과 겹치면 알린다(고치지 않는다).
        반환: [{'name','text','old','new','what','overlap'}] — old/new 는 인치 (x, y, w, h)."""
        p = self._slide(slide_no); x = open(p, encoding='utf8').read()
        W, H = self.slide_size(); tol = tol_in * EMU_IN
        fp = font_path or _theme_body_font_file(self, slide_no)
        grp = [(m.start(), m.end()) for m in re.finditer(r'<p:grpSp>.*?</p:grpSp>', x, re.S)]
        boxes = []
        for m in re.finditer(r'<p:(sp|pic)>(?:(?!<p:\1>).)*?</p:\1>', x, re.S):
            xf = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"\s*/>\s*<a:ext cx="(\d+)" cy="(\d+)"\s*/>', m.group(0))
            if xf and not any(a <= m.start() < b for a, b in grp):
                nm = re.search(r'<p:cNvPr\b[^>]*\bname="([^"]*)"', m.group(0))
                boxes.append((m, xf, html.unescape(nm.group(1)) if nm else ''))
        inch = lambda v: round(v / EMU_IN, 2)
        out, edits = [], []
        for m, xf, nm in boxes:
            seg = m.group(0)
            if m.group(1) != 'sp' or '<p:ph' in seg or '<p:txBody>' not in seg:
                continue
            sp = (re.search(r'<p:spPr\b.*?</p:spPr>|<p:spPr\s*/>', seg, re.S) or [''])[0]
            if re.search(r'<a:(?:solidFill|gradFill|pattFill|blipFill)\b', re.sub(r'<a:ln\b.*?</a:ln>', '', sp, flags=re.S)):
                continue
            ln = re.search(r'<a:ln\b.*?</a:ln>', sp, re.S)
            if ln and '<a:noFill/>' not in ln.group(0) and re.search(r'<a:(?:solidFill|gradFill|pattFill)\b', ln.group(0)):
                continue
            x0, y0, cx, cy = (int(v) for v in xf.groups())
            right, bottom, left, top = x0 + cx >= W - tol, y0 + cy >= H - tol, x0 <= tol, y0 <= tol
            if not (right or bottom or left or top):
                continue
            txt = html.unescape(''.join(_AT.findall(seg))).strip()
            if not txt:
                continue
            bp = (re.search(r'<a:bodyPr\b[^>]*', seg) or [''])[0]
            ins = {k: int((re.search(r'\b%s="(\d+)"' % k, bp) or [0, d])[1]) for k, d in (('lIns', 91440), ('rIns', 91440), ('tIns', 45720), ('bIns', 45720))}
            lines, max_sz = [], 0
            for pm in re.findall(r'<a:p>.*?</a:p>', seg, re.S):
                for part in re.split(r'<a:br\b[^>]*/>', pm):
                    w = 0.0
                    for rm in re.finditer(r'<a:r>(.*?)</a:r>', part, re.S):
                        t = html.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>', rm.group(1))))
                        sz = int((re.search(r'\bsz="(\d+)"', rm.group(1)) or [0, 1800])[1]) / 100.0
                        max_sz = max(max_sz, sz)
                        w += _text_width_pt(t, sz, fp)
                    if w or part.strip():
                        lines.append(w)
            if not lines:
                continue
            need_w = int(max(lines) * 12700 * (1 + pad)) + ins['lIns'] + ins['rIns']
            need_h = int(len(lines) * max_sz * 1.2 * 12700) + ins['tIns'] + ins['bIns']
            ncx, ncy = max(cx, need_w), max(cy, need_h)
            if (ncx, ncy) == (cx, cy):
                continue
            nx = x0 + cx - ncx if (right and not left) else x0
            ny = y0 + cy - ncy if (bottom and not top) else y0
            rec = {'name': nm, 'text': txt[:40], 'old': (inch(x0), inch(y0), inch(cx), inch(cy)), 'new': (inch(nx), inch(ny), inch(ncx), inch(ncy)), 'overlap': []}
            if nx < 0 or ny < 0 or nx + ncx > W or ny + ncy > H:
                rec.update(what='건너뜀: 반대쪽으로 키울 자리가 없다(슬라이드보다 커짐)', new=None); out.append(rec); continue
            for m2, xf2, nm2 in boxes:
                if m2 is m:
                    continue
                a, b, c, d = (int(v) for v in xf2.groups())
                inter_new = nx < a + c and a < nx + ncx and ny < b + d and b < ny + ncy
                inter_old = x0 < a + c and a < x0 + cx and y0 < b + d and b < y0 + cy
                if inter_new and not inter_old:
                    rec['overlap'].append(nm2)
            rec['what'] = '바꿈'
            edits.append((xf.start() + m.start(), xf.end() + m.start(), '<a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/>' % (nx, ny, ncx, ncy)))
            out.append(rec)
        if edits and not dry_run:
            for a, b, sg in sorted(edits, reverse=True):
                x = x[:a] + sg + x[b:]
            open(p, 'w', encoding='utf8').write(x)
        return out

    def widen_label(self, slide_no, name=None, pattern=None, min_width_in=2.0, dry_run=False):
        """v16.26 (발표 K6): 채우기·테두리 없는 글상자(자리 표시자·그룹 안 제외)의 폭을 min_width_in 인치까지 넓힌다.
        wrap="none"·spAutoFit 을 따르지 않는 보기(Google Slides·Drive 미리보기)에서 풀이자 이름표가 두 줄로 꺾여 옆 글을 가린 일.
        정렬 쪽 모서리를 고정한다(왼쪽 정렬 = 왼쪽 끝, 오른쪽 = 오른쪽 끝, 가운데 = 가운데). 글·크기·색은 그대로.
        슬라이드 밖으로 나가게 되면 바꾸지 않는다. name(도형 이름) 또는 pattern(글 전체가 맞는 정규식) 중 하나는 준다.
        반환: [(이름, 글, 전 폭 인치|None, 새 폭 인치|None, '바꿈'|'그대로…'|'건너뜀: …')]"""
        if name is None and pattern is None:
            raise ValueError('widen_label: name 또는 pattern 을 준다')
        p = self._slide(slide_no); x = open(p, encoding='utf8').read()
        W, _ = self.slide_size(); need = int(round(min_width_in * EMU_IN))
        grp = [(m.start(), m.end()) for m in re.finditer(r'<p:grpSp>.*?</p:grpSp>', x, re.S)]
        out, edits = [], []
        for m in re.finditer(r'<p:sp>(?:(?!<p:sp>).)*?</p:sp>', x, re.S):
            seg = m.group(0)
            if '<p:ph' in seg or any(a <= m.start() < b for a, b in grp):
                continue
            nm = re.search(r'<p:cNvPr\b[^>]*\bname="([^"]*)"', seg); nm = html.unescape(nm.group(1)) if nm else ''
            txt = html.unescape(''.join(_AT.findall(seg))).strip()
            if (name is not None and nm != name) or (pattern is not None and not re.fullmatch(pattern, txt)):
                continue
            sp = (re.search(r'<p:spPr\b.*?</p:spPr>|<p:spPr\s*/>', seg, re.S) or [''])[0]
            if re.search(r'<a:(?:solidFill|gradFill|pattFill|blipFill)\b', re.sub(r'<a:ln\b.*?</a:ln>', '', sp, flags=re.S)):
                out.append((nm, txt, None, None, '건너뜀: 채우기 있음')); continue
            ln = re.search(r'<a:ln\b.*?</a:ln>', sp, re.S)
            if ln and '<a:noFill/>' not in ln.group(0) and re.search(r'<a:(?:solidFill|gradFill|pattFill)\b', ln.group(0)):
                out.append((nm, txt, None, None, '건너뜀: 테두리 있음')); continue
            xf = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"\s*/>\s*<a:ext cx="(\d+)" cy="(\d+)"\s*/>', seg)
            if not xf:
                out.append((nm, txt, None, None, '건너뜀: 위치 없음')); continue
            x0, cx = int(xf.group(1)), int(xf.group(3))
            if cx >= need:
                out.append((nm, txt, cx / EMU_IN, cx / EMU_IN, '그대로(이미 넓음)')); continue
            al = (re.search(r'<a:pPr\b[^>]*\balgn="(\w+)"', seg) or [None, 'l'])[1]
            nx = x0 + cx - need if al == 'r' else (x0 + (cx - need) // 2 if al == 'ctr' else x0)
            if nx < 0 or nx + need > W:
                out.append((nm, txt, cx / EMU_IN, None, '건너뜀: 슬라이드 밖으로 나감')); continue
            new = seg[:xf.start()] + '<a:off x="%d" y="%s"/><a:ext cx="%d" cy="%s"/>' % (nx, xf.group(2), need, xf.group(4)) + seg[xf.end():]
            edits.append((m.start(), m.end(), new)); out.append((nm, txt, cx / EMU_IN, need / EMU_IN, '바꿈'))
        if edits and not dry_run:
            for a, b, sg in reversed(edits):
                x = x[:a] + sg + x[b:]
            open(p, 'w', encoding='utf8').write(x)
        return out

    def delete_shape(self, slide_no, name, must_contain=None):
        """v16.18 (발표 C1): 이름이 정확히 name 인 도형(sp·pic·grpSp·graphicFrame·cxnSp) **하나**를 지운다. 같은 이름이 둘 이상이거나
        없으면 거부(ValueError). must_contain 을 주면 그 도형 글에 들어 있어야 지운다(엉뚱한 상자를 지우지 않게). 지운 도형만 쓰던
        그림·링크 관계(rels)도 뺀다(media 파일은 purge_orphans 가 정리). 반환: 지운 도형의 글."""
        p = self._slide(slide_no); x = open(p, encoding='utf8').read()
        hits = []
        for tag in ('sp', 'pic', 'grpSp', 'graphicFrame', 'cxnSp'):
            for m in re.finditer(r'<p:%s>(?:(?!<p:%s>).)*?</p:%s>' % (tag, tag, tag), x, re.S):
                nm = re.search(r'<p:cNvPr\b[^>]*\bname="([^"]*)"', m.group(0))
                if nm and html.unescape(nm.group(1)) == name:
                    hits.append(m)
        # 그룹 안의 같은 이름 도형과 그룹 자체가 둘 다 잡히지 않게, 다른 매치 안에 든 것은 뺀다
        hits = [m for m in hits if not any(o is not m and o.start() <= m.start() and m.end() <= o.end() for o in hits)]
        if len(hits) != 1:
            raise ValueError('delete_shape: 이름 "%s" 도형 %d개 — 정확히 1개여야 함 (slide%d)' % (name, len(hits), slide_no))
        seg = hits[0].group(0)
        txt = html.unescape(''.join(_AT.findall(seg)))
        if must_contain and must_contain not in txt:
            raise ValueError('delete_shape: "%s" 의 글에 %r 이 없음 — 지우지 않음' % (name, must_contain))
        x = x[:hits[0].start()] + x[hits[0].end():]
        open(p, 'w', encoding='utf8').write(x)
        rp = self._slide_rels(slide_no)
        if os.path.exists(rp):
            r = open(rp, encoding='utf8').read()
            for rid in set(re.findall(r'r:(?:embed|link|id)="(rId\d+)"', seg)):
                if 'r:embed="%s"' % rid not in x and 'r:id="%s"' % rid not in x and 'r:link="%s"' % rid not in x:
                    r = re.sub(r'<Relationship [^>]*Id="%s"[^>]*/>' % rid, '', r)
            open(rp, 'w', encoding='utf8').write(r)
        return txt

    def delete_paragraph(self, slide_no, key, shape=None):
        x, a, b = self._find_para(slide_no, key, shape)
        open(self._slide(slide_no), 'w', encoding='utf8').write(x[:a] + x[b:])
        return True

    # ---- v16.7 (F6): 인용 상자 ----
    def set_cite(self, slide_no, lines, box=(0.2, 7.12, 9.6, 0.28), size=800, name='CiteBox'):
        """우하단 인용 상자. 있으면 글·위치를 바꾸고 없으면 만든다. 항상 wrap=square — wrap=none 인 채 길어져
        슬라이드 밖으로 나간 사고가 10회 이상. box 는 인치 (x, y, w, h)."""
        p = self._slide(slide_no); x = open(p, encoding='utf8').read()
        m = re.search(r'<p:sp>(?:(?!</p:sp>).)*?name="%s"(?:(?!</p:sp>).)*</p:sp>' % re.escape(name), x, re.S)
        if m:
            x = x[:m.start()] + x[m.end():]
        bx, by, bw, bh = (int(v * 914400) for v in box)
        paras = ''.join('<a:p><a:r><a:rPr lang="en-US" altLang="ko-KR" sz="%d" dirty="0"><a:solidFill><a:schemeClr val="bg1"><a:lumMod val="65000"/></a:schemeClr></a:solidFill></a:rPr><a:t>%s</a:t></a:r></a:p>' % (size, esc(l)) for l in lines)
        sp = ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
              '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
              '<p:txBody><a:bodyPr wrap="square" lIns="0" rIns="0" tIns="0" bIns="0" anchor="b"><a:normAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody></p:sp>'
              % (self._next_shape_id(x), name, bx, by, bw, bh, paras))
        i = x.rindex('</p:spTree>')
        open(p, 'w', encoding='utf8').write(x[:i] + sp + x[i:])
        return name

    # ---- v16.7 (F3): 영상 자리 격자 ----
    def image_grid(self, slide_no, items, cols, x=6.0, y=1.05, w=3.9, h=6.0, gap=0.15, label_h=0.26):
        """items: [(label, comment), ...]. 라벨 + 점선 자리표("[넣을 영상] …")를 cols 열 격자로 놓는다.
        사용자가 영상을 직접 넣는 case review 표준 작업(5회 반복). 좌표는 인자 — 슬라이드별 판단은 호출자."""
        p = self._slide(slide_no); x_ = open(p, encoding='utf8').read()
        rows = -(-len(items) // cols)
        cw = (w - gap * (cols - 1)) / cols; ch = (h - gap * (rows - 1)) / rows
        E = 914400; out = []
        for k, (label, comment) in enumerate(items):
            cx = x + (k % cols) * (cw + gap); cy = y + (k // cols) * (ch + gap)
            sid = self._next_shape_id(x_) + 2 * k
            out.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="SeqLabel %d"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
                       '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
                       '<p:txBody><a:bodyPr wrap="square" lIns="0" rIns="0" tIns="0" bIns="0"/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US" altLang="ko-KR" sz="1200" b="1" dirty="0"><a:solidFill><a:schemeClr val="bg1"/></a:solidFill></a:rPr><a:t>%s</a:t></a:r></a:p></p:txBody></p:sp>'
                       % (sid, sid, int(cx * E), int(cy * E), int(cw * E), int(label_h * E), esc(label)))
            out.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="ImagePlaceholder %d"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                       '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                       '<a:solidFill><a:srgbClr val="3A3A3A"/></a:solidFill><a:ln w="19050"><a:solidFill><a:srgbClr val="FFC000"/></a:solidFill><a:prstDash val="dash"/></a:ln></p:spPr>'
                       '<p:txBody><a:bodyPr wrap="square" anchor="ctr"><a:normAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="ko-KR" altLang="en-US" sz="1100" dirty="0"><a:solidFill><a:srgbClr val="FFC000"/></a:solidFill></a:rPr><a:t>%s</a:t></a:r></a:p></p:txBody></p:sp>'
                       % (sid + 1, sid + 1, int(cx * E), int((cy + label_h + 0.02) * E), int(cw * E), int((ch - label_h - 0.02) * E), esc('[넣을 영상] ' + comment)))
        i = x_.rindex('</p:spTree>')
        open(p, 'w', encoding='utf8').write(x_[:i] + ''.join(out) + x_[i:])
        return len(items)

    def _next_shape_id(self, xml):
        ids = [int(v) for v in re.findall(r'<p:cNvPr id="(\d+)"', xml)]
        return (max(ids) if ids else 1) + 1

    def set_background(self, slide_no, rgb=None, scheme=None):
        """v16.10 (발표 W3): 슬라이드 배경을 단색으로. rgb='D2F6F6' 또는 scheme='bg2'. 둘 다 없으면 슬라이드 배경을 지워
        레이아웃·마스터 배경을 따른다. 반환: 이전에 슬라이드 배경이 있었는지."""
        p = self._slide(slide_no); x = open(p, encoding='utf8').read()
        had = '<p:bg>' in x
        x = re.sub(r'<p:bg>.*?</p:bg>', '', x, count=1, flags=re.S)
        if rgb or scheme:
            fill = '<a:srgbClr val="%s"/>' % rgb.lstrip('#').upper() if rgb else '<a:schemeClr val="%s"/>' % scheme
            x = re.sub(r'(<p:cSld\b[^>]*>)', r'\1<p:bg><p:bgPr><a:solidFill>%s</a:solidFill><a:effectLst/></p:bgPr></p:bg>' % fill, x, count=1)
        open(p, 'w', encoding='utf8').write(x)
        return had

    def bake_autofit(self, slide_no, shape=None):
        """v16.10 (발표 W1-3): normAutofit 의 fontScale·lnSpcReduction 을 실제 run 글자 크기와 줄 간격으로 적어 넣고 비율을 뺀다.
        PowerPoint 모양은 그대로이고, 자동 맞춤을 안 따르는 뷰어(Google Slides 등)에서도 같게 보인다. 크기는 run 에 적힌 값, 없으면
        레이아웃·마스터의 단계별 기본 크기(글상자는 1800), 줄 간격은 문단 → 레이아웃·마스터 단계별 값(없으면 100%%) − 축소분.
        반환: 바꾼 상자 수."""
        p = self._slide(slide_no); x = open(p, encoding='utf8').read(); n = 0
        def fix_sp(m):
            nonlocal n
            sp = m.group(0)
            if shape and 'name="%s"' % shape not in sp:
                return sp
            na = re.search(r'<a:normAutofit\b([^>]*)/>', sp)
            if not na or 'fontScale' not in na.group(1) and 'lnSpcReduction' not in na.group(1):
                return sp
            fs = int((re.search(r'fontScale="(\d+)"', na.group(1)) or [0, 100000])[1]) / 100000.0
            red = int((re.search(r'lnSpcReduction="(\d+)"', na.group(1)) or [0, 0])[1])
            ph = re.search(r'<p:ph\b([^>]*)/?>', sp)
            sizes = _body_level_sizes(self, slide_no, ph.group(1)) if ph else {}
            lns = _body_level_lnspc(self, slide_no, ph.group(1)) if ph else {}
            def para(pm):
                q = pm.group(0)
                lv = int((re.search(r'<a:pPr\b[^>]*\blvl="(\d)"', q) or [0, 0])[1])
                base = sizes.get(lv) or sizes.get(0) or 1800
                q = re.sub(r'(<a:(?:rPr|endParaRPr)\b[^>]*?\bsz=")(\d+)"', lambda mm: '%s%d"' % (mm.group(1), int(int(mm.group(2)) * fs)), q)
                q = re.sub(r'<a:(rPr|endParaRPr)\b((?:(?!\bsz=)[^>])*?)(/?)>', lambda mm: '<a:%s%s sz="%d"%s>' % (mm.group(1), mm.group(2), int(base * fs), mm.group(3)), q)
                q = re.sub(r'<a:r><a:t\b', '<a:r><a:rPr lang="ko-KR" sz="%d"/><a:t' % int(base * fs), q)
                if red:
                    own = re.search(r'<a:lnSpc><a:spcPct val="(\d+)"/></a:lnSpc>', q)
                    pts = re.search(r'<a:lnSpc><a:spcPts val="(\d+)"/></a:lnSpc>', q)
                    if pts:
                        # v16.32 (발표 D2): pt 로 고정된 줄 간격(Google 내보내기) — 전에는 spcPct 를 하나 더 넣어 lnSpc 가 두 개가 됐다.
                        # 명세 문구대로 lnSpcReduction 비율만 뺀다(글자 크기 비율은 곱하지 않는다 — PowerPoint 실제와 다를 수 있다)
                        q = q.replace(pts.group(0), '<a:lnSpc><a:spcPts val="%d"/></a:lnSpc>' % max(100, int(int(pts.group(1)) * (1 - red / 100000.0))), 1)
                        ln = None
                    else:
                        cur = int(own.group(1)) if own else lns.get(lv, lns.get(0, 100000))
                        ln = '<a:lnSpc><a:spcPct val="%d"/></a:lnSpc>' % max(10000, cur - red)
                    if ln is None:
                        pass
                    elif own:
                        q = q.replace(own.group(0), ln, 1)
                    elif re.search(r'<a:pPr\b[^>]*/>', q):
                        q = re.sub(r'<a:pPr\b([^>]*)/>', r'<a:pPr\1>%s</a:pPr>' % ln, q, count=1)
                    elif '<a:pPr' in q:
                        q = re.sub(r'(<a:pPr\b[^>]*>)', r'\1' + ln, q, count=1)
                    else:
                        q = q.replace('<a:p>', '<a:p><a:pPr>%s</a:pPr>' % ln, 1)
                return q
            sp = re.sub(r'<a:p>.*?</a:p>', para, sp, flags=re.S)
            sp = sp.replace(na.group(0), '<a:normAutofit/>', 1)
            n += 1
            return sp
        x = re.sub(r'<p:sp>(?:(?!</p:sp>).)*</p:sp>', fix_sp, x, flags=re.S)
        open(p, 'w', encoding='utf8').write(x)
        return n

    def clear_pictures(self, slide_no, labels=False, margin=0.15):
        """v16.7 (F2): 슬라이드의 <p:pic> 을 지우고, 그 슬라이드만 쓰던 media·rels 를 정리한다. 다른 슬라이드와
        공유된 media 는 남긴다(이걸 스크립트에서 os.remove 로 했다가 깨질 수 있었던 것이 V2). 반환: 지운 그림 수.
        labels=True (v16.7.1, MSK 수용검사 F2): 그림 bbox(여유 margin 인치) 안에 든 작은 도형(라벨·화살표·connector)도
        지운다. placeholder(<p:ph>)와 제목·본문은 건드리지 않는다 — base 영상 슬라이드를 틀로 쓸 때 sequence 라벨이
        새 자리표와 겹치던 문제."""
        p = self._slide(slide_no); x = open(p, encoding='utf8').read()
        pics = re.findall(r'<p:pic>.*?</p:pic>', x, re.S)
        if not pics:
            return 0
        rids = set(r for pm in pics for r in re.findall(r'r:embed="(rId\d+)"', pm))
        x, _ = _strip_pictures_xml(x, labels=labels, margin=margin)
        open(p, 'w', encoding='utf8').write(x)
        rp = self._slide_rels(slide_no)
        if os.path.exists(rp):
            rels = open(rp, encoding='utf8').read()
            for rid in rids:
                m = re.search(r'<Relationship [^>]*Id="%s"[^>]*/>' % rid, rels)
                if not m:
                    continue
                tgt = re.search(r'Target="([^"]+)"', m.group(0)).group(1)
                rels = rels.replace(m.group(0), '')
                fname = tgt.split('/')[-1]
                shared = any(fname in open(os.path.join(self.dir, 'ppt/slides/_rels', f), encoding='utf8').read()
                             for f in os.listdir(os.path.join(self.dir, 'ppt/slides/_rels')) if f != os.path.basename(rp))
                mp = os.path.join(self.dir, 'ppt/media', fname)
                if not shared and os.path.exists(mp):
                    os.remove(mp)
            open(rp, 'w', encoding='utf8').write(rels)
        return len(pics)

    def move_slide(self, slide_no, after=None, after_pos=None):
        """v16.7 (F1): 화면 순서만 바꾼다(sldIdLst). 파일·sldId·rId 는 그대로.
        **slide_no 와 after 는 모두 slide 파일 번호(slideN.xml 의 N)다 — 화면 위치가 아니다** (v16.7.1 명시, X1).
        화면 위치로 지정하려면 after_pos=k (k번째 화면 뒤, 0 이면 맨 앞). after=0 도 맨 앞.
        스크립트가 presentation.xml 의 <p:sldId> 를 문자열로 맞바꾸던 경계 위반(V1)을 대신한다."""
        if after_pos is not None:
            order = [sn for sn, _, _ in self.order()]
            after = 0 if after_pos <= 0 else order[min(after_pos, len(order)) - 1]
        if after is None:
            raise ValueError('after(파일 번호) 또는 after_pos(화면 위치) 중 하나를 줄 것')
        pxp = os.path.join(self.dir, 'ppt/presentation.xml'); d = open(pxp, encoding='utf8').read()
        ent = {sn: '<p:sldId id="%s" r:id="%s"/>' % (sid, rid) for sn, sid, rid in self.order()}
        if slide_no not in ent or (after and after not in ent) or after == slide_no:
            raise ValueError('move_slide: slide %s / after %s' % (slide_no, after))
        d = d.replace(ent[slide_no], '', 1)
        if after:
            d = d.replace(ent[after], ent[after] + ent[slide_no], 1)
        else:
            d = d.replace('<p:sldIdLst>', '<p:sldIdLst>' + ent[slide_no], 1)
        open(pxp, 'w', encoding='utf8').write(d)
        return [sn for sn, _, _ in self.order()]

    def sld_id(self, slide_no):
        """v16.7 (N2): 파일 번호 → sldId. PowerPoint 는 저장할 때 파일 번호를 화면 순서로 다시 매기지만 sldId 는 유지한다."""
        for sn, sid, _ in self.order():
            if sn == slide_no:
                return int(sid)
        return None

    def slide_by_id(self, sld_id):
        for sn, sid, _ in self.order():
            if int(sid) == int(sld_id):
                return sn
        return None

    def remove_slide(self, slide_no):
        """슬라이드를 순서에서 뺀다. 파일은 남기되 presentation 에서 참조를 끊는다."""
        pxp = os.path.join(self.dir, 'ppt/presentation.xml')
        d = open(pxp, encoding='utf8').read()
        for sn, sid, rid in self.order():
            if sn == slide_no:
                d = d.replace('<p:sldId id="%s" r:id="%s"/>' % (sid, rid), '')
                open(pxp, 'w', encoding='utf8').write(d)
                return True
        return False

    def purge_orphans(self):
        """v16.6.1 (전평 수용검사 2-3): 순서(sldIdLst)에 없는 슬라이드 파일과 그 rels·노트, 어느 슬라이드도 쓰지 않는
        미디어를 지우고 [Content_Types].xml·presentation.xml.rels 의 항목을 정리한다. `remove_slide` 나 베이스 덱을 비운 뒤
        저장 전에 부른다. 반환 {'slides': n, 'notes': n, 'media': n}."""
        live = {sn for sn, _, _ in self.order() if sn}
        sdir = os.path.join(self.dir, 'ppt/slides')
        orphan = sorted(int(m.group(1)) for f in os.listdir(sdir) for m in [re.match(r'slide(\d+)\.xml$', f)] if m and int(m.group(1)) not in live)
        ct_p = os.path.join(self.dir, '[Content_Types].xml'); ct = open(ct_p, encoding='utf8').read()
        prp = os.path.join(self.dir, 'ppt/_rels/presentation.xml.rels'); pr = open(prp, encoding='utf8').read()
        n_notes = 0
        for sn in orphan:
            nn = self.notes_no(sn)
            for f in (self._slide(sn), self._slide_rels(sn)):
                if os.path.exists(f):
                    os.remove(f)
            ct = re.sub(r'<Override PartName="/ppt/slides/slide%d\.xml"[^>]*/>' % sn, '', ct)
            pr = re.sub(r'<Relationship [^>]*Target="slides/slide%d\.xml"[^>]*/>' % sn, '', pr)
            if nn:
                still = any(self.notes_no(o) == nn for o in live)
                if not still:
                    for f in (os.path.join(self.dir, 'ppt/notesSlides/notesSlide%d.xml' % nn),
                              os.path.join(self.dir, 'ppt/notesSlides/_rels/notesSlide%d.xml.rels' % nn)):
                        if os.path.exists(f):
                            os.remove(f); n_notes += f.endswith('.xml')
                    ct = re.sub(r'<Override PartName="/ppt/notesSlides/notesSlide%d\.xml"[^>]*/>' % nn, '', ct)
        open(ct_p, 'w', encoding='utf8').write(ct); open(prp, 'w', encoding='utf8').write(pr)
        # 미디어: 남은 모든 rels(슬라이드·레이아웃·마스터·노트) 에서 참조되는 것만 남긴다
        used = set()
        for root, _, files in os.walk(os.path.join(self.dir, 'ppt')):
            for f in files:
                if f.endswith('.rels'):
                    used.update(re.findall(r'media/([\w.\-]+)', open(os.path.join(root, f), encoding='utf8').read()))
        mdir = os.path.join(self.dir, 'ppt/media'); n_media = 0
        if os.path.isdir(mdir):
            for f in os.listdir(mdir):
                if f not in used:
                    os.remove(os.path.join(mdir, f)); n_media += 1
        return {'slides': len(orphan), 'notes': n_notes, 'media': n_media}

    def _next_notes_no(self):
        base = os.path.join(self.dir, 'ppt/notesSlides')
        os.makedirs(os.path.join(base, '_rels'), exist_ok=True)
        used = [int(m.group(1)) for f in os.listdir(base)
                for m in [re.fullmatch(r'notesSlide(\d+)\.xml', f)] if m]
        return (max(used) if used else 0) + 1

    def _ensure_default_ct(self, ext):
        ct = os.path.join(self.dir, '[Content_Types].xml')
        c = open(ct, encoding='utf8').read()
        if re.search(r'<Default Extension="%s"' % re.escape(ext), c, re.I):
            return
        mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                'gif': 'image/gif', 'bmp': 'image/bmp', 'tiff': 'image/tiff',
                'emf': 'image/x-emf', 'wmf': 'image/x-wmf'}.get(ext.lower(), 'image/' + ext)
        c = c.replace('<Default Extension="rels"',
                      '<Default Extension="%s" ContentType="%s"/><Default Extension="rels"'
                      % (ext, mime), 1)
        open(ct, 'w', encoding='utf8').write(c)

    def _register_slide(self, slide_no, notes_no, after):
        """content types / presentation rels / sldIdLst 에 새 슬라이드를 등록."""
        ct = os.path.join(self.dir, '[Content_Types].xml')
        c = open(ct, encoding='utf8').read()
        c = c.replace('</Types>',
            '<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
            '<Override PartName="/ppt/notesSlides/notesSlide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>'
            '</Types>' % (slide_no, notes_no))
        open(ct, 'w', encoding='utf8').write(c)

        prp = os.path.join(self.dir, 'ppt/_rels/presentation.xml.rels')
        d = open(prp, encoding='utf8').read()
        used = [int(x) for x in re.findall(r'Id="rId(\d+)"', d)]
        rid = 'rId%d' % (max(used) + 1)
        open(prp, 'w', encoding='utf8').write(d.replace(
            '</Relationships>',
            '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide%d.xml"/></Relationships>'
            % (rid, slide_no)))

        pxp = os.path.join(self.dir, 'ppt/presentation.xml')
        d = open(pxp, encoding='utf8').read()
        ids = [int(x) for x in re.findall(r'<p:sldId id="(\d+)"', d)]
        new_entry = '<p:sldId id="%d" r:id="%s"/>' % ((max(ids) if ids else 255) + 1, rid)
        if after is None or after == 0:
            d = d.replace('<p:sldIdLst>', '<p:sldIdLst>' + new_entry, 1)
        else:
            anchor_e = None
            for sn, sid, arid in self.order():
                if sn == after:
                    anchor_e = '<p:sldId id="%s" r:id="%s"/>' % (sid, arid)
                    break
            if anchor_e is None or anchor_e not in d:
                raise ValueError('삽입 위치를 찾지 못함: after=%s' % after)
            d = d.replace(anchor_e, anchor_e + new_entry)
        open(pxp, 'w', encoding='utf8').write(d)

    # ---- v16.6: 텍스트 안전 치환 (학회 덱 회신 요청 8) ----
    def settext(self, slide_no, old, new, shape=None, notes=False, delete_para=False, dry_run=False, whole=False, strict=False, zone=None):
        """본문 또는 노트의 텍스트를 안전하게 치환한다.

        규칙 (학회 제출본 수정 때 1회용 스크립트 240줄로 하던 일을 명령으로):
          - old 는 한 <a:t> 안에서 **정확히 1회** 매치돼야 한다. 0회·2회 이상은 거부(치환 안 함).
            run 경계로 쪼개진 문장은 잡지 못한다 — 그때는 unpack 후 XML 을 직접 본다.
          - shape 을 주면 그 도형(name 속성) 안에서만 찾는다.
          - notes=True 면 그 슬라이드의 노트를 대상으로.
          - delete_para=True 면 new 를 무시하고 old 가 든 문단(<a:p>)을 통째로 지운다.
          - dry_run=True 면 파일을 쓰지 않고 결과만 돌려준다.
        도형 삭제·좌표 재배치는 하지 않는다(발표 회신도 경고만 권함).
        반환 {'ok', 'count', 'where', 'before', 'after', 'text_before', 'text_after'}"""
        if notes:
            nn = self.notes_no(slide_no)
            if not nn:
                return {'ok': False, 'reason': '노트 없음', 'count': 0}
            path = os.path.join(self.dir, 'ppt/notesSlides/notesSlide%d.xml' % nn)
        else:
            path = self._slide(slide_no)
        x = open(path, encoding='utf8').read()
        region = (0, len(x))
        if notes and zone:
            # v16.17 (발표 H2): 노트의 한 구역만 — 'script'(대본) / 'tips'(참고) / 'memo'(기존 메모). 새 참고에 원작자 메모와 같은
            # 문구가 있어 2회 매치로 거부되던 것
            paras = self.notes_paragraphs(slide_no)
            mi = next((i for i, q in enumerate(paras) if _is_memo_sep(q['text'])), len(paras))
            ti = next((i for i, q in enumerate(paras[:mi]) if _is_cutoff_line(q['text']) or _looks_like_cutoff(q['text'])), mi)
            rng = {'script': (0, ti), 'tips': (ti + 1, mi), 'memo': (mi + 1, len(paras))}.get(zone)
            if rng is None:
                raise ValueError("zone 은 'script' / 'tips' / 'memo'")
            sel = paras[rng[0]:rng[1]]
            if not sel:
                res = {'ok': False, 'reason': '노트에 %s 구역이 없음' % zone, 'count': 0}
                if strict:
                    raise ValueError('settext 거부 — ' + res['reason'])
                return res
            region = (sel[0]['start'], sel[-1]['end'])
        if shape and not notes:
            m = re.search(r'<p:(sp|pic)>(?:(?!</p:\1>).)*?name="%s"(?:(?!</p:\1>).)*</p:\1>' % re.escape(shape), x, re.S)
            if not m:
                if strict:
                    raise ValueError('settext 거부 — 도형 "%s" 없음' % shape)
                return {'ok': False, 'reason': '도형 "%s" 없음' % shape, 'count': 0}
            region = (m.start(), m.end())
        seg = x[region[0]:region[1]]
        old_x = esc(old)
        if whole:   # v16.15 (발표 R2): 글 조각 **전체**가 old 인 곳만 — 'Denonvillier' 와 'Denonvilliers' 가 함께 있을 때
            hits = [m for m in re.finditer(r'<a:t[^>]*>([^<]*)</a:t>', seg) if m.group(1) == old_x]
            count = len(hits)
        else:
            hits = [m for m in re.finditer(r'<a:t[^>]*>([^<]*)</a:t>', seg) if old_x in m.group(1)]
            count = sum(m.group(1).count(old_x) for m in hits)
        if count != 1:
            res = {'ok': False, 'reason': '매치 %d회 — 정확히 1회여야 함%s (run 경계로 쪼개졌으면 unpack 후 XML 확인)'
                   % (count, '' if whole else '; 조각 전체가 old 인 곳만이면 whole=True'), 'count': count}
            if strict:   # v16.15 (발표 R5): 돌려받은 값을 안 보는 덱 스크립트용
                raise ValueError('settext 거부 — %s: %r' % (res['reason'], old))
            return res
        m = hits[0]
        text_before = ''.join(re.findall(r'<a:t[^>]*>([^<]*)</a:t>', seg))
        if delete_para:
            ps = seg.rfind('<a:p>', 0, m.start()); pe = seg.find('</a:p>', m.end()) + len('</a:p>')
            if ps == -1 or pe < len('</a:p>'):
                return {'ok': False, 'reason': '문단 경계를 찾지 못함', 'count': 1}
            new_seg = seg[:ps] + seg[pe:]
            after_txt = ''
        else:
            new_seg = seg[:m.start(1)] + m.group(1).replace(old_x, esc(new), 1) + seg[m.end(1):]
            after_txt = m.group(1).replace(old_x, esc(new), 1)
        text_after = ''.join(re.findall(r'<a:t[^>]*>([^<]*)</a:t>', new_seg))
        res = {'ok': True, 'count': 1, 'where': '%s%s' % (self.label(slide_no), ' 노트' if notes else ''),
               'before': m.group(1), 'after': after_txt, 'text_before': text_before, 'text_after': text_after,
               'dry_run': dry_run}
        if not dry_run:
            open(path, 'w', encoding='utf8').write(x[:region[0]] + new_seg + x[region[1]:])
        return res

    def strip_color(self, slide_no, hexcolor='FF0000'):
        """본문 run 의 특정 solidFill 색을 제거해 상속색으로 되돌린다 (전평 build_lgi.strip_answer 일반형, v16.6).
        시험 풀이 덱의 '정답 빨강'을 지워 문제 제시용 슬라이드를 만드는 데 쓴다. 반환: 제거 수.
        v16.45 (코드 리뷰 14): **글자 색만** — run·문단 끝·목록 기본 글자 속성(`a:rPr`·`a:endParaRPr`·`a:defRPr`)의 바로 아래 채움.
        도형 채움·선(병변 화살표·동그라미)과 글자 외곽선(`a:ln`)은 두고, 표기(소문자 `ff0000`, 줄바꿈·들여쓰기,
        `lumMod` 같은 자식이 붙은 색)가 달라도 잡는다. 전에는 붙여 쓴 한 모양만 잡으면서 파일 전체에서 지웠다."""
        p = self._slide(slide_no); x = open(p, encoding='utf8').read()
        fill = re.compile(r'<a:solidFill>\s*<a:srgbClr\s+val="%s"\s*(?:/>|>.*?</a:srgbClr>)\s*</a:solidFill>' % re.escape(hexcolor), re.S | re.I)
        ln = re.compile(r'<a:ln\b[^>]*/>|<a:ln\b.*?</a:ln>', re.S)
        n = [0]

        def props(m):
            body, out, k = m.group(3), [], 0
            for lm in ln.finditer(body):             # 외곽선 안의 채움은 글자 색이 아니다
                out.append(fill.subn('', body[k:lm.start()])); out.append((lm.group(0), 0)); k = lm.end()
            out.append(fill.subn('', body[k:]))
            n[0] += sum(c for _, c in out)
            return m.group(1) + ''.join(t for t, _ in out) + m.group(4)
        y = re.sub(r'(<a:(rPr|endParaRPr|defRPr)\b[^>]*(?<!/)>)(.*?)(</a:\2>)', props, x, flags=re.S)
        if n[0]:
            open(p, 'w', encoding='utf8').write(y)
        return n[0]

    def fix_title_box(self, slide_no, cy):
        """제목 placeholder(type="title")의 저장 높이를 cy(EMU)로 맞추고 normAutofit 을 켠다 (전평 build_lgi 흡수, v16.6).
        답안지에서 온 슬라이드는 두 줄 제목인데 높이가 한 줄분이라 회색 띠 밖으로 나갔다.
        xfrm 이 없는(레이아웃 상속) 제목 상자는 건드리지 않고 False 를 돌려준다 — 그런 상자의 높이를
        정규식으로 고치려다 그림 xfrm 을 잡은 사고가 있었다."""
        p = self._slide(slide_no); x = open(p, encoding='utf8').read()
        m = re.search(r'<p:sp>(?:(?!</p:sp>).)*?type="title"(?:(?!</p:sp>).)*</p:sp>', x, re.S)
        if not m:
            return False
        seg = m.group(0)
        if '<a:xfrm>' not in seg:
            return False
        seg2 = re.sub(r'(<a:xfrm>\s*<a:off[^/]*/>\s*<a:ext cx="\d+" cy=")\d+(")', r'\g<1>%d\2' % cy, seg, 1)
        if '<a:normAutofit' not in seg2:
            seg2 = re.sub(r'<a:bodyPr([^>]*)/>', r'<a:bodyPr\1><a:normAutofit/></a:bodyPr>', seg2, 1)
        open(p, 'w', encoding='utf8').write(x[:m.start()] + seg2 + x[m.end():])
        return True

    def check_image_aspect(self, tol=0.04):
        """그림의 표시 비율이 원본 픽셀 비율과 다르면(찌그러짐) 보고. srcRect 크롭은 반영."""
        try:
            from PIL import Image
        except ImportError:
            return []
        probs = []
        media = os.path.join(self.dir, 'ppt/media')
        for sn in self.slide_numbers():
            rels = self._slide_rels(sn)
            if not os.path.exists(rels):
                continue
            rmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="\.\./media/([^"]+)"',
                                   open(rels, encoding='utf8').read()))
            x = open(self._slide(sn), encoding='utf8').read()
            for m in re.finditer(r'<p:pic>.*?</p:pic>', x, re.S):
                pic = m.group(0)
                rid = re.search(r'r:embed="(rId\d+)"', pic)
                ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', pic)
                if not rid or not ext or rid.group(1) not in rmap:
                    continue
                f = os.path.join(media, rmap[rid.group(1)])
                if not os.path.exists(f) or f.lower().endswith(('.emf', '.wmf', '.svg')):
                    continue
                try:
                    w, h = Image.open(f).size
                except Exception:
                    continue
                sr = re.search(r'<a:srcRect([^/]*)/>', pic)
                l = t = r = b = 0
                if sr:
                    g = dict(re.findall(r'(\w)="(-?\d+)"', sr.group(1)))
                    l, t, r, b = (int(g.get(k, 0)) / 100000.0 for k in 'ltrb')
                w_eff = w * (1 - l - r)
                h_eff = h * (1 - t - b)
                if w_eff <= 0 or h_eff <= 0:
                    continue
                shown = int(ext.group(1)) / float(ext.group(2))
                native = w_eff / h_eff
                if abs(shown / native - 1) > tol:
                    probs.append('slide%d: 그림 %s 비율 왜곡 (표시 %.2f vs 원본 %.2f)'
                                 % (sn, rmap[rid.group(1)], shown, native))
        return probs

    def check_near_duplicate_bodies(self, threshold=0.8):
        """본문(제목 제외)이 다른 슬라이드와 거의 같은 경우. 같은 그림의 연속 패널은
        의도된 것일 수 있으니 판정은 사람이 한다."""
        import difflib
        bodies = {}
        for sn in self.slide_numbers():
            t = [x.strip() for x in self.texts(sn)[1:] if len(x.strip()) > 3]
            if len(' '.join(t)) > 40:
                bodies[sn] = ' '.join(t)
        probs, seen = [], set()
        keys = sorted(bodies)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                r = difflib.SequenceMatcher(None, bodies[a], bodies[b]).ratio()
                if r >= threshold and (a, b) not in seen:
                    seen.add((a, b))
                    probs.append('slide%d 와 slide%d 의 본문이 거의 같음 (유사도 %.2f) — 반복인지 확인'
                                 % (a, b, r))
        return probs

    def audit(self, stream=sys.stdout):
        w, h = self.slide_size()
        order = self.order()
        print('슬라이드 크기: %d x %d EMU (%s)' % (
            w, h, '4:3' if abs(w / h - 4 / 3) < 0.02 else '16:9'), file=stream)
        print('총 %d장\n' % len(order), file=stream)

        seen_notes, seen_imgs = {}, {}
        problems = []
        for pos, (sn, _, _) in enumerate(order, 1):
            if sn is None:
                continue
            t = self.texts(sn)
            nt = self.notes(sn)
            im = self.images(sn)
            nn = self.notes_no(sn)
            print('--- [%02d] slide%d  notes=%s  media=%s' % (pos, sn, nn, im or '-'),
                  file=stream)
            orph = self.orphan_images(sn)
            if orph:
                problems.append('[참고] slide%d 배치되지 않은 이미지 rel: %s' % (sn, ', '.join(orph)))
            print('    TEXT : %s' % ' | '.join(t)[:400], file=stream)
            print('    NOTES: %s' % ' '.join(nt)[:400], file=stream)

            key = ' '.join(nt).strip()
            if key:
                if key in seen_notes:
                    problems.append('slide%d 의 노트가 slide%d 와 동일' % (sn, seen_notes[key]))
                else:
                    seen_notes[key] = sn
            for f in im:
                seen_imgs.setdefault(f, []).append(sn)
            if not t:
                problems.append('slide%d 에 텍스트가 전혀 없음' % sn)
            # v16.7.1 (MSK 수용검사 P1): 표 칸의 '—'(값 없음)·대시류는 잔재가 아니다; 빈 불릿 검사도 문단 단위로
            ptx = self.para_texts(sn, tables=False)
            if any(len(x.strip()) == 1 and x.strip() not in _DASHES for x in ptx):
                problems.append('slide%d 에 한 글자 잔재 텍스트' % sn)
            if any(x.strip() in ('-', '·', '•') for x in ptx):
                problems.append('slide%d 에 빈 불릿 자리표시자' % sn)
            if not nt:
                problems.append('slide%d 노트 비어 있음' % sn)

        for f, slides in seen_imgs.items():
            if len(slides) > 1:
                problems.append('이미지 %s 가 slide %s 에 중복 사용' %
                                (f, ', '.join(map(str, slides))))
        problems.extend(self.check_image_aspect())
        problems.extend(self.check_near_duplicate_bodies())

        print('\n=== 제목 흐름 (이것만 읽어도 논리가 이어져야 한다) ===', file=stream)
        for pos, (sn, _, _) in enumerate(order, 1):
            if sn is not None:
                print('  %2d. %s' % (pos, (self.texts(sn) or ['(제목 없음)'])[0][:80]), file=stream)

        print('\n=== 점검 결과 ===', file=stream)
        if problems:
            for p in problems:
                print('  [!] %s' % p, file=stream)
        else:
            print('  특이사항 없음', file=stream)
        return problems



# ----------------------------------------------------------------------------
# 밀도 / 시간 규격  (DECK_SPEC.md §3 참조)
#
#  근거
#   * 멀티미디어 학습 연구: 투사되는 글자는 분당 20단어를 넘기지 않는 것이 좋다
#   * 한 문단이 3줄 이상이면 절반 이상의 청중이 읽기를 포기한다
#   * 본문 최소 16pt, 제목 28pt 이상이어야 뒷줄에서 읽힌다
#   * Assertion-Evidence: 영상 슬라이드는 문장형 헤드라인 + 영상, 불릿 금지
# ----------------------------------------------------------------------------

# 슬라이드 종류별 상한. word 는 영어 단어 + 한글 2글자당 1단어로 환산한 값.
DENSITY = {
    # --- 케이스 발표 (quiz / case review) ---
    'image':      {'words': 25,  'paras': 3,  'key_phrases': 2},   # 영상 + 헤드라인
    'history':    {'words': 45,  'paras': 5,  'key_phrases': 2},   # 케이스 제시
    'findings':   {'words': 95,  'paras': 12, 'key_phrases': 4},   # Radiologic findings
    'review':     {'words': 115, 'paras': 14, 'key_phrases': 4},   # Disease review / 배경 서술
    'summary':    {'words': 80,  'paras': 8,  'key_phrases': 4},   # Take home / Conclusion
    # --- 학회 발표 · journal review (v11 추가) ---
    'title':      {'words': 40,  'paras': 6,  'key_phrases': 0},   # 표지 (제목·저자·소속)
    'divider':    {'words': 12,  'paras': 2,  'key_phrases': 0},   # 섹션 구분 (Results / Discussion)
    'method':     {'words': 90,  'paras': 10, 'key_phrases': 3},   # 대상·획득·분석
    'result':     {'words': 70,  'paras': 9,  'key_phrases': 4},   # 그림·표 + 수치 헤드라인
    'limitation': {'words': 110, 'paras': 14, 'key_phrases': 3},   # 카드형 Limitations
    'closing':    {'words': 80,  'paras': 12, 'key_phrases': 0},   # Acknowledgments / 연락처
}

# 제목 키워드 → 종류. 앞에서부터 처음 맞는 것. classify() 가 쓴다.
KIND_KEYWORDS = [
    # v16.7 (MSK 회신 N4): disease review 에 문헌 그림이 들어가면 그림 때문에 result 로 기울었다 — 제목이 review 면 먼저 review
    ('review',     ('review', '리뷰', 'disease', 'overview', 'background', 'anatomy', 'classification', 'pathophysiology')),
    ('summary',    ('take home', 'summary', 'conclusion', 'key message', 'practice')),
    ('findings',   ('radiologic findings', 'radiographic findings', 'imaging findings')),
    ('limitation', ('limitation', 'caveat', 'weakness')),
    ('closing',    ('acknowledg', 'thank you', 'contact', 'funding', 'disclosure')),
    ('method',     ('method', 'material', 'participant', 'patient', 'cohort', 'acquisition',
                    'protocol', 'analysis', 'study design', 'design', 'statistic')),
    ('result',     ('result', 'effect size', 'correlat', 'comparison', 'across stage',
                    'key results', 'table ', 'figure ')),
]

# 노트 첫 줄에 [kind: result] 처럼 적으면 제목 추정보다 우선한다
_KIND_TAG = re.compile(r'\[\s*kind\s*[:=]\s*(\w+)\s*\]', re.I)

MIN_BODY_PT = 16          # sz=1600
MIN_TITLE_PT = 24         # sz=2400
MAX_PARA_LINES = 2        # 한 문단 2줄 이내
ENGLISH_ONLY_KINDS = ('journal review', 'case review', 'quiz review', 'pathology review', 'anatomy seminar')   # v16.7.3 (T1)
_DECK_TAG = re.compile(r'\[\s*deck\s*[:=]\s*([^\]]+)\]', re.I)


def deck_kind(deck, override=None):
    """덱 종류: --deck-kind 인자 > 첫 화면 노트의 [deck: case review] 태그 > None. 슬라이드 언어 규칙(DECK_SPEC §0 A-1)에 쓴다."""
    if override:
        return override.strip().lower()
    first = [sn for sn, _, _ in deck.order() if sn]
    if first:
        for ln in deck.notes(first[0])[:3]:
            m = _DECK_TAG.search(ln)
            if m:
                return m.group(1).strip().lower()
    return None


TABLE_MIN_PT = 12   # v16.7.2 (Y1): 표 칸 최소 글씨. 본문 16pt 와 별도
READ_WPM = 20             # 청중이 슬라이드 글자를 읽는 속도 (분당 단어)
SPEAK_KO_CPM = 280        # 한국어 발표 속도 (분당 글자)
SPEAK_EN_WPM = 115        # 영어 발표 속도 (분당 단어).
                          # 130 은 원어민 기준. 비원어민이 학회에서 또박또박
                          # 읽으면 100~115 가 현실적이라 보수적으로 잡는다.


# 대본 안에서 "발표 중 읽지 않는" 블록의 시작을 알리는 표지
NOTES_CUTOFF = ('ANTICIPATED QUESTIONS', '예상 질문', 'Q&A', 'NOT SPOKEN',
                'BACKUP', '백업', '기존 메모', '기존 노트')


def _is_cutoff_line(t):
    """예상 질문 블록의 **표지 줄**인지 판정.

    본문 문장 안에 'Q&A' 가 들어간 것만으로 뒤를 다 잘라내면 안 된다
    (실제로 '...Q&A 에서 자주 나오는...' 한 줄 때문에 대본 전체가 시간 계산에서
    빠진 적이 있다). 표지 줄은 짧고, 마커로 시작하거나 괄호·별표로 감싸여 있다.
    """
    # 앞뒤 장식(별표·괄호·대시·박스문자 ─ 등)을 전부 벗긴다. 실제 덱의 표지 줄:
    #   '────── ANTICIPATED QUESTIONS (not spoken) ──────'
    s = re.sub(r'^[\W_]+|[\W_]+$', '', t.strip())
    up = s.upper()
    for k in NOTES_CUTOFF:
        ku = k.upper()
        if up == ku or up.startswith(ku) and len(s) <= len(k) + 20:
            return True
    # v16.7 (MSK 회신 N1): 장식(─ 등)으로 감싼 짧은 줄 **안에** 표지어가 있으면 인정.
    # '─────  [참고 — NOT SPOKEN]  ─────' 가 표지로 인정되지 않아 참고 블록이 낭독 시간에 들어간 사고(2.7배 과대).
    # 본문 속 'Q&A' 오절단을 막는 원래 조건(짧은 줄 + 장식)은 유지된다.
    if _looks_like_cutoff(t) and any(k.upper() in up for k in NOTES_CUTOFF):
        return True
    return False


def _looks_like_cutoff(t):
    """장식 문자(─ ═ - = * ─ 등) 5개 이상이고 60자 이하인 줄 — 표지처럼 보인다."""
    t = t.strip()
    return len(t) <= 60 and len(re.findall(r'[\u2500-\u257f=\-\*_#~]', t)) >= 5


_MC_OPTION = re.compile(r'^[①-⑩㉠-㉻ⓐ-ⓩ]|^\(?[1-5a-eA-E]\)\s')   # 객관식 보기 줄 (v16.7.1)
_AT = re.compile(r'<a:t(?:\s[^>]*)?>([^<]*)</a:t>')   # v16.9: xml:space 등 속성이 붙은 <a:t> 도
_DASHES = ('—', '–', '-', '·', '•', '―')   # 표 칸 '값 없음' 표시류 — 잔재 아님 (v16.7.1)
NOTES_SEP = '───────── NOT SPOKEN · 참고 ─────────'
NOTES_SEP_MEMO = '───────── NOT SPOKEN · 기존 메모 ─────────'   # v16.9: 원작자 메모 구역 표지. 순서는 대본 → 참고 → 기존 메모   # v16.7 (S1·F4): 대본/참고 공식 표지. set_notes(n, script, tips) 가 넣는다


def _spoken_notes(lines):
    """실제로 낭독하는 부분만 남긴다. 예상 질문 블록은 시간 계산에서 제외."""
    out = []
    for t in lines:
        if _is_cutoff_line(t):
            break
        out.append(t)
    return out


def _is_memo_sep(t):
    """'NOT SPOKEN · 기존 메모' 류 표지 (v16.9). 옛 형식 '────── 기존 메모 ──────'(영상의학 v1 대본 덱) 도 인정.
    v16.16 (발표 P1): 변형 '────── 기존 노트 (작성자) ──────'(물리 덱) 도 — 못 알아봐 restore-memo 가 서식 없는 옛 메모 사본을
    대본 쪽에 남긴 채 원본 메모를 또 붙였고, normalize-notes 는 이 줄을 참고 표지로 바꿨다."""
    return (_is_cutoff_line(t) or _looks_like_cutoff(t)) and bool(re.search(r'기존\s*(?:메모|노트)|원작자|ORIGINAL', t, re.I))


def _cutoff_status(lines):
    """v16.7: ('cut'|'none'|'nearmiss', 줄). nearmiss = 표지처럼 보이는데 인정되지 않은 줄."""
    for t in lines:
        if _is_cutoff_line(t):
            return 'cut', t
    for t in lines:
        if _looks_like_cutoff(t) and len(t.strip()) > 10:
            return 'nearmiss', t
    return 'none', ''


def _is_reference(text):
    """참고문헌 줄 판별. 밀도·최소글씨 검사에서 제외한다."""
    t = text.strip()
    if len(t) < 12:
        return False
    return bool(re.search(r'\b(et al|\d{4};\s*\d+|doi|PMID)\b', t, re.I))


def _weighted_words(text):
    """영어 단어 + 한글 2글자당 1단어로 환산."""
    ko = len(re.findall(r'[\uac00-\ud7a3]', text))
    en = len(re.findall(r'[A-Za-z][A-Za-z\-/]*', text))
    return en + ko / 2.0


def _est_lines(text, size_pt, width_emu):
    """렌더 줄 수 근사. Calibri bold 기준 글자폭 ~0.5em."""
    if not text.strip():
        return 0
    char_emu = size_pt * 12700 * 0.5
    per_line = max(10, int(width_emu / char_emu))
    ko = len(re.findall(r'[\uac00-\ud7a3]', text))
    width_units = len(text) + ko          # 한글은 2배 폭
    return max(1, -(-width_units // per_line))


def classify_why(deck, slide_no, pos=None, total=None):
    """v16.7: classify 와 같되 판정 근거 문자열을 함께 돌려준다 — lint 가 '글자량 초과' 에 붙인다."""
    notes = deck.notes(slide_no)
    for ln in notes[:3]:
        m = _KIND_TAG.search(ln)
        if m and m.group(1).lower() in DENSITY:
            return m.group(1).lower(), '[kind:] 태그'
    texts = [t for t in deck.texts(slide_no) if t.strip()]
    title = (texts[0] if texts else '').lower()
    for kind, keys in KIND_KEYWORDS:
        hit = [k for k in keys if k in title]
        if hit:
            k2 = classify(deck, slide_no, pos, total)
            return k2, '제목 "%s"' % hit[0] if k2 == kind else '제목 "%s" 이나 구조상 %s' % (hit[0], k2)
    k2 = classify(deck, slide_no, pos, total)
    return k2, ('그림 %s · 본문 %d단어 → 구조 추정' % ('있음' if deck.images(slide_no) else '없음', _weighted_words(' '.join(texts[1:]))))


def classify(deck, slide_no, pos=None, total=None):
    """슬라이드 종류 추정.

    우선순위: 노트의 [kind: xxx] 태그 > 제목 키워드 > 위치·구조 휴리스틱.
    학회 발표 덱에서 결과 슬라이드가 'history' 로 잡혀 45단어 상한이 적용되던 문제(v10)를
    고치기 위해 종류를 늘리고 명시 태그를 두었다. 제목이 비표준이면 태그를 쓰는 편이 확실하다.
    """
    notes = deck.notes(slide_no)
    for ln in notes[:3]:
        m = _KIND_TAG.search(ln)
        if m and m.group(1).lower() in DENSITY:
            return m.group(1).lower()

    texts = [t for t in deck.texts(slide_no) if t.strip()]
    title = (texts[0] if texts else '').lower()
    has_img = bool(deck.images(slide_no))
    wt = _weighted_words(' '.join(texts))

    body_wt = _weighted_words(' '.join(texts[1:]))
    if pos == 1 or (pos is None and slide_no == 1 and not has_img and wt <= 40):
        return 'title'
    for kind, keys in KIND_KEYWORDS:
        if any(k in title for k in keys):
            # 'Results' 처럼 제목뿐인 섹션 구분 슬라이드는 result 가 아니라 divider
            if kind == 'result' and not has_img and body_wt <= 4:
                return 'divider'
            return kind
    if not has_img and body_wt <= 4:
        return 'divider'
    if has_img:
        # 그림 + 수치가 2개 이상이면 케이스 제시가 아니라 결과 슬라이드다
        if len(_numbers(' '.join(texts))) >= 2:
            return 'result'
        return 'history' if wt > 25 else 'image'
    return 'review'


def lint(deck, stream=sys.stdout, deck_kind_override=None):
    """밀도·시간·색 예산 점검. (문제목록, 요약dict) 반환."""
    body_w, _ = deck.slide_size()
    body_w -= 328246
    problems = []
    total_read = 0.0
    total_speak = 0.0
    rows = []
    n_total = len(deck.order())
    n_tagged = sum(1 for sn in deck.slide_numbers() if any(_KIND_TAG.search(ln) for ln in deck.notes(sn)[:3]))

    for pos, (sn, _, _) in enumerate(deck.order(), 1):
        if sn is None:
            continue
        xml = open(deck._slide(sn), encoding='utf8').read()
        kind, why = classify_why(deck, sn, pos=pos, total=n_total)
        cap = DENSITY[kind]

        # 본문 문단 추출 (제목 제외). v16.7.1 (X2): 캡션·인용·라벨 상자(이름에 caption/cite/label, LitCaption N 등)는
        # 글씨 크기 검사에서 뺀다 — DECK_SPEC §5 캡션(출처·환자·modality)은 본문이 아니다
        xml_body = re.sub(r'<p:sp>(?:(?!</p:sp>).)*?name="[^"]*(?:[Cc]aption|[Cc]ite|SeqLabel|LitLabel|ImagePlaceholder)[^"]*".*?</p:sp>', '', xml, flags=re.S)
        # v16.7.2 (Y1): 표 칸은 본문 16pt 기준이 아니라 표 기준(TABLE_MIN_PT)으로 따로 본다
        tbl_sizes = [int(v) for t in re.findall(r'<a:tbl>.*?</a:tbl>', xml_body, re.S) for v in re.findall(r'sz="(\d+)"', t)]
        xml_body = re.sub(r'<a:tbl>.*?</a:tbl>', '', xml_body, flags=re.S)
        paras = re.findall(r'<a:p>(.*?)</a:p>', xml_body, re.S)
        title_txt = ' '.join(deck.texts(sn)[:1])
        body_paras = []
        for pa in paras:
            t = ''.join(re.findall(r'<a:t>([^<]*)</a:t>', pa))
            if not t.strip() or t.strip() == title_txt.strip():
                continue
            sizes = [int(x) for x in re.findall(r'sz="(\d+)"', pa)]
            sz = min(sizes) if sizes else 1800
            if _is_reference(t):      # 참고문헌 줄은 밀도·글씨 검사에서 제외
                continue
            body_paras.append((t, sz))

        words = sum(_weighted_words(t) for t, _ in body_paras)
        n_par = len(body_paras)

        # 색 예산
        pal = THEMES[deck.theme]
        key_hits = len(re.findall('val="%s"' % pal[C.KEY], xml)) if pal[C.KEY] else 0

        # 폰트
        small = [s for _, s in body_paras if s < MIN_BODY_PT * 100 and s >= 1000]
        tsp = re.search(r'<p:sp>(?:(?!</p:sp>).)*?type="title".*?</p:sp>', xml, re.S)   # v16.7.1: 제목 도형 안에서만 sz 를 찾는다
        tsize = re.search(r'sz="(\d+)"', tsp.group(0)) if tsp else None
        tsize = int(tsize.group(1)) if tsize else None

        # 줄 수
        long_paras = [t[:40] for t, s in body_paras
                      if _est_lines(t, s / 100.0, body_w) > MAX_PARA_LINES]

        read_min = words / READ_WPM
        notes_txt = ' '.join(_spoken_notes(deck.notes(sn)))
        ko = len(re.findall(r'[\uac00-\ud7a3]', notes_txt))
        en = len(re.findall(r'[A-Za-z][A-Za-z\-/]*', notes_txt))
        speak_min = ko / SPEAK_KO_CPM + en / SPEAK_EN_WPM
        total_read += read_min
        total_speak += speak_min
        rows.append((pos, sn, kind, int(words), n_par, key_hits, speak_min))

        tag = 'slide%d(%s)' % (sn, kind)
        if words > cap['words']:
            problems.append('%s 글자량 초과: %d단어 (상한 %d) — 종류 판정 근거: %s. 틀리면 노트 첫 줄에 [kind: review] 등' % (tag, words, cap['words'], why))
        if n_par > cap['paras']:
            problems.append('%s 문단 과다: %d개 (상한 %d)' % (tag, n_par, cap['paras']))
        if key_hits > cap['key_phrases']:
            problems.append('%s 강조색 남용: KEY %d개 (상한 %d)'
                            % (tag, key_hits, cap['key_phrases']))
        if tbl_sizes and min(tbl_sizes) < TABLE_MIN_PT * 100:
            problems.append('[참고] %s 표 글씨 %dpt (표 최소 %dpt, DECK_SPEC §3)' % (tag, min(tbl_sizes) // 100, TABLE_MIN_PT))
        if small:
            problems.append('%s 본문 글씨 작음: %s (최소 %dpt)'
                            % (tag, [s / 100 for s in small], MIN_BODY_PT))
        if tsize and tsize < MIN_TITLE_PT * 100:
            problems.append('%s 제목 글씨 작음: %dpt (최소 %dpt)'
                            % (tag, tsize // 100, MIN_TITLE_PT))
        for lp in long_paras:
            problems.append('%s 문단이 %d줄 초과 추정: "%s..."' % (tag, MAX_PARA_LINES, lp))
        if speak_min > 2.5:
            problems.append('%s 대본이 김: 약 %.1f분' % (tag, speak_min))

    print('%-4s %-9s %-9s %6s %5s %4s %7s' %
          ('#', 'slide', 'kind', 'words', 'para', 'KEY', 'speak'), file=stream)
    for r in rows:
        print('%-4d slide%-4d %-9s %6d %5d %4d %6.1f분' % r, file=stream)

    summary = {'read_min': total_read, 'speak_min': total_speak,
               'slides': len(rows)}
    print('\n슬라이드 %d장' % len(rows), file=stream)
    print('화면 글자 밀도 기준 시간(분당 %d단어) 합계  : 약 %.1f분  — 읽기 시간이 아니라 밀도 기준' % (READ_WPM, total_read), file=stream)
    if total_read > total_speak > 0:
        problems.append('화면 글자 밀도 기준 시간(%.1f분)이 대본 시간(%.1f분)보다 큼 — 글자가 많다' % (total_read, total_speak))
    n_cut = n_near = n_img = 0
    for sn in deck.slide_numbers():
        st, ln = _cutoff_status(deck.notes(sn))
        n_cut += st == 'cut'
        if st == 'nearmiss':
            n_near += 1
            problems.append('slide%d: 표지처럼 보이는 줄이 절단되지 않음 — 참고 블록이 낭독 시간에 들어간다: %r' % (sn, ln[:50]))
        if deck.images(sn) and _weighted_words(' '.join(deck.texts(sn)[1:])) <= 40:
            n_img += 1
    print('낭독 추정(하한)                       : 약 %.1f분  — 영상을 가리키며 말하는 시간은 안 들어감' % total_speak, file=stream)
    print('발표 시간 추정(여유 20%% 포함)          : 약 %.1f분  — 실측 1건(MSK CR 20분)과 일치했던 지표' % (total_speak * 1.2), file=stream)
    print('절단 표지: 있는 슬라이드 %d / 표지처럼 보이나 미인정 %d / 영상 슬라이드(그림 + 짧은 본문) %d장' % (n_cut, n_near, n_img), file=stream)

    # v16.7.3 (발표 T1): 영어만 쓰는 덱 종류면 슬라이드 본문(노트 제외)의 한글을 [참고]로. 전평·전문의 시험 풀이는 원본 존중이라 검사 안 함
    dk = deck_kind(deck, deck_kind_override)   # (슬라이드 종류 변수 kind 와 이름이 겹쳐 한 번 틀렸다)
    if dk in ENGLISH_ONLY_KINDS:
        for sn in deck.slide_numbers():
            ko = sum(len(re.findall(r'[\uac00-\ud7a3]', t)) for t in deck.texts(sn))
            if ko:
                problems.append('[참고] slide%d 본문에 한글 %d자 — %s 는 슬라이드 영어만 (DECK_SPEC §0 A-1)' % (sn, ko, dk))
    problems += check_note_substitution(deck)   # v16.9: 한→영 치환 오염
    if dk is None:
        problems.append('[참고] 덱 종류 미지정 — 슬라이드 언어 검사 생략. `lint --deck-kind "case review"` 또는 첫 화면 노트에 [deck: case review]')
    # v16.6 (학회 덱 회신 요청 6): 태그 없는 슬라이드가 절반을 넘으면 종류 추정임을 알린다 — 분류 로직은 그대로
    if n_total and n_tagged < n_total / 2:
        problems.append('슬라이드 %d/%d 에 [kind:] 태그 없음 — 종류는 제목·위치로 추정했다. 학회 덱은 노트 첫 줄에 [kind: result] 등 태그 권장'
                        % (n_total - n_tagged, n_total))
    # v16.5: 카드 안쪽 여백 일관성 (수정 없음, 확인용)
    problems += [x.replace('[참고] ', '') for x in check_card_insets(deck, stream=io.StringIO())]

    problems = [deck.relabel(p) for p in problems]   # v16.8.1 (Z2): lint 도 '화면 N (slideM.xml)' 표기
    print('\n=== 밀도·시간 점검 ===', file=stream)
    if problems:
        for p in problems:
            print('  [!] %s' % p, file=stream)
    else:
        print('  특이사항 없음', file=stream)
    return problems, summary



# ----------------------------------------------------------------------------
# polish — 자잘하지만 매번 해야 하는 마무리 작업 묶음
# ----------------------------------------------------------------------------

# rPr 안에서 latin/ea/cs 보다 뒤에 와야 하는 자식 요소 (CT_TextCharacterProperties 순서)
_AFTER_FONT = ('<a:sym', '<a:hlinkClick', '<a:hlinkMouseOver', '<a:rtl', '<a:extLst')


def _apply_font_tags(x, tags):
    """rPr / endParaRPr / defRPr 마다 폰트 태그를 스키마 순서에 맞는 자리에 넣는다.

    이전 구현은 self-closing 이거나 solidFill 바로 뒤일 때만 넣어서,
    (a) 채움 없이 폰트만 있던 run, (b) solidFill 뒤에 effectLst 가 있는 run 에서는
    폰트가 통째로 빠졌다. 실제 덱에서 (a)가 자주 나온다.
    """
    def fix(m):
        tag, attrs, rest = m.group(1), m.group(2), m.group(3)
        if rest == '/>':
            return '<a:%s%s>%s</a:%s>' % (tag, attrs, tags, tag)
        inner = rest[1:-len('</a:%s>' % tag)]
        inner = re.sub(r'<a:(latin|ea|cs) typeface="[^"]*"[^/]*/>', '', inner)
        cut = len(inner)
        for k in _AFTER_FONT:
            i = inner.find(k)
            if i != -1:
                cut = min(cut, i)
        return '<a:%s%s>%s%s%s</a:%s>' % (tag, attrs, inner[:cut], tags, inner[cut:], tag)
    x = re.sub(r'<a:(rPr|endParaRPr|defRPr)\b([^>]*?)(/>|>.*?</a:\1>)', fix, x, flags=re.S)
    # rPr 자체가 없는 run 은 폰트를 테마에서 상속하므로 여기서 만들어 넣는다
    x = re.sub(r'<a:r>(?!\s*<a:rPr)',
               '<a:r><a:rPr lang="en-US" dirty="0">' + tags + '</a:rPr>', x)
    return x


def set_fonts(deck, profile=None):
    """모든 run 과 테마 폰트를 지정 프로파일로 통일한다.

    라틴·한글·기호 폰트를 전부 명시해야 발표 PC가 바뀌어도 같게 보인다.
    명시하지 않으면 테마 폰트를 상속하는데, 그 테마 폰트가 PC에 없으면
    임의의 서체로 대체되어 줄바꿈과 배치가 무너진다.
    """
    f = FONT_PROFILES[profile or DEFAULT_FONT]
    tags = _font_tags(profile)
    n = 0

    for folder in ('ppt/slides', 'ppt/notesSlides'):
        base = os.path.join(deck.dir, folder)
        if not os.path.isdir(base):
            continue
        for fn in os.listdir(base):
            if not fn.endswith('.xml'):
                continue
            fp = os.path.join(base, fn)
            x = open(fp, encoding='utf8').read()
            orig = x
            x = _apply_font_tags(x, tags)
            if x != orig:
                open(fp, 'w', encoding='utf8').write(x)
                n += 1

    # 테마의 major/minor 폰트도 맞춘다 (상속 run 대비)
    tdir = os.path.join(deck.dir, 'ppt/theme')
    if os.path.isdir(tdir):
        for fn in os.listdir(tdir):
            fp = os.path.join(tdir, fn)
            x = open(fp, encoding='utf8').read()
            orig = x
            x = re.sub(r'(<a:(?:majorFont|minorFont)>\s*<a:latin typeface=")[^"]*"',
                       r'\g<1>%s"' % f['latin'], x)
            x = re.sub(r'(<a:(?:majorFont|minorFont)>\s*<a:latin[^/]*/>\s*'
                       r'<a:ea typeface=")[^"]*"', r'\g<1>%s"' % f['ea'], x)
            if x != orig:
                open(fp, 'w', encoding='utf8').write(x)
    return n, f


def merge_runs(deck):
    """서식이 같은 인접 run 을 합친다.

    주의: 정규식 하나로 두 run 을 한 번에 잡으면 lazy 수량자가 중간 run 을 통째로
    삼켜 **글자가 사라진다.** v15 까지 그 버그가 있었고 실제로 ', ' 와 '.' 이
    사라졌다('심부전, 신부전, 간경화' → '심부전신부전간경화'). run 을 토큰으로
    끊어 놓고 인접·동일 서식만 합치며, 병합 전후 텍스트가 다르면 되돌린다.
    """
    RUN = re.compile(r'<a:r>(?P<pr><a:rPr\b(?:(?!</a:rPr>).)*</a:rPr>|<a:rPr\b[^>]*/>)?'
                     r'<a:t(?P<attr>[^>]*)>(?P<txt>[^<]*)</a:t></a:r>', re.S)
    n = 0
    base = os.path.join(deck.dir, 'ppt/slides')
    for fn in sorted(os.listdir(base)):
        if not fn.endswith('.xml'):
            continue
        fp = os.path.join(base, fn)
        x = open(fp, encoding='utf8').read()
        out, pos, pending = [], 0, None

        def flush():
            if pending is None:
                return ''
            pr, attr, txt = pending
            sp = '' if 'xml:space' in attr else (
                ' xml:space="preserve"' if txt != txt.strip() else '')
            return '<a:r>%s<a:t%s%s>%s</a:t></a:r>' % (pr or '', attr, sp, txt)

        for m in RUN.finditer(x):
            gap = x[pos:m.start()]
            pos = m.end()
            pr, attr, txt = m.group('pr'), m.group('attr'), m.group('txt')
            if pending is not None and gap == '' and pending[0] == pr:
                pending = (pr, pending[1], pending[2] + txt)
                n += 1
            else:
                out.append(flush()); out.append(gap)
                pending = (pr, attr, txt)
        out.append(flush()); out.append(x[pos:])
        new_x = ''.join(out)
        before = ''.join(re.findall(r'<a:t[^>]*>([^<]*)</a:t>', x))
        after = ''.join(re.findall(r'<a:t[^>]*>([^<]*)</a:t>', new_x))
        if before != after:
            continue                       # 안전장치: 글자가 바뀌면 이 파일은 건드리지 않는다
        if new_x != x:
            open(fp, 'w', encoding='utf8').write(new_x)
    return n


def clean_placeholders(deck):
    """내용이 없는 placeholder 를 지운다.

    남아 있으면 편집 화면에서 '텍스트를 입력하십시오' 안내문이 보이고,
    일부 뷰어에서는 발표 중에도 빈 상자 테두리가 뜬다.
    """
    n = 0
    base = os.path.join(deck.dir, 'ppt/slides')
    for fn in sorted(os.listdir(base)):
        if not fn.endswith('.xml'):
            continue
        fp = os.path.join(base, fn)
        x = open(fp, encoding='utf8').read()
        orig = x
        for m in list(re.finditer(r'<p:sp>.*?</p:sp>', x, re.S)):
            s = m.group(0)
            if '<p:ph' not in s:
                continue
            txt = ''.join(re.findall(r'<a:t>([^<]*)</a:t>', s))
            if txt.strip() == '':
                x = x.replace(s, '')
                n += 1
        if x != orig:
            open(fp, 'w', encoding='utf8').write(x)
    return n


def force_autofit(deck):
    """본문 텍스트 상자에 자동 축소를 켠다. 넘치면 잘리는 대신 줄어든다."""
    n = 0
    base = os.path.join(deck.dir, 'ppt/slides')
    for fn in sorted(os.listdir(base)):
        if not fn.endswith('.xml'):
            continue
        fp = os.path.join(base, fn)
        x = open(fp, encoding='utf8').read()
        orig = x
        x = x.replace('<a:bodyPr/>', '<a:bodyPr><a:normAutofit/></a:bodyPr>')
        x = re.sub(r'(<a:bodyPr\b[^>]*[^/])>(?!\s*<a:(?:normAutofit|spAutoFit|noAutofit))',
                   r'\1><a:normAutofit/>', x)
        if x != orig:
            open(fp, 'w', encoding='utf8').write(x)
            n += 1
    return n


# 환자식별정보 후보 패턴
PHI_PATTERNS = [
    (r'\b\d{6}[-–]\s?[1-4]\d{6}\b', '주민등록번호 형태'),
    (r'\b(?!(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\b)\d{8,10}\b',
     '등록번호/차트번호 후보'),   # YYYYMMDD 날짜는 제외
    (r'\bACC\w*\s*[:#]?\s*\d{6,}', 'accession number'),
    (r'(?i)\b(patient\s*(name|id)|환자\s*(성명|이름|번호))\b', '환자 식별 필드명'),
    (r'[가-힣]{2,4}\s*\(\s*[MF]\s*/\s*\d{1,3}\s*\)', '이름(성별/나이) 형태'),
    (r'(?i)\bdose\s*report\b', 'dose report 페이지'),
]


_EXTERNAL_WORDS = ('외부', '학회', 'conference', 'external', 'kcr', 'rsna')


def deck_audience(deck, override=None):
    """'external' | 'internal' | None. --audience 인자 > 첫 화면 노트 [deck: …] 태그(외부·학회·conference 가 있으면 external,
    그 밖의 종류는 internal) > None. (v16.9, 2026-09-24 사용자: 내부 발표는 환자 정보가 있어야 한다)"""
    if override:
        return override
    dk = deck_kind(deck)
    if dk is None:
        return None
    return 'external' if any(w in dk for w in _EXTERNAL_WORDS) else 'internal'


def scan_phi(deck, stream=sys.stdout, audience=None):
    """환자식별정보 의심 문자열을 찾는다. 값 자체는 출력하지 않는다.
    v16.9 (2026-09-24 사용자): **내부 발표는 환자 정보를 남긴다** — case review 등은 등록번호로 내부 기록을 찾아 공부해야 한다.
    외부 발표(학회·외부 공유)만 지운다. audience='internal' 이면 검사하지 않고, None(미지정)이면 검사하되 [참고] 로만 알린다."""
    if audience == 'internal':
        print('[개인정보 점검] 내부 발표 — 환자 정보는 남긴다(생략). 외부로 내보낼 때 --audience external 로 다시 돈다', file=stream)
        return []
    hits = []
    for sn in deck.slide_numbers():
        blob = ' '.join(deck.texts(sn)) + ' ' + ' '.join(deck.notes(sn))
        for pat, label in PHI_PATTERNS:
            if re.search(pat, blob):
                hits.append('slide%d: %s 의심' % (sn, label))
    if hits:
        if audience == 'external':
            print('[개인정보 점검] 외부 발표 — 아래를 지워야 한다 (값은 출력하지 않음):', file=stream)
        else:
            print('[개인정보 점검] 발표 범위 미지정 — 외부로 내보낼 때만 지운다. 내부 발표면 무시 (값은 출력하지 않음):', file=stream)
        for h in hits:
            print('  %s %s' % ('[!]' if audience == 'external' else '[참고]', h), file=stream)
    else:
        print('[개인정보 점검] 텍스트에서 식별정보 패턴 없음', file=stream)
    print('  * 영상에 구워진 글자(번인)는 텍스트 검사로 잡히지 않습니다. '
          '렌더 이미지를 눈으로 확인하십시오.', file=stream)
    return hits


def check_bounds(deck, stream=sys.stdout):
    """슬라이드 밖으로 나가거나 제목을 덮는 도형을 찾는다."""
    W, H = deck.slide_size()
    probs = []
    for sn in deck.slide_numbers():
        for sh in deck.shapes(sn):
            if not sh['xy']:
                continue
            x, y, cx, cy = map(int, sh['xy'])
            if x < -10000 or y < -10000 or x + cx > W + 10000 or y + cy > H + 10000:
                probs.append('slide%d: "%s" 가 슬라이드 밖으로 나감' % (sn, sh['name']))
            if sh['kind'] == 'pic' and y < 700000:
                probs.append('slide%d: "%s" 가 제목 영역을 침범' % (sn, sh['name']))
    for p in probs:
        print('  [!] %s' % p, file=stream)
    if not probs:
        print('  배치 이상 없음', file=stream)
    return probs


def export_notes(deck, path):
    """대본을 마크다운 유인물로 뽑는다. 슬라이드는 얇게, 밀도는 여기로."""
    lines = ['# 발표 대본', '']
    for pos, (sn, _, _) in enumerate(deck.order(), 1):
        if sn is None:
            continue
        title = (deck.texts(sn) or [''])[0]
        lines.append('## %d. %s' % (pos, title.strip() or '(제목 없음)'))
        body = [t for t in deck.texts(sn)[1:] if t.strip()]
        if body:
            lines.append('')
            lines.append('> ' + ' / '.join(body))
        lines.append('')
        nt = [t for t in deck.notes(sn) if t.strip()]
        lines.extend(nt if nt else ['_(대본 없음)_'])
        lines.append('')
    open(path, 'w', encoding='utf8').write('\n'.join(lines))
    return path


def _all_text(deck):
    out = []
    base = os.path.join(deck.dir, 'ppt/slides')
    for fn in sorted(os.listdir(base)):
        if fn.endswith('.xml'):
            x = open(os.path.join(base, fn), encoding='utf8').read()
            out.append(''.join(re.findall(r'<a:t[^>]*>([^<]*)</a:t>', x)))
    return '\n'.join(out)


MODALITY_WORDS = {
    'sagittal': ('sagittal', '시상', 'sagittal 재구성'),
    'axial': ('axial', '축상'),
    'coronal': ('coronal', '관상'),
    'mri': ('mri', 't1wi', 't2wi', 'flair', 'dwi', 'adc'),
    'ct': ('ct',),
    'pet': ('pet',),
    'radiograph': ('radiograph', 'x선', 'x-ray', '단순촬영'),
}


def check_notes_alignment(deck, stream=sys.stdout):
    """발표자 노트가 슬라이드와 어긋났는지 본다.

    실제 사고에서 나왔다. 케이스 제시 슬라이드가 병력과 첫 영상을 함께 담고
    있었는데 노트는 병력만 다루고 시작해, 이후 노트가 전부 한 칸씩 밀렸다.
    수치도 문구도 같아서 sync 로는 잡히지 않았다.

    슬라이드 화면의 모달리티 표기(제목·헤더)와 노트가 말하는 모달리티를
    대조한다. 화면이 "axial" 인데 노트가 "sagittal" 을 말하면 표시한다.
    영상 슬라이드에 모달리티 표기를 달아두면 이 검사가 작동한다.
    """
    probs = []
    for sn in deck.slide_numbers():
        body = ' '.join(deck.texts(sn)).lower()
        note = ' '.join(_spoken_notes(deck.notes(sn))).lower()
        if not body.strip() or not note.strip():
            continue
        b = {k for k, ws in MODALITY_WORDS.items() if any(w in body for w in ws)}
        n = {k for k, ws in MODALITY_WORDS.items() if any(w in note for w in ws)}
        if not b or not n:
            continue
        # ct/mri 같은 상위 개념이나 앞뒤 슬라이드를 미리 언급하는 문장 때문에
        # 오탐이 많으므로, 평면(sagittal/axial/coronal)이 서로 배타적인 경우만 본다
        planes = {'sagittal', 'axial', 'coronal'}
        bp, np_ = b & planes, n & planes
        if bp and np_ and not (bp & np_):
            probs.append('slide%d: 화면은 %s 인데 노트는 %s 를 설명함 '
                         '— 노트가 밀렸는지 확인'
                         % (sn, '/'.join(sorted(bp)), '/'.join(sorted(np_))))

    for sn in deck.slide_numbers():
        if deck.images(sn) and ' '.join(_spoken_notes(deck.notes(sn))).strip() == '':
            probs.append('slide%d: 영상이 있으나 발표자 노트가 비어 있음' % sn)

    for p in probs:
        print('  [?] %s' % p, file=stream)
    if not probs:
        print('  노트-슬라이드 정렬 이상 없음', file=stream)
    print('  * 후보 목록입니다. 슬라이드를 열어 직접 확인하십시오.', file=stream)
    print('  * 영상 슬라이드에 모달리티 표기가 없으면 이 검사는 작동하지 않습니다.',
          file=stream)
    return probs


def polish(deck, font=None, stream=sys.stdout, audience=None):
    """마무리 작업 일괄 수행 + 점검 보고.
    v16.6: 실행 전후 전체 텍스트를 비교해 글자가 바뀌면 [!!] 경고 — merge_runs 가 글자를 삼키던 사고
    (전평 대화창 9/8 보고, 9/13 흡수) 이후의 안전장치. 반환 'text_intact' 가 False 면 결과를 쓰지 않는다."""
    _t0 = _all_text(deck)
    nf, f = set_fonts(deck, font)
    nm = merge_runs(deck)
    nc = clean_placeholders(deck)
    na = force_autofit(deck)
    print('폰트 통일: %s / %s  (%d개 파트)' % (f['latin'], f['ea'], nf), file=stream)
    print('쪼개진 run 병합: %d회' % nm, file=stream)
    print('빈 placeholder 제거: %d개' % nc, file=stream)
    print('자동 축소 설정: %d개 슬라이드' % na, file=stream)
    print('\n[배치 점검]', file=stream)
    bounds = check_bounds(deck, stream)
    print('', file=stream)
    print('[텍스트 넘침 점검]', file=stream)
    overflow = check_text_overflow(deck, stream=stream)
    print('', file=stream)
    phi = scan_phi(deck, stream, audience=deck_audience(deck, audience))
    _t1 = _all_text(deck)
    if _t0 != _t1:
        print('\n[!!] 경고: polish 과정에서 텍스트가 변경되었습니다. 결과를 사용하지 마십시오.', file=stream)
    else:
        print('텍스트 무결성: 변경 없음', file=stream)
    return {'text_intact': _t0 == _t1, 'fonts': nf, 'merged': nm, 'cleaned': nc, 'autofit': na,
            'bounds': bounds, 'overflow': overflow, 'phi': phi}


# ----------------------------------------------------------------------------
# 기존 덱을 하우스 스타일로 변환
# ----------------------------------------------------------------------------

# 흔히 쓰이는 액센트 → 하우스 팔레트 매핑
_RESTYLE_MAP = {
    'FF0000': C.FLAG, 'C00000': C.FLAG, 'E74C3C': C.FLAG,
    'FFFF00': C.KEY,  'FFFF99': C.KEY,  'F0E442': C.KEY,
    'FFC000': C.CTX,  'ED7D31': C.CTX,  'E69F00': C.CTX,
    '00B0F0': C.HEAD, '0070C0': C.HEAD, '4472C4': C.HEAD, '56B4E9': C.HEAD,
    '00B050': C.FLAG, '92D050': C.FLAG, '009E73': C.FLAG,
}


def restyle(deck, min_body=MIN_BODY_PT * 100, min_title=MIN_TITLE_PT * 100,
            stream=sys.stdout):
    """다른 양식의 덱을 하우스 스타일에 맞춘다.

    기계적으로 할 수 있는 것만 한다:
      - 액센트 색을 하우스 팔레트로 재매핑
      - 본문/제목 최소 글씨 크기 강제
      - 한 글자 잔재, 빈 불릿 자리표시자 제거
    구조 재작성(문단→항목, 강조 구 선정)은 판단이 필요하므로 하지 않고 보고만 한다.
    """
    pal = THEMES[deck.theme]
    changed = {'color': 0, 'size': 0, 'stub': 0}
    todo = []

    for sn in deck.slide_numbers():
        p = deck._slide(sn)
        d = open(p, encoding='utf8').read()
        orig = d

        for src, role in _RESTYLE_MAP.items():
            dst = pal.get(role)
            if dst and src.upper() != dst.upper():
                n = d.count('val="%s"' % src)
                if n:
                    d = d.replace('val="%s"' % src, 'val="%s"' % dst)
                    changed['color'] += n

        def bump(m):
            v = int(m.group(1))
            ctx_before = d[max(0, m.start() - 2000):m.start()]
            # 같은 <a:p> 안의 텍스트를 보고 참고문헌 줄이면 건드리지 않는다
            pstart = d.rfind('<a:p>', 0, m.start())
            pend = d.find('</a:p>', m.start())
            para_txt = ''.join(re.findall(r'<a:t>([^<]*)</a:t>',
                                          d[pstart:pend if pend > 0 else len(d)]))
            if _is_reference(para_txt):
                return m.group(0)
            floor = min_title if 'type="title"' in ctx_before else min_body
            if 800 < v < floor:
                changed['size'] += 1
                return 'sz="%d"' % floor
            return m.group(0)
        d = re.sub(r'sz="(\d+)"', bump, d)

        for stub in ('<a:t>B</a:t>', '<a:t>T</a:t>', '<a:t> - </a:t>',
                     '<a:t>-</a:t>', '<a:t> -</a:t>'):
            if stub in d:
                d = d.replace(stub, '<a:t></a:t>')
                changed['stub'] += 1

        if d != orig:
            open(p, 'w', encoding='utf8').write(d)

        txts = deck.texts(sn)
        for t in txts:
            if _weighted_words(t) > 40:
                todo.append('slide%d: 한 문단이 %d단어 — 항목형으로 쪼개야 함'
                            % (sn, int(_weighted_words(t))))
                break

    print('색 재매핑 %d곳, 글씨 크기 보정 %d곳, 잔재 텍스트 제거 %d곳'
          % (changed['color'], changed['size'], changed['stub']), file=stream)
    if todo:
        print('\n손으로 고쳐야 하는 것 (판단 필요):', file=stream)
        for t in todo:
            print('  [~] %s' % t, file=stream)
    return changed, todo


# ----------------------------------------------------------------------------
# 스켈레톤 생성 — spec(JSON/dict) → 빈 덱 구조
# ----------------------------------------------------------------------------

SKELETON = {
    'quiz': lambda case: [
        ('history',  '%s 제시' % case),
        ('image',    '%s 영상' % case),
        ('findings', 'Radiologic findings'),
        ('review',   'Disease review'),
    ],
    'case_review': lambda case: [
        ('history',  '%s 임상 경과' % case),
        ('image',    '%s 영상' % case),
        ('findings', 'Radiologic findings'),
        ('review',   'Disease review'),
        ('review',   'Differential comparison'),
    ],
    # journal review — original article: 설계·결과·한계가 축
    'journal_original': lambda paper: [
        ('review',     '%s — citation and question' % paper),
        ('review',     'Background and gap'),
        ('method',     'Study design'),
        ('result',     'Key results'),
        ('result',     'Key results (cont.)'),
        ('limitation', 'Limitations'),
        ('summary',    'How it changes my practice'),
    ],
    # journal review — review article: 근거 수준과 실전 적용이 축. 결과 슬라이드 대신 개념 정리
    'journal_review_article': lambda paper: [
        ('review',     '%s — scope and question' % paper),
        ('review',     'Key concepts'),
        ('review',     'Evidence level of each claim'),
        ('image',      'Representative images'),
        ('limitation', 'What the review does not settle'),
        ('summary',    'How it changes my practice'),
    ],
    # 학회 구연 발표 (10분 기준). 케이스별 반복이 없으므로 cases 는 [발표제목] 하나만
    'conference': lambda topic: [
        ('review',     'Background'),
        ('review',     'Purpose / hypothesis'),
        ('method',     'Participants and acquisition'),
        ('method',     'Analysis'),
        ('divider',    'Results'),
        ('result',     'Main result'),
        ('result',     'Secondary result'),
        ('divider',    'Discussion'),
        ('review',     'Interpretation'),
        ('limitation', 'Limitations'),
        ('summary',    'Conclusion'),
        ('closing',    'Acknowledgments'),
    ],
}
SKELETON['journal_review'] = SKELETON['journal_original']   # 하위 호환

PLAN_MIN = {'title': 0.3, 'history': 0.8, 'image': 1.5, 'findings': 1.2, 'review': 2.0,
            'summary': 1.0, 'divider': 0.1, 'method': 1.0, 'result': 1.2,
            'limitation': 1.0, 'closing': 0.2}


def plan(kind, cases, stream=sys.stdout, minutes=None):
    """발표 유형과 케이스 목록에서 슬라이드 구성안과 예상 시간을 뽑는다."""
    if kind not in SKELETON:
        raise ValueError('kind 는 %s 중 하나' % list(SKELETON))
    out = [('title', kind + ' 표지')]
    for c in cases:
        out.extend(SKELETON[kind](c))
    if kind != 'conference':
        out.append(('summary', 'Take home message'))

    total = sum(PLAN_MIN[k] for k, _ in out)
    print('%-4s %-10s %s' % ('#', 'kind', 'title'), file=stream)
    for i, (k, t) in enumerate(out, 1):
        print('%-4d %-10s %s' % (i, k, t), file=stream)
    print('\n슬라이드 %d장, 예상 발표 %.0f분 (질의응답 별도)' % (len(out), total),
          file=stream)
    if minutes:
        content = sum(1 for k, _ in out if k not in ('title', 'divider', 'closing'))
        budget = minutes * 0.8          # 질의·전환 여유 20%
        print('시간 예산 %d분 → 발표 %.1f분 안에 끝내야 함. 내용 슬라이드 %d장 '
              '(분당 %.1f장)' % (minutes, budget, content, content / budget), file=stream)
        if total > budget:
            print('  [!] 구성안이 예산을 %.1f분 초과. 케이스/결과 슬라이드를 줄이거나 '
                  '대본을 얇게' % (total - budget), file=stream)
        if content / budget > 1.6:
            print('  [!] 분당 1.6장 이상은 청중이 따라오기 어렵다', file=stream)
    return out



# ----------------------------------------------------------------------------
# 원고·표와의 수치 교차검증
#
#  발표 슬라이드의 숫자가 원고/표/보충자료에 실제로 존재하는지 대조한다.
#  손으로 하면 반드시 빠지는 작업이고, 실제로 이 툴킷을 만들게 된 계기이기도 하다.
#  주의: "원고에 있다"가 "옳다"는 뜻은 아니다. 원고 자체가 틀렸을 수 있다.
# ----------------------------------------------------------------------------

def read_docx(path):
    """docx 본문 텍스트를 뽑는다 (표 셀 포함)."""
    with zipfile.ZipFile(path) as z:
        parts = [n for n in z.namelist()
                 if re.fullmatch(r'word/(document|footnotes|endnotes)\.xml', n)]
        out = []
        for n in parts:
            x = z.read(n).decode('utf8', 'ignore')
            x = re.sub(r'</w:(p|tr|tc)>', '\n', x)
            x = re.sub(r'<[^>]+>', '', x)
            out.append(html.unescape(x))
    return '\n'.join(out)


def read_any(path):
    """docx / txt / md 를 텍스트로 읽는다.
    v16.6 (학회 덱 회신 결함 3): 확장자가 아니라 zip 매직 바이트(PK\\x03\\x04)로 docx 를 판별한다.
    프로젝트 지식이 docx 를 텍스트로 바꿔 놓은 파일이 `.docx` 이름으로 오는 경우가 있다."""
    with open(path, 'rb') as f:
        head = f.read(4)
    if head == b'PK\x03\x04':
        return read_docx(path)
    if path.lower().endswith('.docx'):
        print('  [참고] %s 는 이름만 docx 이고 내용은 텍스트 — 텍스트로 읽음' % os.path.basename(path), file=sys.stderr)
    return open(path, encoding='utf8', errors='ignore').read()


# 대조에서 제외할 숫자: 연도, 순번, 축 눈금 등
_SKIP_NUM = re.compile(r'^(19|20)\d\d$')


def _numbers(text):
    """유효숫자 2자리 이상의 수치만 뽑는다. 부호는 버리고 절대값으로 비교.

    4자리 연도(19xx/20xx)는 버리되, 'b = 2000', 'b=2000', 'b-value 2000' 처럼
    b-value 문맥에 붙은 것은 살린다. (실제 사고: b=2000 이 연도로 버려져
    crosscheck 대상에서 통째로 빠져 있었다.)
    """
    found = set()
    for m in re.finditer(r'-?\d+\.\d+|\b\d{2,}\b', text):
        tok = m.group(0).lstrip('-−')
        if _SKIP_NUM.match(tok):
            pre = text[max(0, m.start() - 30):m.start()].lower()
            # 'b = 2000', 'b=2000', 'b-values of 800 and 2000', 'b = 800/2000'
            if not re.search(r'\bb\s*(-?\s*values?)?\s*(=|of|at)?'
                             r'[\d\s,/&]*(and\s+)?$', pre):
                continue
        if '.' not in tok and len(tok) < 3:
            continue
        found.add(tok)
    return found


def _matches(tok, corpus_floats, corpus_raw):
    """슬라이드 수치가 원전 수치와 맞는지 판정.

    반올림은 흡수하되 자기 자릿수에서 정확히 반올림된 경우만 인정한다.
      12.3   <-> 12.270  통과
      0.89   <-> 0.890   통과
      6.7    <-> 6.651   통과
      0.7777 <-> 없음    불통과
    정수(1065 등)는 반올림을 허용하지 않고 정확히 일치해야 한다.
    부호는 무시한다. 슬라이드가 "-12.3 -> -6.7"처럼 쓰는 경우가 많다.
    """
    if tok in corpus_raw:
        return True
    if '.' not in tok:
        return False
    nd = len(tok.split('.')[1])
    try:
        want = abs(float(tok))
    except ValueError:
        return False
    fmt = '%.' + str(nd) + 'f'
    target = fmt % want
    return any((fmt % abs(f)) == target for f in corpus_floats)

def crosscheck(deck, sources, stream=sys.stdout, notes=False):
    """슬라이드의 수치가 원고/표/보충자료에 존재하는지 대조한다.

    sources: docx/txt/md 경로 목록
    notes=True (v16.6, 학회 덱 회신 요청 7): 발표자 노트(대본·예상 질문)의 수치도 대조한다.
      학회 제출본에서 원고와 어긋난 서술은 전부 노트에 있었다. 수치만 본다 — 서술 불일치는 도구 범위 밖.
    반환: (미확인 항목 [(slide, 토큰, '본문'|'노트')], 대조한 숫자 수)
    """
    corpus = ''
    for s in sources:
        corpus += '\n' + read_any(s)
    corpus_raw = _numbers(corpus)
    corpus_floats = []
    for t in corpus_raw:
        try:
            corpus_floats.append(float(t))
        except ValueError:
            pass

    unmatched, total = [], 0
    for pos, (sn, _, _) in enumerate(deck.order(), 1):
        if sn is None:
            continue
        blob = ' '.join(deck.texts(sn))
        for tok in sorted(_numbers(blob)):
            total += 1
            if not _matches(tok, corpus_floats, corpus_raw):
                unmatched.append((sn, tok, '본문'))
        if notes:
            nblob = ' '.join(_spoken_notes(deck.notes(sn)))
            for tok in sorted(_numbers(nblob) - _numbers(blob)):
                total += 1
                if not _matches(tok, corpus_floats, corpus_raw):
                    unmatched.append((sn, tok, '노트'))

    print('슬라이드 수치 %d개 대조%s, 원전에서 확인되지 않은 값 %d개'
          % (total, ' (노트 포함)' if notes else '', len(unmatched)), file=stream)
    for sn, tok, where in unmatched:
        print('  [?] %s%s: %s' % (deck.label(sn), (' [%s]' % where) if notes else '', tok), file=stream)
    if not unmatched:
        print('  모든 수치가 원전에서 확인됨', file=stream)
    print('  * 원전에 있다는 것이 옳다는 뜻은 아닙니다. 원전 자체의 오류는 별도 확인 필요.',
          file=stream)
    return unmatched, total


def locate(sources, *values, context=90, stream=sys.stdout):
    """주어진 수치·문구가 원전 어디에 어떤 맥락으로 나오는지 찾아 보여준다.

    판정하지 않는다. 사람이 볼 근거를 모아 줄 뿐이다.
    회신 문서의 수치가 제출 원고와 맞는지 확인할 때 쓴다.
    실제 사례: 회신의 "FA800 P = 0.594" 와 Table 1 의 "P = 0.538" 이 어긋난 것을
    이 방식으로 확인했다.
    """
    hits = {}
    for s in sources:
        txt = re.sub(r'\s+', ' ', read_any(s))
        for v in values:
            for m in re.finditer(re.escape(str(v)), txt):
                a = max(0, m.start() - context)
                snippet = txt[a:m.end() + context].strip()
                hits.setdefault(str(v), []).append((os.path.basename(s), snippet))
    for v in values:
        v = str(v)
        print('=== %s' % v, file=stream)
        if v not in hits:
            print('    원전에서 찾을 수 없음', file=stream)
            continue
        for doc, snip in hits[v][:6]:
            print('    [%s] ...%s...' % (doc, snip), file=stream)
    return hits


def _layout_ph_geometry(deck, slide_no):
    """슬라이드 레이아웃에서 placeholder 별 위치·크기를 읽는다.

    슬라이드에 xfrm 이 없는 placeholder 는 레이아웃 값을 상속하므로,
    이것이 없으면 템플릿 기반 덱의 본문 상자를 통째로 놓치게 된다.
    """
    geo = {}
    try:
        lay = deck.layout_of(slide_no)
    except Exception:
        return geo
    # 레이아웃도 xfrm 이 없으면 마스터를 상속하므로 마스터부터 깔고 덮어쓴다
    files = []
    mdir = os.path.join(deck.dir, 'ppt/slideMasters')
    if os.path.isdir(mdir):
        files += [os.path.join(mdir, f) for f in sorted(os.listdir(mdir))
                  if f.endswith('.xml')]
    p = os.path.join(deck.dir, 'ppt/slideLayouts', lay)
    if os.path.exists(p):
        files.append(p)
    x = '\n'.join(open(f, encoding='utf8').read() for f in files)
    for m in re.finditer(r'<p:sp>.*?</p:sp>', x, re.S):
        s = m.group(0)
        ph = re.search(r'<p:ph([^/]*)/>', s)
        off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>'
                        r'<a:ext cx="(\d+)" cy="(\d+)"', s)
        if not (ph and off):
            continue
        idx = re.search(r'idx="(\d+)"', ph.group(1))
        typ = re.search(r'type="(\w+)"', ph.group(1))
        val = tuple(int(v) for v in off.groups())
        if idx:
            geo[('idx', idx.group(1))] = val
        if typ:
            geo[('type', typ.group(1))] = val
        if typ in (None,) and not idx:
            geo[('type', '')] = val
    return geo


# ----------------------------------------------------------------------------
# v16.9: 제목 템플릿 맞춤 — 베이스 덱의 제목 규격을 배워 옮겨 온 슬라이드에 적용한다
# (2026-09-24 사용자: 템플릿을 안 지킨 새 연도 덱을 옮겨 오면 도구로든 손 복사로든 제목이 띠를 넘친다)
# ----------------------------------------------------------------------------

_TITLE_SP = re.compile(r'<p:sp>(?:(?!</p:sp>).)*?<p:ph\b[^>]*type="(?:title|ctrTitle)"(?:(?!</p:sp>).)*</p:sp>', re.S)
_GEO = re.compile(r'<a:off x="(-?\d+)" y="(-?\d+)"/>\s*<a:ext cx="(\d+)" cy="(\d+)"/>')
EMU_IN = 914400


def _master_of(deck, slide_no):
    lr = os.path.join(deck.dir, 'ppt/slideLayouts/_rels', deck.layout_of(slide_no) + '.rels')
    if os.path.exists(lr):
        m = re.search(r'slideMasters/(slideMaster\d+\.xml)', open(lr, encoding='utf8').read())
        if m:
            return os.path.join(deck.dir, 'ppt/slideMasters', m.group(1))
    return None


def _title_default_sz(deck, slide_no):
    """그 슬라이드의 **마스터** titleStyle 1단계 글자 크기(1/100 pt). 레이아웃 제목 placeholder 에 sz 가 있으면 그것. 없으면 3200.
    (첫 마스터만 보던 판은 마스터가 여럿인 덱 — 실제 전평 덱은 7개 — 에서 틀렸다)"""
    lp = os.path.join(deck.dir, 'ppt/slideLayouts', deck.layout_of(slide_no))
    if os.path.exists(lp):
        t = _TITLE_SP.search(open(lp, encoding='utf8').read())
        m = t and re.search(r'<a:(?:defRPr|rPr)\b[^>]*\bsz="(\d+)"', t.group(0))
        if m:
            return int(m.group(1))
    mp = _master_of(deck, slide_no)
    if mp and os.path.exists(mp):
        m = re.search(r'<p:titleStyle>.*?<a:lvl1pPr\b.*?<a:defRPr\b[^>]*\bsz="(\d+)"', open(mp, encoding='utf8').read(), re.S)
        if m:
            return int(m.group(1))
    return 3200


def _title_chain(deck, slide_no):
    """레이아웃 → 마스터의 제목 자리 표시자 도형(위치가 없는 것도) — 여백·채움을 물려받을 곳."""
    out = []
    for f in (os.path.join(deck.dir, 'ppt/slideLayouts', deck.layout_of(slide_no)), _master_of(deck, slide_no)):
        if f and os.path.exists(f):
            t = _TITLE_SP.search(open(f, encoding='utf8').read())
            if t:
                out.append(t.group(0))
    return out


def _title_materialized(i):
    """v16.32 (발표 K13): 위치·크기를 물려받는 제목이면 물려받은 위치·크기·안쪽 여백을 슬라이드 도형에 적어 넣은 seg 를 돌려준다
    (모양은 그대로). 레이아웃은 고치지 않는다. 반환 (seg, 적어 넣었나)."""
    seg = i['seg']
    if _GEO.search(seg):
        return seg, False
    xf = '<a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>' % (i['x'], i['y'], i['w'], i['h'])
    if re.search(r'<p:spPr\s*/>', seg):
        seg = re.sub(r'<p:spPr\s*/>', '<p:spPr>%s</p:spPr>' % xf, seg, 1)
    else:
        seg = re.sub(r'(<p:spPr\b[^>]*>)', lambda mm: mm.group(1) + xf, seg, 1)
    at = ' lIns="%d" tIns="%d" rIns="%d" bIns="%d"' % (i['lIns'], i['tIns'], i['rIns'], i['bIns'])
    bp = re.search(r'<a:bodyPr\b[^>]*?/?>', seg)
    if bp:
        tag = bp.group(0)
        nt = re.sub(r'\s(?:lIns|tIns|rIns|bIns)="-?\d+"', '', tag)
        nt = (nt[:-2] + at + '/>') if nt.endswith('/>') else (nt[:-1] + at + '>')
        seg = seg.replace(tag, nt, 1)
    return seg, True


def _inherited_title(deck, slide_no):
    """레이아웃 → 마스터 순으로 제목 placeholder 의 위치·크기·bodyPr 를 찾는다."""
    for f in (os.path.join(deck.dir, 'ppt/slideLayouts', deck.layout_of(slide_no)), _master_of(deck, slide_no)):
        if f and os.path.exists(f):
            t = _TITLE_SP.search(open(f, encoding='utf8').read())
            if t and _GEO.search(t.group(0)):
                return t.group(0)
    return ''


def _title_info(deck, slide_no):
    """제목 도형 정보. kind: 'ph'(title placeholder) / 'box'(맨 위의 넓고 얇은 글상자 — placeholder 아님) / None."""
    x = open(deck._slide(slide_no), encoding='utf8').read()
    W, H = deck.slide_size()
    m = _TITLE_SP.search(x); kind = 'ph'
    if not m:
        kind = 'box'; m = None
        for mm in re.finditer(r'<p:sp>(?:(?!</p:sp>).)*</p:sp>', x, re.S):
            seg = mm.group(0)
            g = _GEO.search(seg)
            if '<p:ph' in seg or not g or not _AT.search(seg):
                continue
            gx, gy, gw, gh = (int(v) for v in g.groups())
            n_par = len([q for q in re.findall(r'<a:p>(.*?)</a:p>', seg, re.S) if _AT.search(q)])
            # 맨 위(0.35" 이내)·넓고(슬라이드 폭 60% 이상)·얇은(1") 한두 문단 — '<정답>' 같은 본문 상자를 제목으로 오인하지 않게
            if gy <= 0.35 * EMU_IN and gw >= W * 0.6 and gh <= 1.0 * EMU_IN and n_par <= 2 and (m is None or gy < int(_GEO.search(m.group(0)).group(2))):
                m = mm
        if m is None:
            return None
    seg = m.group(0)
    inh = _inherited_title(deck, slide_no) if kind == 'ph' else ''
    chain = _title_chain(deck, slide_no) if kind == 'ph' else []     # v16.32 (발표 K13): 레이아웃(위치가 없어도) → 마스터
    g = _GEO.search(seg) or (_GEO.search(inh) if inh else None)
    if not g:
        return None
    geo = tuple(int(v) for v in g.groups())
    bp = re.search(r'<a:bodyPr\b([^>]*)', seg); bpa = bp.group(1) if bp else ''
    bpis = [(re.search(r'<a:bodyPr\b([^>]*)', c) or [None, ''])[1] for c in chain] or [(re.search(r'<a:bodyPr\b([^>]*)', inh) or [None, ''])[1]]
    def ins(k, d):
        for a in [bpa] + bpis:
            mm = re.search(r'\b%s="(-?\d+)"' % k, a or '')
            if mm:
                return int(mm.group(1))
        return d
    FILL_RE = r'<a:(?:solidFill|gradFill|blipFill|pattFill)>.*?</a:(?:solidFill|gradFill|blipFill|pattFill)>|<a:noFill/>'
    fill = None
    for c in [seg] + chain:
        sppr = re.search(r'<p:spPr\b[^>]*>(.*?)</p:spPr>', c, re.S)
        fill = re.search(FILL_RE, re.sub(r'<a:ln\b.*?</a:ln>', '', sppr.group(1), flags=re.S), re.S) if sppr else None
        if fill:
            break
    paras = [html.unescape(''.join(_AT.findall(pm))) for pm in re.findall(r'<a:p>(.*?)</a:p>', seg, re.S)]
    szs = [int(v) for v in re.findall(r'<a:rPr\b[^>]*\bsz="(\d+)"', seg)]
    latin = re.search(r'<a:rPr\b.*?<a:latin typeface="([^"]*)"', seg, re.S)
    autofit = 'norm' if '<a:normAutofit' in seg else 'sp' if '<a:spAutoFit' in seg else 'no' if '<a:noAutofit' in seg else ''
    # 줄 간격: 슬라이드 제목 문단 → 레이아웃·마스터 제목 → 마스터 titleStyle (실물 전평 템플릿은 90% — 이것을 빼면 2줄 띠가 넘친다고 오판)
    ls = re.search(r'<a:lnSpc><a:spcPct val="(\d+)"', seg) or re.search(r'<a:lnSpc><a:spcPct val="(\d+)"', inh)
    if not ls and kind == 'ph':
        mp = _master_of(deck, slide_no)
        if mp and os.path.exists(mp):
            ls = re.search(r'<p:titleStyle>.*?<a:lvl1pPr\b.*?<a:lnSpc><a:spcPct val="(\d+)"', open(mp, encoding='utf8').read(), re.S)
    lnspc = int(ls.group(1)) / 100000.0 if ls else 1.0
    return {'kind': kind, 'slide': slide_no, 'start': m.start(), 'end': m.end(), 'seg': seg, 'x': geo[0], 'y': geo[1], 'w': geo[2], 'h': geo[3],
            'inherit': not _GEO.search(seg), 'paras': [p for p in paras if p.strip()], 'sz': szs[0] if szs else None,
            'eff_sz': szs[0] if szs else _title_default_sz(deck, slide_no),
            'latin': latin.group(1) if latin else None, 'autofit': autofit, 'fill': fill.group(0) if fill else None,
            'lIns': ins('lIns', 91440), 'rIns': ins('rIns', 91440), 'tIns': ins('tIns', 45720), 'bIns': ins('bIns', 45720),
            'lnspc': lnspc, 'layout': deck.layout_of(slide_no)}


def _title_lines(info, sz, w=None):
    w = max(1, (w or info['w']) - info['lIns'] - info['rIns'])
    return sum(max(1, _est_lines(t, sz / 100.0, w)) for t in info['paras']) or 1


def _title_need(info, sz=None, w=None):
    """제목 글이 차지할 높이(EMU): 줄 수 × 글자 크기 × 줄 간격 + 위아래 여백."""
    sz = sz or info['eff_sz']
    return int(_title_lines(info, sz, w) * sz / 100.0 * LINE_FACTOR * info.get('lnspc', 1.0) * 12700 + info['tIns'] + info['bIns'])


def _mode(vals):
    vals = [v for v in vals]
    return max(set(vals), key=vals.count) if vals else None


def title_profile(deck, like=None, slides=None):
    """제목 규격을 배운다. like = 템플릿을 지킨 **화면 번호** 하나(예: 회색 띠 제목이 제대로 된 화면) — 그 화면과 같은
    레이아웃의 제목들에서 위치·폭, 줄 수별 높이, 글자 크기, 글꼴, 채움(띠 색), 안쪽 여백, 자동 맞춤을 최빈값으로 배운다.
    실제 전평 덱은 마스터가 7개인 짜깁기라 '덱 전체 최빈값' 은 템플릿이 아니었다(2026-09-24 실물 확인) — like 를 준다.
    like 가 없으면 slides(파일 번호 목록) 또는 덱 전체."""
    ri = None
    if like is not None:
        order = [s for s, _, _ in deck.order() if s]
        ref = order[int(like) - 1]
        lay = deck.layout_of(ref)
        ri = _title_info(deck, ref)
        # 같은 레이아웃이라도 문제 화면(회색 띠)과 해설 화면(띠 없음)이 섞여 있다(실물 전평 덱) — 띠 색까지 같은 제목만 배운다
        slides = [s for s in order if deck.layout_of(s) == lay and (_title_info(deck, s) or {}).get('fill') == (ri or {}).get('fill')]
    infos = [i for i in (_title_info(deck, s) for s in (slides or deck.slide_numbers())) if i and i['kind'] == 'ph']
    if not infos:
        return None
    # v16.30 (발표 K8-b): 한 덱에 제목 무리가 둘 이상일 수 있다(원본 덱 제목 여백 0.39", 가져온 제목 0.05"). 수가 많은 쪽을 고르면
    # 제목 몇 장만 고쳐도 규격이 뒤집힌다 — **위 여백** 으로 무리를 나누고, like 가 있으면 기준 제목의 무리, 없으면 가장 큰 무리에서 배운다
    groups = {}
    for i in infos:
        groups.setdefault(int(round((i['tIns'] or 0) / 9144.0)), []).append(i)      # 0.01" 단위로 묶음
    if like is not None and ri:
        gkey = int(round((ri['tIns'] or 0) / 9144.0))
    else:
        gkey = max(groups, key=lambda k: len(groups[k]))
    group_summary = {k / 100.0: len(v) for k, v in sorted(groups.items())}
    infos = groups.get(gkey) or infos
    sz = _mode([i['sz'] for i in infos]); est = sz or _mode([i['eff_sz'] for i in infos])
    hb, excluded, contrib, exl = {}, 0, {}, []
    ins_mode = _mode([(i['lIns'], i['rIns'], i['tIns'], i['bIns']) for i in infos])
    for i in infos:
        n = _title_lines(i, est)
        # v16.28 (발표 K8): 띠가 필요 높이(안쪽 여백 + 줄 높이 × 줄 수)보다 확연히 낮은 제목은 높이를 배우지 않는다 — PowerPoint 의
        # spAutoFit 에 기대는 제목(Google Slides 는 키우지 않는다)이나 도구가 만든 값이 다음 규격이 된 일(근골격 1줄 1.22" → 0.66")
        # v16.30 (발표 화면 6·7): 빼는 판정은 그 제목 **자기 글자 크기** 로 — 23pt 제목을 규격 28pt 로 세면 2줄로 보여 빠졌다
        own = i['eff_sz'] or est
        need = _title_need_h(i['tIns'], i['bIns'], _title_lines(i, own), own, i.get('lnspc', 1.0))
        if i['h'] < 0.9 * need:
            excluded += 1; exl.append((i['slide'], i['h'], need))
            continue
        contrib.setdefault(n, []).append((i['slide'], i['h'], i['tIns'], i['bIns']))
    # v16.29 (발표 K8-b): 높이와 안쪽 여백을 따로 최빈값으로 고르면 서로 다른 제목의 값이 섞인다(작은 여백 제목의 0.66" + 큰 여백
    # 0.39"×2 = 담지 못하는 띠). 규격 여백과 같은 여백을 가진 제목의 높이만으로 — 없으면 그 줄 수의 모든 제목으로
    for n, rows in contrib.items():
        same = [h for _, h, t, b in rows if (t, b) == (ins_mode[2], ins_mode[3])]
        hb[n] = same or [h for _, h, _, _ in rows]
    return {'x': _mode([i['x'] for i in infos]), 'y': _mode([i['y'] for i in infos]), 'w': _mode([i['w'] for i in infos]),
            'h_by_lines': {n: _mode(hs) for n, hs in hb.items()}, 'sz': sz, 'est_sz': est,
            'latin': _mode([i['latin'] for i in infos]), 'autofit': _mode([i['autofit'] for i in infos]),
            'fill': _mode([i['fill'] for i in infos]),
            'ins': _mode([(i['lIns'], i['rIns'], i['tIns'], i['bIns']) for i in infos]),
            'bodyPr': _mode([re.search(r'<a:bodyPr\b[^>]*?/?>', i['seg']).group(0) if re.search(r'<a:bodyPr\b', i['seg']) else '' for i in infos]),
            'n': len(infos), 'layout': infos[0]['layout'], 'excluded': excluded, 'excluded_list': exl, 'contrib': contrib,
            'groups': group_summary, 'group': gkey / 100.0}


def _title_need_h(t_ins, b_ins, lines, sz, lnspc=1.0):
    """v16.28: 제목 띠가 글을 담는 데 필요한 높이(EMU) = 위·아래 안쪽 여백 + 줄 수 × 글자 크기 × 줄간격."""
    return int((t_ins or 0) + (b_ins or 0) + lines * (sz or 2800) / 100.0 * LINE_FACTOR * (lnspc or 1.0) * 12700)


def raise_title_band(deck, slide_no, dry_run=False, shrink_bottom=None):
    """v16.28 (발표 K8 선택 3): Google 안전 — 제목 자리 표시자 띠가 필요 높이보다 낮으면 위쪽 끝을 고정하고 필요 높이로 키운다.
    키운 띠가 아래 내용(본문·그림)과 겹치면 바꾸지 않고 알린다. 반환: 문자열 목록('[!]' = 바꾸지 않음)."""
    i = _title_info(deck, slide_no)
    if not i or i['kind'] != 'ph':
        return []
    lines = _title_lines(i, i['eff_sz'])
    need = _title_need_h(i['tIns'], i['bIns'], lines, i['eff_sz'], i.get('lnspc', 1.0))
    if i['h'] >= need - (i['bIns'] or 0):      # 글이 보이는 데는 위 여백 + 줄 높이면 된다(아래 여백은 먹혀도 보인다)
        return []
    below = [(n, y0) for n, y0, y1 in _shapes_below_title(deck, slide_no, i['start'], i['end']) if y1 > i['y']]
    hit = [(n, y0) for n, y0 in below if y0 < i['y'] + need - int(0.02 * EMU_IN)]
    new_b = None
    if hit:
        if shrink_bottom is None:
            return ['[!] 띠 %.2f" < 필요 %.2f" 인데 키우면 "%s" 와 겹친다 — 바꾸지 않음(--shrink-bottom-inset 이면 아래 여백을 줄여 본다)'
                    % (i['h'] / EMU_IN, need / EMU_IN, hit[0][0])]
        # v16.29 (발표 K9, 사용자 결정): 위 여백은 그대로(글자 자리를 다른 화면과 같게), 아래 여백만 줄여 아래 내용 위까지
        new_b = int(round(shrink_bottom * EMU_IN))
        need = need - (i['bIns'] or 0) + new_b
        top = min(y0 for _, y0 in hit)
        if i['y'] + need > top:
            return ['[!] 아래 여백을 %.2f" 로 줄여도 띠 %.2f" 가 "%s"(%.2f") 와 겹친다 — 바꾸지 않음'
                    % (shrink_bottom, need / EMU_IN, hit[0][0], top / EMU_IN)]
    base, mat = _title_materialized(i)
    seg = re.sub(r'(<a:off x="-?\d+" y="-?\d+"\s*/>\s*<a:ext cx="\d+" cy=")\d+(")', lambda m: m.group(1) + str(need) + m.group(2), base, 1)
    if new_b is not None and seg != i['seg']:
        bp = re.search(r'<a:bodyPr\b[^>]*?(/?)>', seg)
        if bp:
            tag = bp.group(0)
            new_tag = re.sub(r'\sbIns="-?\d+"', '', tag)
            new_tag = new_tag[:-2] + ' bIns="%d"/>' % new_b if new_tag.endswith('/>') else new_tag[:-1] + ' bIns="%d">' % new_b
            seg = seg.replace(tag, new_tag, 1)
    if not dry_run:
        p = deck._slide(slide_no); x = open(p, encoding='utf8').read()
        open(p, 'w', encoding='utf8').write(x[:i['start']] + seg + x[i['end']:])
    pre = '물려받던 제목 — 적어 넣음 · ' if mat else ''
    if new_b is not None:
        return [pre + '띠 %.2f" → %.2f"(%d줄) · 아래 여백 %.2f" → %.2f"(위 여백 그대로)' % (i['h'] / EMU_IN, need / EMU_IN, lines, (i['bIns'] or 0) / EMU_IN, new_b / EMU_IN)]
    return [pre + '띠 %.2f" → %.2f"(%d줄, 안쪽 여백 포함)' % (i['h'] / EMU_IN, need / EMU_IN, lines)]


def balance_title_band(deck, slide_no, prof, gap_in=0.1, min_ins_in=0.05, dry_run=False):
    """v16.30 (발표 K10, 사용자 09-27): 채운 제목 띠(회색 띠)를 규격 높이(prof — 기준 제목 무리의 줄 수별 높이)로 하되, 띠 아래 첫
    내용 윗끝 − gap 까지만(본문이 붙어 있을수록 여유가 줄어든다), **위·아래 여백을 같게**((띠 − 글 높이)/2, 최소 min_ins).
    위쪽 끝·글·글자 크기·띠 색은 그대로. 내용은 옮기지 않는다(§0-C). 반환: 문자열 목록('[!]' = 바꾸지 않음)."""
    i = _title_info(deck, slide_no)
    if not i or i['kind'] != 'ph' or not i['fill'] or '<a:noFill/>' in (i['fill'] or ''):
        return []
    sz = i['eff_sz'] or (prof or {}).get('est_sz') or 2800
    lines = _title_lines(i, sz)
    text_h = int(lines * sz / 100.0 * LINE_FACTOR * i.get('lnspc', 1.0) * 12700)
    target = (prof or {}).get('h_by_lines', {}).get(lines) if prof else None
    if target is None:
        t = (prof or {}).get('ins', (0, 0, i['tIns'], i['bIns']))
        target = text_h + (t[2] or 0) + (t[3] or 0)
    below = [(n, y0) for n, y0, y1 in _shapes_below_title(deck, slide_no, i['start'], i['end']) if y0 > i['y']]
    limit_by = None
    new_h = target
    if below:
        name, top = min(below, key=lambda b: b[1])
        room = top - int(gap_in * EMU_IN) - i['y']
        if room < new_h:
            new_h, limit_by = room, name
    min_ins = int(min_ins_in * EMU_IN)
    if new_h < text_h + 2 * min_ins:
        return ['[!] 띠를 %.2f" 까지만 쓸 수 있어(아래 "%s") 글 %.2f" + 여백 %.2f"×2 가 들어가지 않는다 — 바꾸지 않음'
                % (max(new_h, 0) / EMU_IN, limit_by, text_h / EMU_IN, min_ins_in)]
    ins = max(min_ins, (new_h - text_h) // 2)
    if abs(new_h - i['h']) < 0.02 * EMU_IN and abs((i['tIns'] or 0) - ins) < 0.02 * EMU_IN and abs((i['bIns'] or 0) - ins) < 0.02 * EMU_IN:
        return []
    base, mat = _title_materialized(i)
    seg = re.sub(r'(<a:off x="-?\d+" y="-?\d+"\s*/>\s*<a:ext cx="\d+" cy=")\d+(")', lambda m: m.group(1) + str(new_h) + m.group(2), base, 1)
    bp = re.search(r'<a:bodyPr\b[^>]*?/?>', seg)
    if bp:
        tag = bp.group(0)
        nt = re.sub(r'\s(?:tIns|bIns)="-?\d+"', '', tag)
        nt = (nt[:-2] + ' tIns="%d" bIns="%d"/>' % (ins, ins)) if nt.endswith('/>') else (nt[:-1] + ' tIns="%d" bIns="%d">' % (ins, ins))
        seg = seg.replace(tag, nt, 1)
    if not dry_run:
        p = deck._slide(slide_no); x = open(p, encoding='utf8').read()
        open(p, 'w', encoding='utf8').write(x[:i['start']] + seg + x[i['end']:])
    return [('물려받던 제목 — 적어 넣음 · ' if mat else '') + '띠 %.2f" → %.2f"%s · 위/아래 여백 %.2f"/%.2f" → %.2f"/%.2f" (%d줄 %dpt)' % (
        i['h'] / EMU_IN, new_h / EMU_IN, (' (아래 "%s" 까지)' % limit_by) if limit_by else ' (규격)',
        (i['tIns'] or 0) / EMU_IN, (i['bIns'] or 0) / EMU_IN, ins / EMU_IN, ins / EMU_IN, lines, sz // 100)]


def _theme_rgb(deck, slide_no):
    """마스터의 테마 색표 {이름: 'RRGGBB'} — bg1/tx1/bg2/tx2 는 마스터 clrMap 으로 풀어 둔다."""
    mp = _master_of(deck, slide_no)
    if not mp or not os.path.exists(mp):
        return {}
    rel = os.path.join(os.path.dirname(mp), '_rels', os.path.basename(mp) + '.rels')
    tm = re.search(r'Target="\.\./theme/(theme\d+\.xml)"', open(rel, encoding='utf8').read()) if os.path.exists(rel) else None
    if not tm:
        return {}
    th = open(os.path.join(deck.dir, 'ppt/theme', tm.group(1)), encoding='utf8').read()
    out = {}
    for m in re.finditer(r'<a:(dk1|lt1|dk2|lt2|accent\d|hlink|folHlink)>(.*?)</a:\1>', th, re.S):
        c = re.search(r'(?:srgbClr val|lastClr)="([0-9A-Fa-f]{6})"', m.group(2))
        if c:
            out[m.group(1)] = c.group(1).upper()
    cm = re.search(r'<p:clrMap\b([^>]*)/>', open(mp, encoding='utf8').read())
    amap = dict(re.findall(r'(\w+)="(\w+)"', cm.group(1))) if cm else {'bg1': 'lt1', 'tx1': 'dk1', 'bg2': 'lt2', 'tx2': 'dk2'}
    for k in ('bg1', 'tx1', 'bg2', 'tx2'):
        if amap.get(k) in out:
            out[k] = out[amap[k]]
    return out


PRST_RGB = {'white': 'FFFFFF', 'black': '000000', 'red': 'FF0000', 'yellow': 'FFFF00', 'lime': '00FF00', 'green': '008000',
            'blue': '0000FF', 'cyan': '00FFFF', 'aqua': '00FFFF', 'magenta': 'FF00FF', 'fuchsia': 'FF00FF', 'orange': 'FFA500',
            'gray': '808080', 'grey': '808080', 'silver': 'C0C0C0', 'navy': '000080', 'maroon': '800000', 'purple': '800080',
            'teal': '008080', 'olive': '808000', 'ltGray': 'C0C0C0', 'dkGray': '404040'}


def _fill_rgb(xml, theme):
    """solidFill 안의 srgbClr/schemeClr/prstClr → 'RRGGBB' (못 풀면 None). v16.33: prstClr(미리 정한 색 이름 — white 등)."""
    c = re.search(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', xml or '')
    if c:
        return c.group(1).upper()
    c = re.search(r'<a:schemeClr val="(\w+)"', xml or '')
    if c:
        return theme.get(c.group(1))
    c = re.search(r'<a:prstClr val="(\w+)"', xml or '')
    return PRST_RGB.get(c.group(1)) if c else None


def _color_keys(xml, theme):
    """색 비교 열쇠: {16진수, 이름(prstClr·schemeClr, 소문자)}."""
    keys = set()
    h = _fill_rgb(xml, theme)
    if h:
        keys.add(h)
    for m in re.finditer(r'<a:(?:prstClr|schemeClr) val="(\w+)"', xml or ''):
        keys.add(m.group(1).lower())
    return keys


def _rel_lum(rgb):
    def ch(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(rgb[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def _contrast(a, b):
    la, lb = sorted((_rel_lum(a), _rel_lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _lab(rgb):
    def ch(v):
        v = v / 255.0
        return ((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92
    r, g, b = (ch(int(rgb[i:i + 2], 16)) for i in (0, 2, 4))
    X = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    Y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    Z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3.0) if t > 0.008856 else 7.787 * t + 16 / 116.0
    return 116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))


def _delta_e(a, b):
    la, lb = _lab(a), _lab(b)
    return sum((p - q) ** 2 for p, q in zip(la, lb)) ** 0.5


def _darken_for(rgb, bg, others, min_contrast=3.0, min_de=20.0):
    """같은 색상(hue)·채도로 명도만 낮춰 bg 대비 min_contrast 이상, others(이미 쓰인 글자색) 모두와 색차 min_de 이상인 첫 색. 없으면 None."""
    import colorsys
    r, g, b = (int(rgb[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s_ = colorsys.rgb_to_hls(r, g, b)
    step = 0.02
    while l > 0.05:
        l -= step
        rr, gg, bb = colorsys.hls_to_rgb(h, l, s_)
        cand = '%02X%02X%02X' % (int(round(rr * 255)), int(round(gg * 255)), int(round(bb * 255)))
        if _contrast(cand, bg) >= min_contrast and all(_delta_e(cand, o) >= min_de for o in others):
            return cand
    return None


def _lum(rgb):
    r, g, b = (int(rgb[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _slide_bg_rgb(deck, slide_no, theme):
    """슬라이드 → 레이아웃 → 마스터 순서로 단색 배경. 그림·그라데이션이면 None, 어디에도 없으면 bg1."""
    paths = [deck._slide(slide_no), os.path.join(deck.dir, 'ppt/slideLayouts', deck.layout_of(slide_no)), _master_of(deck, slide_no)]
    for pth in paths:
        if not pth or not os.path.exists(pth):
            continue
        bg = re.search(r'<p:bg>(.*?)</p:bg>', open(pth, encoding='utf8').read(), re.S)
        if bg:
            if re.search(r'<a:(?:blipFill|gradFill|pattFill)\b', bg.group(1)):
                return None
            return _fill_rgb(bg.group(1), theme)
    return theme.get('bg1', 'FFFFFF')


def adopt_house_look(deck, slide_no, dry_run=False, light_text=0.85, light_bg=0.6, recolor=(), auto_light=True, darken=False, min_contrast=3.0):
    """v16.31 (발표 K12): 가져온 슬라이드를 기준 덱 모양으로 — ① 밝은 배경 위의 아주 밝은 글자색(흰색 등)을 지워 테마 글자색을
    따르게(강조색·어두운 채움 상자 안의 흰 글자는 그대로), ② 제목 자리 표시자가 비었으면 위쪽의 제목 글상자(위 25% 안, 가장 큰
    글자, 두 문단 이하·80자 이하)를 제목 자리 표시자로 옮긴다(글만 옮기고 글상자는 지운다 — 뒤에 titles/title-bands 규격을 받게).
    그림·도형 색은 건드리지 않는다. 반환: 문자열 목록('[참고]' = 바꾸지 않은 까닭)."""
    p = deck._slide(slide_no); x = open(p, encoding='utf8').read()
    theme = _theme_rgb(deck, slide_no)
    W, H = deck.slide_size()
    out = []
    # ② 제목
    ti = _title_info(deck, slide_no)
    has_title = bool(ti and ti['kind'] == 'ph' and ''.join(ti['paras']).strip())
    if not has_title:
        cands = []
        for m in re.finditer(r'<p:sp>(?:(?!<p:sp>).)*?</p:sp>', x, re.S):
            seg = m.group(0)
            if '<p:ph' in seg or '<p:txBody>' not in seg:
                continue
            xf = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', seg)
            paras = [html.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>', q))) for q in re.findall(r'<a:p>.*?</a:p>', seg, re.S)]
            paras = [q for q in paras if q.strip()]
            szs = [int(v) for v in re.findall(r'<a:rPr\b[^>]*\bsz="(\d+)"', seg)]
            if xf and paras and int(xf.group(2)) < H * 0.25:
                cands.append((max(szs) if szs else 0, m, seg, paras))
        big = sorted(cands, key=lambda c: -c[0])
        lay = os.path.join(deck.dir, 'ppt/slideLayouts', deck.layout_of(slide_no))
        lay_has_title = os.path.exists(lay) and re.search(r'<p:ph\b[^>]*type="(?:title|ctrTitle)"', open(lay, encoding='utf8').read())
        if not big:
            out.append('[참고] 제목 자리 표시자가 비었는데 위쪽에 제목 글상자 후보가 없다')
        elif len(big) > 1 and big[0][0] == big[1][0]:
            out.append('[참고] 위쪽 글상자 중 가장 큰 글자가 둘 이상(%dpt) — 제목을 고르지 않음' % (big[0][0] // 100))
        elif len(big[0][3]) > 2 or len(' '.join(big[0][3])) > 80:
            out.append('[참고] 위쪽 가장 큰 글상자가 제목으로 보기에 길다 — 옮기지 않음: "%s"' % ' '.join(big[0][3])[:40])
        elif not lay_has_title:
            out.append('[참고] 레이아웃에 제목 자리 표시자가 없다 — 옮기지 않음')
        else:
            sz, m, seg, paras = big[0]
            text = ' '.join(t.strip() for t in paras)
            ids = [int(v) for v in re.findall(r'<p:cNvPr\b[^>]*\bid="(\d+)"', x)]
            body = '<a:p><a:r><a:rPr lang="ko-KR" dirty="0"/><a:t>%s</a:t></a:r></a:p>' % html.escape(text, quote=False)
            if ti and ti['kind'] == 'ph':      # 빈 제목 자리 표시자에 글을 넣는다
                new_t = re.sub(r'(<p:txBody>.*?)(<a:p>.*</a:p>|<a:p/>)(\s*</p:txBody>)', lambda mm: mm.group(1) + body + mm.group(3), ti['seg'], 1, flags=re.S)
                if '<p:txBody>' not in ti['seg']:
                    new_t = ti['seg'].replace('</p:sp>', '<p:txBody><a:bodyPr/><a:lstStyle/>%s</p:txBody></p:sp>' % body)
                x2 = x[:ti['start']] + new_t + x[ti['end']:]
                x2 = x2.replace(seg, '', 1)
            else:
                sp = ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="제목 %d"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="title"/></p:nvPr>'
                      '</p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>%s</p:txBody></p:sp>') % (max(ids + [1]) + 1, max(ids + [1]) + 1, body)
                x2 = x.replace(seg, '', 1)
                x2 = re.sub(r'(<p:grpSpPr\s*/>|<p:grpSpPr>.*?</p:grpSpPr>)', lambda mm: mm.group(1) + sp, x2, 1, flags=re.S)
            x = x2
            out.append('제목 글상자 "%s"(%dpt) → 제목 자리 표시자' % (text[:40], sz // 100))
    # ①′ v16.32 (발표 K14, 사용자 09-28): 지정한 색(--recolor, 예: 연두 92D050·주황 FFC000)은 배경과 관계없이 테마 글자색으로 — 빨강은 강조로 남긴다
    rec = set()
    for c in (recolor or ()):
        c = c.strip().lstrip('#')
        if c:
            rec.add(c.upper() if re.fullmatch(r'[0-9A-Fa-f]{6}', c) else c.lower())
            if c.lower() in {k.lower() for k in PRST_RGB}:     # 이름을 주면 같은 16진수 색도(white = FFFFFF)
                rec.add(PRST_RGB[next(k for k in PRST_RGB if k.lower() == c.lower())])
    if rec:
        n_rec = 0

        def fix_rec(rm):
            nonlocal n_rec
            inner = rm.group(0)
            sf = re.search(r'<a:solidFill>(.*?)</a:solidFill>', inner, re.S)
            if sf and _color_keys(sf.group(1), theme) & rec:      # v16.33 (발표 K15-1): 이름(white·black)·테마 색도
                n_rec += 1
                return inner.replace(sf.group(0), '', 1)
            return inner
        x = re.sub(r'<a:(?:rPr|endParaRPr)\b[^>]*>.*?</a:(?:rPr|endParaRPr)>', fix_rec, x, flags=re.S)
        if n_rec:
            out.append('지정한 색 %s %d곳을 지워 테마 글자색으로' % ('·'.join(sorted(rec)), n_rec))
    # ① 글자색
    bg = _slide_bg_rgb(deck, slide_no, theme)
    if bg is None:
        out.append('[참고] 배경이 그림·그라데이션 — 글자색 그대로')
    elif _lum(bg) < light_bg:
        out.append('[참고] 배경이 어둡다(#%s) — 글자색 그대로' % bg)
    elif not auto_light:
        pass                                    # v16.33 (발표 K15-1): 밝은 색 자동 지우기를 끈다 — 목록에 없는 색은 강조로 남긴다
    else:
        n_runs = 0

        def fix_shape(mm):
            nonlocal n_runs
            seg = mm.group(0)
            sp = (re.search(r'<p:spPr\b.*?</p:spPr>', seg, re.S) or [''])[0]
            own = _fill_rgb((re.search(r'<a:solidFill>.*?</a:solidFill>', re.sub(r'<a:ln\b.*?</a:ln>', '', sp, flags=re.S), re.S) or [''])[0], theme)
            if own and _lum(own) < light_bg:
                return seg                      # 어두운 채움 상자 안의 흰 글자는 그대로

            def fix_rpr(rm):
                nonlocal n_runs
                inner = rm.group(0)
                sf = re.search(r'<a:solidFill>(.*?)</a:solidFill>', inner, re.S)
                c = _fill_rgb(sf.group(1), theme) if sf else None
                if c and _lum(c) >= light_text:
                    n_runs += 1
                    return inner.replace(sf.group(0), '', 1)
                return inner
            return re.sub(r'<a:(?:rPr|endParaRPr)\b[^>]*>.*?</a:(?:rPr|endParaRPr)>', fix_rpr, seg, flags=re.S)
        x = re.sub(r'<p:sp>(?:(?!<p:sp>).)*?</p:sp>', fix_shape, x, flags=re.S)
        if n_runs:
            out.append('밝은 글자색 %d곳을 지워 테마 글자색으로(배경 #%s)' % (n_runs, bg))
    # ② v16.33 (발표 K15-1 개정): 배경 대비가 모자란 강조색만 같은 계열의 진한 색으로 — 그 화면의 다른 글자색·빨강과 구분되게
    if darken and bg:
        used = set()
        for sf in re.findall(r'<a:rPr\b[^>]*>.*?<a:solidFill>(.*?)</a:solidFill>', x, re.S):
            c = _fill_rgb(sf, theme)
            if c:
                used.add(c)
        used.add('FF0000')
        changes = {}
        for c in sorted(used):
            if c == 'FF0000' or _contrast(c, bg) >= min_contrast:
                continue
            new = _darken_for(c, bg, [o for o in used | set(changes.values()) if o != c], min_contrast)
            changes[c] = new
        n_dk = 0

        def fix_dk(rm):
            nonlocal n_dk
            inner = rm.group(0)
            sf = re.search(r'<a:solidFill>(.*?)</a:solidFill>', inner, re.S)
            c = _fill_rgb(sf.group(1), theme) if sf else None
            if c in changes and changes[c]:
                n_dk += 1
                return inner.replace(sf.group(0), '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % changes[c], 1)
            return inner
        x = re.sub(r'<a:(?:rPr|endParaRPr)\b[^>]*>.*?</a:(?:rPr|endParaRPr)>', fix_dk, x, flags=re.S)
        for c, new in sorted(changes.items()):
            out.append(('배경 대비가 낮은 %s → %s(대비 %.1f → %.1f)' % (c, new, _contrast(c, bg), _contrast(new, bg))) if new else
                       ('[!] 배경 대비가 낮은 %s — 구분되는 진한 색을 찾지 못해 그대로' % c))
        if n_dk:
            out.append('진하게 바꾼 조각 %d' % n_dk)
    if not dry_run:
        open(p, 'w', encoding='utf8').write(x)
    return out


def _band_shape(x, W):
    """v16.33 (발표 K15-3): 제목 띠로 따로 그린 도형 — 글 없는 채운 사각형, 위쪽(윗끝 0.1" 이내)·가로 거의 전체(90%↑)·높이 2" 이하.
    둘 이상이면 None(애매)."""
    hits = []
    for m in re.finditer(r'<p:sp>(?:(?!<p:sp>).)*?</p:sp>', x, re.S):
        seg = m.group(0)
        if '<p:ph' in seg or _AT.search(seg) and ''.join(_AT.findall(seg)).strip():
            continue
        g = _GEO.search(seg)
        sp = (re.search(r'<p:spPr\b.*?</p:spPr>', seg, re.S) or [''])[0]
        if not g or not re.search(r'<a:(?:solidFill|gradFill)\b', re.sub(r'<a:ln\b.*?</a:ln>', '', sp, flags=re.S)):
            continue
        gx, gy, gw, gh = (int(v) for v in g.groups())
        if gy <= 0.1 * EMU_IN and gx <= 0.1 * EMU_IN and gw >= 0.9 * W and gh <= 2 * EMU_IN and 'prst="line"' not in seg:
            nm = re.search(r'<p:cNvPr\b[^>]*\bname="([^"]*)"', seg)
            hits.append({'seg': seg, 'geo': (gx, gy, gw, gh), 'name': html.unescape(nm.group(1)) if nm else ''})
    return hits[0] if len(hits) == 1 else None


def _ph_geo(deck, slide_no, seg):
    """자리 표시자가 물려받는 위치·크기: 레이아웃의 같은 idx(없으면 같은 type), 없으면 마스터의 같은 type."""
    ph = re.search(r'<p:ph\b([^>]*)/?>', seg)
    if not ph:
        return None
    idx = re.search(r'idx="(\d+)"', ph.group(1)); typ = (re.search(r'type="(\w+)"', ph.group(1)) or [None, 'body'])[1]
    for f in (os.path.join(deck.dir, 'ppt/slideLayouts', deck.layout_of(slide_no)), _master_of(deck, slide_no)):
        if not f or not os.path.exists(f):
            continue
        for m in re.finditer(r'<p:sp>(?:(?!<p:sp>).)*?</p:sp>', open(f, encoding='utf8').read(), re.S):
            q = re.search(r'<p:ph\b([^>]*)/?>', m.group(0))
            if not q:
                continue
            same = (idx and re.search(r'idx="%s"' % idx.group(1), q.group(1))) or \
                   ((re.search(r'type="(\w+)"', q.group(1)) or [None, 'body'])[1] == typ and (not idx or 'master' in f.lower()))
            g = _GEO.search(m.group(0))
            if same and g:
                return tuple(int(v) for v in g.groups())
    return None


def _wrap_lines(text, size_pt, first_w, rest_w, font_path=None):
    """v16.37 (발표 K22-2): 단어 단위 줄바꿈 줄 수 — 한 줄에 안 드는 긴 단어는 자기 폭만큼 줄을 차지한다(쪼개지 않는 PowerPoint 처럼
    다음 줄로 넘기고, 그래도 넘치면 글자 단위로 나뉜다). 한글은 글자마다 끊을 수 있다."""
    emu = lambda pt: pt * 12700
    toks = re.findall(r'[\uac00-\ud7a3]|[^\s\uac00-\ud7a3]+', text)
    if not toks:
        return 1
    sp = emu(_text_width_pt(' ', size_pt, font_path)) * 0.6
    lines, cur, cap = 1, 0.0, max(1.0, first_w)
    for t in toks:
        w = emu(_text_width_pt(t, size_pt, font_path))
        add = w if cur == 0 else w + (0 if re.match(r'[\uac00-\ud7a3]', t) else sp)
        if cur + add <= cap:
            cur += add; continue
        if cur > 0:
            lines += 1; cap = max(1.0, rest_w); cur = 0.0
        while w > cap:                       # 칸보다 긴 한 단어
            w -= cap; lines += 1
        cur = w
    return lines


def _para_metrics(deck, seg, default_sz=1800):
    """글상자 문단마다 {text, sz(pt), marL, indent(EMU), ln_pct, ln_pts, bef, aft(pt)} — 문단 pPr → 도형 lstStyle 같은 수준 → 발표 기본 글 스타일."""
    lst = (re.search(r'<a:lstStyle>(.*?)</a:lstStyle>', seg, re.S) or [None, ''])[1]
    pres = os.path.join(deck.dir, 'ppt/presentation.xml')
    dts = (re.search(r'<p:defaultTextStyle>(.*?)</p:defaultTextStyle>', open(pres, encoding='utf8').read(), re.S) or [None, ''])[1] if os.path.exists(pres) else ''
    def lvl_attr(src, lv, attr):
        m = re.search(r'<a:lvl%dpPr\b([^>]*)' % (lv + 1), src or '')
        mm = re.search(r'\b%s="(-?\d+)"' % attr, m.group(1)) if m else None
        return int(mm.group(1)) if mm else None
    def lvl_ln(src, lv):
        m = re.search(r'<a:lvl%dpPr\b[^>]*>(.*?)</a:lvl%dpPr>' % (lv + 1, lv + 1), src or '', re.S)
        return m.group(1) if m else ''
    out = []
    for pm in re.findall(r'<a:p>(.*?)</a:p>', seg, re.S):
        t = html.unescape(''.join(_AT.findall(pm)))
        szs = [int(v) for v in re.findall(r'<a:(?:rPr|endParaRPr)\b[^>]*\bsz="(\d+)"', pm)] or [default_sz]
        ppr_tag = (re.search(r'<a:pPr\b[^>]*', pm) or [''])[0]
        ppr_body = (re.search(r'<a:pPr\b[^>]*>(.*?)</a:pPr>', pm, re.S) or [None, ''])[1]
        lv = int((re.search(r'\blvl="(\d)"', ppr_tag) or [0, 0])[1])
        def pick(attr):
            m = re.search(r'\b%s="(-?\d+)"' % attr, ppr_tag)
            if m:
                return int(m.group(1))
            for src in (lst, dts):
                v = lvl_attr(src, lv, attr)
                if v is not None:
                    return v
            return 0
        lnsrc = ppr_body or lvl_ln(lst, lv) or lvl_ln(dts, lv)
        pct = re.search(r'<a:lnSpc><a:spcPct val="(\d+)"', lnsrc); pts = re.search(r'<a:lnSpc><a:spcPts val="(\d+)"', lnsrc)
        bef = re.search(r'<a:spcBef><a:spcPts val="(\d+)"', lnsrc); aft = re.search(r'<a:spcAft><a:spcPts val="(\d+)"', lnsrc)
        out.append({'text': t, 'sz': max(szs) / 100.0, 'marL': pick('marL'), 'indent': pick('indent'),
                    'ln_pct': int(pct.group(1)) / 100000.0 if pct else 1.0, 'ln_pts': int(pts.group(1)) / 100.0 if pts else None,
                    'bef': int(bef.group(1)) / 100.0 if bef else 0.0, 'aft': int(aft.group(1)) / 100.0 if aft else 0.0})
    return out


def _top_shapes(x):
    """spTree 바로 아래 도형들(그룹은 한 덩어리) — [{'tag','start','end','seg','name','geo'}]."""
    tree = re.search(r'<p:spTree>(.*)</p:spTree>', x, re.S)
    off0, body, res, k = tree.start(1), tree.group(1), [], 0
    while True:
        m = re.search(r'<p:(sp|pic|cxnSp|graphicFrame|grpSp)>', body[k:])
        if not m:
            break
        tag, a = m.group(1), k + m.start()
        depth, j = 0, a
        for mm in re.finditer(r'<p:%s>|</p:%s>' % (tag, tag), body[a:]):
            depth += 1 if mm.group(0)[1] != '/' else -1
            if depth == 0:
                j = a + mm.end(); break
        segx = body[a:j]
        g = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"\s*/>\s*<a:ext cx="(\d+)" cy="(\d+)"', segx)
        nm = re.search(r'<p:cNvPr\b[^>]*\bname="([^"]*)"', segx)
        res.append({'tag': tag, 'start': off0 + a, 'end': off0 + j, 'seg': segx, 'name': html.unescape(nm.group(1)) if nm else '',
                    'geo': tuple(int(v) for v in g.groups()) if g else None})
        k = j
    return res


def _inter(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def _inside_frac(a, b):
    """a 가 b 안에 드는 넓이 비율."""
    w = max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])); h = max(0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
    return (w * h) / float(max(1, a[2] * a[3]))


def fit_layout(deck, slide_no, title_min=20, body_min=14, body_max=None, max_up=1.5, min_scale=0.5, band_gap=0.08, gap=0.2,
               margin=0.05, col_gap=0.2, min_text_w=0.35, text_margin=1.1, arrange='auto', drop_title=False, label_pos=None, dry_run=False):
    """v16.33 1단계 → v16.34 2단계 (발표 K16·K17, 사용자 09-28 배치 양식): 밀집 화면.
    ① 제목 띠를 촘촘하게(글 높이 + 위아래 band_gap, 위에 붙임, 2줄이면 title_min 까지 줄여 1줄이 되는지) — drop_title 이면 제목·띠 도형을
       빼고 그 자리까지 영역으로(노트는 그대로). 띠와 본문 간격 gap(기본 0.2" — K17 F3).
    ② 배치 — arrange='side'(그림이 본문 오른쪽이면 auto 가 고른다 — K17 S2·S3): 그림들(주석·바로 옆 작은 설명 상자와 한 덩어리)을 영역
       오른쪽 위에 붙여 영역 높이·(영역 폭 − 글 칸 최소 폭) 안에서 비율대로, 본문은 그 왼쪽 칸 폭으로 좁히고 글자는 body_max(없으면 원래
       크기)에서 body_min 사이에서 칸에 드는 가장 큰 크기. arrange='keep': 1단계처럼 그림 구석 고정 비율, 본문 글자는 원래→body_min.
    ③ 본문 상자 높이는 추정 글 높이 × text_margin 으로 적어 넣는다(K17 F1 — spAutoFit 상자의 저장 높이가 그대로라 PowerPoint 가 옛 높이로
       그렸다). 겹침은 이 **저장 위치** 로 판정(K17 F2).
    ④ 이름표는 label_pos(기준 화면의 이름표 자리)로 옮기고 맨 앞 층으로, 그림은 이름표와도 안 겹치게(K17 S4).
    안 되면 바꾸지 않고 '[!] 나누기 필요'. 글 내용은 바꾸지 않는다. 반환: 문자열 목록."""
    x = open(deck._slide(slide_no), encoding='utf8').read()
    W, H = deck.slide_size(); E = EMU_IN
    i = _title_info(deck, slide_no)
    if not drop_title and (not i or i['kind'] != 'ph'):
        return ['[!] 제목 자리 표시자가 없다 — adopt-house-look 으로 먼저']
    out = []
    band = _band_shape(x, W)
    shp = _top_shapes(x)
    tsh = [q for q in shp if re.search(r'<p:ph\b[^>]*type="(?:title|ctrTitle)"', q['seg'])]
    rest = [q for q in shp if q not in tsh and not (band and q['seg'] == band['seg'])]
    pics = [q for q in rest if q['geo'] and (q['tag'] == 'pic' or (q['tag'] == 'grpSp' and '<p:pic>' in q['seg']))]
    txt = lambda q: html.unescape(''.join(_AT.findall(q['seg']))).strip()
    texts = [q for q in rest if q['geo'] and q['tag'] == 'sp' and txt(q)]
    label = next((q for q in texts if re.match(r'\(R\d', txt(q))), None)
    ann = {}
    for q in rest:
        if q in pics or not q['geo'] or q is label:
            continue
        best = max(pics, key=lambda p_: _inside_frac(q['geo'], p_['geo']), default=None)
        if best and _inside_frac(q['geo'], best['geo']) >= 0.7:
            ann.setdefault(id(best), []).append(q)
    attached = {id(q) for v in ann.values() for q in v}
    cand = [q for q in texts if q is not label and id(q) not in attached]
    body = max(cand, key=lambda q: q['geo'][2] * q['geo'][3], default=None)
    # 그림 바로 바깥(0.3" 이내)의 작은 글상자 = 그림 설명 — 그림과 같이 움직인다(자리 규칙은 뒤 단계)
    cites = [q for q in texts if q is not body and q is not label and id(q) not in attached and _is_cite(txt(q))]
    cap_notes = []
    for q in texts:
        if q is body or q is label or id(q) in attached or q in cites:
            continue
        for p_ in pics:
            px, py, pw, ph_ = p_['geo']; g = int(0.3 * E)
            if q['geo'][2] * q['geo'][3] < 0.25 * pw * ph_ and _inter(q['geo'], (px - g, py - g, pw + 2 * g, ph_ + 2 * g)):
                ann.setdefault(id(p_), []).append(q); attached.add(id(q))
                qx, qy, qw, qh = q['geo']
                dist = max(0, max(px - (qx + qw), qx - (px + pw), py - (qy + qh), qy - (py + ph_)))
                cap_notes.append('설명 판정: "%s" — 그림 "%s" 과 %.2f" · 넓이 %d%%' % (q['name'], p_['name'], dist / E, 100 * qw * qh // max(1, pw * ph_)))
                break
    fixed = [q for q in rest if q['geo'] and q not in pics and q is not body and q is not label and id(q) not in attached and q not in cites
             and not re.search(r'<p:ph\b[^>]*type="(?:dt|ftr|sldNum)"', q['seg'])]
    fp = _theme_body_font_file(deck, slide_no)
    # ① 제목
    edits, removes = [], []
    if drop_title:
        for q in tsh:
            removes.append(q['seg'])
        if band:
            removes.append(band['seg'])
        top = int(margin * E) + int(0.05 * E)
        out.append('제목%s 뺌(앞 화면과 같은 제목 — 노트는 그대로)' % ('·띠 도형' if band else ''))
    else:
        tsz = i['eff_sz'] or 2800
        new_tsz = tsz
        if _title_lines(i, tsz) > 1:
            for p_ in range(tsz // 100 - 1, title_min - 1, -1):
                if _title_lines(i, p_ * 100) == 1:
                    new_tsz = p_ * 100; break
        t_text = int(_title_lines(i, new_tsz) * new_tsz / 100.0 * LINE_FACTOR * i.get('lnspc', 1.0) * 12700)
        bgap = int(band_gap * E); t_h = t_text + 2 * bgap
        tx, tw = (band['geo'][0], band['geo'][2]) if band else (i['x'], i['w'])
        top = t_h + int(gap * E)
        tseg, mat = _title_materialized(i)
        tseg = re.sub(r'<a:off x="-?\d+" y="-?\d+"\s*/>\s*<a:ext cx="\d+" cy="\d+"\s*/>', '<a:off x="%d" y="0"/><a:ext cx="%d" cy="%d"/>' % (tx, tw, t_h), tseg, 1)
        bpm = re.search(r'<a:bodyPr\b[^>]*?/?>', tseg)
        if bpm:
            nt = re.sub(r'\s(?:tIns|bIns)="-?\d+"', '', bpm.group(0))
            nt = (nt[:-2] + ' tIns="%d" bIns="%d"/>' % (bgap, bgap)) if nt.endswith('/>') else (nt[:-1] + ' tIns="%d" bIns="%d">' % (bgap, bgap))
            tseg = tseg.replace(bpm.group(0), nt, 1)
        if new_tsz != tsz:
            tseg = re.sub(r'(<a:(?:rPr|endParaRPr)\b[^>]*?\bsz=")\d+"', lambda mm: '%s%d"' % (mm.group(1), new_tsz), tseg)
            tseg = re.sub(r'<a:(rPr|endParaRPr)\b((?:(?!\bsz=)[^>])*?)(/?)>', lambda mm: '<a:%s%s sz="%d"%s>' % (mm.group(1), mm.group(2), new_tsz, mm.group(3)), tseg)
        edits.append((i['start'], i['end'], tseg))
        if band:
            nb = re.sub(r'<a:off x="-?\d+" y="-?\d+"\s*/>\s*<a:ext cx="(\d+)" cy="\d+"', lambda mm: '<a:off x="%d" y="0"/><a:ext cx="%s" cy="%d"' % (tx, mm.group(1), t_h), band['seg'], 1)
            s0 = x.find(band['seg']); edits.append((s0, s0 + len(band['seg']), nb))
        out.append('제목 띠 %.2f" → %.2f"(위에 붙임, 여백 %.2f")%s%s' % (((band['geo'][3] if band else i['h']) / E), t_h / E, band_gap,
                   (' · 제목 %dpt → %dpt' % (tsz // 100, new_tsz // 100)) if new_tsz != tsz else '', ' · 물려받던 제목 적어 넣음' if mat else ''))
    mx = int(margin * E)
    R0 = (mx, top, W - 2 * mx, H - mx - top)
    rx0, ry0, rx1, ry1 = R0[0], R0[1], R0[0] + R0[2], R0[1] + R0[3]
    # ④ 이름표 자리
    lab_box = None
    if label:
        lx, ly = (label_pos if label_pos else label['geo'][:2])
        lab_box = (lx, ly, label['geo'][2], label['geo'][3])
    # 본문 글 높이(여유 포함) — 폭 bw, 글자 비율 f
    b_szs = [int(v) for v in re.findall(r'<a:(?:rPr|endParaRPr)\b[^>]*\bsz="(\d+)"', body['seg'])] if body else []
    b_base = 1800
    if body and not b_szs:
        php = re.search(r'<p:ph\b([^>]*)/?>', body['seg'])
        if php:
            b_base = _body_level_sizes(deck, slide_no, php.group(1)).get(0) or 1800
    pmax = (max(b_szs) if b_szs else b_base) // 100
    bp = (re.search(r'<a:bodyPr\b[^>]*', body['seg']) or [''])[0] if body else ''
    l_, r_, t_, b_ = (int((re.search(r'\b%s="(-?\d+)"' % k, bp) or [0, d])[1]) for k, d in (('lIns', 91440), ('rIns', 91440), ('tIns', 45720), ('bIns', 45720)))
    paras = _para_metrics(deck, body['seg'], pmax * 100) if body else []
    def text_h(pt, bw):
        # v16.37 (발표 K22-2): 단어 단위 줄바꿈, 문단 들여쓰기(marL·indent — 글머리표 자리), 줄 간격(lnSpc %·pt), 앞뒤 간격 —
        # 전에는 글자 수 ÷ 폭 모델이라 좁은 칸(3.32")에서 5.13" 로 추정했는데 실제는 슬라이드 아래로 한참 넘쳤다
        f = pt / float(pmax)
        hh = 0.0
        for q in paras:
            ps = q['sz'] * f
            line_h = (q['ln_pts'] * f if q['ln_pts'] else ps * LINE_FACTOR * q['ln_pct']) * 12700
            hh += (q['bef'] + q['aft']) * f * 12700
            if not q['text'].strip():
                hh += line_h * 0.5; continue
            avail = bw - l_ - r_ - q['marL']
            first = avail - q['indent']
            hh += _wrap_lines(q['text'], ps, first, avail, fp) * line_h
        return int(hh * text_margin) + t_ + b_
    cite_boxes, cy_ = [], H - int(margin * E)
    for q in sorted(cites, key=lambda q: -q['geo'][1]):          # 아래에 있던 것부터 우하단에 쌓는다(K19-2, §0)
        qw, qh = min(q['geo'][2], W - 2 * int(margin * E)), q['geo'][3]
        cy_ -= qh
        cite_boxes.append((q, (W - int(margin * E) - qw, cy_, qw, qh)))
        cy_ -= int(0.03 * E)
    obst0 = [q['geo'] for q in fixed if not any(_inter(q['geo'], p_['geo']) for p_ in pics)] + ([lab_box] if lab_box else []) + [b for _, b in cite_boxes]
    # v16.37 (발표 K22-1): auto 는 그림이 본문 **옆**(오른쪽이면서 그림 윗끝이 본문 상자의 위쪽 60% 안)일 때만 옆 배치 —
    # 본문이 위에 전폭이고 그림이 그 아래인 화면(인터벤션 27)을 옆 배치로 골라 본문을 좁은 칸에 밀어 넣었다
    side = bool(pics and body) and (arrange == 'side' or (arrange == 'auto' and all(
        p_['geo'][0] + p_['geo'][2] / 2.0 > body['geo'][0] + body['geo'][2] / 2.0 and p_['geo'][1] < body['geo'][1] + 0.6 * body['geo'][3]
        for p_ in pics)))
    groups = [(p_, ann.get(id(p_), [])) for p_ in pics]
    plan = None                    # {'body': (x,y,w,h,pt), 'pics': [(pic, k, (ax,ay), (dx,dy))]}
    if side:
        ux0 = min(p_['geo'][0] for p_ in pics); uy0 = min(p_['geo'][1] for p_ in pics)
        ux1 = max(p_['geo'][0] + p_['geo'][2] for p_ in pics); uy1 = max(p_['geo'][1] + p_['geo'][3] for p_ in pics)
        uw, uh = ux1 - ux0, uy1 - uy0
        k = min(max_up, R0[3] / float(uh), (R0[2] - min_text_w * W) / float(uw))
        k = int(k * 100) / 100.0
        while k >= min_scale - 1e-9:
            box = (rx1 - int(uw * k), ry0, int(uw * k), int(uh * k))
            if not any(_inter(box, o) for o in obst0):
                break
            k = round(k - 0.02, 4)
        if k >= min_scale - 1e-9:
            bx = max(body['geo'][0], rx0); bw = rx1 - int(uw * k) - int(col_gap * E) - bx
            top_pt = body_max or pmax
            for pt in range(top_pt, body_min - 1, -1):
                h_ = text_h(pt, bw)
                bb = (bx, ry0, bw, h_)
                if ry0 + h_ <= ry1 and not any(_inter(bb, o) for o in obst0):
                    plan = {'body': (bx, ry0, bw, h_, pt), 'pics': [(p_, k, (ux1, uy0), (rx1 - ux1, ry0 - uy0)) for p_ in pics]}
                    break
        if plan is None:
            out.append('[참고] 옆 배치로는 안 된다 — 제자리 배치로 본다')
    if plan is None:
        best = None
        for pt in range(pmax, body_min - 1, -1):
            if body:
                bx, by, bw, bh = body['geo']; by = max(by, ry0)
                h_ = text_h(pt, bw)
                if by + h_ > ry1:
                    continue
                bb = (bx, by, bw, h_)
            else:
                bb = None
            obst = obst0 + ([bb] if bb else [])
            placed, ok = [], True
            for p_ in sorted(pics, key=lambda q: -(q['geo'][2] * q['geo'][3])):
                gx, gy, gw, gh = p_['geo']
                dy = max(0, ry0 - gy); gy += dy
                corners = {'tl': (gx, gy, rx0, ry0), 'tr': (gx + gw, gy, rx1, ry0), 'bl': (gx, gy + gh, rx0, ry1), 'br': (gx + gw, gy + gh, rx1, ry1)}
                cn = min(corners, key=lambda c: (corners[c][0] - corners[c][2]) ** 2 + (corners[c][1] - corners[c][3]) ** 2)
                ax, ay = corners[cn][0], corners[cn][1]
                if abs(ax - corners[cn][2]) <= 0.75 * E:
                    ax = corners[cn][2]
                if abs(ay - corners[cn][3]) <= 0.75 * E:
                    ay = corners[cn][3]
                k, hit = max_up, None
                while k >= min_scale - 1e-9:
                    nw, nh = int(gw * k), int(gh * k)
                    box = (ax - nw if cn[1] == 'r' else ax, ay - nh if cn[0] == 'b' else ay, nw, nh)
                    if box[0] >= rx0 and box[1] >= ry0 and box[0] + nw <= rx1 and box[1] + nh <= ry1 and \
                            not any(_inter(box, o) for o in obst + [b for _, _, _, _, b in placed]):
                        hit = (p_, k, (ax, ay), (0, dy), box); break
                    k = round(k - 0.02, 4)
                if not hit:
                    ok = False; break
                placed.append(hit)
            if not ok:
                continue
            area = sum(b[2] * b[3] for _, _, _, _, b in placed)
            if best is None or area > best[0] * 1.001:
                best = (area, {'body': (bb + (pt,)) if bb else None, 'pics': [(p_, k, a, d) for p_, k, a, d, _ in placed]})
        if best is None:
            # v16.35 (발표 K19-1): 크기·위치 조정만 건너뛰고, 제목 빼기와 이름표(자리·맨 앞)는 적용한다
            out = [o for o in out if o.startswith('제목') and '뺌' in o]
            msg = '[!] 본문 %dpt·그림 %d%% 하한에서도 겹침 없이 안 들어간다 — 크기 조정 못 함%s(나누기 필요할 수 있음)' % (
                body_min, int(min_scale * 100), ' · 제목 뺌·이름표만' if (drop_title or label) else '')
            if not (drop_title or label):
                return [msg]
            edits = []
            plan = {'body': None, 'pics': []}
            cite_boxes = []
            out.insert(0, msg)
        else:
            plan = best[1]      # v16.36 (발표 K20): 16.35 가 K19-1 을 넣으며 이 줄을 빠뜨려 제자리 배치 '성공' 화면에서 TypeError
    # 적용 — 본문
    if body and plan['body']:
        bx, by, bw, bh, pt = plan['body']
        f = pt / float(pmax)
        nb = body['seg']
        if abs(f - 1) > 1e-3:
            nb = re.sub(r'(<a:(?:rPr|endParaRPr)\b[^>]*?\bsz=")(\d+)"', lambda mm: '%s%d"' % (mm.group(1), int(round(int(mm.group(2)) * f))), nb)
            nb = re.sub(r'<a:(rPr|endParaRPr)\b((?:(?!\bsz=)[^>])*?)(/?)>', lambda mm: '<a:%s%s sz="%d"%s>' % (mm.group(1), mm.group(2), pt * 100, mm.group(3)), nb)
            nb = re.sub(r'<a:r><a:t\b', '<a:r><a:rPr lang="ko-KR" sz="%d"/><a:t' % (pt * 100), nb)
        if re.search(r'<a:off x="-?\d+" y="-?\d+"', nb):
            nb = re.sub(r'<a:off x="-?\d+" y="-?\d+"\s*/>\s*<a:ext cx="\d+" cy="\d+"', '<a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"' % (bx, by, bw, bh), nb, 1)
        else:
            xf = '<a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>' % (bx, by, bw, bh)
            nb = re.sub(r'<p:spPr\s*/>', '<p:spPr>%s</p:spPr>' % xf, nb, 1) if re.search(r'<p:spPr\s*/>', nb) else re.sub(r'(<p:spPr\b[^>]*>)', lambda mm: mm.group(1) + xf, nb, 1)
        edits.append((body['start'], body['end'], nb))
        ob = body['geo']
        out.append('본문 "%s" %dpt → %dpt · 상자 %.2f×%.2f" → %.2f×%.2f"(높이 = 추정 글 높이 × %.1f)%s' % (
            body['name'], pmax, pt, ob[2] / E, ob[3] / E, bw / E, bh / E, text_margin, ' · 옆 배치(글 왼쪽·그림 오른쪽)' if side and plan.get('pics') and plan['body'][1] == ry0 and side else ''))
    # 적용 — 그림(주석·설명 함께)
    for p_, k, (ax, ay), (dx, dy) in plan['pics']:
        def tf(g):
            X, Y, CX, CY = g
            X += dx; Y += dy
            AX, AY = ax + dx, ay + dy
            return (int(AX + (X - AX) * k), int(AY + (Y - AY) * k), int(CX * k), int(CY * k))
        for q in [p_] + ann.get(id(p_), []):
            qx, qy, qw, qh = tf(q['geo'])
            if q is not p_ and (qx < 0 or qy < 0 or qx + qw > W or qy + qh > H):
                if qw > W or qh > H:
                    out.append('[!] "%s" 이 그림과 같이 옮기면 슬라이드 밖 — 옮기지 않음' % q['name']); continue
                qx, qy = min(max(qx, 0), W - qw), min(max(qy, 0), H - qh)
                out.append('[참고] "%s" 이 슬라이드 밖으로 나가 안으로 들임' % q['name'])
            qs = re.sub(r'<a:off x="-?\d+" y="-?\d+"\s*/>\s*<a:ext cx="\d+" cy="\d+"', '<a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"' % (qx, qy, qw, qh), q['seg'], 1)
            if q is not p_ and abs(k - 1) > 1e-3:
                qs = re.sub(r'(<a:(?:rPr|endParaRPr)\b[^>]*?\bsz=")(\d+)"', lambda mm: '%s%d"' % (mm.group(1), max(800, int(int(mm.group(2)) * k))), qs)
            edits.append((q['start'], q['end'], qs))
        out.append('그림 "%s" %d%%%s' % (p_['name'], int(round(k * 100)), (' · 주석·설명 %d 같이' % len(ann.get(id(p_), []))) if ann.get(id(p_)) else ''))
    # 적용 — 인용·출처 메모(우하단, 슬라이드 안)
    for q, (cx_, cy2, cw, ch) in cite_boxes:
        qs = re.sub(r'<a:off x="-?\d+" y="-?\d+"\s*/>\s*<a:ext cx="\d+" cy="\d+"', '<a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"' % (cx_, cy2, cw, ch), q['seg'], 1)
        if qs != q['seg']:
            edits.append((q['start'], q['end'], qs))
            out.append('인용·출처 "%s" → 우하단(%.2f", %.2f")' % (txt(q)[:24], cx_ / E, cy2 / E))
    out += cap_notes
    # 적용 — 이름표(자리·맨 앞)
    lab_seg = None
    if label:
        lx, ly, lw, lh = lab_box
        lab_seg = re.sub(r'<a:off x="-?\d+" y="-?\d+"', '<a:off x="%d" y="%d"' % (lx, ly), label['seg'], 1)
        edits.append((label['start'], label['end'], ''))
        if (lx, ly) != tuple(label['geo'][:2]):
            out.append('이름표 "%s" → 기준 자리(%.2f", %.2f")·맨 앞' % (txt(label)[:20], lx / E, ly / E))
        else:
            out.append('이름표 맨 앞으로')
    if not dry_run:
        for a_, b_, sg in sorted(edits, key=lambda e: -e[0]):
            x = x[:a_] + sg + x[b_:]
        for sg in removes:
            x = x.replace(sg, '', 1)
        if lab_seg:
            x = x.replace('</p:spTree>', lab_seg + '</p:spTree>', 1)
        open(deck._slide(slide_no), 'w', encoding='utf8').write(x)
    return out


CITE_RE = re.compile(r'et al|doi|\b(?:19|20)\d{2}\s*[;:]\s*\d|\b(?:19|20)\d{2}\b.*\b\d+\s*[-–]\s*\d+|'
                     r'\b(?:Radiology|Radiol|AJR|Am J|Eur|J Vasc|Cardiovasc|Interv|Surg|Journal|JAMA|Lancet|NEJM)\b', re.I)
MEMO_RE = re.compile(r'^\s*\d{6}\b|^\s*(?:출처|source|from)\b|^(?=.{0,60}$).*(?:발표|선생님|강의)', re.I | re.S)   # 날짜로 시작하거나, 60자 이하 짧은 발표·출처 메모만


def _is_cite(text):
    """v16.35 (발표 K19-2): 인용(학술지·해·권:쪽, et al, doi) 또는 출처·발표 메모(날짜 숫자 6자리, '발표' 등) — 그림 설명이 아니다."""
    t = (text or '').strip()
    return bool(t) and len(t) <= 300 and bool(CITE_RE.search(t) or MEMO_RE.search(t))


def _label_spot(deck, slide_no):
    """기준 화면의 이름표((R… 로 시작하는 글상자) 위치."""
    for q in _top_shapes(open(deck._slide(slide_no), encoding='utf8').read()):
        if q['geo'] and q['tag'] == 'sp' and re.match(r'\s*\(R\d', html.unescape(''.join(_AT.findall(q['seg'])))):
            return q['geo'][:2]
    return None


def _body_pt_of(deck, slide_no):
    """기준 화면의 본문(가장 큰 글상자) 최대 글자 크기(pt)."""
    best = None
    for q in _top_shapes(open(deck._slide(slide_no), encoding='utf8').read()):
        if q['geo'] and q['tag'] == 'sp' and ''.join(_AT.findall(q['seg'])).strip() and not re.search(r'type="(?:title|ctrTitle)"', q['seg']):
            if best is None or q['geo'][2] * q['geo'][3] > best['geo'][2] * best['geo'][3]:
                best = q
    if not best:
        return None
    szs = [int(v) for v in re.findall(r'<a:rPr\b[^>]*\bsz="(\d+)"', best['seg'])]
    if szs:
        return max(szs) // 100
    php = re.search(r'<p:ph\b([^>]*)/?>', best['seg'])
    return ((_body_level_sizes(deck, slide_no, php.group(1)).get(0) or 1800) // 100) if php else None


def title_block(deck, slide_no, band_h=None, prof=None, gap_in=0.1, drop_rule=False, push=False, min_pt=12, dry_run=False):
    """v16.32 (발표 K14, 사용자 09-28): 가져온 해설 슬라이드를 "제목 띠 + 그 아래 본문" 으로 — `--screens` 로 준 화면만.
    ① 제목 자리 표시자의 띠를 band_h(없으면 prof 규격 무리의 줄 수별 높이)로, 위쪽 끝 고정·위아래 여백 같게(물려받는 제목은 적어 넣는다).
    ② drop_rule: 띠 안에 든 가로선 하나(옛 글상자 제목 밑줄 — 폭이 슬라이드의 40% 이상·두께 0.2" 이하)를 지운다. 둘 이상이면 지우지 않고 알림.
    ③ push: 제목이 아닌 상자·그림 중 윗끝이 '띠 아랫끝 + 간격' 보다 위인 것을 같은 거리만큼 한 덩어리로 내린다(§0-C 의 예외 — 사용자
       09-28, 이 명령으로 지정한 화면만). 내린 글상자가 슬라이드 아래를 넘으면 넘는 만큼 글자 크기를 비율로 줄여 적고 상자를 슬라이드 안으로
       (min_pt 밑으로는 줄이지 않고 알림). 그림은 옮기기만, 넘으면 알림. 반환: 문자열 목록('[!]'·'[참고]' = 바꾸지 않은 것)."""
    i = _title_info(deck, slide_no)
    if not i or i['kind'] != 'ph':
        return ['[!] 제목 자리 표시자가 없다 — adopt-house-look 으로 먼저 옮긴다']
    W, H = deck.slide_size()
    out = []
    sz = i['eff_sz'] or 2800
    lines = _title_lines(i, sz)
    text_h = int(lines * sz / 100.0 * LINE_FACTOR * i.get('lnspc', 1.0) * 12700)
    target = int(band_h * EMU_IN) if band_h else ((prof or {}).get('h_by_lines', {}).get(lines) or i['h'])
    x0 = open(deck._slide(slide_no), encoding='utf8').read()
    band = _band_shape(x0, W)
    base, mat = _title_materialized(i)
    if band:
        # v16.33 (발표 K15-3): 따로 그린 띠 도형 — 제목 자리 표시자를 그 띠에 맞추고, 띠 높이 = max(규격, 제목이 들어갈 높이), 도형과 함께
        bx, by, bw, bh = band['geo']
        target = max(target, text_h + int(0.1 * EMU_IN))
        base = re.sub(r'<a:off x="-?\d+" y="-?\d+"\s*/>\s*<a:ext cx="\d+" cy="\d+"\s*/>',
                      '<a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/>' % (bx, by, bw, target), base, 1)
        i = dict(i, x=bx, y=by, w=bw)
    ins = max(int(0.05 * EMU_IN), (target - text_h) // 2)
    seg = re.sub(r'(<a:off x="-?\d+" y="-?\d+"\s*/>\s*<a:ext cx="\d+" cy=")\d+(")', lambda m: m.group(1) + str(target) + m.group(2), base, 1)
    bp = re.search(r'<a:bodyPr\b[^>]*?/?>', seg)
    if bp:
        tag = bp.group(0); nt = re.sub(r'\s(?:tIns|bIns)="-?\d+"', '', tag)
        nt = (nt[:-2] + ' tIns="%d" bIns="%d"/>' % (ins, ins)) if nt.endswith('/>') else (nt[:-1] + ' tIns="%d" bIns="%d">' % (ins, ins))
        seg = seg.replace(tag, nt, 1)
    x = x0[:i['start']] + seg + x0[i['end']:]
    if band:
        bseg = band['seg']
        nb = re.sub(r'(<a:off x="-?\d+" y="-?\d+"\s*/>\s*<a:ext cx="\d+" cy=")\d+(")', lambda m: m.group(1) + str(target) + m.group(2), bseg, 1)
        x = x.replace(bseg, nb, 1)
        band = dict(band, seg=nb)                 # 아래 '내리기' 에서 띠 도형을 빼려면 바뀐 모양으로 찾는다
        out.append('띠 도형 "%s" 을 띠로 — 제목 자리 표시자를 그 위치로%s · 띠 %.2f" → %.2f" (도형과 함께)' % (
            band['name'], '(물려받던 위치 → 적어 넣음)' if mat else '', band['geo'][3] / EMU_IN, target / EMU_IN))
    elif seg != i['seg']:
        out.append(('물려받던 제목 — 적어 넣음 · ' if mat else '') + '띠 %.2f" → %.2f" · 위/아래 여백 %.2f"' % (i['h'] / EMU_IN, target / EMU_IN, ins / EMU_IN))
    band_bottom = i['y'] + target
    tstart = i['start']

    def shapes(xml):
        res = []
        tree = re.search(r'<p:spTree>(.*)</p:spTree>', xml, re.S)
        off0 = tree.start(1)
        body = tree.group(1)
        k = 0
        while True:
            m = re.search(r'<p:(sp|pic|cxnSp|graphicFrame|grpSp)>', body[k:])
            if not m:
                break
            tag = m.group(1); a = k + m.start()
            depth, j = 0, a
            pat = re.compile(r'<p:%s>|</p:%s>' % (tag, tag))
            for mm in pat.finditer(body, a):
                depth += 1 if mm.group(0)[1] != '/' else -1
                if depth == 0:
                    j = mm.end(); break
            segx = body[a:j]
            g = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"\s*/>\s*<a:ext cx="(\d+)" cy="(\d+)"', segx)
            nm = re.search(r'<p:cNvPr\b[^>]*\bname="([^"]*)"', segx)
            inh = None
            if not g and '<p:ph' in segx and not re.search(r'<p:ph\b[^>]*type="(?:title|ctrTitle)"', segx):
                inh = _ph_geo(deck, slide_no, segx)      # v16.33 (발표 K15-3): 위치를 물려받는 본문 자리 표시자
            if band and band['seg'] == segx:
                k = j; continue
            res.append({'tag': tag, 'start': off0 + a, 'end': off0 + j, 'seg': segx, 'name': html.unescape(nm.group(1)) if nm else '',
                        'geo': tuple(int(v) for v in g.groups()) if g else inh, 'inh': bool(inh),
                        'title': bool(re.search(r'<p:ph\b[^>]*type="(?:title|ctrTitle)"', segx)),
                        'foot': bool(re.search(r'<p:ph\b[^>]*type="(?:dt|ftr|sldNum)"', segx))})
            k = j
        return res
    # ② 옛 제목 밑줄
    lines_in_band = [sh for sh in shapes(x) if not sh['title'] and sh['geo'] and sh['geo'][3] <= 0.2 * EMU_IN and sh['geo'][2] >= 0.4 * W
                     and sh['geo'][1] + sh['geo'][3] <= band_bottom + 0.1 * EMU_IN
                     and (sh['tag'] == 'cxnSp' or re.search(r'prst="line"', sh['seg']))]
    if lines_in_band:
        if not drop_rule:
            out.append('[참고] 띠 안 가로선 %d개("%s") — 지우려면 --drop-title-rule' % (len(lines_in_band), lines_in_band[0]['name']))
        elif len(lines_in_band) > 1:
            out.append('[참고] 띠 안 가로선이 %d개 — 어느 것이 옛 제목 밑줄인지 애매해 지우지 않음' % len(lines_in_band))
        else:
            sh = lines_in_band[0]
            x = x[:sh['start']] + x[sh['end']:]
            out.append('옛 제목 밑줄 "%s"(y %.2f") 지움' % (sh['name'], sh['geo'][1] / EMU_IN))
    # ③ 본문 내리기
    limit = band_bottom + int(gap_in * EMU_IN)
    offenders = [sh for sh in shapes(x) if not sh['title'] and not sh['foot'] and sh['geo'] and sh['geo'][1] < limit]
    if offenders and not push:
        out.append('[참고] 띠 아래 간격보다 위에 있는 상자 %d개("%s" 등) — 내리려면 --push-content' % (len(offenders), offenders[0]['name']))
    elif offenders:
        shift = limit - min(sh['geo'][1] for sh in offenders)
        for sh in sorted(offenders, key=lambda s_: -s_['start']):
            gx, gy, gw, gh = sh['geo']
            ny, ncy, nseg = gy + shift, gh, sh['seg']
            note = ''
            if ny + gh > H:
                if sh['tag'] == 'sp' and '<p:txBody>' in nseg:
                    f = max(0.0, (H - ny) / float(gh))
                    szs = [int(v) for v in re.findall(r'<a:(?:rPr|endParaRPr)\b[^>]*\bsz="(\d+)"', nseg)] or [1800]
                    if max(szs) * f < min_pt * 100:
                        out.append('[!] "%s" — 내리면 아래로 %.2f" 넘치는데 %dpt 밑으로 줄여야 해 글자는 그대로(상자만 내림)' % (sh['name'], (ny + gh - H) / EMU_IN, min_pt))
                    else:
                        nseg = re.sub(r'(<a:(?:rPr|endParaRPr)\b[^>]*?\bsz=")(\d+)"', lambda mm: '%s%d"' % (mm.group(1), int(int(mm.group(2)) * f)), nseg)
                        nseg = re.sub(r'<a:(rPr|endParaRPr)\b((?:(?!\bsz=)[^>])*?)(/?)>', lambda mm: '<a:%s%s sz="%d"%s>' % (mm.group(1), mm.group(2), int(1800 * f), mm.group(3)), nseg)
                        ncy = H - ny
                        note = ' · 아래 넘침만큼 글자 %d%% 로(%s)' % (int(f * 100), '·'.join('%.1fpt' % (v * f / 100.0) for v in sorted(set(szs))))
                else:
                    note = ' · [!] 그림·도형이 아래로 %.2f" 넘침(크기 그대로)' % ((ny + gh - H) / EMU_IN)
            if sh.get('inh'):   # 물려받던 위치 — 적어 넣는다
                xf = '<a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>' % (gx, gy, gw, gh)
                nseg = re.sub(r'<p:spPr\s*/>', '<p:spPr>%s</p:spPr>' % xf, nseg, 1) if re.search(r'<p:spPr\s*/>', nseg) else \
                    re.sub(r'(<p:spPr\b[^>]*>)', lambda mm: mm.group(1) + xf, nseg, 1)
                note += ' · 물려받던 위치 → 적어 넣음'
            nseg = re.sub(r'(<a:off x="-?\d+" y=")-?\d+("\s*/>\s*<a:ext cx="\d+" cy=")\d+(")',
                          lambda mm: '%s%d%s%d%s' % (mm.group(1), ny, mm.group(2), ncy, mm.group(3)), nseg, 1)
            x = x[:sh['start']] + nseg + x[sh['end']:]
            out.append('"%s" 내림 %.2f"%s' % (sh['name'], shift / EMU_IN, note))
    if not dry_run:
        open(deck._slide(slide_no), 'w', encoding='utf8').write(x)
    return out


def _shapes_below_title(deck, slide_no, title_start, title_end):
    """제목 말고 내용 도형들의 (이름, 위쪽 y). 날짜·바닥글·번호 placeholder 와 슬라이드 전체 배경 그림은 뺀다."""
    x = open(deck._slide(slide_no), encoding='utf8').read()
    W, H = deck.slide_size(); out = []
    for mm in re.finditer(r'<p:(sp|pic|graphicFrame|grpSp|cxnSp)>.*?</p:\1>', x, re.S):
        if title_start <= mm.start() < title_end:
            continue
        seg = mm.group(0)
        if re.search(r'<p:ph\b[^>]*type="(?:dt|ftr|sldNum)"', seg):
            continue
        g = _GEO.search(seg)
        if not g:
            continue
        gx, gy, gw, gh = (int(v) for v in g.groups())
        if gw >= 0.9 * W and gh >= 0.9 * H:
            continue
        name = re.search(r'name="([^"]*)"', seg)
        out.append((name.group(1) if name else '', gy, gy + gh))
    return out


def check_title_template(deck, prof=None, screens=None, stream=sys.stdout, tol=0.05):
    """두 가지를 본다.
    (1) 모든 화면(또는 screens): 제목 글이 **자기 상자(띠)를 넘치는지** — 실제 적용되는 글자 크기(직접 지정 또는 레이아웃·마스터
        상속)와 안쪽 여백으로 계산. 규격 없이도 된다. 띠가 제목 상자의 채움이면 이것이 '띠 넘침' 이다.
    (2) screens 를 주고 prof 가 있으면: 그 화면 제목이 규격(글자 크기·글꼴·띠 색·위치·높이)과 다른 점. 다른 사람이 만든 화면까지
        규격으로 재지 않도록 **대상 화면만** 본다(원본 존중, §0-A-1).
    screens 는 화면 번호. 반환 {slide_no: [문제...]}."""
    out = {}
    t = int(tol * EMU_IN)
    order = [s for s, _, _ in deck.order() if s]
    targets = [order[k - 1] for k in screens] if screens else order
    for sn in targets:
        i = _title_info(deck, sn)
        if not i:
            continue
        iss = []
        need = _title_need(i)
        # 띠(제목 상자의 채움)가 있을 때만 넘침이 화면에 보인다 — 띠 없는 제목까지 잡으면 실물 덱에서 오탐이 났다
        banded = bool(i['fill']) and '<a:noFill' not in (i['fill'] or '')
        if banded and need > i['h'] + t and i['autofit'] != 'norm':
            iss.append('[!] 제목이 띠를 넘친다 — 필요 %.2f" / 띠 %.2f" (%dpt%s)'
                       % (need / EMU_IN, i['h'] / EMU_IN, i['eff_sz'] // 100, '' if i['sz'] else ' 상속'))
        if screens and prof:
            if i['kind'] == 'box':
                iss.append('[!] 제목이 placeholder 가 아니라 글상자 — 템플릿 제목 서식을 안 받는다')
            if prof['sz'] and i['eff_sz'] != prof['sz']:
                iss.append('글자 크기 %dpt ≠ 규격 %dpt' % (i['eff_sz'] // 100, prof['sz'] // 100))
            if i['latin'] and i['latin'] != prof['latin']:
                iss.append('글꼴 %s ≠ 규격 %s' % (i['latin'], prof['latin'] or '(템플릿 상속)'))
            if (i['fill'] or '') != (prof['fill'] or ''):
                iss.append('띠 색(채움)이 규격과 다름')
            if abs(i['x'] - prof['x']) > t or abs(i['y'] - prof['y']) > t or abs(i['w'] - prof['w']) > t:
                iss.append('위치·폭이 규격과 다름')
            lines = _title_lines(dict(i, lIns=prof['ins'][0], rIns=prof['ins'][1]), prof['est_sz'], prof['w'])
            want = prof['h_by_lines'].get(lines)
            if want is None:
                iss.append('[!] 규격 크기로 %d줄 — 규격에 없는 줄 수. 제목을 줄여야 띠 안에 든다' % lines)
            elif abs(i['h'] - want) > t:
                iss.append('높이 %.2f" ≠ 규격 %d줄 높이 %.2f"' % (i['h'] / EMU_IN, lines, want / EMU_IN))
        if iss:
            out[sn] = iss
    for sn, iss in out.items():
        print('  %s: %s' % (deck.label(sn), ' / '.join(iss)), file=stream)
    if not out:
        print('  제목 문제 없음', file=stream)
    return out


def conform_title(deck, slide_no, prof, adopt_box=False, dry_run=False):
    """제목을 규격으로 맞춘다: 위치·폭, 줄 수에 맞는 높이, 띠 색(채움), 안쪽 여백·자동 맞춤(bodyPr), 글자 크기·글꼴.
    글자·색·굵게(run 색)는 안 건드린다. **띠를 키우면 아래 본문·그림과 겹치는 경우는 바꾸지 않고 알린다** — 도구가 본문을
    옮기지 않는다(재배치 시도가 사고를 냈다, §0-C). 글상자 제목은 adopt_box=True 일 때만 placeholder 로.
    반환: 바꾼 것(또는 dry_run 이면 바꿀 것) 목록. '[!]' 로 시작하면 바꾸지 않았다는 뜻."""
    i = _title_info(deck, slide_no)
    if not i or not prof:
        return []
    if i['kind'] == 'box' and not adopt_box:
        # 글상자 제목: placeholder 로 바꾸지 않고 자리도 그대로, 띠 색과 '띠 안에 들어가는 글자 크기' 만 맞춘다
        return _fit_title_in_box(deck, slide_no, i, prof, [], dry_run)
    lines = _title_lines(dict(i, lIns=prof['ins'][0], rIns=prof['ins'][1]), prof['est_sz'], prof['w'])
    want_h = prof['h_by_lines'].get(lines)
    need_h = _title_need_h(prof['ins'][2], prof['ins'][3], lines, prof['est_sz'], i.get('lnspc', 1.0))
    raised = None
    if want_h is None and lines <= 2:
        want_h, raised = need_h, '규격에 %d줄 높이가 없어 필요 높이 %.2f\"' % (lines, need_h / EMU_IN)
    elif want_h is not None and want_h < 0.9 * need_h:
        # v16.28 (발표 K8): 규격 높이가 필요 높이보다 낮으면 필요 높이로 — Google Slides 는 spAutoFit 을 따르지 않아 글이 띠 밖으로 나온다
        raised = '규격 %.2f\" < 필요 %.2f\"(안쪽 여백 포함) — 필요 높이로' % (want_h / EMU_IN, need_h / EMU_IN)
        want_h = need_h
    if want_h is None:
        return ['[!] 규격 크기로 %d줄 — 제목 글을 줄여야 한다(도구가 줄이지 않는다)' % lines]
    band_bottom = prof['y'] + want_h
    hit = [(n, y0) for n, y0, y1 in _shapes_below_title(deck, slide_no, i['start'], i['end']) if y0 < band_bottom - int(0.02 * EMU_IN) and y1 > prof['y']]
    if hit:
        # 규격 띠가 본문과 겹치면: 띠(상자) 자리는 그대로 두고 **글자를 줄여 띠 안에 넣는다** (§0-A-2 "글자 수가 많으면 글자를
        # 줄이되 띠 밖으로 나가지 않는다"). 띠 색만 규격으로. 도구는 본문을 옮기지 않는다
        return _fit_title_in_box(deck, slide_no, i, prof, hit, dry_run)
    seg = i['seg']; ch = []
    if i['kind'] == 'box':
        seg = re.sub(r'<p:nvPr\s*/>', '<p:nvPr><p:ph type="title"/></p:nvPr>', seg, 1)
        seg = seg.replace('<p:cNvSpPr txBox="1"/>', '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>', 1)
        ch.append('글상자 → title placeholder')
    # spPr: 위치·크기 + 채움
    xf = '<a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>' % (prof['x'], prof['y'], prof['w'], want_h)
    sppr = re.search(r'<p:spPr\b[^>]*/>|<p:spPr\b[^>]*>.*?</p:spPr>', seg, re.S)
    inner = '' if sppr.group(0).endswith('/>') else re.search(r'<p:spPr\b[^>]*>(.*)</p:spPr>', sppr.group(0), re.S).group(1)
    inner = re.sub(r'<a:xfrm\b[^>]*>.*?</a:xfrm>', '', inner, flags=re.S)
    inner = re.sub(r'<a:(solidFill|gradFill|blipFill|pattFill)>.*?</a:\1>|<a:noFill/>', '', inner, flags=re.S)
    geom = re.search(r'<a:(?:prstGeom|custGeom)\b.*?</a:(?:prstGeom|custGeom)>', inner, re.S)
    rest = inner.replace(geom.group(0), '') if geom else inner
    new_sppr = '<p:spPr>' + xf + (geom.group(0) if geom else '') + (prof['fill'] or '') + rest + '</p:spPr>'
    seg = seg[:sppr.start()] + new_sppr + seg[sppr.end():]
    ch.append('위치·크기 → 규격 %d줄 (%.2f")' % (lines, want_h / EMU_IN) + ((' — ' + raised) if raised else ''))
    if (i['fill'] or '') != (prof['fill'] or ''):
        ch.append('띠 색 → 규격')
    # bodyPr: 여백·정렬·자동 맞춤을 규격 것으로
    if prof['bodyPr']:
        seg2 = re.sub(r'<a:bodyPr\b[^>]*/>|<a:bodyPr\b[^>]*>.*?</a:bodyPr>', lambda _: prof['bodyPr'] if prof['bodyPr'].endswith('/>') else prof['bodyPr'] + _autofit_xml(prof['autofit']) + '</a:bodyPr>', seg, 1, flags=re.S)
        if seg2 != seg:
            ch.append('안쪽 여백·자동 맞춤 → 규격')
        seg = seg2
    # 글자 크기·글꼴
    def rpr(m):
        attrs = re.sub(r'\s+sz="\d+"', '', m.group(2))
        if prof['sz'] is not None:
            attrs += ' sz="%d"' % prof['sz']
        return '<a:%s%s%s>' % (m.group(1), attrs, m.group(3))
    seg2 = re.sub(r'<a:(rPr|endParaRPr)\b([^>]*?)(/?)>', rpr, seg)
    if seg2 != seg:
        ch.append('글자 크기 → %s' % ('%dpt' % (prof['sz'] // 100) if prof['sz'] else '템플릿 상속'))
    seg = seg2
    seg2 = re.sub(r'(<a:(?:latin|ea) typeface=")[^"]*(")', r'\g<1>%s\2' % prof['latin'], seg) if prof['latin'] else \
        re.sub(r'<a:(?:latin|ea|cs) typeface="[^"]*"[^>]*/>', '', seg)
    if seg2 != seg:
        ch.append('글꼴 → %s' % (prof['latin'] or '템플릿 상속'))
    seg = seg2
    if not dry_run and seg != i['seg']:
        p = deck._slide(slide_no); x = open(p, encoding='utf8').read()
        open(p, 'w', encoding='utf8').write(x[:i['start']] + seg + x[i['end']:])
    return ch


MIN_FIT_TITLE_PT = MIN_TITLE_PT   # v16.27 (발표 근골격): 띠 안에 넣으려 줄일 때의 하한 = lint 제목 최소 24pt(전에는 16 — 23pt 로 줄여 lint 와 부딪쳤다). 더 줄여야 하면 [!]
FIT_WIDTH_MARGIN = 0.9  # 글자폭 추정 여유: 실물 렌더(굵은 한글 글꼴·대체 글꼴)에서 추정보다 한 줄 더 꺾였다(2026-09-24)


def _fit_title_in_box(deck, slide_no, i, prof, hit, dry_run):
    avail = i['h'] - i['tIns'] - i['bIns']
    sz = min(prof['sz'] or i['eff_sz'], i['eff_sz'])
    fw = int(i['w'] - (1 - FIT_WIDTH_MARGIN) * (i['w'] - i['lIns'] - i['rIns']))
    while sz >= MIN_FIT_TITLE_PT * 100:
        need = _title_lines(i, sz, fw) * sz / 100.0 * LINE_FACTOR * i.get('lnspc', 1.0) * 12700
        if need <= avail:
            break
        sz -= 100
    where = ', '.join('"%s"(%.2f")' % (n, y0 / EMU_IN) for n, y0 in hit[:2])
    why = ('규격 띠는 %s 와 겹쳐' % where) if hit else '글상자 제목이라'
    if sz < MIN_FIT_TITLE_PT * 100:
        return ['[!] %s 띠 자리를 그대로 두는데, 띠 안에 넣으려면 %dpt 밑으로 줄여야 한다 — 제목 글을 줄일 것' % (why, MIN_FIT_TITLE_PT)]
    seg = i['seg']
    ch = ['[참고] %s 띠 자리는 그대로 두고 글자 %dpt%s' % (why, sz // 100, '' if sz == i['eff_sz'] else ' 로 줄였다')]
    seg = re.sub(r'<a:(rPr|endParaRPr)\b([^>]*?)(/?)>', lambda m: '<a:%s%s sz="%d"%s>' % (m.group(1), re.sub(r'\s+sz="\d+"', '', m.group(2)), sz, m.group(3)), seg)
    if prof['fill'] and (i['fill'] or '') != prof['fill']:
        sppr = re.search(r'<p:spPr\b[^>]*/>|<p:spPr\b[^>]*>.*?</p:spPr>', seg, re.S)
        if sppr:
            body = '' if sppr.group(0).endswith('/>') else re.search(r'<p:spPr\b[^>]*>(.*)</p:spPr>', sppr.group(0), re.S).group(1)
            body = re.sub(r'<a:(solidFill|gradFill|blipFill|pattFill)>.*?</a:\1>|<a:noFill/>', '', body, flags=re.S)
            geom = re.search(r'<a:(?:prstGeom|custGeom)\b.*?</a:(?:prstGeom|custGeom)>', body, re.S)
            if geom:
                body = body.replace(geom.group(0), geom.group(0) + prof['fill'], 1)
            else:
                xf = re.search(r'<a:xfrm\b.*?</a:xfrm>', body, re.S)
                body = (body.replace(xf.group(0), xf.group(0) + prof['fill'], 1) if xf else prof['fill'] + body)
            seg = seg[:sppr.start()] + '<p:spPr>' + body + '</p:spPr>' + seg[sppr.end():]
            ch.append('띠 색 → 규격')
    if i['kind'] == 'box':
        ch.append('(글상자 제목은 그대로 두었다)')
    if not dry_run and seg != i['seg']:
        p = deck._slide(slide_no); x = open(p, encoding='utf8').read()
        open(p, 'w', encoding='utf8').write(x[:i['start']] + seg + x[i['end']:])
    return ch


def _autofit_xml(kind):
    return {'norm': '<a:normAutofit/>', 'sp': '<a:spAutoFit/>', 'no': '<a:noAutofit/>'}.get(kind or '', '')


def _layout_identity(deck, layout_file):
    """(레이아웃 이름, 테마 이름, 제목·본문 latin 글꼴) — 두 덱의 같은 이름 레이아웃이 같은 모양인지 가늠한다."""
    lp = os.path.join(deck.dir, 'ppt/slideLayouts', layout_file)
    if not os.path.exists(lp):
        return None
    lx = open(lp, encoding='utf8').read()
    name = (re.search(r'<p:cSld name="([^"]*)"', lx) or [None, ''])[1]
    theme = fonts = ''
    lr = os.path.join(deck.dir, 'ppt/slideLayouts/_rels', layout_file + '.rels')
    if os.path.exists(lr):
        m = re.search(r'Target="\.\./slideMasters/([^"]+)"', open(lr, encoding='utf8').read())
        if m:
            mr = os.path.join(deck.dir, 'ppt/slideMasters/_rels', m.group(1) + '.rels')
            if os.path.exists(mr):
                t = re.search(r'Target="\.\./theme/([^"]+)"', open(mr, encoding='utf8').read())
                tp = os.path.join(deck.dir, 'ppt/theme', t.group(1)) if t else None
                if tp and os.path.exists(tp):
                    tx = open(tp, encoding='utf8').read()
                    theme = (re.search(r'<a:theme [^>]*name="([^"]*)"', tx) or [None, ''])[1]
                    fonts = '/'.join(re.findall(r'<a:(?:major|minor)Font><a:latin typeface="([^"]*)"', tx))
    return (name, theme, fonts)


def _layout_default_sizes(deck, layout_file):
    """(제목 기본 크기, 본문 1단계 기본 크기) — 레이아웃 파일 기준(그 레이아웃을 쓰는 가상의 슬라이드)."""
    class _L:
        dir = deck.dir
        def layout_of(self, _):
            return layout_file
        def slide_size(self):
            return deck.slide_size()
    L = _L()
    return (_title_default_sz(L, None), _body_level_sizes(L, None, 'idx="1"').get(0))


def _layout_name(deck, layout_file):
    lp = os.path.join(deck.dir, 'ppt/slideLayouts', layout_file)
    return (re.search(r'<p:cSld name="([^"]*)"', open(lp, encoding='utf8').read()) or [None, ''])[1] if os.path.exists(lp) else ''


def _layouts_of_master(deck, master_path):
    if not master_path:
        return []
    mr = os.path.join(os.path.dirname(master_path), '_rels', os.path.basename(master_path) + '.rels')
    return re.findall(r'slideLayouts/(slideLayout\d+\.xml)', open(mr, encoding='utf8').read()) if os.path.exists(mr) else []


def _pick_layout(deck, src, src_layout, prof, after, layout=None):
    """목적지 레이아웃 고르기:
    0. layout 을 주면 그것
    1. (v16.14, 발표 S1) 목적지에 원천 레이아웃과 **이름·테마·글꼴이 모두 같은** 레이아웃이 있으면 그것(같은 파일 이름이면 우선) —
       같은 덱 안에서 복제하거나 같은 템플릿 덱끼리면 원천 모양이 그대로 유지된다. 전에는 after 이웃의 마스터로 붙어 교육목표 19장이
       네 테마로 갈렸다
    2. 기준 마스터(규격 레이아웃의 마스터 → after 슬라이드의 마스터) 안에서 표시 이름이 같은 것 → 기준 레이아웃 그 자체
    3. 같은 파일 이름 → slideLayout2"""
    if layout:
        if not os.path.exists(os.path.join(deck.dir, 'ppt/slideLayouts', layout)):
            raise ValueError('레이아웃 %s 없음' % layout)
        return layout
    sid = _layout_identity(src, src_layout)
    if sid and not prof:
        same = [c for c in sorted(os.listdir(os.path.join(deck.dir, 'ppt/slideLayouts'))) if c.endswith('.xml') and _layout_identity(deck, c) == sid]
        if same:
            return src_layout if src_layout in same else same[0]
    name = _layout_name(src, src_layout)
    ref_layout = (prof or {}).get('layout') or (deck.layout_of(after) if after else None)
    if ref_layout:
        lr = os.path.join(deck.dir, 'ppt/slideLayouts/_rels', ref_layout + '.rels')
        m = re.search(r'slideMasters/(slideMaster\d+\.xml)', open(lr, encoding='utf8').read()) if os.path.exists(lr) else None
        cands = _layouts_of_master(deck, os.path.join(deck.dir, 'ppt/slideMasters', m.group(1))) if m else []
        for c in cands:
            if _layout_name(deck, c) == name:
                return c
        return ref_layout
    if os.path.exists(os.path.join(deck.dir, 'ppt/slideLayouts', src_layout)):
        return src_layout
    return 'slideLayout2.xml'


def _body_level_sizes(deck, slide_no, ph_attrs):
    """본문 placeholder 의 단계별 기본 글자 크기 {0: 2000, 1: 1800, …}: 레이아웃의 같은 placeholder lstStyle → 마스터 bodyStyle."""
    out = {}
    idx = re.search(r'idx="(\d+)"', ph_attrs)
    lp = os.path.join(deck.dir, 'ppt/slideLayouts', deck.layout_of(slide_no))
    if os.path.exists(lp) and idx:
        lx = open(lp, encoding='utf8').read()
        for m in re.finditer(r'<p:sp>(?:(?!</p:sp>).)*</p:sp>', lx, re.S):
            if re.search(r'<p:ph\b[^>]*idx="%s"' % idx.group(1), m.group(0)):
                for lv, sz in re.findall(r'<a:lvl(\d)pPr\b[^>]*>(?:(?!</a:lvl\d?pPr>).)*?<a:defRPr\b[^>]*\bsz="(\d+)"', m.group(0), re.S):
                    out.setdefault(int(lv) - 1, int(sz))
                break
    mp = _master_of(deck, slide_no)
    if mp and os.path.exists(mp):
        bs = re.search(r'<p:bodyStyle>(.*?)</p:bodyStyle>', open(mp, encoding='utf8').read(), re.S)
        if bs:
            for lv, sz in re.findall(r'<a:lvl(\d)pPr\b[^>]*>(?:(?!</a:lvl\d?pPr>).)*?<a:defRPr\b[^>]*\bsz="(\d+)"', bs.group(1), re.S):
                out.setdefault(int(lv) - 1, int(sz))
    return out


def _body_level_lnspc(deck, slide_no, ph_attrs):
    """본문 placeholder 의 단계별 줄 간격(spcPct, 100000=100%): 레이아웃 같은 placeholder lstStyle → 마스터 bodyStyle."""
    out = {}
    idx = re.search(r'idx="(\d+)"', ph_attrs)
    srcs = []
    lp = os.path.join(deck.dir, 'ppt/slideLayouts', deck.layout_of(slide_no))
    if os.path.exists(lp) and idx:
        for m in re.finditer(r'<p:sp>(?:(?!</p:sp>).)*</p:sp>', open(lp, encoding='utf8').read(), re.S):
            if re.search(r'<p:ph\b[^>]*idx="%s"' % idx.group(1), m.group(0)):
                srcs.append(m.group(0)); break
    mp = _master_of(deck, slide_no)
    if mp and os.path.exists(mp):
        bs = re.search(r'<p:bodyStyle>(.*?)</p:bodyStyle>', open(mp, encoding='utf8').read(), re.S)
        if bs:
            srcs.append(bs.group(1))
    for s in srcs:
        for lv, v in re.findall(r'<a:lvl(\d)pPr\b[^>]*>(?:(?!</a:lvl\d?pPr>).)*?<a:lnSpc><a:spcPct val="(\d+)"', s, re.S):
            out.setdefault(int(lv) - 1, int(v))
    return out


def _body_level_spc(deck, slide_no, ph_attrs, tag):
    """본문 placeholder 의 단계별 문단 앞·뒤 간격 {단계: ('pts', 값) | ('pct', 값)}: 레이아웃 lstStyle → 마스터 bodyStyle."""
    out = {}
    idx = re.search(r'idx="(\d+)"', ph_attrs)
    srcs = []
    lp = os.path.join(deck.dir, 'ppt/slideLayouts', deck.layout_of(slide_no))
    if os.path.exists(lp) and idx:
        for m in re.finditer(r'<p:sp>(?:(?!</p:sp>).)*</p:sp>', open(lp, encoding='utf8').read(), re.S):
            if re.search(r'<p:ph\b[^>]*idx="%s"' % idx.group(1), m.group(0)):
                srcs.append(m.group(0)); break
    mp = _master_of(deck, slide_no)
    if mp and os.path.exists(mp):
        bs = re.search(r'<p:bodyStyle>(.*?)</p:bodyStyle>', open(mp, encoding='utf8').read(), re.S)
        if bs:
            srcs.append(bs.group(1))
    for s in srcs:
        for lv, body in re.findall(r'<a:lvl(\d)pPr\b[^>]*>(.*?)</a:lvl\1pPr>', s, re.S):
            m = re.search(r'<a:%s><a:spc(Pts|Pct) val="(\d+)"' % tag, body)
            if m:
                out.setdefault(int(lv) - 1, ('pts' if m.group(1) == 'Pts' else 'pct', int(m.group(2))))
    return out


def _materialize_ph_geometry(src, src_slide_no, sx):
    """원천에서 상속하던 값을 슬라이드에 적어 넣어, 목적지 레이아웃·마스터로 바뀌어도 모양이 그대로이게 한다.
    - xfrm 이 없는 placeholder: 원천 레이아웃·마스터의 위치·크기
    - 제목 placeholder: 안쪽 여백(bodyPr l/t/r/bIns)과 글자 크기(sz). 실물 전평 덱에서 새 연도 제목(0.66" 띠)이 받는 덱 마스터의
      0.39" 여백·33pt 를 상속해 띠를 넘친 것이 '옮기면 항상 제목이 넘친다' 의 실제 원인이었다(2026-09-24 재현)."""
    geo = _layout_ph_geometry(src, src_slide_no)
    inh = _inherited_title(src, src_slide_no)
    bpi = re.search(r'<a:bodyPr\b([^>]*)', inh); bpia = bpi.group(1) if bpi else ''
    src_sz = _title_default_sz(src, src_slide_no)
    def title_fix(seg):
        bp = re.search(r'<a:bodyPr\b([^>]*?)(/?)>', seg)
        if bp:
            attrs = bp.group(1)
            for k, d in (('lIns', 91440), ('tIns', 45720), ('rIns', 91440), ('bIns', 45720)):
                if not re.search(r'\b%s="' % k, attrs):
                    mm = re.search(r'\b%s="(-?\d+)"' % k, bpia)
                    attrs += ' %s="%s"' % (k, mm.group(1) if mm else d)
            seg = seg[:bp.start()] + '<a:bodyPr%s%s>' % (attrs, bp.group(2)) + seg[bp.end():]
        seg = re.sub(r'<a:(rPr|endParaRPr)\b((?:(?!\bsz=)[^>])*?)(/?)>', lambda mm: '<a:%s%s sz="%d"%s>' % (mm.group(1), mm.group(2), src_sz, mm.group(3)), seg)
        return seg
    def body_fix(seg, ph_attrs):
        # 본문 placeholder: 원천 레이아웃·마스터에서 물려받던 단계별 글자 크기를 run 에 적어 넣는다 — 받는 덱 마스터의 큰 본문
        # 글자를 입어 25-11 정답 보기 ㉣ 가 그림 뒤로 가려진 사고(영상의학 회신 09-24) 이후
        sizes = _body_level_sizes(src, src_slide_no, ph_attrs)
        if not sizes:
            return seg
        def para(pm):
            p = pm.group(0)
            lv = re.search(r'<a:pPr\b[^>]*\blvl="(\d+)"', p)
            sz = sizes.get(int(lv.group(1)) if lv else 0) or sizes.get(0)
            if not sz:
                return p
            p = re.sub(r'<a:(rPr|endParaRPr)\b((?:(?!\bsz=)[^>])*?)(/?)>', lambda mm: '<a:%s%s sz="%d"%s>' % (mm.group(1), mm.group(2), sz, mm.group(3)), p)
            return re.sub(r'<a:r><a:t\b', '<a:r><a:rPr lang="ko-KR" sz="%d"/><a:t' % sz, p)
        return re.sub(r'<a:p>.*?</a:p>', para, seg, flags=re.S)
    def fix(m):
        seg = m.group(0)
        ph = re.search(r'<p:ph\b([^>]*)/?>', seg)
        if ph and re.search(r'type="(?:title|ctrTitle)"', ph.group(1)):
            seg = title_fix(seg)
        elif ph and not re.search(r'type="(?:dt|ftr|sldNum|pic|chart|tbl|media|clipArt|sldImg)"', ph.group(1)):
            seg = body_fix(seg, ph.group(1))
        if not ph or _GEO.search(seg):
            return seg
        typ = re.search(r'type="(\w+)"', ph.group(1)); idx = re.search(r'idx="(\d+)"', ph.group(1))
        g = (geo.get(('idx', idx.group(1))) if idx else None) or (geo.get(('type', typ.group(1))) if typ else None) \
            or (geo.get(('type', 'body')) if idx and not typ else None)
        if not g:
            return seg
        xf = '<a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>' % g
        if '<p:spPr/>' in seg:
            return seg.replace('<p:spPr/>', '<p:spPr>%s</p:spPr>' % xf, 1)
        return re.sub(r'(<p:spPr\b[^>]*>)', r'\1' + xf, seg, 1)
    return re.sub(r'<p:sp>(?:(?!</p:sp>).)*</p:sp>', fix, sx, flags=re.S)


def _strip_pictures_xml(x, labels=False, margin=0.15):
    """<p:pic> 을 지운 XML 과 그 그림들의 rId 집합. labels=True 면 그림 bbox(여유 margin 인치) 안에 완전히 든
    non-placeholder 도형·connector(라벨·화살표)도 지운다 (v16.7.1)."""
    pics = re.findall(r'<p:pic>.*?</p:pic>', x, re.S)
    rids = set(r for pm in pics for r in re.findall(r'r:embed="(rId\d+)"', pm))
    if labels and pics:
        mg = int(margin * 914400); boxes = []
        for pm in pics:
            g = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>\s*<a:ext cx="(\d+)" cy="(\d+)"', pm)
            if g:
                bx, by, bw, bh = (int(v) for v in g.groups())
                boxes.append((bx - mg, by - mg, bx + bw + mg, by + bh + mg))
        def _inside(seg):
            if '<p:ph' in seg:
                return False
            g = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>\s*<a:ext cx="(\d+)" cy="(\d+)"', seg)
            if not g:
                return False
            sx_, sy_, sw, sh = (int(v) for v in g.groups())
            return any(sx_ >= L and sy_ >= T and sx_ + sw <= R and sy_ + sh <= B for L, T, R, B in boxes)
        x = re.sub(r'<p:(sp|cxnSp)>.*?</p:\1>', lambda m: '' if _inside(m.group(0)) else m.group(0), x, flags=re.S)
    return re.sub(r'<p:pic>.*?</p:pic>', '', x, flags=re.S), rids


def _group_transforms(xml):
    """v16.6: <p:grpSp> 블록마다 (start, end, 변환) 를 돌려준다. 변환은 자식 좌표 → 슬라이드 좌표.
    중첩 그룹은 바깥 변환을 합성한다. 그룹 안 도형은 chOff/chExt 좌표계로 저장되므로 그대로 쓰면 자리가 어긋난다
    (전평 대화창 사고: 자식 좌표를 옮겨 영상이 엉뚱한 자리로). 반환 [(start, end, (ox, oy, sx, sy, chx, chy))]."""
    out, stack = [], []
    for m in re.finditer(r'<p:grpSp>|</p:grpSp>', xml):
        if m.group(0) == '<p:grpSp>':
            stack.append(m.start())
        elif stack:
            start = stack.pop()
            blk = xml[start:m.end()]
            g = re.search(r'<p:grpSpPr>.*?<a:off x="(-?\d+)" y="(-?\d+)"/>\s*<a:ext cx="(\d+)" cy="(\d+)"/>'
                          r'\s*<a:chOff x="(-?\d+)" y="(-?\d+)"/>\s*<a:chExt cx="(\d+)" cy="(\d+)"/>', blk, re.S)
            if g:
                ox, oy, ex, ey, cx, cy, cw, ch = (int(v) for v in g.groups())
                sx = ex / cw if cw else 1.0; sy = ey / ch if ch else 1.0
                out.append((start, m.end(), (ox, oy, sx, sy, cx, cy)))
    out.sort(key=lambda t: (t[0], -t[1]))
    return out


def _apply_groups(groups, pos, box):
    """box (x, y, w, h) 가 groups 중 어느 그룹 안이면(가장 안쪽부터 바깥으로) 슬라이드 좌표로 바꾼다."""
    x, y, w, h = box
    inner = sorted([g for g in groups if g[0] < pos < g[1]], key=lambda g: -g[0])   # 안쪽 → 바깥
    for _, _, (ox, oy, sx, sy, cx, cy) in inner:
        x = int(ox + (x - cx) * sx); y = int(oy + (y - cy) * sy); w = int(w * sx); h = int(h * sy)
    return (x, y, w, h)


def _text_shapes(deck, slide_no):
    """텍스트가 있는 도형을 (이름, x, y, w, h, 문단리스트) 로 돌려준다.

    슬라이드에 xfrm 이 없는 placeholder 는 레이아웃 값을 가져다 쓴다.
    """
    x = open(deck._slide(slide_no), encoding='utf8').read()
    lay_geo = _layout_ph_geometry(deck, slide_no)
    groups = _group_transforms(x)
    out = []
    for m in re.finditer(r'<p:sp>.*?</p:sp>', x, re.S):
        s = m.group(0)
        off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>'
                        r'<a:ext cx="(\d+)" cy="(\d+)"', s)
        if off:
            box = _apply_groups(groups, m.start(), tuple(int(v) for v in off.groups()))
        else:
            ph = re.search(r'<p:ph([^/]*)/>', s)
            if not ph:
                continue
            idx = re.search(r'idx="(\d+)"', ph.group(1))
            typ = re.search(r'type="(\w+)"', ph.group(1))
            keys = []
            if idx:
                keys.append(('idx', idx.group(1)))
            if typ:
                keys.append(('type', typ.group(1)))
            if idx and not typ:
                keys.append(('type', 'body'))   # idx만 있는 본문 placeholder
            box = next((lay_geo[k] for k in keys if k in lay_geo), None)
            if not box:
                continue
        name = re.search(r'name="([^"]*)"', s)
        paras = []
        # v16.12 (발표 U2): 줄 간격(lnSpc)·문단 앞 간격(spcBef)·상속 글자 크기·빈 문단을 센다 — 교육목표 슬라이드에서 계산은 상자 안인데
        # 실제 글꼴 렌더로는 마지막 줄이 잘렸다. 상속값은 레이아웃·마스터의 단계별 값
        php = re.search(r'<p:ph\b([^>]*)/?>', s)
        inh_sz = _body_level_sizes(deck, slide_no, php.group(1)) if php and 'type="title"' not in php.group(0) else {}
        inh_ln = _body_level_lnspc(deck, slide_no, php.group(1)) if php and 'type="title"' not in php.group(0) else {}
        inh_bef = _body_level_spc(deck, slide_no, php.group(1), 'spcBef') if php and 'type="title"' not in php.group(0) else {}
        inh_aft = _body_level_spc(deck, slide_no, php.group(1), 'spcAft') if php and 'type="title"' not in php.group(0) else {}
        allp = list(re.finditer(r'<a:p>(.*?)</a:p>', s, re.S))
        last_text = max((k for k, pm in enumerate(allp) if _AT.search(pm.group(1)) and ''.join(_AT.findall(pm.group(1))).strip()), default=-1)
        for k, pm in enumerate(allp):
            body = pm.group(1)
            txt = html.unescape(''.join(_AT.findall(body)))
            if not txt.strip() and k > last_text:
                continue                      # 끝의 빈 문단은 넘침에 영향이 적다(렌더러마다 다름) — 세지 않는다
            lv = int((re.search(r'<a:pPr\b[^>]*\blvl="(\d)"', body) or [0, 0])[1])
            szs = [int(v) for v in re.findall(r'<a:(?:rPr|endParaRPr)\b[^>]*\bsz="(\d+)"', body)]
            sz = (max(szs) if szs else inh_sz.get(lv) or inh_sz.get(0) or 1800) / 100.0
            ln = re.search(r'<a:lnSpc><a:spcPct val="(\d+)"', body)
            lpt = re.search(r'<a:lnSpc><a:spcPts val="(\d+)"', body)
            lnspc = int(ln.group(1)) / 100000.0 if ln else inh_ln.get(lv, inh_ln.get(0, 100000)) / 100000.0
            if lpt and not ln:      # v16.32 (발표 D2): pt 로 고정된 줄 간격 — 줄 높이 = 그 pt(글자 크기와 무관)
                lnspc = (int(lpt.group(1)) / 100.0) / (sz * LINE_FACTOR)
            def spc(tag, inh):
                m1 = re.search(r'<a:%s><a:spcPts val="(\d+)"/>' % tag, body)
                if m1:
                    return int(m1.group(1)) / 100.0
                m2 = re.search(r'<a:%s><a:spcPct val="(\d+)"/>' % tag, body)
                if m2:
                    return int(m2.group(1)) / 100000.0 * sz
                v = inh.get(lv, inh.get(0))
                return (v[1] / 100.0 if v[0] == 'pts' else v[1] / 100000.0 * sz) if v else 0.0
            runs = []
            for rm in re.finditer(r'<a:r>(.*?)</a:r>', body, re.S):
                rt = html.unescape(''.join(_AT.findall(rm.group(1))))
                if rt:
                    runs.append((rt, bool(re.search(r'<a:rPr\b[^>]*\bb="1"', rm.group(1)))))
            paras.append({'text': txt if txt.strip() else ' ', 'sz': sz, 'lnspc': lnspc, 'runs': runs,
                          'bef': spc('spcBef', inh_bef) if k else 0.0, 'aft': spc('spcAft', inh_aft)})
        if paras:
            bp = re.search(r'<a:bodyPr([^>]*)/?>', s)
            bpa = bp.group(1) if bp else ''
            anc = re.search(r'anchor="(\w+)"', bpa)
            fs = re.search(r'<a:normAutofit[^>]*fontScale="(\d+)"', s)
            def ins(k, default):
                m2 = re.search(r'%s="(-?\d+)"' % k, bpa)
                return int(m2.group(1)) if m2 else default
            out.append({'name': name.group(1) if name else '',
                        'x': box[0], 'y': box[1], 'w': box[2], 'h': box[3],
                        'paras': paras,
                        'fill': bool(re.search(r'<a:solidFill><a:srgbClr', s)),
                        # v16.5: 세로 정렬·줄바꿈·여백 (overflow 가 카드 경계·가로 넘침을 재는 데 쓴다)
                        'anchor': anc.group(1) if anc else 't',
                        'wrap': 'none' if re.search(r'wrap="none"', bpa) else 'square',
                        'lIns': ins('lIns', INSET_EMU), 'rIns': ins('rIns', INSET_EMU),
                        'tIns': ins('tIns', 45720), 'bIns': ins('bIns', 45720),
                        # v16.6: PowerPoint 자동 축소 비율(100000 = 100%). 100% 미만이면 글자를 줄여 넘침을 숨긴 것
                        'fontScale': int(fs.group(1)) / 1000.0 if fs else None,
                        # v16.10 (발표 W2): 두 단 상자(numCol) — 필요 높이를 단 수로 나눈다
                        'numCol': int((re.search(r'numCol="(\d+)"', bpa) or [0, 1])[1]),
                        'spcCol': int((re.search(r'spcCol="(\d+)"', bpa) or [0, 0])[1]),
                        'autofit': bool(re.search(r'<a:normAutofit', s)),
                        'in_group': any(g[0] < m.start() < g[1] for g in groups)})
    return out


def _fill_shapes(deck, slide_no):
    """배경 카드(채움이 있고 글자가 없는 도형). 그룹 안 카드는 슬라이드 좌표로 바꿔 준다(v16.6)."""
    x = open(deck._slide(slide_no), encoding='utf8').read()
    groups = _group_transforms(x)
    out = []
    for m in re.finditer(r'<p:sp>.*?</p:sp>', x, re.S):
        s = m.group(0)
        if not re.search(r'<a:solidFill><a:srgbClr', s):
            continue
        if re.search(r'<a:t>\S', s):
            continue
        off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>'
                        r'<a:ext cx="(\d+)" cy="(\d+)"', s)
        if off:
            name = re.search(r'name="([^"]*)"', s)
            bx, by, bw, bh = _apply_groups(groups, m.start(), tuple(int(v) for v in off.groups()))
            out.append({'name': name.group(1) if name else '', 'x': bx, 'y': by, 'w': bw, 'h': bh})
    return out


LINE_FACTOR = 1.22          # 줄간격 배수
INSET_EMU = 91440           # 기본 좌우 여백 (0.1 inch)


_FONT_CACHE = {}


def _parse_screens(spec, n):
    """'3,5-9' → {3,5,6,7,8,9}. v16.44 (코드 리뷰 ⑬): 1..n 밖이거나 숫자가 아니면 멈춘다 — 전에는 조용히 버렸고,
    따로 풀던 명령에서는 0 이 마지막 화면(order[-1])이 됐다."""
    out, bad = set(), []
    for part in str(spec).split(','):
        part = part.strip()
        try:
            if '-' in part:
                a, b = part.split('-', 1); out |= set(range(int(a), int(b) + 1))
            elif part:
                out.add(int(part))
        except ValueError:
            bad.append(part)
    bad += [str(k) for k in sorted(out) if not 1 <= k <= n]
    if bad:
        raise SystemExit('[멈춤] 화면 번호 %s 는 이 덱에 없다 — 1-%d 안에서 준다' % (', '.join(bad[:10]), n))
    return out


def _text_width_pt(text, size_pt, font_path=None):
    """v16.27: 한 줄 글의 폭(pt). 글꼴 파일이 있으면 PIL, 없으면 영문 0.5em·한글 1em 모델."""
    if not text:
        return 0.0
    if font_path:
        try:
            from PIL import ImageFont
            key = (font_path, int(size_pt * 10))
            if key not in _FONT_CACHE:
                _FONT_CACHE[key] = ImageFont.truetype(font_path, size=int(size_pt * 10))
            return _FONT_CACHE[key].getlength(text) / 10.0
        except Exception:
            pass
    ko = len(re.findall(r'[\uac00-\ud7a3]', text))
    return (len(text) + ko) * 0.5 * size_pt


def _est_lines_font(text, size_pt, width_emu, font_path):
    """v16.6: 폰트 파일이 있을 때 PIL 로 실제 글자폭을 재서 줄 수를 센다 (단어 단위 줄바꿈).
    `_est_lines` 의 0.5em 모델보다 정확하지만 PowerPoint 의 커닝·자간과는 여전히 다르다."""
    if not text.strip():
        return 0
    from PIL import ImageFont
    key = (font_path, int(size_pt * 10))
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(font_path, size=int(size_pt * 10))   # 10 px/pt 로 재고 pt 로 환산
    f = _FONT_CACHE[key]
    width_pt = width_emu / 12700.0
    def w(s):
        return f.getlength(s) / 10.0
    lines, cur = 1, ''
    for word in text.split(' '):
        cand = (cur + ' ' + word).strip() if cur else word
        if w(cand) <= width_pt or not cur:
            cur = cand
        else:
            lines += 1; cur = word
    return lines


def _est_lines_font_runs(runs, size_pt, width_emu, font_path, bold_path=None):
    """v16.14 (발표 §5): 굵은 run 은 굵은 글꼴 파일로 잰다 — 교육목표 항목 이름이 굵은데 Regular 로 재서 줄바꿈을 적게 셌을 수 있다."""
    from PIL import ImageFont
    def font(pth):
        key = (pth, int(size_pt * 10))
        if key not in _FONT_CACHE:
            _FONT_CACHE[key] = ImageFont.truetype(pth, size=int(size_pt * 10))
        return _FONT_CACHE[key]
    fr = font(font_path); fb = font(bold_path) if bold_path else fr
    width_pt = width_emu / 12700.0
    words, cur = [], 0.0          # 공백으로 나뉜 단어의 폭(여러 run 에 걸친 단어는 조각 폭의 합)
    for text, bold in runs:
        f = fb if bold else fr
        parts = text.split(' ')
        for k, part in enumerate(parts):
            if k:
                words.append(cur); cur = 0.0
            cur += f.getlength(part.replace('\t', '    ')) / 10.0
    words.append(cur)
    sp = fr.getlength(' ') / 10.0
    lines, line_w = 1, None
    for w in words:
        if line_w is None:
            line_w = w
        elif line_w + sp + w <= width_pt:
            line_w += sp + w
        else:
            lines += 1; line_w = w
    return lines


def _estimated_height(shape, font_path=None):
    """도형 안 텍스트가 실제로 차지할 높이(EMU)를 근사한다. font_path 가 있으면 실제 글자폭으로(v16.6)."""
    total = 0
    ncol = max(1, shape.get('numCol', 1) or 1)
    usable_w = max(1, (shape['w'] - 2 * INSET_EMU - shape.get('spcCol', 0) * (ncol - 1)) // ncol)
    for p in shape['paras']:
        if font_path and p.get('runs'):
            lines = _est_lines_font_runs(p['runs'], p['sz'], usable_w, font_path, _bold_sibling(font_path))
        elif font_path:
            lines = _est_lines_font(p['text'], p['sz'], usable_w, font_path)
        else:
            lines = _est_lines(p['text'], p['sz'], usable_w)
        total += lines * p['sz'] * LINE_FACTOR * p.get('lnspc', 1.0) * 12700
        total += (p['aft'] + p.get('bef', 0.0)) * 12700
    return total / ncol if ncol > 1 else total


def _longest_line_emu(shape):
    """wrap="none" 상자에서 가장 긴 문단의 추정 폭(EMU). _est_lines 와 같은 글자폭 모델(0.5em, 한글 2배)."""
    best = 0
    for p in shape['paras']:
        ko = len(re.findall(r'[\uac00-\ud7a3]', p['text']))
        units = len(p['text']) + ko
        best = max(best, int(units * p['sz'] * 12700 * 0.5))
    return best


def _text_extent(shape, need):
    """anchor 를 반영한 텍스트의 실제 상단·하단(EMU). t: 위에서, ctr: 가운데, b: 아래에서 need 만큼."""
    a = shape.get('anchor', 't')
    if a == 'ctr':
        mid = shape['y'] + shape['h'] / 2.0
        return mid - need / 2.0, mid + need / 2.0
    if a == 'b':
        bottom = shape['y'] + shape['h'] - shape.get('bIns', 45720)
        return bottom - need, bottom
    top = shape['y'] + shape.get('tIns', 45720)
    return top, top + need


def check_text_overflow(deck, tol=1.04, headroom=None, stream=sys.stdout, font_path=None):
    """텍스트가 자기 상자·배경 카드·슬라이드를 벗어나는지 본다.

    실제 사고 둘 (도구회신 overflow검사범위, 2026-09-09):
      - 상자가 카드보다 크게 그려진 슬라이드(anchor=ctr)에서 텍스트가 카드 아래로 나갔는데
        v16.4 는 텍스트를 자기 상자와만 비교해 [참고]조차 안 냈다.
      - wrap="none" 각주가 좌우로 슬라이드 밖까지 나갔는데 세로만 재서 못 잡았다.

    v16.5 판정:
      [심각] 텍스트의 실제 범위(anchor 반영)가 겹친 배경 카드의 위/아래 경계 밖 — 상자 크기와 무관
      [심각] 텍스트 범위가 슬라이드 밖
      [심각] wrap="none" 상자의 가장 긴 줄이 상자 폭(여백 제외) 또는 슬라이드 폭을 넘음
      [참고] 텍스트 높이가 자기 상자 높이의 tol 배를 넘음 (주변에 여백이 있으면 문제 아님)
      [참고] 상자 자체가 겹친 카드 밖으로 나감 (텍스트는 아직 안 나갔더라도 편집하면 나간다)
      [참고] headroom 지정 시: 필요 높이가 상자의 (1-headroom) 을 넘음 — PowerPoint 폰트가
             LibreOffice 렌더보다 넓은 것을 여유로 흡수 (도구회신 요청 0.15)

    근사치이므로 render 로 확인해야 한다. 폰트 대체(LibreOffice) 로 렌더가 더 좁게 나올 수 있다.
    """
    probs = []
    SW, SH = deck.slide_size()
    used_fonts, model_only = set(), set()
    for sn in deck.slide_numbers():
        cards = _fill_shapes(deck, sn)
        # v16.13 (발표 U2): --font-path 가 없으면 그 슬라이드 테마 본문 글꼴 파일을 시스템에서 찾아 쓴다. 기본 글자폭 모델(영문 0.5em·
        # 한글 1em)은 Pretendard 덱에서 PowerPoint 에서 멀쩡한 교육목표 3장을 [심각] 으로 냈고, 실제 글꼴 폭은 PowerPoint 와 맞았다
        fp = font_path or _theme_body_font_file(deck, sn)
        if fp:
            used_fonts.add(os.path.basename(fp))
        else:
            model_only.add(sn)
        for sh in _text_shapes(deck, sn):
            need = _estimated_height(sh, fp)
            if sh.get('fontScale') is not None and sh['fontScale'] < 100:
                probs.append('[참고] slide%d: "%s" PowerPoint 가 글자를 %d%% 로 자동 축소해 넘침을 숨기고 있음 (normAutofit) — 상자를 키우거나 글을 줄일 것'
                             % (sn, sh['name'], int(sh['fontScale'])))
            box_flag = need > sh['h'] * tol
            if box_flag:
                probs.append('[참고] slide%d: "%s" 텍스트가 자기 상자를 넘침 '
                             '(필요 %.2f\" / 상자 %.2f\")'
                             % (sn, sh['name'], need / 914400, sh['h'] / 914400))
            elif need > sh['h']:   # v16.6 (학회 덱 회신 결함 2): 넘지만 허용 4% 이내 — headroom 라벨과 구분
                probs.append('[참고] slide%d: "%s" 상자를 넘음(허용 %d%% 이내, 필요 %.2f\" / 상자 %.2f\")'
                             % (sn, sh['name'], int((tol - 1) * 100), need / 914400, sh['h'] / 914400))
            elif headroom and need > sh['h'] * (1 - headroom):
                probs.append('[참고] slide%d: "%s" 여유 %d%% 미만 (필요 %.2f\" / 상자 %.2f\") — PowerPoint 에서 넘칠 수 있음'
                             % (sn, sh['name'], int(headroom * 100), need / 914400, sh['h'] / 914400))
            top, bottom = _text_extent(sh, need)
            if bottom > SH + 20000 or top < -20000:
                over = max(bottom - SH, -top)
                if not fp and over <= MODEL_ONLY_TOL * sh['h']:
                    # v16.13 (발표 U2): 실제 글꼴 없이 모델로만 계산한 작은 넘침은 [심각] 이 아니다 — 모델 오차 안이다
                    probs.append('[참고] slide%d: "%s" 슬라이드 밖으로 %.2f\" (글꼴 폭 모델 — 덱 글꼴 파일이 없어 오차 범위 안, PowerPoint 확인)'
                                 % (sn, sh['name'], over / 914400))
                else:
                    probs.append('[심각] slide%d: "%s" 텍스트가 슬라이드 밖으로 %.2f\" 나감'
                                 % (sn, sh['name'], over / 914400))
            # v16.5: wrap="none" 가로 넘침
            if sh.get('wrap') == 'none':
                lw = _longest_line_emu(sh)
                usable = sh['w'] - sh.get('lIns', INSET_EMU) - sh.get('rIns', INSET_EMU)
                right = sh['x'] + sh.get('lIns', INSET_EMU) + lw
                if right > SW + 20000 or sh['x'] < 0:
                    probs.append('[심각] slide%d: "%s" wrap=none 텍스트가 슬라이드 오른쪽 밖으로 %.2f\" 나감'
                                 % (sn, sh['name'], (right - SW) / 914400))
                elif lw > usable * tol:
                    probs.append('[심각] slide%d: "%s" wrap=none 가장 긴 줄이 상자 폭을 넘음 '
                                 '(추정 %.2f\" / 상자 %.2f\") — wrap=square 로 바꾸거나 상자를 넓힐 것'
                                 % (sn, sh['name'], lw / 914400, usable / 914400))
            for c in cards:
                h_overlap = sh['x'] < c['x'] + c['w'] and sh['x'] + sh['w'] > c['x']
                v_overlap = sh['y'] < c['y'] + c['h'] and sh['y'] + sh['h'] > c['y']
                if not (h_overlap and v_overlap):
                    continue
                if bottom > c['y'] + c['h'] + 20000:
                    probs.append('[심각] slide%d: "%s" 텍스트가 카드 "%s" 아래로 %.2f\" 삐져나감'
                                 % (sn, sh['name'], c['name'], (bottom - c['y'] - c['h']) / 914400))
                elif top < c['y'] - 20000:
                    probs.append('[심각] slide%d: "%s" 텍스트가 카드 "%s" 위로 %.2f\" 삐져나감'
                                 % (sn, sh['name'], c['name'], (c['y'] - top) / 914400))
                elif sh['y'] + sh['h'] > c['y'] + c['h'] + 20000 or sh['y'] < c['y'] - 20000:
                    probs.append('[참고] slide%d: "%s" 상자가 카드 "%s" 밖으로 나가 있음 (상자 %.2f\" / 카드 %.2f\") — 글을 늘리면 카드 밖으로 나간다'
                                 % (sn, sh['name'], c['name'], sh['h'] / 914400, c['h'] / 914400))
    # v16.6.1 (전평 수용검사 2-2): PowerPoint 가 실제로 줄인(fontScale 있음) 상자의 [심각]은 추정치 기반이므로 [참고]로 낮춘다.
    # fontScale 없는 normAutofit 은 마지막 저장 때 축소가 안 걸린 것이라 [심각] 유지.
    scaled = {(sn, sh['name']) for sn in deck.slide_numbers() for sh in _text_shapes(deck, sn) if sh.get('fontScale') is not None}
    def _downgrade(p):
        m = re.match(r'\[(?:심각|참고)\] slide(\d+): "([^"]*)"', p)
        if m and (int(m.group(1)), m.group(2)) in scaled and '자동 축소' not in p:
            # v16.10 (발표 W1): PowerPoint 는 줄여 보이지만 **자동 맞춤을 안 따르는 뷰어(Google Slides 등)에서는 넘친다**
            # — 실제로 사용자가 Google Slides 로 열어 넘친 일이 반복됐다. 별도 등급. 필요 높이는 fontScale 없이 계산한 값
            return '[자동맞춤 의존] ' + p.split('] ', 1)[1] + ' — PowerPoint 에서는 줄여 보이나 자동 맞춤을 안 따르는 보기(Google Slides 등)에서는 넘칠 수 있다(실측: H&N 화면 2 넘침, 흉부1 3곳 괜찮음). 고치려면 bake-autofit, 확인은 render --no-autofit'
        return p
    probs = [_downgrade(p) for p in probs]
    seen, uniq = set(), []
    for p in probs:
        if p not in seen:
            seen.add(p); uniq.append(p)
    uniq.sort(key=lambda s: (not s.startswith('[심각]'), s))
    uniq = [deck.relabel(p) for p in uniq]
    for p in uniq:
        print('  %s' % p, file=stream)
    if not uniq:
        print('  텍스트 넘침 없음', file=stream)
    print('  * [심각]은 카드·슬라이드 밖으로 나간 것이라 화면에서 바로 보입니다.', file=stream)
    print('  * [참고]는 자기 상자만 넘었거나 여유가 적은 것으로, 주변에 여백이 있으면 문제가 아닙니다.',
          file=stream)
    print('  * 근사 계산입니다. **최종 기준은 PowerPoint(사용자 확인)** — LibreOffice 렌더는 덱 글꼴을 설치해도 PowerPoint 보다 보수적일 수 있다(H&N v9).', file=stream)
    print('  * 글자폭: %s%s' % (', '.join(sorted(used_fonts)) + (' (--font-path)' if font_path else ' (덱 테마 글꼴 자동)') if used_fonts else '모델(영문 0.5em·한글 1em)',
          (' / 글꼴 파일이 없어 모델로 계산한 슬라이드 %d장 — 그 슬라이드의 작은 넘침은 [참고]' % len(model_only)) if used_fonts and model_only else ''), file=stream)
    print('  * 가정: 줄 높이 = 글자 크기 × %.2f × 줄 간격(문단 → 레이아웃·마스터 lnSpc), 문단 앞·뒤 간격(spcBef·spcAft) 포함, 글자 크기는 '
          '문단 → 레이아웃·마스터 단계별' % LINE_FACTOR, file=stream)
    return uniq


def check_card_insets(deck, tol_emu=91440, stream=sys.stdout):
    """카드형 상자의 안쪽 여백이 슬라이드 간 tol(기본 0.1") 이상 다르면 [참고]. 서식 통일 확인용, 수정 없음.

    v16.5.1 (실물검증 회신 §3): 카드마다 **첫 상자**(가장 위 y, 같은 y 면 가장 왼쪽 x) 하나만 여백으로 잡는다.
    v16.5 는 카드 안 모든 상자의 y 를 "위 여백"으로 집계해 마지막 요약 상자의 2.28" 이 섞였다.

    두 검사를 낸다.
      (1) 슬라이드 **간**: 카드 첫 상자의 왼쪽·위 여백이 tol 이상 다르면 [참고]
      (2) 같은 카드 **안**: 텍스트 상자들의 왼쪽 x(및 오른쪽 x+w)가 0.05" 이상 다르면 [참고]

    (2) 의 소속 판정은 v16.5.2 에서 **겹침 기준**으로 바꿨다. v16.5.1 은 (1) 과 같은 "카드 안에 완전히
    들어간 상자"만 봐서, 카드 폭을 꽉 채우거나 가장자리를 조금 넘는 헤더 띠가 빠졌다 — 실물에서
    헤더(x = 카드 왼쪽 가장자리)와 본문(x = 여백 0.30")이 어긋난 슬라이드를 이 규칙 때문에 놓쳤다
    (발표 도구회신 260910 §3). 이제 상자 중심이 카드 안에 있으면 그 카드 소속으로 본다."""
    rows = []      # (slide, card, left, top)
    align = []     # (slide, card, [(name, x, right)...])
    for sn in deck.slide_numbers():
        cards = _fill_shapes(deck, sn)
        texts = _text_shapes(deck, sn)
        for c in cards:
            inside = [sh for sh in texts
                      if sh['x'] >= c['x'] - 20000 and sh['y'] >= c['y'] - 20000
                      and sh['x'] + sh['w'] <= c['x'] + c['w'] + 20000
                      and sh['y'] + sh['h'] <= c['y'] + c['h'] + 20000]
            # v16.5.2: 정렬 검사는 중심이 카드 안이면 소속으로 (헤더 띠처럼 가장자리를 넘는 상자 포함)
            belong = [sh for sh in texts
                      if c['x'] - 20000 <= sh['x'] + sh['w'] / 2 <= c['x'] + c['w'] + 20000
                      and c['y'] - 20000 <= sh['y'] + sh['h'] / 2 <= c['y'] + c['h'] + 20000]
            if inside:
                first = min(inside, key=lambda sh: (sh['y'], sh['x']))
                rows.append((sn, c['name'], first['x'] - c['x'], first['y'] - c['y']))
            if len(belong) > 1:
                lefts_ = sorted(set(sh['x'] for sh in belong))
                rights_ = sorted(set(sh['x'] + sh['w'] for sh in belong))
                if lefts_[-1] - lefts_[0] > 45720 or rights_[-1] - rights_[0] > 45720:
                    align.append((sn, c['name'],
                                  sorted(((sh['name'], sh['x'], sh['x'] + sh['w']) for sh in belong),
                                         key=lambda t: t[1])))
    probs = []
    if rows:
        lefts = [r[2] for r in rows]; tops = [r[3] for r in rows]
        def fmt(idx):
            return ', '.join('slide%d %.2f"' % (r[0], r[idx] / 914400) for r in rows[:10]) + (' …' if len(rows) > 10 else '')
        if max(lefts) - min(lefts) > tol_emu:
            probs.append('[참고] 카드 첫 상자의 왼쪽 여백이 슬라이드마다 다름: %.2f"~%.2f" (%s)'
                         % (min(lefts) / 914400, max(lefts) / 914400, fmt(2)))
        if max(tops) - min(tops) > tol_emu:
            probs.append('[참고] 카드 첫 상자의 위 여백이 슬라이드마다 다름: %.2f"~%.2f" (%s)'
                         % (min(tops) / 914400, max(tops) / 914400, fmt(3)))
    for sn, cn, boxes in align:
        probs.append('[참고] slide%d 카드 "%s" 안 상자들의 좌우가 안 맞음: %s'
                     % (sn, cn, ', '.join('%s %.2f"~%.2f"' % (n or '(이름없음)', x / 914400, r / 914400)
                                          for n, x, r in boxes)))
    probs = [deck.relabel(p) for p in probs]
    for p in probs:
        print('  %s' % p, file=stream)
    return probs


def check_notes_slide_sync(deck, stream=sys.stdout):
    """슬라이드 본문과 발표자 노트가 어긋나는지 본다.

    두 층위를 본다.
      (1) 수치 - 본문에 쓴 값이 노트에 반영되지 않은 경우
      (2) 주장 - 본문이 방향이나 한정을 명시했는데 노트는 뭉뚱그린 경우

    (2)는 실제 사고에서 나왔다. 본문을 "marker A decreased and marker B
    increased"로 고쳤는데 노트는 "diffusion did change" 그대로 남아,
    수치 비교만으로는 잡히지 않았다.
    """
    CLAIM_TERMS = [
        # v16.7.1 (MSK 수용검사 P4): 한 글자 '높'·'낮' 은 오답 보기까지 걸려 좁혔다
        ('increase', ('increas', 'higher', 'greater', 'rose', '증가', '상승', '높아', '높게', '높은', '높다')),
        ('decrease', ('decreas', 'lower', 'reduc', 'fell', '감소', '저하', '낮아', '낮게', '낮은', '낮다')),
        ('preserved', ('preserv', 'unchanged', 'stable', 'identical', '유지', '변화 없', '차이 없')),
        ('nonsignificant', ('non-significant', 'nonsignificant',
                            'not significant', 'no group difference', 'n.s.',
                            'did not differ', 'did not move', 'no difference', '유의하지 않', '유의차 없', '차이 없')),
        ('both_b_values', ('both b', 'b = 2000', 'b=2000')),
        ('cannot_provide', ('cannot provide', 'volume cannot', 'does not capture',
                            'cannot capture')),
    ]
    probs = []
    for sn in deck.slide_numbers():
        # v16.7.1 (P4): 문제 보기 줄(①②…/㉠㉡…/(1)(2)…) 은 주장이 아니다 — [주장] 검사에서 뺀다
        ptx = deck.para_texts(sn)
        body = ' '.join(deck.texts(sn))
        claim_body = ' '.join(t for t in ptx if not _MC_OPTION.match(t.strip()))
        note = ' '.join(_spoken_notes(deck.notes(sn)))
        if not note.strip():
            continue
        bl, nl = claim_body.lower(), note.lower()

        bn, nn = _numbers(body), _numbers(note)
        for tok in sorted(bn - nn):
            ctx = re.search(r'.{0,40}' + re.escape(tok) + r'.{0,20}', body)
            label = ctx.group(0) if ctx else ''
            key = re.search(r'\b(b\s*=|FA|MD|HFC|QSM|AUC|r\s*=|P\s*[=<])',
                            label, re.I)
            if key and key.group(1).lower() in nl:
                probs.append('slide%d [수치] 본문 "%s" 가 노트에 없음'
                             % (sn, label.strip()))

        for name, variants in CLAIM_TERMS:
            hit = next((v for v in variants if v in bl), None)
            if hit and not any(v in nl for v in variants):
                ctx = re.search(r'.{0,45}' + re.escape(hit) + r'.{0,30}', bl)
                probs.append('slide%d [주장] 본문의 %s 표현이 노트에 없음 -- %s'
                             % (sn, name, (ctx.group(0) if ctx else hit).strip()))

    # v16.6 (학회 덱 회신 요청 9): 노트에만 있는 수치 — 본문과 대조되지 않았다는 신호. [참고]
    only_notes = 0
    for sn in deck.slide_numbers():
        note = ' '.join(_spoken_notes(deck.notes(sn)))
        if note.strip():
            only_notes += len(_numbers(note) - _numbers(' '.join(deck.texts(sn))))
    probs = [deck.relabel(p) for p in probs]
    for p in probs:
        print('  [!] %s' % p, file=stream)
    if not probs:
        print('  본문-노트 불일치 없음', file=stream)
    if only_notes:
        print('  [참고] 노트에만 있는 수치 %d개 — 본문과 대조되지 않았다. 원고 대조는 crosscheck --notes' % only_notes, file=stream)
    return probs

# ----------------------------------------------------------------------------
# 주장 관계도 / 의존 그래프 — v13 부터 claim_graph.py 로 분리
#
#  발표·저자·리뷰어 세 프로젝트가 같은 그래프 규약을 쓰기 위해 pptx 에 독립적인
#  모듈로 뺐다. 여기서는 pptx 자리(slide:N / notes:N)를 읽어 주는 resolver 만 만들어
#  넘긴다. 규약과 명령 설명은 CLAIM_GRAPH.md 를 본다.
# ----------------------------------------------------------------------------

sys.dont_write_bytecode = True   # claim_graph import 가 /mnt/project 에 __pycache__ 를 남기지 않게 (v16.8.2)
import claim_graph as CG
from claim_graph import (load_claims, load_claims_meta, save_claims,
                         mapgraph, impact, EDGE_TYPES, CLAIM_STATUS, IMPACT_CUTOFF)


def _site_text(deck, site):
    """'slide:11' / 'notes:11' (파일 번호) 또는 'slide@256' / 'notes@256' (sldId, v16.7 권장) -> 자리의 텍스트.
    PowerPoint 는 저장할 때 slide 파일을 화면 순서대로 다시 번호 매기므로 파일 번호 사이트는 사용자 저장본에서
    조용히 다른 슬라이드를 가리킨다(MSK 회신 N2, 29장 실측). sldId 는 저장을 견딘다."""
    m = re.match(r'^(slide|notes)([:@])(\d+)$', site.strip())
    if not m:
        raise ValueError('site 는 slide:N / notes:N / slide@ID / notes@ID 형식이어야 합니다: %s' % site)
    kind, sep, num = m.group(1), m.group(2), int(m.group(3))
    sn = deck.slide_by_id(num) if sep == '@' else num
    if sn is None:
        raise ValueError('sldId %d 인 슬라이드 없음' % num)
    return ' '.join(deck.texts(sn) if kind == 'slide' else deck.notes(sn))


def sites_to_sldid(deck, claims):
    """v16.7 (N2): claims 의 slide:N / notes:N 사이트를 slide@ID / notes@ID 로 바꾼다. 반환: 바꾼 수."""
    n = 0
    for c in claims:
        new = []
        for s in c.get('sites', []):
            m = re.match(r'^(slide|notes):(\d+)$', s.strip())
            if m and deck.sld_id(int(m.group(2))):
                new.append('%s@%d' % (m.group(1), deck.sld_id(int(m.group(2))))); n += 1
            else:
                new.append(s)
        c['sites'] = new
    return n


def _order_warning(deck, claims, stream):
    file_sites = [s for c in claims for s in c.get('sites', []) if re.match(r'^(slide|notes):\d+$', s.strip())]
    order = [sn for sn, _, _ in deck.order() if sn]
    if file_sites and order != sorted(order):
        print('[경고] 화면 순서 ≠ 파일 번호인 덱인데 파일 번호 사이트(slide:N)가 %d개 — PowerPoint 로 저장하면 번호가 바뀐다. '
              '`mapcheck --to-sldid` 로 slide@ID 로 바꿀 것' % len(file_sites), file=stream)


def _resolver(deck):
    return lambda site: _site_text(deck, site)


def _relabel_sldid(deck, text):
    """v16.7.3 (발표 T3): 'slide@261' 옆에 '(화면 8)'. sldId 는 사람이 읽고 화면을 알 수 없다."""
    def f(m):
        sn = deck.slide_by_id(int(m.group(2)))
        pos = deck.screen_no(sn) if sn else None
        return m.group(0) + (' (화면 %d)' % pos if pos else ' (없음)')
    return re.sub(r'\b(slide|notes)@(\d+)\b(?! \()', f, text)


def mapcheck(deck, claims, stream=sys.stdout, nums=False):
    _order_warning(deck, claims, stream)
    buf = io.StringIO()
    probs, matrix = CG.mapcheck(_resolver(deck), claims, buf, nums=nums)
    stream.write(_relabel_sldid(deck, buf.getvalue()))
    probs = [_relabel_sldid(deck, p) for p in probs]
    unmapped_sites(deck, claims, stream)
    return probs, matrix


def mapreport(deck, claims, stream=sys.stdout):
    return CG.mapreport(claims, stream)


def mapfreeze(deck, claims, at=None, sources=None, stream=None):
    return CG.mapfreeze(_resolver(deck), claims, at, sources=sources, stream=stream)   # v16.41: 근거 원문 폴더(교과서 분할 등)


def mapstale(deck, claims, stream=sys.stdout, sources=None):
    return CG.mapstale(_resolver(deck), claims, stream, sources=sources)


def _paragraphs(path):
    """슬라이드/노트 XML 의 문단 단위 텍스트. run 은 붙이고 문단은 줄로 나눈다."""
    x = open(path, encoding='utf8').read()
    out = []
    for pm in re.finditer(r'<a:p>(.*?)</a:p>', x, re.S):
        t = ''.join(re.findall(r'<a:t[^>]*>([^<]*)</a:t>', pm.group(1)))
        if t.strip():
            out.append(html.unescape(t.strip()))
    return out


def deck_units(deck):
    """extract 용: 덱의 자리마다 (site, text). 문단은 줄바꿈으로 구분, 표지 제외."""
    out = []
    order = [sn for sn, _, _ in deck.order() if sn]
    for sn in order[1:]:
        out.append(('slide:%d' % sn, '\n'.join(_paragraphs(deck._slide(sn)))))
        n = deck.notes_no(sn)
        p = os.path.join(deck.dir, 'ppt/notesSlides/notesSlide%d.xml' % n) if n else None
        lines = _paragraphs(p) if p and os.path.exists(p) else []
        out.append(('notes:%d' % sn, '\n'.join(_spoken_notes(lines))))
    return out


def unmapped_sites(deck, claims, stream=sys.stdout):
    """본문 텍스트가 있는데 어느 주장에도 속하지 않은 슬라이드/노트.

    관계도가 덱보다 뒤처지는 것을 잡는다. 표지·케이스 제시 슬라이드는 주장이
    없는 것이 정상이므로 [참고] 로만 낸다.
    """
    covered = set()
    for c in claims:
        covered.update(c.get('sites', []))
    out = []
    first = (deck.order() or [(None,)])[0][0]      # 표지는 제외
    for sn in deck.slide_numbers():
        if sn == first:
            continue
        body = [t for t in deck.texts(sn)[1:] if t.strip()]
        if len(body) >= 3 and 'slide:%d' % sn not in covered:
            out.append('slide:%d' % sn)
        if _weighted_words(' '.join(_spoken_notes(deck.notes(sn)))) > 60 \
                and 'notes:%d' % sn not in covered:
            out.append('notes:%d' % sn)
    if out:
        print('  [참고] 어느 주장에도 속하지 않은 자리: %s' % ', '.join(out), file=stream)
    return out

# ----------------------------------------------------------------------------
# 미디어 / 렌더 / 검증
# ----------------------------------------------------------------------------

def extract_media(pptx, outdir, scale=2):
    os.makedirs(outdir, exist_ok=True)
    with zipfile.ZipFile(pptx) as z:
        names = [n for n in z.namelist() if n.startswith('ppt/media/')]
        for n in names:
            with open(os.path.join(outdir, os.path.basename(n)), 'wb') as f:
                f.write(z.read(n))
    try:
        from PIL import Image
    except ImportError:
        print('PIL 없음 — 확대본 생략')
        return sorted(os.listdir(outdir))
    for f in sorted(os.listdir(outdir)):
        if f.startswith('x2_'):
            continue
        p = os.path.join(outdir, f)
        try:
            im = Image.open(p)
        except Exception:
            continue
        w, h = im.size
        print('%-16s %dx%d' % (f, w, h))
        if scale > 1:
            im.resize((w * scale, h * scale)).save(
                os.path.join(outdir, 'x2_' + os.path.splitext(f)[0] + '.png'))
    return sorted(os.listdir(outdir))


def no_autofit_copy(pptx, out):
    """모든 normAutofit(비율 포함)을 noAutofit 으로 바꾼 사본 — 자동 맞춤을 안 따르는 뷰어의 모양을 LibreOffice 로 본다 (v16.10, W1)."""
    zin = zipfile.ZipFile(pptx); zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED); n = 0
    for it in zin.infolist():
        data = zin.read(it.filename)
        if it.filename.startswith('ppt/slides/slide') and it.filename.endswith('.xml'):
            x = data.decode('utf8'); k = len(re.findall(r'<a:normAutofit\b[^>]*/>', x)); n += k
            data = re.sub(r'<a:normAutofit\b[^>]*/>', '<a:noAutofit/>', x).encode('utf8')
        zout.writestr(it, data)
    zin.close(); zout.close()
    return n


MODEL_ONLY_TOL = 0.05   # 실제 글꼴 없이 계산한 넘침이 상자 높이의 5% 이내면 [참고] (v16.13, 발표 U2 제안 2)
_FONT_FILES = None
_FONT_STYLES = {}


def _bold_sibling(path):
    """같은 글꼴의 굵은 파일(Bold → SemiBold). 파일 이름의 Regular 를 바꿔 보고, 없으면 fc-list 색인에서. 없으면 None."""
    if not path:
        return None
    for w in ('Bold', 'SemiBold'):
        c = re.sub(r'Regular(?=\.[ot]tf$)', w, path)
        if c != path and os.path.exists(c):
            return c
    _font_file_index()
    fam = next((f for (f, st), pth in _FONT_STYLES.items() if pth == path), None)
    for st in ('bold', 'semibold'):
        if fam and (fam, st) in _FONT_STYLES:
            return _FONT_STYLES[(fam, st)]
    return None


def _font_file_index():
    """{소문자 글꼴 이름: 파일 경로} — fc-list 의 family(여러 이름·지역 이름 포함). 굵기 별 파일은 Regular 를 우선."""
    global _FONT_FILES
    if _FONT_FILES is None:
        _FONT_FILES = {}
        try:
            out = subprocess.run(['fc-list', ':', 'family', 'style', 'file'], capture_output=True, text=True).stdout
        except Exception:
            out = ''
        for line in out.splitlines():
            m = re.match(r'^(.*?):\s*(.*?)(?::style=(.*))?$', line)
            if not m:
                continue
            path, fams, style = m.group(1), m.group(2), (m.group(3) or '')
            first = style.split(',')[0].strip()        # 'ExtraLight,Regular' 처럼 뒤에 Regular 가 붙는 굵기가 있다 — 첫 이름으로
            regular = first in ('Regular', 'Normal', 'Book', 'Roman', '') or os.path.basename(path).lower().endswith(('-regular.otf', '-regular.ttf'))
            for fam in fams.split(','):
                k = fam.strip().lower()
                if k and (k not in _FONT_FILES or regular):
                    _FONT_FILES[k] = path
                if k:
                    _FONT_STYLES.setdefault((k, first.lower()), path)
    return _FONT_FILES


def _theme_body_font_file(deck, slide_no):
    """그 슬라이드 마스터 테마의 본문 글꼴(minor — 한글 ea 가 있으면 그것, 없으면 latin) 파일 경로. 없으면 None."""
    mp = _master_of(deck, slide_no)
    if not mp or not os.path.exists(mp):
        return None
    mr = os.path.join(os.path.dirname(mp), '_rels', os.path.basename(mp) + '.rels')
    t = re.search(r'Target="\.\./theme/([^"]+)"', open(mr, encoding='utf8').read()) if os.path.exists(mr) else None
    tp = os.path.join(deck.dir, 'ppt/theme', t.group(1)) if t else None
    if not tp or not os.path.exists(tp):
        return None
    minor = re.search(r'<a:minorFont>(.*?)</a:minorFont>', open(tp, encoding='utf8').read(), re.S)
    if not minor:
        return None
    idx = _font_file_index()
    for tag in ('ea', 'latin'):
        m = re.search(r'<a:%s typeface="([^"]+)"' % tag, minor.group(1))
        if m and m.group(1).lower() in idx:
            return idx[m.group(1).lower()]
    return None


def theme_fonts_missing(pptx):
    """v16.12 (발표 U2): 덱 테마 글꼴(major/minor latin·ea) 중 이 시스템에 없는 것. 없으면 LibreOffice 가 다른 글꼴로 그려 줄바꿈이 달라진다."""
    try:
        have = subprocess.run(['fc-list', ':', 'family'], capture_output=True, text=True).stdout.lower()
    except Exception:
        return []
    need = set()
    with zipfile.ZipFile(pptx) as z:
        for f in z.namelist():
            if f.startswith('ppt/theme/theme') and f.endswith('.xml'):
                x = z.read(f).decode('utf8', 'ignore')
                for part in re.findall(r'<a:(?:major|minor)Font>(.*?)</a:(?:major|minor)Font>', x, re.S):
                    need.update(v for v in re.findall(r'<a:(?:latin|ea) typeface="([^"+][^"]*)"', part) if v)
    return sorted(f for f in need if f.lower() not in have)


def render(pptx, outdir, dpi=110, no_autofit=False):
    os.makedirs(outdir, exist_ok=True)
    miss = theme_fonts_missing(pptx)
    if miss:
        print('[참고] 테마 글꼴이 이 시스템에 없다: %s — 렌더가 다른 글꼴로 그려 줄바꿈·넘침이 PowerPoint 와 다를 수 있다. '
              '글꼴 파일을 ~/.fonts 에 넣고 fc-cache -f' % ', '.join(miss), file=sys.stderr)
    if no_autofit:
        cp = os.path.join(tempfile_dir('naf'), os.path.basename(pptx))
        print('자동 맞춤을 끈 상자 %d개' % no_autofit_copy(pptx, cp))
        pptx = cp
    soffice = '/mnt/skills/public/pptx/scripts/office/soffice.py'
    cmd = ([sys.executable, soffice] if os.path.exists(soffice) else ['soffice'])
    subprocess.run(cmd + ['--headless', '--convert-to', 'pdf', os.path.abspath(pptx)],
                   cwd=outdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(pptx))[0] + '.pdf')
    subprocess.run(['pdftoppm', '-jpeg', '-r', str(dpi), pdf,
                    os.path.join(outdir, 'slide')], check=True)
    return sorted(f for f in os.listdir(outdir) if f.endswith('.jpg'))


MIN_PPTX_B64_NOTE = """
make_fixture() 는 외부 샘플 없이 테스트를 돌리기 위한 최소 덱을 만든다.
python-pptx 가 있으면 그것을 쓰고, 없으면 사용자가 샘플 pptx 를 주어야 한다.
"""


def make_fixture(path, slides=14, widescreen=False):
    """테스트용 최소 pptx 를 생성한다. python-pptx 필요.

    audit 이 검출해야 하는 결함을 일부러 심어 둔다:
      - 같은 이미지를 두 슬라이드에 중복 사용
      - 한 글자 잔재 텍스트
      - 노트가 동일한 슬라이드 쌍
    """
    try:
        from pptx import Presentation
        from pptx.util import Inches
    except ImportError:
        raise FileNotFoundError(
            'python-pptx 가 없어 샘플 덱을 만들 수 없습니다. '
            'pip install python-pptx 하거나 TK_DECK 환경변수로 '
            '샘플 pptx 경로를 지정하십시오.')
    img = os.path.join(os.path.dirname(path) or '.', '_tk_fixture.png')
    if not os.path.exists(img):
        try:
            from PIL import Image as _Im
            _Im.new('RGB', (64, 64), (90, 90, 90)).save(img)
        except ImportError:
            img = None

    prs = Presentation()
    if widescreen:
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    layout = prs.slide_layouts[1]
    for i in range(1, slides + 1):
        s = prs.slides.add_slide(layout)
        s.shapes.title.text = 'Slide %d title' % i
        tf = s.placeholders[1].text_frame
        tf.text = 'Value 0.505 and 0.541 on slide %d' % i
        if i == 6:
            tf.add_paragraph().text = 'B'          # 한 글자 잔재
        if img and i in (4, 5):                    # 이미지 중복 사용
            s.shapes.add_picture(img, Inches(4), Inches(2), Inches(2))
        note = 'Note for slide %d' % i
        if i in (9, 10):
            note = 'Duplicated note text'          # 노트 중복
        s.notes_slide.notes_text_frame.text = note
    prs.save(path)
    return path


def validate_path():
    """validate.py 자리 — handoff 와 같은 환경변수(HANDOFF_VALIDATE_PY)를 따른다(v16.38 — 전에는 deck 만 고정 경로라 둘이 달랐다)."""
    return os.environ.get('HANDOFF_VALIDATE_PY', '/mnt/skills/public/pptx/scripts/office/validate.py')


def vword(r):
    """validate 결과 → 말. None 은 validate.py 없이 구조 검사만 통과한 것 — 정밀 검사 '통과' 가 아니다(v16.39)."""
    return {True: '통과', False: '실패', None: '구조 검사 통과(정밀 검사 없음)'}[r]


def structure_check(pptx):
    """v16.39 (사용자 09-29): validate.py 가 없을 때(Cowork) 쓰는 가벼운 구조 검사 — zip 이 온전한지, 모든 XML·rels 가 제대로
    닫혔는지(파싱), python-pptx 로 다시 열리는지. 스키마·관계 규칙은 보지 않는다(정밀 검사 아님). 반환: 문제 목록(빈 목록 = 통과)."""
    import xml.etree.ElementTree as ET
    try:
        z = zipfile.ZipFile(pptx)
    except Exception as e:
        return ['zip 을 열지 못했다: %s: %s' % (type(e).__name__, str(e)[:80])]
    probs = []
    with z:
        try:
            bad = z.testzip()
        except Exception as e:
            return ['zip 을 읽지 못했다: %s: %s' % (type(e).__name__, str(e)[:80])]
        if bad:
            probs.append('zip 항목이 깨졌다: %s' % bad)
        for n in z.namelist():
            if n.endswith(('.xml', '.rels')):
                try:
                    ET.fromstring(z.read(n))
                except Exception as e:
                    probs.append('XML 이 온전하지 않다: %s (%s)' % (n, str(e)[:60]))
    if not probs:
        try:
            from pptx import Presentation
        except ImportError:
            print('[참고] python-pptx 없음 — 다시 열기 검사는 건너뛴다')
        else:
            try:
                Presentation(pptx)
            except Exception as e:
                probs.append('python-pptx 로 열리지 않는다: %s: %s' % (type(e).__name__, str(e)[:80]))
    return probs


def validate(pptx, original=None, vpath=None):
    """검증. **original 을 반드시 넘긴다.**

    original 없이 돌리면 원본에 원래 있던 무해한 스키마 오류
    (예: ppt/revisionInfo.xml)까지 실패로 잡혀 위양성이 난다.
    --original 을 주면 '원본 대비 새로 생긴 오류'만 본다.
    """
    v = vpath or validate_path()
    if not os.path.exists(v):   # v16.38: 전에는 True('통과'). v16.39: 없으면 구조 검사 — 통과 None, 실패 False
        probs = structure_check(pptx)
        if probs:
            print('구조 검사 실패 — validate.py 없음(%s), 가벼운 검사에서 걸림:' % v)
            for p_ in probs[:20]:
                print('  - %s' % p_)
            return False
        print('구조 검사 통과(정밀 검사 없음) — validate.py 없음(%s). zip·XML·python-pptx 열기만 봤다' % v)
        return None
    if original is None:
        print('[주의] original 미지정 — 원본에 있던 오류까지 잡힐 수 있음')
    cmd = [sys.executable, v, pptx]
    if original:
        cmd += ['--original', original]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-800:])
    return r.returncode == 0


# ----------------------------------------------------------------------------
# v16.9: 원본 대비 비교 (H&N 보충 A·B) — 화면 순서로 짝짓고, 노트는 원본 문단 XML 이 남았는지 본다
# ----------------------------------------------------------------------------

def parse_screen_map(path):
    """매핑표(markdown 표) → [(편집본 화면, 출처 이름, 원본 화면, 의도한 수정)]. 영상의학 회신 형식:
    `| 33 | 2025 덱 4 | 제목 | 의도한 본문 수정 |`, `| 4 | H&N 원본 43 복제 | … |`. 출처 이름은 숫자 앞 글자 전부."""
    out = []
    for line in open(path, encoding='utf8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) < 2 or not c[0].isdigit():
            continue
        m = re.match(r'^(.*?)\s*(\d+)\s*(?:복제)?$', c[1])
        if m:
            out.append((int(c[0]), m.group(1).strip(), int(m.group(2)), c[3] if len(c) > 3 else ''))
    return out


def _box_texts(deck, sn):
    """v16.32 (발표 D1): 상자(도형·표)마다 글을 모아 띄어쓰기를 하나로 — 정렬한 목록. 상자 순서가 바뀌거나 한 상자 안의 글 조각이
    합쳐져도 같다(adopt-house-look 이 제목 글상자를 제목 자리 표시자로 옮긴 화면이 '의도하지 않은 글 변경' 으로 잡힌 일)."""
    x = open(deck._slide(sn), encoding='utf8').read()
    out = []
    for m in re.finditer(r'<p:(sp|graphicFrame)>(?:(?!<p:\1>).)*?</p:\1>', x, re.S):
        t = ' '.join(html.unescape(''.join(_AT.findall(q))) for q in re.findall(r'<a:p>(.*?)</a:p>', m.group(0), re.S))
        t = re.sub(r'\s+', ' ', t).strip()
        if t:
            out.append(t)
    return sorted(out)


def _slide_text(deck, sn):
    return ' '.join(t.strip() for t in deck.texts(sn) if t.strip())


def _slide_key(deck, sn):
    """짝짓기 열쇠: (슬라이드 글, 쓰인 그림들의 해시). v16.10 (발표 Z3): 글이 없는 영상 슬라이드가 많은 덱에서 글만으로 짝지어
    엉뚱한 화면과 붙었다 — 그림 해시를 더한다."""
    import hashlib
    hs = []
    for m in deck.images(sn):
        fp = os.path.join(deck.dir, 'ppt/media', m)
        if os.path.exists(fp):
            hs.append(hashlib.md5(open(fp, 'rb').read()).hexdigest()[:10])
    return (_slide_text(deck, sn), tuple(sorted(hs)))


def _key_index(decks):
    """{열쇠: [(덱, slide)...]} — 열쇠가 여러 화면에 걸리면 모호."""
    idx = {}
    for D in decks:
        for s in [s for s, _, _ in D.order() if s]:
            idx.setdefault(_slide_key(D, s), []).append((D, s))
    return idx


def diff_decks(original, edited, stream=sys.stdout, mapping=None, sources=None, match_text=False, memo_only=False):
    """원본 덱과 편집본을 비교한다. 짝짓기는 셋 중 하나:
    - 기본: presentation.xml **순서**로(파일 이름이 아니라 — python-pptx 재저장처럼 파트 이름이 다시 매겨져도 된다, 보충 B)
    - mapping: 매핑표 [(편집 화면, 출처 이름, 원본 화면, 의도한 수정)] — 순서를 바꾸고 다른 덱을 섞은 편집본(H&N v3). sources 는
      {출처 이름: 덱 또는 경로}, 이름이 없으면 original 을 쓴다
    - match_text=True: 편집본 화면마다 슬라이드 글이 같은 원본 화면을 찾는다(복제 화면은 같은 원본에 여러 번 짝지어진다)
    화면마다: 슬라이드 글이 원본과 같은가(다르면 매핑표의 의도한 수정이 있어야 한다), 원본 노트 문단의 보존(XML 동일) / 서식 변경
    (글은 같고 XML 다름 — 굵게·색·링크 소실, 보충 A) / 사라짐, sldNum 자리 소실. **직전 판이 아니라 작업 전 원본과 비교한다.**
    memo_only=True (v16.9.2): 원본 노트에 '기존 메모' 표지가 있으면 그 뒤 문단만 센다 — 판끼리(v3 → v5) 비교에서 우리가 다시 쓴
    대본·참고 문단을 '사라짐' 으로 세지 않는다.
    반환 {'slides_changed': [...], 'unintended': [...], 'notes': {화면: (보존, 서식변경, 사라짐)}, 'sldnum_lost': [...], 'unmatched': [...]}"""
    made = []
    def op(d, tag):
        if isinstance(d, Deck):
            return d
        t = tempfile_dir(tag); made.append(t)
        return Deck.open(d, t)
    try:
        return _diff_decks(op(original, 'dfa'), op(edited, 'dfb'), {k: op(v, 'dfs') for k, v in (sources or {}).items()},
                           stream, mapping, match_text, memo_only)
    finally:
        for t in made:   # v16.9.2 (Y1): 경로로 받아 여기서 연 덱의 추출 폴더는 끝나면 지운다
            shutil.rmtree(t, ignore_errors=True)
            if t in _TEMP_DIRS:
                _TEMP_DIRS.remove(t)


def _diff_decks(A, B, src, stream, mapping, match_text, memo_only):
    ob = [s for s, _, _ in B.order() if s]
    pairs = []   # (편집 화면, 원본 덱, 원본 slide, 의도한 수정)
    res = {'slides_changed': [], 'unintended': [], 'notes': {}, 'sldnum_lost': [], 'unmatched': []}
    if mapping:
        for es, label, os_, intended in mapping:
            D = src.get(label, A)
            od = [s for s, _, _ in D.order() if s]
            if es > len(ob) or os_ > len(od):
                res['unmatched'].append(es); continue
            pairs.append((es, D, od[os_ - 1], intended))
    elif match_text:
        idx = _key_index([A])
        res['ambiguous'] = []
        for pos, sb in enumerate(ob, 1):
            key = _slide_key(B, sb)
            hit = idx.get(key, [])
            if not key[0] and not key[1]:
                res['ambiguous'].append(pos)            # 글도 그림도 없는 화면 — 짝지을 근거가 없다
            elif len(hit) == 1:
                pairs.append((pos, A, hit[0][1], ''))
            elif len(hit) > 1:
                res['ambiguous'].append(pos)            # v16.10 (Z3): 후보가 여럿이면 짝짓지 않고 '모호' 로 보고
            else:
                res['unmatched'].append(pos)
    else:
        oa = [s for s, _, _ in A.order() if s]
        if len(oa) != len(ob):
            print('[!] 화면 수가 다름: 원본 %d / 편집본 %d — 앞에서부터 짝짓는다 (순서가 바뀐 편집본이면 --map 또는 --match-text)' % (len(oa), len(ob)), file=stream)
        pairs = [(pos, A, sa, '') for pos, sa in enumerate(oa[:len(ob)], 1)]
    for pos, D, sa, intended in pairs:
        sb = ob[pos - 1]
        if open(D._slide(sa), encoding='utf8').read() != open(B._slide(sb), encoding='utf8').read():
            res['slides_changed'].append(pos)
        if _box_texts(D, sa) != _box_texts(B, sb) and not intended:   # v16.32 (발표 D1): 상자 순서·조각 합침은 같은 글
            res['unintended'].append(pos)
        allp = D.notes_paragraphs(sa)
        if memo_only:
            k = next((i for i, q in enumerate(allp) if _is_memo_sep(q['text'])), None)
            # v16.10 (발표 W4): 기존 메모 표지가 없는 화면은 원작자 메모가 없는 것 — 대본을 세지 않는다
            allp = allp[k + 1:] if k is not None else []
        pa = [q for q in allp if q['text'].strip()]
        # v16.16 (발표 P2): 하이퍼링크 등 r:id 는 rels 의 대상으로 풀어 비교 — 복사하며 새 rId 로 옮긴 문단을 '서식 변경' 으로 셌다
        na_t, nb_t = _notes_rel_targets(D, sa), _notes_rel_targets(B, sb)
        xb = [_rid_to_target(q['xml'], nb_t) for q in B.notes_paragraphs(sb)]
        tb = [q['text'] for q in B.notes_paragraphs(sb)]
        keep = fmt = gone = 0
        for q in pa:
            if _rid_to_target(q['xml'], na_t) in xb:
                keep += 1
            elif q['text'] in tb:
                fmt += 1
            else:
                gone += 1
        if pa:
            res['notes'][pos] = (keep, fmt, gone)
        na, nb = D._notes_path(sa), B._notes_path(sb)
        if na and 'type="sldNum"' in open(na, encoding='utf8').read() and not (nb and 'type="sldNum"' in open(nb, encoding='utf8').read()):
            res['sldnum_lost'].append(pos)
    tot = [sum(v[i] for v in res['notes'].values()) for i in range(3)]
    how = '매핑표' if mapping else '슬라이드 글 일치' if match_text else '화면 순서'
    print('=== 원본 대비 비교 (%s로 짝지음, %d화면%s) ===' % (how, len(pairs), ', 기존 메모 구역만' if memo_only else ''), file=stream)
    if res['unmatched']:
        print('[!] 짝을 못 찾은 편집본 화면: %s' % res['unmatched'], file=stream)
    if res.get('ambiguous'):
        print('[!] 짝이 모호해 세지 않은 화면(글·그림이 같은 원본 화면이 여럿이거나 없음): %s — 매핑표(--map)로' % res['ambiguous'], file=stream)
    print('슬라이드 글이 원본과 다른데 의도한 수정이 없는 화면: %s' % (res['unintended'] or '없음'), file=stream)
    print('원본 노트 문단: 보존 %d / 서식 변경 %d / 사라짐 %d' % tuple(tot), file=stream)
    for pos, (k, f, g) in res['notes'].items():
        if f or g:
            print('  화면 %d: 서식 변경 %d · 사라짐 %d' % (pos, f, g), file=stream)
    if res['sldnum_lost']:
        print('[!] 노트 sldNum 자리가 사라진 화면: %s' % res['sldnum_lost'], file=stream)
    return res


NOTE_TAGS = re.compile(r'\[(?:검증|색인|기억 기반|미검증|영상 확인|발표 전 확인|역추정)(?:[:：][^\]]*)?\]')   # 영상의학 작업규약 §5.5


def _split_sentences(t):
    return [x for x in re.split(r'(?<=[.?!。])\s+', t) if x and x.strip()]


def _tidy(t):
    return re.sub(r'\s+([.?!,])', r'\1', re.sub(r'\s{2,}', ' ', t)).strip()


def normalize_notes(deck, slide_no, dry_run=False):
    """노트를 현행 규격으로 (v16.9, 사용자 09-24 — 영상의학 v1 대본 덱 전부):
    - 낭독 부분에 있던 **근거 태그**([검증]·[색인]·[기억 기반]·[미검증]·[영상 확인]·[발표 전 확인]·[역추정], `[검증: 출처]` 형 포함)를
      뺀다. 태그가 붙은 문장은 '태그 + 문장' 으로 참고 구역에 옮기고, 낭독에는 태그를 뺀 문장을 남긴다(작업규약 §5.5 "문장 단위").
      태그만 있는 문단은 통째로 옮긴다
    - 옛 표지(`────── 기존 메모 ──────` 등)를 `NOTES_SEP_MEMO` 로, 참고 구역이 필요하면 `NOTES_SEP` 를 넣는다
    - 태그가 없는 낭독 문단·참고 문단·기존 메모 문단은 바이트 그대로
    반환 {'moved': n, 'sep': 바꾼 표지 수}"""
    paras = deck.notes_paragraphs(slide_no)
    if not paras:
        return {'moved': 0, 'sep': 0}
    memo_i = next((i for i, q in enumerate(paras) if _is_memo_sep(q['text'])), len(paras))
    tip_i = next((i for i, q in enumerate(paras[:memo_i]) if _is_cutoff_line(q['text']) or _looks_like_cutoff(q['text'])), memo_i)
    spoken_xml, moved = [], []
    for q in paras[:tip_i]:
        t = q['text']
        if not NOTE_TAGS.search(t):
            spoken_xml.append(q['xml']); continue
        if NOTE_TAGS.match(t.strip()):          # 태그로 시작하는 문단 = 근거 줄 → 통째로 참고로
            moved.append(_tidy(t)); continue
        keep = []
        for sent in _split_sentences(t):
            tags = NOTE_TAGS.findall(sent)
            if tags:
                bare = _tidy(NOTE_TAGS.sub('', sent))
                moved.append(' '.join(tags) + ((' ' + bare) if bare else ''))
                if bare and not re.fullmatch(r'[\W\d_]*', bare):
                    keep.append(bare)
            else:
                keep.append(sent.strip())
        rest = ' '.join(keep).strip()
        if rest and not re.fullmatch(r'[\W_]*', rest):
            spoken_xml.append(notes_xml([rest]))
    n_sep = 0
    tips_xml = [q['xml'] for q in paras[tip_i:memo_i]]
    if tips_xml and paras[tip_i]['text'].strip() != NOTES_SEP and not _is_memo_sep(paras[tip_i]['text']):
        tips_xml[0] = notes_xml([NOTES_SEP]); n_sep += 1
    if moved:
        if not tips_xml:
            tips_xml = [notes_xml(['', NOTES_SEP])]
        tips_xml += [notes_xml(['- ' + m for m in moved])]
    memo_xml = [q['xml'] for q in paras[memo_i:]]
    if memo_xml and paras[memo_i]['text'].strip() != NOTES_SEP_MEMO:
        memo_xml[0] = notes_xml([NOTES_SEP_MEMO]); n_sep += 1
    if not dry_run and (moved or n_sep):
        p, x, a, e = deck._notes_body(slide_no)
        s0, s1 = paras[0]['start'], paras[-1]['end']
        open(p, 'w', encoding='utf8').write(x[:s0] + ''.join(spoken_xml + tips_xml + memo_xml) + x[s1:])
    return {'moved': len(moved), 'sep': n_sep, 'samples': moved[:2]}


def parse_fixes(path):
    """`## 본문 수정` 표 → [(화면, 원문, 수정문)]. 형식 `| 화면 | 원문 | 수정문 | (근거) |`, 화면은 **작업 전 원본 덱** 번호."""
    out = []
    for line in open(path, encoding='utf8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) >= 3 and c[0].isdigit() and c[1]:
            out.append((int(c[0]), c[1].strip('`'), c[2].strip('`')))
    return out


def apply_fixes(deck, fixes, dry_run=False, stream=sys.stdout):
    """본문 오기·보정 수정을 한 곳씩 적용한다(사용자 09-24: 다른 사람 풀이도 형식을 지키며 고칠 수 있으면 고치고, 고친 뒤 보고).
    `settext` 규칙 그대로 — 한 <a:t> 안에서 정확히 1회 매치일 때만 바꾸고, 0회·여러 번·run 경계로 쪼개진 곳은 거부한다(형식이 깨질
    위험이 있는 곳은 손대지 않음). 반환 [(화면, 원문, 수정문, '적용'|'거부: 이유')]. 끝에 보고용 표를 찍는다."""
    order = [s for s, _, _ in deck.order() if s]
    res = []
    for scr, old, new in fixes:
        if scr > len(order):
            res.append((scr, old, new, '거부: 화면 번호 범위 밖')); continue
        r = deck.settext(order[scr - 1], old, new, dry_run=dry_run)
        res.append((scr, old, new, '적용' if r['ok'] else '거부: ' + r['reason']))
    print('| 화면 | 원문 | 수정문 | 결과 |\n|---|---|---|---|', file=stream)
    for scr, old, new, st in res:
        print('| %d | %s | %s | %s |' % (scr, old, new, st + (' (dry-run)' if dry_run and st == '적용' else '')), file=stream)
    print('적용 %d / 거부 %d' % (sum(1 for r in res if r[3] == '적용'), sum(1 for r in res if r[3] != '적용')), file=stream)
    return res


def match_sources_by_text(edited, sources):
    """편집본 화면마다 슬라이드 글이 같은 원천 화면을 여러 원천 덱에서 찾는다. 반환 ([(편집 slide, 원천 덱, 원천 slide)], [짝 없는 편집 화면 번호])."""
    idx = _key_index(sources)
    pairs, miss = [], []
    for pos, sb in enumerate([s for s, _, _ in edited.order() if s], 1):
        hit = idx.get(_slide_key(edited, sb), [])
        if len(hit) == 1:
            pairs.append((sb, hit[0][0], hit[0][1]))
        else:
            miss.append(pos)        # 없거나 모호 — 메모를 엉뚱한 화면에서 가져오지 않는다
    return pairs, miss


def _notes_rel_targets(deck, slide_no):
    n = deck.notes_no(slide_no)
    rp = os.path.join(deck.dir, 'ppt/notesSlides/_rels/notesSlide%s.xml.rels' % n) if n else ''
    if not rp or not os.path.exists(rp):
        return {}
    return {m.group(1): m.group(2) for m in re.finditer(r'<Relationship [^>]*?Id="(rId\d+)"[^>]*?Target="([^"]+)"', open(rp, encoding='utf8').read())}


def _rid_to_target(xml, targets):
    return re.sub(r'r:(id|embed|link)="(rId\d+)"', lambda m: 'r:%s="%s"' % (m.group(1), targets.get(m.group(2), m.group(2))), xml)


def restore_memo(edited, original, pairs=None, stream=sys.stdout):
    """원작자 메모 되살리기 (영상의학 회신 §5 — 대본 덱 5개). 편집본 화면마다 '기존 메모' 구역(표지 뒤 전부)을 지우고 원본 화면의
    노트 문단을 XML 그대로 붙인다(copy_note_paragraphs, 하이퍼링크 rId 재매핑). 대본·참고 구역과 표지는 그대로. 표지가 없으면
    NOTES_SEP_MEMO 를 붙인 뒤 복사. pairs = [(편집 slide, 원본 slide)] 또는 [(편집 slide, 원본 덱, 원본 slide)](여러 원본),
    없으면 화면 순서대로. 반환: 복사한 문단 수."""
    if pairs is None:
        oa = [s for s, _, _ in original.order() if s]; ob = [s for s, _, _ in edited.order() if s]
        pairs = list(zip(ob, oa))
    total = 0
    for pr in pairs:
        sb, O, sa = (pr[0], original, pr[1]) if len(pr) == 2 else pr
        if not any(q['text'].strip() for q in O.notes_paragraphs(sa)):
            continue
        paras = edited.notes_paragraphs(sb)
        k = next((i for i, q in enumerate(paras) if _is_memo_sep(q['text'])), None)
        b = edited._notes_body(sb)
        if b is None:
            edited.set_notes(sb, ['']); b = edited._notes_body(sb); paras = edited.notes_paragraphs(sb)
        p, x, a, e = b
        if k is None:
            x = x[:e] + notes_xml([NOTES_SEP_MEMO]) + x[e:]
        else:
            x = x[:paras[k]['end']] + x[e:]
        open(p, 'w', encoding='utf8').write(x)
        total += edited.copy_note_paragraphs(O, sa, sb)
    print('원작자 메모 되살림: %d화면, %d문단' % (len(pairs), total), file=stream)
    return total


_TEMP_DIRS = []


def _default_out(pptx, suffix):
    """-o 없을 때 저장 자리: 입력 옆, 입력 폴더가 읽기 전용이면(/mnt/user-data/uploads) /mnt/user-data/outputs → 현재 폴더 (v16.10, X1)."""
    name = os.path.splitext(os.path.basename(pptx))[0] + suffix + '.pptx'
    for d in (os.path.dirname(os.path.abspath(pptx)), '/mnt/user-data/outputs', os.getcwd()):
        if os.path.isdir(d) and os.access(d, os.W_OK):
            return os.path.join(d, name)
    return os.path.join(tempfile_dir('out'), name)


def tempfile_dir(tag):
    """임시 추출 폴더. v16.9.2 (발표 Y1): 만든 폴더를 기록해 두고 cleanup_temp() / 프로세스 종료 때 지운다 — 60 MB 덱을 몇 번
    비교하자 /tmp 에 dk_* 61개(8.3 GB)가 쌓여 '공간 없음' 으로 멈췄다."""
    import tempfile, atexit
    d = tempfile.mkdtemp(prefix='dk_%s_' % tag)
    if not _TEMP_DIRS:
        atexit.register(cleanup_temp)
    _TEMP_DIRS.append(d)
    return d


def cleanup_temp(keep=()):
    """tempfile_dir 로 만든 폴더를 지운다(keep 에 든 것은 남긴다)."""
    for d in list(_TEMP_DIRS):
        if d not in keep:
            shutil.rmtree(d, ignore_errors=True)
            _TEMP_DIRS.remove(d)


# ----------------------------------------------------------------------------
# v16.9: 한→영 치환 오염 (H&N P1)
# ----------------------------------------------------------------------------

_KO_PARTICLES = ('은', '는', '이', '가', '을', '를', '의', '에', '로', '으로', '와', '과', '도', '만', '까지', '부터', '에서',
                 '에게', '처럼', '보다', '이다', '입니다', '이고', '이며', '이면', '이라', '라', '로서', '로써', '상', '형',
                 '되', '된', '될', '돼', '됩', '됐', '됨', '였', '이었', '여야', '이어야', '뿐', '째', '하', '한', '할', '해', '했', '함', '합', '시', '들', '인', '일', '임', '이나', '나',
                 '랑', '이랑', '며', '고', '면', '죠', '요', '적', '측', '쪽')


def check_note_substitution(deck):
    """노트 낭독분에서 한→영 일괄 치환이 단어 안쪽을 바꾼 흔적을 찾는다. [참고] 목록.
    (a) 한글 바로 뒤 영어 3자↑ ('구ecchymosis', '막tongue')  (b) 영어 바로 뒤 조사·어미가 아닌 한글 ('vessel성')
    ((c) 영어 두 단어 붙음 규칙은 v16.17 에서 뺐다 — 아래 주석) 띄어쓴 채 뜻만 바뀐 치환은 못 잡는다 —
    치환 전 원문이 있으면 작업 쪽에서 '사전 키가 더 긴 한글 단어 안에서 걸린 자리' 를 원문에서 찾을 것(DECK_SPEC §6)."""
    out = []
    for sn in deck.slide_numbers():
        txt = ' '.join(_spoken_notes(deck.notes(sn)))
        hits = []
        hits += [m.group(0) for m in re.finditer(r'[가-힣][A-Za-z]{3,}', txt)]
        for m in re.finditer(r'([A-Za-z]{3,})([가-힣]+)', txt):
            word, ko = m.group(1), m.group(2)
            if ko.startswith(_KO_PARTICLES):
                continue
            # v16.23 (발표 B1 철회, 사용자 09-26): 영어 낱말 뒤 조사는 한국어로 읽은 소리를 기준으로 한다 — segment→세그먼트,
            # point→포인트 는 모음으로 끝나 'segment다' 가 맞다. 철자로는 읽은 소리의 받침을 알 수 없으므로 '다'(서술격)는 잡지 않는다
            if ko.startswith('다'):
                continue
            hits.append(m.group(0))
        # (c) '영어 두 단어 붙음' 규칙은 v16.17 에서 뺐다 — 세 번의 회신에서 실제 영어 단어를 잘못 잡았고(intracranial·
        # epiglottic·transformation, methylcellulose, cholestasis), 예외 접두사 목록만 늘었다. 맞게 잡은 것은 H&N 의
        # vesselenhancement 하나였고, 그 원인(부분 문자열 치환)은 이제 영상의학 치환 쪽 규칙(작업규약 §5.3)이 막는다
        if hits:
            out.append('[참고] slide%d 노트에 한→영 치환 흔적 의심: %s' % (sn, ', '.join(sorted(set(hits))[:6])))
    return out


def safe_replace_terms(text, mapping):
    """한→영 용어 치환을 **단어 경계**를 지켜서 한다 (v16.9, H&N 예방 규칙). 키 앞 글자가 한글이면 치환하지 않고,
    뒤 글자가 한글이면 조사·어미일 때만 치환한다. 긴 키부터 적용. 반환 (새 텍스트, [(키, 위치)...] 건너뛴 자리)."""
    skipped = []
    for k in sorted(mapping, key=len, reverse=True):
        v = mapping[k]; pos = 0; out = []
        for m in re.finditer(re.escape(k), text):
            before = text[m.start() - 1] if m.start() else ''
            after = text[m.end():m.end() + 3]
            if re.match(r'[가-힣]', before) or (after[:1] and re.match(r'[가-힣]', after[:1]) and not after.startswith(_KO_PARTICLES)):
                skipped.append((k, m.start())); continue
            out.append(text[pos:m.start()]); out.append(v); pos = m.end()
        out.append(text[pos:]); text = ''.join(out)
    return text, skipped


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description='영상의학 PPTX 작업 툴킷')
    sub = ap.add_subparsers(dest='cmd', required=True)

    a = sub.add_parser('audit'); a.add_argument('pptx')
    u = sub.add_parser('unpack'); u.add_argument('pptx'); u.add_argument('-o', default=None)
    m = sub.add_parser('media'); m.add_argument('pptx'); m.add_argument('-o', default='media')
    r = sub.add_parser('render'); r.add_argument('pptx'); r.add_argument('-o', default='png')
    r.add_argument('--no-autofit', action='store_true', help='자동 맞춤을 끈 사본을 렌더 — Google Slides 등에서의 모양 (v16.10)')
    pk = sub.add_parser('pack'); pk.add_argument('workdir'); pk.add_argument('-o', required=True)
    pk.add_argument('--original', default=None)
    v = sub.add_parser('verify'); v.add_argument('pptx'); v.add_argument('--original', default=None)
    df = sub.add_parser('diff', help='원본 대비 비교: 슬라이드 글·노트 문단 보존/서식 변경/사라짐 (v16.9)')
    df.add_argument('original'); df.add_argument('edited')
    df.add_argument('--map', help='매핑표 markdown (| 편집 화면 | 출처 원본 화면 | 제목 | 의도한 수정 |)')
    df.add_argument('--src', action='append', default=[], help='매핑표 출처 이름=경로 (예: "2025 덱=y2025.pptx"). 없는 이름은 original')
    df.add_argument('--match-text', action='store_true', help='슬라이드 글이 같은 원본 화면을 찾아 짝짓는다')
    df.add_argument('--memo-only', action='store_true', help='원본 노트의 기존 메모 구역만 센다 — 판끼리 비교용 (v16.9.2)')
    rm = sub.add_parser('restore-memo', help='원작자 메모를 원본 노트 문단으로 되살린다 (v16.9)')
    rm.add_argument('edited'); rm.add_argument('--original', required=True); rm.add_argument('-o', required=True)
    rm.add_argument('--map', help='매핑표 — 없으면 화면 순서')
    rm.add_argument('--src', action='append', default=[], help='매핑표 출처 이름=경로 (--match-text 와 함께면 경로만 줘도 된다)')
    rm.add_argument('--match-text', action='store_true', help='원본·--src 덱들에서 슬라이드 글이 같은 화면을 찾아 짝짓는다')
    ba = sub.add_parser('bake-autofit', help='자동 맞춤 비율을 실제 글자 크기·줄 간격으로 적어 넣는다 (v16.10)')
    ba.add_argument('pptx'); ba.add_argument('--screens', required=True, help='화면 번호: 2 또는 2,5 또는 2-4'); ba.add_argument('-o', default=None)
    af = sub.add_parser('apply-fixes', help='`## 본문 수정` 표를 한 곳씩 적용하고 결과 표를 낸다 (v16.9)')
    af.add_argument('pptx'); af.add_argument('--fixes', required=True); af.add_argument('-o', default=None); af.add_argument('--dry-run', action='store_true')
    nn = sub.add_parser('normalize-notes', help='노트를 현행 규격으로: 낭독 부분 태그를 참고로, 옛 표지를 새 표지로 (v16.9)')
    nn.add_argument('pptx'); nn.add_argument('-o', default=None); nn.add_argument('--dry-run', action='store_true')
    l = sub.add_parser('lint'); l.add_argument('pptx'); l.add_argument('--theme', default=DEFAULT_THEME)
    l.add_argument('--deck-kind', default=None, help='덱 종류: journal review / case review / quiz review / pathology review / anatomy seminar / book review / 전평 … (v16.7.3)')
    rs = sub.add_parser('restyle'); rs.add_argument('pptx'); rs.add_argument('-o', required=True)
    rs.add_argument('--theme', default=DEFAULT_THEME)
    pl = sub.add_parser('plan'); pl.add_argument('kind', choices=list(SKELETON))
    pl.add_argument('--cases', nargs='+', default=['Case 1'])
    pl.add_argument('--minutes', type=int, default=None, help='발표 시간 예산(분)')
    po = sub.add_parser('polish'); po.add_argument('pptx'); po.add_argument('-o', required=True)
    po.add_argument('--font', default=DEFAULT_FONT, choices=list(FONT_PROFILES))
    po.add_argument('--audience', choices=('internal', 'external'), default=None, help='내부 발표는 환자 정보 검사 생략, 외부는 [!] (v16.9)')
    ex = sub.add_parser('handout'); ex.add_argument('pptx'); ex.add_argument('-o', required=True)
    fl = sub.add_parser('fit-layout', help='밀집 화면 배치(v16.34, 발표 K16·K17): 제목 띠·반복 제목 빼기·옆 배치·본문 글자·그림+주석 비율·이름표')
    fl.add_argument('pptx'); fl.add_argument('-o', required=True); fl.add_argument('--screens', required=True); fl.add_argument('--dry-run', action='store_true')
    fl.add_argument('--title-min', type=int, default=20); fl.add_argument('--body-min', type=int, default=14); fl.add_argument('--body-max', type=int, default=None)
    fl.add_argument('--max-upscale', type=float, default=1.5); fl.add_argument('--min-scale', type=float, default=0.5)
    fl.add_argument('--gap', type=float, default=0.2, help='제목 띠와 본문 간격(인치, v16.34 기본 0.2 — K17 F3)')
    fl.add_argument('--text-margin', type=float, default=1.1, help='추정 글 높이 여유(K17 F2)')
    fl.add_argument('--arrange', choices=('auto', 'keep', 'side'), default='auto', help='side = 글 왼쪽·그림 오른쪽(K17 S2·S3)')
    fl.add_argument('--drop-repeat-titles', choices=('off', 'overlap', 'all'), default='off',
                    help='앞 화면과 제목 글이 같으면 제목·띠를 뺀다 — all: 겹침과 상관없이(K17 S1, 사용자 09-28), overlap: 안 들어갈 때만')
    fl.add_argument('--like', type=int, default=None, help='기준 화면 — 이름표 자리와 본문 크기 상한(--body-max 가 없을 때)')
    fl.add_argument('--render', default=None, help='결과 화면을 PNG 로(이 폴더에) — LibreOffice 가 있는 곳에서')
    hl = sub.add_parser('adopt-house-look', help='가져온 슬라이드의 흰 글자·글상자 제목을 기준 덱 모양으로(v16.31, 발표 K12)')
    hl.add_argument('pptx'); hl.add_argument('-o', required=True); hl.add_argument('--screens', required=True); hl.add_argument('--dry-run', action='store_true')
    hl.add_argument('--recolor', default='', help='테마 글자색으로 바꿀 색(쉼표 — 16진수·white/black 같은 이름·bg1/tx1 같은 테마 색, v16.33 K15-1)')
    hl.add_argument('--no-auto-light', action='store_true', help='밝은 색 자동 지우기를 끈다 — 목록에 없는 색은 강조로 남긴다(v16.33)')
    hl.add_argument('--darken-low-contrast', action='store_true', help='배경 대비가 모자란 강조색만 같은 계열의 진한 색으로(v16.33)')
    hl.add_argument('--min-contrast', type=float, default=3.0)
    hl.add_argument('--title-band', action='store_true', help='제목 띠 + 그 아래 본문(K14): 띠 높이는 --band-height 또는 --like 규격')
    hl.add_argument('--band-height', type=float, default=None); hl.add_argument('--like', type=int, default=None)
    hl.add_argument('--push-content', action='store_true', help='띠 아래 간격보다 위의 상자·그림을 한 덩어리로 내린다(§0-C 예외 — 지정한 화면만)')
    hl.add_argument('--drop-title-rule', action='store_true', help='띠 안 가로선(옛 제목 밑줄) 하나를 지운다 — 둘 이상이면 알림')
    hl.add_argument('--gap', type=float, default=0.1); hl.add_argument('--min-pt', type=int, default=12)
    bm = sub.add_parser('box-to-memo', help='글상자를 노트 기존 메모 구역으로 옮기고 지운다(v16.37, 발표 K21)')
    bm.add_argument('pptx'); bm.add_argument('-o', required=True); bm.add_argument('--screens', required=True); bm.add_argument('--match', required=True)
    bm.add_argument('--dry-run', action='store_true')
    tb = sub.add_parser('title-bands', help='제목 띠가 필요 높이보다 낮으면 키운다 — Google Slides 안전(v16.28, 발표 K8)')
    tb.add_argument('pptx'); tb.add_argument('-o', required=True); tb.add_argument('--screens', default=None); tb.add_argument('--dry-run', action='store_true')
    tb.add_argument('--shrink-bottom-inset', nargs='?', const=0.1, type=float, default=None,
                    help='겹쳐서 못 키울 때 아래 여백만 줄여(기본 0.1") 아래 내용 위까지(v16.29, 발표 K9)')
    tb.add_argument('--balance', action='store_true', help='채운 제목 띠를 규격 높이(아래 내용 − 간격까지)로, 위·아래 여백을 같게(v16.30, 발표 K10) — --like 필요')
    tb.add_argument('--like', type=int, default=None, help='--balance 의 규격을 배울 기준 화면(원래 제목 모양)')
    tb.add_argument('--gap', type=float, default=0.1, help='--balance: 띠와 아래 내용 사이 간격(인치)')
    pm = sub.add_parser('protect-memo', help='표지 없는 원작자 노트를 기존 메모 구역으로 감싼다(v16.27, 발표 P2)')
    pm.add_argument('pptx'); pm.add_argument('-o', required=True); pm.add_argument('--screens', default=None, help='화면 번호(예: 3,5-9). 없으면 전부')
    fc = sub.add_parser('fit-corner-boxes', help='가장자리에 붙은 글상자를 붙은 쪽 고정으로 글에 맞게 키운다(v16.27, 발표 K7)')
    fc.add_argument('pptx'); fc.add_argument('-o', required=True); fc.add_argument('--pad', type=float, default=0.15)
    fc.add_argument('--tol', type=float, default=0.02, help='가장자리에 붙었다고 볼 거리(인치)'); fc.add_argument('--dry-run', action='store_true')
    wl = sub.add_parser('widen-labels', help='채우기·테두리 없는 이름표 글상자의 폭을 넓힌다(정렬 쪽 모서리 고정, v16.26)')
    wl.add_argument('pptx'); wl.add_argument('-o', required=True); wl.add_argument('--pattern', required=True, help='글 전체가 맞을 정규식, 예: "\\(R\\d [^)]*\\)"')
    wl.add_argument('--min-width', type=float, default=2.0); wl.add_argument('--dry-run', action='store_true')
    pg = sub.add_parser('purge', help='순서 밖 슬라이드·노트·고아 미디어 제거 후 저장 (v16.6.1)'); pg.add_argument('pptx'); pg.add_argument('-o', required=True)
    ti = sub.add_parser('titles', help='제목 띠 넘침 점검, --like 로 규격을 배워 --screens 를 맞춘다 (v16.9)')
    ti.add_argument('pptx')
    ti.add_argument('--like', type=int, default=None, help='템플릿을 지킨 화면 번호 — 그 화면과 같은 레이아웃의 제목에서 규격을 배운다')
    ti.add_argument('--base', default=None, help='--like 화면이 있는 덱(기본: 이 덱)')
    ti.add_argument('--screens', default=None, help='규격과 대조·적용할 화면(예: 30,43 또는 30-43). 옮겨 온 화면만 준다')
    ti.add_argument('--apply', action='store_true'); ti.add_argument('--adopt-box', action='store_true', help='글상자 제목도 placeholder 로 바꾼다')
    ti.add_argument('-o', default=None)
    st = sub.add_parser('settext', help='본문·노트 텍스트 안전 치환 (정확히 1회 매치일 때만, v16.6)')
    st.add_argument('pptx'); st.add_argument('--slide', type=int, required=True, help='xml 번호(slideN.xml 의 N). 화면 번호가 아니다')
    st.add_argument('--old', required=True); st.add_argument('--new', default='')
    st.add_argument('--shape'); st.add_argument('--notes', action='store_true')
    st.add_argument('--delete-para', action='store_true'); st.add_argument('--dry-run', action='store_true')
    st.add_argument('--whole', action='store_true', help='글 조각 전체가 --old 인 곳만 (v16.15)')
    st.add_argument('-o', help='저장 경로(기본: 원본 옆 *_edit.pptx). 저장 후 verify --original 자동 실행')
    cc = sub.add_parser('crosscheck'); cc.add_argument('pptx')
    cc.add_argument('--sources', nargs='+', required=True)
    cc.add_argument('--notes', action='store_true', help='발표자 노트의 수치도 대조 (v16.6)')
    lo = sub.add_parser('locate'); lo.add_argument('--sources', nargs='+', required=True)
    lo.add_argument('values', nargs='+')
    sy = sub.add_parser('sync'); sy.add_argument('pptx')
    ov = sub.add_parser('overflow'); ov.add_argument('pptx')
    ov.add_argument('--headroom', type=float, default=None, help='필요 높이가 상자의 (1-headroom) 을 넘으면 [참고]. 예 0.15')
    ov.add_argument('--font-path', default=None, help='TTF 파일 경로. 있으면 실제 글자폭으로 줄 수를 잰다 (v16.6). 예 /usr/share/fonts/.../Lato-Regular.ttf')

    al = sub.add_parser('align'); al.add_argument('pptx')
    mc = sub.add_parser('mapcheck'); mc.add_argument('pptx')
    mc.add_argument('--claims', required=True)
    mc.add_argument('--nums', action='store_true')
    mc.add_argument('--to-sldid', metavar='OUT_JSON', help='slide:N 사이트를 slide@ID 로 바꿔 저장 (v16.7)')
    mr = sub.add_parser('mapreport'); mr.add_argument('pptx')
    mr.add_argument('--claims', required=True)
    mg = sub.add_parser('mapgraph'); mg.add_argument('--claims', required=True)
    im = sub.add_parser('impact'); im.add_argument('--claims', required=True)
    im.add_argument('ids', nargs='+')
    mf = sub.add_parser('mapfreeze'); mf.add_argument('pptx')
    mf.add_argument('--claims', required=True); mf.add_argument('-o', required=True)
    ms = sub.add_parser('mapstale'); ms.add_argument('pptx')
    ms.add_argument('--claims', required=True)
    for _p in (mf, ms):
        _p.add_argument('--sources', default=None, help='근거 원문 폴더(교과서 분할·문헌 보관소) — claims 의 sources 칸 원문 바뀜도 본다 (v16.41)')
    ex2 = sub.add_parser('extract'); ex2.add_argument('pptx'); ex2.add_argument('-o', required=True)
    ex2.add_argument('--min-score', type=int, default=2)
    sc = sub.add_parser('scaffold'); sc.add_argument('--claims', required=True)
    args = ap.parse_args()
    if args.cmd == 'audit':
        Deck.open(args.pptx).audit()
    elif args.cmd == 'unpack':
        d = Deck.open(args.pptx, args.o)
        print('언팩 완료: %s' % d.dir)
    elif args.cmd == 'media':
        extract_media(args.pptx, args.o)
    elif args.cmd == 'render':
        for f in render(args.pptx, args.o, no_autofit=args.no_autofit):
            print(f)
    elif args.cmd == 'pack':
        Deck(args.workdir).save(args.o)
        ok = validate(args.o, args.original)     # v16.42 (코드 리뷰 ⑮): 결과를 버리지 않는다 — 실패면 1, 검증 못 함(None)은 0
        print('저장: %s / verify%s: %s' % (args.o, ' --original' if args.original else '', vword(ok)))
        sys.exit(1 if ok is False else 0)
    elif args.cmd == 'diff':
        srcs = dict(x.split('=', 1) for x in args.src)
        r = diff_decks(args.original, args.edited, mapping=parse_screen_map(args.map) if args.map else None,
                       sources=srcs, match_text=args.match_text, memo_only=args.memo_only)
        sys.exit(1 if any(f or g for _, f, g in r['notes'].values()) or r['sldnum_lost'] or r['unintended'] or r['unmatched'] else 0)
    elif args.cmd == 'bake-autofit':
        dk = Deck.open(args.pptx); order = [s for s, _, _ in dk.order() if s]
        scr = sorted(_parse_screens(args.screens, len(order)))     # v16.44: 따로 풀던 것 — 0 이 마지막 화면이 됐다
        for k in scr:
            print('화면 %d: 자동 맞춤 비율을 적어 넣은 상자 %d개' % (k, dk.bake_autofit(order[k - 1])))
        out = args.o or _default_out(args.pptx, '_baked'); dk.save(out)
        print('저장: %s / verify --original: %s' % (out, vword(validate(out, args.pptx))))
    elif args.cmd == 'apply-fixes':
        dk = Deck.open(args.pptx)
        res = apply_fixes(dk, parse_fixes(args.fixes), dry_run=args.dry_run)
        if not args.dry_run:
            out = args.o or _default_out(args.pptx, '_fixed'); dk.save(out)
            print('저장: %s / verify --original: %s' % (out, vword(validate(out, args.pptx))))
        sys.exit(0 if all(r[3] == '적용' for r in res) else 1)
    elif args.cmd == 'normalize-notes':
        dk = Deck.open(args.pptx); tot = {'moved': 0, 'sep': 0}; shown = 0
        for sn in dk.slide_numbers():
            r = normalize_notes(dk, sn, dry_run=args.dry_run)
            tot['moved'] += r['moved']; tot['sep'] += r['sep']
            if r['moved'] and shown < 5:
                print('  %s: 태그 문장 %d개 → 참고 (예: %s)' % (dk.label(sn), r['moved'], ' / '.join(x[:60] for x in r['samples']))); shown += 1
        print('태그 문장 %d개를 참고로, 표지 %d개를 새 형식으로%s' % (tot['moved'], tot['sep'], ' (dry-run)' if args.dry_run else ''))
        left = [dk.label(sn) for sn in dk.slide_numbers() if NOTE_TAGS.search(' '.join(_spoken_notes(dk.notes(sn))))]
        print('낭독 부분에 남은 태그: %s' % (left[:10] or '없음'))
        if not args.dry_run:
            out = args.o or _default_out(args.pptx, '_notes'); dk.save(out)
            print('저장: %s / verify --original: %s' % (out, vword(validate(out, args.pptx))))
    elif args.cmd == 'restore-memo':
        E = Deck.open(args.edited); O = Deck.open(args.original, tempfile_dir('rmo'))
        srcs = {k: Deck.open(v, tempfile_dir('rms')) for k, v in ((x.split('=', 1) if '=' in x else (x, x)) for x in args.src)}
        pairs = None
        if args.match_text:
            pairs, miss = match_sources_by_text(E, [O] + list(srcs.values()))
            print('글로 짝지음: %d화면, 짝 없음 %d화면 %s' % (len(pairs), len(miss), miss[:20]))
        elif args.map:
            ob = [s for s, _, _ in E.order() if s]
            pairs = []
            for es, label, os_, _ in parse_screen_map(args.map):
                D = srcs.get(label, O); od = [s for s, _, _ in D.order() if s]
                if es <= len(ob) and os_ <= len(od):
                    pairs.append((ob[es - 1], D, od[os_ - 1]))
        restore_memo(E, O, pairs)
        E.save(args.o)
        if args.match_text:
            print('verify --original: %s' % (vword(validate(args.o, args.edited))))
            sys.exit(0)
        r = diff_decks(args.original, args.o, mapping=parse_screen_map(args.map) if args.map else None,
                       sources={k: v for k, v in (x.split('=', 1) for x in args.src)})
        print('verify --original: %s' % (vword(validate(args.o, args.edited))))
        sys.exit(1 if any(g for _, _, g in r['notes'].values()) else 0)
    elif args.cmd == 'verify':
        ok = validate(args.pptx, args.original)
        print('verify%s: %s' % (' --original' if args.original else '', vword(ok)))   # v16.9.2 (Y3) · v16.38 None = 검증 못 함
        sys.exit(1 if ok is False else 0)
    elif args.cmd == 'lint':
        lint(Deck.open(args.pptx, theme=args.theme), deck_kind_override=args.deck_kind)
    elif args.cmd == 'restyle':
        dk = Deck.open(args.pptx, theme=args.theme)
        restyle(dk)
        dk.save(args.o)
        ok = validate(args.o, args.pptx)
        print('저장: %s / verify --original: %s' % (args.o, vword(ok)))
        sys.exit(1 if ok is False else 0)
    elif args.cmd == 'plan':
        plan(args.kind, args.cases, minutes=args.minutes)
    elif args.cmd == 'polish':
        dk = Deck.open(args.pptx)
        r = polish(dk, args.font, audience=args.audience)
        if not r['text_intact']:            # v16.42: 경고만 하고 저장하던 것 — 글자가 바뀌면 쓰지 않고 멈춘다
            print('[멈춤] polish 가 글자를 바꿨다 — %s 를 저장하지 않았다' % args.o)
            sys.exit(1)
        dk.save(args.o)
        ok = validate(args.o, args.pptx)
        print('저장: %s / verify --original: %s' % (args.o, vword(ok)))
        sys.exit(1 if ok is False else 0)
    elif args.cmd == 'handout':
        print(export_notes(Deck.open(args.pptx), args.o))
    elif args.cmd == 'fit-layout':
        dk = Deck.open(args.pptx, tempfile_dir('fl')) if args.dry_run else Deck.open(args.pptx); order = [s for s, _, _ in dk.order() if s]
        ttl = {}
        for pos, sn in enumerate(order, 1):
            ti = _title_info(dk, sn)
            ttl[pos] = ' '.join(ti['paras']).strip() if ti and ti['kind'] == 'ph' else ''
        lab = _label_spot(dk, order[args.like - 1]) if args.like else None
        bmax = args.body_max or (_body_pt_of(dk, order[args.like - 1]) if args.like else None)
        for pos in sorted(_parse_screens(args.screens, len(order))):
            same = bool(ttl.get(pos)) and ttl.get(pos) == ttl.get(pos - 1)
            kw = dict(title_min=args.title_min, body_min=args.body_min, body_max=bmax, max_up=args.max_upscale, min_scale=args.min_scale,
                      gap=args.gap, text_margin=args.text_margin, arrange=args.arrange, label_pos=lab)
            if args.drop_repeat_titles == 'all' and same:
                res = fit_layout(dk, order[pos - 1], drop_title=True, **kw)
            else:
                res = fit_layout(dk, order[pos - 1], **kw)
                if res and res[0].startswith('[!]') and args.drop_repeat_titles == 'overlap' and same:
                    res = fit_layout(dk, order[pos - 1], drop_title=True, **kw)
            for c in res:
                print('화면 %d: %s' % (pos, c))
        target = os.path.join(tempfile_dir('flo'), 'fit.pptx') if args.dry_run else args.o
        dk.save(target)
        if args.render:
            try:
                render(target, args.render)
                print('렌더 → %s' % args.render)
            except Exception as e:
                print('[참고] 렌더 못 함(%s) — LibreOffice 가 있는 곳에서' % type(e).__name__)
        print('(dry-run — 저장 안 함)' if args.dry_run else '→ %s' % args.o)
    elif args.cmd == 'adopt-house-look':
        # dry-run 도 사본 덱에 실제로 해 본다(제목을 옮긴 뒤의 띠·본문을 보려면) — 저장만 하지 않는다
        dk = Deck.open(args.pptx, tempfile_dir('ahl')) if args.dry_run else Deck.open(args.pptx); order = [s for s, _, _ in dk.order() if s]
        rec = [c.strip() for c in args.recolor.split(',') if c.strip()]
        bprof = title_profile(dk, like=args.like) if (args.title_band and args.like) else None
        if args.title_band and not (args.band_height or bprof):
            sys.exit('--title-band 에는 --band-height 인치 또는 --like 기준 화면이 필요하다')
        for pos in sorted(_parse_screens(args.screens, len(order))):
            for c in adopt_house_look(dk, order[pos - 1], recolor=rec, auto_light=not args.no_auto_light,
                                      darken=args.darken_low_contrast, min_contrast=args.min_contrast):
                print('화면 %d: %s' % (pos, c))
            if args.title_band:
                for c in title_block(dk, order[pos - 1], band_h=args.band_height, prof=bprof, gap_in=args.gap, drop_rule=args.drop_title_rule,
                                     push=args.push_content, min_pt=args.min_pt):
                    print('화면 %d: %s' % (pos, c))
        if not args.dry_run:
            dk.save(args.o)
        print('(dry-run — 저장 안 함)' if args.dry_run else '→ %s' % args.o)
    elif args.cmd == 'box-to-memo':
        dk = Deck.open(args.pptx); order = [s for s, _, _ in dk.order() if s]; bad = 0
        for pos in sorted(_parse_screens(args.screens, len(order))):
            try:
                nm, t, b0, b1 = dk.box_to_memo(order[pos - 1], args.match, dry_run=args.dry_run)
                print('화면 %d: "%s" → 기존 메모 끝("%s") · 메모 %d → %d줄' % (pos, nm, t[:60], b0, b1))
            except ValueError as e:
                bad += 1; print('[!] 화면 %d: %s' % (pos, e))
        if not args.dry_run and not bad:
            dk.save(args.o)
        print('(dry-run — 저장 안 함)' if args.dry_run else ('[!] 멈춤 — 저장 안 함' if bad else '→ %s' % args.o))
        sys.exit(1 if bad else 0)
    elif args.cmd == 'title-bands':
        dk = Deck.open(args.pptx); order = [s for s, _, _ in dk.order() if s]
        want = _parse_screens(args.screens, len(order)) if args.screens else set(range(1, len(order) + 1))
        n_ch = n_sk = 0
        bprof = None
        if args.balance:
            if not args.like:
                sys.exit('--balance 에는 --like 기준 화면(원래 제목 모양)이 필요하다')
            bprof = title_profile(dk, like=args.like)
            print('규격(화면 %d 의 무리 — 위 여백 %.2f"): 줄 수별 높이 %s' % (args.like, bprof['group'], {k: round(v / 914400, 2) for k, v in bprof['h_by_lines'].items()}))
        for pos, sn in enumerate(order, 1):
            if pos not in want:
                continue
            for c in (balance_title_band(dk, sn, bprof, gap_in=args.gap, dry_run=args.dry_run) if args.balance else
                      raise_title_band(dk, sn, dry_run=args.dry_run, shrink_bottom=args.shrink_bottom_inset)):
                print('화면 %d: %s' % (pos, c))
                if c.startswith('[!]'):
                    n_sk += 1
                elif not c.startswith('[참고]'):
                    n_ch += 1
        if not args.dry_run:
            dk.save(args.o)
        print('제목 띠 키움 %d · 바꾸지 않음 %d%s' % (n_ch, n_sk, ' (dry-run — 저장 안 함)' if args.dry_run else ' → %s' % args.o))
    elif args.cmd == 'protect-memo':
        dk = Deck.open(args.pptx); order = [s for s, _, _ in dk.order() if s]
        want = _parse_screens(args.screens, len(order)) if args.screens else set(range(1, len(order) + 1))
        done, has, empty = [], 0, 0
        for pos, sn in enumerate(order, 1):
            if pos not in want:
                continue
            if dk.protect_memo(sn):
                done.append(pos)
            elif any(t.strip() for t in dk.notes(sn)):
                has += 1
            else:
                empty += 1
        dk.save(args.o)
        print('감싼 화면 %d · 이미 구조가 있거나 표지 있음 %d · 빈 노트 %d → %s' % (len(done), has, empty, args.o))
        if done:
            print('감싼 화면: %s' % ', '.join(map(str, done[:40])) + (' …' if len(done) > 40 else ''))
    elif args.cmd == 'fit-corner-boxes':
        dk = Deck.open(args.pptx); order = [s for s, _, _ in dk.order() if s]; n_ch = n_sk = 0
        for pos, sn in enumerate(order, 1):
            for r in dk.fit_corner_boxes(sn, tol_in=args.tol, pad=args.pad, dry_run=args.dry_run):
                if r['what'] == '바꿈':
                    n_ch += 1
                    print('화면 %d "%s" %s → %s%s' % (pos, r['name'], r['old'], r['new'], ('  [참고] 겹침: %s' % ', '.join(r['overlap'])) if r['overlap'] else ''))
                else:
                    n_sk += 1; print('[참고] 화면 %d "%s" %s' % (pos, r['name'], r['what']))
        if not args.dry_run:
            dk.save(args.o)
        print('구석 글상자 맞춤 %d · 건너뜀 %d%s' % (n_ch, n_sk, ' (dry-run — 저장 안 함)' if args.dry_run else ' → %s' % args.o))
    elif args.cmd == 'widen-labels':
        dk = Deck.open(args.pptx); order = [s for s, _, _ in dk.order() if s]; n_ch = n_sk = 0
        for pos, sn in enumerate(order, 1):
            for nm, txt, a, b, what in dk.widen_label(sn, pattern=args.pattern, min_width_in=args.min_width, dry_run=args.dry_run):
                if what == '바꿈':
                    n_ch += 1
                elif what.startswith('건너뜀'):
                    n_sk += 1; print('[참고] 화면 %d "%s" %s — %s' % (pos, nm, txt[:30], what))
        if not args.dry_run:
            dk.save(args.o)
        print('이름표 넓힘 %d · 건너뜀 %d%s' % (n_ch, n_sk, ' (dry-run — 저장 안 함)' if args.dry_run else ' → %s' % args.o))
    elif args.cmd == 'purge':
        dk = Deck.open(args.pptx); r = dk.purge_orphans(); dk.save(args.o)
        print('제거: 슬라이드 %d · 노트 %d · 미디어 %d → %s / verify: %s' % (r['slides'], r['notes'], r['media'], args.o, vword(validate(args.o))))
    elif args.cmd == 'titles':
        dk = Deck.open(args.pptx)
        prof = None
        if args.like:
            prof = title_profile(Deck.open(args.base, tempfile_dir('tb')) if args.base else dk, like=args.like)
            if not prof:
                sys.exit('화면 %d 의 제목이 title placeholder 가 아니다 — 템플릿을 지킨 다른 화면을 --like 로' % args.like)
            print('규격(화면 %d 과 같은 레이아웃 제목 %d개): %s, 줄 수별 높이 %s' % (args.like, prof['n'],
                  '%dpt' % (prof['sz'] // 100) if prof['sz'] else '글자 크기 상속', {k: round(v / 914400, 2) for k, v in prof['h_by_lines'].items()}))
            # v16.29 (발표 K8-b): 규격이 어디서 왔는지 — 줄 수별로 높이를 준 제목(화면·높이·위/아래 여백)과 뺀 제목
            bd = Deck.open(args.base, tempfile_dir('tb2')) if args.base else dk
            pos = {s: k for k, s in enumerate([s for s, _, _ in bd.order() if s], 1)}
            E = 914400.0
            print('  제목 무리(위 여백 → 수): %s · 규격은 %.2f" 무리에서(%s)' % (
                ', '.join('%.2f"→%d' % kv for kv in prof['groups'].items()), prof['group'], '기준 화면의 무리' if args.like else '가장 큰 무리'))
            print('  안쪽 여백 규격(위/아래): %.2f"/%.2f" · 뺀 제목(필요 높이의 90%% 미만) %d개%s' % (
                prof['ins'][2] / E, prof['ins'][3] / E, prof['excluded'],
                (': ' + ', '.join('화면 %s %.2f"<%.2f"' % (pos.get(sn, '?'), h / E, nd / E) for sn, h, nd in prof['excluded_list'][:10])) if prof['excluded_list'] else ''))
            for n, rows in sorted(prof['contrib'].items()):
                from collections import Counter as _C
                dist = _C((round(h / E, 2), round(t / E, 2), round(b / E, 2)) for _, h, t, b in rows)
                print('  %d줄 제목 %d개 — (높이, 위, 아래 여백) 분포: %s · 화면 %s' % (n, len(rows),
                      ', '.join('%s×%d' % (k, v) for k, v in dist.most_common(4)),
                      ', '.join(str(pos.get(sn, '?')) for sn, _, _, _ in rows[:15]) + (' …' if len(rows) > 15 else '')))
        scr = None
        if args.screens:
            scr = sorted(_parse_screens(args.screens, len([s for s, _, _ in dk.order() if s])))   # v16.44
        print('=== 제목 점검 ===')
        bad = check_title_template(dk, prof, screens=scr)
        if args.apply:
            if not (prof and scr):
                sys.exit('--apply 에는 --like 와 --screens 가 필요하다 (다른 사람이 만든 화면까지 바꾸지 않도록)')
            order = [s for s, _, _ in dk.order() if s]
            for k in scr:
                ch = conform_title(dk, order[k - 1], prof, adopt_box=args.adopt_box)
                print('  화면 %d: %s' % (k, ' · '.join(ch) or '변경 없음'))
            out = args.o or _default_out(args.pptx, '_titles')
            dk.save(out)
            print('다시 점검:'); rest = check_title_template(dk, prof, screens=scr)
            print('저장: %s / verify --original: %s' % (out, vword(validate(out, args.pptx))))
            sys.exit(1 if any(x.startswith('[!]') for v in rest.values() for x in v) else 0)
        sys.exit(1 if any(x.startswith('[!]') for v in bad.values() for x in v) else 0)
    elif args.cmd == 'settext':
        dk = Deck.open(args.pptx)
        r = dk.settext(args.slide, args.old, args.new, shape=args.shape, notes=args.notes,
                       delete_para=args.delete_para, dry_run=args.dry_run, whole=args.whole)
        if not r['ok']:
            print('[거부] %s' % r['reason']); sys.exit(1)
        print('%s: %r -> %r%s' % (r['where'], r['before'], r['after'], '  (dry-run)' if args.dry_run else ''))
        if not args.dry_run:
            out = args.o or _default_out(args.pptx, '_edit')
            dk.save(out)
            ok = validate(out, args.pptx)
            print('저장: %s / verify --original: %s' % (out, vword(ok)))
            sys.exit(1 if ok is False else 0)
    elif args.cmd == 'crosscheck':
        crosscheck(Deck.open(args.pptx), args.sources, notes=args.notes)
    elif args.cmd == 'locate':
        locate(args.sources, *args.values)
    elif args.cmd == 'sync':
        check_notes_slide_sync(Deck.open(args.pptx))
    elif args.cmd == 'overflow':
        check_text_overflow(Deck.open(args.pptx), headroom=args.headroom, font_path=args.font_path)


    elif args.cmd == 'align':
        check_notes_alignment(Deck.open(args.pptx))
    elif args.cmd == 'mapcheck':
        dk = Deck.open(args.pptx)
        if args.to_sldid:
            meta, cl = CG.load_claims_full(args.claims)
            n = sites_to_sldid(dk, cl)
            print('사이트 %d개를 sldId 로 변환: %s' % (n, CG.save_claims(args.to_sldid, cl, meta=meta)))
            mapcheck(dk, cl, nums=args.nums)
        else:
            mapcheck(dk, load_claims(args.claims), nums=args.nums)
    elif args.cmd == 'mapreport':
        mapreport(Deck.open(args.pptx), load_claims(args.claims))
    elif args.cmd == 'mapgraph':
        meta_, cl_ = CG.load_claims_full(args.claims)          # v16.43: 맨 위 kind(증례)를 읽는다 — claim_graph 16.6
        probs, _ = mapgraph(cl_, kind=meta_.get('kind'))
        sys.exit(1 if any(not p.startswith('[참고]') for p in probs) else 0)
    elif args.cmd == 'impact':
        impact(load_claims(args.claims), args.ids)
    elif args.cmd == 'mapfreeze':
        meta, cl = CG.load_claims_full(args.claims)          # v16.40 (코드 리뷰 ⑧): 맨 위 칸(refs_maps_applied 등)을 그대로 — 전에는 deck·note 만 남겼다
        mapfreeze(Deck.open(args.pptx), cl, sources=args.sources, stream=sys.stdout)
        print('기록 완료: %s' % save_claims(args.o, cl, meta=meta))   # doc 그래프가 deck 으로 바뀌던 것도 없어진다
    elif args.cmd == 'mapstale':
        r = mapstale(Deck.open(args.pptx), load_claims(args.claims), sources=args.sources)
        sys.exit(1 if (r['changed'] or r['unverified']) else 0)
    elif args.cmd == 'extract':
        dk = Deck.open(args.pptx)
        cands = CG.extract(deck_units(dk), args.min_score)
        save_claims(args.o, cands, os.path.basename(args.pptx), 'extract 초안 — 사람이 확정해야 함')
        print('저장: %s' % args.o)
    elif args.cmd == 'scaffold':
        CG.scaffold(load_claims(args.claims))
if __name__ == '__main__':
    main()
