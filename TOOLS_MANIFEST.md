# TOOLS_MANIFEST — 도구 릴리스 목록 (코드 프로젝트 진본)

**manifest 판: v103 · 릴리스 v2.83 · 2026-10-02**

> **이 파일이 진본 판정 기준이다.** 파일명은 고정(`TOOLS_MANIFEST.md`), 판은 이 줄에만 있다.
> 세트는 전부 삭제 → 전부 재업로드이므로 파일명에 판이 있을 이유가 없고, 파일명 판이 "어느 manifest 가 최신인가"
> 혼선의 원인이었다(v2.0 개정). 실물 검증 결과·배포 사고 이력·릴리스 연혁은 코드 프로젝트 `HISTORY.md`.

## 1. 파일 · 판 · 해시(SHA256 앞 12자리) · 테스트

| 파일 | 판 | 해시 | 테스트 | 크기(바이트) |
|---|---|---|---|---|
| `claim_graph.py` | v16.23 | `e6c4243ade62` | `test_claim_graph.py` 101/101 | 204726 |
| `test_claim_graph.py` | v16.23 동반 | `b40e84e1314b` | — | 164061 |
| `CLAIM_GRAPH.md` | v16.23 | `0410c30e4f71` | — | 65446 |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | `test_toolkit.py` 265/265 (deck 164 + 공용 101, SKIP 0) | 387224 |
| `test_toolkit.py` | v16.51 동반 | `2193bcdf541c` | — | 187647 |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — | 117127 |
| `verify_toolkit.py` | v1.3.8 | `529ce4740c17` | `test_verify_toolkit.py` 47/47 | 40736 |
| `test_verify_toolkit.py` | v1.3.8 동반 | `a1b46f5e0e74` | — | 27919 |
| `handoff.py` | v2.2 | `d8b5305111f4` | `test_handoff.py` 27/27 | 87549 |
| `test_handoff.py` | v2.2 동반 | `7b2a11d55b3a` | — | 45806 |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — | 15351 |
| `textbook.py` | v0.7.2 | `446049895c66` | `test_textbook.py` 32/32 | 60910 |
| `test_textbook.py` | v0.7.2 동반 | `93d75911d86c` | — | 37793 |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — | 13558 |
| `literature.py` | v0.8.6 | `b99516fb6f9a` | `test_literature.py` 17/17 | 48678 |
| `test_literature.py` | v0.8.6 동반 | `ac0646359a75` | — | 39279 |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — | 18917 |
| `REVIEW_PROTOCOL.md` | v7.4 | `8c56bf02ca59` | — | 20411 |
| `CODE_PROJECT_README.md` · `HISTORY.md` · `release.py` | 코드 프로젝트 전용 | (배포하지 않음 — 판·해시는 RELEASE §3 코드 표) | — | — |

해시: `sha256sum <파일> | cut -c1-12`. 판: `python3 -c "import claim_graph; print(claim_graph.__version__)"` (deck_toolkit·verify_toolkit 동일), 문서는 첫 줄.
의존: 테스트 3종 python-docx, test_toolkit 은 python-pptx, test_verify_toolkit·`list_images` 는 Pillow, textbook·test_textbook·literature·test_literature 는 pypdf(v2.22·v2.37). 테스트는 pytest 없이 `python3 test_*.py` 로 돈다.

## 2. 프로젝트별 배포표 — 누가 무엇을 받는가

