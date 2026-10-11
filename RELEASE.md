# RELEASE v2.91 — manifest v111 — 2026-10-11

> **v2.91** — `DECK_SPEC.md` 16.55(문서만): 전평 풀이 덱 형식 규칙 §0-B-5 · 09-28 글자색 줄 · §2 적용 범위 · §2-4 그림 위 표지. `deck_toolkit.py` 는 판 번호만(동작 변경 없음).

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `DECK_SPEC.md` · `deck_toolkit.py` · `test_toolkit.py` | 16.55 | §0-B-5 새 절(사용자 10-11): 강조색은 화면마다 핵심 한두 구절 · 빨강 = 정답 · 핵심(다른 색은 뜻이 분명할 때만 · 뜻은 대본에서) · 원작자 화면은 글자색만 고치고 크기 · 줄 · 배치는 그대로(점검 숫자만) · 우리가 만드는 해설 화면 본문 6줄 이하 · 점검 기준 본문 18 · 각주 12 · 밀집 14pt · 마무리 형식 점검(쪽 번호 · 수만). §0-B 09-28 글자색 줄에 "쪽 전체를 칠한 곳은 핵심 구절만". §2 머리에 적용 범위(학회 덱 · 전평은 §0-B-5 가 앞섬) · 출처 표시 없음. §2-4 끝에 "우리가 그림 위에 얹는 표지는 모든 덱이 이 체계". 도구는 `__version__` · `EXPECT_VERSION` 만 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 부관리자 지시 `형식규칙병합_v1`(10-11) 할 일 1 — DECK_SPEC 고침 | 사용자 코드 창 "해"(10-11) · 고침안 9줄 그대로(보고 `형식점검스크립트와DECK_SPEC고침안_v1`) |

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
| `TOOLS_MANIFEST.md` | v111 | `406747d2ae22` | ○ |
| `RELEASE.md` | v2.91 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.55 | `afba564c68b1` | ○ |
| `test_toolkit.py` | v16.55 | `2178ab7dcc1f` | ○ |
| `DECK_SPEC.md` | v16.55 | `2f0e47912c9d` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v111 | `406747d2ae22` | ○ |
| `RELEASE.md` | v2.91 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v111 | `406747d2ae22` | ○ |
| `RELEASE.md` | v2.91 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.8.2 | `aee9c78eb534` | — |
| `test_textbook.py` | v0.8.2 | `2d8efa6d0cb5` | — |
| `TEXTBOOK.md` | v0.8.2 | `01e49ab0c032` | — |
| `TOOLS_MANIFEST.md` | v111 | `406747d2ae22` | ○ |
| `RELEASE.md` | v2.91 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `TOOLS_MANIFEST.md` | v111 | `406747d2ae22` | ○ |
| `RELEASE.md` | v2.91 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.55 | `afba564c68b1` | ○ |
| `test_toolkit.py` | v16.55 | `2178ab7dcc1f` | ○ |
| `DECK_SPEC.md` | v16.55 | `2f0e47912c9d` | ○ |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | — |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.8.2 | `aee9c78eb534` | — |
| `test_textbook.py` | v0.8.2 | `2d8efa6d0cb5` | — |
| `TEXTBOOK.md` | v0.8.2 | `01e49ab0c032` | — |
| `literature.py` | v0.8.6 | `b99516fb6f9a` | — |
| `test_literature.py` | v0.8.6 | `ac0646359a75` | — |
| `LITERATURE.md` | v0.8.6 | `73b0b00bd897` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v111 | `406747d2ae22` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `daeb1970a19a` | ○ |
| `release.py` | — | `144c0e39f14a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `5902bac98881` | — |
| `RELEASE.md` | v2.91 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v110 이상.
2. **교과서(Cowork)**: 다음 plan 부터 0.8.2. "확인할 것" 에 "쪽 머리 한 번만 보고 받았다" 줄이 있으면 그 쪽이 장 여는 쪽인지 원본 그림으로 보고, 아니면 장 표의 시작 쪽을 고친다.

## 5. 검증하지 않은 것

- 한 줄이 붙는 기준(12쪽)은 v0.8 의 lookahead 와 같게 두었다 — 맥 7권 밖 17권에서 몇 줄이 붙는지는 안 셌다.
- Cowork(Python 3.10) 환경의 실제 plan 은 돌리지 않았다(build 의 3.10·옛 라이브러리 시험만).
