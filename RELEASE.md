# RELEASE v2.94 — manifest v114 — 2026-10-16

> **v2.94** — `claim_graph.py` 16.25: `mapcheck` 가 evidence 글 속 표·그림 번호를 원고의 가장 큰 번호와 맞대 넘는 번호(옛 번호)를 [참고]로 알린다. 함께: `mapgraph` 의 caveat → role=rebuttal [참고] 를 한 줄로 · `oral sync` 가 [필수] 에서 멈출 때도 옛 스냅숏 안내를 먼저 · `test_claim_graph.py` 는 `/tmp` 대신 임시 폴더에 · selfcheck 가 죽은 시험의 stderr 끝 줄을 보임.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` · `test_claim_graph.py` · `CLAIM_GRAPH.md` | 16.25 | `mapcheck doc --claims` 가 늘 evidence 글 속 `Table N` · `Table SN` · `Supplementary Table SN` · `Figure N` · `Fig. SN` · `Suppl SN` 을 읽어, 원고(doc) 글에 나온 그 종류의 가장 큰 번호를 넘으면 주장마다 `[참고] id: evidence 의 표·그림 번호가 원고보다 큼 — Table S16(원고 보충 표 S15 까지)` 한 줄. 원고에 그 종류 번호가 없으면 한 줄로 모아 "맞대지 못함". 이어진 목록(`Tables S1–S15`)은 펼침 · 소수 · `eTable` 은 번호 아님 · superseded 는 안 봄 · `--nums-sep` 이면 앞쪽만. [참고]라 종료 코드는 그대로. 덱(`deck_toolkit mapcheck`)은 원고 글이 없어 바뀌지 않음(CLAIM_GRAPH §3-1 표 · §4) |
| 〃 | 16.25 | `mapgraph`: caveat 간선이 role=rebuttal 주장을 가리키는 [참고] 를 간선마다 내지 않고 한 줄로 — `caveat 간선이 role=rebuttal 주장을 가리킴 N개(a -> b, …)`(짝은 10개까지). 규약 · 기존 그래프는 그대로(출력만) |
| 〃 | 16.25 | `oral sync`: [필수] 에서 멈출 때도 옛 스냅숏(16.19 전)이면 맨 앞에 "간선 변화는 이번 sync 에서 보지 않는다" 한 줄 |
| 〃 | 16.25 | `test_claim_graph.py`: 임시 파일 47곳을 `/tmp` 대신 `tempfile` 폴더에 — `/tmp` 쓰기를 막은 샌드박스에서도 끝까지 돈다(시험 1개가 글 안 `/tmp` 경로를 막음) |
| 〃 | 16.25 | `selfcheck --tests`: 시험이 stdout 없이 죽으면(import 실패 등) "(출력 없음)" 대신 `stderr: …` 끝 줄. `release.py` 도 같은 함수를 쓴다 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 저자 회신 `분석근거매임셈_v1`(10-16) 덤 — evidence 의 옛 보충 번호(`Suppl Table S16` · 지금 S15 까지)가 mapcheck 에 안 걸림 | 그대로(넘는 번호). **범위 안에서 밀린 번호**(`Suppl S13` → 지금 S12)는 수로는 못 잡는다 — 고칠 때 `remap-refs --suppl` |
| 리뷰어 회신 `규약3-1과mapgraph참고_v1`(10-05) — 규약 §3-1 대로 쓴 그래프에서 [참고] 30 중 27 이 caveat → rebuttal 간선마다 | (가) 한 줄로 묶음(사용자 10-06 "추천대로"). (나) 규약 §3-1 고침은 투고 뒤 큰 판 후보로 둔다 |
| 발표 회신 `oralsync첫실물_v1`(10-05) 참고 — [필수] 에서 멈출 때도 옛 스냅숏 안내를 미리 | 그대로 |
| 저자 도구회신 `selfcheck테스트와validate자리_v1`(10-14) ① `test_claim_graph.py` 가 `/tmp` 에 써서 맥 Code 샌드박스에서 멈춤 | 그대로(`/tmp` 쓰기를 막고 옛 시험이 첫 줄에서 `PermissionError` 로 멈추는 것을 재현 → 새 시험은 끝까지) |
| 〃 ② `test_verify_toolkit.py` 는 맥 기본 3.9 에 python-docx 없음 | 코드 바꿈 없음 — 저자 시작 명령을 python-docx 가 있는 파이썬(작업 venv)으로. `test_verify_toolkit.py` 의 임시 폴더는 아직 `/tmp/vt_test` 가 기본이라 샌드박스에서는 `VT_TMP=<쓸 수 있는 폴더>` 를 함께(다음 verify 판에서 고침) |
| 〃 ③ selfcheck 가 시험 stderr 를 "출력 없음" 으로 보임 | 그대로(stderr 끝 줄) |
| 〃 ④ docx `validate.py` 맥 자리 물음 | 이 판에서 답하지 않음 — 따로 답한다 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.25 | `f32b407c6d5a` | ○ |
| `test_claim_graph.py` | v16.25 | `9d8780d6c279` | ○ |
| `CLAIM_GRAPH.md` | v16.25 | `29cfa86b7472` | ○ |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | — |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | — |
| `TOOLS_MANIFEST.md` | v114 | `93eb8829105a` | ○ |
| `RELEASE.md` | v2.94 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.25 | `f32b407c6d5a` | ○ |
| `test_claim_graph.py` | v16.25 | `9d8780d6c279` | ○ |
| `CLAIM_GRAPH.md` | v16.25 | `29cfa86b7472` | ○ |
| `deck_toolkit.py` | v16.57 | `4e2cdbe4cf48` | — |
| `test_toolkit.py` | v16.57 | `af948f478617` | — |
| `DECK_SPEC.md` | v16.57 | `d98772d96308` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v114 | `93eb8829105a` | ○ |
| `RELEASE.md` | v2.94 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.25 | `f32b407c6d5a` | ○ |
| `test_claim_graph.py` | v16.25 | `9d8780d6c279` | ○ |
| `CLAIM_GRAPH.md` | v16.25 | `29cfa86b7472` | ○ |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v114 | `93eb8829105a` | ○ |
| `RELEASE.md` | v2.94 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.8.2 | `aee9c78eb534` | — |
| `test_textbook.py` | v0.8.2 | `2d8efa6d0cb5` | — |
| `TEXTBOOK.md` | v0.8.2 | `01e49ab0c032` | — |
| `TOOLS_MANIFEST.md` | v114 | `93eb8829105a` | ○ |
| `RELEASE.md` | v2.94 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.7 | `e2b37c4419db` | — |
| `test_literature.py` | v0.8.7 | `7b5df6c4f42e` | — |
| `LITERATURE.md` | v0.8.7 | `14fbd3d2b676` | — |
| `TOOLS_MANIFEST.md` | v114 | `93eb8829105a` | ○ |
| `RELEASE.md` | v2.94 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.25 | `f32b407c6d5a` | ○ |
| `test_claim_graph.py` | v16.25 | `9d8780d6c279` | ○ |
| `CLAIM_GRAPH.md` | v16.25 | `29cfa86b7472` | ○ |
| `deck_toolkit.py` | v16.57 | `4e2cdbe4cf48` | — |
| `test_toolkit.py` | v16.57 | `af948f478617` | — |
| `DECK_SPEC.md` | v16.57 | `d98772d96308` | — |
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
| `TOOLS_MANIFEST.md` | v114 | `93eb8829105a` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `9a39ae0ba3c5` | ○ |
| `release.py` | — | `3ff520faf69b` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `5902bac98881` | — |
| `RELEASE.md` | v2.94 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v114 이상.
2. **저자**: 다음 `mapcheck` 때 새 [참고] 줄(표·그림 번호)을 보고 evidence 의 옛 번호를 고친다(claims v42). 원고 글은 바뀌지 않는다. 맥 Code 샌드박스에서도 `test_claim_graph.py` 가 돈다 — `test_verify_toolkit.py` 는 `VT_TMP` 를 함께.
3. **리뷰어**: evidence 에 재현 표 번호를 적는다면 `--nums-sep` 앞쪽만 본다 — 원고 쪽 번호만 맞댄다. `mapgraph` 의 caveat → rebuttal [참고] 는 이제 한 줄이다(세던 줄 수가 줄어든다).
4. **발표**: 할 일 없음(`oral sync` 출력 한 줄 더).

## 5. 검증하지 않은 것

- 실물 원고(docx)로는 돌리지 않았다 — 저자 claims v41 evidence 에서 번호를 뽑는 것만 확인(번호 있는 주장 28 · `Suppl Table S16` 한 곳이 보충 표 S15 까지에 걸림). 원고 글의 번호 셈은 시험 원고로만.
- 범위 안에서 밀린 번호와 빈 번호는 못 잡는다(설계 — 수만 봄).
