# RELEASE v2.52 — manifest v72 — 2026-09-29

> **v2.52** — v2.51(같은 날)의 XML 변환을 **실제 Europe PMC XML 9편**으로 확인하다 찾은 것 세 가지를 고쳤다. ① 이웃 문단·제목이 띄어쓰기 없이 붙음(`noteSpringer`, `participateNot` — 옛 판부터), ② 수식 안 글(변수 이름)이 `[수식]` 으로 사라짐, ③ 초록 제목(`Key points`)이 빠짐. 9편 기준 낱말 24,595개 중 **v2.50 변환은 1,865개가 빠졌고(찾기로도 못 찾는 낱말 256종), v2.52 는 20개**(첨자가 붙은 것뿐 — 찾기에는 걸림). literature 0.8.1. v2.51 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `literature.py` | 0.8.1 | XML → md: 문단·제목·목록 항목·각주·표 칸 등 블록 사이에 띄어쓰기를 넣는다(전에는 `<p>A</p><p>B</p>` → `AB`) |
| `literature.py` | 0.8.1 | 수식은 `[수식: MathML 글]`(300자까지) — 수식 안 변수 이름도 찾기에 걸린다. TeX 판(`tex-math`)은 머리말이 섞여 쓰지 않는다 |
| `literature.py` | 0.8.1 | 초록 제목을 표지에(`[§ Abstract · Key points]`) |
| `literature.py` | 0.8.1 | 변환 판 표지 `변환 v0.8.1` — v0.8 로 만든 md 도 `oa` 재실행 때 paper.xml 에서 다시 만든다 |
| 테스트 | — | test_literature JATS 시험에 위 세 가지(이웃 문단 붙음·MathML/TeX 수식·초록 제목) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| v2.51 §5 "실제 Europe PMC XML 로는 시험하지 못했다" | 이 세션에서 Europe PMC 가 열려(09-29, 간헐 503) OA 9편(영상의학 학술지 2022·2026)으로 옛/새 변환을 비교했다 — 위 머리말 숫자 |
| 리뷰어 09-29 결함 3건 중 1 (합자) | v2.51 에서 고침 |
| 같은 회신 2 (`oa` 조회 실패 표시) | 작은 판 순서 안에서. 이번 시험에서도 Europe PMC 가 503 을 여러 번 냈다 — 지금 `oa` 는 이것을 "OA 없음 … [조회 오류 HTTPError]" 로 적는다 |
| 같은 회신 3 (허용 목록 / 규약 2b) | 사용자 결정 대기 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | — |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | — |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | — |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `TOOLS_MANIFEST.md` | v72 | `ea8eb308244d` | ○ |
| `RELEASE.md` | v2.52 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | — |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | — |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | — |
| `deck_toolkit.py` | v16.40 | `5ee58284d889` | — |
| `test_toolkit.py` | v16.40 | `040aea20b6de` | — |
| `DECK_SPEC.md` | v16.40 | `45d526ffac2a` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v72 | `ea8eb308244d` | ○ |
| `RELEASE.md` | v2.52 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | — |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | — |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v72 | `ea8eb308244d` | ○ |
| `RELEASE.md` | v2.52 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `TOOLS_MANIFEST.md` | v72 | `ea8eb308244d` | ○ |
| `RELEASE.md` | v2.52 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.1 | `a922c1e181e1` | ○ |
| `test_literature.py` | v0.8.1 | `132288e82edd` | ○ |
| `LITERATURE.md` | v0.8.1 | `ba42525acca9` | ○ |
| `TOOLS_MANIFEST.md` | v72 | `ea8eb308244d` | ○ |
| `RELEASE.md` | v2.52 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | — |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | — |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | — |
| `deck_toolkit.py` | v16.40 | `5ee58284d889` | — |
| `test_toolkit.py` | v16.40 | `040aea20b6de` | — |
| `DECK_SPEC.md` | v16.40 | `45d526ffac2a` | — |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `literature.py` | v0.8.1 | `a922c1e181e1` | ○ |
| `test_literature.py` | v0.8.1 | `132288e82edd` | ○ |
| `LITERATURE.md` | v0.8.1 | `ba42525acca9` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v72 | `ea8eb308244d` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `6cbc1b4b46bb` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.52 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v72 이상. 회신에 pypdf·Pillow 판 한 줄(`python3 -c "import pypdf, PIL; print(pypdf.__version__, PIL.__version__)"`).
2. 리뷰어·문헌: **`oa` 로 받은 문헌**(보관소 폴더에 `paper.xml` 이 있는 것)은 `oa` 를 한 번 다시 돌려 paper.md 를 다시 만든다(네트워크 없이, 결과 칸 "다시 변환"). 그 문헌으로 낸 "0회" 판정은 다시 본다.
3. 리뷰어: PDF 로 받은 문헌의 옛 `locate` 결과 중 0회였던 말은 v0.8 이상 `locate` 로 다시 확인한다(합자, v2.51).

## 5. 검증하지 않은 것

- 실제 XML 은 9편, 모두 한 출판사 계열 영상의학 학술지다. 상자 글(`boxed-text`)·부록(`app`)·본문 밖 표(`floats-group`)는 이 9편에 없어 fixture 로만 시험했다.
- `oa` 전체(Unpaywall 조회 포함)를 실제로 끝까지 돌리지는 않았다 — Unpaywall 은 이메일이 필요하고, 사용자 이메일을 시험에 쓰지 않았다. 변환(`jats_to_md`)만 실제 XML 로 확인.
- 합자 fixture 는 paper.md 에 글자를 넣은 것 — 합자가 든 실제 PDF 로는 돌리지 않았다(v2.51 과 같음).
