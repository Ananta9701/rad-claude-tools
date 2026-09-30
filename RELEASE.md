# RELEASE v2.78 — manifest v98 — 2026-09-30

> **v2.78** — ④ 문헌 그래프 2판 전 작은 고침 셋(첫 실물 논문 paper.md 로 찾음): 옛 쪽 표지 `[p.N]` 을 `PDF N` 으로 풀어 적기 · 쪽 머리·꼬리(저자 et al. DOI · 학술지 이름 쪽번호) 줄을 문단에서 빼기 · 줄 끝 하이픈 낱말을 붙인 꼴로도 찾기.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.20 | `DocSource`(쪽 표지 md): `mark_of` 가 옛 표지 `[p.N]` → `PDF N`, `[p.N · 인쇄]` → `[p.인쇄 · PDF N]` · `doc:sec:PDF N`·`doc:sec:p.인쇄` 는 쪽 번호로 맞춤(옛 표지도, `PDF 1` 이 `PDF 10` 을 집지 않음) · 쪽 머리·꼬리 빼기 — 쪽 표지 3쪽 이상, 쪽 위·아래 세 줄에서 쪽 절반 이상(3쪽 이상)에 되풀이되는 줄 앞머리(숫자 같게, 12자 이상, 쪽 번호가 들었거나 줄 전체) · `doc:find` 가 줄 끝 하이픈(+ 다음 줄 소문자)을 붙인 찾기 사본으로도 찾음(문단 글은 원문 그대로) |
| `CLAIM_GRAPH.md` | 16.20 | §3-8 — 하이픈·쪽 머리·꼬리·옛 표지 |
| 테스트 | — | test_claim_graph 3(옛 표지 풀어 적기·쪽 번호 절·없는 쪽 오류·새 표지와 절 표지는 그대로 / 쪽 머리·붙은 꼬리 빠짐·붙어 있던 본문 남음·2쪽뿐인 줄·흔한 문장 첫머리·3쪽 이하·절 표지 md 는 그대로 / 하이픈 붙인 꼴·원래 꼴 둘 다 찾음·대문자 복합어는 안 붙임·없는 낱말 오류) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 부관리자 지시 09-30(`권한방식과역할상태_v1` 3번): ④ 2판 전 작은 고침 셋 | 위. 첫 실물 paper.md(옛 표지) 측정: 머리 줄 14쪽·꼬리 15곳 → 0(남은 1곳은 본문 속 주소 — 맞음), 뺀 낱말 146 = 머리 14×4 + 꼬리 15×6(본문 손실 0) · 줄 끝 하이픈 낱말 176 중 못 찾음 39 → 0 · 줄바꿈 넘는 6낱말 구절 1,169: 한 곳 1,105 → 1,097, 모호 64 → 57, 못 찾음 0 → 15(15개 모두 뺀 머리·꼬리를 걸친 구절) |
| literature `locate` 도 같이 고칠지(HISTORY §5) | **고치지 않음**(코드 판단): locate 는 문단 점수만 쓰고, 하이픈·밑줄은 "0회" 판정에서 이미 느슨하게 다시 센다(v0.4). 머리·꼬리 줄은 찾을 말과 겹치지 않아 점수에 거의 영향 없음. 실물에서 문제가 보이면 그때 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.20 | `6723cb79d479` | ○ |
| `test_claim_graph.py` | v16.20 | `733745e40924` | ○ |
| `CLAIM_GRAPH.md` | v16.20 | `ed01ad170aed` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v98 | `c70149aebfba` | ○ |
| `RELEASE.md` | v2.78 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.20 | `6723cb79d479` | ○ |
| `test_claim_graph.py` | v16.20 | `733745e40924` | ○ |
| `CLAIM_GRAPH.md` | v16.20 | `ed01ad170aed` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v98 | `c70149aebfba` | ○ |
| `RELEASE.md` | v2.78 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.20 | `6723cb79d479` | ○ |
| `test_claim_graph.py` | v16.20 | `733745e40924` | ○ |
| `CLAIM_GRAPH.md` | v16.20 | `ed01ad170aed` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v98 | `c70149aebfba` | ○ |
| `RELEASE.md` | v2.78 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v98 | `c70149aebfba` | ○ |
| `RELEASE.md` | v2.78 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `TOOLS_MANIFEST.md` | v98 | `c70149aebfba` | ○ |
| `RELEASE.md` | v2.78 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.20 | `6723cb79d479` | ○ |
| `test_claim_graph.py` | v16.20 | `733745e40924` | ○ |
| `CLAIM_GRAPH.md` | v16.20 | `ed01ad170aed` | ○ |
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
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v98 | `c70149aebfba` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `de852f91334a` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.78 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v98 이상.
2. 문헌 그래프를 이미 `mapfreeze` 한 곳은 없다(첫 실물 전) — 있었다면 쪽 머리·꼬리가 든 문단은 이번 판에서 글이 바뀌어 `mapstale` 이 [변경] 을 낸다(원문은 그대로, 읽는 법이 바뀜).

## 5. 검증하지 않은 것

- 실물은 한 편(옛 표지, 한 출판사 조판)뿐. 다른 조판(두 단·쪽 꼬리가 다른 곳에 붙는 것·쪽 번호 없는 머리 줄)은 모름 — 쪽 번호도 없고 줄 전체도 아닌 머리·꼬리는 빼지 않는다(본문을 먹지 않는 쪽으로).
- 교과서 분할 md(쪽 표지 있음)에도 같은 규칙이 돈다 — 책 쪽 머리(장 제목 + 쪽 번호)가 빠질 것으로 보지만 실물로 돌리지 않았다.
- 사람 이름 꼴 검사는 그대로(네 가지 꼴).
