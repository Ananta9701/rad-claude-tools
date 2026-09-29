# RELEASE v2.56 — manifest v76 — 2026-09-29

> **v2.56** — 작은 판 두 가지. ① **인용 점검 en dash 거짓 위반**(코드 리뷰 ⑫): `check_citations` 가 `[4–6]`(Word 가 자동으로 바꾼 en dash)을 인용으로 읽지 못해 4·5·6 이 빠지고 뒤 인용이 순서 위반·결번으로 나왔다. verify_toolkit 1.3.7. ② 간선이 하나도 없는 그래프에서 **주장별 간선 [참고]**(role=claim 인데 premise 없음 등)가 주장마다 한 줄씩 나오던 것을 요약 한 줄에 합쳤다(사용자 09-29, 부관리자 재현 — role=claim 21개면 21줄). claim_graph 16.3. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `verify_toolkit.py` | 1.3.7 | `check_citations`: 인용 패턴에 en dash(`–`, U+2013)를 넣고 범위로 편다(`[4–6]`·`[5 – 6]`). 다른 곳(`renumber` 의 `_CITE_RE`)은 이미 en dash 를 읽었다 |
| `claim_graph.py` | 16.3 | `mapgraph`: 그래프 전체에 간선이 없으면 주장별 [참고] "role=main/claim 인데 premise 간선이 없음"·"evidence 인데 걸린 caveat 이 없음" 을 줄마다 내지 않고 "간선이 하나도 없는 그래프" 한 줄에 개수로(`premise 없음 N · caveat 없음 M`). 간선이 하나라도 있으면 전처럼 줄마다. 그래프 전체 한 줄([참고] role=main 개수)과 간선과 무관한 주장별 [참고](forbidden·supersedes 등)는 그대로 |
| `CLAIM_GRAPH.md` | 16.3 | §3-1 표 |
| 테스트 | — | test_verify_toolkit 1(재현 — 옛 코드 실패: en dash 범위 성공 · 범위가 건너뛴 결번 · 진짜 순서 위반), test_claim_graph 외톨이 시험에 role=claim 21개 간선 0(한 줄) · 간선 하나 있으면 줄마다 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 코드 리뷰 ⑫ 인용 en dash 거짓 위반 | 위 verify_toolkit 1.3.7 |
| 사용자 09-29: 간선 0 그래프의 주장별 [참고] 21줄 | 위 claim_graph 16.3. 발표 실제 claims 확인: Drive 에 있는 발표 claims(09-08 판)에는 **role 칸이 없다**(발표 회신이 말한 09-20 판 형식과 같음) — 그래서 실제 발표 그래프에서는 role 기반 [참고] 가 원래 나오지 않고, 남는 주장별 [참고] 는 forbidden·supersedes 줄뿐(간선과 무관 — 그대로 둠) |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.3 | `0073d9a97be1` | ○ |
| `test_claim_graph.py` | v16.3 | `38c006968580` | ○ |
| `CLAIM_GRAPH.md` | v16.3 | `3edc1e0dd2f2` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | ○ |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | ○ |
| `TOOLS_MANIFEST.md` | v76 | `285374d5fa8c` | ○ |
| `RELEASE.md` | v2.56 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.3 | `0073d9a97be1` | ○ |
| `test_claim_graph.py` | v16.3 | `38c006968580` | ○ |
| `CLAIM_GRAPH.md` | v16.3 | `3edc1e0dd2f2` | ○ |
| `deck_toolkit.py` | v16.41 | `48c6d92415c7` | — |
| `test_toolkit.py` | v16.41 | `03718a9b26e4` | — |
| `DECK_SPEC.md` | v16.41 | `a7766b2b137a` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v76 | `285374d5fa8c` | ○ |
| `RELEASE.md` | v2.56 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.3 | `0073d9a97be1` | ○ |
| `test_claim_graph.py` | v16.3 | `38c006968580` | ○ |
| `CLAIM_GRAPH.md` | v16.3 | `3edc1e0dd2f2` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v76 | `285374d5fa8c` | ○ |
| `RELEASE.md` | v2.56 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `TOOLS_MANIFEST.md` | v76 | `285374d5fa8c` | ○ |
| `RELEASE.md` | v2.56 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | — |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | — |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | — |
| `TOOLS_MANIFEST.md` | v76 | `285374d5fa8c` | ○ |
| `RELEASE.md` | v2.56 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.3 | `0073d9a97be1` | ○ |
| `test_claim_graph.py` | v16.3 | `38c006968580` | ○ |
| `CLAIM_GRAPH.md` | v16.3 | `3edc1e0dd2f2` | ○ |
| `deck_toolkit.py` | v16.41 | `48c6d92415c7` | — |
| `test_toolkit.py` | v16.41 | `03718a9b26e4` | — |
| `DECK_SPEC.md` | v16.41 | `a7766b2b137a` | — |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | ○ |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | ○ |
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
| `TOOLS_MANIFEST.md` | v76 | `285374d5fa8c` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `3627091e2242` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.56 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v76 이상.
2. 저자: `check_citations` 에서 `[n–m]` 때문에 순서 위반·결번이 나왔던 원고가 있으면 다시 돌린다.

## 5. 검증하지 않은 것

- en dash 외 다른 줄표(em dash `—`, figure dash `‒`, minus `−`)는 인용 범위로 읽지 않는다 — Vancouver 인용에서 실물 사례를 못 봤다. 나오면 알려 달라.
- 발표의 09-20 판 claims 는 이 세션에 없다 — Drive 의 09-08 판(role 없음)과 발표 회신의 설명으로 판단.
