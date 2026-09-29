# RELEASE v2.62 — manifest v82 — 2026-09-29

> **v2.62** — 작은 판 17(코드 리뷰 ⑰ + 리뷰어 09-29 2번). ① **`oa` 조회 실패를 "OA 없음" 과 나눔**: 네트워크·차단·이메일 오류가 `OA 없음 … [조회 오류 URLError]` 로 섞여 "다시 조회" 와 "브라우저·사용자" 가 구별되지 않았다 — 이제 `조회 못 함 — 다시 조회(…)`, 결과 `err`. literature 0.8.3. ② **split 실패 길**: 하위 프로세스가 실패한 책을 '이번 실행' 에 세고 맨 위 INDEX 에 `(남음)` 으로 적었다(예산 때문에 남은 책과 같게) — 이제 `(실패 — 까닭)`, 실패가 있으면 rc=1. textbook 0.7.2. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `literature.py` | 0.8.3 | `oa`: 조회 실패(예외 — URLError·HTTPError·JSON 아님)를 `Unpaywall`·`Europe PMC` 별로 모아, 아무것도 못 찾았는데 실패가 있으면 `조회 못 함 — 다시 조회(Unpaywall URLError · Europe PMC HTTPError 503)`, 결과 `err`. 한쪽이 찾았으면 찾은 것 + `(Unpaywall 조회 못 함 … — OA PDF 는 모름)`. `OA 없음` 은 두 곳 모두 답했을 때만. HTTP 오류는 상태 번호까지(422 = 이메일 거부). 표 아래 `**조회 못 함 N편**` 한 줄. 종료 코드는 그대로 0 |
| `LITERATURE.md` | 0.8.3 | `oa` 조회 못 함 한 문단 |
| `textbook.py` | 0.7.2 | `split`: 하위 프로세스 실패 책은 `(실패 — rc=1 ValueError: 장 표가 비었다 …. 고친 뒤 같은 명령)`, 끝 줄 `이번 실행 N권 · 실패 M권 · 남은 책 K권`, 실패가 있으면 rc=1(남은 책만 있으면 0). 실패 뒤 다음 책은 예산을 따진다 |
| `TEXTBOOK.md` | 0.7.2 | split 실패 한 줄 |
| 테스트 | — | test_literature 1(재현 — 옛 코드는 둘 다 막혀도 `none`: 둘 다 실패 · Unpaywall 422 + Europe PMC 없음 · Unpaywall 실패 + Europe PMC 전문 · 둘 다 답하고 없음(성공 길) · 200 인데 HTML), test_textbook 2(재현 — 옛 코드는 실패 책을 `done=1`·`(남음)`: 장 표 빔 → 실패·rc=1 → 고친 뒤 같은 명령 성공 · plan 오류는 `(장 표 없음)` · 예산 넘김은 `(남음)`) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 리뷰어 09-29 2번(`oa` 네트워크 실패가 "OA 없음" 칸에) | 위 literature 0.8.3 — 제안 중 "실패 행을 조회 못 함으로" 를 택함(칸을 늘리지 않음) |
| 코드 리뷰 ⑰ split·oa 실패 길 시험 | 위 두 테스트. split 에서 실패 책이 '이번 실행' 에 세어지는 결함을 시험으로 찾아 고침 |
| 리뷰어 09-29 3번(클라우드에서 unpaywall·ebi 막힘 / 규약 2b) | 이번 판 아님 — 문헌 1분 시험 회신을 기다린다 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8 | `e0c1830c3763` | — |
| `test_claim_graph.py` | v16.8 | `3d88155641a6` | — |
| `CLAIM_GRAPH.md` | v16.8 | `d372fc42d6a6` | — |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v82 | `8053d71bba30` | ○ |
| `RELEASE.md` | v2.62 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8 | `e0c1830c3763` | — |
| `test_claim_graph.py` | v16.8 | `3d88155641a6` | — |
| `CLAIM_GRAPH.md` | v16.8 | `d372fc42d6a6` | — |
| `deck_toolkit.py` | v16.44 | `044f3040c83f` | — |
| `test_toolkit.py` | v16.44 | `d2d3c75d1156` | — |
| `DECK_SPEC.md` | v16.44 | `13ca36446345` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v82 | `8053d71bba30` | ○ |
| `RELEASE.md` | v2.62 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8 | `e0c1830c3763` | — |
| `test_claim_graph.py` | v16.8 | `3d88155641a6` | — |
| `CLAIM_GRAPH.md` | v16.8 | `d372fc42d6a6` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v82 | `8053d71bba30` | ○ |
| `RELEASE.md` | v2.62 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | ○ |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | ○ |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | ○ |
| `TOOLS_MANIFEST.md` | v82 | `8053d71bba30` | ○ |
| `RELEASE.md` | v2.62 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.3 | `5a14ca0f8bc8` | ○ |
| `test_literature.py` | v0.8.3 | `18788f693b7e` | ○ |
| `LITERATURE.md` | v0.8.3 | `fe3ef46e0731` | ○ |
| `TOOLS_MANIFEST.md` | v82 | `8053d71bba30` | ○ |
| `RELEASE.md` | v2.62 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8 | `e0c1830c3763` | — |
| `test_claim_graph.py` | v16.8 | `3d88155641a6` | — |
| `CLAIM_GRAPH.md` | v16.8 | `d372fc42d6a6` | — |
| `deck_toolkit.py` | v16.44 | `044f3040c83f` | — |
| `test_toolkit.py` | v16.44 | `d2d3c75d1156` | — |
| `DECK_SPEC.md` | v16.44 | `13ca36446345` | — |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | ○ |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | ○ |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | ○ |
| `literature.py` | v0.8.3 | `5a14ca0f8bc8` | ○ |
| `test_literature.py` | v0.8.3 | `18788f693b7e` | ○ |
| `LITERATURE.md` | v0.8.3 | `fe3ef46e0731` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v82 | `8053d71bba30` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `b1765d2a6c86` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.62 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v82 이상.
2. 문헌 Cowork: `oa` 표에 `조회 못 함` 이 있으면 같은 명령을 다시 돌린다(받은 것은 건너뜀). 계속 막히면 브라우저(규약 2b). `OA 없음` 이면 전처럼 브라우저·사용자.
3. 교과서 Cowork: `split` 끝 줄이 `실패 N권` 이면 맨 위 INDEX 의 `(실패 — …)` 까닭을 보고 코드에 알린다(rc=1).

## 5. 검증하지 않은 것

- 실제 Unpaywall 이 **없는 DOI 에 주는 답**(404 로 추정)은 확인하지 못했다 — 이 세션에서 예시 이메일은 422 로 거부됐다. 404 도 지금은 `조회 못 함 … HTTPError 404` 로 나온다(없음과 섞지 않는 쪽).
- 실제 교과서 PDF 로 split 실패를 내 보지는 않았다 — 가짜 책(장 표를 지움)으로만.
