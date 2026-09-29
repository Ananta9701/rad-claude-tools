# RELEASE v2.64 — manifest v84 — 2026-09-29

> **v2.64** — 작은 판 16(코드 리뷰 ⑯, 겹치는 코드) — **동작은 바뀌지 않는다.** 코드 세션의 릴리스 도구(비공개)가 파일 해시·테스트 실행·코드 전용 목록을 따로 두던 것을 claim_graph 의 것을 가져다 쓰게 했다(방향: 공개 → 비공개). claim_graph 16.8.1. textbook↔literature 겹침은 합치지 않았다(아래 §2). **v2.63 §4 의 "넘김 문서의 뺄 상자(`delete_shape`)에 적는다" 는 틀렸다** — 아래 §4. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.8.1 | `_hash12(path)`(sha256 앞 12자리)·`_run_test(folder, 테스트, python=, env=)` 를 한 곳에 — `selfcheck` 의 해시 3곳·테스트 실행과 `remap-refs` 의 매핑 해시가 이것을 쓴다. 출력·판정·종료 코드는 그대로 |
| `CLAIM_GRAPH.md` | 16.8.1 | 첫 줄 판만 |
| 테스트 | — | 새 시험 없음(동작 그대로) — 대신 같은 입력으로 전·후 출력을 비교했다(§5) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 코드 리뷰 ⑯ claim_graph↔release.py | 위. 비공개 쪽 목록·내용은 공개 파일로 옮기지 않았다(코드 전용 파일 이름 목록 `CODE_ONLY` 는 v15.8.2 부터 claim_graph 에 있던 것 — 비공개가 그것을 쓰게만 함) |
| 코드 리뷰 ⑯ textbook↔literature | **합치지 않음.** 두 파일은 다른 역할 세트(교과서·문헌)에 따로 간다 — 한쪽이 다른 쪽을 import 하면 세트에 파일이 늘고, 공통 파일을 새로 두면 두 세트 모두 바뀐다. 겹치는 것은 pypdf 찾기·NFC·쪽 번호표 읽기 약 30줄이고, **서로 조금 다르다**(pypdf 찾는 자리 `~/pypdf`, 쪽 글자 읽기 실패 표시) — 맞추면 동작이 바뀌므로 사용자 결정 뒤 |
| 사용자 09-29: 14번 변화를 발표·영상의학에 | `to발표`·`to영상의학` 에 통보(`260929_통보_코드to{발표,영상의학}_stripcolor빨간도형남음_v1`) |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8.1 | `ec38bbbcf67f` | ○ |
| `test_claim_graph.py` | v16.8.1 | `381a057eb97b` | ○ |
| `CLAIM_GRAPH.md` | v16.8.1 | `8765704a5830` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v84 | `92ba21d38b06` | ○ |
| `RELEASE.md` | v2.64 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8.1 | `ec38bbbcf67f` | ○ |
| `test_claim_graph.py` | v16.8.1 | `381a057eb97b` | ○ |
| `CLAIM_GRAPH.md` | v16.8.1 | `8765704a5830` | ○ |
| `deck_toolkit.py` | v16.45 | `eeb2305adca7` | — |
| `test_toolkit.py` | v16.45 | `d0123d0f9c21` | — |
| `DECK_SPEC.md` | v16.45 | `1c2910d1d90a` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v84 | `92ba21d38b06` | ○ |
| `RELEASE.md` | v2.64 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8.1 | `ec38bbbcf67f` | ○ |
| `test_claim_graph.py` | v16.8.1 | `381a057eb97b` | ○ |
| `CLAIM_GRAPH.md` | v16.8.1 | `8765704a5830` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v84 | `92ba21d38b06` | ○ |
| `RELEASE.md` | v2.64 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v84 | `92ba21d38b06` | ○ |
| `RELEASE.md` | v2.64 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.4 | `0585dbb787b0` | — |
| `test_literature.py` | v0.8.4 | `940eca6399e2` | — |
| `LITERATURE.md` | v0.8.4 | `e35c0d149938` | — |
| `TOOLS_MANIFEST.md` | v84 | `92ba21d38b06` | ○ |
| `RELEASE.md` | v2.64 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8.1 | `ec38bbbcf67f` | ○ |
| `test_claim_graph.py` | v16.8.1 | `381a057eb97b` | ○ |
| `CLAIM_GRAPH.md` | v16.8.1 | `8765704a5830` | ○ |
| `deck_toolkit.py` | v16.45 | `eeb2305adca7` | — |
| `test_toolkit.py` | v16.45 | `d0123d0f9c21` | — |
| `DECK_SPEC.md` | v16.45 | `1c2910d1d90a` | — |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.4 | `0585dbb787b0` | — |
| `test_literature.py` | v0.8.4 | `940eca6399e2` | — |
| `LITERATURE.md` | v0.8.4 | `e35c0d149938` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v84 | `92ba21d38b06` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `a9585b3f6476` | ○ |
| `release.py` | — | `0a430411a738` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.64 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v84 이상. 이 판에서 할 일은 없다(동작 그대로).
2. **정정(v2.63 §4-2)**: 넘김의 `해설 상자 "…"` 는 **도형 안의 글**로 찾는다 — 글 없는 빨간 화살표·동그라미는 적어도 지울 수 없다(코드가 시험함: 후보 0개). 다음 판까지는 발표가 복제 화면을 눈으로 보고, 정답을 가리키는 도형은 손으로 또는 `Deck.delete_shape(n, "도형 이름")` 으로 지운다. 자세한 것은 `to발표`·`to영상의학` 통보.

## 5. 검증한 것 · 하지 않은 것

- 같은 입력으로 정리 **전(v2.63)·후** 를 돌려 출력을 비교했다:
  - `claim_graph selfcheck --tests` — 역할 6개 지정·역할 추정·일부러 깨뜨린 세트(해시 불일치, 종료 코드 1)·예비 폴더 대조(`--compare`): **머리 줄의 판 번호(v16.8 → v16.8.1) 말고 한 글자도 같다.**
  - `remap-refs` — 첫 적용(저장 파일까지)·같은 매핑 두 번(거부, 종료 코드 2, 매핑 해시): 같다.
  - `release.py` — `test_release.py` 8/8 전·후 같음. `build` 전·후 산출물 비교와 `check` 통과·실패 두 쪽 비교는 HISTORY §3 에 적었다.
- textbook·literature 는 이 판에서 바뀌지 않았다.
