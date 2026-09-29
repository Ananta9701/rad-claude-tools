# RELEASE v2.65 — manifest v85 — 2026-09-29

> **v2.65** — claim_graph 작은 것 일곱(저자·리뷰어·발표 질문지 회신 09-29). 그중 **결함 하나: `doc:tbl:0`·`doc:p:0` 이 오류 없이 마지막 표·문단을 돌려줬다**(조용한 오답) — 이제 읽을 수 없는 자리. 나머지는 편의: 보충자료 수치 한 줄, 보충 번호 재번호, `add`/`link`, 파일 이름만 줄 때 안내, selfcheck 환경 줄, mapcheck 통과 문구. claim_graph 16.9. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.9 | ① **`doc:tbl:N`·`doc:p:N`** 은 1..개수 밖이면 `읽을 수 없음(번호는 1부터 K 까지)` — 전에는 0 이 마지막 것(리뷰어 3). `mapfreeze` 는 v2.49 부터 읽을 수 없는 자리에서 멈춘다 ② **`mapcheck --nums`**: evidence 에 `Suppl S{n}` 표지가 있으면 그 evidence 의 **못 찾은** 수치를 주장마다 적지 않고 `[참고] 보충자료 표지(Suppl S…)가 든 evidence N개(id…)의 수치 M개가 sites 에 없음` 한 줄로(저자 3a) ③ **`remap-refs --suppl S매핑.json`**: `Suppl S{n}`·`Supplementary Table S4 and S2` 재번호, `--map` 과 따로·함께, 없는·삭제 번호는 그대로 + [경고], 두 번 적용 거부(저자 3b) ④ **`add`·`link`**: 간선 weight 를 type 기본값으로, 없는 id·같은 간선·순환은 멈춤(저자 3c) ⑤ `--claims` 를 받는 명령에 파일 이름만 주면 고칠 명령을 보여 줌(발표 3) ⑥ **selfcheck `환경` 행**: Python·pypdf·Pillow·python-pptx·python-docx 판(발표 4) ⑦ **mapcheck 통과 문구** `모든 주장의 자리에 찾는 표현이 있음 — 주장·evidence 가 최신인지는 보지 않는다`(저자 4 — 전에는 "반영됨") |
| `CLAIM_GRAPH.md` | 16.9 | §자리·`--nums` 줄·`selfcheck`·`mapcheck`·`remap-refs` 줄, `add`·`link` 두 줄, §4 머리 안내 |
| 테스트 | — | test_claim_graph 7(재현 6 — 옛 코드: `doc:tbl:0` 이 마지막 표, Suppl 수치 주장마다 한 줄, `--suppl` 없음, `add`/`link` 없음, 파일 이름만 주면 argparse 오류, "반영됨". 각 성공·실패 두 쪽) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 저자 3a 보충자료 수치 | ② — **실물 모양을 보고 정함**: 저자 claims v9 의 `Suppl` 표기 15개가 모두 evidence 맨 앞 `Suppl S{n}` 출처 표지이고 수치는 뒤 조각에 있다. 그래서 "표지가 든 조각만 건너뛰기" 가 아니라 "표지가 있는 evidence 의 못 찾은 수치를 한 줄로" 로 했다. 본문 수치가 같은 evidence 에 섞여 있어도 **찾으면** 조용하고, 못 찾으면 한 줄에 합쳐진다 — 그 경우는 주장별로 안 보인다(한계) |
| 저자 3b 보충 재번호 | ③ |
| 저자 3c add/link | ④ — `-o` 필수(제자리 덮어쓰기 안 함, mapfreeze·remap-refs 와 같게) |
| 리뷰어 3 `doc:tbl:0` | ① — 문서만 고칠 일이 아니라 결함이었다 |
| 발표 3 파일 이름만 | ⑤ |
| 발표 4 환경 표시 | ⑥ |
| 저자 4 "통과" 의 뜻 | ⑦ |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.9 | `c57862ed2485` | ○ |
| `test_claim_graph.py` | v16.9 | `4cee6ef82a26` | ○ |
| `CLAIM_GRAPH.md` | v16.9 | `af7dde0cafca` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v85 | `8884a01130d9` | ○ |
| `RELEASE.md` | v2.65 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.9 | `c57862ed2485` | ○ |
| `test_claim_graph.py` | v16.9 | `4cee6ef82a26` | ○ |
| `CLAIM_GRAPH.md` | v16.9 | `af7dde0cafca` | ○ |
| `deck_toolkit.py` | v16.45 | `eeb2305adca7` | — |
| `test_toolkit.py` | v16.45 | `d0123d0f9c21` | — |
| `DECK_SPEC.md` | v16.45 | `1c2910d1d90a` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v85 | `8884a01130d9` | ○ |
| `RELEASE.md` | v2.65 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.9 | `c57862ed2485` | ○ |
| `test_claim_graph.py` | v16.9 | `4cee6ef82a26` | ○ |
| `CLAIM_GRAPH.md` | v16.9 | `af7dde0cafca` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v85 | `8884a01130d9` | ○ |
| `RELEASE.md` | v2.65 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v85 | `8884a01130d9` | ○ |
| `RELEASE.md` | v2.65 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.4 | `0585dbb787b0` | — |
| `test_literature.py` | v0.8.4 | `940eca6399e2` | — |
| `LITERATURE.md` | v0.8.4 | `e35c0d149938` | — |
| `TOOLS_MANIFEST.md` | v85 | `8884a01130d9` | ○ |
| `RELEASE.md` | v2.65 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.9 | `c57862ed2485` | ○ |
| `test_claim_graph.py` | v16.9 | `4cee6ef82a26` | ○ |
| `CLAIM_GRAPH.md` | v16.9 | `af7dde0cafca` | ○ |
| `deck_toolkit.py` | v16.45 | `eeb2305adca7` | — |
| `test_toolkit.py` | v16.45 | `d0123d0f9c21` | — |
| `DECK_SPEC.md` | v16.45 | `1c2910d1d90a` | — |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.4 | `0585dbb787b0` | — |
| `test_literature.py` | v0.8.4 | `940eca6399e2` | — |
| `LITERATURE.md` | v0.8.4 | `e35c0d149938` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v85 | `8884a01130d9` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `2c4237be8cfa` | ○ |
| `release.py` | — | `0a430411a738` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.65 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v85 이상. 표에 `환경` 행이 새로 나온다 — 회신에 그대로 붙인다.
2. 저자·리뷰어: 그래프에 `doc:tbl:0`·`doc:p:0` 자리가 있으면 이제 `mapcheck`·`mapfreeze` 가 읽을 수 없다고 멈춘다. **전에는 마지막 표·문단을 읽고 있었다** — 1부터 다시 적는다.
3. 저자: `mapcheck --nums` 의 보충자료 [참고] 가 한 줄로 준다. 보충 표를 재번호하면 `remap-refs --suppl`.

## 5. 검증하지 않은 것

- 실제 원고 docx 로는 돌리지 않았다(이 세션에 없다). Suppl 규칙은 저자 claims v9 의 **표기 모양만** 보고 정했다(내용은 옮기지 않음). claims v10 은 Drive 에서 찾지 못했다.
- 리뷰어 그래프에 `doc:tbl:0` 이 실제로 남아 있는지는 모른다.
