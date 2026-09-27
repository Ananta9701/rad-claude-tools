# RELEASE v2.22 — manifest v42 — 2026-09-27

> **v2.22** — 교과서 분할·색인 1단계: `textbook.py` v0.1(구조 조사 probe)과 `TEXTBOOK.md`, manifest 에 **교과서** 역할(Cowork). 다른 도구는 그대로. 이전 판 내용은 `HISTORY.md`.
> 대화창의 Drive 연결은 교과서 스캔 PDF 의 내용을 읽지 못했다(3권 시도, 빈칸) — 분할 규칙은 Cowork 의 조사 결과를 보고 정한다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `textbook.py` | 0.1 (신규) | `probe 폴더 --out 결과폴더` — 책마다 크기·쪽 수·만든 프로그램·책갈피 전체·PageLabels·앞 40쪽 글자 수/그림/쪽 머리·"차례·목차·Contents" 쪽 글자 전부·본문 표본 20쪽·PDF 쪽 − 인쇄 쪽 최빈값. 요약 md + 책마다 md. 원본은 읽기만, 같은 이름 덮어쓰기 거부, 이름에 `& / ?` 거부, `--only` 는 한글 NFC/NFD 를 맞춰 찾음(Mac 파일 이름). pypdf 필요(없으면 설치 방법을 알리고 멈춤, `/tmp/pypdf` 소스도 찾음) |
| `test_textbook.py` | 0.1 (신규) | fixture PDF(pypdf 로 생성: 책갈피 2단·PageLabels·빈 쪽·깨진 PDF) 6개. pypdf 가 없으면 건너뛰지 않고 실패 |
| `TEXTBOOK.md` | 0.1 (신규) | 단계(조사 → 규칙 → 분할 → 읽기), Cowork 조사 절차, 결과 읽는 법, 분할 설계 초안 |
| manifest §2 | — | **교과서** 열(Cowork 역할, `selfcheck --role 교과서`): textbook 3종 + manifest + RELEASE. GitHub 공개 세트 = 네 역할의 합 |

`claim_graph selfcheck` 는 역할을 manifest §2 열에서 읽으므로 코드 변경 없음(`--role` 도움말 글자만 옛 네 역할 — 다음에 claim_graph 를 고칠 때 같이).

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 발표 `260927_도구회신_v2.21_재시험_v1` — N1·N2·N3 확인, "새 넘김은 도구 적용 + 보고서 확인" | 받음. 발표 쪽 시험 종결 |
| 같은 회신 N4 (첫 가져옴 본문 크기가 원천 덱 값으로 고정) | 이번 판에 넣지 않음 — 발표 판단대로 급하지 않다(첫 가져옴에만). HISTORY §5 미결 |
| 같은 회신 N5 (`compare` 서식이 명시·상속 크기를 다르게 봄) | 이번 판에 넣지 않음 — 비교 도구 잡음. HISTORY §5 미결 |
| 메모 `260927_메모_코드_다음할일_v1` | 교과서 1단계를 이번 판으로. 나머지는 HISTORY §5 로 옮김 |

## 3. 받을 파일

zip 두 개: `v2.22_GitHub.zip`(GitHub 에 전부 — 새 파일 3개 포함), `v2.22_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v42 | `7e053d510158` | ○ |
| `RELEASE.md` | v2.22 | — | 이 문서 |

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
| `TOOLS_MANIFEST.md` | v42 | `7e053d510158` | ○ |
| `RELEASE.md` | v2.22 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v42 | `7e053d510158` | ○ |
| `RELEASE.md` | v2.22 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.1 | `07b822fe3520` | 신규 |
| `test_textbook.py` | v0.1 | `e553d3b362c9` | 신규 |
| `TEXTBOOK.md` | v0.1 | `301b6fa47092` | 신규 |
| `TOOLS_MANIFEST.md` | v42 | `7e053d510158` | ○ |
| `RELEASE.md` | v2.22 | — | 이 문서 |

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
| `textbook.py` | v0.1 | `07b822fe3520` | 신규 |
| `test_textbook.py` | v0.1 | `e553d3b362c9` | 신규 |
| `TEXTBOOK.md` | v0.1 | `301b6fa47092` | 신규 |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v42 | `7e053d510158` | ○ |
| `CODE_PROJECT_README.md` | v5 | `369b99ea8f0f` | — |
| `HISTORY.md` | — | `f2fc57d34cab` | ○ |
| `release.py` | — | `d6f02167dda3` | ○ |
| `GITHUB_README.md` | — | `de9f905c7f6c` | ○ |
| `PRIVATE_TERMS.txt` | — | `4285e1f439fb` | — |
| `RELEASE.md` | v2.22 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 저자·발표·리뷰어: 도구 변경 없음. 세션 시작 selfcheck 만.
2. 교과서(Cowork): `TEXTBOOK.md` §1 — 교과서 폴더를 동기화 폴더 안에 보이게 한 뒤 `probe` 를 돌려 `Claude 전달함/→코드` 에 결과를 쓴다. 한 권(`--only`)으로 먼저 돌려 시간을 보고 전체로.

## 5. 검증하지 않은 것

- 실제 교과서 PDF 에서 한 번도 돌리지 않았다. 시험은 pypdf 로 만든 fixture 와, 이 컨테이너에서 tesseract 로 만든 "그림 + 보이지 않는 OCR 글자층" 2쪽 PDF(글자층·그림 판정 확인)뿐이다.
- Cowork VM 에 pypdf 가 있는지, `pip install` 이 되는지 모른다(`git clone` 은 09-26 통과).
- 1 GB 스캔 PDF 에서 pypdf 가 걸리는 시간과 메모리, Drive 데스크톱이 큰 파일을 읽을 때 통째로 내려받는지 모른다.
