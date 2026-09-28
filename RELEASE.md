# RELEASE v2.35 — manifest v55 — 2026-09-28

> **v2.35** — 발표 `260928_도구회신_K17fitlayout2단계_결함_v1`·`260928_통보_발표to코드_K17제목빼기범위_v1` 처리. `deck_toolkit.py` 16.34 하나. 이전 판 내용은 `HISTORY.md`.
> `fit-layout` 1단계 첫 실물(대본 v5)에서 결함 셋(F1–F3) — 모두 코드 쪽. 사용자 결정(09-28): 같은 제목 묶음은 첫 장에만(겹침과 상관없이). K15-1 색은 실물 확인("글자는 다 잘 확인된다").

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.34 | `fit-layout` 2단계. **F1** 본문 상자 높이 = 추정 글 높이 × 1.1(`--text-margin`) 로 적어 넣음. **F2** 겹침을 그 저장 위치로 판정, 글 폭은 테마 본문 글꼴 파일로(있으면). **F3** 띠–본문 간격 기본 0.2". **S1** `--drop-repeat-titles all\|overlap` — 제목·띠 도형을 빼고 그 자리까지 영역, 노트 그대로. **S2·S3** `--arrange side`(그림이 본문 오른쪽이면 auto 가 고름): 그림 덩어리를 오른쪽 위에 붙여 비율로, 본문은 왼쪽 칸으로 좁히고 글자를 `--body-max`(없으면 `--like` 화면 본문 크기) 까지 키울 수 있음 — 칸에 드는 가장 큰 크기. **S4** 이름표를 `--like` 화면의 자리·맨 앞 층으로, 그림은 이름표와도 안 겹치게. 그림 바로 바깥의 작은 설명 상자는 그림과 같이 움직임 |
| `test_toolkit.py` | 16.34 | 180개(+1): 같은 제목 세 장에서 둘째·셋째 제목 뺌, 옆 배치(글 왼쪽·그림 오른쪽·제목 뺀 자리까지 위로), 본문 높이 줄여 적음, 14pt → 기준 본문 크기 쪽으로 키움, 이름표 기준 자리·맨 앞·그림과 안 겹침 |
| `DECK_SPEC.md` | 16.34 | 판 기록 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| F1 spAutoFit 높이 | deck 16.34 |
| F2 겹침 판정 낙관적 | deck 16.34 — 원인 둘(F1, 추정 글 영역으로 판정) 모두. 글 높이는 여전히 추정이라 여유(1.1)를 두었다 — 그림이 조금 작게 나올 수 있다 |
| F3 간격 | deck 16.34 기본 0.2" |
| S1 반복 제목 빼기 | deck 16.34 `--drop-repeat-titles all`(사용자 결정 가) |
| S2 옆 배치·글자 키우기 | deck 16.34 `--arrange side`(auto) + `--body-max`/`--like` |
| S3 그림 오른쪽 끝(87·88) | S2 와 같은 기능 — 넘치는 그림은 영역 높이에 맞게 비율로 줄인다 |
| S4 이름표 | deck 16.34 — 이름표 자리·맨 앞. 그림 설명·인용 자리 규칙(§0)은 아직 — 설명 상자는 그림과 같이 움직이기만 |

## 3. 받을 파일

zip 두 개: `v2.35_GitHub.zip`(GitHub 에 전부), `v2.35_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v55 | `fbad09e09b67` | ○ |
| `RELEASE.md` | v2.35 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.34 | `2deea648cc99` | ○ |
| `test_toolkit.py` | v16.34 | `54cc28ebee76` | ○ |
| `DECK_SPEC.md` | v16.34 | `83786baadd59` | ○ |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v55 | `fbad09e09b67` | ○ |
| `RELEASE.md` | v2.35 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v55 | `fbad09e09b67` | ○ |
| `RELEASE.md` | v2.35 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v55 | `fbad09e09b67` | ○ |
| `RELEASE.md` | v2.35 | — | 이 문서 |

### 코드 (22)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.34 | `2deea648cc99` | ○ |
| `test_toolkit.py` | v16.34 | `54cc28ebee76` | ○ |
| `DECK_SPEC.md` | v16.34 | `83786baadd59` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v55 | `fbad09e09b67` | ○ |
| `CODE_PROJECT_README.md` | v5 | `6db694b44ea6` | — |
| `HISTORY.md` | — | `cb8ba1a59193` | ○ |
| `release.py` | — | `00abde82a376` | — |
| `GITHUB_README.md` | — | `a338fce401db` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.35 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: 인터벤션 **대본 v2 에서 다시** → v6. 26–34·87·88: `fit-layout --screens 26-34,87,88 --like 35 --drop-repeat-titles all --dry-run`(26 은 제목 남음, 27–34 는 뺌) → 목록을 사용자와 → 적용 → 사용자가 PowerPoint 로 겹침·여백 확인.
2. 그 밖의 프로젝트: 도구 변경 없음.

## 5. 검증하지 않은 것

- 글 높이는 여전히 추정(글꼴 파일이 없으면 0.5em 모델)이다. Cowork Mac 에 렌더가 없어 **확인은 사용자 PowerPoint 화면뿐** — 여유 1.1 로도 겹치면 `--text-margin 1.2` 로.
- 옆 배치에서 본문 글자를 키울 상한은 `--like` 화면 본문의 가장 큰 글자 크기로 잡는다 — 그 화면의 본문이 제목 같은 큰 글을 담고 있으면 상한이 커진다. 그러면 `--body-max` 를 준다.
- fixture(본문 글상자 하나·그림 하나·이름표)와 이 컨테이너 LibreOffice 렌더로만 봤다. 그림이 여럿이거나 그룹인 화면은 dry-run 에서 처음 본다.
