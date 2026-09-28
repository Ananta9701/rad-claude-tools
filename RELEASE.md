# RELEASE v2.34 — manifest v54 — 2026-09-28

> **v2.34** — 발표 `260928_도구회신_K15인터벤션서식_색_글자_그림_띠도형_v1`·`260928_도구회신_K16밀집화면배치양식_K15개정_v1` 처리. `deck_toolkit.py` 16.33 하나. 이전 판 내용은 `HISTORY.md`.
> 사용자 결정(09-28): K16 은 단계로 — 이번은 1단계(제목 띠 촘촘히·본문 글자·그림+주석 비율). 그림 설명·인용·이름표 자리와 반복 제목 빼기는 1단계 결과를 보고 2단계. 색은 흰색·검정만 덱 글자색, 그 밖은 강조로 남기고 안 보이는 것만 진하게. DECK_SPEC §0 사용자 결정 6줄.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.33 | **K15-1 개정** `adopt-house-look --recolor` 가 색 이름(`prstClr` white 등)·테마 색 이름을 받는다(흰 글자 61조각이 `prstClr` 라 v2.33 이 못 잡음), `--no-auto-light`, `--darken-low-contrast [--min-contrast 3.0]`(배경 대비가 모자란 강조색만 같은 색상으로 진하게, 다른 글자색·빨강과 색차 20 이상). **K15-3** 따로 그린 띠 도형을 띠로 알아봄 — 제목 자리 표시자를 그 위치로, 띠 높이 = max(규격, 제목 높이)로 도형과 함께, 위치를 물려받는 본문 자리 표시자도 적어 넣고 내린다. **K16 1단계** `fit-layout` — 제목 띠 촘촘히(20pt 까지), 본문 14pt 까지, 그림+주석을 구석 고정 비율(0.5×–1.5×)로 본문 글과 안 겹치는 가장 큰 크기, 안 되면 [!] 나누기 필요. `--dry-run`·`--render 폴더`(LibreOffice 있는 곳) |
| `test_toolkit.py` | 16.33 | 179개(+1): 색(white·검정 → 테마, 노랑 남겨 진하게·대비 3 이상·빨강과 구분, 빨강 그대로), 띠 도형(제목·도형 같이 1.8", 본문 자리 표시자 적어 넣고 내림), fit-layout(띠 위에 붙음·그림 영역 안·본문 글과 안 겹침·주석 그림 안·이름표 그대로·너무 많은 글이면 바꾸지 않음) |
| `DECK_SPEC.md` | 16.33 | §0 사용자 결정 6줄(글자색·밀집 화면 배치 순서·그림 위 주석·그림 설명·인용/이름표·글 내용 불변), 판 기록 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| K15-1 색(개정) | deck 16.33 — `--recolor white,black,FFFFFF,000000 --no-auto-light --darken-low-contrast` |
| K15-2 14pt·그림 | K16 으로 바뀜(발표) — `fit-layout` 1단계 |
| K15-3 따로 그린 띠 도형 | deck 16.33 — 도형을 지우고 자리 표시자에 채움을 옮기는 대신, 도형과 자리 표시자를 같은 위치·높이로 함께 움직인다(모양 그대로) |
| K16 밀집 화면 배치 | **1단계** 만 — 사용자 결정(단계로). 2단계: 그림 설명을 그림 옆에·인용 우하단·이름표 템플릿 자리·`--drop-repeat-titles` |
| DECK_SPEC §0 추가안 | 6줄 반영 |

## 3. 받을 파일

zip 두 개: `v2.34_GitHub.zip`(GitHub 에 전부), `v2.34_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v54 | `d1793ed65938` | ○ |
| `RELEASE.md` | v2.34 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.33 | `3c866da7affb` | ○ |
| `test_toolkit.py` | v16.33 | `ecb721b5b4aa` | ○ |
| `DECK_SPEC.md` | v16.33 | `5f14631a16e1` | ○ |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v54 | `d1793ed65938` | ○ |
| `RELEASE.md` | v2.34 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v54 | `d1793ed65938` | ○ |
| `RELEASE.md` | v2.34 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v54 | `d1793ed65938` | ○ |
| `RELEASE.md` | v2.34 | — | 이 문서 |

### 코드 (22)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.33 | `3c866da7affb` | ○ |
| `test_toolkit.py` | v16.33 | `ecb721b5b4aa` | ○ |
| `DECK_SPEC.md` | v16.33 | `5f14631a16e1` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v54 | `d1793ed65938` | ○ |
| `CODE_PROJECT_README.md` | v5 | `6db694b44ea6` | — |
| `HISTORY.md` | — | `5cc4710f805d` | ○ |
| `release.py` | — | `00abde82a376` | — |
| `GITHUB_README.md` | — | `a338fce401db` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.34 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: 인터벤션 **대본 v2 에서 다시** → v5. 화면 26–34: `adopt-house-look --screens 26-34 --recolor white,black,FFFFFF,000000 --no-auto-light --darken-low-contrast --title-band --like 35 --drop-title-rule --push-content` → `fit-layout --screens 26-34 --dry-run --render <폴더>`(렌더가 Cowork VM 에서 안 되면 결과 덱을 사용자가 PowerPoint 로). 화면 81–89: `adopt-house-look --screens 81-89 --no-auto-light --title-band --like 35 --push-content --dry-run`(띠 도형). 목록·그림을 사용자와 본 뒤 적용.
2. 그 밖의 프로젝트: 도구 변경 없음.

## 5. 검증하지 않은 것

- `fit-layout` 은 fixture 한 장(본문 글상자 하나·그림 하나·주석 하나·이름표)과 이 컨테이너의 LibreOffice 렌더로만 봤다. 글 높이는 추정(0.5em 모델·줄 높이 1.22)이라 실제 줄바꿈과 다를 수 있고, 여러 그림·그림 든 그룹·본문 자리 표시자가 여럿인 화면은 처음이다 — dry-run 목록과 렌더(또는 PowerPoint)를 사용자가 본 뒤 적용.
- 주석 판정(그림 안에 70% 이상)은 그림 옆에 붙은 설명 상자를 주석으로 보지 않고, 그림 위에 걸친 큰 글상자를 본문으로 볼 수 있다.
- `--darken-low-contrast` 의 대비 기준(3.0)과 색차(ΔE 20)는 정한 값이 아니라 기본값이다 — 노랑이 어떤 색으로 바뀌는지 사용자가 본다.