| 파일 | 저자 | 발표 | 리뷰어 | 교과서 | 문헌 | 코드 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| claim_graph.py · test_claim_graph.py · CLAIM_GRAPH.md | ○ | ○ | ○ | × | × | 진본 |
| deck_toolkit.py · test_toolkit.py · DECK_SPEC.md | × | ○ | × | × | × | 진본 |
| verify_toolkit.py · test_verify_toolkit.py | ○ | × | × | × | × | 진본 |
| handoff.py · test_handoff.py · HANDOFF_FORMAT.md | × | ○ | × | × | × | 진본 |
| textbook.py · test_textbook.py · TEXTBOOK.md | × | × | × | ○ | × | 진본 |
| literature.py · test_literature.py · LITERATURE.md | × | × | × | × | ○ | 진본 |
| REVIEW_PROTOCOL.md | × | × | ○ | × | × | 진본 |
| TOOLS_MANIFEST.md (이 파일) · RELEASE.md (최신 릴리스) | ○ | ○ | ○ | ○ | ○ | 진본 |
| CODE_PROJECT_README.md · HISTORY.md · release.py · GITHUB_README.md · PRIVATE_TERMS.txt | × | × | × | × | × | 진본 |
| **받는 파일 수** | **7** | **11** | **6** | **5** | **5** | 25 |

**코드 프로젝트도 공개 도구는 GitHub 에서 받는다** (v2.18~) — 프로젝트 파일에는 코드 전용 5개만 둔다(`CODE_PROJECT_README.md` 첫머리).

**교과서** (v2.22~): 사람 프로젝트가 아니라 Cowork 가 교과서 폴더에서 돌리는 역할(`selfcheck --role 교과서`). 규약은 `TEXTBOOK.md`.

**문헌** (v2.37~): Cowork 가 병원 컴퓨터에서 논문 원문을 받아 `문헌 보관소` 에 쌓는 역할(`selfcheck --role 문헌`). 규약은 `LITERATURE.md`.

**GitHub 공개 세트** (v2.15~): 저자·발표·리뷰어·교과서·문헌 세트의 합(v2.37: 20개) + `GITHUB_README.md` 를 `README.md` 로. 코드 전용 파일(HISTORY·README·
release.py·PRIVATE_TERMS)은 올리지 않는다. release.py 가 `PRIVATE_TERMS.txt`(사람·기관 이름, 연구 주제어)와 나이/성별·이메일 모양을
찾아 하나라도 있으면 빌드를 멈춘다. 저장소: `github.com/Ananta9701/rad-claude-tools`(공개 — 프로필 비공개와 무관하게 누구나 볼 수 있다).

의존 방향: `deck_toolkit.py` → `claim_graph.py`(import), `handoff.py` → `deck_toolkit.py`(기준 덱 대조 때). `HANDOFF_FORMAT.md` 는 영상의학도
GitHub 에서 읽는다(넘김 문서를 쓰는 쪽). 발표에서 claim_graph 3종을 빼면 deck_toolkit 이 안 돈다.
`remap-refs` 의 입력 refmap 은 `verify_toolkit renumber` 가 만든다(저자에만 둘 다 있음).

## 3. 절차

**세션 시작 확인 3단계** — 셋 다 맞아야 작업 시작. 하나라도 어긋나면 멈추고 사용자에게 알린다.
**한 명령으로**: `python3 claim_graph.py selfcheck --dir /mnt/project --tests` (v20) — 3단계 + 테스트 + 파일 분류를 표로 낸다.
그 표를 수령 확인 도구회신 §1 에 그대로 붙인다. 아래는 그 명령이 하는 일이다.
1. 이 파일 둘째 줄의 **manifest 판**이 `RELEASE.md` 첫 줄의 판과 같은가
2. §1 의 **파일별 판**과 프로젝트 파일의 판 표기(`__version__`, 문서 첫 줄)가 같은가 — 세트가 한 폴더에 있으면 `python3 test_*.py` 가 이 대조를 자동으로 한다(v19)
3. **해시**가 같은가

해시는 "그 판이 맞는가"만 보장하고 "최신인가"는 보장하지 않는다 — 2단계가 구판 잔존을 잡는다.

**배포** — 릴리스마다 `RELEASE.md` 하나(변경·회신 답·프로젝트별 받을 파일 표). 세트(zip)에는 변경 여부와 무관하게
§2 의 그 프로젝트 파일 **전체**를 넣고, 받는 쪽은 그 파일들을 **전부 삭제 → 전부 재업로드**한다. manifest 판이 오르면
네 프로젝트 전부가 세트를 받는다. "manifest 만" 세트, "변경분만" 세트는 내지 않는다(사고 이력은 HISTORY.md).

