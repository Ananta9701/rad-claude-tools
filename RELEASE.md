# RELEASE v2.25 — manifest v45 — 2026-09-27

> **v2.25** — 교과서 3단계(`textbook.py` 0.4: split·page·search)와 발표 회신 세 건(`handoff.py` 1.6, `deck_toolkit.py` 16.26 이름표 폭). 전달 규약 v3(폴더 `→` → `to`, 09-27 사용자 결정 — id 그대로). claim_graph·verify 는 그대로. 이전 판 내용은 `HISTORY.md`.
> 사용자 결정(09-27): 장별 원본 PDF 는 만들지 않는다(글자 md + 필요한 쪽만 그림), Gemini 는 수동 조사 + 로컬 찾기(API 자동화 안 함), 한 판으로 올린다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `textbook.py` | 0.4 | **split** — 확인한 plan 장 표로 책마다 `{번호}_{책}/` 에 앞붙이·장·뒤붙이 md 와 INDEX, 맨 위 INDEX. 장 파일마다 앞뒤 2쪽 겹침(표지), 30쪽 넘는 장은 나눔, 쪽 표지 `[p.인쇄 · PDF]`. 책마다 하위 프로세스·예산 이어하기, INDEX 가 끝 표시. **page** — 인쇄 쪽(INDEX 로) 또는 PDF 쪽의 이미지를 PNG 로(스캔본은 쪽 전체). **search** — 분할 md 에서 띄어쓰기 무시 찾기, 겹침 쪽은 제 장 파일로 한 번. **plan 고침**: 예산을 목록·사전 점검부터 재고 기본 120초, 다 만든 뒤에 md 를 열어 씀(0바이트 원인), 0바이트·깨진 md 는 다시 함·요약에서 "남음". 기본 이름·`--name` 에 `→` 안 씀. **장 표 v2 검토 뒤 보강**: 앞붙이·뒤붙이도 30쪽씩(뒤붙이 509쪽 한 파일 방지), 수상하게 긴 장의 뒤쪽은 `미확인` 이름(사용자 결정 나), `Chapter N` 제목을 하위 책갈피 이름으로(Gore), 쪽 번호 표가 있으면 그 번호로 표지·INDEX·`page --printed`, plan 은 여는 쪽 표지를 제목 일치보다 먼저·쪽 머리 없는 꼬리 60쪽 넘으면 경고 |
| `test_textbook.py` | 0.4 | 27개(+7): 책 이름 줄이기, 0바이트 md 이어하기, split 끝까지(겹침 표지·INDEX·인쇄→PDF·다시 돌리면 건너뜀)와 찾기, 긴 장 나누기, 쪽 그림, 여는 쪽 먼저·꼬리 경고·앞뒤 나눔·미확인 이름·Chapter N 제목 채움, 쪽 번호 표 |
| `TEXTBOOK.md` | 0.4 | §3 split·page·search 절차, 도구 경로 `~/rct`, 결과 폴더 `to코드` |
| `handoff.py` | 1.6 | **Y1** 연도 규칙 강조를 출제줄(⇥ 문단)의 범위 안 번호 서식으로(3개 미만이면 덱 전체, 못 정하면 경고). **R2** 대본·참고의 `**` 를 노트에 넣을 때 지움 + 문법 경고. **K1** 결과 zip 항목 시각 고정(같은 입력 → 같은 sha), 보고서에 내용 해시, `기준 sha256` 이 내용 해시와 맞으면 경고만. **K2** 결과를 임시 폴더에서 만들어 마지막에 복사. **K4** validate.py 가 없으면 "건너뜀(통과 아님)". 미리보기 제목 앞 `—` 제거 |
| `test_handoff.py` | 1.6 | 22개(+2): 출제줄 기준 빨강·`**` 지움, 두 번 적용 sha 같음·내용 해시 대조·validate 건너뜀 |
| `HANDOFF_FORMAT.md` | 1.6 | v1.6 규칙 한 문단, `기준 sha256` 에 내용 해시 허용 |
| `deck_toolkit.py` | 16.26 | **K6** `widen_label(n, name=|pattern=, min_width_in=2.0)`·CLI `widen-labels` — 채우기·테두리 없는 글상자만, 정렬 쪽 모서리 고정, 글·크기·색 불변, 슬라이드 밖이면 건너뜀 |
| `test_toolkit.py` | 16.26 | 171개(+1): 오른쪽·왼쪽 고정, 채우기 있는 상자·밖으로 나가는 상자 건너뜀 |
| `DECK_SPEC.md` | 16.26 | 판 기록 한 줄, 전달함 폴더 이름 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 발표 `260927_도구회신_첫실전적용_v1` R1 (보내는 쪽 sha 자리) | 전달 규약 v3 §4 — `{같은 줄기}_보냄기록.md` 한 줄(이름·바이트·sha256 앞 16자) |
| R2 (`**` 가 노트에) | handoff 1.6 |
| 발표 `260927_도구회신_Cowork실전시험_v1` K1 (sha 비결정) | handoff 1.6 — zip 정규화 + 내용 해시(기계가 다르면 압축 결과가 다를 수 있어 내용 해시를 함께) |
| K2 (동기화 폴더에 바로 쓰기 실패) | handoff 1.6 |
| K3 (`/tmp/rct`) | README·TEXTBOOK·전달 규약 v3 — Cowork 는 `~/rct` |
| K4 (validate 건너뜀을 통과로) | handoff 1.6 |
| K5 (`→` 폴더 연결 거부) | 폴더 이름 `to…` 로 바꿈(09-27, 사용자 결정 가). 이 이름으로 연결되는지는 다음 Cowork 작업에서 확인 |
| 발표 `260927_도구회신_병합시험_v1` Y1 | handoff 1.6 |
| 미리보기 `—` | handoff 1.6 |
| K6 이름표 폭 | deck 16.26 |
| Cowork `260927_회신_Cowork→코드_교과서plan_v2_결과_v1` 3-1 예산 | textbook 0.4 |
| 3-2 0바이트 거짓 완료 | textbook 0.4 — 원인은 하위 프로세스가 md 를 먼저 열어 비운 채 계산한 것(Killed 면 0바이트가 남는다) |
| 3-3 메모리 2.6 GB | 고치지 않음 — 책마다 하위 프로세스로 한 권씩만. 더 큰 책에서 죽으면 알려 달라 |

