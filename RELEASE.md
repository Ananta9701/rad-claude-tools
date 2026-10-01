# RELEASE v2.81 — manifest v101 — 2026-10-01

> **v2.81** — 저자 회신 둘: `verify_toolkit` 1.3.8 — 영어 본문 문단 안 한글 자리표시(`[자리표시 — …]`·〔수정〕·(한글))만 지우고 나머지 영어를 센다(1.3.7 은 그 문단을 **경고 없이** 통째로 빼서 단어·인용이 사라졌다), 괄호 밖에도 한글이 있는 문단은 종전대로 빼되 몇 문단·몇 낱말·그 안 인용을 알린다 · `claim_graph` 16.23 — `suggest` 규칙 3 이 main 에 안 걸린 한계에 "→ main 에 직접 걸기" 대신 "→ main 에 걸 후보(사슬 k/n)".

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `verify_toolkit.py` | 1.3.8 | `_english_part`: 본문 구간 문단에서 한글이 든 `[…]`·`〔…〕`·`【…】`·`(…)` 구간만 지움 → `check_word_count`·`check_citations` 가 남은 영어를 센다. 괄호를 지운 뒤에도 한글이 남은 문단은 한글 메모로 보고 뺀다(종전) — 이제 "⚠ 한글이 괄호 밖에도 있는 문단 N개를 통째로 뺐습니다(영어 낱말 W개 빠짐 — 그 안 인용 …)" 경고. 반환에 `korean`(segments·paras·words·cites) |
| `claim_graph.py` | 16.23 | `suggest` 규칙 3: main 에 안 걸린 공통 한계의 권고 "→ main 에 걸 후보(사슬 k/n)(Limitations 첫 문단)" — k/n 은 덧줄과 같은 main 전제 사슬(premise 만, main 포함) n 개 중 걸린 수, main 이 둘 이상이면 main 마다. 반환 `caveats[i].chain = {main: [k, n]}`. 규칙(3개 이상 주장)·덧줄·"(main 에 이미 걸림)" 은 그대로 |
| `CLAIM_GRAPH.md` | 16.23 | §3 suggest 표 규칙 3 줄 |
| 테스트 | — | test_verify_toolkit 2(자리표시 든 영어 문단 — 단어·인용 그대로·〔〕() 도 / 괄호 밖 한글 문단 — 빼되 경고·빠진 인용 표시·한글 없으면 경고 없음) · test_claim_graph 1(사슬 3/6 후보 · 사슬 밖 한계 0/6 · 이미 걸림엔 수 없음), v16.18 시험 문구를 새 권고로 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 저자 10-01 `도구회신_저자to코드_wordcount한글문단_v1` — wordcount 가 한글 든 본문 문단을 조용히 뺌 | 재현(가짜 원고: 본문 11 → 5, 경고 없음). 1.3.8 에서 한글 괄호 구간만 지우고 센다 + 남은 한글 문단은 경고 |
| 같은 회신 — `citations` 가 자리표시 안 숫자(244명·44명)를 인용 번호로 읽음 | **원인이 다르다**: 인용 패턴은 숫자·쉼표·하이픈만 든 `[…]` 만 잡아서 `[자리표시 — 244명·44명]` 은 읽지 않는다. 실제 원인은 wordcount 와 같다 — 자리표시가 든 문단을 통째로 빼서 **그 문단의 진짜 인용 [n] 이 사라지고** 뒤 번호가 순서 위반·결번으로 보였다(재현: 순서 위반 [7] · 결번 2–6). 같은 고침으로 해결 — v49 를 다시 세면 21 → 2 근처가 나와야 한다(실물로는 안 셈) |
| 저자 10-01 `도구회신_저자to코드_suggest재실행_v1` §3-2 — 사슬 0/6 한계에도 "main 에 직접 걸기" | 사용자 10-01 답(부관리자 지시 `v7답과전체지침v4_v1` 2번 ①): 규칙은 두고 줄마다 "사슬 k/n" + "후보" — 위 16.23 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.23 | `e6c4243ade62` | ○ |
| `test_claim_graph.py` | v16.23 | `b40e84e1314b` | ○ |
| `CLAIM_GRAPH.md` | v16.23 | `0410c30e4f71` | ○ |
| `verify_toolkit.py` | v1.3.8 | `529ce4740c17` | ○ |
| `test_verify_toolkit.py` | v1.3.8 | `a1b46f5e0e74` | ○ |
| `TOOLS_MANIFEST.md` | v101 | `9261e15df37b` | ○ |
| `RELEASE.md` | v2.81 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.23 | `e6c4243ade62` | ○ |
| `test_claim_graph.py` | v16.23 | `b40e84e1314b` | ○ |
| `CLAIM_GRAPH.md` | v16.23 | `0410c30e4f71` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v101 | `9261e15df37b` | ○ |
| `RELEASE.md` | v2.81 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.23 | `e6c4243ade62` | ○ |
| `test_claim_graph.py` | v16.23 | `b40e84e1314b` | ○ |
| `CLAIM_GRAPH.md` | v16.23 | `0410c30e4f71` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v101 | `9261e15df37b` | ○ |
| `RELEASE.md` | v2.81 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v101 | `9261e15df37b` | ○ |
| `RELEASE.md` | v2.81 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `TOOLS_MANIFEST.md` | v101 | `9261e15df37b` | ○ |
| `RELEASE.md` | v2.81 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.23 | `e6c4243ade62` | ○ |
| `test_claim_graph.py` | v16.23 | `b40e84e1314b` | ○ |
| `CLAIM_GRAPH.md` | v16.23 | `0410c30e4f71` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
| `verify_toolkit.py` | v1.3.8 | `529ce4740c17` | ○ |
| `test_verify_toolkit.py` | v1.3.8 | `a1b46f5e0e74` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v101 | `9261e15df37b` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `ac775f25b177` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.81 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v101 이상.
2. 저자: 원고 v49·v50 을 `wordcount`·`citations` 로 다시 센다 — 자리표시를 지운 사본과 같은 수가 나오는지(회신의 5,234·5,313 / 인용 위반 2), 남은 경고("통째로 뺐습니다")가 있으면 그 문단을 본다. `suggest` 규칙 3 줄이 "후보(사슬 k/n)" 로 나오는지 claims v11 로 한 번.

## 5. 검증하지 않은 것

- 실물 원고(v49·v50)로 다시 세지 않았다 — 가짜 docx 로만. 회신의 5,234·5,313(자리표시를 지운 사본)과 같게 나와야 하나, 자리표시가 괄호 밖 한글이면 경고와 함께 여전히 빠진다.
- 한글 괄호는 `[]`·`〔〕`·`【】`·`()` 만 본다. 다른 표시(예: `<…>`, 따옴표 안 한글)는 문단째 빠지고 경고가 난다.
- `suggest` 사슬 k/n 은 가짜 그래프로만 — 저자 claims v11 로는 안 돌렸다(회신 수치로는 `dti-16-directions` 3/6, 나머지 0/6 이 나와야 한다).
