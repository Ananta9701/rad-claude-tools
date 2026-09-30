# RELEASE v2.77 — manifest v97 — 2026-09-30

> **v2.77** — 큰 방향 ④ 문헌 그래프 1판: 논문 한 편의 주장을 claims.json 으로(`kind: 문헌`, 자리 = 그 논문 paper.md). paper.md 를 literature `locate` 와 같은 규칙으로 읽어 줄바꿈·합자에 걸린 구절도 `doc:find` 로 찾는다 — `mapcheck` 가 AI 가 적은 구절이 원문에 있는지 본다. 발표 S1: `oral sync` 가 간선 변화를 알린다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.19 | `DocSource` — 쪽·절 표지가 있는 md 는 표지로 쪽을 나누고 빈 줄·`.`·`:` 로 끝난 줄에서 문단(locate 와 같음), `doc:find` 는 NFKC·띄어쓰기 무시(한 문단에만), `doc:sec` 은 표지, `mark_of(자리)` · `LIT_KINDS`(문헌) — mapgraph 가 caveat 없는 evidence·supersedes 없는 forbidden [참고] 를 끔 · `lit_graph_problems`: doi 없음·모양·meta.md doi 와 다름·id 에 `:#` 빈칸 [필수], doc≠doi·paper_sha 없음/다름·자리가 doc: 아님·사람 이름 꼴·판정 대기 수 [참고] — `mapgraph --claims` 가 kind 문헌이면 함께 · mapfreeze 는 문헌 그래프의 doc(DOI)을 paper.md 이름으로 바꾸지 않고, mapstale 은 이름 다름 경고를 하지 않음 · `oral_snapshot` 에 간선(`deps`), `oral sync` 가 쓴 주장·무대 밖 상류의 간선이 늘면 `… 에 caveat Y 가 새로 걸림 — 화면에 없음/화면 …`, 줄면 `… 에서 … 가 빠짐`, 옛 스냅숏이면 한 줄 |
| `CLAIM_GRAPH.md` | 16.19 | §3-8 새 절(문헌 그래프 1판) · §3-5 sync 간선 줄 |
| 테스트 | — | test_claim_graph 4(sync 간선 늘고 줄음·화면 있음/없음 / 그대로면 조용 / 옛 스냅숏 한 줄 · paper.md 줄바꿈·합자 구절 찾음, 다른 쪽 안 섞임, 표지, 없는 구절·모호 → 오류, 표지 없는 md 는 전처럼 · 문헌 그래프 검사 성공 / doi 없음·meta 다름·id # [필수] / paper_sha 다름·이름 꼴 [참고] 주장마다 한 줄 · CLI mapgraph·mapcheck·mapfreeze(kind 보존)·mapstale 그대로·원문 바뀜 [변경]·[필수] 종료 1) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-30: ④ 첫 실물 = 원고 v48 [42](보관소에 있음) · 저자 claims v11, 1판부터 | 위 1판. 실물 paper.md 로 자리 해석 확인은 아직(§5) |
| 발표 09-30 S1: 간선만 바뀐 저자 판에 oral sync 가 조용 | 스냅숏에 간선, 늘고 줄면 [참고] — 새로 걸린 쪽의 화면 유무까지 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.19 | `587deafdd6b7` | ○ |
| `test_claim_graph.py` | v16.19 | `d07ff106f90e` | ○ |
| `CLAIM_GRAPH.md` | v16.19 | `6d2c33a84a98` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v97 | `e31d74b3052b` | ○ |
| `RELEASE.md` | v2.77 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.19 | `587deafdd6b7` | ○ |
| `test_claim_graph.py` | v16.19 | `d07ff106f90e` | ○ |
| `CLAIM_GRAPH.md` | v16.19 | `6d2c33a84a98` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v97 | `e31d74b3052b` | ○ |
| `RELEASE.md` | v2.77 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.19 | `587deafdd6b7` | ○ |
| `test_claim_graph.py` | v16.19 | `d07ff106f90e` | ○ |
| `CLAIM_GRAPH.md` | v16.19 | `6d2c33a84a98` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v97 | `e31d74b3052b` | ○ |
| `RELEASE.md` | v2.77 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v97 | `e31d74b3052b` | ○ |
| `RELEASE.md` | v2.77 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `TOOLS_MANIFEST.md` | v97 | `e31d74b3052b` | ○ |
| `RELEASE.md` | v2.77 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.19 | `587deafdd6b7` | ○ |
| `test_claim_graph.py` | v16.19 | `d07ff106f90e` | ○ |
| `CLAIM_GRAPH.md` | v16.19 | `6d2c33a84a98` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
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
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v97 | `e31d74b3052b` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `33452087ae6b` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.77 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v97 이상.
2. 발표: 지금 덧붙임(v3)의 스냅숏에는 간선이 없다 — 다음 저자 판 sync 때 "옛 스냅숏" 한 줄이 나오고, 그 sync 부터 간선 변화를 알린다. 이번 v11 의 새 caveat(화면에 없는 것)은 발표 회신에 적은 대로 사람이 본다.
3. 문헌 그래프는 아직 쓰지 않는다 — 초안 역할·크기 등 사용자 결정(④ 설계안 §6) 뒤 지시가 간다.

## 5. 검증하지 않은 것

- **실물 paper.md**(PDF 글자층 — 조판마다 줄바꿈·하이픈·표가 다르다)로 자리 해석을 아직 돌리지 않았다. 가짜 paper.md(쪽 표지·물리적 줄·합자)로만. 첫 실물 논문(보관소에 있음)으로 코드 세션이 확인할 것.
- 줄 끝 하이픈으로 끊긴 낱말은 붙이지 않는다(locate 와 같음) — 실물에서 얼마나 걸리는지 모름.
- 사람 이름 꼴 검사는 네 가지 꼴만 — 이름만 따로 쓴 경우(`Kim reported`)는 못 잡는다.