## 3. 받을 파일

zip 두 개: `v2.25_GitHub.zip`(GitHub 에 전부), `v2.25_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v45 | `8495c7f6da1d` | ○ |
| `RELEASE.md` | v2.25 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.26 | `cab6d76ae0d8` | ○ |
| `test_toolkit.py` | v16.26 | `b9405ff4bfd8` | ○ |
| `DECK_SPEC.md` | v16.26 | `ac64f8ec2607` | ○ |
| `handoff.py` | v1.6 | `267652b14b3e` | ○ |
| `test_handoff.py` | v1.6 | `2b94fe5cae1f` | ○ |
| `HANDOFF_FORMAT.md` | v1.6 | `1e05b05950d4` | ○ |
| `TOOLS_MANIFEST.md` | v45 | `8495c7f6da1d` | ○ |
| `RELEASE.md` | v2.25 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v45 | `8495c7f6da1d` | ○ |
| `RELEASE.md` | v2.25 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.4 | `6372db295c4c` | ○ |
| `test_textbook.py` | v0.4 | `94a34fd8445f` | ○ |
| `TEXTBOOK.md` | v0.4 | `7f92ff9511f3` | ○ |
| `TOOLS_MANIFEST.md` | v45 | `8495c7f6da1d` | ○ |
| `RELEASE.md` | v2.25 | — | 이 문서 |

### 코드 (22)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.26 | `cab6d76ae0d8` | ○ |
| `test_toolkit.py` | v16.26 | `b9405ff4bfd8` | ○ |
| `DECK_SPEC.md` | v16.26 | `ac64f8ec2607` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v1.6 | `267652b14b3e` | ○ |
| `test_handoff.py` | v1.6 | `2b94fe5cae1f` | ○ |
| `HANDOFF_FORMAT.md` | v1.6 | `1e05b05950d4` | ○ |
| `textbook.py` | v0.4 | `6372db295c4c` | ○ |
| `test_textbook.py` | v0.4 | `94a34fd8445f` | ○ |
| `TEXTBOOK.md` | v0.4 | `7f92ff9511f3` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v45 | `8495c7f6da1d` | ○ |
| `CODE_PROJECT_README.md` | v5 | `6db694b44ea6` | ○ |
| `HISTORY.md` | — | `e9a32b3e8fbe` | ○ |
| `release.py` | — | `d6f02167dda3` | — |
| `GITHUB_README.md` | — | `a338fce401db` | ○ |
| `PRIVATE_TERMS.txt` | — | `d2562278023a` | ○ |
| `RELEASE.md` | v2.25 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

0. **모든 프로젝트 지침**: `→` 를 `to` 로(폴더 `to코드`·`to발표`·`to영상의학`·`to저자`·`to리뷰어`, id 그대로) — 맨 위 `260927_통보_코드to전체_Drive전달규약_v3`. Cowork 는 도구를 `~/rct` 로.
1. 발표: selfcheck(handoff 1.6·deck 16.26). 이름표는 `widen-labels --pattern "\(R\d [^)]*\)" --dry-run` 으로 먼저 보고 적용, PowerPoint·Drive 미리보기 확인은 사용자. 다음 적용 회신부터 보고서의 내용 해시도 적는다.
2. 영상의학: 넘김을 올리면 `…_보냄기록.md` 한 줄(전달 규약 v3 §4). 참고에 `**` 를 쓰지 않아도 된다(지워진다).
3. 교과서(Cowork): 사용자가 장 표 확인용 md(`교과서 분할/260927_장표확인_v1.md`)로 장 수·제목을 확인한 뒤 `TEXTBOOK.md` §3 의 split. 제목 고침은 plan md 의 표 줄에. 그 전에는 돌리지 않는다.
4. 저자·리뷰어: 폴더 이름만.

## 5. 검증하지 않은 것

- split·page·search 는 fixture PDF 와 이 컨테이너의 tesseract "그림 + OCR 글자층" PDF 로만 돌렸다. 실제 스캔 책의 이미지 방식(JBIG2 등)을 pypdf 가 풀지 못하면 page 가 실패한다 — 첫 실행에서 드러난다.
- 30쪽 나눔이 대화창이 한 번에 읽기에 알맞은지는 어림이다.
- Drive 검색이 `교과서 분할` 의 md 를 찾는지(대화창 낱말 찾기)는 첫 분할 뒤 확인한다.
- handoff 의 sha 고정은 같은 기계에서만 보장된다(zlib 판이 다르면 압축 결과가 다를 수 있다) — 그래서 내용 해시를 함께 쓴다.
- `→` 를 바꾼 폴더 이름으로 Cowork 연결이 되는지 모른다.
