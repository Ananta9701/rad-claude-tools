# RELEASE v2.53 — manifest v73 — 2026-09-29

> **v2.53 — 5판: 주장 그래프의 근거 칸·반박·관계도**(사용자 결정 09-29, 저자·리뷰어·발표 질문지 답). claim_graph **16.0**. ① 근거 칸 `sources`(공통 세 칸 kind·what·at + 선택 판정 칸), ② 근거 원문이 바뀌면 `mapstale --sources` 가 알림 — 쪽 표지·변환 판만 바뀐 것은 한 줄로 묶어 쏟아지지 않게, ③ 새 관계 `rebuttal`(반박), ④ 같은 뜻 = 그래프에 짝 저장, 다듬음 = `supersedes` 이력, ⑤ 관계도 `mapdraw`(Mermaid). 함께: literature 0.8.2(초록 표지 겹침 — v2.52 결함), deck_toolkit 16.41(`--sources` 전달). 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.0 | **근거 칸** `sources: [{kind, what, at, element?, verdict?, via?, pdf?, date?, note?}]` — kind 문헌·교과서·덱·원고·기타, verdict 부합·부분·근거 없음·반대 방향. mapgraph 가 값 검사(필수 3 · 참고 4) |
| `claim_graph.py` | 16.0 | `mapfreeze`·`mapstale` `--sources <폴더>`(문헌 보관소·교과서 분할): 근거 자리의 본문 해시를 적고 비교 — `[같음]`(본문 같음 — 쪽 표지·머리말·다른 쪽만, 개수 한 줄) · `[변환]`(원 PDF·XML sha 같고 변환만 바뀜 — 하류 전파 없음, 판정이 근거 없음·부분인 것만 "다시 볼 것") · `[변경]`(원 파일이 다르거나 원문을 못 찾음 — impact 전파). 폴더를 안 주면 전처럼. 쪽 표지는 새 `[p.인쇄 · PDF N]`·옛 `[p.N]`·`p.56`(인쇄)·`PDF 70`, 절은 `[§ …]`(상자 뒤 다시 붙은 같은 표지도 한 절로) |
| `claim_graph.py` | 16.0 | 간선 `type: "rebuttal"`(반박, 0.5 — caveat 과 같은 방향·같은 무게로 전파). [참고]: caveat 간선이 role=rebuttal 을 가리킴, 반대 방향 판정인데 rebuttal 간선 없음 |
| `claim_graph.py` | 16.0 | `mapdiff --save-pairs`(짝을 그래프 맨 위 칸 `pairs_with` 에 저장, 다음부터 `--pairs` 없이 · 반대쪽에서도), `supersedes` 목록(판마다 좁힌 이력) |
| `claim_graph.py` | 16.0 | **`mapdraw --claims -o 관계도.md [--impact ID …] [--text]`** — Mermaid 글. 근거 → 주장 화살표, 간선 종류별 선, 역할별 모양, impact 면 경로만·색 |
| `CLAIM_GRAPH.md` | 16.0 | §3-2 근거 칸·반박·같은 뜻·다듬음, §3-3 관계도, 명령 표 |
| `deck_toolkit.py`·`DECK_SPEC.md` | 16.41 | `mapfreeze`·`mapstale` 에 `--sources` 전달(발표 — 교과서 쪽 근거). 덱 근거(`kind: 덱`)는 덱 자신에서 본다 |
| `literature.py`·`LITERATURE.md` | 0.8.2 | 초록 표지가 `[§ Abstract · Abstract · Methods]`·`· 절` 로 겹치던 것(v0.8.1, 실제 XML 에서 발견). 변환 판 표지 `변환 v0.8.2` — `oa` 재실행 때 다시 만든다 |
| 테스트 | — | test_claim_graph 7(근거 칸 검사 · 반박 · 이력 · 원문 바뀜 문헌 6경우 · 교과서·절 · mapdraw · 짝 저장/mapdraw CLI), test_toolkit 1(덱 --sources), test_literature 초록 표지 줄 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 저자 질문지 6 근거 위치(문헌 쪽·절·식·표) · 리뷰어 5 판정 칸 · 발표 6 교과서 쪽·덱 화면(sldId) | `sources` 칸 하나 + 공통 세 칸 + 선택 판정 칸(사용자 결정 1) |
| 리뷰어 5 "paper.md 가 바뀌면 다시 볼 것으로" | `mapstale --sources`(사용자 결정 2 — 폴더를 줄 때만, 형식·변환 판만 바뀐 것은 쏟아지지 않게). v2.51·v2.52 재변환 실물로 시험: 실제 XML 9편 절 230곳, v0.7 → v0.8.2 재변환 뒤 `[같음]` 172 · `[변환]` 58 · `[변경]` 0 |
| 저자·리뷰어 8 반박 | `rebuttal` 간선(사용자 결정 3) |
| 리뷰어 8 같은 뜻 · 저자 8 다듬음 · 발표 8 | 새 관계 없이 — `pairs_with`·`supersedes` 목록·premise(사용자 결정 4) |
| 저자·리뷰어·발표 7 관계도 | `mapdraw` 최소판(사용자 결정 5) |
| 작은 것(저자 3a·3b·3c, 리뷰어 3, 발표 3·4) | 다음 작은 판들(HISTORY §5) |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.0 | `ef835c231d70` | ○ |
| `test_claim_graph.py` | v16.0 | `9260ec19712a` | ○ |
| `CLAIM_GRAPH.md` | v16.0 | `634cabdefccc` | ○ |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `TOOLS_MANIFEST.md` | v73 | `776edac329da` | ○ |
| `RELEASE.md` | v2.53 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.0 | `ef835c231d70` | ○ |
| `test_claim_graph.py` | v16.0 | `9260ec19712a` | ○ |
| `CLAIM_GRAPH.md` | v16.0 | `634cabdefccc` | ○ |
| `deck_toolkit.py` | v16.41 | `48c6d92415c7` | ○ |
| `test_toolkit.py` | v16.41 | `03718a9b26e4` | ○ |
| `DECK_SPEC.md` | v16.41 | `a7766b2b137a` | ○ |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `TOOLS_MANIFEST.md` | v73 | `776edac329da` | ○ |
| `RELEASE.md` | v2.53 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.0 | `ef835c231d70` | ○ |
| `test_claim_graph.py` | v16.0 | `9260ec19712a` | ○ |
| `CLAIM_GRAPH.md` | v16.0 | `634cabdefccc` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v73 | `776edac329da` | ○ |
| `RELEASE.md` | v2.53 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `TOOLS_MANIFEST.md` | v73 | `776edac329da` | ○ |
| `RELEASE.md` | v2.53 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | ○ |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | ○ |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | ○ |
| `TOOLS_MANIFEST.md` | v73 | `776edac329da` | ○ |
| `RELEASE.md` | v2.53 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.0 | `ef835c231d70` | ○ |
| `test_claim_graph.py` | v16.0 | `9260ec19712a` | ○ |
| `CLAIM_GRAPH.md` | v16.0 | `634cabdefccc` | ○ |
| `deck_toolkit.py` | v16.41 | `48c6d92415c7` | ○ |
| `test_toolkit.py` | v16.41 | `03718a9b26e4` | ○ |
| `DECK_SPEC.md` | v16.41 | `a7766b2b137a` | ○ |
| `verify_toolkit.py` | v1.3.6 | `328b15bcc55e` | — |
| `test_verify_toolkit.py` | v1.3.6 | `b118dbe7b3db` | — |
| `handoff.py` | v2.1 | `6e27b4b50fb0` | — |
| `test_handoff.py` | v2.1 | `77d29be6dc53` | — |
| `HANDOFF_FORMAT.md` | v2.1 | `6932c48c139e` | — |
| `textbook.py` | v0.7.1 | `20d10c9948a9` | — |
| `test_textbook.py` | v0.7.1 | `6c348abb7431` | — |
| `TEXTBOOK.md` | v0.7.1 | `bc6c01aed463` | — |
| `literature.py` | v0.8.2 | `7a6d83eb7cae` | ○ |
| `test_literature.py` | v0.8.2 | `dbdb67022a18` | ○ |
| `LITERATURE.md` | v0.8.2 | `235284450ca3` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v73 | `776edac329da` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `3e0994b3634a` | ○ |
| `release.py` | — | `de451827dfe0` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.53 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v73 이상. 회신에 pypdf·Pillow 판 한 줄.
2. 저자·리뷰어·발표: 근거 칸은 **선택**이다 — 지금 그래프는 그대로 돈다. 쓰기 시작하면 `CLAIM_GRAPH.md` §3-2 대로, freeze 때 `--sources "<문헌 보관소 또는 교과서 분할>"`.
3. 리뷰어: 반대 증거를 caveat 으로 걸어 둔 것은 mapgraph [참고] 로 나온다 — 반대 증거면 `type: "rebuttal"` 로.
4. 관계도: `python3 claim_graph.py mapdraw --claims X.json -o 관계도.md [--impact ID]` → md 를 대화창에 붙이고 "Mermaid 로 보여 줘".
5. 리뷰어·문헌: `oa` 로 받은 문헌은 `oa` 를 한 번 다시(변환 v0.8.2). 그 전에 `--sources` 로 freeze 했다면 뒤 mapstale 은 `[변환]` 으로 나온다.

## 5. 검증하지 않은 것

- 근거 원문 비교의 실물 시험은 **실제 Europe PMC XML 9편**(literature 로 만든 md)뿐. 실제 PDF 에서 만든 paper.md·교과서 분할 md 는 fixture 로만(쪽 표지 형식은 두 도구와 같게 만들었다).
- `mapdraw` 출력은 **mermaid 11 파서(`mermaid.parse`)로 문법 통과**를 확인했다(전체 그림·impact 그림, 모든 모양·간선 종류). 그림으로 그려진 모양은 **눈으로 보지 못했다** — 첫 사용에서 이상하면 알려 달라. (첫 빌드에서 줄바꿈 `<br/>` 이 이스케이프되던 결함을 파서 검사 전에 잡아 고쳤다.)
- 덱 근거(`kind: 덱`)는 docx 대상 `claim_graph.py mapstale` 에서는 읽지 못해 기록하지 않는다(발표는 deck_toolkit 명령으로).
