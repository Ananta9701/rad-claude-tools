# RELEASE v2.61 — manifest v81 — 2026-09-29

> **v2.61** — 작은 판 둘. ① **화면 번호 범위 밖**(코드 리뷰 ⑬): `--screens` 가 덱 밖 번호를 조용히 버렸고, `bake-autofit`·`titles` 는 `--screens 0` 이 **마지막 화면**을 고쳤다 — 이제 멈춘다. deck_toolkit 16.44. ② **증례 묶음 순서·가로지름**(사용자 09-29, 증례 claims v3 렌더): 묶음이 case3 → case1 로 거꾸로 놓이고 결론 선이 다른 묶음을 가로질렀다 — 묶음을 처음 나온 순서대로 놓는다. claim_graph 16.8. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.44 | `_parse_screens` 가 1..화면 수 밖이거나 숫자가 아닌 번호에서 `[멈춤] 화면 번호 … 는 이 덱에 없다 — 1-N 안에서` 로 멈춘다. `bake-autofit`·`titles` 도 같은 풀이를 쓴다(따로 풀던 것 — 0 → order[-1]) |
| `DECK_SPEC.md` | 16.44 | 머리에 한 줄 |
| `claim_graph.py` | 16.8 | `mapdraw` 전체 그림: 묶음이 둘 이상이면 묶음 안 `direction LR` + 보이지 않는 연결 `g1 ~~~ g2 ~~~ …`(처음 나온 순서). 묶음 하나면 넣지 않음 |
| `CLAIM_GRAPH.md` | 16.8 | §3-2-1 묶음 순서와 **한계** 한 줄(공통 상자의 점선은 묶음 사이를 지날 수 있다 — 공통 상자를 group 에 넣거나 `--impact`) |
| 테스트 | — | test_toolkit 1(재현 — 옛 코드는 `0` 을 멈추지 않음: 범위 안 · 0 · N+1 · 넘는 범위 · 숫자 아님 · bake-autofit 0 은 파일을 안 씀 · fit-layout 범위 밖), test_claim_graph(묶음 순서 연결 · 파일 순서 · 묶음 하나면 없음) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 코드 리뷰 ⑬ | 위 deck 16.44 |
| 사용자 09-29: 묶음이 거꾸로 · 결론 선이 다른 묶음을 가로지름 | 가짜 증례 3개(묶음 밖 공통 상자 2 — 감별축·전체 결론)를 mermaid 11 로 렌더해 재 봄: 선언 순서만 바꿔서는 안 바뀜, 위→아래 배치(TB)는 가로지름 그대로, **보이지 않는 연결 + 묶음 안 LR** 이 순서 처음 나온 대로 · 다른 묶음을 지나는 선 2 → 0(1314×1174 px). 이것을 넣음. 남는 것은 공통 상자의 가는 점선 — CLAIM_GRAPH 에 한계로 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8 | `e0c1830c3763` | ○ |
| `test_claim_graph.py` | v16.8 | `3d88155641a6` | ○ |
| `CLAIM_GRAPH.md` | v16.8 | `d372fc42d6a6` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v81 | `4cc4155f68d4` | ○ |
| `RELEASE.md` | v2.61 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8 | `e0c1830c3763` | ○ |
| `test_claim_graph.py` | v16.8 | `3d88155641a6` | ○ |
| `CLAIM_GRAPH.md` | v16.8 | `d372fc42d6a6` | ○ |
| `deck_toolkit.py` | v16.44 | `044f3040c83f` | ○ |
| `test_toolkit.py` | v16.44 | `d2d3c75d1156` | ○ |
| `DECK_SPEC.md` | v16.44 | `13ca36446345` | ○ |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v81 | `4cc4155f68d4` | ○ |
| `RELEASE.md` | v2.61 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8 | `e0c1830c3763` | ○ |
| `test_claim_graph.py` | v16.8 | `3d88155641a6` | ○ |
| `CLAIM_GRAPH.md` | v16.8 | `d372fc42d6a6` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v81 | `4cc4155f68d4` | ○ |
| `RELEASE.md` | v2.61 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `TOOLS_MANIFEST.md` | v81 | `4cc4155f68d4` | ○ |
| `RELEASE.md` | v2.61 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | — |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | — |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | — |
| `TOOLS_MANIFEST.md` | v81 | `4cc4155f68d4` | ○ |
| `RELEASE.md` | v2.61 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.8 | `e0c1830c3763` | ○ |
| `test_claim_graph.py` | v16.8 | `3d88155641a6` | ○ |
| `CLAIM_GRAPH.md` | v16.8 | `d372fc42d6a6` | ○ |
| `deck_toolkit.py` | v16.44 | `044f3040c83f` | ○ |
| `test_toolkit.py` | v16.44 | `d2d3c75d1156` | ○ |
| `DECK_SPEC.md` | v16.44 | `13ca36446345` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | — |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | — |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v81 | `4cc4155f68d4` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `7d99ddc5cc59` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.61 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v81 이상.
2. 발표·발표 Cowork: `--screens` 에 덱 밖 번호를 주면 이제 멈춘다(전에는 조용히 건너뛰거나 0 이 마지막 화면).
3. 발표: 증례 관계도를 다시 그리면 묶음이 처음 나온 순서(claims 파일 순서)대로 놓인다 — 순서를 바꾸려면 파일에서 주장 순서를 바꾼다.

## 5. 검증하지 않은 것

- 발표의 실제 증례 claims v3 로는 재지 않았다(이 세션에 없다) — 가짜 증례 두 모양(공통 상자 있음 · 없음)으로만. 공통 상자가 없으면 묶음이 옆으로(왼쪽→오른쪽) 놓인다.
