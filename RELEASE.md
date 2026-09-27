# RELEASE v2.32 — manifest v52 — 2026-09-27

> **v2.32** — 발표 `260927_도구회신_K11나누기_K12흰글자제목_v1`(인터벤션 첫 병합 뒤 사용자 관찰) 처리. `handoff.py` 2.0(나누기 — 넘김 문법이 늘어 +1), `deck_toolkit.py` 16.31. 이전 판 내용은 `HISTORY.md`.
> 사용자 결정(09-27): 나눈 두 장 모두 원작자 메모를 둔다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `handoff.py` | 2.0 | **K11 `나누기`** — `작업: 나누기 — 본문 k 문단 뒤에서`(선택 `· 제목에 번호`), `나눈 뒤(2/2) 대본:`(필수)·`나눈 뒤(2/2) 참고:`·`나눈 뒤(2/2) 상자 지우기: "…"`. 화면을 바로 뒤에 복제(그림·글상자·원작자 메모 두 장 모두), 1/2 는 앞 k 문단·2/2 는 나머지, 2/2 노트는 나눈 뒤 대본·참고 + 같은 메모. check 가 비어 있지 않은 문단 수로 k 를 대조(문단 작업이 같이 있으면 경고). 보고서 "나누기" 줄(두 slide, 넘침 [심각] 전 → 1/2 + 2/2, 메모 같음). 앞에 복제·삭제와 같이 쓰면 오류 |
| `test_handoff.py` | 2.0 | 26개(+1): 문법 오류 3가지, check 의 문단 수, 적용(순서·본문 나눔·제목 번호·두 노트·메모 두 장 같음·보고) |
| `HANDOFF_FORMAT.md` | 2.0 | 나누기 한 문단 |
| `deck_toolkit.py` | 16.31 | **K12 `adopt-house-look --screens … [--dry-run]`** — ① 밝은 배경 위 아주 밝은 글자색(흰색 등)을 지워 테마 글자색으로(강조색·어두운 채움 상자·그림·도형은 그대로, 배경이 그림·그라데이션·어두우면 그대로). ② 제목 자리 표시자가 비었으면 위쪽 가장 큰 글자 글상자를 제목 자리 표시자로 옮김(애매하면 [참고]) — 그 뒤 `titles`/`title-bands` 로 규격을 받는다 |
| `test_toolkit.py` | 16.31 | 176개(+1): 흰 글자 → 테마색, 빨강 그대로, 어두운 상자 그대로, 글상자 제목 → 제목 자리 표시자 |
| `DECK_SPEC.md` | 16.31 | 판 기록 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| K11 나누기 — 메모 규칙 | 두 장 모두(사용자 결정). 넘김 문법은 발표 제안대로(`나눈 뒤(2/2) 대본:`), 2/2 글상자 지우기는 `나눈 뒤(2/2) 상자 지우기:` 로(지금 문법의 해설 상자는 앞에 복제에만) |
| K11 제목 번호 | 선택 작업어 `제목에 번호` |
| K12 흰 글자·글상자 제목 | deck 16.31 `adopt-house-look` — 대안(`배경 원천대로`)은 만들지 않음(사용자는 통일을 원함) |
| 참고: 기준 덱 화면 80–88 제목 넘침 | 도구 변경 없음 — `title-bands`(발표 미리보기 중) |

## 3. 받을 파일

zip 두 개: `v2.32_GitHub.zip`(GitHub 에 전부), `v2.32_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v52 | `3159d8b88421` | ○ |
| `RELEASE.md` | v2.32 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.31 | `6a87e0849537` | ○ |
| `test_toolkit.py` | v16.31 | `cb14d97150dc` | ○ |
| `DECK_SPEC.md` | v16.31 | `297ef9629d53` | ○ |
| `handoff.py` | v2.0 | `642269d51cc5` | ○ |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | ○ |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | ○ |
| `TOOLS_MANIFEST.md` | v52 | `3159d8b88421` | ○ |
| `RELEASE.md` | v2.32 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v52 | `3159d8b88421` | ○ |
| `RELEASE.md` | v2.32 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v52 | `3159d8b88421` | ○ |
| `RELEASE.md` | v2.32 | — | 이 문서 |

### 코드 (22)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.31 | `6a87e0849537` | ○ |
| `test_toolkit.py` | v16.31 | `cb14d97150dc` | ○ |
| `DECK_SPEC.md` | v16.31 | `297ef9629d53` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | ○ |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | ○ |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | ○ |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v52 | `3159d8b88421` | ○ |
| `CODE_PROJECT_README.md` | v5 | `6db694b44ea6` | — |
| `HISTORY.md` | — | `ec37b3e2c993` | ○ |
| `release.py` | — | `00abde82a376` | — |
| `GITHUB_README.md` | — | `a338fce401db` | — |
| `PRIVATE_TERMS.txt` | — | `d2562278023a` | — |
| `RELEASE.md` | v2.32 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: 인터벤션 v1 화면 25–33 에 `adopt-house-look --screens 25-33 --dry-run` → 사용자와 목록 → 적용 → `title-bands --balance --like {원래 제목 화면}` 으로 새 제목 띠 → 전후 diff(글·노트 불변, 색·제목만). 화면 10 은 영상의학에 나누기 넘김을 요청(나눌 문단 k·두 장 대본 — HANDOFF_FORMAT v2.0).
2. 영상의학: 넘김 문법에 `나누기` 가 생겼다(HANDOFF_FORMAT v2.0 — GitHub).
3. 저자·리뷰어·교과서: 도구 변경 없음.

## 5. 검증하지 않은 것

- `adopt-house-look` 은 fixture 한 장으로만. 실제 인터벤션 slide338–346 의 흰 글자가 run 에 직접 지정된 색인지(그러면 지운다), 도형·표·레이아웃에서 오는 색인지(그러면 못 바꾼다)는 dry-run 에서 드러난다. 제목 글상자 고르기(가장 위·가장 큰 글자)는 글상자가 여럿인 슬라이드에서 틀릴 수 있어 애매하면 옮기지 않는다.
- 나누기 뒤 넘침이 실제로 줄었는지는 보고서 줄로 본다 — 1/2 에 남은 문단이 여전히 길면 줄지 않는다.
