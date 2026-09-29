# RELEASE v2.68 — manifest v88 — 2026-09-29

> **v2.68** — `locate` 의 옛 쪽 표지 알림(사용자 09-29 다음 할 일 ②). 보관소 문헌 md 가 옛 표지 `[p.N]` 이면 후보 문단 자리가 `[p.1]` 로만 보여 인쇄 1쪽으로 읽힐 수 있었다 — 이제 `[p.1](옛 표지 — PDF 1쪽)` 으로 풀어 적고 문헌마다 한 줄 알린다. (코드 쪽: 릴리스 도구가 올릴 커밋의 작성자·커미터 이름·이메일도 검사한다 — 역할 쪽 할 일은 없다.)

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `literature.py` | 0.8.5 | `locate`: 옛 쪽 표지 `[p.N]`·`[p.N · 인쇄]`(v0.6 까지 — N 은 PDF 쪽)를 후보 문단·찾을 말별 첫 자리에서 `[p.N](옛 표지 — PDF N쪽[, 인쇄 X])` 로, 그 문헌 줄 아래에 "옛 쪽 표지 — N 은 PDF 쪽이지 인쇄 쪽이 아니다 … `ingest` 를 다시 돌리면 새 표지" 한 줄. 새 표지 `[p.인쇄 · PDF N]`·절 표지 `[§ …]` 는 그대로 |
| `LITERATURE.md` | 0.8.5 | `locate` 설명에 한 줄 |
| 테스트 | — | test_literature 1(옛 표지 두 꼴 풀어 적기 · 새 표지·절 표지 그대로 · 새 변환은 알림 없음 · 옛 변환은 알림과 풀어 쓴 자리, 맨몸 `[p.N]` 없음), v07 옛 형식 호환 시험의 기대 문구를 새 표시로 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-29(다음 할 일 ②): locate 가 옛 쪽 표지를 만나면 "옛 표지 — PDF 쪽" 으로 알림 | 위 literature 0.8.5 |
| 사용자 09-29: v2.67 Linux 확인 | 부관리자 대화창(Linux, fc-list·DejaVu 있음)에서 selfcheck `--tests` **405 전부 통과** — v2.67 §5 의 "Linux 에서 돌리지 않았다" 는 **확인됨** |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.10 | `47f516373f16` | — |
| `test_claim_graph.py` | v16.10 | `5817f71b4016` | — |
| `CLAIM_GRAPH.md` | v16.10 | `539acf8f59bc` | — |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v88 | `eadf4a22716c` | ○ |
| `RELEASE.md` | v2.68 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.10 | `47f516373f16` | — |
| `test_claim_graph.py` | v16.10 | `5817f71b4016` | — |
| `CLAIM_GRAPH.md` | v16.10 | `539acf8f59bc` | — |
| `deck_toolkit.py` | v16.47 | `8b1ab74de52c` | — |
| `test_toolkit.py` | v16.47 | `819595d18946` | — |
| `DECK_SPEC.md` | v16.47 | `61bbe8c12ef1` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v88 | `eadf4a22716c` | ○ |
| `RELEASE.md` | v2.68 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.10 | `47f516373f16` | — |
| `test_claim_graph.py` | v16.10 | `5817f71b4016` | — |
| `CLAIM_GRAPH.md` | v16.10 | `539acf8f59bc` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v88 | `eadf4a22716c` | ○ |
| `RELEASE.md` | v2.68 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v88 | `eadf4a22716c` | ○ |
| `RELEASE.md` | v2.68 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | ○ |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | ○ |
| `LITERATURE.md` | v0.8.5 | `d9049de45a40` | ○ |
| `TOOLS_MANIFEST.md` | v88 | `eadf4a22716c` | ○ |
| `RELEASE.md` | v2.68 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.10 | `47f516373f16` | — |
| `test_claim_graph.py` | v16.10 | `5817f71b4016` | — |
| `CLAIM_GRAPH.md` | v16.10 | `539acf8f59bc` | — |
| `deck_toolkit.py` | v16.47 | `8b1ab74de52c` | — |
| `test_toolkit.py` | v16.47 | `819595d18946` | — |
| `DECK_SPEC.md` | v16.47 | `61bbe8c12ef1` | — |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | ○ |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | ○ |
| `LITERATURE.md` | v0.8.5 | `d9049de45a40` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v88 | `eadf4a22716c` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | ○ |
| `HISTORY.md` | — | `d335b4d0fde1` | ○ |
| `release.py` | — | `d0fe4b4d184a` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.68 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v88 이상.
2. 리뷰어·문헌: `locate` 결과에 `(옛 표지 — PDF N쪽)` 이 보이면 그 쪽 번호는 PDF 쪽이다 — 인용 쪽은 논문 첫 쪽 서지로 확인한다. 보관소를 새 표지로 바꾸는 re-ingest 는 코드가 따로 한다(다음 할 일 ④).

## 5. 검증하지 않은 것

- 보관소의 실제 옛 표지 문헌 3편으로 `locate` 를 돌리지는 않았다 — 가짜 문헌을 옛 형식으로 바꿔 시험했다(3편은 다음 할 일 ④ re-ingest 때 새 표지로 바뀐다).
- 옛 형식 `[p.N · 인쇄]` 꼴은 문서에만 있고 실제 보관소 파일에서 본 적은 없다.
- (v2.67 §5 의 Linux 미확인은 확인됨 — 위 §2.)
