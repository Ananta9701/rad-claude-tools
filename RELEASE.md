# RELEASE v2.93 — manifest v113 — 2026-10-15

> **v2.93** — `DECK_SPEC.md` 16.57(문서만): AI 가 그려 낸 그림 · 모식도에 'AI 생성' 표시(§0 A-3). `deck_toolkit.py` 는 판 번호만.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `DECK_SPEC.md` · `deck_toolkit.py` · `test_toolkit.py` | 16.57 | §0 A-3 에 한 줄(사용자 10-15): AI 가 그려 낸 그림과 모식도에는 화면에 'AI 생성' 이라고 표시 · 흐름도 · 표 · 그래프는 사실만 담으므로 표시하지 않음 · 해부 · 영상 소견 그림은 생성하지 않음. 원작자 그림 · 교과서 그림 · 실제 영상은 해당 없음 · 표시는 그림 오른쪽 아래 작은 글자 한 줄. 다음 덱부터. 동작 변경 없음 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 부관리자 지시 `AI연수적용묶음_v1` 1 · 회신 `덱규칙표시범위_v1`(10-15) — DECK_SPEC AI 그림 표시 한 줄 · 표시 범위 | 그대로(사용자 코드 창 "해" 10-15) |

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
| `TOOLS_MANIFEST.md` | v113 | `a401ac13ed1d` | ○ |
| `RELEASE.md` | v2.93 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.57 | `4e2cdbe4cf48` | ○ |
| `test_toolkit.py` | v16.57 | `af948f478617` | ○ |
| `DECK_SPEC.md` | v16.57 | `d98772d96308` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v113 | `a401ac13ed1d` | ○ |
| `RELEASE.md` | v2.93 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v113 | `a401ac13ed1d` | ○ |
| `RELEASE.md` | v2.93 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.8.2 | `aee9c78eb534` | — |
| `test_textbook.py` | v0.8.2 | `2d8efa6d0cb5` | — |
| `TEXTBOOK.md` | v0.8.2 | `01e49ab0c032` | — |
| `TOOLS_MANIFEST.md` | v113 | `a401ac13ed1d` | ○ |
| `RELEASE.md` | v2.93 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.7 | `e2b37c4419db` | — |
| `test_literature.py` | v0.8.7 | `7b5df6c4f42e` | — |
| `LITERATURE.md` | v0.8.7 | `14fbd3d2b676` | — |
| `TOOLS_MANIFEST.md` | v113 | `a401ac13ed1d` | ○ |
| `RELEASE.md` | v2.93 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.57 | `4e2cdbe4cf48` | ○ |
| `test_toolkit.py` | v16.57 | `af948f478617` | ○ |
| `DECK_SPEC.md` | v16.57 | `d98772d96308` | ○ |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | — |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.8.2 | `aee9c78eb534` | — |
| `test_textbook.py` | v0.8.2 | `2d8efa6d0cb5` | — |
| `TEXTBOOK.md` | v0.8.2 | `01e49ab0c032` | — |
| `literature.py` | v0.8.7 | `e2b37c4419db` | — |
| `test_literature.py` | v0.8.7 | `7b5df6c4f42e` | — |
| `LITERATURE.md` | v0.8.7 | `14fbd3d2b676` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v113 | `a401ac13ed1d` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `20719642d42b` | ○ |
| `release.py` | — | `3ff520faf69b` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `5902bac98881` | — |
| `RELEASE.md` | v2.93 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v113 이상.
2. **발표**: 다음 덱부터 AI 가 그려 낸 그림 · 모식도에 'AI 생성' 표시(DECK_SPEC §0 A-3 · 16.57). 해부 · 영상 소견 그림은 생성하지 않는다. 이미 끝난 덱은 고치지 않는다.

## 5. 검증하지 않은 것

- 문서만 — 이 줄을 따른 덱은 아직 없다(다음 덱에서 처음). 표시 여부를 세는 검사 도구는 없다.
