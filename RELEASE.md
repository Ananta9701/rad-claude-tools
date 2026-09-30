# RELEASE v2.74 — manifest v94 — 2026-09-30

> **v2.74** — 초점 그림 고침(부관리자 Linux 첫 확인 09-30): mermaid 가 그리지 못했는데 글자만 찍힌 PNG 를 저장하고 0 으로 끝나던 [결함] → 찍기 전에 SVG 를 확인해 없으면 PNG 없이 [!]·종료 1. 배경은 회색으로 나누고 범례에 "배경". 무대 밖 받침은 종류 색을 흐리게.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.16 | `render_png` 두 번 돌림 — ① `--dump-dom` 으로 제목 표시(`done`·`mermaid-load-failed`·`mermaid-error: …`)와 `<svg` 확인(`_mermaid_status`) → 못 그렸으면 PNG 를 만들지 않고 까닭과 `npm install mermaid@11 또는 --mermaid-js` ② 찍기. 두 번 모두 결과가 나오면 그 임시 프로필의 브라우저만 끈다 · HTML 에 mermaid 불러오기 실패(`onerror`·mermaid 없음)·그리기 오류 표시 · `focus_graph` 배경 종류(role background · context 로만 닿은 받침, premise 로도 닿으면 핵심 근거) · 배경 색·범례 "배경" · 무대 밖은 종류별 흐린 색(`<종류>_off`) |
| `CLAIM_GRAPH.md` | 16.16 | §3-6 배경·무대 밖 색·SVG 확인 |
| 테스트 | — | test_claim_graph 2(가짜 브라우저 — `--dump-dom`·`--screenshot` 흉내, 끝나지 않고 기다림: 불러오기 실패·시간 초과 → 종료 1·PNG 없음·안내 / done+svg → PNG, 25초 안에 끝냄 · `_mermaid_status` 5가지 · 배경 종류·색·범례와 없을 때 · 구연 무대 밖 종류별 흐린 색) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 부관리자 09-30 [결함]: CDN 막힌 곳에서 mermaid 글자가 찍힌 PNG·종료 0 | 위 — SVG 확인, PNG 없이 [!]·종료 1 |
| 사용자 09-30: 배경 색·범례 "배경" · 무대 밖 종류 색 흐리게 | 위 |
| 부관리자 09-30: Linux PNG(npm mermaid@11 뒤) 세 칸·한계·반박·범례·한글 정상 3571×949 | v2.73 §5 "Linux 미확인" 은 확인됨 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.16 | `6aaa5751db14` | ○ |
| `test_claim_graph.py` | v16.16 | `fba30bff6b0f` | ○ |
| `CLAIM_GRAPH.md` | v16.16 | `42f44234660a` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v94 | `81fbfaa08d9c` | ○ |
| `RELEASE.md` | v2.74 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.16 | `6aaa5751db14` | ○ |
| `test_claim_graph.py` | v16.16 | `fba30bff6b0f` | ○ |
| `CLAIM_GRAPH.md` | v16.16 | `42f44234660a` | ○ |
| `deck_toolkit.py` | v16.50 | `66c593d157b7` | — |
| `test_toolkit.py` | v16.50 | `fd00196d9736` | — |
| `DECK_SPEC.md` | v16.50 | `bbe61c4aebd5` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v94 | `81fbfaa08d9c` | ○ |
| `RELEASE.md` | v2.74 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.16 | `6aaa5751db14` | ○ |
| `test_claim_graph.py` | v16.16 | `fba30bff6b0f` | ○ |
| `CLAIM_GRAPH.md` | v16.16 | `42f44234660a` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v94 | `81fbfaa08d9c` | ○ |
| `RELEASE.md` | v2.74 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v94 | `81fbfaa08d9c` | ○ |
| `RELEASE.md` | v2.74 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `TOOLS_MANIFEST.md` | v94 | `81fbfaa08d9c` | ○ |
| `RELEASE.md` | v2.74 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.16 | `6aaa5751db14` | ○ |
| `test_claim_graph.py` | v16.16 | `fba30bff6b0f` | ○ |
| `CLAIM_GRAPH.md` | v16.16 | `42f44234660a` | ○ |
| `deck_toolkit.py` | v16.50 | `66c593d157b7` | — |
| `test_toolkit.py` | v16.50 | `fd00196d9736` | — |
| `DECK_SPEC.md` | v16.50 | `bbe61c4aebd5` | — |
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
| `TOOLS_MANIFEST.md` | v94 | `81fbfaa08d9c` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `a44661ea7849` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.74 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v94 이상.
2. 저자·발표: `focus --png` 가 `[!] mermaid 가 그리지 못했다` 로 끝나면 `cd /tmp && npm install mermaid@11` 뒤 `/tmp` 에서 다시(또는 `--mermaid-js`). 전에 그 상태로 만든 PNG 가 있으면 글자만 찍힌 것이니 버린다.

## 5. 검증하지 않은 것

- SVG 확인은 Mac Chrome 154 로 실제 확인(mermaid 아닌 파일 → 종료 1·PNG 없음 1초 / 로컬 mermaid 11.17.2 → PNG 2초). Linux Chromium 에서 `--dump-dom` 이 같은 모양으로 나오는지는 부관리자 대화창에서 확인할 것.
