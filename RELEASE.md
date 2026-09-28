# RELEASE v2.47 — manifest v67 — 2026-09-28

> **v2.47** — 거짓 "통과" 세 가지(코드 리뷰 09-28 ③)와 추적 변경 이동 표지 안전장치. deck_toolkit 16.38 · claim_graph 15.8.3 · verify_toolkit 1.3.6. **Cowork 등 validate.py 가 없는 곳에서 `verify` 가 이제 "통과" 대신 "검증 못 함" 을 말한다**(종료 코드는 0 — 실패만 1). 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.38 | `Deck.order`: sldId 를 속성 순서·공백과 무관하게 읽고, 읽지 못한 sldId 가 있으면 **멈춘다**(전에는 `" />"` 하나로 0장 — 오류 없음). `validate`: validate.py 가 없으면 `None` 과 "검증 못 함 — 통과가 아니다"(전에는 `True`), 자리는 handoff 와 같은 `HANDOFF_VALIDATE_PY` 를 따른다. CLI 의 `verify:` 줄이 통과·실패·검증 못 함 셋 중 하나 |
| `claim_graph.py` | 15.8.3 | `selfcheck`: manifest 판을 읽지 못하면 1단계 실패(전에는 판 없음 = 판 없음으로 "통과 — 작업 시작 가능") |
| `verify_toolkit.py` | 1.3.6 | 추적 변경: 이동 표지(`moveFrom`·`moveTo`)가 있으면 정리하지 않고 **멈춘다**("Word 에서 직접 적용"), 결과 파일을 쓰지 않는다. `scan_track_changes` 가 이동 수(`moves`)를 알린다 |
| 테스트 | — | 시험 4개(성공·실패 두 쪽). `test_toolkit` 의 validate 확인 55줄은 "실패가 아니면" 으로 — validate.py 가 있는 곳·없는 곳 모두 같은 통과 수(185) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 코드 리뷰 ③-4 `Deck.order` 가 조용히 0장 | 재현(고치기 전 `[]`) → 고침 |
| 코드 리뷰 ③-5 validate 없음 = 통과 | 재현(고치기 전 `True`, 말 없음) → `None`·"검증 못 함" |
| 코드 리뷰 ③-6 selfcheck 빈 manifest 통과 | 재현(고치기 전 `ok: True`) → 1단계 실패 |
| 사용자 09-28: 이동 표지는 처리하지 말고 멈춤 | 재현(고치기 전 멈추지 않음) → 멈춤 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.3 | `5a24115bec26` | ○ |
| `test_claim_graph.py` | v15.8.3 | `802dfce23228` | ○ |
| `CLAIM_GRAPH.md` | v15.8.3 | `df34a36ca19e` | ○ |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | ○ |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | ○ |
| `TOOLS_MANIFEST.md` | v67 | `837eb0e0cbd1` | ○ |
| `RELEASE.md` | v2.47 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.3 | `5a24115bec26` | ○ |
| `test_claim_graph.py` | v15.8.3 | `802dfce23228` | ○ |
| `CLAIM_GRAPH.md` | v15.8.3 | `df34a36ca19e` | ○ |
| `deck_toolkit.py` | v16.38 | `fca83692b92e` | ○ |
| `test_toolkit.py` | v16.38 | `2cbd4a5ce163` | ○ |
| `DECK_SPEC.md` | v16.38 | `6277e06ed237` | ○ |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v67 | `837eb0e0cbd1` | ○ |
| `RELEASE.md` | v2.47 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.3 | `5a24115bec26` | ○ |
| `test_claim_graph.py` | v15.8.3 | `802dfce23228` | ○ |
| `CLAIM_GRAPH.md` | v15.8.3 | `df34a36ca19e` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v67 | `837eb0e0cbd1` | ○ |
| `RELEASE.md` | v2.47 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.6 | `505e14289fd2` | — |
| `test_textbook.py` | v0.6 | `29298da49346` | — |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | — |
| `TOOLS_MANIFEST.md` | v67 | `837eb0e0cbd1` | ○ |
| `RELEASE.md` | v2.47 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.5 | `9a4167578ad4` | — |
| `test_literature.py` | v0.5 | `30c01cdb3ac1` | — |
| `LITERATURE.md` | v0.5 | `ce1ea0cade3d` | — |
| `TOOLS_MANIFEST.md` | v67 | `837eb0e0cbd1` | ○ |
| `RELEASE.md` | v2.47 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.3 | `5a24115bec26` | ○ |
| `test_claim_graph.py` | v15.8.3 | `802dfce23228` | ○ |
| `CLAIM_GRAPH.md` | v15.8.3 | `df34a36ca19e` | ○ |
| `deck_toolkit.py` | v16.38 | `fca83692b92e` | ○ |
| `test_toolkit.py` | v16.38 | `2cbd4a5ce163` | ○ |
| `DECK_SPEC.md` | v16.38 | `6277e06ed237` | ○ |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | ○ |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | ○ |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.6 | `505e14289fd2` | — |
| `test_textbook.py` | v0.6 | `29298da49346` | — |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | — |
| `literature.py` | v0.5 | `9a4167578ad4` | — |
| `test_literature.py` | v0.5 | `30c01cdb3ac1` | — |
| `LITERATURE.md` | v0.5 | `ce1ea0cade3d` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v67 | `837eb0e0cbd1` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `a3b4bf8a80b5` | ○ |
| `release.py` | — | `a6cdc6064a0b` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.47 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v67 이상 확인. **validate.py 가 없는 곳(Cowork 등)은 `verify` 결과가 "검증 못 함" 으로 바뀐다 — 실패가 아니다**(종료 코드 0). 회신에는 "검증 못 함" 을 그대로 적는다.
2. 저자: 이동(`moveFrom`·`moveTo`)이 있는 원고는 추적 변경 정리가 멈춘다 — Word 에서 직접 적용.

## 5. 검증하지 않은 것

- 실제 덱에 sldId 속성 순서·공백이 다른 것이 있는지(시험 fixture 로만).
- `pack`·`restyle`·`polish` 는 여전히 validate 결과를 버린다(종료 코드에 반영 안 함 — 코드 리뷰 15번, 다음에).
