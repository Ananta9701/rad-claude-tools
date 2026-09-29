# RELEASE v2.57 — manifest v77 — 2026-09-29

> **v2.57** — 작은 판. ① **pack·restyle·polish 가 검증 결과를 버리던 것**(코드 리뷰 ⑮): 검증 실패여도 종료 코드 0 이었고, `polish` 는 글자가 바뀌었다고 경고하면서도 저장했다 — deck_toolkit 16.42. ② **증례(case review) 모양 예시**(사용자 결정 09-29, 발표 (나)): `CLAIM_GRAPH.md` §3-2-1 에 가짜 증례로 소견 = evidence · 감별 = claim · 결론 = main · 배제 = rebuttal — claim_graph 16.4(문서만). 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.42 | `pack`·`restyle`·`polish` CLI: 검증(validate) 결과를 `저장: … / verify: 통과·실패·구조 검사 통과(정밀 검사 없음)` 로 적고, **실패면 종료 코드 1**. 검증 못 함(None)은 0(사용자 09-29 결정 그대로). `polish` 는 글자가 바뀌면(`text_intact` False) **저장하지 않고 1** |
| `DECK_SPEC.md` | 16.42 | 머리에 위 한 줄 |
| `CLAIM_GRAPH.md`·`claim_graph.py` | 16.4 | §3-2-1 증례 모양 예시(가짜 증례 — 소견 2 · 배제 1 · 감별 2 · 결론 1). 코드 동작 변화 없음(판만) |
| 테스트 | — | test_toolkit 2(재현 — 옛 코드: 검증 실패에도 0, 글자 바뀐 polish 결과를 저장 · 성공·실패·검증 못 함 세 길), test_claim_graph 1(문서 예시가 mapgraph [필수] 없음 · impact · mapdraw 반박 선으로 돈다) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 코드 리뷰 ⑮ 종료 코드 | 위 deck 16.42 |
| 발표 09-29 claims 관계 방향 → 사용자 결정: 증례 (나) · 구연 (가) · 전평·퀴즈 (다)+sources | 증례 예시는 이 판. 구연 "저자 claims 가져와 sites 만" 명령은 설계에 넣고 근거 공백 목록 다음 순서. `참고:` 줄 변환은 나중 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.4 | `80a275acf7eb` | ○ |
| `test_claim_graph.py` | v16.4 | `b3fab77dd514` | ○ |
| `CLAIM_GRAPH.md` | v16.4 | `48517447035a` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v77 | `b14920814da7` | ○ |
| `RELEASE.md` | v2.57 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.4 | `80a275acf7eb` | ○ |
| `test_claim_graph.py` | v16.4 | `b3fab77dd514` | ○ |
| `CLAIM_GRAPH.md` | v16.4 | `48517447035a` | ○ |
| `deck_toolkit.py` | v16.42 | `51c2c776af44` | ○ |
| `test_toolkit.py` | v16.42 | `f97534059e49` | ○ |
| `DECK_SPEC.md` | v16.42 | `cc1f82e171ea` | ○ |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v77 | `b14920814da7` | ○ |
| `RELEASE.md` | v2.57 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.4 | `80a275acf7eb` | ○ |
| `test_claim_graph.py` | v16.4 | `b3fab77dd514` | ○ |
| `CLAIM_GRAPH.md` | v16.4 | `48517447035a` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v77 | `b14920814da7` | ○ |
| `RELEASE.md` | v2.57 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `TOOLS_MANIFEST.md` | v77 | `b14920814da7` | ○ |
| `RELEASE.md` | v2.57 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | — |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | — |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | — |
| `TOOLS_MANIFEST.md` | v77 | `b14920814da7` | ○ |
| `RELEASE.md` | v2.57 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.4 | `80a275acf7eb` | ○ |
| `test_claim_graph.py` | v16.4 | `b3fab77dd514` | ○ |
| `CLAIM_GRAPH.md` | v16.4 | `48517447035a` | ○ |
| `deck_toolkit.py` | v16.42 | `51c2c776af44` | ○ |
| `test_toolkit.py` | v16.42 | `f97534059e49` | ○ |
| `DECK_SPEC.md` | v16.42 | `cc1f82e171ea` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | — |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | — |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v77 | `b14920814da7` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `8db6ee0a7198` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.57 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v77 이상.
2. 발표·발표 Cowork: `pack`·`restyle`·`polish` 가 이제 검증 실패 때 1 로 끝난다 — 스크립트로 이어 부르던 곳이 있으면 종료 코드를 본다. `polish` 가 "[멈춤] … 저장하지 않았다" 면 입력 덱을 그대로 두고 알린다.
3. 발표: 증례 claims 에 관계를 붙일 때 `CLAIM_GRAPH.md` §3-2-1 을 본다.

## 5. 검증하지 않은 것

- 실제 validate.py(pptx 스킬) 로는 돌리지 않았다 — 실패·통과를 흉내 내는 가짜 validate.py 로 종료 코드를 시험했다.
