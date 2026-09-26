# TOOLS_MANIFEST — 도구 릴리스 목록 (코드 프로젝트 진본)

**manifest 판: v36 · 릴리스 v2.16 · 2026-09-26**

> **이 파일이 진본 판정 기준이다.** 파일명은 고정(`TOOLS_MANIFEST.md`), 판은 이 줄에만 있다.
> 세트는 전부 삭제 → 전부 재업로드이므로 파일명에 판이 있을 이유가 없고, 파일명 판이 "어느 manifest 가 최신인가"
> 혼선의 원인이었다(v2.0 개정). 실물 검증 결과·배포 사고 이력·릴리스 연혁은 코드 프로젝트 `HISTORY.md`.

## 1. 파일 · 판 · 해시(SHA256 앞 12자리) · 테스트

| 파일 | 판 | 해시 | 테스트 | 크기(바이트) |
|---|---|---|---|---|
| `claim_graph.py` | v15.7 | `be1559a3ace8` | `test_claim_graph.py` 34/34 | 65366 |
| `test_claim_graph.py` | v15.7 동반 | `6946b6a49119` | — | 29032 |
| `CLAIM_GRAPH.md` | v15.7 | `836652b84421` | — | 22073 |
| `deck_toolkit.py` | v16.21 | `f6314d3068bd` | `test_toolkit.py` 169/169 (deck 135 + 공용 34, SKIP 0) | 278858 |
| `test_toolkit.py` | v16.21 동반 | `7f0e7684556e` | — | 111071 |
| `DECK_SPEC.md` | v16.21 | `22ec2cd7906e` | — | 96241 |
| `verify_toolkit.py` | v1.3.3 | `6683437604f9` | `test_verify_toolkit.py` 41/41 | 35925 |
| `test_verify_toolkit.py` | v1.3.3 동반 | `ffd443ae7943` | — | 20655 |
| `handoff.py` | v1.0 | `ac46b281ca9d` | `test_handoff.py` 12/12 | 23006 |
| `test_handoff.py` | v1.0 동반 | `598d9fb30a95` | — | 11731 |
| `HANDOFF_FORMAT.md` | v1.0 | `9df63e3200f7` | — | 6032 |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — | 17531 |
| `CODE_PROJECT_README.md` · `HISTORY.md` · `release.py` | 코드 프로젝트 전용 | (배포하지 않음 — 판·해시는 RELEASE §3 코드 표) | — | — |

해시: `sha256sum <파일> | cut -c1-12`. 판: `python3 -c "import claim_graph; print(claim_graph.__version__)"` (deck_toolkit·verify_toolkit 동일), 문서는 첫 줄.
의존: 테스트 3종 python-docx, test_toolkit 은 python-pptx, test_verify_toolkit·`list_images` 는 Pillow. 테스트는 pytest 없이 `python3 test_*.py` 로 돈다.

## 2. 프로젝트별 배포표 — 누가 무엇을 받는가

| 파일 | 저자 | 발표 | 리뷰어 | 코드 |
|---|:-:|:-:|:-:|:-:|
| claim_graph.py · test_claim_graph.py · CLAIM_GRAPH.md | ○ | ○ | ○ | 진본 |
| deck_toolkit.py · test_toolkit.py · DECK_SPEC.md | × | ○ | × | 진본 |
| verify_toolkit.py · test_verify_toolkit.py | ○ | × | × | 진본 |
| handoff.py · test_handoff.py · HANDOFF_FORMAT.md | × | ○ | × | 진본 |
| REVIEW_PROTOCOL.md | × | × | ○ | 진본 |
| TOOLS_MANIFEST.md (이 파일) · RELEASE.md (최신 릴리스) | ○ | ○ | ○ | 진본 |
| CODE_PROJECT_README.md · HISTORY.md · release.py · GITHUB_README.md · PRIVATE_TERMS.txt | × | × | × | 진본 |
| **받는 파일 수** | **7** | **11** | **6** | 19 |

**GitHub 공개 세트** (v2.15~): 저자·발표·리뷰어 세트의 합(v2.16: 14개) + `GITHUB_README.md` 를 `README.md` 로. 코드 전용 파일(HISTORY·README·
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

<!-- prev-release: v2.15 · CLAIM_GRAPH.md=836652b84421;CODE_PROJECT_README.md=0f2f45890804;DECK_SPEC.md=2ff161dce2a9;GITHUB_README.md=c8f5dfa53ca1;HISTORY.md=d3d83a97996a;PRIVATE_TERMS.txt=4285e1f439fb;REVIEW_PROTOCOL.md=7f6e413d4d48;claim_graph.py=be1559a3ace8;deck_toolkit.py=58d415b5f386;release.py=f2e41ea81fed;test_claim_graph.py=6946b6a49119;test_toolkit.py=37733a678996;test_verify_toolkit.py=ffd443ae7943;verify_toolkit.py=6683437604f9 -->
<!-- release-hashes: v2.16 · CLAIM_GRAPH.md=836652b84421;CODE_PROJECT_README.md=0f2f45890804;DECK_SPEC.md=22ec2cd7906e;GITHUB_README.md=2e2886c5a453;HANDOFF_FORMAT.md=9df63e3200f7;HISTORY.md=5aacc49d52f2;PRIVATE_TERMS.txt=4285e1f439fb;REVIEW_PROTOCOL.md=7f6e413d4d48;claim_graph.py=be1559a3ace8;deck_toolkit.py=f6314d3068bd;handoff.py=ac46b281ca9d;release.py=7ad307268638;test_claim_graph.py=6946b6a49119;test_handoff.py=598d9fb30a95;test_toolkit.py=7f0e7684556e;test_verify_toolkit.py=ffd443ae7943;verify_toolkit.py=6683437604f9 -->
