# RELEASE v2.59 — manifest v79 — 2026-09-29

> **v2.59** — 발표 K23(09-29, 첫 실물 증례 관계도): 배제된 감별이 확정 진단과 같은 초록 상자로 그려져 구별이 안 됐다. `status: "excluded"`(배제된 감별 — 자리에 계속 실림) · mapdraw 흰 채움 + 점선 + "배제" · mapgraph 는 premise 없음 대신 "배제 근거 없음" [참고]. 덧붙여(사용자): `group` 칸 → 증례마다 묶어 그리기(Mermaid subgraph), 맨 위 `kind: "증례"` → 논문용 [참고] 끄기, 증례 예시에 두 반박 모양. claim_graph 16.6 · deck_toolkit 16.43. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.6 | `status: "excluded"` — 배제된 감별. `superseded`(철회)와 달리 sites·keys 대조는 그대로. mapgraph: premise 없음 [참고] 를 내지 않고, rebuttal 간선이 없으면 [참고] "배제 근거가 없는 배제". `gaps` 는 배제 감별을 공백에서 뺀다 |
| `claim_graph.py` | 16.6 | `mapdraw` 전체 그림: 배제 상자는 **흰 채움 + 점선 테두리 + "배제"**(회색은 background 색이라 쓰지 않음, 사용자), 역할 색을 받지 않음, 그림 아래 범례 한 줄. `group` 칸이 있으면 같은 group 을 **subgraph** 로 묶는다 |
| `claim_graph.py` | 16.6 | 그래프 맨 위 `"kind": "증례"`(또는 `case`) — mapgraph 가 논문용 [참고] 셋(forbidden 인데 supersedes 없음 · evidence 인데 caveat 없음 · main 여럿)을 끈다. CLI `mapgraph` 가 맨 위 칸을 읽는다 |
| `deck_toolkit.py`·`DECK_SPEC.md` | 16.43 | `mapgraph` 명령이 맨 위 `kind` 를 claim_graph 에 넘긴다 |
| `CLAIM_GRAPH.md` | 16.6 | §3-2-1 증례 예시를 두 반박 모양으로(소견이 배제 감별에 바로 rebuttal = 기본 · 병력 등 소견 하나가 아닌 이유는 따로 rebuttal 노드), `excluded`·`group`·`kind` 설명, §3 표 |
| 테스트 | — | test_claim_graph 2(배제 감별·증례 모드·묶음·색·gaps 제외·모르는 status · CLI kind 있음/없음), 문서 예시 시험을 새 예시로(증례 모드에서 알림 0) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 발표 K23 요청 1 배제 표시 칸 | `status: "excluded"`(이름은 코드 판단 — status 가 이미 철회·제안을 담는 칸이라) |
| 요청 2 mapdraw 구별 | 흰 채움 + 점선 + "배제"(사용자 — 회색 대신) |
| 요청 3 mapgraph | premise [참고] 끔, rebuttal 없으면 [참고] |
| 요청 4 반박 모양 | **소견(evidence)에서 배제 감별로 바로 rebuttal 이 기본**. 배제 이유가 소견 하나가 아닐 때(병력·역학·문헌)만 따로 rebuttal 노드. §3-2-1 에 둘 다 |
| 사용자: 묶음 그리기(다른 증례 상자를 뚫는 선) | `group` → subgraph |
| 사용자: 증례 모드(논문용 [참고] 16줄) | 맨 위 `kind: "증례"` |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.6 | `73a10a035548` | ○ |
| `test_claim_graph.py` | v16.6 | `d3353661aa6a` | ○ |
| `CLAIM_GRAPH.md` | v16.6 | `65fdba927970` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v79 | `9dc4f6da305b` | ○ |
| `RELEASE.md` | v2.59 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.6 | `73a10a035548` | ○ |
| `test_claim_graph.py` | v16.6 | `d3353661aa6a` | ○ |
| `CLAIM_GRAPH.md` | v16.6 | `65fdba927970` | ○ |
| `deck_toolkit.py` | v16.43 | `b652a0cb4079` | ○ |
| `test_toolkit.py` | v16.43 | `9e13ce358f6e` | ○ |
| `DECK_SPEC.md` | v16.43 | `8249466f90e0` | ○ |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v79 | `9dc4f6da305b` | ○ |
| `RELEASE.md` | v2.59 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.6 | `73a10a035548` | ○ |
| `test_claim_graph.py` | v16.6 | `d3353661aa6a` | ○ |
| `CLAIM_GRAPH.md` | v16.6 | `65fdba927970` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v79 | `9dc4f6da305b` | ○ |
| `RELEASE.md` | v2.59 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `TOOLS_MANIFEST.md` | v79 | `9dc4f6da305b` | ○ |
| `RELEASE.md` | v2.59 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | — |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | — |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | — |
| `TOOLS_MANIFEST.md` | v79 | `9dc4f6da305b` | ○ |
| `RELEASE.md` | v2.59 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.6 | `73a10a035548` | ○ |
| `test_claim_graph.py` | v16.6 | `d3353661aa6a` | ○ |
| `CLAIM_GRAPH.md` | v16.6 | `65fdba927970` | ○ |
| `deck_toolkit.py` | v16.43 | `b652a0cb4079` | ○ |
| `test_toolkit.py` | v16.43 | `9e13ce358f6e` | ○ |
| `DECK_SPEC.md` | v16.43 | `8249466f90e0` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | — |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | — |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v79 | `9dc4f6da305b` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `e7219da41945` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.59 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v79 이상.
2. 발표: 증례 claims 에 ① 맨 위 `"kind": "증례"` ② 배제된 감별 넷에 `"status": "excluded"` ③ 주장마다 `"group": "case1"` 등을 달고 관계도를 다시 그려 사용자에게 보인다. 반박은 지금처럼 소견에서 바로 거는 모양이 기본이다.

## 5. 검증하지 않은 것

- 발표의 실제 증례 claims 로는 돌리지 않았다(공개 저장소에 넣지 않는 파일 — 이 세션에 없다). 가짜 증례 두 개(묶음 2 · 배제 2 · 반박 노드 1)를 mermaid 11 로 렌더해 확인(977×1017 px).
- subgraph 안에서는 Mermaid 가 위→아래로 놓는다 — 증례가 많으면 세로로 길어질 수 있다.
