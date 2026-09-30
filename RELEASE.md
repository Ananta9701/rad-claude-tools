# RELEASE v2.73 — manifest v93 — 2026-09-30

> **v2.73** — 교신저자 설명용 초점 그림 `focus`(사용자 09-30 큰 방향 ②): 선택한 주장을 가운데, 받침(상류 2단계·한계·반박)과 영향(하류)을 세 칸 한 그림에, 쉬운 말 범례, 로컬 브라우저 headless 로 PNG. 저자 파일만(원고 기준)과 저자+덧붙임(구연 기준, 화면 번호) 둘 다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.15 | `focus <id…> (--claims \| --oral --author) -o md [--png] [--pptx] [--up 2] [--ids] [--mermaid-js] [--size]` — `focus_graph`(받침 2단계 · 한계·반박은 선택+받침 1단계 · 영향은 impact 0.25↑) · `focus_mermaid`(받침·선택한 주장·영향 세 칸, 선택한 주장은 전문 줄바꿈·나머지 40자, 구연은 화면 번호·무대 밖 흐림) · `focus_legend`(그림에 있는 것만, 반박 선이 없으면 뺌) · `find_mermaid_js`(--mermaid-js → 환경변수 → npm node_modules → CDN) · `find_browser`(환경변수 → macOS Chrome → `/opt/pw-browsers/chromium-*` → PATH) · `render_png`(임시 프로필, PNG 가 생기면 그 브라우저만 끔, 여백 자르기, 2배) — 브라우저가 없으면 md·html 을 남기고 [!]·종료 코드 1 |
| `CLAIM_GRAPH.md` | 16.15 | §3-6 초점 그림 · 저자 대화창 첫 사용(`npm install mermaid@11` 한 줄) · 명령표 |
| 테스트 | — | test_claim_graph 3(받침·한계·반박·영향 범위와 빠지는 것, 상자 글 전문/40자/--ids, 범례와 반박 없을 때, 없는 id · 구연 화면 번호·무대 밖·slide@ID · mermaid 찾기 순서 4가지와 없는 파일, HTML, 브라우저 없음 → md·html 남기고 종료 1, PNG 없이 md 만 종료 0) — 브라우저로 찍기는 자동 테스트에 없다(빌드 환경에 브라우저 보장 없음) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-30: 초점 그림 설계 답(받침 2단계 · 한계 직접+받침 1단계 · 선택한 주장 전문 · 범례+반박 · mermaid 로컬 우선 · PNG 는 Mac·저자 대화창 둘 다 · 한 판) | 위 claim_graph 16.15 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.15 | `8ea3867962a6` | ○ |
| `test_claim_graph.py` | v16.15 | `f33cb412b068` | ○ |
| `CLAIM_GRAPH.md` | v16.15 | `9789d2eee48c` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v93 | `8c1a238faa71` | ○ |
| `RELEASE.md` | v2.73 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.15 | `8ea3867962a6` | ○ |
| `test_claim_graph.py` | v16.15 | `f33cb412b068` | ○ |
| `CLAIM_GRAPH.md` | v16.15 | `9789d2eee48c` | ○ |
| `deck_toolkit.py` | v16.50 | `66c593d157b7` | — |
| `test_toolkit.py` | v16.50 | `fd00196d9736` | — |
| `DECK_SPEC.md` | v16.50 | `bbe61c4aebd5` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v93 | `8c1a238faa71` | ○ |
| `RELEASE.md` | v2.73 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.15 | `8ea3867962a6` | ○ |
| `test_claim_graph.py` | v16.15 | `f33cb412b068` | ○ |
| `CLAIM_GRAPH.md` | v16.15 | `9789d2eee48c` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v93 | `8c1a238faa71` | ○ |
| `RELEASE.md` | v2.73 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v93 | `8c1a238faa71` | ○ |
| `RELEASE.md` | v2.73 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `TOOLS_MANIFEST.md` | v93 | `8c1a238faa71` | ○ |
| `RELEASE.md` | v2.73 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.15 | `8ea3867962a6` | ○ |
| `test_claim_graph.py` | v16.15 | `f33cb412b068` | ○ |
| `CLAIM_GRAPH.md` | v16.15 | `9789d2eee48c` | ○ |
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
| `TOOLS_MANIFEST.md` | v93 | `8c1a238faa71` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `05f3bb414685` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.73 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v93 이상.
2. 저자: 교신저자에게 보낼 그림이 필요하면 CLAIM_GRAPH §3-6 "저자 대화창 첫 사용" — `cd /tmp && npm install mermaid@11` 한 번, 그다음 `claim_graph.py focus <id> --claims <claims> -o /tmp/f.md --png /tmp/f.png`. 출력의 `mermaid: … · 브라우저: …` 줄과 PNG 를 코드에 알려 주면 좋다(Linux 첫 확인).
3. 발표: 구연 준비에 `focus <id> --oral … --author … --pptx 덱 --png …` 로 화면 번호가 붙은 그림.

## 5. 검증하지 않은 것

- **Linux(claude.ai 컨테이너)에서 PNG 를 찍지 않았다** — Mac(Chrome 154, CDN mermaid@11)에서만 찍어 확인(2초, 여백 자름, 한글·줄바꿈·세 칸·범례·화면 번호). 부관리자 대화창에서 확인 예정(사용자 09-30).
- Mac 의 로컬 mermaid 파일 경로(환경변수·--mermaid-js)로는 아직 찍지 않았다 — 순서는 자동 테스트로만.
- 큰 그래프(받침이 많은 주장)에서 읽히는지 모른다 — 가짜 10주장 그래프로만.
