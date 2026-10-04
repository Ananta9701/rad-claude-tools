# RELEASE v2.90 — manifest v110 — 2026-10-05

> **v2.90** — `textbook.py` 0.8.2: v0.8 장 찾기 규칙이 쪽 머리 한 번만 보고 받은 장 중 위험한 모양을 plan "확인할 것" 에 올림(v2.88 검수 참고 A). 장을 나누는 결과는 바뀌지 않음. 다른 도구 동작 변경 없음.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `textbook.py` · `test_textbook.py` · `TEXTBOOK.md` | 0.8.2 | `resolve_chapters` 가 v0.8 "다음 쪽 머리" 규칙으로만 받은 장(뒤 12쪽 안에 같은 번호가 없음)에서 다음 쪽 머리가 **같은 번호**(장을 닫는 다음 번호가 아님)면 그 거리를 `lone_gap` 으로 남기고, `chapters_from_heads` 가 "확인할 것" 에 한 줄. 합성(3장 1·3·5쪽 · 잡음 4 @8 · 진짜 4장 40·42쪽)은 4장 8쪽 그대로 + 한 줄. 시험 1건(고치기 전 실패 · 성공·실패 두 쪽) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| v2.88 클라우드 검수 참고 A — 듬성한 장의 잡음 c+1 을 장 시작으로 받는 시험 안 된 실패 쪽 | 사용자 10-05 안 다: 규칙 그대로 + 확인할 것. 맥 7권 대조 — 0.7.2·0.8 이 둘 다 찾은 장의 시작 쪽이 다른 곳 0 · 이 한 줄이 붙는 곳 4(모두 실제로 맞는 장 시작). 안 가(거리 한도)는 실제 장 하나를 34쪽 늦추고 안 나(여는 쪽 표지 동반)는 새로 찾은 장을 거의 다 잃어 쓰지 않음 |
| v2.88 클라우드 검수 참고 B — manifest `release-hashes` 의 HISTORY 해시가 §1 줄 넣기 전 것 | 코드 전용 `release.py` 에서 고침(이 판부터 맞음 · 비공개 시험 1건) |

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
| `TOOLS_MANIFEST.md` | v110 | `64d1381fea82` | ○ |
| `RELEASE.md` | v2.90 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.54 | `71b8a1bfa924` | — |
| `test_toolkit.py` | v16.54 | `217fa50a4cc6` | — |
| `DECK_SPEC.md` | v16.54 | `724b3edaa739` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v110 | `64d1381fea82` | ○ |
| `RELEASE.md` | v2.90 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v110 | `64d1381fea82` | ○ |
| `RELEASE.md` | v2.90 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.8.2 | `aee9c78eb534` | ○ |
| `test_textbook.py` | v0.8.2 | `2d8efa6d0cb5` | ○ |
| `TEXTBOOK.md` | v0.8.2 | `01e49ab0c032` | ○ |
| `TOOLS_MANIFEST.md` | v110 | `64d1381fea82` | ○ |
| `RELEASE.md` | v2.90 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `TOOLS_MANIFEST.md` | v110 | `64d1381fea82` | ○ |
| `RELEASE.md` | v2.90 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.54 | `71b8a1bfa924` | — |
| `test_toolkit.py` | v16.54 | `217fa50a4cc6` | — |
| `DECK_SPEC.md` | v16.54 | `724b3edaa739` | — |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | — |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.8.2 | `aee9c78eb534` | ○ |
| `test_textbook.py` | v0.8.2 | `2d8efa6d0cb5` | ○ |
| `TEXTBOOK.md` | v0.8.2 | `01e49ab0c032` | ○ |
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v110 | `64d1381fea82` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `100aa90336b7` | ○ |
| `release.py` | — | `144c0e39f14a` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `5902bac98881` | — |
| `RELEASE.md` | v2.90 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v110 이상.
2. **교과서(Cowork)**: 다음 plan 부터 0.8.2. "확인할 것" 에 "쪽 머리 한 번만 보고 받았다" 줄이 있으면 그 쪽이 장 여는 쪽인지 원본 그림으로 보고, 아니면 장 표의 시작 쪽을 고친다.

## 5. 검증하지 않은 것

- 한 줄이 붙는 기준(12쪽)은 v0.8 의 lookahead 와 같게 두었다 — 맥 7권 밖 17권에서 몇 줄이 붙는지는 안 셌다.
- Cowork(Python 3.10) 환경의 실제 plan 은 돌리지 않았다(build 의 3.10·옛 라이브러리 시험만).
