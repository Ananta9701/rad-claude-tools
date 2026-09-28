# RELEASE v2.44 — manifest v64 — 2026-09-28

> **v2.44** — `textbook.py` 0.6. Cowork 도구회신(09-28, Jacobson 어깨 그림): `page --png` 가 전자책의 CMYK 그림 3장을 모두 저장하지 못했는데 종료 코드가 0 이었다(결함 2). 고쳤고, 전자책은 그림 조각만 나와 캡션·그림 번호가 빠지므로 쪽 전체를 그리는 `--render`, 크기 상한 `--max-px`, 이름 틀 `--name` 을 더했다(사용자 결정). 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `textbook.py` | 0.6 | `page --png`: CMYK 등 PNG 가 못 쓰는 모드는 RGB 로 바꿔 저장(색은 PDF 뷰어와 같게 — `/Decode` 있는 Adobe CMYK JPEG 확인). 하나도 저장하지 못하면 `[멈춤]`·종료 코드 0 아님. `--render [--dpi 150]` 쪽 전체 그림(pdftoppm — 없으면 멈춤), `--max-px N` 긴 변 상한, `--name '틀_p{printed:03d}'`(`{printed}`·`{pdf}`), 출력 첫 줄 `[쪽] 인쇄 N · PDF M` |
| `TEXTBOOK.md` | 0.6 | 쪽 그림 뽑기 절에 위 내용 |
| `test_textbook.py` | 0.6 | 시험 2개(CMYK PNG 저장·종료 코드, render·max-px·name) — 성공·실패 길 모두. pdftoppm 이 없는 곳에서는 render 성공 길만 빼고 돈다 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| Cowork 09-28 [결함] `page --png` CMYK 저장 실패(OSError) | 재현(고치기 전 코드에서 같은 OSError) → RGB 로 바꿔 저장 |
| Cowork 09-28 [결함] 파일 0개인데 rc=0 | 0 이 아닌 종료 코드와 `[멈춤] 저장한 그림이 없다` |
| Cowork 09-28 제안 `--render --dpi N` | 사용자 결정: 만든다 · pdftoppm 만(PyMuPDF 쓰지 않음) · `--max-px`·`--name` 도 |
| Cowork 09-28 제안 Adobe CMYK 색 확인 | 시험 PDF 3종을 MuPDF·pdftoppm 과 대조: `/Decode` 있는 것은 제 색, 없는 것은 뷰어도 뒤집어 그린다 — 도구가 따로 되돌리지 않는다 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | — |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | — |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v64 | `3cb69427beaa` | ○ |
| `RELEASE.md` | v2.44 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | — |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | — |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | — |
| `deck_toolkit.py` | v16.37 | `75507c4a9834` | — |
| `test_toolkit.py` | v16.37 | `4a9355ac210d` | — |
| `DECK_SPEC.md` | v16.37 | `d5b88da3990f` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v64 | `3cb69427beaa` | ○ |
| `RELEASE.md` | v2.44 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | — |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | — |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v64 | `3cb69427beaa` | ○ |
| `RELEASE.md` | v2.44 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.6 | `505e14289fd2` | ○ |
| `test_textbook.py` | v0.6 | `29298da49346` | ○ |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | ○ |
| `TOOLS_MANIFEST.md` | v64 | `3cb69427beaa` | ○ |
| `RELEASE.md` | v2.44 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.4 | `1fe34738bcc8` | — |
| `test_literature.py` | v0.4 | `660b68142ab7` | — |
| `LITERATURE.md` | v0.4 | `42e9bcc9e1c6` | — |
| `TOOLS_MANIFEST.md` | v64 | `3cb69427beaa` | ○ |
| `RELEASE.md` | v2.44 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | — |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | — |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | — |
| `deck_toolkit.py` | v16.37 | `75507c4a9834` | — |
| `test_toolkit.py` | v16.37 | `4a9355ac210d` | — |
| `DECK_SPEC.md` | v16.37 | `d5b88da3990f` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.6 | `505e14289fd2` | ○ |
| `test_textbook.py` | v0.6 | `29298da49346` | ○ |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | ○ |
| `literature.py` | v0.4 | `1fe34738bcc8` | — |
| `test_literature.py` | v0.4 | `660b68142ab7` | — |
| `LITERATURE.md` | v0.4 | `42e9bcc9e1c6` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v64 | `3cb69427beaa` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `ec52b914eefd` | ○ |
| `release.py` | — | `a5dad4e3e398` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.44 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 교과서(Cowork): selfcheck 로 manifest v64 이상·textbook 0.6 확인. 쪽 그림은 전자책이면 `--render` 로(TEXTBOOK.md 쪽 그림 뽑기 절). Jacobson 어깨 그림은 코드가 새 지시문을 준다(사용자가 붙여 넣음).
2. 다른 역할: 할 일 없음.

## 5. 검증하지 않은 것

- 실물 전자책(Jacobson)에서 `--render` 결과 — 시험 PDF 로만 확인. 첫 쪽(PDF 74)을 Cowork 가 열어 본다.
- Acrobat 에서 `/Decode` 없는 Adobe CMYK JPEG 가 어떻게 보이는지(MuPDF·pdftoppm 으로만 대조).
