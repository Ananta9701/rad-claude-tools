# RELEASE v2.23 — manifest v43 — 2026-09-27

> **v2.23** — 교과서 2단계: `textbook.py` 0.2 `plan`(책마다 장 표 제안)과 Cowork 조사 회신(probe 7건) 반영. 다른 도구는 그대로. 이전 판 내용은 `HISTORY.md`.
> 1단계 결과(24권): 글자층은 읽힌 23권 모두 있음, 책갈피로 나눌 수 있는 책은 전자책 4권 — 스캔본은 쪽 머리 "제 N 장" 으로 장을 정한다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `textbook.py` | 0.2 | **`plan`** 신설 — 책마다 장 표(장·제목·PDF 쪽 범위·쪽 수·인쇄 쪽·근거) + "확인할 것". 책갈피가 넉넉하면 'Chapter N'·'N.' 제목이 가장 많은 깊이(앞뒤 Cover·Index 는 앞붙이·뒤붙이, `--level` 로 바꿈), 모자라면 쪽 머리 "제 N 장"·"Chapter N"(OCR 변형 '저1 2 장'·'저15 징'·'제 6 잠' 을 후보 여럿으로 받고, 장 번호는 같거나 +1(+2) 로만, 새 번호는 뒤 12쪽 안에 다시 나와야, 장 번호가 여럿인 쪽은 차례로 보고 버림). 장 시작은 여는 쪽 표지·장 제목으로, 못 찾으면 추정 + 확인할 것. `--budget`(기본 150초)에서 멈추고 다시 돌리면 이어서 |
| | | **probe·plan 공통** — 시작 전에 모든 대상 PDF 의 앞·끝을 읽어 보고 클라우드에만 있는 파일(Errno 35)이 있으면 아무것도 쓰지 않고 멈춤(Cowork 3-1), 차례 찾기에 OCR '차려'·'C O N T E N T S'(3-3), `--recursive`(3-6), `--skip`(3-7) |
| `test_textbook.py` | 0.2 | 16개(+10): 쪽 머리 OCR 변형·차례 쪽 버림, 장 경계 풀이(건너뛴 장·본문 속 "제5장" 잡음), 책갈피 깊이 고르기, 사전 점검이 쓰기 전에 멈춤, 하위 폴더·빼기, plan 쪽 머리·책갈피 PDF, 예산 멈춤·이어하기, CLI |
| `TEXTBOOK.md` | 0.2 | §1 오프라인 먼저·바로가기 대신 대상 폴더, §2 plan 절차, §3 분할 설계(글자층은 OCR — 인용은 원본 쪽 그림으로 확인) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| Cowork `260927_회신_Cowork→코드_교과서probe_결과_v1` 3-1 클라우드에만 있는 원본 | 0.2 사전 점검으로 멈춤 + §1 에 "오프라인으로 사용 가능" 먼저 |
| 3-2 긴 실행(셸 180초) | plan `--budget`·이어하기. 3단계 분할도 같은 방식으로 |
| 3-3 차례 탐지(OCR 로 깨진 "차례") | 차례 낱말 변형 추가. 다만 plan 은 차례보다 **쪽 머리**를 쓴다 — 차례 쪽은 여러 단이 섞여 순서가 뒤엉킨다(12 부인과영상 확인) |
| 3-4 08 두경부(pypdf 로 못 읽음) | 이번 판에 넣지 않음 — 사용자: 방법이 생기면 한다 |
| 3-5 쪽 번호 차이 신뢰도 | plan 은 장마다 최빈값으로 인쇄 쪽을 계산하고, 쪽 번호 표가 있는 책은 그것을 쓴다 |
| 3-6 하위 폴더 | `--recursive` |
| 3-7 빼기 옵션 | `--skip`(여러 번) |
| 발표 `260927_도구회신_병합넘김_준비_v1` M1–M4 | **v2.24** — 사용자 결정(09-27): 교과서 2단계 먼저 |

## 3. 받을 파일

zip 두 개: `v2.23_GitHub.zip`(GitHub 에 전부), `v2.23_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v43 | `e1daedf9fc9e` | ○ |
| `RELEASE.md` | v2.23 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.25 | `85cbd8af803d` | — |
| `test_toolkit.py` | v16.25 | `51cdbea4be1e` | — |
| `DECK_SPEC.md` | v16.25 | `f8f57f8d85df` | — |
| `handoff.py` | v1.4 | `b894bab94cee` | — |
| `test_handoff.py` | v1.4 | `baed9ca329db` | — |
| `HANDOFF_FORMAT.md` | v1.4 | `24e39acfa50d` | — |
| `TOOLS_MANIFEST.md` | v43 | `e1daedf9fc9e` | ○ |
| `RELEASE.md` | v2.23 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v43 | `e1daedf9fc9e` | ○ |
| `RELEASE.md` | v2.23 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.2 | `524aad4672fb` | ○ |
| `test_textbook.py` | v0.2 | `632d0017da78` | ○ |
| `TEXTBOOK.md` | v0.2 | `cf125c3d2d5f` | ○ |
| `TOOLS_MANIFEST.md` | v43 | `e1daedf9fc9e` | ○ |
| `RELEASE.md` | v2.23 | — | 이 문서 |

### 코드 (22)
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
| `handoff.py` | v1.4 | `b894bab94cee` | — |
| `test_handoff.py` | v1.4 | `baed9ca329db` | — |
| `HANDOFF_FORMAT.md` | v1.4 | `24e39acfa50d` | — |
| `textbook.py` | v0.2 | `524aad4672fb` | ○ |
| `test_textbook.py` | v0.2 | `632d0017da78` | ○ |
| `TEXTBOOK.md` | v0.2 | `cf125c3d2d5f` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v43 | `e1daedf9fc9e` | ○ |
| `CODE_PROJECT_README.md` | v5 | `369b99ea8f0f` | — |
| `HISTORY.md` | — | `c75857a79ed2` | ○ |
| `release.py` | — | `d6f02167dda3` | — |
| `GITHUB_README.md` | — | `de9f905c7f6c` | — |
| `PRIVATE_TERMS.txt` | — | `4285e1f439fb` | — |
| `RELEASE.md` | v2.23 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 저자·발표·리뷰어: 도구 변경 없음. 세션 시작 selfcheck 만. 발표 M1–M4 는 v2.24.
2. 교과서(Cowork): `TEXTBOOK.md` §2 — `plan` 을 "남은 책 0권" 이 될 때까지 같은 명령으로 되풀이, 결과는 `Claude 전달함/→코드`. 두경부는 `--skip 두경부`.

## 5. 검증하지 않은 것

- plan 을 실제 교과서에서 한 번도 돌리지 않았다. 쪽 머리 규칙은 조사 md 에서 본 두 권(12 부인과영상, 10 복부영상의학)의 쪽 머리 모양과, 그 OCR 변형을 흉내 낸 문자열 시험뿐이다. 나머지 스캔본의 쪽 머리 모양은 보지 않았다.
- 한글 쪽 머리가 든 PDF fixture 는 못 만들었다(시험 글꼴이 영어뿐) — PDF 끝까지 가는 시험은 영어 "Chapter N" 책뿐이다.
- 책갈피 깊이 고르기는 전자책 4권의 실제 책갈피로 시험하지 않았다(fixture 만).
- 쪽 머리 방법은 모든 쪽의 글자를 뽑는다 — 800쪽 책의 시간은 조사 속도(표본 60쪽)로 어림한 값뿐이다.
