# RELEASE v2.82 — manifest v102 — 2026-10-01

> **v2.82** — 문서만: `REVIEW_PROTOCOL` 7.3 — §10 리뷰어 프로젝트 파일 규칙 v5. 도구는 GitHub 세트로만(프로젝트 도구 사본은 뺀다 · GitHub 이 안 되면 심사를 시작하지 않는다) · 회차 원고·Supplementary 는 새 대화마다 docx 첨부 · 그림 sha 는 docx 안 그림 기준. 코드 동작 변경 없음.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `REVIEW_PROTOCOL.md` | 7.3 | §10 v5 — 첫 문단: 진본은 GitHub 세트 `TOOLS_MANIFEST.md`, 세션 시작은 `selfcheck --role 리뷰어 --tests`, 실패·GitHub 불가면 심사 시작 안 함 · "둔다" 에서 `claim_graph.py`·`test_claim_graph.py`·`CLAIM_GRAPH.md`·`TOOLS_MANIFEST` 와 회차 원고·Supplementary 를 뺌 · 새 "대화마다 첨부"(회차 원고·Supplementary docx) · 새 "그림 sha"(docx 안 그림 기준) · "뺀다" 에 프로젝트에 남은 도구 사본 전부 · §9 변경 이력 v7.3. 그 밖의 절은 그대로 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 부관리자 지시 10-01 `리뷰규약10절_v1` 1~5 (근거: 저자 `261001_회신_저자to부관리자_리뷰어프로젝트점검_v1`) | 위 §10 v5. 5번 그림 sha 는 §10 에 둠 — HANDOFF_FORMAT 은 발표 덱 넘김 규약이라 원고 그림과 맞지 않음 |
| 같은 지시 6번: 판·release | 공개 파일이 바뀌므로 판(v2.82). 코드·테스트 변경 없음 |

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
| `TOOLS_MANIFEST.md` | v102 | `a7cd8e8e1272` | ○ |
| `RELEASE.md` | v2.82 | — | 이 문서 |

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
| `TOOLS_MANIFEST.md` | v102 | `a7cd8e8e1272` | ○ |
| `RELEASE.md` | v2.82 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.23 | `e6c4243ade62` | — |
| `test_claim_graph.py` | v16.23 | `b40e84e1314b` | — |
| `CLAIM_GRAPH.md` | v16.23 | `0410c30e4f71` | — |
| `REVIEW_PROTOCOL.md` | v7.3 | `a186eacaf621` | ○ |
| `TOOLS_MANIFEST.md` | v102 | `a7cd8e8e1272` | ○ |
| `RELEASE.md` | v2.82 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v102 | `a7cd8e8e1272` | ○ |
| `RELEASE.md` | v2.82 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `TOOLS_MANIFEST.md` | v102 | `a7cd8e8e1272` | ○ |
| `RELEASE.md` | v2.82 | — | 이 문서 |

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
| `REVIEW_PROTOCOL.md` | v7.3 | `a186eacaf621` | ○ |
| `TOOLS_MANIFEST.md` | v102 | `a7cd8e8e1272` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `7468be046be4` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.82 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v102 이상.
2. **리뷰어**: 프로젝트 파일에서 도구 사본(`claim_graph.py`·`test_claim_graph.py`·`CLAIM_GRAPH.md`·`TOOLS_MANIFEST*`·구판 사본 — 지금 manifest v35)과 회차 원고·Supplementary docx 를 **사용자가 지운다**. 새 REVIEW_PROTOCOL(7.3)을 프로젝트에 올린다. 회차 원고는 새 대화마다 docx 첨부. 지운 뒤에도 `selfcheck --compare /mnt/project` 는 "다름 — 받은 것을 쓴다" 한 줄만 낸다(실패 아님).

## 5. 검증하지 않은 것

- 리뷰어 프로젝트에서 실제로 지운 뒤 selfcheck 를 돌리지 않았다 — `--compare` 가 정보 한 줄이라는 것은 코드로만 확인.
- "둔다" 의 Figure(프로젝트에 올린 jpg)는 재인코딩되지만 지시대로 그대로 둠 — 눈으로 보는 참고용이고 sha 대조는 docx 안 그림으로 한다.
