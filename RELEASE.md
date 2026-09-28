# RELEASE v2.33 — manifest v53 — 2026-09-28

> **v2.33** — 발표 `260927_도구회신_K13상속제목띠_v1`·`260928_도구회신_diff상자순서_bake잔여넘침_v1`·`260928_도구회신_K14가져온슬라이드_본문내리기_색_v1`(+ `260928_통보_발표to코드_K14사용자결정_v1`) 처리. `deck_toolkit.py` 16.32 하나. 이전 판 내용은 `HISTORY.md`.
> 사용자 결정(09-28): 가져온 해설 슬라이드는 제목 띠 아래로 본문(§0-C 예외 — 지정한 화면만), 연두·주황은 검정(테마 글자색), 빨강은 강조로 남김, 옛 제목 밑줄은 지운다. 화면 149·250 은 bake 하지 않은 원래 모양으로(발표). K11 나누기 실물 확인(사용자 "제대로 나옴").

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.32 | **K13** 물려받는 제목(슬라이드에 위치 없음)도 `title-bands` 세 방식 대상 — 바꿀 때 위치·크기·안쪽 여백을 그 슬라이드에 적어 넣는다(모양 그대로, 레이아웃 불변), 보고 "물려받던 제목 — 적어 넣음". 제목 정보가 여백·**채움**을 레이아웃(위치가 없는 자리 표시자도) → 마스터에서 물려받는다 — 전에는 채움을 슬라이드에서만 봐 `--balance` 가 '회색 띠 아님' 으로 조용히 건너뛰었다. **D1** `diff` 가 '의도하지 않은 글 변경' 을 상자별 글 모음으로(순서 무시·조각 합침 같음). **D2** `bake-autofit` 결함: pt 고정 줄 간격(`spcPts`) 문단에 `lnSpc` 를 하나 더 넣어 문단마다 줄 간격이 두 개가 됐다(재현 확인) — 이제 그 pt 에서 lnSpcReduction 비율만 뺀다. 넘침 계산이 pt 줄 간격을 읽는다(전에는 무시하고 글자 크기 × 1.22 로 쟀다) |
| `deck_toolkit.py`(K14) | 16.32 | **K14** `adopt-house-look` 에 `--recolor 색,색`(지정한 색만 테마 글자색 — 빨강 등은 그대로), `--title-band --band-height 인치 \| --like N`(제목 띠 높이·위아래 여백 같게, 물려받는 제목은 적어 넣음), `--drop-title-rule`(띠 안 가로선 하나 지움 — 둘 이상이면 알림), `--push-content [--gap 0.1] [--min-pt 12]`(띠 아래 간격보다 위의 상자·그림을 한 덩어리로 내림, 아래를 넘는 글상자는 넘는 만큼 글자 비율로 줄이고 상자를 슬라이드 안으로, 그림은 옮기기만). 기본은 내리지도 지우지도 않고 [참고] 로 알림. dry-run 은 사본 덱에서 실제로 해 보고 저장하지 않는다 |
| `test_toolkit.py` | 16.32 | 178개(+2): 물려받는 제목 키우기·균형(적어 넣음·레이아웃 불변·채움 물려받음), diff 상자 순서·조각 합침은 같은 글·진짜 변경은 잡음, bake pt 줄 간격(중복 없음·2700→2160·글자 55%), K14(색·띠·밑줄·본문 내림·글자 비율·아래 이름표 그대로·기본은 알림만) |
| `DECK_SPEC.md` | 16.32 | 판 기록 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| K13 물려받는 제목도 title-bands 로 | deck 16.32. 원인 둘: 위치가 없으면 도구가 '상속 — 바꾸지 않음' 으로 돌려보냈고, `--balance` 는 채움을 슬라이드에서만 봐 레이아웃이 칠한 회색 띠를 못 알아봤다 |
| 참고: 원래 덱 제목 넘침 36화면 | 도구 변경 없음 — 발표·사용자가 따로 |
| D1 diff 상자 순서 | deck 16.32 — 발표 제안대로 |
| K14 가져온 해설 슬라이드 — 제목 띠 + 그 아래 본문, 색 | deck 16.32 `adopt-house-look` 옵션 넷. 사용자 결정 두 가지(빨강 남김·옛 밑줄 지움) — 도구 기본값은 '알림만'(발표가 옵션으로 켠다). §0-C 에 예외 한 줄 |
| K14 참고: 화면 149·250 bake 안 함 | 도구 변경 없음(발표가 대상에서 뺀다) — D2 결함 수정은 그대로 넣었다 |
| D2 bake 뒤 넘침 추정 2곳 | **결함 하나 확인**: pt 고정 줄 간격 문단에 lnSpc 중복(Google 내보내기 상자에 흔하다 — 두 상자 이름이 `Google Shape;…`). 고쳤다. 넘침 계산도 pt 줄 간격을 읽게 했다. **남은 불확실**: PowerPoint 의 자동 맞춤이 pt 줄 간격·문단 앞 간격(spcBef pt)을 글자 비율로 줄이는지 명세로는 알 수 없다 — 도구는 명세 문구대로 줄 간격에서 축소 비율만 뺀다. 두 화면(148·249)은 bake 를 다시 한 뒤 사용자가 PowerPoint·Google Slides 로 본다 |

