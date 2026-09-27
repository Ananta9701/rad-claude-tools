# RELEASE v2.29 — manifest v49 — 2026-09-27

> **v2.29** — 발표 K8(가져옴 제목 띠) 원인 확정 뒤 수정: `deck_toolkit.py` 16.28 하나. 다른 도구는 그대로. 이전 판 내용은 `HISTORY.md`.
> 원인(발표 자료 `260927_회신_발표to코드_K8제목띠자료_v1`): 가져온 제목의 안쪽 여백이 위·아래 0.39"씩인데 띠를 0.66" 로 맞췄다 — Google Slides 는 spAutoFit 으로 띠를 키우지 않아 글 아래쪽이 띠 밖. 0.66" 는 결과 덱에서 다시 배운 규격(원본은 1줄 1.22"). 코드 추정("Google 이 2줄로 그린다")은 틀렸다 — 제목은 1줄.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.28 | **요청 1** `conform_title` — 규격 높이가 필요 높이(안쪽 여백 + 줄 높이 × 줄 수)의 90% 도 안 되면 필요 높이로, 규격에 그 줄 수 높이가 없으면(1–2줄) 필요 높이로. **요청 2** `title_profile` — 띠가 필요 높이의 90% 도 안 되는 제목은 높이를 배우지 않는다(`excluded` 수). **요청 3(선택)** CLI `title-bands [--screens] [--dry-run]` — 띠가 위 여백 + 줄 높이보다 낮으면 위쪽 끝 고정으로 필요 높이까지, 아래 내용과 겹치면 바꾸지 않고 알림 |
| `test_toolkit.py` | 16.28 | 173개(+1): 0.66" 띠 셋은 규격에서 빠짐, 오염된 규격으로도 필요 높이로 맞춤, title-bands 가 0.66" 는 키우고 1.22" 는 그대로 |
| `DECK_SPEC.md` | 16.28 | 판 기록 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 발표 `260927_회신_발표to코드_K8제목띠자료_v1` 요청 1(맞춤 높이 하한 = 필요 높이) | deck 16.28 — 규격이 필요의 90% 미만일 때(1.22" 규격은 필요 1.26" 의 97% 라 그대로 — PowerPoint 실측 1.21" 과 맞다) |
| 요청 2(규격 배우기에서 작은 제목 빼기) | deck 16.28 — `excluded` |
| 요청 3(Google 안전 모드, 선택) | deck 16.28 `title-bands` |
| `260927_통보_발표to코드_K7실물확인_v1` — `fit-corner-boxes` 가 Google Slides 에서 고쳐 보임(사용자) | 기록. 구석이 아닌 wrap="none" 상자 요청은 사용자 확인 뒤(발표) |

## 3. 받을 파일

zip 두 개: `v2.29_GitHub.zip`(GitHub 에 전부), `v2.29_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v49 | `c449aaf4f64e` | ○ |
| `RELEASE.md` | v2.29 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.28 | `5c5633c37895` | ○ |
| `test_toolkit.py` | v16.28 | `1280dca7540f` | ○ |
| `DECK_SPEC.md` | v16.28 | `ad214f108f5f` | ○ |
| `handoff.py` | v1.9 | `36df9ec98b79` | — |
| `test_handoff.py` | v1.9 | `bc5c482ccb99` | — |
| `HANDOFF_FORMAT.md` | v1.9 | `a0e89ec847a8` | — |
| `TOOLS_MANIFEST.md` | v49 | `c449aaf4f64e` | ○ |
| `RELEASE.md` | v2.29 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v49 | `c449aaf4f64e` | ○ |
| `RELEASE.md` | v2.29 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v49 | `c449aaf4f64e` | ○ |
| `RELEASE.md` | v2.29 | — | 이 문서 |

### 코드 (22)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.28 | `5c5633c37895` | ○ |
| `test_toolkit.py` | v16.28 | `1280dca7540f` | ○ |
| `DECK_SPEC.md` | v16.28 | `ad214f108f5f` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v1.9 | `36df9ec98b79` | — |
| `test_handoff.py` | v1.9 | `bc5c482ccb99` | — |
| `HANDOFF_FORMAT.md` | v1.9 | `a0e89ec847a8` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v49 | `c449aaf4f64e` | ○ |
| `CODE_PROJECT_README.md` | v5 | `6db694b44ea6` | — |
| `HISTORY.md` | — | `2ed8e54428af` | ○ |
| `release.py` | — | `00abde82a376` | — |
| `GITHUB_README.md` | — | `a338fce401db` | — |
| `PRIVATE_TERMS.txt` | — | `d2562278023a` | — |
| `RELEASE.md` | v2.29 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: 근골격 v3 서식 보정 이어서 — 가져온 제목 4장(121·122 등)에 `title-bands --screens … --dry-run` 으로 먼저 보고 적용(또는 `titles --like 7 --screens … --apply` — 이제 필요 높이로 맞춘다). 전후 diff(글·노트 불변) → 새 sha 를 영상의학에. 사용자가 Google Slides 로 확인.
2. 그 밖의 프로젝트: 도구 변경 없음.

## 5. 검증하지 않은 것

- 필요 높이의 줄 높이(글자 크기 × 1.22)는 PowerPoint 실측(1줄 1.21")보다 조금 크다(계산 1.26"). Google Slides 에서 띠가 딱 맞는지는 사용자 확인.
- 실제 근골격 덱으로는 돌리지 않았다(python-pptx 로 만든 같은 여백·크기의 fixture).
