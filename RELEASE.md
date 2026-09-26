# RELEASE v2.21 — manifest v41 — 2026-09-27

> **v2.21** — 발표 `260927_도구회신_v2.20_재시험_v1` 처리. handoff 1.4 만 바뀐다. 이전 판 내용은 `HISTORY.md`.
> v2.20 재시험: 흉부1 v1 다른 화면 98 → 3(셋 다 넘김에 지시 없는 해설 상자 — 경고대로), LGI v2 11 → 0, 물리 v1 Traceback → 적용, H&N v9 조용한 누락 → 문법 오류로 멈춤. 3-1–3-7·결정 1·2 모두 확인. 새 결함 3.

## 1. 바뀐 것 — handoff 1.4

| # | 결함 | 고친 것 |
|---|---|---|
| N1 | 새 슬라이드의 L2 문단이 L1 서식(marL·글자 크기)으로 — 틀 화면(H&N v8 화면 61)에 L2 가 없었다, 경고 없음 | 틀 화면에 없는 수준이 있으면 **같은 레이아웃·같은 배경의 다른 화면** 중 모든 수준을 가진 화면을 본문 틀로. 그런 화면도 없으면 경고 |
| N2 | 같은 자리 뒤로 여러 화면을 이동하면 순서가 거꾸로(물리 v1: 2·3·4 → 4·3·2) | 같은 자리로 가는 화면들을 원래 순서대로 이어 붙인다 |
| N3 | 다른 덱에서 **처음** 가져오는 슬라이드의 마스터를 근거 없이 고름(H&N v6: 레이아웃 8) | 작업어 **`레이아웃 = 화면 N 과 같게`** 추가(새 슬라이드·가져옴). 없으면 도구가 고르되 **경고**. 같은 배경 슬라이드가 있으면 그 레이아웃(v2.20)은 그대로 |

HANDOFF_FORMAT 1.4 — 작업어 한 줄, 적용 규칙 문단(문단 추가·새 슬라이드는 표기대로 — 굵게는 `**…**`, 틀에 없는 수준, 이동 순서).

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| N1 L2 서식 | 반영 |
| N2 이동 순서 | 반영 |
| N3 첫 가져옴 레이아웃 | 작업어 + 경고(발표 제안) |
| 물리 `Nipple marking` 굵게 | 설계대로(문단 추가는 표기대로) — 영상의학이 `**…**` 로 적게 HANDOFF_FORMAT 에 명시 |

## 3. 받을 파일

zip 두 개: `v2.21_GitHub.zip`(GitHub 에 전부), `v2.21_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v41 | `c26cf6f4d0a3` | ○ |
| `RELEASE.md` | v2.21 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.25 | `85cbd8af803d` | — |
| `test_toolkit.py` | v16.25 | `51cdbea4be1e` | — |
| `DECK_SPEC.md` | v16.25 | `f8f57f8d85df` | — |
| `handoff.py` | v1.4 | `b894bab94cee` | ○ |
| `test_handoff.py` | v1.4 | `baed9ca329db` | ○ |
| `HANDOFF_FORMAT.md` | v1.4 | `24e39acfa50d` | ○ |
| `TOOLS_MANIFEST.md` | v41 | `c26cf6f4d0a3` | ○ |
| `RELEASE.md` | v2.21 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v41 | `c26cf6f4d0a3` | ○ |
| `RELEASE.md` | v2.21 | — | 이 문서 |

### 코드 (19)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.25 | `85cbd8af803d` | — |
| `test_toolkit.py` | v16.25 | `51cdbea4be1e` | — |
| `DECK_SPEC.md` | v16.25 | `f8f57f8d85df` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v1.4 | `b894bab94cee` | ○ |
| `test_handoff.py` | v1.4 | `baed9ca329db` | ○ |
| `HANDOFF_FORMAT.md` | v1.4 | `24e39acfa50d` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v41 | `c26cf6f4d0a3` | ○ |
| `CODE_PROJECT_README.md` | v5 | `369b99ea8f0f` | — |
| `HISTORY.md` | — | `a8bcb4f2902e` | ○ |
| `release.py` | — | `8ce7a3ea9b82` | — |
| `GITHUB_README.md` | — | `60aa56dc93ea` | — |
| `PRIVATE_TERMS.txt` | — | `4285e1f439fb` | — |
| `RELEASE.md` | v2.21 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: H&N v9(고친 사본)·물리 v1·H&N v6 만 다시 — H&N v6 은 넘김 사본에 `· 레이아웃 = 화면 61 과 같게` 를 넣은 것과 안 넣은 것(경고) 둘 다. 그 뒤로는 새 넘김을 도구로 적용하고 보고서만 확인하는 방식으로(발표 제안).
2. 영상의학: 다른 덱에서 처음 가져오는 새 슬라이드에는 `레이아웃 = 화면 N 과 같게`, 이웃 줄처럼 굵게 할 이름은 `**…**` (코드가 알림).

## 5. 검증하지 않은 것

N3 는 fixture 에 마스터가 하나라 작업어 해석만 시험했다 — 실제 레이아웃 선택은 발표의 H&N v6 재시험으로.
