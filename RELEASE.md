# RELEASE v2.50 — manifest v70 — 2026-09-29

> **v2.50** — 두 가지. ① **쪽 그림 색이 라이브러리 판에 따라 뒤집히던 결함**(예비 대화창 09-29): pypdf 5.x 가 Adobe CMYK JPEG 에 `/Decode` 를 한 번 더 적용해 빨강이 검정으로 나왔다(pypdf 6.19 는 맞음, Pillow 판은 무관 — 재현으로 확인). textbook 0.7 이 JPEG 를 직접 풀어 PDF 뷰어와 같은 규칙으로 색을 정한다. ② **문헌 쪽 표지를 교과서와 같은 순서로**(사용자 결정, 코드 리뷰 ⑩): `[p.인쇄쪽 · PDF N]`, 같아도 늘 둘 다. literature 0.7. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `textbook.py` | 0.7 | `page`(그림 뽑기 길): CMYK JPEG(`/DCTDecode`) 는 JPEG 바이트를 직접 Pillow 로 풀고, Adobe 표지와 `/Decode` 로 뷰어와 같은 색을 정한다 — pypdf 판에 기대지 않는다 |
| `literature.py` | 0.7 | `ingest` 쪽 표지 `[p.인쇄쪽 · PDF N]` — 인쇄 쪽 = PDF 쪽 번호 표(PageLabels) 값, 없으면 `—`, 같아도 줄이지 않음. 옛 `[p.N]`(N = PDF 쪽) md 도 `locate`·`check` 가 그대로 읽는다 |
| `LITERATURE.md` | 0.7 | "쪽 표지" 절 — 인쇄 쪽을 무엇으로 정하는지(학술지 쪽 번호·e-번호 등 PageLabels 그대로, 머리말 글자에서 추정하지 않음), 옛 형식 읽는 법 |
| 테스트 | — | test_literature 1(e-번호 표 · 표 없음 · 옛 형식 호환), 기존 쪽 표지 확인 4줄을 새 형식으로. test_textbook 은 기존 CMYK 시험(Adobe+Decode · Adobe 만 · Pillow CMYK)이 옛 pypdf 에서 실패하던 것을 재현으로 삼음 |
| (코드 전용) `release.py` | — | 빌드가 **옛 라이브러리 판**(Pillow 12.1.1 · pypdf 5.9.0)으로도 모든 시험을 돌려 통과 수가 같아야 끝난다 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 예비 대화창 09-29 [결함] v051 CMYK 검정(Pillow 12.1.1·pypdf 5.9.0) | 재현: Pillow 12.1.1+pypdf 5.9 · Pillow 12.3+pypdf 5.9 실패, Pillow 12.1.1+pypdf 6.19 통과 → **원인 pypdf**. 고친 뒤 네 조합 모두 통과. 빌드 환경 Pillow 12.3.0·pypdf 6.19.0, Cowork Pillow 12.3.0(09-28 회신)·pypdf 모름 |
| 사용자 09-29: 쪽 표지 (가) | 위 literature 0.7. 보관소 paper.md 3편은 옛 형식 그대로(읽기 호환) |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | — |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | — |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | — |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `TOOLS_MANIFEST.md` | v70 | `e485273656ea` | ○ |
| `RELEASE.md` | v2.50 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | — |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | — |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | — |
| `deck_toolkit.py` | v16.40 | `5ee58284d889` | — |
| `test_toolkit.py` | v16.40 | `040aea20b6de` | — |
| `DECK_SPEC.md` | v16.40 | `45d526ffac2a` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v70 | `e485273656ea` | ○ |
| `RELEASE.md` | v2.50 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | — |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | — |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v70 | `e485273656ea` | ○ |
| `RELEASE.md` | v2.50 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7 | `93c3a9728d40` | ○ |
| `test_textbook.py` | v0.7 | `7221ecebdbb0` | ○ |
| `TEXTBOOK.md` | v0.7 | `683b8239ba07` | ○ |
| `TOOLS_MANIFEST.md` | v70 | `e485273656ea` | ○ |
| `RELEASE.md` | v2.50 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.7 | `886e0ffa18d9` | ○ |
| `test_literature.py` | v0.7 | `c1d5b53bf061` | ○ |
| `LITERATURE.md` | v0.7 | `4661fbbc22e5` | ○ |
| `TOOLS_MANIFEST.md` | v70 | `e485273656ea` | ○ |
| `RELEASE.md` | v2.50 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.4 | `b943f326a530` | — |
| `test_claim_graph.py` | v15.8.4 | `a9367fe420e6` | — |
| `CLAIM_GRAPH.md` | v15.8.4 | `f8cc78904ef7` | — |
| `deck_toolkit.py` | v16.40 | `5ee58284d889` | — |
| `test_toolkit.py` | v16.40 | `040aea20b6de` | — |
| `DECK_SPEC.md` | v16.40 | `45d526ffac2a` | — |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `textbook.py` | v0.7 | `93c3a9728d40` | ○ |
| `test_textbook.py` | v0.7 | `7221ecebdbb0` | ○ |
| `TEXTBOOK.md` | v0.7 | `683b8239ba07` | ○ |
| `literature.py` | v0.7 | `886e0ffa18d9` | ○ |
| `test_literature.py` | v0.7 | `c1d5b53bf061` | ○ |
| `LITERATURE.md` | v0.7 | `4661fbbc22e5` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v70 | `e485273656ea` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `4f61db127305` | ○ |
| `release.py` | — | `de451827dfe0` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.50 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v70 이상 확인. **selfcheck 회신에 pypdf·Pillow 판을 한 줄 적어 달라**(`python3 -c "import pypdf, PIL; print(pypdf.__version__, PIL.__version__)"`) — 판 차이 결함을 미리 잡기 위해.
2. 리뷰어·문헌: 새로 ingest 하는 paper.md 는 `[p.인쇄 · PDF N]`. 옛 `[p.N]` 은 N 이 PDF 쪽이다(LITERATURE "쪽 표지").
3. 교과서(Cowork): 쪽 그림 색이 이상했던 적이 있으면 다시 뽑는다(pypdf 5.x 였다면).

## 5. 검증하지 않은 것

- Cowork 의 pypdf 판 — 모른다(위 §4-1 로 받는다). 옛 라이브러리 판 시험은 예비 대화창 조합(Pillow 12.1.1·pypdf 5.9.0) 하나뿐.
- ICC 색 공간(`/ICCBased`, N=4) CMYK JPEG 는 같은 규칙으로 처리하지만 시험 fixture 는 `/DeviceCMYK` 뿐.
