# RELEASE v2.89 — manifest v109 — 2026-10-04

> **v2.89** — `textbook.py` 0.8.1: 교과서 장 표 줄을 **읽지 못하면 버리되 경고**하고, plan 이 빈 제목 줄을 쓰지 않게 함. 다른 도구 동작 변경 없음.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `textbook.py` · `test_textbook.py` · `TEXTBOOK.md` | 0.8.1 | ① `plan_dropped()` — 장 표 모양(칸 7개)인데 읽지 못한 줄을 찾아 split 출력(`[경고] 장 표 줄 N개를 읽지 못해 버림 — 줄 …`)과 그 책 `INDEX.md` 머리(`[경고] 장 표에서 읽지 못해 버린 줄 N개`)에 적는다 — 전에는 아무 말 없이 그 장이 빠졌다(Gore 100–127장). ② plan 이 쪽 머리 제목이 빈 장을 `(제목 못 읽음)` 으로 쓴다 — 빈 칸 줄(`\| 11 \|  \| 143 \|`)은 split 이 읽지 못해 버렸다(실제 인터벤션 11장, 10-04 다시 나누기에서 발견). 시험 2건(고치기 전 2 실패 · 성공·실패 두 쪽) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 부관리자 `_계획/대기열_v1` B — textbook.py 고침 판의 "줄을 버리면 경고"(v2.88 에서 빠짐) | 위 ① |
| 10-04 교과서 6권 다시 나누기에서 인터벤션 11장(PDF 143–146) 줄이 버려진 것 | 위 ②. 이미 나눈 `_보충/19_인터벤션` 은 이 판으로 11장 파일·INDEX 만 더한다(비공개 기록) |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | — |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | — |
| `TOOLS_MANIFEST.md` | v109 | `d06a03102e9d` | ○ |
| `RELEASE.md` | v2.89 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.54 | `71b8a1bfa924` | — |
| `test_toolkit.py` | v16.54 | `217fa50a4cc6` | — |
| `DECK_SPEC.md` | v16.54 | `724b3edaa739` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v109 | `d06a03102e9d` | ○ |
| `RELEASE.md` | v2.89 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v109 | `d06a03102e9d` | ○ |
| `RELEASE.md` | v2.89 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.8.1 | `7c7209da8ae6` | ○ |
| `test_textbook.py` | v0.8.1 | `c74411fafc92` | ○ |
| `TEXTBOOK.md` | v0.8.1 | `c6da3ec0c3fa` | ○ |
| `TOOLS_MANIFEST.md` | v109 | `d06a03102e9d` | ○ |
| `RELEASE.md` | v2.89 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `TOOLS_MANIFEST.md` | v109 | `d06a03102e9d` | ○ |
| `RELEASE.md` | v2.89 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.54 | `71b8a1bfa924` | — |
| `test_toolkit.py` | v16.54 | `217fa50a4cc6` | — |
| `DECK_SPEC.md` | v16.54 | `724b3edaa739` | — |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | — |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.8.1 | `7c7209da8ae6` | ○ |
| `test_textbook.py` | v0.8.1 | `c74411fafc92` | ○ |
| `TEXTBOOK.md` | v0.8.1 | `c6da3ec0c3fa` | ○ |
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v109 | `d06a03102e9d` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `fc3f0c071db5` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `5902bac98881` | ○ |
| `RELEASE.md` | v2.89 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v109 이상.
2. **교과서(Cowork)**: 다음 분할부터 0.8.1. split 출력이나 책 `INDEX.md` 머리에 `[경고]` 가 있으면 장 표의 그 줄(장 번호 두·세 자리 · 제목 칸 비지 않게)을 고친 뒤 그 책 폴더를 지우고 다시.

## 5. 검증하지 않은 것

- 경고는 칸 7개 줄만 본다 — 칸 수까지 틀린 줄(파이프 빠짐)은 장 표 줄로 보지 않아 경고도 없다.
- Cowork(Python 3.10) 환경의 실제 분할은 돌리지 않았다(build 의 3.10·옛 라이브러리 시험만). 맥 실제 장 표 9개에 `plan_dropped` 를 돌려 인터벤션 한 줄만 잡힘(나머지 8개 0).
