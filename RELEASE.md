# RELEASE v2.49 — manifest v69 — 2026-09-29

> **v2.49** — claim_graph 업그레이드 전에 고칠 전제 조건 세 가지(코드 리뷰 09-28 ④ — 7·8·11번). claim_graph 15.8.4 · deck_toolkit 16.40 · literature 0.6. **바뀐 동작: `mapfreeze` 는 읽을 수 없는 자리가 하나라도 있으면 기록하지 않고 멈춘다**(전에는 그 자리를 "없음" 으로 적어 두었다가, 나중에도 못 읽으면 "바뀐 것 없음" 이라고 했다). 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 15.8.4 | `mapfreeze`: 자리를 먼저 모두 읽고, 못 읽는 자리가 있으면 **멈춤**(무엇이 안 읽혔는지 목록). `mapstale`: 못 읽는 자리를 "자리를 읽을 수 없다(지운 화면·바뀐 절 제목?)" 로 알림 — 구판 freeze 가 없음으로 적어 둔 그래프도 |
| `deck_toolkit.py` | 16.40 | `mapfreeze` CLI: claims.json 맨 위 칸(`refs_maps_applied`·`version` 등)을 그대로 둔다(전에는 `deck`·`note` 만 남겼고 원고 그래프의 `doc` 이 `deck` 으로 바뀌었다) |
| `literature.py` | 0.6 | `locate`: 쪽 표지 `[p.…]` 뿐 아니라 `oa` 로 받은 md 의 절 표지 `[§ …]` 로도 문단을 나눈다(전에는 후보 0) |
| 테스트 | — | 시험 3개(성공·실패 두 쪽). claim_graph CLI 시험이 덱 자리(slide:7) 그래프로 md 를 freeze 하던 것을 원고 자리로 — 덱 자리 그래프는 이제 멈추는 것을 확인 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 코드 리뷰 ⑦ 읽을 수 없는 자리 = 안 바뀜 | 재현(고치기 전 freeze 가 멈추지 않고 None 기록) → 멈춤·알림 |
| 코드 리뷰 ⑧ deck mapfreeze 가 맨 위 칸을 버림 | 재현(고치기 전 `refs_maps_applied` 사라짐) → 그대로 |
| 코드 리뷰 ⑪ locate 가 `[§]` md 에서 후보 0 | 재현 → 절 표지로도 나눔 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | ○ |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | ○ |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | ○ |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `TOOLS_MANIFEST.md` | v69 | `eb6bb763b6be` | ○ |
| `RELEASE.md` | v2.49 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | ○ |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | ○ |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | ○ |
| `deck_toolkit.py` | v16.40 | `5ee58284d889` | ○ |
| `test_toolkit.py` | v16.40 | `040aea20b6de` | ○ |
| `DECK_SPEC.md` | v16.40 | `45d526ffac2a` | ○ |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v69 | `eb6bb763b6be` | ○ |
| `RELEASE.md` | v2.49 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | ○ |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | ○ |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v69 | `eb6bb763b6be` | ○ |
| `RELEASE.md` | v2.49 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.6 | `505e14289fd2` | — |
| `test_textbook.py` | v0.6 | `29298da49346` | — |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | — |
| `TOOLS_MANIFEST.md` | v69 | `eb6bb763b6be` | ○ |
| `RELEASE.md` | v2.49 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.6 | `83e5673bad41` | ○ |
| `test_literature.py` | v0.6 | `5f1287e8afb6` | ○ |
| `LITERATURE.md` | v0.6 | `c5e3870e3e00` | ○ |
| `TOOLS_MANIFEST.md` | v69 | `eb6bb763b6be` | ○ |
| `RELEASE.md` | v2.49 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | ○ |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | ○ |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | ○ |
| `deck_toolkit.py` | v16.40 | `5ee58284d889` | ○ |
| `test_toolkit.py` | v16.40 | `040aea20b6de` | ○ |
| `DECK_SPEC.md` | v16.40 | `45d526ffac2a` | ○ |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `textbook.py` | v0.6 | `505e14289fd2` | — |
| `test_textbook.py` | v0.6 | `29298da49346` | — |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | — |
| `literature.py` | v0.6 | `83e5673bad41` | ○ |
| `test_literature.py` | v0.6 | `5f1287e8afb6` | ○ |
| `LITERATURE.md` | v0.6 | `c5e3870e3e00` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v69 | `eb6bb763b6be` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `7f2461d40b49` | ○ |
| `release.py` | — | `a6cdc6064a0b` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.49 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 저자·리뷰어·발표: selfcheck 로 manifest v69 이상 확인. **`mapfreeze` 가 "[멈춤] 자리를 읽지 못해" 로 끝나면** 그 목록의 sites(지운 화면·바뀐 절 제목)를 먼저 고친 뒤 다시 freeze 한다 — 전에는 조용히 기록됐던 것이다. `mapstale` 에 "자리를 읽을 수 없다" 가 나와도 같다.
2. 리뷰어: `oa` 로 받은 문헌(절 표지)도 `locate` 후보가 나온다.

## 5. 검증하지 않은 것

- 실제 claims.json(각 역할의 그래프)에서 읽을 수 없는 자리가 몇 개나 있는지 — 첫 freeze 때 멈출 수 있다.
- 쪽 표지 순서(교과서 `[p.인쇄 · PDF N]` ↔ 문헌 `[p.PDF · 인쇄]`, 코드 리뷰 ⑩)는 이번 판에서 바꾸지 않았다 — 사용자 결정 대기.
