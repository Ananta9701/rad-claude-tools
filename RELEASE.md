# RELEASE v2.48 — manifest v68 — 2026-09-29

> **v2.48** — validate.py 가 없는 곳(Cowork 등)의 **가벼운 대체 검사**(사용자 09-29). v2.47 은 없으면 "검증 못 함" 이라고만 했다 — 이제 zip 이 온전한지, 모든 XML·rels 가 제대로 닫혔는지(파싱), python-pptx 로 다시 열리는지를 보고 **"구조 검사 통과(정밀 검사 없음)"**(종료 코드 0) 또는 **"구조 검사 실패"**(종료 코드 1). 덱 적용(handoff apply)도 전에는 검사를 건너뛰었는데 이제 같은 검사를 거친다. deck_toolkit 16.39 · handoff 2.1. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.39 | `structure_check(pptx)` 새로. `validate`: validate.py 가 없으면 구조 검사 — 통과 `None`("구조 검사 통과(정밀 검사 없음)"), 실패 `False`("구조 검사 실패" + 걸린 곳). `verify` CLI 는 실패만 종료 코드 1 |
| `handoff.py` | 2.1 | `apply` 가 validate.py 가 없어도 `T.validate` 를 부른다(구조 검사). 보고의 validate 칸: 통과 / **실패** / 구조 검사 통과(정밀 검사 없음) — 전에는 "건너뜀" |
| 테스트 | — | test_toolkit 1(깨진 XML·깨진 zip → 실패·종료 코드 1, 온전한 덱 → 구조 검사 통과), test_handoff 1 늘림(구조 검사 통과 문구, 결과 덱이 망가졌을 때 valid False·"실패" — 전에는 이 실패 길 시험이 없었다) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-29: "검증 못 함" 종료 코드는 0 유지, 대신 가벼운 대체 검사 | 재현(고치기 전: 깨진 덱도 None "검증 못 함", handoff 는 "건너뜀") → 구조 검사. 통과는 0, 실패는 1 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.3 | `5a24115bec26` | — |
| `test_claim_graph.py` | v15.8.3 | `802dfce23228` | — |
| `CLAIM_GRAPH.md` | v15.8.3 | `df34a36ca19e` | — |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `TOOLS_MANIFEST.md` | v68 | `d5b33da04f06` | ○ |
| `RELEASE.md` | v2.48 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.3 | `5a24115bec26` | — |
| `test_claim_graph.py` | v15.8.3 | `802dfce23228` | — |
| `CLAIM_GRAPH.md` | v15.8.3 | `df34a36ca19e` | — |
| `deck_toolkit.py` | v16.39 | `9439ee8e900c` | ○ |
| `test_toolkit.py` | v16.39 | `a1459b79664a` | ○ |
| `DECK_SPEC.md` | v16.39 | `fbb948b8e736` | ○ |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | ○ |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | ○ |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | ○ |
| `TOOLS_MANIFEST.md` | v68 | `d5b33da04f06` | ○ |
| `RELEASE.md` | v2.48 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.3 | `5a24115bec26` | — |
| `test_claim_graph.py` | v15.8.3 | `802dfce23228` | — |
| `CLAIM_GRAPH.md` | v15.8.3 | `df34a36ca19e` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v68 | `d5b33da04f06` | ○ |
| `RELEASE.md` | v2.48 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.6 | `505e14289fd2` | — |
| `test_textbook.py` | v0.6 | `29298da49346` | — |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | — |
| `TOOLS_MANIFEST.md` | v68 | `d5b33da04f06` | ○ |
| `RELEASE.md` | v2.48 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.5 | `9a4167578ad4` | — |
| `test_literature.py` | v0.5 | `30c01cdb3ac1` | — |
| `LITERATURE.md` | v0.5 | `ce1ea0cade3d` | — |
| `TOOLS_MANIFEST.md` | v68 | `d5b33da04f06` | ○ |
| `RELEASE.md` | v2.48 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.3 | `5a24115bec26` | — |
| `test_claim_graph.py` | v15.8.3 | `802dfce23228` | — |
| `CLAIM_GRAPH.md` | v15.8.3 | `df34a36ca19e` | — |
| `deck_toolkit.py` | v16.39 | `9439ee8e900c` | ○ |
| `test_toolkit.py` | v16.39 | `a1459b79664a` | ○ |
| `DECK_SPEC.md` | v16.39 | `fbb948b8e736` | ○ |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | ○ |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | ○ |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | ○ |
| `textbook.py` | v0.6 | `505e14289fd2` | — |
| `test_textbook.py` | v0.6 | `29298da49346` | — |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | — |
| `literature.py` | v0.5 | `9a4167578ad4` | — |
| `test_literature.py` | v0.5 | `30c01cdb3ac1` | — |
| `LITERATURE.md` | v0.5 | `ce1ea0cade3d` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v68 | `d5b33da04f06` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `8a38b02ee3fc` | ○ |
| `release.py` | — | `a6cdc6064a0b` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.48 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표(Cowork 포함): selfcheck 로 manifest v68 이상 확인. validate.py 가 없는 곳의 `verify`·덱 적용 보고는 **"구조 검사 통과(정밀 검사 없음)"** 또는 **"구조 검사 실패"** 다. 실패면 종료 코드 1 — 그 덱은 쓰지 않고 `to코드` 에 도구회신.
2. 다른 역할: 할 일 없음.

## 5. 검증하지 않은 것

- 구조 검사는 스키마·관계(rels 대상이 실제로 있는지 등)를 보지 않는다 — PowerPoint 가 "복구" 를 묻는 덱 중 일부는 통과할 수 있다(정밀 검사 아님).
- 큰 덱(수백 MB)에서 걸리는 시간은 재지 않았다.