**프로젝트 파일 정리** — 세트 파일 외의 프로젝트 파일은 각 프로젝트 대화창이 첫 세션에서 목록을 뽑아 세 갈래로 나눈다:
(a) 세트 파일(§2) — 이 manifest 와 대조, (b) 그 프로젝트 고유 산출물(원고·덱·claims·회신·지침) — 그대로,
(c) 삭제 대상 — `TOOLS_MANIFEST_v*.md`, `*_릴리스_v*.md`, `*_배포안내_*`, `*_manifest만_*`, 이미 코드 프로젝트에
보낸 `도구회신` 사본, `__N_` 접미사 파일, 다른 프로젝트 소속 도구(예: 리뷰어의 deck·verify 계열), **현재 덱을 재현하지
못하는 구판 덱 스크립트**(진본은 pptx), **DECK_SPEC 등 규격에 흡수된 문서**(같은 내용이 두 파일에 있으면 규격 쪽이 진본). (c) 는 사용자에게
목록으로 보고하고 사용자가 지운다. 도구는 이 분류를 대신하지 않는다 — 프로젝트 파일 목록은 대화창만 볼 수 있다.

**코드 수정** — 코드 프로젝트에서만. 다른 프로젝트는 `{YYMMDD}_도구회신_{주제}_v{M}.md` 로 보낸다. 덱 전용 스크립트
(`build_*.py`)는 발표 프로젝트가 직접 쓰되 툴킷 함수를 고치거나 새 툴킷 함수를 만들면 회신으로 보낸다.

<!-- prev-release: v2.82 · CLAIM_GRAPH.md=0410c30e4f71;CODE_PROJECT_README.md=f4c839b0b750;DECK_SPEC.md=9ce13600b06d;GITHUB_README.md=c81d29504e46;HANDOFF_FORMAT.md=92fb4a11e9bb;HISTORY.md=6c8d7a9e9418;LITERATURE.md=73b0b00bd897;PRIVATE_TERMS.txt=6e8c2862cf5e;REVIEW_PROTOCOL.md=a186eacaf621;TEXTBOOK.md=4bfff4aa0771;claim_graph.py=e6c4243ade62;deck_toolkit.py=c14c4686c2b1;handoff.py=d8b5305111f4;literature.py=b99516fb6f9a;release.py=d0fe4b4d184a;test_claim_graph.py=b40e84e1314b;test_handoff.py=7b2a11d55b3a;test_literature.py=ac0646359a75;test_textbook.py=93d75911d86c;test_toolkit.py=2193bcdf541c;test_verify_toolkit.py=a1b46f5e0e74;textbook.py=446049895c66;verify_toolkit.py=529ce4740c17 -->
<!-- release-hashes: v2.83 · CLAIM_GRAPH.md=0410c30e4f71;CODE_PROJECT_README.md=f4c839b0b750;DECK_SPEC.md=9ce13600b06d;GITHUB_README.md=c81d29504e46;HANDOFF_FORMAT.md=92fb4a11e9bb;HISTORY.md=101c443bed2b;LITERATURE.md=73b0b00bd897;PRIVATE_TERMS.txt=6e8c2862cf5e;REVIEW_PROTOCOL.md=8c56bf02ca59;TEXTBOOK.md=4bfff4aa0771;claim_graph.py=e6c4243ade62;deck_toolkit.py=c14c4686c2b1;handoff.py=d8b5305111f4;literature.py=b99516fb6f9a;release.py=d0fe4b4d184a;test_claim_graph.py=b40e84e1314b;test_handoff.py=7b2a11d55b3a;test_literature.py=ac0646359a75;test_textbook.py=93d75911d86c;test_toolkit.py=2193bcdf541c;test_verify_toolkit.py=a1b46f5e0e74;textbook.py=446049895c66;verify_toolkit.py=529ce4740c17 -->
