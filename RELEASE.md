# RELEASE v2.31 — manifest v51 — 2026-09-27

> **v2.31** — 발표 `260927_도구회신_K9적용결과_K8b자료_v1`·`260927_도구회신_K10제목띠위아래균형_v1` 처리. `deck_toolkit.py` 16.30 하나. 이전 판 내용은 `HISTORY.md`.
> K9 는 실물 성공(근골격 대본 v4, 화면 61 을 사용자가 PowerPoint·Google Slides 로 확인). 사용자 결정(09-27): K10 은 1–3번(규격 높이·아래 내용까지·위아래 같게)만, 본문 내리기(`--move-content`)는 결과를 보고 정한다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.30 | **K10** `title-bands --balance --like N [--gap 0.1] [--screens] [--dry-run]` — 채운 제목 띠마다 목표 = 기준 화면 무리의 줄 수별 규격 높이, 띠 아래 첫 내용 윗끝 − gap 을 넘지 않게, 위·아래 여백 = (띠 − 글 높이)/2(최소 0.05"). 글이 안 들어가면 바꾸지 않고 [!]. 내용은 옮기지 않는다. **K8-b** `title_profile` 이 위 여백 무리로 나눠 배운다(like = 기준 제목의 무리, 없으면 가장 큰 무리) — 무리 수가 바뀌어도 규격이 뒤집히지 않는다. `titles --like` 출력에 무리. **화면 6·7** 규격에서 뺄 제목을 그 제목 자기 글자 크기로 판정 |
| `test_toolkit.py` | 16.30 | 175개(+1): balance(아래 본문까지·규격 높이·너무 가까우면 [!]·이미 균형이면 그대로·위아래 같음), 23pt 제목을 빼지 않음, 기준 무리에서 배움(수가 적어도). 16.29 시험의 무리 기대값을 새 규칙으로 |
| `DECK_SPEC.md` | 16.30 | 판 기록 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| K9 적용 결과(성공) | 기록 |
| K8-b 규격이 무리 수에 따라 뒤집힘 — 무리별로 배우고 같은 위 여백 무리 규격으로 | deck 16.30 — 위 여백으로 무리를 나누고 기준 제목의 무리에서 배운다(K9 로 아래 여백만 바꾼 제목은 같은 무리에 남는다) |
| 화면 6·7 — `titles` 와 `title-bands` 판정이 다름 | **결함(titles 쪽)**: 규격에서 뺄 제목을 규격 글자 크기(28pt)로 세어 23pt 제목을 2줄로 봤다. `title-bands` 는 제 크기로 봐서 1줄 — 사용자 캡처와 맞다. 16.30 에서 자기 크기로 |
| K10 1–3번 | deck 16.30 `--balance` |
| K10 4번 `--move-content` | 이번 판에 넣지 않음 — 사용자 결정(결과를 보고). DECK_SPEC §0-C "도구는 본문을 옮기지 않는다" 와 부딪친다 |

## 3. 받을 파일

zip 두 개: `v2.31_GitHub.zip`(GitHub 에 전부), `v2.31_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v51 | `c7b30299519b` | ○ |
| `RELEASE.md` | v2.31 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.30 | `fb4b821707f2` | ○ |
| `test_toolkit.py` | v16.30 | `f124636a8e0f` | ○ |
| `DECK_SPEC.md` | v16.30 | `e28187299c67` | ○ |
| `handoff.py` | v1.9 | `36df9ec98b79` | — |
| `test_handoff.py` | v1.9 | `bc5c482ccb99` | — |
| `HANDOFF_FORMAT.md` | v1.9 | `a0e89ec847a8` | — |
| `TOOLS_MANIFEST.md` | v51 | `c7b30299519b` | ○ |
| `RELEASE.md` | v2.31 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v51 | `c7b30299519b` | ○ |
| `RELEASE.md` | v2.31 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v51 | `c7b30299519b` | ○ |
| `RELEASE.md` | v2.31 | — | 이 문서 |

### 코드 (22)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.30 | `fb4b821707f2` | ○ |
| `test_toolkit.py` | v16.30 | `f124636a8e0f` | ○ |
| `DECK_SPEC.md` | v16.30 | `e28187299c67` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v1.9 | `36df9ec98b79` | — |
| `test_handoff.py` | v1.9 | `bc5c482ccb99` | — |
| `HANDOFF_FORMAT.md` | v1.9 | `a0e89ec847a8` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v51 | `c7b30299519b` | ○ |
| `CODE_PROJECT_README.md` | v5 | `6db694b44ea6` | — |
| `HISTORY.md` | — | `5447c089b76d` | ○ |
| `release.py` | — | `00abde82a376` | — |
| `GITHUB_README.md` | — | `a338fce401db` | — |
| `PRIVATE_TERMS.txt` | — | `d2562278023a` | — |
| `RELEASE.md` | v2.31 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: 근골격 v4 에 `title-bands --balance --like 7 --dry-run`(원래 하지 덱 제목 모양 — 화면 7 이 여백 0.39" 무리인지 `titles --like 7` 의 무리 줄로 먼저 확인) → 목록을 사용자와 → 적용(대본 v5) → 전후 diff(글·노트 불변) → 사용자가 화면 6·7·25·85·61 을 PowerPoint·Google Slides 로. 여유가 여전히 모자란 화면이 있으면 그 목록으로 `--move-content` 를 요청.
2. 그 밖의 프로젝트: 도구 변경 없음.

## 5. 검증하지 않은 것

- 글 높이(글자 크기 × 1.22 × 줄간격)는 실측보다 조금 클 수 있다 — 크면 계산한 여백이 작아져 글이 가운데보다 아주 조금 위에 놓인다. 사용자 눈으로 확인.
- 실제 근골격 덱으로는 돌리지 않았다(같은 여백·크기를 흉내 낸 fixture).
