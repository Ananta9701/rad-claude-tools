# RELEASE v2.55 — manifest v75 — 2026-09-29

> **v2.55** — 간선이 하나도 없는 그래프(발표 09-20 판 claims 모양 — 주장 21개, 간선 0)에서 v2.54 가 mapgraph 는 21개 id 를 한 줄에 늘어놓고, mapdraw 전체 그림은 빈 그림(16×16 px) + 21줄 목록을 냈다(사용자 지적 09-29, 코드가 같은 모양 그래프로 재현). 이제 둘 다 **한 줄 요약**만. claim_graph 16.2. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.2 | `mapgraph`: 그래프 전체에 간선이 없으면(주장 2개 이상) 외톨이 이름 목록 대신 `[참고] 간선이 하나도 없는 그래프(주장 N개) — 관계(depends_on)를 아직 적지 않았다`. 간선이 조금이라도 있으면 v16.1 그대로(외톨이 이름 목록) |
| `claim_graph.py` | 16.2 | `mapdraw` 전체 그림: 간선 0 이면 Mermaid 블록 없이 한 줄(상자만 보려면 `--all-edges` — v16.0 모양). `--impact`·`--all-edges` 는 그대로 |
| `CLAIM_GRAPH.md` | 16.2 | §3-3 표·§3-1 표에 위 두 줄 |
| 테스트 | — | test_claim_graph: 간선 0 · 주장 21 그래프(재현 — v16.1 은 21줄 목록)의 mapdraw 한 줄·`--all-edges` 상자·주장 하나 그래프, mapgraph 한 줄 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-29: 발표 claims(간선 0)에서 외톨이 목록이 전부 늘어놓이지 않는지 | 재현(v2.54: mapgraph 21개 id, mapdraw 빈 그림 16×16 + 21줄) → 위 |
| 저자 09-29 관계도 전체 확인: 외톨이 [참고] · 그림에서 따로 모으기 제안 | v2.54 에 이미 들어감(외톨이 5개 — 저자 그래프에서 확인). "일부러 외톨이로 두는 표지" 는 넣지 않음(사용자 — 저자가 다섯 개 모두 이을 예정) |
| 같은 회신: `--text` 의 `#lt;`·`#gt;` 가 화면에서 부등호로 보이는지 | mermaid 11 렌더로 확인 — `A < B > C` 로 보인다 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.2 | `2fa1f4033e62` | ○ |
| `test_claim_graph.py` | v16.2 | `d8ffabd4540f` | ○ |
| `CLAIM_GRAPH.md` | v16.2 | `3cf274776293` | ○ |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `TOOLS_MANIFEST.md` | v75 | `ea22f3e3ce0c` | ○ |
| `RELEASE.md` | v2.55 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.2 | `2fa1f4033e62` | ○ |
| `test_claim_graph.py` | v16.2 | `d8ffabd4540f` | ○ |
| `CLAIM_GRAPH.md` | v16.2 | `3cf274776293` | ○ |
| `deck_toolkit.py` | v16.41 | `48c6d92415c7` | — |
| `test_toolkit.py` | v16.41 | `03718a9b26e4` | — |
| `DECK_SPEC.md` | v16.41 | `a7766b2b137a` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v75 | `ea22f3e3ce0c` | ○ |
| `RELEASE.md` | v2.55 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.2 | `2fa1f4033e62` | ○ |
| `test_claim_graph.py` | v16.2 | `d8ffabd4540f` | ○ |
| `CLAIM_GRAPH.md` | v16.2 | `3cf274776293` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v75 | `ea22f3e3ce0c` | ○ |
| `RELEASE.md` | v2.55 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `TOOLS_MANIFEST.md` | v75 | `ea22f3e3ce0c` | ○ |
| `RELEASE.md` | v2.55 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | — |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | — |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | — |
| `TOOLS_MANIFEST.md` | v75 | `ea22f3e3ce0c` | ○ |
| `RELEASE.md` | v2.55 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.2 | `2fa1f4033e62` | ○ |
| `test_claim_graph.py` | v16.2 | `d8ffabd4540f` | ○ |
| `CLAIM_GRAPH.md` | v16.2 | `3cf274776293` | ○ |
| `deck_toolkit.py` | v16.41 | `48c6d92415c7` | — |
| `test_toolkit.py` | v16.41 | `03718a9b26e4` | — |
| `DECK_SPEC.md` | v16.41 | `a7766b2b137a` | — |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
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
| `TOOLS_MANIFEST.md` | v75 | `ea22f3e3ce0c` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `6c939ee881fd` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.55 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 저자·리뷰어·발표: selfcheck 로 manifest v75 이상.
2. 발표: 지금 claims(간선 없음)로 mapgraph·mapdraw 를 돌리면 한 줄만 나온다 — 간선을 적은 뒤 그림이 생긴다.

## 5. 검증하지 않은 것

- 발표의 실제 claims 파일로는 돌리지 않았다(이 세션에 없다) — 같은 모양(주장 21개·간선 0) fixture 로 재현·확인.
