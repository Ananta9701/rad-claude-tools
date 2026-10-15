# RELEASE v2.92 — manifest v112 — 2026-10-15

> **v2.92** — `DECK_SPEC.md` 16.56(문서만): 전평 풀이 덱 대본 꼴(§0 A-4). `literature.py` 0.8.7: 맥 로컬 거부 검사 파일을 `RAD_GUARD_DIR`(기본 `~/.config/rad-guard`)에서 찾음 · 거부 검사 파일은 공개 세트에서 뺌(없으면 전과 같음). `deck_toolkit.py` 는 판 번호만.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `DECK_SPEC.md` · `deck_toolkit.py` · `test_toolkit.py` | 16.56 | §0 A-4 끝에 전평 풀이 덱 대본 꼴 일곱 줄(사용자 10-15): 목록 화면 한 줄 길잡이 · 문제 화면은 영상 읽기 네 단계(사진 종류 · 정상 비교 · 이상 소견 · sign) 뒤 문제의 포인트 · 설명은 기전 · 감별 짝 · 외울 것 · 정답 앞 이음 줄 · 교과서 화면은 제목 한 줄 기본 · 노트는 말할 문장만 위 · 안 말할 것은 모두 `NOT SPOKEN` 아래 · 교과서 화면 빈 곳에 그 장 그림(원내 교육 발표만 · 고르는 법 넷). 다음 전평 덱부터. 동작 변경 없음 |
| `literature.py` · `test_literature.py` · `LITERATURE.md` | 0.8.7 | 거부 검사(10-12 맥 로컬 스위치)를 공개 세트 안 파일 대신 `RAD_GUARD_DIR`(기본 `~/.config/rad-guard`)에서 찾음 — 있으면 막힌 자리를 가리키는 인자에서 종료 3, 없으면(Cowork) 전과 같음. 거부 검사 파일은 공개 저장소에서 뺌. 시험 1(있음 → 3 · 없음 → 막지 않음 · 세트에 파일 없음) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 부관리자 지시 `대본꼴과V29숫자_v1` 1 · `근골격발표판노트고침_v1` 2(10-15) — DECK_SPEC A-4 대본 꼴 · 6번 바꿈 | 그대로(사용자 코드 창 "둘 다 해" 10-15) |
| 판 막힘(공개 거부 검사 파일이 세트 밖) — D261015-04 (가) | 공개에서 빼고 맥 로컬로 · literature 0.8.7 |

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
| `TOOLS_MANIFEST.md` | v112 | `cdf750e690d8` | ○ |
| `RELEASE.md` | v2.92 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.56 | `01d68835a20a` | ○ |
| `test_toolkit.py` | v16.56 | `19b70ed1cd63` | ○ |
| `DECK_SPEC.md` | v16.56 | `47899e71958c` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v112 | `cdf750e690d8` | ○ |
| `RELEASE.md` | v2.92 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v112 | `cdf750e690d8` | ○ |
| `RELEASE.md` | v2.92 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.8.2 | `aee9c78eb534` | — |
| `test_textbook.py` | v0.8.2 | `2d8efa6d0cb5` | — |
| `TEXTBOOK.md` | v0.8.2 | `01e49ab0c032` | — |
| `TOOLS_MANIFEST.md` | v112 | `cdf750e690d8` | ○ |
| `RELEASE.md` | v2.92 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.7 | `e2b37c4419db` | ○ |
| `test_literature.py` | v0.8.7 | `7b5df6c4f42e` | ○ |
| `LITERATURE.md` | v0.8.7 | `14fbd3d2b676` | ○ |
| `TOOLS_MANIFEST.md` | v112 | `cdf750e690d8` | ○ |
| `RELEASE.md` | v2.92 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.24 | `078d3171ba96` | — |
| `test_claim_graph.py` | v16.24 | `696f603a61b8` | — |
| `CLAIM_GRAPH.md` | v16.24 | `1858ba70d529` | — |
| `deck_toolkit.py` | v16.56 | `01d68835a20a` | ○ |
| `test_toolkit.py` | v16.56 | `19b70ed1cd63` | ○ |
| `DECK_SPEC.md` | v16.56 | `47899e71958c` | ○ |
| `verify_toolkit.py` | v1.3.9 | `c88c2b37d1ce` | — |
| `test_verify_toolkit.py` | v1.3.9 | `fe6c80d1abad` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.8.2 | `aee9c78eb534` | — |
| `test_textbook.py` | v0.8.2 | `2d8efa6d0cb5` | — |
| `TEXTBOOK.md` | v0.8.2 | `01e49ab0c032` | — |
| `literature.py` | v0.8.7 | `e2b37c4419db` | ○ |
| `test_literature.py` | v0.8.7 | `7b5df6c4f42e` | ○ |
| `LITERATURE.md` | v0.8.7 | `14fbd3d2b676` | ○ |
| `REVIEW_PROTOCOL.md` | v7.6 | `79c3201b3693` | — |
| `TOOLS_MANIFEST.md` | v112 | `cdf750e690d8` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `1ccbc3d21077` | ○ |
| `release.py` | — | `ec7c75121b22` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `5902bac98881` | — |
| `RELEASE.md` | v2.92 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v112 이상.
2. **발표**: 다음 전평 풀이 덱 대본부터 DECK_SPEC §0 A-4 대본 꼴(16.56)을 따른다. 이미 끝난 덱은 고치지 않는다.
3. **문헌(Cowork)**: 할 일 없음 — 거부 검사 파일이 없으면 0.8.6 과 같다.

## 5. 검증하지 않은 것

- 대본 꼴은 문서만 — 새 꼴로 짠 덱은 아직 없다(다음 전평 덱에서 처음).
- Cowork(Python 3.10) 환경의 실제 literature 명령은 돌리지 않았다(build 의 3.10 · 옛 라이브러리 시험만).
