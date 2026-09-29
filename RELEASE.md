# RELEASE v2.58 — manifest v78 — 2026-09-29

> **v2.58 — 큰 방향 가: 근거 공백 작업표**(사용자 결정 09-29). claim_graph **16.5**. `gaps` 가 그래프에서 근거 공백(문헌 없음 · 근거 하나 · 약한 고리 · 외톨이)을 뽑아 **문헌 찾기 작업표**(공백마다 받침·반박 두 줄)로 내고, 채운 표를 literature 검증지시로 바꾼다. `mapgraph --sources <문헌 보관소>` 는 보관소에 없는 문헌 근거를 [필수], 판정 없는 문헌 근거를 [참고]. 규칙: AI 가 제안한 논문은 DOI 확인 → 원문 입수 → 리뷰어 판정을 거친 것만 sources 에. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.5 | **`gaps --claims X.json -o 작업표.md`** — 문헌 없음(claim·main·background — evidence 제외) · 근거 하나(문헌·교과서 1 또는 받침 간선 1) · 약한 고리(confidence low 에 premise·support 로 기댐) · 외톨이. 공백마다 받침·반박 두 줄, 칸: 검색어 · 후보 DOI · 출처(AI 제안/사람) · 입수 · 판정. 철회 주장 제외. 간선 0 그래프는 외톨이를 줄마다 내지 않음 |
| `claim_graph.py` | 16.5 | **`gaps --to-instr 작업표.md -o 검증지시.md [--name]`** — 후보 DOI 가 있고 판정이 빈 줄만 literature 검증지시(`## 참고문헌` · `## 확인할 주장`)로, 같은 DOI 는 한 번. 알림: DOI 없는 후보 칸 · 반박 줄이 빈 공백 |
| `claim_graph.py` | 16.5 | **`mapgraph --sources <문헌 보관소>`** — 문헌 근거 DOI 가 보관소에 없으면 [필수](종료 코드 1), 판정이 없으면 [참고] |
| `CLAIM_GRAPH.md` | 16.5 | §3-4 근거 공백 작업표·규칙, 명령 표, §3-1 표 |
| 테스트 | — | test_claim_graph 4(공백 네 종류·evidence 제외·철회 제외·간선 0 · 작업표 두 줄 · to-instr 선택·중복 DOI·알림 두 가지·literature 파서로 읽힘 · 보관소 [필수]/[참고]/안 줄 때 · CLI 세 길) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-29 설계 답 가 1)–3) | 위. 실물: 저자 claims v9(51주장)에 돌리면 공백 17(문헌 없음 14 — 아직 sources 칸을 쓰지 않음 · 약한 고리 3 · 근거 하나 2 · 외톨이 5), 작업표 34줄 |
| 설계 답 4)–6)(탐색적 표지 · 문헌 그래프 (B) · 이름 없이 DOI) | 나·다 설계로 기록(HISTORY). 아직 만들지 않음 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.5 | `5b5506b90f81` | ○ |
| `test_claim_graph.py` | v16.5 | `bda20a927409` | ○ |
| `CLAIM_GRAPH.md` | v16.5 | `00ae003114ab` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v78 | `bd6d978b7d0c` | ○ |
| `RELEASE.md` | v2.58 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.5 | `5b5506b90f81` | ○ |
| `test_claim_graph.py` | v16.5 | `bda20a927409` | ○ |
| `CLAIM_GRAPH.md` | v16.5 | `00ae003114ab` | ○ |
| `deck_toolkit.py` | v16.42 | `51c2c776af44` | — |
| `test_toolkit.py` | v16.42 | `f97534059e49` | — |
| `DECK_SPEC.md` | v16.42 | `cc1f82e171ea` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v78 | `bd6d978b7d0c` | ○ |
| `RELEASE.md` | v2.58 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.5 | `5b5506b90f81` | ○ |
| `test_claim_graph.py` | v16.5 | `bda20a927409` | ○ |
| `CLAIM_GRAPH.md` | v16.5 | `00ae003114ab` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v78 | `bd6d978b7d0c` | ○ |
| `RELEASE.md` | v2.58 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `TOOLS_MANIFEST.md` | v78 | `bd6d978b7d0c` | ○ |
| `RELEASE.md` | v2.58 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | — |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | — |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | — |
| `TOOLS_MANIFEST.md` | v78 | `bd6d978b7d0c` | ○ |
| `RELEASE.md` | v2.58 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.5 | `5b5506b90f81` | ○ |
| `test_claim_graph.py` | v16.5 | `bda20a927409` | ○ |
| `CLAIM_GRAPH.md` | v16.5 | `00ae003114ab` | ○ |
| `deck_toolkit.py` | v16.42 | `51c2c776af44` | — |
| `test_toolkit.py` | v16.42 | `f97534059e49` | — |
| `DECK_SPEC.md` | v16.42 | `cc1f82e171ea` | — |
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
| `TOOLS_MANIFEST.md` | v78 | `bd6d978b7d0c` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `0c5e5c8e3d6b` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.58 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 저자·리뷰어: selfcheck 로 manifest v78 이상. 자기 그래프로 `gaps` 를 한 번 — 작업표 주인은 각자.
2. 후보 논문은 작업표에만(AI 가 찾은 것은 출처 "AI 제안"). 채우면 `gaps --to-instr` → 검증지시를 `Claude 작업/문헌` 에 두고 문헌 Cowork 로. 받고 판정한 것만 sources 로.
3. sources 를 쓴 뒤 `mapgraph --sources <문헌 보관소>` — [필수]는 받지 않은 문헌 근거다.

## 5. 검증하지 않은 것

- 작업표 → 검증지시 → literature(plan·oa·ingest·locate) 를 **끝까지** 돌리지는 않았다 — literature 의 지시 파서(parse_refs·parse_claims)로 읽히는 것까지만 시험.
- 저자 v9 는 공백 수만 세었다(내용은 이 세션에 남기지 않았다).
