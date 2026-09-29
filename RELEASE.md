# RELEASE v2.63 — manifest v83 — 2026-09-29

> **v2.63** — 작은 판 둘. ① **`strip_color` 는 글자 색만**(코드 리뷰 ⑭): 붙여 쓴 한 모양(`<a:solidFill><a:srgbClr val="FF0000"/></a:solidFill>`)만 잡으면서 슬라이드 전체에서 지워, 문제 제시용 복제본에서 **빨간 화살표·동그라미 도형의 채움·선까지** 지웠다 — 이제 글자 속성만, 표기가 달라도. deck_toolkit 16.45. ② **Unpaywall 404 는 "조회 못 함" 이 아니다**(사용자 09-29 — Unpaywall 도움말): Crossref 에 없는 DOI 는 404, 다시 조회해도 같다 — `Unpaywall 에 없는 DOI — DOI 확인 필요`(결과 `baddoi`)로 따로. literature 0.8.4. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.45 | `Deck.strip_color(n, 색)`: `a:rPr`·`a:endParaRPr`·`a:defRPr` 바로 아래의 그 색 `solidFill` 만 지운다. 도형 `spPr` 채움·선, 글자 외곽선(`a:ln`) 안의 채움은 둔다. 대소문자·줄바꿈·들여쓰기·자식(`lumMod` 등)이 붙은 `srgbClr` 도 잡는다. 반환은 전처럼 지운 수(handoff 의 '앞에 복제' 보고 수도 이 수) |
| `DECK_SPEC.md` | 16.45 | 머리에 한 줄, §0-B-3 첫 제시 줄에 "도형은 그대로 — 정답 표시 도형은 `delete_shape`" |
| `literature.py` | 0.8.4 | `oa`: Unpaywall HTTP 404 → `Unpaywall 에 없는 DOI — DOI 확인 필요(오타 · 없는 논문 · Crossref 밖)`, 결과 `baddoi`, 표 아래 `**Unpaywall 에 없는 DOI N편**`(AI 제안 DOI 면 없는 논문일 수 있다). `조회 못 함 N편` 에 세지 않는다. Europe PMC 가 찾았으면 찾은 것 + `(Unpaywall 에 없는 DOI — Crossref 밖일 수 있음)`. 404 밖의 HTTP 오류(422·5xx)·네트워크 오류는 그대로 `조회 못 함`. 종료 코드 0 그대로 |
| `LITERATURE.md` | 0.8.4 | Unpaywall 에 없는 DOI 문단 — gaps 작업표의 "AI 제안" DOI 를 거르는 뜻 |
| 테스트 | — | test_toolkit 1(재현 — 옛 코드는 빨간 화살표의 채움·선을 지움: 소문자 · 줄바꿈+`lumMod` · 외곽선 옆 글자 색 · endParaRPr 는 지우고, 도형·외곽선·C00000 은 둠, 두 번째는 0), test_literature 1(재현 — 옛 0.8.3 은 404 를 `err`: 404+없음 · 404+Europe PMC 실패 · 404+Europe PMC 전문 · 422·500·503 은 조회 못 함) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 코드 리뷰 ⑭ strip_color 한 모양만·도형 빨강까지 | 위 deck 16.45 |
| 사용자 09-29: Unpaywall 404 는 조회 못 함이 아님, gaps AI 제안 DOI 거르기에도 | 위 literature 0.8.4 · LITERATURE.md 한 문단 |

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
| `TOOLS_MANIFEST.md` | v83 | `345c12748e11` | ○ |
| `RELEASE.md` | v2.63 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8 | `e0c1830c3763` | — |
| `test_claim_graph.py` | v16.8 | `3d88155641a6` | — |
| `CLAIM_GRAPH.md` | v16.8 | `d372fc42d6a6` | — |
| `deck_toolkit.py` | v16.45 | `eeb2305adca7` | ○ |
| `test_toolkit.py` | v16.45 | `d0123d0f9c21` | ○ |
| `DECK_SPEC.md` | v16.45 | `1c2910d1d90a` | ○ |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v83 | `345c12748e11` | ○ |
| `RELEASE.md` | v2.63 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8 | `e0c1830c3763` | — |
| `test_claim_graph.py` | v16.8 | `3d88155641a6` | — |
| `CLAIM_GRAPH.md` | v16.8 | `d372fc42d6a6` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v83 | `345c12748e11` | ○ |
| `RELEASE.md` | v2.63 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v83 | `345c12748e11` | ○ |
| `RELEASE.md` | v2.63 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.4 | `0585dbb787b0` | ○ |
| `test_literature.py` | v0.8.4 | `940eca6399e2` | ○ |
| `LITERATURE.md` | v0.8.4 | `e35c0d149938` | ○ |
| `TOOLS_MANIFEST.md` | v83 | `345c12748e11` | ○ |
| `RELEASE.md` | v2.63 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8 | `e0c1830c3763` | — |
| `test_claim_graph.py` | v16.8 | `3d88155641a6` | — |
| `CLAIM_GRAPH.md` | v16.8 | `d372fc42d6a6` | — |
| `deck_toolkit.py` | v16.45 | `eeb2305adca7` | ○ |
| `test_toolkit.py` | v16.45 | `d0123d0f9c21` | ○ |
| `DECK_SPEC.md` | v16.45 | `1c2910d1d90a` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.4 | `0585dbb787b0` | ○ |
| `test_literature.py` | v0.8.4 | `940eca6399e2` | ○ |
| `LITERATURE.md` | v0.8.4 | `e35c0d149938` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v83 | `345c12748e11` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `efd6d403fb44` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.63 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v83 이상.
2. 발표·발표 Cowork: '앞에 복제'(정답 미표시)에서 빨간 **화살표·동그라미 도형이 이제 남는다**. 정답을 가리키는 도형이면 넘김 문서의 뺄 상자(`delete_shape`)에 적는다.
3. 문헌 Cowork: `oa` 표의 `Unpaywall 에 없는 DOI` 는 다시 돌리지 말고 지시의 DOI 를 확인한다(AI 제안 DOI 면 없는 논문일 수 있다 — 리뷰어·저자에게 알린다).

## 5. 검증하지 않은 것

- 실제 시험 풀이 덱으로 `strip_color` 를 돌려 보지는 않았다(이 세션에 없다) — 가짜 슬라이드(원본 덱 7번에 빨간 글자 4모양·화살표)로만. 정답 빨강이 `srgbClr` 가 아닌 테마 색(`schemeClr`)이나 강조(`a:highlight`)로 칠해진 덱은 여전히 못 잡는다.
- Unpaywall 404 동작은 사용자가 부관리자 대화창에서 공식 도움말로 확인한 것을 따랐다 — 이 세션에서 실제 404 응답을 받아 보지는 못했다(예시 이메일은 422).
