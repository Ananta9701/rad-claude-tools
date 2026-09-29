# RELEASE v2.69 — manifest v89 — 2026-09-29

> **v2.69** — `gaps` 2부 제목에 1부로 간 겹친 수(사용자 09-29 다음 할 일 ③). 실물 v9 에서 머리 줄은 "인용 있음 6" 인데 2부 제목은 "2개" 였다 — 나머지 4개는 약한 고리·외톨이와 겹쳐 1부에 있었는데 표에 그 말이 없었다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.11 | `gaps` 작업표: 인용 있음 주장 중 다른 공백과 겹쳐 1부에 간 것이 있으면 2부 제목 `## 2. 인용 있음 — sources 미기입 N개 (+ 다른 공백과 겹쳐 1부에 간 M개)`, 그 아래 `> 인용 있음 N+M개 중 M개는 … — G02 c4 · …. 그 주장도 인용 문헌 DOI 를 1부 받침 줄의 후보 DOI 칸에 적는다.` 겹친 것이 없으면 제목·표는 전과 같다. 표 줄(`--to-instr` 가 읽는 것)은 그대로 |
| `CLAIM_GRAPH.md` | 16.11 | §4-1 작업표 두 부분 설명에 한 줄 |
| 테스트 | — | test_claim_graph 1(겹친 2개가 제목·알림 줄에 G 번호와 함께, 머리 줄 4 = 2 + 2 · 겹친 것이 없으면 전과 같은 제목 · 채운 1부 받침 줄이 `--to-instr` 로 그대로 넘어감) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-29(다음 할 일 ③): gaps 2부 제목에 1부로 간 겹친 수 | 위 claim_graph 16.11 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.11 | `8ca9ab8c48a0` | ○ |
| `test_claim_graph.py` | v16.11 | `615898e1466a` | ○ |
| `CLAIM_GRAPH.md` | v16.11 | `27946885eb00` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v89 | `ca9237639693` | ○ |
| `RELEASE.md` | v2.69 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.11 | `8ca9ab8c48a0` | ○ |
| `test_claim_graph.py` | v16.11 | `615898e1466a` | ○ |
| `CLAIM_GRAPH.md` | v16.11 | `27946885eb00` | ○ |
| `deck_toolkit.py` | v16.47 | `8b1ab74de52c` | — |
| `test_toolkit.py` | v16.47 | `819595d18946` | — |
| `DECK_SPEC.md` | v16.47 | `61bbe8c12ef1` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v89 | `ca9237639693` | ○ |
| `RELEASE.md` | v2.69 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.11 | `8ca9ab8c48a0` | ○ |
| `test_claim_graph.py` | v16.11 | `615898e1466a` | ○ |
| `CLAIM_GRAPH.md` | v16.11 | `27946885eb00` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v89 | `ca9237639693` | ○ |
| `RELEASE.md` | v2.69 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v89 | `ca9237639693` | ○ |
| `RELEASE.md` | v2.69 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `d9049de45a40` | — |
| `TOOLS_MANIFEST.md` | v89 | `ca9237639693` | ○ |
| `RELEASE.md` | v2.69 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.11 | `8ca9ab8c48a0` | ○ |
| `test_claim_graph.py` | v16.11 | `615898e1466a` | ○ |
| `CLAIM_GRAPH.md` | v16.11 | `27946885eb00` | ○ |
| `deck_toolkit.py` | v16.47 | `8b1ab74de52c` | — |
| `test_toolkit.py` | v16.47 | `819595d18946` | — |
| `DECK_SPEC.md` | v16.47 | `61bbe8c12ef1` | — |
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
| `LITERATURE.md` | v0.8.5 | `d9049de45a40` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v89 | `ca9237639693` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `d3b1e1287a12` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.69 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v89 이상.
2. 저자: `gaps` 를 다시 돌리면 2부 제목에 "(+ 다른 공백과 겹쳐 1부에 간 N개)" 와 그 G 번호가 나온다 — 그 주장들도 인용 문헌 DOI 를 1부 받침 줄에 적는다.

## 5. 검증하지 않은 것

- 실물 저자 claims(v9)로는 다시 돌리지 않았다 — 가짜 그래프로 같은 모양(인용 있음 + 약한 고리)을 만들어 시험했다. 09-29 실물 수(머리 6 · 2부 2)라면 제목은 "2개 (+ … 4개)" 가 될 것으로 예상.
