# RELEASE v2.42 — manifest v62 — 2026-09-28

> **v2.42** — 코드 프로젝트가 **Claude Code 웹**(claude.ai/code)으로 옮겨 간다(사용자 결정 09-28). 도구 코드는 v2.41 그대로 — 바뀐 것은 코드 전용 파일(release.py `publish`, HISTORY, 코드 README)과 이 문서·manifest 뿐. **이 판부터 zip 이 없다**: 코드 세션이 두 저장소에 직접 올린다(사용자 허용 뒤). 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| (코드 전용) `release.py` | — | `publish --release X.Y --out … --public-dir … --private-dir …` — build 세트를 공개 저장소 작업 사본에 그대로(세트에 없는 파일은 지움), 코드 전용 파일을 비공개 저장소에 넣고 커밋. push 는 사용자 허용 뒤 따로. Python 3.10 해석기 경로를 두 환경(대화창 컨테이너·웹 세션)에서 찾는다 |
| 공개 세트 | — | 도구·테스트·규격 문서 변경 없음(v2.41 과 같은 해시). `RELEASE.md`·`TOOLS_MANIFEST.md` 만 새 판 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-28: 코드 프로젝트를 Claude Code 웹으로 | 시험 4번 통과(전용 파이썬 환경에서 테스트 6종 전부 통과, Drive 도구로 전달함 읽기·쓰기, 비공개 저장소 main 직접 push, 공개 저장소는 세션에 추가해 push) — 비공개 저장소 `rad-claude-private` 에 지침(CLAUDE.md)·코드 전용 파일 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v62 | `9363113e0b50` | ○ |
| `RELEASE.md` | v2.42 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.37 | `75507c4a9834` | — |
| `test_toolkit.py` | v16.37 | `4a9355ac210d` | — |
| `DECK_SPEC.md` | v16.37 | `d5b88da3990f` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v62 | `9363113e0b50` | ○ |
| `RELEASE.md` | v2.42 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v62 | `9363113e0b50` | ○ |
| `RELEASE.md` | v2.42 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v62 | `9363113e0b50` | ○ |
| `RELEASE.md` | v2.42 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.4 | `1fe34738bcc8` | — |
| `test_literature.py` | v0.4 | `660b68142ab7` | — |
| `LITERATURE.md` | v0.4 | `42e9bcc9e1c6` | — |
| `TOOLS_MANIFEST.md` | v62 | `9363113e0b50` | ○ |
| `RELEASE.md` | v2.42 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
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
| `TOOLS_MANIFEST.md` | v62 | `9363113e0b50` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | ○ |
| `HISTORY.md` | — | `0364d23152b0` | ○ |
| `release.py` | — | `479a10425b4f` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.42 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: 도구 변경이 없으니 할 일 없음. 앞으로 도구회신은 지금처럼 Drive `to코드` 에 — 코드 세션이 읽는다. 릴리스는 GitHub 에 바로 올라가므로 "사용자가 올렸는지" 를 기다릴 필요가 없다(selfcheck 로 받은 커밋 확인).
2. 코드 프로젝트 파일(claude.ai): 옮긴 뒤에는 쓰지 않는다 — 진본은 비공개 저장소.

## 5. 검증하지 않은 것

- 공개 저장소 main 직접 push — 이 판을 올릴 때 처음 해 본다. 막히면 가지로 올리고 사용자가 Merge.
