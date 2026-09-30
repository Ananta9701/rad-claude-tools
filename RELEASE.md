# RELEASE v2.71 — manifest v91 — 2026-09-30

> **v2.71** — 구연 덧붙임 2판(사용자 09-30): 저자 판 따라가기 `oral sync` 와 화면 확인 기록(mapfreeze·mapstale)을 덧붙임에. 쓴 id 가 새 판에서 사라지면 스냅숏 해시로 후보를 보이고 `--pairs`·`--drop` 전까지 멈춘다. 저자 파일은 여전히 읽기만.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.13 | `oral sync --author 새판 --oral 덧붙임 -o 새덧붙임 [--pairs 옛=새] [--drop 옛,…]` — 같은 판이면 할 일 없음 · 쓴 주장 글 바뀜 [변경] · 새 주장·저자가 뺀 주장·무대 밖 상류 글 바뀜 [참고] · **쓴 id 가 없으면 [필수]**(원고 자리·keys 해시로 후보와 점수, `--pairs` 안내) · 새 판에서 철회된 쓴 주장 [필수] · 없는 새 id·철회된 주장으로 옮기기 [필수] — [필수] 면 덧붙임을 쓰지 않는다. 옮긴 주장은 확인 기록 없이, 1:N 은 같은 화면을 둘에, 발표 주장 `p-` 의 기댐도 따라간다. `synced` 이력. 합칠 때 무대 밖 상류는 덧붙임의 `offstage_verified` 로 확인 기록을 가진다 |
| `deck_toolkit.py` | 16.49 | `mapfreeze 덱 --oral … --author … -o 덧붙임` — 확인 기록을 덧붙임에(`use[id].verified` · 발표 주장 · `offstage_verified`). `mapstale 덱 --oral … --author …` — 화면·저자 글·무대 밖 받침 바뀜을 잡는다(받침이 바뀌면 기대는 화면까지) |
| `CLAIM_GRAPH.md` · `DECK_SPEC.md` | 16.13 · 16.49 | §3-5 저자 판 따라가기·화면 확인 기록, 명령표 · 머리 한 줄 |
| 테스트 | — | test_claim_graph 2(사라진 id 멈춤·후보 안내·CLI 종료 1·파일 안 씀 · 없는 새 id·철회 [필수] / 옮김·[변경]·새 주장·뺀 주장·발표 주장 기댐·sha·synced·새 판과 맞음 · --drop · 1:N · 같은 판 · 저자 파일 그대로). test_toolkit 1(mapfreeze 가 덧붙임에 · 저자 파일 그대로 · mapstale 조용 · 받침 글 바뀜 → sync → [변경] 받침 + 기대는 화면 · 쓴 주장 글 바뀜 [변경] · sync 없이 새 판 [필수]) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-30: 구연 2판 — 저자 판 따라가기(결정 4: 사라진 id 는 --pairs·--drop 전까지 멈춤)·화면 확인 기록 | 위 claim_graph 16.13 · deck 16.49 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.13 | `59fa4f2978ed` | ○ |
| `test_claim_graph.py` | v16.13 | `4adcf2f536fb` | ○ |
| `CLAIM_GRAPH.md` | v16.13 | `5b710df3eab8` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v91 | `29620e1aaf47` | ○ |
| `RELEASE.md` | v2.71 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.13 | `59fa4f2978ed` | ○ |
| `test_claim_graph.py` | v16.13 | `4adcf2f536fb` | ○ |
| `CLAIM_GRAPH.md` | v16.13 | `5b710df3eab8` | ○ |
| `deck_toolkit.py` | v16.49 | `4c126e7e5b0e` | ○ |
| `test_toolkit.py` | v16.49 | `eab1a891a0b7` | ○ |
| `DECK_SPEC.md` | v16.49 | `94cfde33b6e1` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v91 | `29620e1aaf47` | ○ |
| `RELEASE.md` | v2.71 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.13 | `59fa4f2978ed` | ○ |
| `test_claim_graph.py` | v16.13 | `4adcf2f536fb` | ○ |
| `CLAIM_GRAPH.md` | v16.13 | `5b710df3eab8` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v91 | `29620e1aaf47` | ○ |
| `RELEASE.md` | v2.71 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v91 | `29620e1aaf47` | ○ |
| `RELEASE.md` | v2.71 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `TOOLS_MANIFEST.md` | v91 | `29620e1aaf47` | ○ |
| `RELEASE.md` | v2.71 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.13 | `59fa4f2978ed` | ○ |
| `test_claim_graph.py` | v16.13 | `4adcf2f536fb` | ○ |
| `CLAIM_GRAPH.md` | v16.13 | `5b710df3eab8` | ○ |
| `deck_toolkit.py` | v16.49 | `4c126e7e5b0e` | ○ |
| `test_toolkit.py` | v16.49 | `eab1a891a0b7` | ○ |
| `DECK_SPEC.md` | v16.49 | `94cfde33b6e1` | ○ |
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
| `TOOLS_MANIFEST.md` | v91 | `29620e1aaf47` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `ec1c1847aee0` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.71 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v91 이상.
2. 발표: 구연 덱 확인을 마치면 `deck_toolkit mapfreeze 덱 --oral 덧붙임 --author 저자 -o 덧붙임`(저자 파일은 고치지 않는다). 저자 새 판이 오면 `claim_graph oral sync --author 새판 --oral 덧붙임 -o 새덧붙임` → [필수] 가 있으면 알려 준 `--pairs`·`--drop` 을 정해 다시 → `oral check` → `mapstale`. 덧붙임은 Drive `Claude 작업/발표` 에 둔다.
3. 저자: claims 판을 올릴 때 id 를 바꾸거나 합쳤으면 전달 통보 md 에 "옛 id → 새 id" 를 적는다(발표의 `--pairs` 가 된다).

## 5. 검증하지 않은 것

- 실물 저자 claims(v9·v10)·실제 구연 덱으로는 돌리지 않았다 — 가짜 그래프와 시험 덱으로만. 실물에서 id 가 바뀐 주장의 후보(원고 자리·keys 해시)가 얼마나 잡히는지 모른다(원고 자리까지 함께 바뀌면 후보 없음 — 그때는 --pairs 를 사람이 적는다).
- 덧붙임 파일 크기를 실물로 재지 않았다(추정 50주장 약 8 KB + 확인 기록).