## 3. 받을 파일

zip 두 개: `v2.33_GitHub.zip`(GitHub 에 전부), `v2.33_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v53 | `8ad8bb712d53` | ○ |
| `RELEASE.md` | v2.33 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.32 | `2e810da2db3a` | ○ |
| `test_toolkit.py` | v16.32 | `218c6138bb7c` | ○ |
| `DECK_SPEC.md` | v16.32 | `d5b80329a1e2` | ○ |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v53 | `8ad8bb712d53` | ○ |
| `RELEASE.md` | v2.33 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v53 | `8ad8bb712d53` | ○ |
| `RELEASE.md` | v2.33 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v53 | `8ad8bb712d53` | ○ |
| `RELEASE.md` | v2.33 | — | 이 문서 |

### 코드 (22)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.32 | `2e810da2db3a` | ○ |
| `test_toolkit.py` | v16.32 | `218c6138bb7c` | ○ |
| `DECK_SPEC.md` | v16.32 | `d5b80329a1e2` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v53 | `8ad8bb712d53` | ○ |
| `CODE_PROJECT_README.md` | v5 | `6db694b44ea6` | — |
| `HISTORY.md` | — | `0ae8f5dc1218` | ○ |
| `release.py` | — | `00abde82a376` | — |
| `GITHUB_README.md` | — | `a338fce401db` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | ○ |
| `RELEASE.md` | v2.33 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: 인터벤션 **대본 v2 에서 다시**(발표 계획대로) — 화면 26–34 `adopt-house-look --screens 26-34 --recolor 92D050,FFC000 --title-band --like 35 --drop-title-rule --push-content --dry-run` → 사용자와 → 적용. 이어서 인터벤션 화면 80–88(근골격 95·96 도)에 `title-bands --dry-run`(필요하면 `--shrink-bottom-inset`·`--balance --like N`) — 이제 "물려받던 제목 — 적어 넣음" 줄이 나와야 한다. **D2**: v1 에서 bake 한 화면 148·249 는 v2.32 bake 로 lnSpc 가 두 개일 수 있다 — 원래 판(bake 전)에서 v2.33 로 다시 bake 하고 `overflow` 로 본 뒤 사용자 화면 확인.
2. 그 밖의 프로젝트: 도구 변경 없음.

## 5. 검증하지 않은 것

- K13 은 python-pptx 기본 템플릿(마스터에서 위치를 물려받음)으로만. 인터벤션 slideLayout19 처럼 레이아웃이 위치·채움을 따로 가진 경우는 발표 dry-run 에서 본다.
- D2 의 PowerPoint 자동 맞춤 의미(pt 줄 간격·문단 앞 간격을 줄이는지)는 확인하지 않았다.
- K14 는 python-pptx fixture 한 장으로(제목은 마스터에서 물려받음, 본문 글상자 하나, 가로선 하나, 아래 이름표). 실제 slide338–346 의 본문이 여러 상자·그림일 때 한 덩어리로 내린 뒤 서로 겹치지 않는지, 글자 비율로 줄인 뒤 줄바꿈이 달라지는지는 dry-run·사용자 화면으로 본다.
