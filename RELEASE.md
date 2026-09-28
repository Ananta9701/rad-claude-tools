# RELEASE v2.43 — manifest v63 — 2026-09-28

> **v2.43** — `claim_graph selfcheck` ②′(RELEASE §3 대조)가 코드 전용 5개(`HISTORY.md`·`PRIVATE_TERMS.txt`·`CODE_PROJECT_README.md`·`release.py`·`GITHUB_README.md`)를 건너뛴다. 이 파일들은 이제 비공개 저장소에서 릴리스 사이에도 바뀌어, 코드 세션 시작 점검(`--role 코드`)이 이유를 아는 불일치를 냈다. 공개 파일 대조는 그대로. 다른 역할은 이 파일들을 받지 않으므로 동작이 같다. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 15.8.2 | selfcheck ②′ 에서 `CODE_ONLY` 5개를 뺀다. 테스트 1개 추가(성공 길: 코드 전용 해시가 모두 달라도 통과 · 실패 길: 공개 파일 해시가 다르면 여전히 ②′) |
| (코드 전용) `release.py` | — | `check` 의 RELEASE 표 해시 대조에서 같은 5개를 뺀다(비공개 저장소에 09-28 먼저 올림) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-28: 코드 전용 파일은 릴리스 사이에도 바뀐다 — 해시 대조에서 뺀다 | release.py check(비공개, 09-28)·claim_graph selfcheck ②′(이 판) |
| 영상의학 09-28 요청: Jacobson 어깨 그림 PNG | 도구 변경 없음 — Cowork(교과서) 일. `textbook.py page --pdf N --png` + 크기 줄이기·이름 바꾸기를 지시문으로(사용자가 Cowork 에 붙여 넣음) |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | ○ |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | ○ |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v63 | `112cfb28ae18` | ○ |
| `RELEASE.md` | v2.43 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | ○ |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | ○ |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | ○ |
| `deck_toolkit.py` | v16.37 | `75507c4a9834` | — |
| `test_toolkit.py` | v16.37 | `4a9355ac210d` | — |
| `DECK_SPEC.md` | v16.37 | `d5b88da3990f` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v63 | `112cfb28ae18` | ○ |
| `RELEASE.md` | v2.43 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | ○ |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | ○ |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v63 | `112cfb28ae18` | ○ |
| `RELEASE.md` | v2.43 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v63 | `112cfb28ae18` | ○ |
| `RELEASE.md` | v2.43 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.4 | `1fe34738bcc8` | — |
| `test_literature.py` | v0.4 | `660b68142ab7` | — |
| `LITERATURE.md` | v0.4 | `42e9bcc9e1c6` | — |
| `TOOLS_MANIFEST.md` | v63 | `112cfb28ae18` | ○ |
| `RELEASE.md` | v2.43 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | ○ |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | ○ |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | ○ |
| `deck_toolkit.py` | v16.37 | `75507c4a9834` | — |
| `test_toolkit.py` | v16.37 | `4a9355ac210d` | — |
| `DECK_SPEC.md` | v16.37 | `d5b88da3990f` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `literature.py` | v0.4 | `1fe34738bcc8` | — |
| `test_literature.py` | v0.4 | `660b68142ab7` | — |
| `LITERATURE.md` | v0.4 | `42e9bcc9e1c6` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v63 | `112cfb28ae18` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `30889519cbe9` | ○ |
| `release.py` | — | `a5dad4e3e398` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.43 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: GitHub 에서 받은 뒤 `claim_graph.py selfcheck --tests` 로 manifest v63 · claim_graph 15.8.2 를 확인한다. 쓰는 법은 바뀌지 않았다.
2. 코드 세션: 세션 시작 점검에서 코드 전용 파일 ②′ 불일치가 더 나오지 않는지 본다.

## 5. 검증하지 않은 것

- 공개 저장소 main 직접 push — v2.42 는 사용자가 웹에서 올렸다(세션 push 는 아직). 이 판에서 해 보고, 막히면 가지로 올리고 사용자가 Merge.
