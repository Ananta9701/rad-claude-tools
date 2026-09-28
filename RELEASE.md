# RELEASE v2.46 — manifest v66 — 2026-09-28

> **v2.46** — `verify_toolkit.py` 1.3.5. 코드 리뷰(09-28)에서 찾은 결함: 추적 변경 받기·되돌리기(`accept_or_reject_changes`)가 Word 의 **문단 표지 변경 표지**(스스로 닫는 `<w:ins …/>`·`<w:del …/>`)를 여는 태그로 잘못 잡아 다음 변경 끝까지 한 덩어리로 처리했다 — **결과 docx 가 깨져 열리지 않거나 남길 문단이 지워졌다.** 저자에게는 09-28 경고 통보(고칠 때까지 쓰지 말 것)를 보냈다. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `verify_toolkit.py` | 1.3.5 | 추적 변경: 여는 태그만 변경 덩어리로 잡는다. 문단 표지 변경 표지는 따로 세고(`scan_track_changes` 의 `marks`), 받을 때는 표지만 뺀다(문단·글은 남음). 결과 document.xml 이 온전한 XML 이 아니면 **파일을 쓰지 않고 멈춘다** |
| `test_verify_toolkit.py` | 1.3.5 | 시험 2개(성공: 문단 표지 변경 + 한글 문단 + 보통 삽입·삭제가 섞인 문서가 온전히 열리고 남길 글이 다 남음 · 실패: 깨진 XML 이면 멈추고 결과 파일을 남기지 않음) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 코드 리뷰 09-28 [결함] 추적 변경 정리가 docx 를 깨뜨림 | 재현(고치기 전 코드: 결과 XML "mismatched tag", python-docx 로 열리지 않음) → 고침 |
| 사용자 09-28: 판을 나눠 고친다, 고치기 전 to저자 경고 | 경고 통보 `to저자/260928_통보_코드to저자_추적변경결함경고_v1` — 이 판으로 풀린다 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | — |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | — |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | — |
| `verify_toolkit.py` | v1.3.5 | `e689f1f0f78c` | ○ |
| `test_verify_toolkit.py` | v1.3.5 | `fba712a29dcc` | ○ |
| `TOOLS_MANIFEST.md` | v66 | `cab2c0699524` | ○ |
| `RELEASE.md` | v2.46 | — | 이 문서 |

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
| `TOOLS_MANIFEST.md` | v66 | `cab2c0699524` | ○ |
| `RELEASE.md` | v2.46 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | — |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | — |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v66 | `cab2c0699524` | ○ |
| `RELEASE.md` | v2.46 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.6 | `505e14289fd2` | — |
| `test_textbook.py` | v0.6 | `29298da49346` | — |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | — |
| `TOOLS_MANIFEST.md` | v66 | `cab2c0699524` | ○ |
| `RELEASE.md` | v2.46 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.5 | `9a4167578ad4` | — |
| `test_literature.py` | v0.5 | `30c01cdb3ac1` | — |
| `LITERATURE.md` | v0.5 | `ce1ea0cade3d` | — |
| `TOOLS_MANIFEST.md` | v66 | `cab2c0699524` | ○ |
| `RELEASE.md` | v2.46 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | — |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | — |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | — |
| `deck_toolkit.py` | v16.37 | `75507c4a9834` | — |
| `test_toolkit.py` | v16.37 | `4a9355ac210d` | — |
| `DECK_SPEC.md` | v16.37 | `d5b88da3990f` | — |
| `verify_toolkit.py` | v1.3.5 | `e689f1f0f78c` | ○ |
| `test_verify_toolkit.py` | v1.3.5 | `fba712a29dcc` | ○ |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.6 | `505e14289fd2` | — |
| `test_textbook.py` | v0.6 | `29298da49346` | — |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | — |
| `literature.py` | v0.5 | `9a4167578ad4` | — |
| `test_literature.py` | v0.5 | `30c01cdb3ac1` | — |
| `LITERATURE.md` | v0.5 | `ce1ea0cade3d` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v66 | `cab2c0699524` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `02b830a650b5` | ○ |
| `release.py` | — | `065a41604f55` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.46 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 저자: selfcheck 로 manifest v66 이상·verify_toolkit 1.3.5 확인. 그 뒤 추적 변경 받기·되돌리기를 다시 써도 된다. **09-28 경고 전에 이 기능으로 만든 docx 가 있으면** Word 로 열어 원본과 대조한다.
2. 다른 역할: 할 일 없음.

## 5. 검증하지 않은 것

- 실제 저자 원고 docx(여러 작성자, 표 안 변경, 이동 `<w:moveFrom>`·`<w:moveTo>`)로는 시험하지 않았다 — 이동 표지는 이번 판도 다루지 않는다.
- 문단 표지 삭제(`<w:del/>` in rPr)를 받을 때 Word 는 두 문단을 합치지만, 이 도구는 표지만 빼고 문단을 나눈 채 둔다(글은 잃지 않음).
