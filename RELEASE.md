# RELEASE v2.70 — manifest v90 — 2026-09-30

> **v2.70** — 구연 덧붙임 1판(사용자 09-30 큰 방향 ①): 저자 claims 는 판째로 **읽기만** 하고, 발표는 따로 둔 덧붙임 파일에 화면 자리·화면 keys 만 적는다. 두 파일은 읽는 순간 합쳐 mapgraph·impact·mapdraw·덱 mapcheck 에 쓴다. 저자 판 따라가기(`oral sync`)와 화면 확인 기록(mapfreeze·mapstale)은 다음 판 v2.71. LITERATURE 에 "Docling 보조" 절.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.12 | 구연 덧붙임(`kind: 구연`): `oral init --author 저자.json -o 덧붙임.json`(빈 덧붙임 — `source` 에 저자 파일 이름·sha·주장 수·**스냅숏은 해시뿐**: 글 지문·원고 자리·keys 해시·role, 원고 문장 없음, 이미 있으면 멈춤) · `oral check --author … --oral …` · mapgraph·impact·mapdraw 에 `--oral … --author …`. 합친 그래프 = 쓴 저자 주장(글·간선·forbidden·status 는 저자, 자리·keys 는 덧붙임) + 그 상류 전부 **무대 밖**(`offstage` — 자리 없음, mapdraw 흐린 점선) + 발표 주장 `p-…`(저자 id 에만 기댐). 저자 파일의 원고 확인 기록(verified)은 뺀다. [필수]: 저자 sha 다름 · 쓴 id 없음 · 철회된 주장이 화면에 · 화면 자리가 아님 · p- 규칙. [참고]: 화면 keys 없는 주장 N개 |
| `deck_toolkit.py` | 16.48 | `mapcheck 덱.pptx --oral 덧붙임.json --author 저자.json` — 합친 그래프로 화면 자리에 keys·forbidden 대조, [필수] 면 대조 전에 멈춤(종료 코드 1) |
| `CLAIM_GRAPH.md` · `DECK_SPEC.md` · `LITERATURE.md` | 16.12 · 16.48 · 0.8.5 | §3-5 구연 덧붙임·명령표 · 머리 한 줄 · §3-1 Docling 보조(명령, 쪽 표지 없음·`−` 바뀜 주의, 09-29 측정 수) |
| 테스트 | — | test_claim_graph 3(스냅숏에 원고 문장·자리·keys 글자가 없음, 해시가 짝짓기 정규화와 같음, init 덮어쓰기 거부 · 합치기 성공: 쓴 것+상류, 하류·철회 빠짐, 무대 밖 자리 없음, 저자 verified 빠짐, keys 없는 주장 [참고] 한 줄, mapgraph 통과, mapdraw offstage, 저자 파일 바이트 그대로 · 실패 6가지와 CLI 종료 코드). test_toolkit 1(덱 mapcheck: 화면 keys 있음 통과 · 없는 표현 [반영 안 됨] · [필수] 멈춤 · --author 없이 2 · 저자 파일 그대로) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-30: 구연용 저자 claims 가져오기 — 설계 결정 8가지(별도 파일 · 상류 무대 밖 · p- · id 사라지면 멈춤 · 화면 keys 따로+없으면 [참고] · 사용자가 전달 · Drive 폴더 · 2판) + 스냅숏은 해시로 | 위 claim_graph 16.12 · deck 16.48 (id 사라짐·sync 는 v2.71) |
| 사용자 09-30: Docling 은 기본 채택 안 함, 보조 명령·주의를 LITERATURE 한 절로(①의 첫 판에 묶음) | 위 LITERATURE §3-1 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.12 | `664fb2536568` | ○ |
| `test_claim_graph.py` | v16.12 | `0140baedb1eb` | ○ |
| `CLAIM_GRAPH.md` | v16.12 | `447f992dfda3` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v90 | `4f30f845721e` | ○ |
| `RELEASE.md` | v2.70 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.12 | `664fb2536568` | ○ |
| `test_claim_graph.py` | v16.12 | `0140baedb1eb` | ○ |
| `CLAIM_GRAPH.md` | v16.12 | `447f992dfda3` | ○ |
| `deck_toolkit.py` | v16.48 | `7dbd370500a7` | ○ |
| `test_toolkit.py` | v16.48 | `0aacabd67376` | ○ |
| `DECK_SPEC.md` | v16.48 | `aff997648daa` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v90 | `4f30f845721e` | ○ |
| `RELEASE.md` | v2.70 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.12 | `664fb2536568` | ○ |
| `test_claim_graph.py` | v16.12 | `0140baedb1eb` | ○ |
| `CLAIM_GRAPH.md` | v16.12 | `447f992dfda3` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v90 | `4f30f845721e` | ○ |
| `RELEASE.md` | v2.70 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v90 | `4f30f845721e` | ○ |
| `RELEASE.md` | v2.70 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | ○ |
| `TOOLS_MANIFEST.md` | v90 | `4f30f845721e` | ○ |
| `RELEASE.md` | v2.70 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.12 | `664fb2536568` | ○ |
| `test_claim_graph.py` | v16.12 | `0140baedb1eb` | ○ |
| `CLAIM_GRAPH.md` | v16.12 | `447f992dfda3` | ○ |
| `deck_toolkit.py` | v16.48 | `7dbd370500a7` | ○ |
| `test_toolkit.py` | v16.48 | `0aacabd67376` | ○ |
| `DECK_SPEC.md` | v16.48 | `aff997648daa` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v90 | `4f30f845721e` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `7dcda332c57e` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.70 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v90 이상.
2. 발표: 구연 덱은 저자 claims 를 **고치지 않는다**. `claim_graph.py oral init --author <저자 claims> -o <덧붙임>` 으로 시작해 `use` 에 화면 자리(`slide@ID`)·화면 keys 를 적고, `oral check` · `deck_toolkit mapcheck 덱 --oral … --author …` 로 본다. 저자 판이 바뀌었을 때(sync)·mapfreeze 는 v2.71 까지 기다린다.
3. 저자: claims 판을 올리면 `to발표` 에 전달 통보 md(판·주장 수·sha256 앞 16자)를 올린다. 파일은 사용자가 Drive 에 옮긴다.
4. 리뷰어·문헌: 수식·표가 판정을 가르는 논문만 LITERATURE §3-1 Docling 보조(환경은 도구 세트에 없다 — 필요하면 코드에 알린다).

## 5. 검증하지 않은 것

- 실물 저자 claims(v9·v10)와 실제 구연 덱으로는 돌리지 않았다 — 가짜 저자 그래프(7주장)와 시험 덱으로만. 무대 밖 상류가 큰 그래프에서 그림이 읽히는지 모른다.
- 덧붙임 크기: 스냅숏은 주장당 약 150 바이트(해시) — 50주장이면 약 8 KB 로 추정, 실물로 재지 않았다.
