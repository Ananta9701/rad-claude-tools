# RELEASE v2.87 — manifest v107 — 2026-10-04

> **v2.87** — `DECK_SPEC` 16.54(문서만): 전평 풀이 덱의 풀이자 표기 규칙과 대본 보강 두 가지. 도구 동작 변경 없음.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `DECK_SPEC.md` | 16.54 | §0 A-4 에 "대본 보강 두 가지" 한 줄 — ① 원작자 화면에 정답이 아닌 보기를 풀이한 내용이 있으면 대본에서도 그 보기를 설명 ② 해설 화면의 강조 색 문구는 대본에서 꼭 말함(화면 글에서 가져오고 지어내지 않음, 늘어나면 숨김으로 맞춤). §0 B-3 의 "발표자 표기 상자" 줄을 풀이자 표기 규칙으로 바꿈 — 문항마다 한 번, 정답이 빨간 첫 화면의 좌측 하단, 한 줄·폭 2000000 EMU, 문제·해설·재게시·숨긴 화면의 표기는 지움, 좌측 하단이 그림·글을 덮으면 원래 자리에 두고 보고 |
| `deck_toolkit.py` · `test_toolkit.py` | 16.54 | 판 번호만(DECK_SPEC 짝) — 동작 변경 없음 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 10-04 — 전평 덱 작업에서 정한 규칙 두 가지를 다음 덱(10/14)부터 | 위 16.54. 같은 규칙을 영상의학 작업규약에도 넣어 달라고 따로 요청함 |

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
| `TOOLS_MANIFEST.md` | v107 | `a281dc7b0500` | ○ |
| `RELEASE.md` | v2.87 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.54 | `71b8a1bfa924` | ○ |
| `test_toolkit.py` | v16.54 | `217fa50a4cc6` | ○ |
| `DECK_SPEC.md` | v16.54 | `724b3edaa739` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v107 | `a281dc7b0500` | ○ |
| `RELEASE.md` | v2.87 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v107 | `a281dc7b0500` | ○ |
| `RELEASE.md` | v2.87 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v107 | `a281dc7b0500` | ○ |
| `RELEASE.md` | v2.87 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `TOOLS_MANIFEST.md` | v107 | `a281dc7b0500` | ○ |
| `RELEASE.md` | v2.87 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.54 | `71b8a1bfa924` | ○ |
| `test_toolkit.py` | v16.54 | `217fa50a4cc6` | ○ |
| `DECK_SPEC.md` | v16.54 | `724b3edaa739` | ○ |
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
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v107 | `a281dc7b0500` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `fb633ef7d4a4` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.87 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v107 이상.
2. **발표**: 다음 전평 덱부터 DECK_SPEC §0 A-4 의 대본 보강 두 가지와 §0 B-3 의 풀이자 표기 규칙을 따른다(체크리스트 두 줄).

## 5. 검증하지 않은 것

- 문서만 바뀐 판이다 — 규칙 문장은 HN 덱(v19·v20)에 손으로 적용한 결과에서 옮겼고, 이 규칙을 자동으로 검사하는 도구는 아직 없다(`lint`·`audit` 검사 안은 다음 판 후보).
