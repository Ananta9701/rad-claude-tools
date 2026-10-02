# RELEASE v2.83 — manifest v103 — 2026-10-02

> **v2.83** — 문서만: `REVIEW_PROTOCOL` 7.4 — §4 체크리스트 2항(측정: 새 정량 지표의 정확도·반복성 · 보고: 대표 영상 참여자 대조) · §10·머리말: REVIEW_PROTOCOL 사본도 프로젝트에 두지 않는다(`/tmp/rct` 의 것만). 다음 회차부터. 코드 동작 변경 없음.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `REVIEW_PROTOCOL.md` | 7.4 | §4 **측정**에 한 줄 — 새 정량 지표의 정확도(팬텀·독립 측정)와 반복성(개인 내 SD·CV·ICC·최소 검출 차이)을 원고·인용 문헌에서 따로 확인, 없으면 효과 크기와 견주어 해석 한계로 지적, 반복성과 정확도를 섞지 않음 · §4 **보고**에 한 줄 — 대표 영상 범례의 인적 사항을 원자료 조합과 대조(없으면 표본 밖일 수 있음), 대조할 수 없으면 표본 안인지 저자에게 묻기, 개인정보 지적과 따로 · 머리말 첫 줄과 §10 첫 문단·"둔다"·"뺀다": REVIEW_PROTOCOL 도 GitHub 세트(`/tmp/rct`)의 것만 읽고 프로젝트 사본은 뺀다 · 머리말 v7.4 줄 · §9 v7.4. 그 밖의 절은 그대로 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 리뷰어 10-02 `회신_리뷰어to코드_체크리스트추가_v1` C-1(E 관점) · C-2(B 관점) | 넣음(사용자 결정 — 부관리자 지시 `리뷰규약체크리스트_v1` 1번). §4 에는 "관점" 묶음 이름이 없어 C-1 은 **보고**(그림·표 대조), C-2 는 **측정**에 둠. 회신의 실례(나이·성별·군·회차·판 번호·원자료 분포)와 지표 이름은 공개 문서에 넣지 않음 — 예는 "새 영상 기반 정량 지표" |
| 부관리자 지시 같은 날 3번: REVIEW_PROTOCOL 사본도 뺌 | 위 §10·머리말 |
| 같은 지시 4번: 판·release | 공개 파일이 바뀌므로 판(v2.83). 적용은 다음 회차부터 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.23 | `e6c4243ade62` | — |
| `test_claim_graph.py` | v16.23 | `b40e84e1314b` | — |
| `CLAIM_GRAPH.md` | v16.23 | `0410c30e4f71` | — |
| `verify_toolkit.py` | v1.3.8 | `529ce4740c17` | — |
| `test_verify_toolkit.py` | v1.3.8 | `a1b46f5e0e74` | — |
| `TOOLS_MANIFEST.md` | v103 | `08c79cae5cfa` | ○ |
| `RELEASE.md` | v2.83 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.23 | `e6c4243ade62` | — |
| `test_claim_graph.py` | v16.23 | `b40e84e1314b` | — |
| `CLAIM_GRAPH.md` | v16.23 | `0410c30e4f71` | — |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v103 | `08c79cae5cfa` | ○ |
| `RELEASE.md` | v2.83 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.23 | `e6c4243ade62` | — |
| `test_claim_graph.py` | v16.23 | `b40e84e1314b` | — |
| `CLAIM_GRAPH.md` | v16.23 | `0410c30e4f71` | — |
| `REVIEW_PROTOCOL.md` | v7.4 | `8c56bf02ca59` | ○ |
| `TOOLS_MANIFEST.md` | v103 | `08c79cae5cfa` | ○ |
| `RELEASE.md` | v2.83 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v103 | `08c79cae5cfa` | ○ |
| `RELEASE.md` | v2.83 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `TOOLS_MANIFEST.md` | v103 | `08c79cae5cfa` | ○ |
| `RELEASE.md` | v2.83 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.23 | `e6c4243ade62` | — |
| `test_claim_graph.py` | v16.23 | `b40e84e1314b` | — |
| `CLAIM_GRAPH.md` | v16.23 | `0410c30e4f71` | — |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
| `verify_toolkit.py` | v1.3.8 | `529ce4740c17` | — |
| `test_verify_toolkit.py` | v1.3.8 | `a1b46f5e0e74` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `REVIEW_PROTOCOL.md` | v7.4 | `8c56bf02ca59` | ○ |
| `TOOLS_MANIFEST.md` | v103 | `08c79cae5cfa` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `89f771682efd` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.83 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v103 이상.
2. **리뷰어**: REVIEW_PROTOCOL 은 `/tmp/rct` 의 7.4 만 읽는다. 프로젝트 파일에 남은 REVIEW_PROTOCOL·도구 사본(manifest v35)은 **사용자가 지운다**. 다음 회차부터 §4 의 새 2항(대표 영상 참여자 대조 · 새 정량 지표 정확도·반복성)을 체크리스트에 넣어 본다.

## 5. 검증하지 않은 것

- 문서만 — 실제 회차에서 새 2항을 써 보지 않았다.
- 바뀐 줄의 개인정보는 release.py 검사(이름·주제어·나이/성별 모양) + 사람 눈으로 봤다 — 나이·성별·회차·판 번호·지표 이름 없음.
