# RELEASE v2.19 — manifest v39 — 2026-09-26

> **v2.19 — apply-handoff 2단계: 적용.** `handoff.py` 1.2 에 `apply`·`compare`. 이전 판 내용은 `HISTORY.md`.
> v2.18 확인: 코드 프로젝트가 새 지침의 세션 시작(GitHub + 코드 전용 5개)으로 통과 — HISTORY ↔ GitHub 판 일치, 테스트 넷 모두 건너뜀 0.

## 1. 바뀐 것

**`handoff.py apply 넘김.md --deck 기준.pptx -o 결과.pptx [--sha …] [--import 덱이름=경로] [--report 보고.md]`**
- 먼저 `check`(기준 덱 대조 포함) — 오류가 하나라도 있으면 **적용하지 않는다**(종료 1, 결과 파일 없음).
- 순서: 본문 수정(한 조각 1회, 아니면 조각 전체) → 문단 교체·삭제·추가(`…` 줄인 키는 실제 문단으로 풀어서) → 배경·숨김 → 새 슬라이드(틀 화면 복제 → 제목·본문·배경·노트)·가져옴 → **앞에 복제**(원천은 본문 수정·문단 작업이 끝난 덱 — D10; 빨강 제거, `해설 상자 "…"` 는 그 글이 든 도형 하나를 지움, 복제본 대본) → 이동 → 노트(대본·참고, `변경 없음`·`없음` 처리, **기존 메모 보존**) → 삭제·purge.
- 문단 교체는 `keep_format` 으로 — 넘김 줄에 빠진 탭·앞 공백·굵게(D5·D7·D9)를 원래 문단에서 살리고 **경고로 알린다**(조용히 고치지 않는다).
- **원작자 메모 수정 요청은 적용하지 않는다** — 보고서에 남기고, 사용자 허락 뒤 `settext(…, notes=True, zone='memo')`(요청서 3-4).
- 보고서: 한 일, 원작자 메모가 기준과 같은 화면 수(다르면 종료 1), 앞에 복제 내역, 경고, 매핑(밀린 구간), **결과 sha256 앞 16자**(적용 회신에 적는다 → 다음 넘김의 `기준 sha256`), validate.
- 표지 없는 기존 노트를 대본으로 보고 바꾸면 경고 — 기준 덱은 restore-memo·normalize-notes 가 끝난 판이어야 한다.
- 지원하지 않는 작업: `재게시`(멈춤), `메모 복사`(경고, 손으로).

**`handoff.py compare A.pptx B.pptx`** — 화면별 제목·슬라이드 글·노트(대본·참고·메모)·숨김·배경을 비교(서식·위치는 보지 않음). 도구 적용본과 발표가 손으로 만든 판을 대조하는 데 쓴다.

**실물 시험(코드 쪽)**: 사용자가 올렸던 H&N 원본 덱(260화면)에 넘김(문단 교체 1·앞에 복제 1·새 슬라이드 1·노트)을 적용 → validate 통과, 원작자 메모 260/260 그대로, 복제본 빨강 제거·원래 화면 빨강 유지, 새 슬라이드 제목·본문·배경, 렌더 확인. 실제 넘김 16건과 그 기준 덱으로는 **발표가 시험**한다(§4).

**문서** — HANDOFF_FORMAT 1.2(적용·비교 한 단락), DECK_SPEC 16.24 §0-B. `CODE_PROJECT_README` 세션 시작 명령의 `{…}` 묶음 표기가 대화창 셸에서 안 되던 것 수정(지침과 같게).

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| apply-handoff 2단계(요청서 3-3·3-4) | 이 판 |
| 메모 수정을 노트 쓰기 전에(D8) | 메모 수정은 적용하지 않고 `zone='memo'` 로 남김 — 구역을 좁히므로 순서와 상관없이 2회 매치가 안 난다 |
| D5·D7·D9 | keep_format + 경고 |

## 3. 프로젝트별 받을 파일

zip 두 개: `v2.19_GitHub.zip`(GitHub 에 전부), `v2.19_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개). 세 프로젝트는 GitHub.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v39 | `78e9e26fd6c1` | ○ |
| `RELEASE.md` | v2.19 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.24 | `f09b3b497531` | ○ |
| `test_toolkit.py` | v16.24 | `15c15486c38c` | ○ |
| `DECK_SPEC.md` | v16.24 | `6cbaa44bb8ee` | ○ |
| `handoff.py` | v1.2 | `209e750f9094` | ○ |
| `test_handoff.py` | v1.2 | `af9140fe25e9` | ○ |
| `HANDOFF_FORMAT.md` | v1.2 | `de0dc1b86126` | ○ |
| `TOOLS_MANIFEST.md` | v39 | `78e9e26fd6c1` | ○ |
| `RELEASE.md` | v2.19 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v39 | `78e9e26fd6c1` | ○ |
| `RELEASE.md` | v2.19 | — | 이 문서 |

### 코드 (19)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.24 | `f09b3b497531` | ○ |
| `test_toolkit.py` | v16.24 | `15c15486c38c` | ○ |
| `DECK_SPEC.md` | v16.24 | `6cbaa44bb8ee` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v1.2 | `209e750f9094` | ○ |
| `test_handoff.py` | v1.2 | `af9140fe25e9` | ○ |
| `HANDOFF_FORMAT.md` | v1.2 | `de0dc1b86126` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v39 | `78e9e26fd6c1` | ○ |
| `CODE_PROJECT_README.md` | v5 | `369b99ea8f0f` | ○ |
| `HISTORY.md` | — | `45930e1b99d9` | ○ |
| `release.py` | — | `8ce7a3ea9b82` | — |
| `GITHUB_README.md` | — | `60aa56dc93ea` | — |
| `PRIVATE_TERMS.txt` | — | `4285e1f439fb` | — |
| `RELEASE.md` | v2.19 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: git clone 한 줄로 받아 selfcheck. 그리고 **지난 넘김을 실제 기준 덱에 `apply` 하고, 발표가 손으로 만든 판과 `compare`** — 다른 화면이 넘김에 없는 손작업(교육목표 간격 3pt 같은 사용자 결정, 해설 상자 삭제 등) 때문인지 도구 결함인지 가려 회신에. 권하는 순서: 노트만(H&N v12·v13, LGI v3) → 숨김·노트(HBP v2) → 문단 작업(H&N v10) → 새 슬라이드(H&N v9) → keep_format(HBP v1) → 앞에 복제(흉부1·복부2). 무거운 덱은 Cowork 에서.
2. 영상의학·저자·리뷰어: 변경 없음.

## 5. 검증하지 않은 것

실제 넘김 16건 × 실제 기준 덱 적용(발표 §4-1). `가져옴`(다른 덱에서)은 fixture 로도 시험하지 않았다 — 16건 중 H&N v6 한 건뿐이고 그 LGI 덱은 발표 쪽에 있다.
