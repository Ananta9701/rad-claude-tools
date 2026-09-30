# RELEASE v2.80 — manifest v100 — 2026-10-01

> **v2.80** — ④ 문헌 그래프 3판: 짝 맺은 논문 주장의 글 지문을 `mapfreeze --lit` 로 적고 `mapstale --lit` 이 논문 주장이 바뀌거나 철회되면 우리 쪽 [변경] 을 하류로 알린다 · `mapdraw`·`focus --lit` 에 청록 "선행 연구" 상자 · `gaps` 가 판정 `부합` 인 same·support 짝을 문헌으로 센다 · LITERATURE §3-2(논문 그래프 절차).

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.22 | `lit_freeze`(짝마다 `lit_links[i].verified` = 논문 주장 statement·status 지문, [필수] 면 아무것도 안 적고 멈춤) · `lit_stale`(글 바뀜·철회·없어짐 → 우리 쪽 [변경], 기록 없는 짝) · `mapstale(…, lit=)` 이 [변경] 을 하류로 · CLI `mapfreeze`·`mapstale --lit`(freeze 에 --lit 없으면 안내 한 줄) · `lit_label`(`문헌 <DOI 뒷부분> · id`) · `mapdraw --lit`(전체 그림: "선행 연구" 묶음·청록·"판정 전" / `--impact` 그림·제목도) · `focus --lit`("선행 연구"·"선행 연구 반박" 종류·범례·상자 아래 `(문헌 … · 판정 전)`, 저장 줄에 선행 연구 수) · `find_gaps`·`gaps_table(…, lit_links)` — same·support + `부합` 짝을 문헌으로(같은 DOI 하나로), 작업표 머리에 한 줄 · `--lit`+`--oral` 종료 2 를 인자 읽은 바로 뒤로(focus 도) · 초점 그림 HTML 범례 네모에 테두리 색 |
| `CLAIM_GRAPH.md` | 16.22 | §3-8-1 3판 · §4 명령 표 |
| `literature.py` · `LITERATURE.md` | 0.8.6 | **문서만** — §3-2 논문 그래프 절차(초안 문헌 Cowork → mapcheck → 리뷰어 판정 → 짝 → `--lit` freeze), claim_graph 가 문헌 세트 밖이라는 한 줄. 코드 동작 변경 없음 |
| 테스트 | — | test_claim_graph 3(freeze --lit 지문·그대로면 조용·글 바뀜 [변경]+하류·철회·없어짐·기록 없는 짝 종료 1·--lit 없으면 안 봄·[필수] 면 freeze 멈춤 / mapdraw 선행 연구 묶음·lit id 안 들어감·--lit 없으면 없음·impact 그림 판정 전 · focus lit·lit_rebut·범례 있을 때만·--oral 같이 종료 2 / gaps 부합 짝 인정·판정 없음·부분·background·rebut 은 안 셈·같은 DOI 하나로·두 논문) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 부관리자 지시 10-01(`시범현황과다음판_v2` 5번): ④ 3판 | 위. 설계안 ④ §2 의 3판 몫(mapstale·mapdraw·focus `--lit`·gaps 인정)과 §4 ⑧ LITERATURE 한 절 |
| 같은 지시 1번: test_textbook v051 "알려진 실패" | 코드 쪽에는 알려진 실패 목록이 없다. v051(pypdf 5.x 가 CMYK 를 두 번 뒤집음)은 v2.50(textbook 0.7)에서 고쳤고 매 빌드 옛 라이브러리 판(Pillow 12.1.1·pypdf 5.9.0)으로 다시 돈다 — 목록에서 빼도 된다 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.22 | `c54df1a56d49` | ○ |
| `test_claim_graph.py` | v16.22 | `133383b262cd` | ○ |
| `CLAIM_GRAPH.md` | v16.22 | `77673864873d` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v100 | `4548950d3b8c` | ○ |
| `RELEASE.md` | v2.80 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.22 | `c54df1a56d49` | ○ |
| `test_claim_graph.py` | v16.22 | `133383b262cd` | ○ |
| `CLAIM_GRAPH.md` | v16.22 | `77673864873d` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v100 | `4548950d3b8c` | ○ |
| `RELEASE.md` | v2.80 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.22 | `c54df1a56d49` | ○ |
| `test_claim_graph.py` | v16.22 | `133383b262cd` | ○ |
| `CLAIM_GRAPH.md` | v16.22 | `77673864873d` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v100 | `4548950d3b8c` | ○ |
| `RELEASE.md` | v2.80 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v100 | `4548950d3b8c` | ○ |
| `RELEASE.md` | v2.80 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | ○ |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | ○ |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | ○ |
| `TOOLS_MANIFEST.md` | v100 | `4548950d3b8c` | ○ |
| `RELEASE.md` | v2.80 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.22 | `c54df1a56d49` | ○ |
| `test_claim_graph.py` | v16.22 | `133383b262cd` | ○ |
| `CLAIM_GRAPH.md` | v16.22 | `77673864873d` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.6 | `b99516fb6f9a` | ○ |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | ○ |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v100 | `4548950d3b8c` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `dbe2892effa3` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.80 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v100 이상.
2. 문헌 그래프·짝은 아직 실물이 없다 — 첫 실물 지시가 따로 간다(문헌 Cowork 초안 → 리뷰어 판정 → 짝). 그 전에는 할 일 없음.

## 5. 검증하지 않은 것

- 실물 없음 — 가짜 보관소로만. Mermaid 그림(mapdraw·focus --lit)은 Mac Chrome + 로컬 mermaid 11.17.2 로 PNG 를 찍어 확인(선행 연구 묶음·청록·빨간 테두리·범례).
- `mapstale --lit` 은 논문 주장 **글(statement·status)** 만 본다 — 논문 주장의 자리(paper.md 구절)가 바뀐 것은 그 논문 그래프의 `mapstale paper.md` 가 본다(두 번 돌린다).
- `claim_graph.py` 가 문헌 세트에 없다 — 문헌 Cowork 는 GitHub 전체(`~/rct`)에서 쓴다. 세트에 넣을지는 첫 실물 지시 때.
