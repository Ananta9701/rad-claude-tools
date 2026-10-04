# RELEASE v2.88 — manifest v108 — 2026-10-04

> **v2.88** — `textbook.py` 0.8: 교과서 분할에서 조용히 빠지던 곳 세 가지(세 자리 장 · 긴 장 이름 · 장 머리 OCR)를 고침. 다른 도구 동작 변경 없음.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `textbook.py` · `test_textbook.py` · `TEXTBOOK.md` | 0.8 | ① 장 표 줄의 **세 자리 장 번호**(`\| 100 \|`)도 읽는다 — 정규식이 두 자리만 받아 Gore 100–127장 28줄을 조용히 버렸다(09-27 분할에서 PDF 1862–2286 빠짐). ② `plan_named()` — plan 첫 줄 `method=` 가 `쪽 머리` 가 아니면(책갈피·사람이 만든/고친 장 표) 긴 장도 `미확인` 없이 장 이름으로 나눔(`split_units(named=True)`). ③ 쪽 머리 OCR `세`(제)를 받고, 새 장 번호가 뒤 12쪽 안에 다시 안 나와도 다음에 처음 잡힌 쪽 머리가 같은 번호나 다음 번호면 받음 — 신경영상의학 10장(13쪽, 쪽 머리 한 번)에서 멈춰 11–31장(509쪽)을 뒤붙이로 보낸 일. 시험 3건(고치기 전 3 실패 · 성공·실패 두 쪽) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자·부관리자 10-04 밤 최종 지시 5 — textbook.py 고침 판(세 자리 장 · 긴 장 이름 · OCR 장 머리), 실패 시험부터 | 위 0.8. 이미 나눈 두 책(Gore 100–127장 · 신경영상의학 269–777쪽)은 10-04 에 같은 규칙의 일회용 스크립트로 `교과서 분할/_보충/` 에 넣었다 — 이 판으로 다시 나누지 않는다 |

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
| `TOOLS_MANIFEST.md` | v108 | `643dcbc06b92` | ○ |
| `RELEASE.md` | v2.88 | — | 이 문서 |

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
| `TOOLS_MANIFEST.md` | v108 | `643dcbc06b92` | ○ |
| `RELEASE.md` | v2.88 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v108 | `643dcbc06b92` | ○ |
| `RELEASE.md` | v2.88 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.8 | `7abf23141257` | ○ |
| `test_textbook.py` | v0.8 | `30f706224461` | ○ |
| `TEXTBOOK.md` | v0.8 | `f6803d176f4a` | ○ |
| `TOOLS_MANIFEST.md` | v108 | `643dcbc06b92` | ○ |
| `RELEASE.md` | v2.88 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `TOOLS_MANIFEST.md` | v108 | `643dcbc06b92` | ○ |
| `RELEASE.md` | v2.88 | — | 이 문서 |

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
| `textbook.py` | v0.8 | `7abf23141257` | ○ |
| `test_textbook.py` | v0.8 | `30f706224461` | ○ |
| `TEXTBOOK.md` | v0.8 | `f6803d176f4a` | ○ |
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v108 | `643dcbc06b92` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `76f237430491` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.88 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v108 이상.
2. **교과서(Cowork)**: 다음 분할부터 0.8. 사람이 고친 장 표는 첫 줄 `method=` 를 `쪽 머리` 가 아닌 말(예: `사람 확인`)로 바꾸면 긴 장도 장 이름으로 나뉜다.

## 5. 검증하지 않은 것

- ③ 의 새 규칙(다음 쪽 머리로 받기)으로 이미 나눈 다른 책의 장 표가 바뀌는지는 맥 원본 24권(두경부 빼고)에서 옛·새 판을 나란히 돌려 비교했다 — 결과는 비공개 기록(HISTORY)에. 실제 다시 나누기는 하지 않았다.
- Cowork(Python 3.10) 환경의 실제 분할은 돌리지 않았다(build 의 3.10·옛 라이브러리 시험만).
