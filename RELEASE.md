# RELEASE v2.60 — manifest v80 — 2026-09-29

> **v2.60** — 작은 판(사용자 09-29, 13번보다 먼저): 저자 gaps 첫 실행 제안 두 가지. ① "문헌 없음" 중 원고 인용 `[n]` 이 이미 있는 주장을 **"문헌 없음(인용 있음 — sources 미기입)"** 으로 따로 — 작업표를 1부 찾을 공백 · 2부 인용 있음(기입 한 줄)으로 나눈다. ② **검색어 칸을 비운다**(keys 는 원고 추적용 앵커라 검색어로 쓸모가 없었다 — 역할 대화창이 만든다). claim_graph 16.7. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.7 | `gaps`: 문헌 없음인데 statement·sites 에 `[n]`(`[12,14]`·`[7–9]` 포함)이 있으면 공백 종류 `문헌 없음(인용 있음 — sources 미기입)`. 작업표 1부(찾을 공백 — 받침·반박 두 줄) / 2부(인용만 있고 다른 공백이 없는 주장 — `G..-기입` 한 줄). 머리 요약도 두 부류를 따로 센다 |
| `claim_graph.py` | 16.7 | `gaps`: 검색어 칸을 비워 낸다(keys 를 넣지 않음). `gaps --to-instr`: 기입 줄도 읽고, 검색어가 빈 줄은 알린다(locate 가 찾을 말이 없다) |
| `CLAIM_GRAPH.md` | 16.7 | §3-4 표·설명, 약한 고리에 caveat 이 들어오는 것은 의도(사용자) |
| 테스트 | — | test_claim_graph 1(문장·자리의 인용으로 구분 · 인용 없으면 그대로 · 인용 + 약한 고리는 1부 · keys 가 검색어로 안 들어감 · 머리 요약 · 기입 줄 → 검증지시 · 빈 검색어 알림), 기존 gaps 시험 두 개를 새 규칙에 맞춤 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 저자 09-29 claims v10·gaps: 문헌 없음 두 부류 | 위 ① |
| 같은 회신: 검색어가 keys 에서 옴 | 위 ② — 사용자: 칸을 비우고 역할 대화창이 만든다 |
| 같은 회신: caveat 도 약한 고리 | 의도(사용자) — support·premise 로 기댄 경우만 잡힌다. 받침으로 쓴 caveat 은 간선 종류를 다시 볼 것 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.7 | `78edf29e1a43` | ○ |
| `test_claim_graph.py` | v16.7 | `d42bf3a61719` | ○ |
| `CLAIM_GRAPH.md` | v16.7 | `ff1eedb8ea59` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v80 | `c555f23be771` | ○ |
| `RELEASE.md` | v2.60 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.7 | `78edf29e1a43` | ○ |
| `test_claim_graph.py` | v16.7 | `d42bf3a61719` | ○ |
| `CLAIM_GRAPH.md` | v16.7 | `ff1eedb8ea59` | ○ |
| `deck_toolkit.py` | v16.43 | `b652a0cb4079` | — |
| `test_toolkit.py` | v16.43 | `9e13ce358f6e` | — |
| `DECK_SPEC.md` | v16.43 | `8249466f90e0` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v80 | `c555f23be771` | ○ |
| `RELEASE.md` | v2.60 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.7 | `78edf29e1a43` | ○ |
| `test_claim_graph.py` | v16.7 | `d42bf3a61719` | ○ |
| `CLAIM_GRAPH.md` | v16.7 | `ff1eedb8ea59` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v80 | `c555f23be771` | ○ |
| `RELEASE.md` | v2.60 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `TOOLS_MANIFEST.md` | v80 | `c555f23be771` | ○ |
| `RELEASE.md` | v2.60 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | — |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | — |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | — |
| `TOOLS_MANIFEST.md` | v80 | `c555f23be771` | ○ |
| `RELEASE.md` | v2.60 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.7 | `78edf29e1a43` | ○ |
| `test_claim_graph.py` | v16.7 | `d42bf3a61719` | ○ |
| `CLAIM_GRAPH.md` | v16.7 | `ff1eedb8ea59` | ○ |
| `deck_toolkit.py` | v16.43 | `b652a0cb4079` | — |
| `test_toolkit.py` | v16.43 | `9e13ce358f6e` | — |
| `DECK_SPEC.md` | v16.43 | `8249466f90e0` | — |
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
| `TOOLS_MANIFEST.md` | v80 | `c555f23be771` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `b4553213c676` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.60 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 저자·리뷰어: selfcheck 로 manifest v80 이상. `gaps` 를 다시 돌리면 작업표가 두 부분으로 나온다 — 2부(인용 있음)는 인용 문헌 DOI 를 적어 받고 판정해 sources 에 기입, 1부만 새로 찾는다. 검색어는 공백을 읽고 대화창이 적는다.

## 5. 검증하지 않은 것

- 저자 claims v10 으로는 돌리지 않았다(이 세션에 없다) — 저자 회신의 "14개 중 6개" 는 저자 쪽에서 다시 확인해 달라.
- 인용 표기는 대괄호 숫자(`[n]`·`[n,m]`·`[n–m]`)만 본다. 저자-연도 인용(`Kim 2020`)은 인용으로 보지 않는다.
