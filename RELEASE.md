# RELEASE v2.30 — manifest v50 — 2026-09-27

> **v2.30** — 발표 `260927_도구회신_K9제목띠아래여백_v1` 처리. `deck_toolkit.py` 16.29 하나. 이전 판 내용은 `HISTORY.md`.
> v2.29 `title-bands` 실물 결과: 근골격 v3 에서 키움 0 · 바꾸지 않음 4(모두 본문 자리 표시자 1.08" 와 겹침). 사용자 결정: 아래 여백을 줄여 본문 위까지 키운다. 발표 정정: PowerPoint 에서도 띠는 0.66" 그대로(spAutoFit 은 열 때 다시 계산하지 않는 것으로 보임) — Google 만의 문제가 아니다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.29 | **K9** `title-bands --shrink-bottom-inset [인치, 기본 0.1]` — 겹쳐서 못 키울 때 위 여백은 그대로, 아래 여백만 줄여 `위 여백 + 줄 높이 × 줄 수 + 새 아래 여백` 이 아래 내용 윗끝을 넘지 않게. 그래도 겹치면 바꾸지 않고 알림. 보고: 띠 전후 높이·아래 여백 전후. **K8-b** `title_profile` — 높이와 안쪽 여백을 따로 최빈값으로 고르면 서로 다른 제목의 값이 섞인다: 높이는 규격 여백과 같은 여백을 가진 제목에서만 배운다. `titles --like` 출력에 규격의 출처(여백 규격, 뺀 제목, 줄 수별 (높이, 위, 아래 여백) 분포와 화면) |
| `test_toolkit.py` | 16.29 | 174개(+1): 0.66" 띠·여백 0.39"·본문 1.08" → 그냥은 [!], 아래 여백 0.1" 로 키움(위 여백 그대로, 본문 위), 본문 0.8" 면 [!], 여백·높이를 같은 제목에서, titles 출처 출력 |
| `DECK_SPEC.md` | 16.29 | 판 기록(발표 정정 포함) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| K9 아래 여백을 줄여 키우기(사용자 결정) | deck 16.29 `--shrink-bottom-inset` |
| K8-b v3 규격이 여전히 1줄 0.66" | **원인 추정(확인 안 됨)**: v2.29 의 "뺀 제목" 은 각 제목 **자기 여백**으로 필요 높이를 잰다 — 0.66" 제목들의 여백이 작으면 빠지지 않는다. 그런데 규격의 여백(bodyPr)은 다른 제목들의 0.39"×2 가 최빈이면, 둘이 섞여 0.66" + 0.39"×2 라는 담지 못하는 띠가 된다. 16.29 는 높이를 규격 여백과 같은 제목에서만 배우고, `titles --like 7` 이 출처를 찍는다 — **발표가 v3 에 다시 돌려 출력(1줄 분포·화면)을 보내 주면 확인한다** |
| 정정(PowerPoint 도 띠를 키우지 않음) | DECK_SPEC 판 기록에 반영 |

## 3. 받을 파일

zip 두 개: `v2.30_GitHub.zip`(GitHub 에 전부), `v2.30_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v50 | `60722e174072` | ○ |
| `RELEASE.md` | v2.30 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.29 | `0dd4fdac532f` | ○ |
| `test_toolkit.py` | v16.29 | `9159ae2edf2a` | ○ |
| `DECK_SPEC.md` | v16.29 | `8153a2ff19a2` | ○ |
| `handoff.py` | v1.9 | `36df9ec98b79` | — |
| `test_handoff.py` | v1.9 | `bc5c482ccb99` | — |
| `HANDOFF_FORMAT.md` | v1.9 | `a0e89ec847a8` | — |
| `TOOLS_MANIFEST.md` | v50 | `60722e174072` | ○ |
| `RELEASE.md` | v2.30 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v50 | `60722e174072` | ○ |
| `RELEASE.md` | v2.30 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v50 | `60722e174072` | ○ |
| `RELEASE.md` | v2.30 | — | 이 문서 |

### 코드 (22)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.29 | `0dd4fdac532f` | ○ |
| `test_toolkit.py` | v16.29 | `9159ae2edf2a` | ○ |
| `DECK_SPEC.md` | v16.29 | `8153a2ff19a2` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v1.9 | `36df9ec98b79` | — |
| `test_handoff.py` | v1.9 | `bc5c482ccb99` | — |
| `HANDOFF_FORMAT.md` | v1.9 | `a0e89ec847a8` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v50 | `60722e174072` | ○ |
| `CODE_PROJECT_README.md` | v5 | `6db694b44ea6` | — |
| `HISTORY.md` | — | `6a87fb1af88a` | ○ |
| `release.py` | — | `00abde82a376` | — |
| `GITHUB_README.md` | — | `a338fce401db` | — |
| `PRIVATE_TERMS.txt` | — | `d2562278023a` | — |
| `RELEASE.md` | v2.30 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: 근골격 v3 에 `title-bands --screens 61,62,121,122 --shrink-bottom-inset --dry-run` → 적용(대본 v4) → 전후 diff(글·노트 불변, 띠 4장만) → 사용자가 PowerPoint·Google Slides 에서 화면 61 확인. 그리고 `titles v3 --like 7` 출력(새 출처 줄)을 K8-b 회신으로.
2. 그 밖의 프로젝트: 도구 변경 없음.

## 5. 검증하지 않은 것

- K8-b 의 원인은 추정이다 — 근골격 v3 의 0.66" 제목들의 여백을 보지 못했다. 16.29 의 출처 출력으로 확인한다.
- 줄 높이(글자 크기 × 1.22)가 실측보다 조금 크다 — 새 띠가 본문과 딱 붙을 수 있다(발표 계산 0.92", 도구 계산 약 0.97" < 본문 1.08").
