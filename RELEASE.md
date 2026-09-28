# RELEASE v2.40 — manifest v60 — 2026-09-28

> **v2.40** — 발표 `260928_도구회신_K20fitlayout_회귀_v1`(v2.39 의 `fit-layout` 회귀 — 인터벤션 v6 3차 실행이 멈춤)과 리뷰어 `260928_도구회신_Cowork_md판정가능_시험_리뷰어_v1`(기본 경로를 md 로). `deck_toolkit.py` 16.36·`literature.py` 0.3. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.36 | **K20 회귀 수정**: 16.35 가 K19-1 을 넣으며 제자리 배치 **성공** 길의 `plan = best[1]` 을 빠뜨렸다(`TypeError: 'NoneType' object is not subscriptable` — 제목을 남기고 제자리 배치가 성공하는 화면만, 인터벤션 26). 발표가 코드를 읽어 찾은 원인 그대로 |
| `test_toolkit.py` | 16.36 | 182개(+1): 제목을 남긴 채 제자리 배치가 성공하고 본문 상자 높이가 줄어드는 화면 — **고치기 전 코드에서 같은 TypeError 를 먼저 재현**. 지금까지 시험이 옆 배치 성공·실패만 덮었다(발표 지적) |
| `literature.py` | 0.3 | `check`: 쪽의 절반 이상이 글자층 없으면 "스캔 — **PDF 필요**"(✗), `--store` 를 주면 보관소 paper.md 의 **쪽 표지 수 = PDF 쪽 수** 대조(다르면 ✗ md 가 잘렸다). `meta.md` 에 "원 PDF: sha256 · 쪽 수 · 글자층 없는 쪽 · paper.md 쪽 표지" 줄 |
| `test_literature.py` | 0.3 | 7개(+1): meta 원 PDF 줄, 쪽 표지 대조(잘린 md → ✗), 스캔 → PDF 필요 |
| `LITERATURE.md` | 0.3 | **기본 경로 = md 로 판정**: Cowork 가 md 만 Drive 로, PDF 는 병원 컴퓨터에 남기고 리뷰어가 요청한 문헌만 사용자가 inbox 로(경로 (b) 는 예외). 조건(meta·check·회신에 입수 경로) |
| `DECK_SPEC.md` | 16.36 | 판 기록 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 발표 K20 ① `else: plan = best[1]` | deck 16.36 |
| ② 제자리 배치 성공 시험 | test_toolkit 16.36 — 옛 코드에서 재현 확인 뒤 고침 |
| ③ Python 3.10 | 빌드가 3.10 으로도 모든 테스트(통과 수 같음) — 이번 회귀는 판과 무관한 코드 결함이었고, 두 판 모두 시험이 그 길을 덮지 않았다 |
| 리뷰어 md 판정 시험 — 기본 경로를 md 로 | LITERATURE 0.3 §0 — 제안 그대로. 코드가 전에 정한 "경로 (b) 기본" 을 바꾼다(리뷰어 채점: paper.md 가 단 순서·표 셀 순서에서 PDF 직접 읽기보다 낫다) |
| 조건 — meta 에 sha·쪽 수·DOI·글자층, 쪽 표지 수 = 쪽 수, 스캔은 PDF 필요 | literature 0.3 `check --store`·meta 줄 |
| 확인하지 않은 것 — 다른 조판 | 다음 시험의 Wiley 1편으로 두 번째 표본(리뷰어 제안 그대로) |

## 3. 받을 파일

zip 두 개: `v2.40_GitHub.zip`(GitHub 에 전부), `v2.40_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v60 | `008059e99c91` | ○ |
| `RELEASE.md` | v2.40 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.36 | `0b59b9883775` | ○ |
| `test_toolkit.py` | v16.36 | `9fbcde56fadb` | ○ |
| `DECK_SPEC.md` | v16.36 | `a117c3a7b204` | ○ |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v60 | `008059e99c91` | ○ |
| `RELEASE.md` | v2.40 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v60 | `008059e99c91` | ○ |
| `RELEASE.md` | v2.40 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v60 | `008059e99c91` | ○ |
| `RELEASE.md` | v2.40 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.3 | `de5ba7a84150` | ○ |
| `test_literature.py` | v0.3 | `0739d23289b8` | ○ |
| `LITERATURE.md` | v0.3 | `e72fffc006c6` | ○ |
| `TOOLS_MANIFEST.md` | v60 | `008059e99c91` | ○ |
| `RELEASE.md` | v2.40 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.36 | `0b59b9883775` | ○ |
| `test_toolkit.py` | v16.36 | `9fbcde56fadb` | ○ |
| `DECK_SPEC.md` | v16.36 | `a117c3a7b204` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `literature.py` | v0.3 | `de5ba7a84150` | ○ |
| `test_literature.py` | v0.3 | `0739d23289b8` | ○ |
| `LITERATURE.md` | v0.3 | `e72fffc006c6` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v60 | `008059e99c91` | ○ |
| `CODE_PROJECT_README.md` | v5 | `fc373977d111` | — |
| `HISTORY.md` | — | `8da714f24e82` | ○ |
| `release.py` | — | `4befd11f62f2` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.40 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: v6 지시 v2 의 판 요구만 v2.40 으로 올려 그대로 다시(발표 계획대로).
2. 리뷰어·문헌 Cowork: 시험 검증지시 v1 — Cowork 에 check → ingest → **check --store** → locate → **md 만 Drive 로**. 리뷰어는 paper.md 로 판정하고, Wiley 1편은 inbox 의 PDF 와 나란히 채점(두 번째 조판 표본).
3. 저자·교과서: 도구 변경 없음.

## 5. 검증하지 않은 것

- 인터벤션 실물 화면 26 은 다시 돌리지 않았다(fixture 로 같은 길을 재현·확인).
- md 로 판정하는 기본 경로는 조판 1종(Frontiers)에서만 채점됐다.
