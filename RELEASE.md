# RELEASE v2.86 — manifest v106 — 2026-10-03

> **v2.86** — `deck_toolkit` 16.53: XML 속성 순서와 상관없이 읽는다(Google Slides 를 거친 덱에서 audit·lint·overflow·titles 가 멈추던 것).

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.53 | `slide_size()` 가 `<p:sldSz>` 의 속성 순서와 상관없이 읽는다(전에는 `cy` 가 먼저면 AttributeError — audit·lint·overflow·titles 가 멈춤). 크기 속성이 없으면 무엇이 없는지 말하는 ValueError. 위치·크기 정규식 30여 곳이 `<a:off x= y=>`·`<a:ext cx= cy=>` 순서를 가정하므로, `Deck.open` 이 순서가 다른 `a:off`·`a:ext`·`a:chOff`·`a:chExt` 만 x,y / cx,cy 순서로 다시 쓴다(뜻은 같다 · 순서가 맞는 파일은 바이트 그대로 · `<a:ext uri=…>` 처럼 두 값이 다 없는 태그는 그대로). 바로잡은 수는 `Deck.attr_order_fixed`, `audit` 머리에 [참고] 한 줄 |
| `test_toolkit.py` | 16.53 | 4건: cy 먼저인 sldSz 로 audit·lint·overflow·titles(성공) · 크기 없는 sldSz 는 ValueError(실패) · 뒤집힌 off/ext 를 열면 원래 덱과 글자 그대로(성공) · 순서가 맞는 덱·`a:ext uri` 는 한 바이트도 안 바뀜(실패 쪽) — 고치기 전 4건 모두 실패 확인 |
| `DECK_SPEC.md` | 16.53 | 첫머리 v16.53 한 줄 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 10-03 — 전평 덱 읽기만 점검에서 찾은 도구 결함(맥 이전 전 시험) | 위 16.53. 실물 덱(140화면)에서 네 명령이 감싸개 없이 돈다(맥 확인) |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | — |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | — |
| `TOOLS_MANIFEST.md` | v106 | `a93daf0422b8` | ○ |
| `RELEASE.md` | v2.86 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.53 | `7eff816ea019` | ○ |
| `test_toolkit.py` | v16.53 | `ec3ac60be824` | ○ |
| `DECK_SPEC.md` | v16.53 | `78dc2d3b7284` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v106 | `a93daf0422b8` | ○ |
| `RELEASE.md` | v2.86 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v106 | `a93daf0422b8` | ○ |
| `RELEASE.md` | v2.86 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v106 | `a93daf0422b8` | ○ |
| `RELEASE.md` | v2.86 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `TOOLS_MANIFEST.md` | v106 | `a93daf0422b8` | ○ |
| `RELEASE.md` | v2.86 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.53 | `7eff816ea019` | ○ |
| `test_toolkit.py` | v16.53 | `ec3ac60be824` | ○ |
| `DECK_SPEC.md` | v16.53 | `78dc2d3b7284` | ○ |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | — |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v106 | `a93daf0422b8` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `630f47efa65c` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.86 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v106 이상.
2. **발표**: Google Slides 를 거친 덱도 audit·lint·overflow·titles 가 돈다. 순서를 바로잡은 덱을 이 도구로 저장하면 위치·크기 태그가 표준 순서로 저장된다(뜻 같음) — `audit` 머리의 [참고] 줄로 안다.

## 5. 검증하지 않은 것

- `a:off`·`a:ext`·`a:chOff`·`a:chExt` 가 뒤집힌 실물 덱은 아직 없다 — 시험 덱(python-pptx 로 만든 것을 뒤집음)으로만 확인. 실물 덱(HN v15)은 `sldSz` 하나만 뒤집혀 있었다.
- 다른 태그의 속성 순서 가정은 찾아봤으나(정규식 안의 두 속성 고정) 읽는 쪽에는 없었다(`<a:rPr lang= sz=` 3곳은 새 글을 쓰는 틀).
