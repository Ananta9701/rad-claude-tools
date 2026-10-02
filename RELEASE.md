# RELEASE v2.84 — manifest v104 — 2026-10-02

> **v2.84** — 문서·도움말 문장만: `REVIEW_PROTOCOL` 7.5 §10 — Figure(그림)는 프로젝트에 두지 않고 대화마다 첨부(xlsx·csv 는 그대로 둔다) · 낡은 "프로젝트 파일에 도구 사본" 문장을 GitHub 세트(`/tmp/rct`) 방식으로(`DECK_SPEC` 16.52 · `CLAIM_GRAPH` 16.24 · `TOOLS_MANIFEST` · `verify_toolkit` 1.3.9 머리말). 코드 동작 변경 없음 — claim_graph 는 `selfcheck --dir` 도움말 한 줄만.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `REVIEW_PROTOCOL.md` | 7.5 | §10 **둔다** 에서 Figure 를 뺌 — **대화마다 첨부** 에 "원고·Supplementary 한 판본과 Figure(그림)"(프로젝트에 올린 그림은 축소·재압축된다). 원자료 xlsx·csv 는 원본 그대로 올라가므로 둔다 |
| `DECK_SPEC.md` · `deck_toolkit.py` · `test_toolkit.py` | 16.52 | 첫머리 "이 문서와 `deck_toolkit.py` 를 프로젝트 지식에 넣어두고" → 세션 시작 때 GitHub 세트에서 받아 참조. 코드는 판만 |
| `CLAIM_GRAPH.md` · `claim_graph.py` · `test_claim_graph.py` | 16.24 | §5-2 "리뷰어 프로젝트에는 도구 회신·claim_graph.py… 만 올린다" → 리뷰어는 도구·규약을 GitHub 세트로만(REVIEW_PROTOCOL §10) · "사본은 릴리스 노트로 배포" → 각 역할이 GitHub 세트를 받아 selfcheck 로 대조 · 명령 표 `selfcheck [--dir /mnt/project]` → `[--dir /tmp/rct] [--role 역할]` · `selfcheck --dir` 도움말 "프로젝트에서는 /mnt/project" → "GitHub 세트면 /tmp/rct" |
| `TOOLS_MANIFEST.md` | v104 | §2 아래 "코드 프로젝트 파일에는 코드 전용 5개만" → 코드는 Claude Code 세션(공개·비공개 저장소), 프로젝트 파일 안 씀 · §3 한 명령 `--dir /mnt/project` → `/tmp/rct … --role {역할}` · 2단계 "프로젝트 파일의 판 표기" → "받은 세트 파일의 판 표기" |
| `verify_toolkit.py` · `test_verify_toolkit.py` | 1.3.9 | 머리말 "프로젝트 지식에 업로드 → /mnt/project/verify_toolkit.py 를 view 로" → GitHub 세트 `/tmp/rct` 에서 바로 실행. 코드는 판만 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 부관리자 지시 10-02 `전체지침v7정리판_v1` C 1번: REVIEW_PROTOCOL §10 "둔다: … Figure" | 위 7.5 |
| 같은 지시 C 2번: 낡은 도구 사본 문장(DECK_SPEC 23행 · CLAIM_GRAPH 486행 · TOOLS_MANIFEST 68행 · verify_toolkit 머리) | 위. grep 으로 같은 꼴을 더 찾아 CLAIM_GRAPH 487행·433행, TOOLS_MANIFEST 51행·71행, claim_graph `--dir` 도움말도 고침 |
| 같은 grep 에서 **고치지 않은 것** | 발표의 `--compare /mnt/project`(README 12·18행, DECK_SPEC "세션 시작" 절 "프로젝트 파일의 도구는 예비로만 둔다", claim_graph `--compare` 도움말·docstring) — 발표는 아직 프로젝트 사본을 **예비**로 대조하는 지금 방식이라 낡은 문장이 아님. 뺄지는 따로 정할 일 · 테스트·deck_toolkit 의 `/mnt/project … __pycache__` 주석 — 대화창에서 돌 때를 위한 이유 설명 |
| 같은 지시 C 3번: DECK_SPEC "원본 pptx 보관" | 보고만(고치지 않음) |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | ○ |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | ○ |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | ○ |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | ○ |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | ○ |
| `TOOLS_MANIFEST.md` | v104 | `13527522bf72` | ○ |
| `RELEASE.md` | v2.84 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | ○ |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | ○ |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | ○ |
| `deck_toolkit.py` | v16.52 | `fd63018fe975` | ○ |
| `test_toolkit.py` | v16.52 | `3bef3c5c6f90` | ○ |
| `DECK_SPEC.md` | v16.52 | `852650b149a3` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v104 | `13527522bf72` | ○ |
| `RELEASE.md` | v2.84 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | ○ |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | ○ |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | ○ |
| `REVIEW_PROTOCOL.md` | v7.5 | `5b4961094b0c` | ○ |
| `TOOLS_MANIFEST.md` | v104 | `13527522bf72` | ○ |
| `RELEASE.md` | v2.84 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v104 | `13527522bf72` | ○ |
| `RELEASE.md` | v2.84 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `TOOLS_MANIFEST.md` | v104 | `13527522bf72` | ○ |
| `RELEASE.md` | v2.84 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | ○ |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | ○ |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | ○ |
| `deck_toolkit.py` | v16.52 | `fd63018fe975` | ○ |
| `test_toolkit.py` | v16.52 | `3bef3c5c6f90` | ○ |
| `DECK_SPEC.md` | v16.52 | `852650b149a3` | ○ |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | ○ |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `REVIEW_PROTOCOL.md` | v7.5 | `5b4961094b0c` | ○ |
| `TOOLS_MANIFEST.md` | v104 | `13527522bf72` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `3937ba1210b3` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.84 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v104 이상. 동작 변경 없음.
2. **리뷰어**: REVIEW_PROTOCOL 7.5 — 다음 회차부터 Figure 도 원고와 같이 대화에 첨부한다. 프로젝트에 남은 Figure 는 **사용자가 지운다**(원자료 xlsx·csv 는 둔다).

## 5. 검증하지 않은 것

- 문서만 — 리뷰어 실제 회차에서 Figure 첨부를 써 보지 않았다.
- 바뀐 줄의 개인정보는 release.py 검사(이름·주제어·나이/성별 모양) + 사람 눈으로 봤다 — 나이·성별·회차·판 번호·지표 이름 없음.
