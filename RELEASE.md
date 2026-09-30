# RELEASE v2.75 — manifest v95 — 2026-09-30

> **v2.75** — 큰 방향 ③(사용자 09-30 설계 결정): 탐색적 표지 `exploratory` — main 의 전제(premise) 사슬에 있으면 사유 없이는 [필수], 표지를 지우면 mapstale [변경]. 새 주장 후보 `suggest`([참고]만 — 안 이어진 이웃 · 안 쓰인 근거 · 공통 한계). 발표 회신: `— note:` 앞 빈칸 한 칸.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.17 | 주장 칸 `exploratory`(true/false)·`exploratory_reason` · `mapgraph`: 탐색적 주장이 main 의 premise 사슬(main 자신 포함, main 마다)에 있으면 [필수], 사유가 있으면 [참고]+사유, support 섞인 경로 [참고], true/false 아닌 값 [필수], 사유만 있고 표지 없음 [참고] · `mapreport` 끝에 "탐색적 주장" 절(사슬 안·밖·사유) · `mapfreeze` 가 표지를 적고 `mapstale` 은 true→false·칸 삭제를 [변경](하류까지), false→true 를 [참고] · `mapdraw`·`focus` 상자에 "탐색"(색 없음, 범례·설명은 있을 때만) · 새 명령 `suggest --claims [-o] [--min-shared 2] [--min-caveat 3]`(claims 는 바꾸지 않음, 종료 0, 증례 그래프는 규칙 1 끔, main 에 직접 걸린 한계 0 이면 규칙 3 머리 한 줄) · `add --exploratory` · `mapcheck` 의 `— note:` 앞 빈칸 한 칸 |
| `CLAIM_GRAPH.md` | 16.17 | §3-7 새 절 · §3 칸 표 · §3-1 판정 표 · §4 명령 표(suggest·add) |
| `deck_toolkit.py` | 16.51 | `mapfreeze --oral`·`mapstale --oral` 의 [!] 줄 `— note:` 앞 빈칸 한 칸(모양만) |
| `DECK_SPEC.md` | 16.51 | 머리 주 한 줄 |
| 테스트 | — | test_claim_graph 10(premise 사슬 [필수]/사유 [참고]/main 자신 · support [참고]/이어지지 않음 조용 · 값 검사·빈 사유·증례 main 마다·철회 · mapreport 절 있음/없음 · mapstale 지움·삭제 [변경]+하류 / 그대로 조용 / 새로 붙음 [참고] / 옛 기록 · suggest 규칙 1 묶음·이어짐·공유 1·철회·DOI 2/1 · 규칙 2 rebuttal 쓰임 · 규칙 3 기준·머리 줄 있음/없음·기준 옵션 · 사슬 절반 덧줄 있음/없음 · 증례 끔 · CLI -o·종료 0·파일 그대로·파일 이름만 → 2 · add --exploratory 있음/없음 · mapdraw 두 모양·focus 표시와 범례 있음/없음 · 구연 합친 그래프 표지·oral check 1) · test_toolkit: 기존 O1·O2 시험에 빈칸 한 칸 확인 세 곳 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-30: ③ 설계 1~8 추천대로 · 기준 공유 2·공통 한계 3(저자 실물로 잼 — 규칙 1 0 · 규칙 2 0 · 규칙 3 8) | 위 `claim_graph` 16.17 |
| 사용자 09-30: 표지 지우기는 [변경](지문에 포함), false→true 는 [참고] | 위 — `verified.exploratory` |
| 사용자 09-30: main 에 직접 걸린 한계 0 이면 규칙 3 머리 한 줄(줄은 그대로) | 위 |
| 발표 09-30 keys_missing 확인: O1·O2 실물 확인됨 · `keys_missing 표시  — note` 빈칸 두 칸 | 빈칸 한 칸(claim_graph mapcheck · deck_toolkit 두 곳) |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.17 | `14c55d4aa06b` | ○ |
| `test_claim_graph.py` | v16.17 | `ea2b9510bd13` | ○ |
| `CLAIM_GRAPH.md` | v16.17 | `fac770aed6a6` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v95 | `21fc2aefe842` | ○ |
| `RELEASE.md` | v2.75 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.17 | `14c55d4aa06b` | ○ |
| `test_claim_graph.py` | v16.17 | `ea2b9510bd13` | ○ |
| `CLAIM_GRAPH.md` | v16.17 | `fac770aed6a6` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | ○ |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | ○ |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v95 | `21fc2aefe842` | ○ |
| `RELEASE.md` | v2.75 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.17 | `14c55d4aa06b` | ○ |
| `test_claim_graph.py` | v16.17 | `ea2b9510bd13` | ○ |
| `CLAIM_GRAPH.md` | v16.17 | `fac770aed6a6` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v95 | `21fc2aefe842` | ○ |
| `RELEASE.md` | v2.75 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v95 | `21fc2aefe842` | ○ |
| `RELEASE.md` | v2.75 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `TOOLS_MANIFEST.md` | v95 | `21fc2aefe842` | ○ |
| `RELEASE.md` | v2.75 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.17 | `14c55d4aa06b` | ○ |
| `test_claim_graph.py` | v16.17 | `ea2b9510bd13` | ○ |
| `CLAIM_GRAPH.md` | v16.17 | `fac770aed6a6` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | ○ |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | ○ |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | ○ |
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
| `TOOLS_MANIFEST.md` | v95 | `21fc2aefe842` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `6c8e872e7b63` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.75 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v95 이상.
2. 저자: `suggest --claims <claims v10>` 을 돌려 규칙 3 머리 줄과 공통 한계 목록을 사용자에게 보인다 — main 에 걸 한계를 사용자가 고른다(to저자 통보). 새 주장을 적으면 `add --exploratory` 뒤 `mapgraph`.
3. 저자·리뷰어·발표: 이미 `exploratory` 칸을 쓴 그래프는 없다(저자 v10 실측 0) — 새로 쓸 때부터 적용된다. 표지를 단 뒤에는 `mapfreeze` 를 다시(옛 freeze 에는 표지 기록이 없어 지워도 [변경] 이 안 뜬다).

## 5. 검증하지 않은 것

- `suggest` 규칙 1 의 **문헌 DOI 공유**는 가짜 그래프로만 시험 — 저자 실물에는 아직 문헌 sources 가 없다. 저자가 근거를 채운 뒤 후보 수를 다시 볼 것.
- `focus --png` 에서 "(탐색)" 줄이 붙은 상자의 실제 PNG 모양은 보지 않았다(mermaid 글·범례만 시험).
