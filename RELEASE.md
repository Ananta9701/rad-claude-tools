# RELEASE v2.41 — manifest v61 — 2026-09-28

> **v2.41** — 발표 `260928_도구회신_K21상자메모_K22옆배치판정_v1`, 리뷰어 `260928_도구회신_문헌시험_md판정채점_리뷰어_v1`·`260928_도구회신_공식API경로_제안_리뷰어_v1`. `deck_toolkit.py` 16.37·`literature.py` 0.4. 이전 판 내용은 `HISTORY.md`.
> 인터벤션 대본 v6: 사용자 "27 과 87·88 말고는 다 잘됐다". 문헌: **끝까지 한 번 통과** — paper.md 만으로 한 판정 = PDF 로 한 판정(2편, 두 번째 조판 Wiley).

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.37 | **K21** `box-to-memo --screens … --match 글` — 출처 메모 글상자를 노트 기존 메모 구역 끝으로 옮기고 지움(정확히 하나일 때만, 구역이 없으면 표지부터). **K22-1** `fit-layout --arrange auto` 는 그림이 본문 **옆** 일 때만 옆 배치(그림 윗끝이 본문 상자 위쪽 60% 안) — 화면 27(본문 위 전폭·그림 아래)은 위아래 그대로. **K22-2** 본문 글 높이 추정: 단어 단위 줄바꿈·문단 들여쓰기(marL·indent — 문단 → 도형 → 발표 기본 스타일)·줄 간격 %·pt·앞뒤 간격 |
| `test_toolkit.py` | 16.37 | 183개(+1): 단어 줄바꿈(긴 단어), 들여쓰기·줄 간격 읽기, 위아래 화면을 옆 배치로 안 고름(본문 폭 그대로), box-to-memo(메모 0 → 1줄, 상자 지움, 없는 글은 거부) |
| `literature.py` | 0.4 | 새 **`oa`**: DOI 마다 **Unpaywall·Europe PMC**(캡차 없는 공식 API, 초당 1 요청, `--email` — 공개 저장소에 적지 않음) 조회, `--fetch` 면 Europe PMC 전문 XML(JATS)을 받아 md(절 표지·표는 행 구조·수식은 [수식])로 보관소에. `locate` 0회 줄: 밑줄·하이픈·공백을 뺀 꼴로 다시 세어 "표기 차이로 0회일 수 있음"(첨자 거짓 양성). `check`·meta: 수식 글꼴 치환(`¼ þ ð Þ`) 알림 |
| `test_literature.py` | 0.4 | 8개(+1): oa(이메일 없으면 멈춤, OA XML 받아 md·표 행·음수 부호, 보관소에 있으면 다시 조회 안 함 — 네트워크 없이 가짜 응답으로), 0회 표기 차이, 수식 글꼴 수 |
| `LITERATURE.md` | 0.4 | 정본 = Drive `문헌 보관소`(PDF 포함 — 공용 PC 의 로컬 파일은 지운다, 사용자), 2b 단계 공식 API, 리뷰어는 `문헌 보관소` 만(동기화된 `문헌작업` 사본은 쓰지 않음), 0회·수식 글꼴 안내 |
| `DECK_SPEC.md` | 16.37 | 판 기록 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 발표 K22-1 옆 배치 판정 | deck 16.37 — 제안 그대로(세로 범위가 겹칠 때만 옆 배치) |
| K22-2 좁은 칸 글 높이 | deck 16.37 — 세 가지 모두(단어 줄바꿈·들여쓰기·줄 간격). 화면 27 실물 수치로는 재지 못했다 — 발표 dry-run 에서 본문 상자 높이 추정을 캡처와 비교 바람 |
| K21 글상자를 노트 메모로 | deck 16.37 `box-to-memo` — 제안 CLI 그대로 |
| 리뷰어 md 판정 채점 — 통과 | 기록(두 번째 조판 표본, 표 셀 순서는 여전히 1편) |
| 제안 1: 0회 거짓 양성(첨자) | literature 0.4 |
| 제안 2: 수식 글꼴 치환 표시 | literature 0.4 (check·meta) |
| 기록: PDF 도 `문헌 보관소` 에(사용자 결정) | LITERATURE 0.4 §0 5단계 — 규약을 사용자 결정에 맞춤 |
| 공식 API 경로 제안 | literature 0.4 `oa` — Unpaywall·Europe PMC(조회 + OA 전문 XML). 출판사 TDM 은 제외(제안 그대로). Cowork 클라우드 셸에서 두 API 에 닿는지는 첫 실행에서 |

## 3. 받을 파일

zip 두 개: `v2.41_GitHub.zip`(GitHub 에 전부), `v2.41_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v61 | `5b0b70612e5d` | ○ |
| `RELEASE.md` | v2.41 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.37 | `75507c4a9834` | ○ |
| `test_toolkit.py` | v16.37 | `4a9355ac210d` | ○ |
| `DECK_SPEC.md` | v16.37 | `d5b88da3990f` | ○ |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v61 | `5b0b70612e5d` | ○ |
| `RELEASE.md` | v2.41 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v61 | `5b0b70612e5d` | ○ |
| `RELEASE.md` | v2.41 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v61 | `5b0b70612e5d` | ○ |
| `RELEASE.md` | v2.41 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.4 | `1fe34738bcc8` | ○ |
| `test_literature.py` | v0.4 | `660b68142ab7` | ○ |
| `LITERATURE.md` | v0.4 | `42e9bcc9e1c6` | ○ |
| `TOOLS_MANIFEST.md` | v61 | `5b0b70612e5d` | ○ |
| `RELEASE.md` | v2.41 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.37 | `75507c4a9834` | ○ |
| `test_toolkit.py` | v16.37 | `4a9355ac210d` | ○ |
| `DECK_SPEC.md` | v16.37 | `d5b88da3990f` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `literature.py` | v0.4 | `1fe34738bcc8` | ○ |
| `test_literature.py` | v0.4 | `660b68142ab7` | ○ |
| `LITERATURE.md` | v0.4 | `42e9bcc9e1c6` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v61 | `5b0b70612e5d` | ○ |
| `CODE_PROJECT_README.md` | v5 | `fc373977d111` | — |
| `HISTORY.md` | — | `17673a1f20e2` | ○ |
| `release.py` | — | `4befd11f62f2` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.41 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: **대본 v2 에서 다시** → 대본 v7(발표 계획): v6 과 같은 단계 + ⑧ 에서 27 을 `auto`(고친 판정) · ⑨ 앞에 87·88 `box-to-memo --match "221122"` → `fit-layout --arrange side`. dry-run 에서 27 의 본문 높이 추정과 사용자 캡처 비교.
2. 리뷰어·문헌 Cowork: 검증지시 v2(5편)부터 `plan` → **`oa --email … --fetch`**(클라우드 셸에서 두 API 가 열리는지 먼저) → 남은 것만 브라우저·사용자.
3. 저자·교과서: 도구 변경 없음.

## 5. 검증하지 않은 것

- `oa` 는 가짜 응답으로만 시험했다 — 이 컨테이너에서 두 API 가 네트워크 허용 목록 밖이라 실제로 부르지 못했다. Cowork 클라우드 셸에서 첫 실행 때 닿는지·응답 모양이 맞는지 본다.
- K22-2 의 새 추정도 글꼴 파일이 없으면 0.5em 모델이다 — 줄바꿈 단위는 맞아졌지만 글자 폭은 여전히 추정.
