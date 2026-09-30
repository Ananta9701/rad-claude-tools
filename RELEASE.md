# RELEASE v2.72 — manifest v92 — 2026-09-30

> **v2.72** — 구연 덧붙임 첫 실물 회신(발표 09-30) O1·O2: 화면 keys 가 없는 자리를 말없이 확인 기록으로 찍던 것 → 표시(`keys_missing`)와 [!] 한 줄, mapstale 도 다시 알림. `use[id].note` 를 공식 칸으로 — [!] 줄 옆에 붙인다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.14 | 합칠 때 덧붙임 `use[id].note`(발표 주장은 자기 `note`)·`keys_missing` 을 넘긴다 · `mapcheck` 의 [!] 줄에 `— note: …` · `oral_keys_missing`(화면 keys 가 없는 자리 — mapcheck "반영되지 않음" 과 같은 판정) · `oral_store_verified` 가 `keys_missing` 을 붙이고(다시 확인해 keys 가 있으면 뺀다) |
| `deck_toolkit.py` | 16.50 | `mapfreeze --oral`: keys 가 없는 자리도 기록하되 `keys_missing: true` + [!] 한 줄(화면 번호·note) · `mapstale --oral`: 표시가 있으면 "바뀐 것 없음" 이어도 [!] 한 줄 |
| `CLAIM_GRAPH.md` · `DECK_SPEC.md` | 16.14 · 16.50 | §3-5 `note`(공식 칸)·`keys_missing`(도구가 씀) · 머리 한 줄 |
| 테스트 | — | test_toolkit 1(가짜 덱·가짜 저자 claims: mapcheck [!] 줄에 note · mapfreeze 가 표시와 [!] · note 보존 · mapstale 이 다시 알림 · keys 를 고치면 표시와 [!] 가 빠지고 mapstale 조용) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 발표 도구회신 09-30 O1: mapfreeze --oral 이 [!] 자리도 말없이 verified | 위 — 기록하되 `keys_missing` 표시·[!], mapstale 도 알림(`--allow-missing` 으로 건너뛰는 안은 쓰지 않음: 의도한 낡은 화면도 기록은 남기는 것이 발표 흐름에 맞다) |
| O2: `use[id].note` 공식 칸, [!] 줄 옆에 | 위 |
| O3: 저자 v11 에서 evidence 추가 예정 | 할 일 없음 — v11 이 오면 `oral sync` |
| 저자 회신 09-30: gaps 두 부류 분리(v10) "14개 중 6개" 정확히 맞음 | 확인 — 대기 회신 닫음 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.14 | `55d583bb1abe` | ○ |
| `test_claim_graph.py` | v16.14 | `cd9dd1102b44` | ○ |
| `CLAIM_GRAPH.md` | v16.14 | `387366a927ad` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v92 | `cdfcf29d51ff` | ○ |
| `RELEASE.md` | v2.72 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.14 | `55d583bb1abe` | ○ |
| `test_claim_graph.py` | v16.14 | `cd9dd1102b44` | ○ |
| `CLAIM_GRAPH.md` | v16.14 | `387366a927ad` | ○ |
| `deck_toolkit.py` | v16.50 | `66c593d157b7` | ○ |
| `test_toolkit.py` | v16.50 | `fd00196d9736` | ○ |
| `DECK_SPEC.md` | v16.50 | `bbe61c4aebd5` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v92 | `cdfcf29d51ff` | ○ |
| `RELEASE.md` | v2.72 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.14 | `55d583bb1abe` | ○ |
| `test_claim_graph.py` | v16.14 | `cd9dd1102b44` | ○ |
| `CLAIM_GRAPH.md` | v16.14 | `387366a927ad` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v92 | `cdfcf29d51ff` | ○ |
| `RELEASE.md` | v2.72 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v92 | `cdfcf29d51ff` | ○ |
| `RELEASE.md` | v2.72 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `TOOLS_MANIFEST.md` | v92 | `cdfcf29d51ff` | ○ |
| `RELEASE.md` | v2.72 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.14 | `55d583bb1abe` | ○ |
| `test_claim_graph.py` | v16.14 | `cd9dd1102b44` | ○ |
| `CLAIM_GRAPH.md` | v16.14 | `387366a927ad` | ○ |
| `deck_toolkit.py` | v16.50 | `66c593d157b7` | ○ |
| `test_toolkit.py` | v16.50 | `fd00196d9736` | ○ |
| `DECK_SPEC.md` | v16.50 | `bbe61c4aebd5` | ○ |
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
| `TOOLS_MANIFEST.md` | v92 | `cdfcf29d51ff` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `907ac01fe738` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.72 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v92 이상.
2. 발표: 덧붙임을 다시 `mapfreeze --oral … -o …` 하면 화면 10·12 처럼 keys 가 화면에 없는 주장에 `keys_missing: true` 가 붙고 [!] 로 나온다(의도한 낡은 화면이면 `use[id].note` 에 까닭을 적어 두면 [!] 줄 옆에 보인다).

## 5. 검증하지 않은 것

- 발표의 실제 덧붙임(31주장)으로는 돌리지 않았다 — 가짜 덱·가짜 저자 claims 로만. 실물 파일은 공개 저장소에 넣지 않는다.
