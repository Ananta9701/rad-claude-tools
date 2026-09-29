# RELEASE v2.66 — manifest v86 — 2026-09-29

> **v2.66** — 빨간 도형 검사와 `빨간 도형도 뺌`(사용자 09-29 — 14번 뒤, 형식 (나) 선택). v2.63 부터 `strip_color` 가 글자 색만 지워 문제 화면(앞에 복제)에 정답을 가리키는 빨간 화살표·동그라미가 남을 수 있다 — 이제 **남으면 적용 보고에 [확인]**, 넘김 설명에 **`빨간 도형도 뺌`** 이면 복제본에서 뺀다. deck_toolkit 16.46 · handoff 2.2. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.46 | `Deck.red_shapes(n, 색='FF0000')` — 도형 속성(`p:spPr`)의 채움·선이 그 색인 도형(sp·cxnSp·pic) 이름 목록, 글자 색은 보지 않는다. `Deck.strip_red_shapes(n, 색)` — 그 도형을 모두 지우고 쓰던 rels 도 뺀다(이름이 겹쳐도 — `delete_shape` 는 한 이름에 하나만). rels 정리는 `delete_shape` 와 같은 함수(`_drop_rels`)로 |
| `DECK_SPEC.md` | 16.46 | 머리에 한 줄, §0-B-3 첫 제시 줄 |
| `handoff.py` | 2.2 | `앞에 복제` 설명에 `빨간 도형도 뺌` → 복제본에서 빨간 도형 모두 뺌(원본 화면 그대로, 새 슬라이드·가져옴의 앞에 복제도). 안 적었는데 남으면 보고 표 `빨간 도형(복제본)` 에 `[확인] 화면 N 복제본(slideM)에 빨간 도형 k개 남음: 이름… — 정답 표시면 넘김에 "빨간 도형도 뺌"`. 앞에 복제 없이 쓰면 경고 |
| `HANDOFF_FORMAT.md` | 2.2 | `앞에 복제` 줄에 `빨간 도형도 뺌` · 해설 상자는 글로 찾는다는 것 |
| 테스트 | — | test_toolkit 1(찾기: 도형 채움·선·connector 선·소문자는 잡고 글자 빨강·파란 상자는 아님, 이름 겹친 둘 모두 빼기, 두 번째 0), test_handoff 1(적은 화면은 복제본만 빼고 원본 그대로 · 안 적은 화면은 [확인] 에 이름 · 앞에 복제 없이 쓰면 경고) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-29: 문제 화면에 남은 빨간 도형 검사 | 위 [확인] |
| 사용자 09-29: 넘김에서 정답 도형 빼기 — (나) `빨간 도형도 뺌` | 위 handoff 2.2 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.9 | `c57862ed2485` | — |
| `test_claim_graph.py` | v16.9 | `4cee6ef82a26` | — |
| `CLAIM_GRAPH.md` | v16.9 | `af7dde0cafca` | — |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v86 | `97e5e0b864ac` | ○ |
| `RELEASE.md` | v2.66 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.9 | `c57862ed2485` | — |
| `test_claim_graph.py` | v16.9 | `4cee6ef82a26` | — |
| `CLAIM_GRAPH.md` | v16.9 | `af7dde0cafca` | — |
| `deck_toolkit.py` | v16.46 | `8277344bf38c` | ○ |
| `test_toolkit.py` | v16.46 | `3dd49a2f30da` | ○ |
| `DECK_SPEC.md` | v16.46 | `2647cfab6cfc` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | ○ |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | ○ |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | ○ |
| `TOOLS_MANIFEST.md` | v86 | `97e5e0b864ac` | ○ |
| `RELEASE.md` | v2.66 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.9 | `c57862ed2485` | — |
| `test_claim_graph.py` | v16.9 | `4cee6ef82a26` | — |
| `CLAIM_GRAPH.md` | v16.9 | `af7dde0cafca` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v86 | `97e5e0b864ac` | ○ |
| `RELEASE.md` | v2.66 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v86 | `97e5e0b864ac` | ○ |
| `RELEASE.md` | v2.66 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.4 | `0585dbb787b0` | — |
| `test_literature.py` | v0.8.4 | `940eca6399e2` | — |
| `LITERATURE.md` | v0.8.4 | `e35c0d149938` | — |
| `TOOLS_MANIFEST.md` | v86 | `97e5e0b864ac` | ○ |
| `RELEASE.md` | v2.66 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.9 | `c57862ed2485` | — |
| `test_claim_graph.py` | v16.9 | `4cee6ef82a26` | — |
| `CLAIM_GRAPH.md` | v16.9 | `af7dde0cafca` | — |
| `deck_toolkit.py` | v16.46 | `8277344bf38c` | ○ |
| `test_toolkit.py` | v16.46 | `3dd49a2f30da` | ○ |
| `DECK_SPEC.md` | v16.46 | `2647cfab6cfc` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | ○ |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | ○ |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | ○ |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.4 | `0585dbb787b0` | — |
| `test_literature.py` | v0.8.4 | `940eca6399e2` | — |
| `LITERATURE.md` | v0.8.4 | `e35c0d149938` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v86 | `97e5e0b864ac` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `4bd91ccf7da7` | ○ |
| `release.py` | — | `0a430411a738` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.66 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v86 이상.
2. 영상의학: 정답을 가리키는 빨간 화살표·동그라미가 있는 `앞에 복제` 화면은 설명에 **`빨간 도형도 뺌`** 을 적는다(예: `앞에 복제(정답 표시 제거) — 해설 상자 없음 · 빨간 도형도 뺌`). 문제가 화살표를 묻는 화면에는 적지 않는다. 09-29 통보의 임시 메모(`정답 도형 있음 — …`)는 이제 필요 없다.
3. 발표·발표 Cowork: 적용 보고의 `빨간 도형(복제본)` 줄에 `[확인]` 이 있으면 그 도형이 정답 표시인지 보고, 그렇다면 영상의학에 알리거나 `Deck.strip_red_shapes(n)` 으로 뺀다.

## 5. 검증하지 않은 것

- 실제 풀이 덱으로는 돌리지 않았다 — 가짜 슬라이드로만. 빨강을 FF0000 이 아닌 색(예: C00000)·테마 색으로 칠한 도형은 잡지 않는다.
- 그룹 안의 빨간 도형은 그 도형만 빼고 그룹은 남긴다(그룹 틀 크기는 그대로) — 실물에서 보기 확인 안 함.
