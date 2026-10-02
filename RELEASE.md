# RELEASE v2.85 — manifest v105 — 2026-10-03

> **v2.85** — 문서만: `REVIEW_PROTOCOL` 7.6 §4 측정에 ROI 희석 점검 한 줄(ROI 부피/구조 부피 비). 코드 동작 변경 없음.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `REVIEW_PROTOCOL.md` | 7.6 | §4 **측정** 에 한 항: ROI 를 정규화·재샘플링 뒤 마스크에 낮은 임계로 정의했으면 ROI 부피(화소 수 × 화소 부피)와 원래 구조 부피의 비를 원자료에서 계산 — 비가 크면 ROI 평균이 구조 밖 조직으로 희석되고, 비교 대상 사이에 비가 다르면 비대칭 희석. 저자에게 비 보고·평균 방식(단순·가중)·임계를 올린 민감도 분석을 묻는다. 기존 "군 간 ROI 크기·구성" 항목과 따로 본다. §9 변경 이력 v7.6 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 리뷰어 회신 10-02 §4 체크리스트 ROI 범위 제안 | 위 7.6 — 사용자 10-03 넣기로. 변경 이력 근거에 리뷰어 회신 파일 이름(요청대로) |

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
| `TOOLS_MANIFEST.md` | v105 | `5e11817354a5` | ○ |
| `RELEASE.md` | v2.85 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.52 | `fd63018fe975` | — |
| `test_toolkit.py` | v16.52 | `3bef3c5c6f90` | — |
| `DECK_SPEC.md` | v16.52 | `852650b149a3` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v105 | `5e11817354a5` | ○ |
| `RELEASE.md` | v2.85 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | ○ |
| `TOOLS_MANIFEST.md` | v105 | `5e11817354a5` | ○ |
| `RELEASE.md` | v2.85 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v105 | `5e11817354a5` | ○ |
| `RELEASE.md` | v2.85 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `TOOLS_MANIFEST.md` | v105 | `5e11817354a5` | ○ |
| `RELEASE.md` | v2.85 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.52 | `fd63018fe975` | — |
| `test_toolkit.py` | v16.52 | `3bef3c5c6f90` | — |
| `DECK_SPEC.md` | v16.52 | `852650b149a3` | — |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | — |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | ○ |
| `TOOLS_MANIFEST.md` | v105 | `5e11817354a5` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `46ba8509b94d` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.85 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v105 이상. 동작 변경 없음.
2. **리뷰어**: REVIEW_PROTOCOL 7.6 — 다음 회차부터 §4 측정의 ROI 희석 항목을 본다.

## 5. 검증하지 않은 것

- 문서만 — 리뷰어 실제 회차에서 새 항목을 써 보지 않았다.
- 바뀐 줄의 개인정보는 release.py 검사(이름·주제어·나이/성별 모양) + 사람 눈으로 봤다 — 특정 원고의 주장·수치·지표 이름 없음, 내부 문서 이름 없음.
