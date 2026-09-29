# RELEASE v2.51 — manifest v71 — 2026-09-29

> **v2.51** — 문헌 원문 찾기의 **거짓 "0회"** 두 가지(리뷰어 판정에서 가장 위험한 쪽). ① **합자**(리뷰어 09-29, 문헌 Cowork): PDF 글자층이 `fl`·`fi` 를 한 글자(`ﬂ`·`ﬁ`)로 담아 원문에 4번 나오는 말이 0회로 나왔다 — `locate` 가 찾기용 사본을 NFKC 로 만든다. ② **XML 변환에서 빠진 글**(코드 리뷰 ⑨): 목록·상자 글·부록·본문 밖 표·수식 뒤 글 등이 paper.md 에 들어가지 않았다. 함께: TEXTBOOK `--render` 문구 정정. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `literature.py` | 0.8 | `locate`: 찾을 말·원문을 **NFKC 사본**으로 찾는다(합자 `ﬂ ﬁ`, 위첨자 `²`, 전각). 0회 줄·후보 문단·찾을 말별 첫 자리 모두. 인용은 원문 글자 그대로(사본 자리 → 원문 자리 표). 제목 짝짓기(`_tokens`)도 같게 |
| `literature.py` | 0.8 | `oa` XML → md: 목록(중첩 포함)·상자 글 `[§ 상자 · …]`·부록 `[§ 부록 · …]`·감사의 글·각주·정의 목록·문단 안 표(행 그대로)·표 주·본문 밖 표·그림(`floats-group`)·절 밖 수식·구조 초록 `[§ Abstract · 절]`·절 앞 본문 `[§ 본문]` 을 넣는다. **수식 뒤 같은 문단의 글**이 사라지던 것(`clear()` 가 tail 까지 지움)도. 모르는 요소도 글이 있으면 남기고 **참고문헌 목록만 뺀다**. 상자·하위 절 뒤 문단은 원래 절 표지 아래로 돌아간다 |
| `literature.py` | 0.8 | 옛 XML 변환 md(v0.8 전)는 `locate` 가 "0회를 믿지 않는다" 로 알리고, `oa` 를 다시 돌리면 보관소의 `paper.xml` 에서 **네트워크 없이** 다시 만든다(결과 칸 "다시 변환") |
| `LITERATURE.md` | 0.8 | 위 세 가지 |
| `textbook.py`·`TEXTBOOK.md` | 0.7.1 | 문구만: "PyMuPDF 는 쓰지 않는다(사용자 09-28)" → "`--render` 는 pdftoppm 으로(09-28 — 설치 하나 덜고 AGPL 피함)". 사용자 결정은 `--render` 방식뿐이었다. 동작 변화 없음 |
| 테스트 | — | test_literature 3: JATS 블록(재현 — 옛 코드에서 17개 낱말 중 11개 빠짐·본문 밖 표 없음·문단 안 표 `eta0.63theta12` 로 뭉개짐, 참고문헌 목록은 안 넣음), 합자(재현 — 옛 코드 0회, 없는 말은 여전히 0회, paper.md 그대로), 옛 변환 다시 만들기(알림 → 다시 변환 → 다시 안 함, PDF 문헌은 대상 아님) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 리뷰어 09-29 (문헌 Cowork 결함 3건) 1. 합자 거짓 0회 | 위 literature 0.8 — 재현 뒤 고침 |
| 같은 회신 2. `oa` 조회 실패가 "OA 없음" 칸에 섞임 | **다음 작은 판들 안에서**(oa 실패 길 시험 ⑰ 과 함께). 그전까지: 행 끝에 `[조회 오류 …]` 가 붙으면 "OA 없음" 이 아니라 "조회 못 함" 으로 읽는다 |
| 같은 회신 3. 클라우드에서 Unpaywall·Europe PMC 막힘 / 규약 2b | 사용자 결정 대기 |
| 코드 리뷰 ⑨ JATS 목록·상자 글·부록·문단 안 표 | 위 literature 0.8 |
| HISTORY "문구 정정" | 위 textbook 0.7.1 |

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
| `TOOLS_MANIFEST.md` | v71 | `74ba9347eb6d` | ○ |
| `RELEASE.md` | v2.51 | — | 이 문서 |

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
| `TOOLS_MANIFEST.md` | v71 | `74ba9347eb6d` | ○ |
| `RELEASE.md` | v2.51 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | — |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | — |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v71 | `74ba9347eb6d` | ○ |
| `RELEASE.md` | v2.51 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.1 | `20d10c9948a9` | ○ |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | ○ |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | ○ |
| `TOOLS_MANIFEST.md` | v71 | `74ba9347eb6d` | ○ |
| `RELEASE.md` | v2.51 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8 | `14036e478f5a` | ○ |
| `test_literature.py` | v0.8 | `6d51cce463db` | ○ |
| `LITERATURE.md` | v0.8 | `ac87fc6cdb59` | ○ |
| `TOOLS_MANIFEST.md` | v71 | `74ba9347eb6d` | ○ |
| `RELEASE.md` | v2.51 | — | 이 문서 |

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
| `textbook.py` | v0.7.1 | `20d10c9948a9` | ○ |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | ○ |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | ○ |
| `literature.py` | v0.8 | `14036e478f5a` | ○ |
| `test_literature.py` | v0.8 | `6d51cce463db` | ○ |
| `LITERATURE.md` | v0.8 | `ac87fc6cdb59` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v71 | `74ba9347eb6d` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `8cea65963c7b` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.51 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v71 이상 확인. selfcheck 회신에 pypdf·Pillow 판 한 줄(`python3 -c "import pypdf, PIL; print(pypdf.__version__, PIL.__version__)"`) — v2.50 에서 부탁했으나 09-29 회신 3건에는 없었다.
2. 리뷰어·문헌: **v0.8 전에 `oa` 로 받은 문헌**(보관소 폴더에 `paper.xml` 이 있는 것)은 `oa` 를 한 번 다시 돌려 paper.md 를 다시 만든다(네트워크 없이). 그 문헌으로 낸 "0회" 판정은 다시 본다.
3. 리뷰어: PDF 로 받은 문헌의 옛 `locate` 결과 중 **0회였던 말**은 v0.8 로 `locate` 를 다시 돌려 확인한다(합자). paper.md 는 다시 만들 필요 없다.

## 5. 검증하지 않은 것

- 실제 Europe PMC XML 로는 시험하지 못했다 — 이 클라우드 환경은 `www.ebi.ac.uk` 가 막혀 있다(09-28). fixture 는 JATS 규격의 요소 이름으로 손으로 만든 것. 출판사마다 쓰는 요소가 다를 수 있다 — 모르는 요소는 글을 남기는 쪽으로 만들었다.
- 합자 fixture 는 paper.md 에 글자를 직접 넣은 것이다. 합자가 든 실제 PDF(리뷰어가 말한 문헌, 124줄)로는 돌려 보지 않았다(원문은 이 세션에 없음).
- NFKC 는 `R²`→`R2`, `µ`→`μ`, `½`→`1⁄2` 도 바꾼다 — 찾기가 넓어지는 쪽이라 거짓 "0회" 는 줄지만, 드물게 다른 뜻의 표기가 "있음" 으로 잡힐 수 있다(판정은 리뷰어가 문단을 읽고 한다).
