# RELEASE v2.76 — manifest v96 — 2026-09-30

> **v2.76** — suggest 첫 실행 회신(저자 09-30): 덧줄의 main 전제 사슬을 설계대로 **main 포함**으로 센다(v2.75 는 main 을 빼고 세어 저자 v10 에서 3줄 — 설계로는 1줄). 이미 main 에 걸린 공통 한계는 "(main 에 이미 걸림)", 규칙 3 줄마다 한계 문장 앞 40자.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.18 | `suggest` 덧줄 — 사슬(premise 만)에 main 을 넣어 세고 "사슬 N개" 의 N 도 main 포함 · 규칙 3 공통 한계가 이미 main 에 걸려 있으면 "→ main 에 직접 걸기" 대신 "(main 에 이미 걸림)"(main 이 여럿이면 어느 main) · 규칙 3 줄·덧줄마다 한계 statement 앞 40자 |
| `CLAIM_GRAPH.md` | 16.18 | §3-7 규칙 3 칸 |
| 테스트 | — | test_claim_graph 2(사슬 main+5 에 걸린 3 → 덧줄 없음 / 4 → "사슬 6개 중 4개" / main 에 걸림 → 없음 · 권고 그대로·statement 40자 / 이미 걸림 표시·권고 없음 / 덧줄 statement) · v16.17 덧줄 시험의 가짜 그래프를 설계 기준으로 바로잡음 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 저자 09-30: 덧줄 3줄(코드 실측 1줄) | [확인 필요] — 가짜 그래프로 재현: 측정 스크립트가 설계(main 포함)와 맞고 v2.75 구현이 main 을 빼고 셌다 → 구현 고침. v10 에 돌리면 1줄이 될 것(코드 실측과 같은 계산) |
| 저자 09-30: 이미 main 에 건 한계도 권고가 붙음 | "(main 에 이미 걸림)" |
| 저자 09-30: 한계 문장을 따로 보여야 했음 | 줄마다 statement 앞 40자 |
| 사용자·부관리자 09-30: v2.75 Linux 확인 · focus "(탐색)" PNG 확인 | v2.75 §5 두 번째 줄 닫음 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.18 | `cb9761933b49` | ○ |
| `test_claim_graph.py` | v16.18 | `857fa213527b` | ○ |
| `CLAIM_GRAPH.md` | v16.18 | `0b19aeedf248` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v96 | `6049b37b6b81` | ○ |
| `RELEASE.md` | v2.76 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.18 | `cb9761933b49` | ○ |
| `test_claim_graph.py` | v16.18 | `857fa213527b` | ○ |
| `CLAIM_GRAPH.md` | v16.18 | `0b19aeedf248` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v96 | `6049b37b6b81` | ○ |
| `RELEASE.md` | v2.76 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.18 | `cb9761933b49` | ○ |
| `test_claim_graph.py` | v16.18 | `857fa213527b` | ○ |
| `CLAIM_GRAPH.md` | v16.18 | `0b19aeedf248` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v96 | `6049b37b6b81` | ○ |
| `RELEASE.md` | v2.76 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v96 | `6049b37b6b81` | ○ |
| `RELEASE.md` | v2.76 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `TOOLS_MANIFEST.md` | v96 | `6049b37b6b81` | ○ |
| `RELEASE.md` | v2.76 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.18 | `cb9761933b49` | ○ |
| `test_claim_graph.py` | v16.18 | `857fa213527b` | ○ |
| `CLAIM_GRAPH.md` | v16.18 | `0b19aeedf248` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
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
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v96 | `6049b37b6b81` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `d51016f23bd1` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.76 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v96 이상.
2. 저자: claims v11 에 `suggest` 를 다시 돌리면 main 에 건 3개는 "(main 에 이미 걸림)", 덧줄은 설계 기준으로 센다. 보류한 한계 2개(문장이 낡음)는 statement 를 고친 뒤 다시.

## 5. 검증하지 않은 것

- 저자 실물(v10·v11)에 v16.18 덧줄을 돌린 수는 코드가 다시 재지 않았다 — v10 측정 스크립트가 같은 계산으로 1줄이었다. 저자 대화창이 v11 로 확인할 것.
- `suggest` 규칙 1 의 문헌 DOI 공유는 여전히 가짜 그래프로만(저자 sources 가 채워진 뒤).
