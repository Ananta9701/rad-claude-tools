# RELEASE v2.54 — manifest v74 — 2026-09-29

> **v2.54** — 관계도 전체 그림을 화면 폭에서 읽히게(사용자 09-29, 작은 판 순서 맨 앞). 저자 그래프(51주장·간선 83, caveat 46)가 **6614×1033 px** 로 옆으로 길었다 → 왼쪽→오른쪽, caveat 접기(`한계 N`), 역할별 색, 외톨이는 목록으로 **1388×2502 px**. `--impact` 그림은 그대로. mapgraph 에 외톨이 [참고]. claim_graph 16.1. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.1 | `mapdraw` 전체 그림 기본: `flowchart LR`(근거 왼쪽 → main 오른쪽) · caveat 상자·간선을 접고 걸린 상자에 `한계 N`(caveat 이 아닌 간선에 낀 caveat 상자는 남김) · 역할별 색(classDef) · 그릴 간선이 없는 상자는 그림 밖 목록(역할·한계 수) · 범례에 상자 글 뜻(`역할·confidence`, `-` = 역할 없음 — 발표 09-29) |
| `claim_graph.py` | 16.1 | `mapdraw --all-edges` = v16.0 전체 그림(아래→위, caveat 까지 모두). `--impact` 그림은 바꾸지 않음 |
| `claim_graph.py` | 16.1 | `mapgraph` [참고] 간선이 하나도 없는 주장(외톨이) — 한 줄에 이름 목록(주장 하나뿐이면 없음) |
| `CLAIM_GRAPH.md` | 16.1 | §3-3 그림 세 가지 표·실측, §3-1 표에 외톨이 |
| 테스트 | — | test_claim_graph 2(전체 그림 새 기본 — caveat 접기·남기기·색·외톨이 목록·impact 그대로·간선 없는 그래프, 외톨이 [참고] 한 줄·없음·주장 하나), 기존 mapdraw 시험 2개는 `--all-edges` 로 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-29: 전체 그림 6600×1030 px(부관리자 mermaid 11 렌더) | 위. 코드 세션에서 같은 그래프를 mermaid 11(Chromium)로 다시 재서 확인: 전 6614×1033 · `--text` 8715×1561 → 후 1388×2502 · 1689×3636. `--all-edges` 6614×1033(옛 모양 그대로), `--impact <주장 하나> --text` 422×975 |
| 사용자 09-29: mapgraph 외톨이 [참고] | 위 |
| 발표 09-29 mapdraw 확인: 상자 `-·mid` 뜻을 범례에 | 전체 그림 범례에 넣음 |
| 저자·리뷰어·발표 09-29: 첫 관계도가 그림으로 보임(사용자 확인) | 기록. 발표 그래프는 간선이 없어 선 모양은 미확인 — 새 기본에서는 21개 모두 그림 밖 목록으로 나온다 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.1 | `1ac39816e5c4` | ○ |
| `test_claim_graph.py` | v16.1 | `67ae6c31863f` | ○ |
| `CLAIM_GRAPH.md` | v16.1 | `82506932836c` | ○ |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `TOOLS_MANIFEST.md` | v74 | `a7d29d2b610c` | ○ |
| `RELEASE.md` | v2.54 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.1 | `1ac39816e5c4` | ○ |
| `test_claim_graph.py` | v16.1 | `67ae6c31863f` | ○ |
| `CLAIM_GRAPH.md` | v16.1 | `82506932836c` | ○ |
| `deck_toolkit.py` | v16.41 | `48c6d92415c7` | — |
| `test_toolkit.py` | v16.41 | `03718a9b26e4` | — |
| `DECK_SPEC.md` | v16.41 | `a7766b2b137a` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v74 | `a7d29d2b610c` | ○ |
| `RELEASE.md` | v2.54 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.1 | `1ac39816e5c4` | ○ |
| `test_claim_graph.py` | v16.1 | `67ae6c31863f` | ○ |
| `CLAIM_GRAPH.md` | v16.1 | `82506932836c` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v74 | `a7d29d2b610c` | ○ |
| `RELEASE.md` | v2.54 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `TOOLS_MANIFEST.md` | v74 | `a7d29d2b610c` | ○ |
| `RELEASE.md` | v2.54 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | — |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | — |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | — |
| `TOOLS_MANIFEST.md` | v74 | `a7d29d2b610c` | ○ |
| `RELEASE.md` | v2.54 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.1 | `1ac39816e5c4` | ○ |
| `test_claim_graph.py` | v16.1 | `67ae6c31863f` | ○ |
| `CLAIM_GRAPH.md` | v16.1 | `82506932836c` | ○ |
| `deck_toolkit.py` | v16.41 | `48c6d92415c7` | — |
| `test_toolkit.py` | v16.41 | `03718a9b26e4` | — |
| `DECK_SPEC.md` | v16.41 | `a7766b2b137a` | — |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
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
| `TOOLS_MANIFEST.md` | v74 | `a7d29d2b610c` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `9fba6992399e` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.54 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 저자·리뷰어·발표: selfcheck 로 manifest v74 이상. `mapdraw` 전체 그림(`--impact` 없이)이 새 모양이다 — 예전 모양은 `--all-edges`.
2. 발표: 지금 claims(간선 없음)로 `mapdraw` 를 돌리면 그림은 비고 21개가 목록으로 나온다 — 간선을 적은 뒤에 그림이 생긴다. mapgraph 도 [참고] 외톨이 한 줄.

## 5. 검증하지 않은 것

- 새 전체 그림의 실물 렌더는 저자 그래프 하나(mermaid 11, 코드 세션 Chromium). 리뷰어 그래프(56주장·90간선) 전체 그림은 재지 않았다(그래프 파일이 이 세션에 없다).
- 역할별 색이 claude.ai 대화창의 어두운 화면에서 어떻게 보이는지는 보지 않았다(흰 바탕 렌더만).
