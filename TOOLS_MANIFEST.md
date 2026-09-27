# TOOLS_MANIFEST — 도구 릴리스 목록 (코드 프로젝트 진본)

**manifest 판: v45 · 릴리스 v2.25 · 2026-09-27**

> **이 파일이 진본 판정 기준이다.** 파일명은 고정(`TOOLS_MANIFEST.md`), 판은 이 줄에만 있다.
> 세트는 전부 삭제 → 전부 재업로드이므로 파일명에 판이 있을 이유가 없고, 파일명 판이 "어느 manifest 가 최신인가"
> 혼선의 원인이었다(v2.0 개정). 실물 검증 결과·배포 사고 이력·릴리스 연혁은 코드 프로젝트 `HISTORY.md`.

## 1. 파일 · 판 · 해시(SHA256 앞 12자리) · 테스트

| 파일 | 판 | 해시 | 테스트 | 크기(바이트) |
|---|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | `test_claim_graph.py` 34/34 | 65974 |
| `test_claim_graph.py` | v15.8.1 동반 | `bcfe1c1e42d6` | — | 29770 |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — | 22160 |
| `deck_toolkit.py` | v16.26 | `cab6d76ae0d8` | `test_toolkit.py` 171/171 (deck 137 + 공용 34, SKIP 0) | 284913 |
| `test_toolkit.py` | v16.26 동반 | `b9405ff4bfd8` | — | 114747 |
| `DECK_SPEC.md` | v16.26 | `ac64f8ec2607` | — | 99492 |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | `test_verify_toolkit.py` 41/41 | 35925 |
| `test_verify_toolkit.py` | v1.3.4 동반 | `aba65de39d87` | — | 20669 |
| `handoff.py` | v1.6 | `267652b14b3e` | `test_handoff.py` 22/22 | 67104 |
| `test_handoff.py` | v1.6 동반 | `2b94fe5cae1f` | — | 33458 |
| `HANDOFF_FORMAT.md` | v1.6 | `1e05b05950d4` | — | 12146 |
| `textbook.py` | v0.4 | `6372db295c4c` | `test_textbook.py` 27/27 | 54094 |
| `test_textbook.py` | v0.4 동반 | `94a34fd8445f` | — | 26750 |
| `TEXTBOOK.md` | v0.4 | `7f92ff9511f3` | — | 11390 |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — | 17531 |
| `CODE_PROJECT_README.md` · `HISTORY.md` · `release.py` | 코드 프로젝트 전용 | (배포하지 않음 — 판·해시는 RELEASE §3 코드 표) | — | — |

해시: `sha256sum <파일> | cut -c1-12`. 판: `python3 -c "import claim_graph; print(claim_graph.__version__)"` (deck_toolkit·verify_toolkit 동일), 문서는 첫 줄.
의존: 테스트 3종 python-docx, test_toolkit 은 python-pptx, test_verify_toolkit·`list_images` 는 Pillow, textbook·test_textbook 은 pypdf(v2.22). 테스트는 pytest 없이 `python3 test_*.py` 로 돈다.

## 2. 프로젝트별 배포표 — 누가 무엇을 받는가

| 파일 | 저자 | 발표 | 리뷰어 | 교과서 | 코드 |
|---|:-:|:-:|:-:|:-:|:-:|
| claim_graph.py · test_claim_graph.py · CLAIM_GRAPH.md | ○ | ○ | ○ | × | 진본 |
| deck_toolkit.py · test_toolkit.py · DECK_SPEC.md | × | ○ | × | × | 진본 |
| verify_toolkit.py · test_verify_toolkit.py | ○ | × | × | × | 진본 |
| handoff.py · test_handoff.py · HANDOFF_FORMAT.md | × | ○ | × | × | 진본 |
| textbook.py · test_textbook.py · TEXTBOOK.md | × | × | × | ○ | 진본 |
| REVIEW_PROTOCOL.md | × | × | ○ | × | 진본 |
| TOOLS_MANIFEST.md (이 파일) · RELEASE.md (최신 릴리스) | ○ | ○ | ○ | ○ | 진본 |
| CODE_PROJECT_README.md · HISTORY.md · release.py · GITHUB_README.md · PRIVATE_TERMS.txt | × | × | × | × | 진본 |
| **받는 파일 수** | **7** | **11** | **6** | **5** | 22 |

**코드 프로젝트도 공개 도구는 GitHub 에서 받는다** (v2.18~) — 프로젝트 파일에는 코드 전용 5개만 둔다(`CODE_PROJECT_README.md` 첫머리).

**교과서** (v2.22~): 사람 프로젝트가 아니라 Cowork 가 교과서 폴더에서 돌리는 역할(`selfcheck --role 교과서`). 규약은 `TEXTBOOK.md`.

**GitHub 공개 세트** (v2.15~): 저자·발표·리뷰어·교과서 세트의 합(v2.22: 17개) + `GITHUB_README.md` 를 `README.md` 로. 코드 전용 파일(HISTORY·README·
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

<!-- prev-release: v2.24 · CLAIM_GRAPH.md=ca0bd5652f32;CODE_PROJECT_README.md=369b99ea8f0f;DECK_SPEC.md=f8f57f8d85df;GITHUB_README.md=de9f905c7f6c;HANDOFF_FORMAT.md=b3781af6adc7;HISTORY.md=64b071590f32;PRIVATE_TERMS.txt=4285e1f439fb;REVIEW_PROTOCOL.md=7f6e413d4d48;TEXTBOOK.md=feb568e6edc9;claim_graph.py=dc3ac0780b61;deck_toolkit.py=85cbd8af803d;handoff.py=724c5adca67b;release.py=d6f02167dda3;test_claim_graph.py=bcfe1c1e42d6;test_handoff.py=b56c09230166;test_textbook.py=f4a634b3cef0;test_toolkit.py=51cdbea4be1e;test_verify_toolkit.py=aba65de39d87;textbook.py=abe606ebc772;verify_toolkit.py=e703af6d5418 -->
<!-- release-hashes: v2.25 · CLAIM_GRAPH.md=ca0bd5652f32;CODE_PROJECT_README.md=6db694b44ea6;DECK_SPEC.md=ac64f8ec2607;GITHUB_README.md=a338fce401db;HANDOFF_FORMAT.md=1e05b05950d4;HISTORY.md=e9a32b3e8fbe;PRIVATE_TERMS.txt=d2562278023a;REVIEW_PROTOCOL.md=7f6e413d4d48;TEXTBOOK.md=7f92ff9511f3;claim_graph.py=dc3ac0780b61;deck_toolkit.py=cab6d76ae0d8;handoff.py=267652b14b3e;release.py=d6f02167dda3;test_claim_graph.py=bcfe1c1e42d6;test_handoff.py=2b94fe5cae1f;test_textbook.py=94a34fd8445f;test_toolkit.py=b9405ff4bfd8;test_verify_toolkit.py=aba65de39d87;textbook.py=6372db295c4c;verify_toolkit.py=e703af6d5418 -->
